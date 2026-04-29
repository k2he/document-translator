"""Document Translator — Entry point.

Translates all .docx files in INPUT_DIR from Chinese to English using
Google Gemini or a local Ollama model, then converts each file to PDF
via LibreOffice.

Usage:
    uv run python main.py

Configuration (via .env):
    TRANSLATION_PROVIDER  — gemini (default) or ollama
    GOOGLE_API_KEY        — required when using Gemini
    GEMINI_MODEL          — default: gemini-2.5-flash
    OLLAMA_MODEL          — default: qwen3.6:35b
    INPUT_DIR             — default: input
    OUTPUT_DIR            — default: output
"""

import os
import sys
from pathlib import Path

from docx import Document
from tqdm import tqdm

import config
from src.docx_builder import apply_body_translations, apply_table_translations
from src.docx_parser import (
    has_chinese,
    iter_body_paragraphs,
    load_document,
)
from src.pdf_exporter import convert_to_pdf
from src.translator import translate_batch

BATCH_SIZE = 10  # paragraphs per API call (smaller = fewer rate limit hits)


def _translate_segments(segments: list[tuple], label: str = "paragraphs") -> dict:
    """Translate segments sequentially in batches."""
    result: dict = {}
    batches = [
        ([k for k, _ in segments[i:i+BATCH_SIZE]], [t for _, t in segments[i:i+BATCH_SIZE]])
        for i in range(0, len(segments), BATCH_SIZE)
    ]
    total_batches = len(batches)

    with tqdm(
        total=len(segments),
        desc=f"  {label}",
        unit="para",
        ncols=88,
        bar_format="  {desc}: {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {bar} {postfix}",
    ) as pbar:
        for batch_num, (keys, texts) in enumerate(batches, 1):
            pbar.set_postfix_str(f"batch {batch_num}/{total_batches} sending...", refresh=True)
            translated = translate_batch(texts)
            for key, trans in zip(keys, translated):
                result[key] = trans
            pbar.update(len(keys))
            pbar.set_postfix_str(f"{batch_num}/{total_batches} batches done", refresh=True)
    return result


def process_file(input_path: str, output_dir: str) -> None:
    print(f"\nProcessing: {input_path}")
    doc: Document = load_document(input_path)

    # --- Body paragraphs ---
    body_segments = [
        (idx, "".join(run.text for run in para.runs))
        for idx, para in iter_body_paragraphs(doc)
    ]
    print(f"  Body paragraphs with Chinese text: {len(body_segments)}")

    # --- Table cell paragraphs ---
    table_segments: list[tuple[tuple[int, int, int], str]] = []
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            seen: set[int] = set()
            for cell in row.cells:
                cell_id = id(cell._tc)
                if cell_id in seen:
                    continue
                seen.add(cell_id)
                for p_idx, para in enumerate(cell.paragraphs):
                    text = "".join(run.text for run in para.runs)
                    if text.strip() and has_chinese(text):
                        table_segments.append(((t_idx, r_idx, p_idx), text))

    print(f"  Table paragraphs with Chinese text: {len(table_segments)}")

    total_paras = len(body_segments) + len(table_segments)
    total_calls = (
        (len(body_segments) + BATCH_SIZE - 1) // BATCH_SIZE
        + (len(table_segments) + BATCH_SIZE - 1) // BATCH_SIZE
    )
    print(f"  Total: {total_paras} paragraphs, ~{total_calls} API calls\n")

    if not body_segments and not table_segments:
        print("  No Chinese text found — skipping file.")
        return

    # Validate API key before the first real translation call
    if config.TRANSLATION_PROVIDER == "gemini" and not config.GOOGLE_API_KEY:
        sys.exit(
            "ERROR: GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    # --- Translate ---
    body_translations = _translate_segments(body_segments, label="Body")
    table_translations = _translate_segments(table_segments, label="Tables")

    # --- Apply translations ---
    apply_body_translations(doc, body_translations)
    apply_table_translations(doc, table_translations)

    # --- Save DOCX ---
    os.makedirs(output_dir, exist_ok=True)
    stem = Path(input_path).stem
    out_docx = os.path.join(output_dir, stem + "_translated.docx")
    doc.save(out_docx)
    print(f"\n  Saved DOCX: {out_docx}")

    # --- Convert to PDF ---
    try:
        pdf_path = convert_to_pdf(out_docx, output_dir)
        print(f"  Saved PDF:  {pdf_path}")
    except FileNotFoundError as exc:
        print(f"  WARNING: {exc}")
        print(f"  PDF conversion skipped. Translated DOCX is at: {out_docx}")


def main() -> None:
    input_dir = config.INPUT_DIR
    docx_files = sorted(Path(input_dir).glob("*.docx"))

    if not docx_files:
        print(
            f"No .docx files found in '{input_dir}/'.\n"
            f"Copy your chapter files into the '{input_dir}/' directory and re-run."
        )
        return

    print(f"Found {len(docx_files)} file(s) in '{input_dir}/'")
    for f in docx_files:
        process_file(str(f), config.OUTPUT_DIR)

    print("\nAll files processed.")


if __name__ == "__main__":
    main()
