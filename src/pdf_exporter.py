"""Convert a DOCX file to PDF using LibreOffice (headless)."""

import os
import subprocess
import sys
from pathlib import Path


def _find_libreoffice() -> str:
    """Return the path to the LibreOffice executable for the current OS."""
    if sys.platform == "darwin":
        candidates = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        ]
    elif sys.platform == "win32":
        candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
    else:
        candidates = ["soffice", "libreoffice"]

    for path in candidates:
        if os.path.isfile(path) or (sys.platform not in ("darwin", "win32") and _on_path(path)):
            return path

    raise FileNotFoundError(
        "LibreOffice not found. Install it from https://www.libreoffice.org/download/ "
        "and ensure 'soffice' is accessible."
    )


def _on_path(name: str) -> bool:
    """Return True if *name* resolves via PATH."""
    import shutil
    return shutil.which(name) is not None


def convert_to_pdf(docx_path: str, output_dir: str) -> str:
    """Convert *docx_path* to PDF inside *output_dir*.

    Returns the path to the generated PDF file.
    Raises RuntimeError on conversion failure.
    """
    soffice = _find_libreoffice()
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        soffice,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        docx_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed (exit {result.returncode}):\n{result.stderr}"
        )

    pdf_path = os.path.join(output_dir, Path(docx_path).stem + ".pdf")
    if not os.path.isfile(pdf_path):
        raise RuntimeError(
            f"LibreOffice ran successfully but PDF not found at expected path: {pdf_path}\n"
            f"stdout: {result.stdout}"
        )
    return pdf_path
