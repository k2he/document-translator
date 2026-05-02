"""
to_pdf.py — Convert a DOCX file to PDF using LibreOffice headless.

Usage:
    python src/to_pdf.py output/charpter-4_translated.docx
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import OUTPUT_DIR


def _find_libreoffice() -> str:
    """
    Return the path to the LibreOffice executable.

    Search order:
      1. PATH (works on Linux and most macOS Homebrew installs)
      2. macOS app bundle default location
      3. Windows default installation path
    """
    # Try PATH first (covers Linux + Homebrew macOS)
    candidate = shutil.which("soffice")
    if candidate:
        return candidate

    system = platform.system()

    if system == "Darwin":
        mac_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            Path.home() / "Applications/LibreOffice.app/Contents/MacOS/soffice",
        ]
        for p in mac_paths:
            if Path(p).exists():
                return str(p)

    elif system == "Windows":
        win_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for p in win_paths:
            if Path(p).exists():
                return p

    return ""


def convert_to_pdf(docx_path: Path) -> Path:
    """
    Run LibreOffice headless to convert *docx_path* to PDF.

    The PDF is placed in the same directory as the DOCX and has the same stem.
    Returns the path to the generated PDF.
    """
    soffice = _find_libreoffice()
    if not soffice:
        print(
            "ERROR: LibreOffice not found. Install from https://www.libreoffice.org/download/",
            file=sys.stderr,
        )
        sys.exit(1)

    output_dir = docx_path.parent
    cmd = [
        soffice,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(docx_path),
    ]

    print(f"Converting {docx_path.name} → PDF …", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: LibreOffice conversion failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    pdf_path = output_dir / (docx_path.stem + ".pdf")
    if not pdf_path.exists():
        print(
            f"ERROR: Expected PDF not found at {pdf_path}. LibreOffice output:\n{result.stdout}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"PDF generated → {pdf_path}", flush=True)
    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Convert a DOCX file to PDF via LibreOffice.")
    parser.add_argument("docx_file", help="Path to the DOCX file to convert")
    args = parser.parse_args()

    docx_path = Path(args.docx_file)
    if not docx_path.exists():
        print(f"ERROR: File not found: {docx_path}", file=sys.stderr)
        sys.exit(1)

    convert_to_pdf(docx_path)


if __name__ == "__main__":
    main()
