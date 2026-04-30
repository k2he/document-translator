# PRD: Chinese Calculus Textbook Translator

**Version:** 2.0  
**Date:** April 30, 2026  
**Status:** Draft

---

## Problem Statement

A Chinese university-level Calculus textbook needs to be translated into North American English. The book is available in both PDF and Microsoft Word (DOCX) formats. It contains Chinese prose (chapter text, definitions, theorems, proofs) mixed with mathematical equations, graphs, diagrams, images, and tables.

No automated pipeline exists to translate such a document while preserving its mathematical content, layout, and formatting. Manual translation is time-consuming and error-prone. General-purpose translation tools (e.g., Google Translate file upload) corrupt or silently drop mathematical notation.

The solution must not require any external LLM API key — the only AI access available is GitHub Copilot via VS Code.

---

## Format Analysis: DOCX vs PDF

Both formats are available. The pipeline processes **DOCX**, not PDF.

| Criterion | DOCX ✅ | PDF ❌ |
|---|---|---|
| Math equations | Stored as OMML XML nodes (`<m:oMath>`) — detected and skipped automatically | Rendered as glyphs/images — no semantic boundary, cannot be isolated |
| Images / graphs | Binary blobs embedded in XML — bypassed automatically | Mixed with text rendering layers — hard to separate |
| Text extraction | Clean paragraph runs via `python-docx` — full sentence context preserved | Character-level with positional noise — sentence structure lost |
| Layout reconstruction | Styles, headings, and table structure preserved; DOCX → PDF via LibreOffice (free, cross-platform) | No reliable free tool to replace text in a PDF at the correct position |
| CJK font handling | Fonts are named in XML and substitutable; LibreOffice handles conversion | CJK font reflow in PDF is unreliable across tools |

**Verdict**: Process DOCX → translate in-place → output translated DOCX + PDF via LibreOffice.  
PDF is the final delivery format; DOCX is the processing intermediary.

---

## Solution Overview

A processor built from two layers:

1. **Python scripts** (`src/`) — deterministic, stateless operations: extract translatable text, apply translations back into the document, export to PDF, apply North American formatting.
2. **A Copilot Skill** (`.github/skills/document-translator/SKILL.md`) — orchestrates the Python scripts and performs the actual Chinese → English translation inline, using whichever GitHub Copilot model is active in the VS Code session. No API key or external service is required.

---

## Translation Engine: GitHub Copilot via Skill

The Copilot model selected in VS Code is the translator. When the skill is invoked:

- Python extracts all Chinese text segments and serializes them to `work/extracted_segments.json`
- The skill reads the file, feeds segments to Copilot, and writes translations to `work/translated_segments.json`
- Python applies translations back into a copy of the DOCX, then exports to PDF

This means the translation quality and speed depend on which Copilot model is active — which is exactly what the test mode is designed to explore.

---

## Architecture

### Directory Layout

```
document-translator/
├── .github/
│   └── skills/
│       └── document-translator/
│           └── SKILL.md          ← skill orchestrator + translator
├── input/
│   ├── chapter-4.pdf             ← reference only, not processed
│   └── charpter-4.docx           ← source (note: filename has typo, harmless)
├── output/
│   ├── chapter-4_translated.docx
│   └── chapter-4_translated.pdf
├── work/
│   ├── extracted_segments.json   ← intermediate: Chinese text segments
│   └── translated_segments.json  ← intermediate: English translations
├── src/
│   ├── config.py                 ← paths, page format constants
│   ├── extract.py                ← walk DOCX, detect Chinese, write segments
│   ├── rebuild.py                ← patch translated text back into DOCX copy
│   └── to_pdf.py                 ← LibreOffice headless → PDF
└── requirements.txt
```

### Data Flow

```
input/*.docx
    → extract.py        (detect Chinese runs → extracted_segments.json)
    → SKILL.md          (Copilot translates segments → translated_segments.json)
    → rebuild.py        (patch DOCX copy with translations; apply NA formatting)
    → output/*_translated.docx
    → to_pdf.py         (LibreOffice headless subprocess)
    → output/*_translated.pdf
```

### Module Responsibilities

| Module | File | Responsibility |
|---|---|---|
| Extractor | `src/extract.py` | Load DOCX; walk all paragraphs and table cells; detect Chinese text via Unicode range `\u4e00`–`\u9fff`; write `work/extracted_segments.json`; supports `--test --pages N` |
| Rebuilder | `src/rebuild.py` | Read `work/translated_segments.json`; patch only the Chinese `<w:t>` nodes by segment ID; apply North American page formatting; write `output/<name>_translated.docx` |
| PDF Exporter | `src/to_pdf.py` | Run `soffice --headless --convert-to pdf` subprocess; auto-detect LibreOffice path on macOS and Windows |
| Config | `src/config.py` | Centralize directory paths and North American formatting constants |
| Skill | `.github/skills/document-translator/SKILL.md` | Orchestrate the three scripts; read extracted segments; translate Chinese → North American English using active Copilot model; write translated segments |

