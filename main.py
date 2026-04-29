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
import time
from pathlib import Path

from docx import Document

import config
from src.docx_builder import apply_body_translations, apply_table_translations
from src.docx_parser import (
    has_chinese,
    iter_body_paragraphs,
    iter_table_paragraphs,
    load_document,
)
from src.pdf_exporter import convert_to_pdf
from src.translator import translate_batch

BATCH_SIZE = 10  # paragraphs per API call (smaller = fewer rate limit hits)


def _translate_segments(segments: list[tuple]) -> dict:
    """Translate a flat list of (key, text) segments and return key→translation."""
    result: dict = {}
    for i in range(0, len(segments), BATCH_SIZE):
        batch = segments[i : i + BATCH_SIZE]
        keys = [k for k, _ in batch]
        texts = [t for _, t in batch]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(segments) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Translating batch {batch_num}/{total_batches} ({len(texts)} paragraphs)...")
        translated = translate_batch(texts)
        for key, trans in zip(keys, translated):
            result[key] = trans
        if i + BATCH_SIZE < len(segments):
            time.sleep(2)  # brief pause between batches to stay within rate limits
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
    table_raw = list(iter_table_paragraphs(doc))
    # Build a stable key: (table_index, row_index, para_index) using cell identity
    # Remap to (cell_id, para_index) for lookup during apply step.
    # We need table/row indices to match apply_table_translations key format.
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

    if not body_segments and not table_segments:
        print("  No Chinese text found — skipping file.")
        return

    # Validate API key before the first real translation call
    if config.TRANSLATION_PROVIDER == "gemini" and not config.GOOGLE_API_KEY:
        sys.exit(
            "ERROR: GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    # --- Translate ---
    body_translations = _translate_segments(body_segments)
    table_translations = _translate_segments(table_segments)

    # --- Apply translations ---
    apply_body_translations(doc, body_translations)
    apply_table_translations(doc, table_translations)

    # --- Save DOCX ---
    os.makedirs(output_dir, exist_ok=True)
    stem = Path(input_path).stem
    out_docx = os.path.join(output_dir, stem + "_translated.docx")
    doc.save(out_docx)
    print(f"  Saved DOCX: {out_docx}")

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
