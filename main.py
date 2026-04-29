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
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
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

# Stay under Gemini free-tier cap (15 RPM). Proactive limiting avoids retries.
_RPM_LIMIT = 12  # conservative headroom under 15


class _RateLimiter:
    """Sliding-window rate limiter: at most max_calls per 60 seconds."""

    def __init__(self, max_calls: int):
        self._max = max_calls
        self._times: list[float] = []
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.time()
                self._times = [t for t in self._times if now - t < 60.0]
                if len(self._times) < self._max:
                    self._times.append(now)
                    return
                wait = 60.0 - (now - self._times[0]) + 0.1
            time.sleep(wait)


_limiter = _RateLimiter(max_calls=_RPM_LIMIT)


def _translate_segments(segments: list[tuple], label: str = "paragraphs") -> dict:
    """Translate segments in parallel batches, rate-limited to stay under RPM cap."""
    result: dict = {}
    batches = [
        (i, [k for k, _ in segments[i:i+BATCH_SIZE]], [t for _, t in segments[i:i+BATCH_SIZE]])
        for i in range(0, len(segments), BATCH_SIZE)
    ]
    total_batches = len(batches)

    def _do_batch(batch_idx: int, keys: list, texts: list) -> tuple:
        _limiter.acquire()
        translated = translate_batch(texts)
        return batch_idx, keys, translated

    with tqdm(
        total=len(segments),
        desc=f"  {label}",
        unit="para",
        ncols=88,
        bar_format="  {desc}: {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {bar} {postfix}",
    ) as pbar:
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = {
                executor.submit(_do_batch, idx, keys, texts): idx
                for idx, keys, texts in batches
            }
            completed = 0
            for future in as_completed(futures):
                batch_idx, keys, translated = future.result()
                for key, trans in zip(keys, translated):
                    result[key] = trans
                pbar.update(len(keys))
                completed += 1
                pbar.set_postfix_str(f"{completed}/{total_batches} batches done", refresh=True)
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