### Math Equation Preservation Detail

DOCX stores inline math as `<m:oMath>` elements and display math as `<m:oMathPara>` elements. These are siblings of `<w:r>` (text run) elements inside `<w:p>` (paragraph) nodes. `python-docx`'s `paragraph.runs` only yields `<w:r>` elements — OMML elements are never returned and therefore never modified. Patching `.text` on a run touches only `<w:t>` nodes inside `<w:r>` nodes.

**Consequence**: A paragraph mixing Chinese prose with inline math will have its text runs translated and its OMML elements preserved in place. This holds for images and graphs embedded as `<w:drawing>` elements for the same reason.

---

## North American Textbook Formatting

Applied by `rebuild.py` via `python-docx` document properties and styles:

| Property | Value |
|---|---|
| Page size | US Letter — 8.5 × 11 inches |
| Margins | 1 inch on all sides |
| Body font | Times New Roman, 12pt |
| Chapter heading | Times New Roman, 14pt, Bold |
| Section heading | Times New Roman, 12pt, Bold |
| Body line spacing | 1.5× |
| Paragraph spacing after | 6pt |

---

## Test Mode & Model Comparison Workflow

### Test Mode

`extract.py` accepts `--test --pages N` to limit extraction to the first N pages of the document. This lets the user translate a small slice before committing to a full run.

```bash
python src/extract.py input/charpter-4.docx --test --pages 5
```

The skill checks for `--test` mode and processes only the extracted subset.

### Comparing Copilot Models

Since the Copilot model is selected in the VS Code model picker, the user can compare models by:

1. Select model A in VS Code (e.g., GPT-4.1)
2. Invoke the skill in test mode on pages 1–5
3. Inspect `output/charpter-4_translated.docx`
4. Switch to model B (e.g., Claude Sonnet 4.6) in the model picker
5. Delete `work/` and re-invoke the skill in test mode on the same pages
6. Compare the two outputs side-by-side

Recommended test selection: choose a page range that includes at least one theorem proof (math-heavy) and one worked example (mixed prose and math) for a meaningful comparison.

---

## Skill Development Process

The `document-translator` skill is developed using the **skill-creator** workflow from a-team:

- Skill location: `document-translator/.github/skills/document-translator/SKILL.md`
- Development follows: draft SKILL.md → run eval test cases → review outputs with `eval-viewer/generate_review.py` → iterate
- Reference: `a-team/.github/skills/skill-creator/SKILL.md`

---

## User Stories

1. **As a reader**, I want to read the Calculus textbook in English so I can understand the content without knowing Chinese.
2. **As a translator**, I want the tool to automatically skip math equations so I do not have to manually protect them before or after translation.
3. **As a user**, I want a test mode so I can verify translation quality on a few pages before running the full book.
4. **As a user**, I want to compare different Copilot models on the same test pages so I can choose the best one for quality and speed.
5. **As a user**, I want both DOCX and PDF output so I can review the DOCX and distribute the PDF.
6. **As a developer**, I want a simple Python script I can run locally on macOS without any API key.

---

## Dependencies

| Dependency | Purpose | Install |
|---|---|---|
| `python-docx >= 1.1.0` | DOCX read / write | `pip install python-docx` |
| LibreOffice (system) | DOCX → PDF via headless subprocess | https://www.libreoffice.org/download/ |

No `openai` package. No API key. No `.env` file required.

---

## Running the Tool

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Place input files
# Ensure .docx files are in the input/ directory

# 3. Test mode — translate first 5 pages only
#    (invoke via Copilot skill in VS Code)
#    The skill runs: python src/extract.py input/charpter-4.docx --test --pages 5
#    Then translates and rebuilds automatically.

# 4. Full run — translate the entire document
#    Invoke the skill without --test flag.

# Output appears in output/ as:
#   charpter-4_translated.docx
#   charpter-4_translated.pdf
```

---

## Known Limitations (v1)

| Limitation | Impact | Planned Fix |
|---|---|---|
| Inline math position may shift to end of paragraph when text runs are collapsed | Visual only; math content preserved | v2: per-run translation with position mapping |
| Headers and footers not translated | Section headings in headers may remain Chinese | v2: iterate `doc.sections[].header` paragraphs |
| Nested tables not walked recursively | Rare in textbooks | v2: recursive cell walker |
| Scanned images with Chinese text (photos of problems) not translated | OCR out of scope | Out of scope |
| `charpter-4.docx` filename typo | Harmless; glob pattern matches all `.docx` in `input/` | Fix input filename manually if desired |

---

## Out of Scope

- Direct PDF-to-PDF translation
- Web UI or REST API
- OCR of scanned images containing Chinese text
- Perfect pixel-level PDF layout reproduction (minor reflow tolerance acceptable)
- Glossary management or translation memory
- Any external API key or paid service beyond GitHub Copilot subscription
