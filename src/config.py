"""
config.py — Centralized paths and North American formatting constants.
"""

from pathlib import Path

# ── Directory layout ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"
OUTPUT_DIR = ROOT / "output"
WORK_DIR = ROOT / "work"

EXTRACTED_SEGMENTS = WORK_DIR / "extracted_segments.json"
TRANSLATED_SEGMENTS = WORK_DIR / "translated_segments.json"
AUDIT_SEGMENTS    = WORK_DIR / "audit_segments.json"
AUDITED_SEGMENTS  = WORK_DIR / "audited_segments.json"

# ── North American textbook formatting ────────────────────────────────────────
# Page size: US Letter (8.5 × 11 inches expressed in EMUs: 1 inch = 914400 EMU)
PAGE_WIDTH_EMU = int(8.5 * 914400)   # 7772160
PAGE_HEIGHT_EMU = int(11 * 914400)   # 10058400

# Margins (1 inch on all sides)
MARGIN_EMU = 914400

# Fonts
BODY_FONT = "Times New Roman"
BODY_FONT_SIZE_PT = 12

HEADING_CHAPTER_FONT = "Times New Roman"
HEADING_CHAPTER_FONT_SIZE_PT = 14
HEADING_CHAPTER_BOLD = True

HEADING_SECTION_FONT = "Times New Roman"
HEADING_SECTION_FONT_SIZE_PT = 12
HEADING_SECTION_BOLD = True

# Line spacing: 1.5× (in twips: 1pt = 20 twips; 1.5× single = 360 twips)
LINE_SPACING_TWIPS = 360  # python-docx uses Pt, so we use Pt(18) = 12pt * 1.5

# Paragraph spacing after: 6pt
PARA_SPACING_AFTER_PT = 6
