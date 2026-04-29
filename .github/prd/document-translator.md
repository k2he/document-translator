# PRD: Chinese Calculus Textbook Translator

**Version:** 1.0  
**Date:** April 29, 2026  
**Status:** Approved

---

## Problem Statement

A Chinese university-level Calculus textbook needs to be translated into English. The book is available in both PDF and Microsoft Word (DOCX) formats. It contains Chinese prose (chapter text, definitions, theorems, proofs) mixed with mathematical equations, graphs, diagrams, images, and tables.

Currently there is no automated pipeline to translate such a document while preserving its mathematical content, layout, and formatting. Manual translation is time-consuming and error-prone. General-purpose translation tools (e.g., Google Translate file upload) corrupt or silently drop mathematical notation.

---

## Solution

Build a Python tool that:

1. Reads source `.docx` chapter files from an input directory
2. Identifies paragraphs containing Chinese text
3. Translates only the Chinese text via OpenAI GPT-4o
4. Leaves all OMML math equations, images, graphs, and tables structurally untouched
5. Rebuilds the document as a translated DOCX
6. Converts the translated DOCX to PDF via LibreOffice (headless)

---

## Format Analysis: DOCX vs PDF

The book is available in both formats. The pipeline is built around **DOCX**, not PDF.

| Criterion | DOCX ✅ | PDF ❌ |
|---|---|---|
| Math equations | Stored as OMML XML nodes — trivially detected and skipped | Rendered as glyphs/images — no semantic boundary, cannot be isolated |
| Images / graphs | Binary blobs embedded in XML — automatically bypassed | Mixed with text rendering layers — hard to separate |
| Text extraction | Clean paragraph runs via `python-docx` — full sentence context preserved | Character-level with positional noise — sentence structure lost |
| Layout reconstruction | Styles, headings, and table structure preserved; DOCX → PDF via LibreOffice (free, cross-platform) | No reliable free tool to replace text in a PDF at the right position |
| Cross-platform tooling | LibreOffice available on macOS and Windows | PDF manipulation libraries (PyMuPDF etc.) struggle with CJK font reflow |

**Verdict**: Process DOCX → translate in-place → output translated DOCX + PDF via LibreOffice.  
PDF is the final delivery format; DOCX is the processing intermediary.

---

## Goals

### In Scope

- Translate all Chinese text in body paragraphs and table cells to English
- Preserve OMML math equations, images, graphs, and inline symbols untouched
- Batch process all `.docx` files in an input directory (full multi-chapter book)
- Output one translated DOCX and one PDF per input file
- Cross-platform support: macOS and Windows

### Out of Scope

- Direct PDF-to-PDF translation (see Format Analysis above)
- Web UI or REST API
- OCR of scanned images containing Chinese text
- Perfect pixel-level PDF layout reproduction (minor layout tolerance acceptable)
- Glossary management or translation memory
- Headers and footers translation (v1)

---

## User Stories

1. **As a reader**, I want to read the Calculus textbook in English so I can understand the content without knowing Chinese.
2. **As a translator**, I want the tool to automatically skip math equations so I do not have to manually protect them before or after translation.
3. **As a user**, I want both DOCX and PDF output so I can review the DOCX and distribute the PDF.
4. **As a developer**, I want a simple Python script I can run locally on macOS and Windows without a web server.

---

## Technical Architecture

### Data Flow

```
input/*.docx
    → docx_parser   (identify paragraphs with Chinese text)
    → translator    (batch GPT-4o calls, 20 paragraphs per request)
    → docx_builder  (write translations back; preserve OMML / images)
    → save *_translated.docx
    → pdf_exporter  (LibreOffice headless subprocess)
    → output/*_translated.docx
    → output/*_translated.pdf
```

### Modules

| Module | File | Responsibility |
|---|---|---|
| Parser | `src/docx_parser.py` | Load DOCX; walk paragraphs; detect Chinese text; expose translatable segments |
| Translator | `src/translator.py` | Batch paragraphs into GPT-4o calls using a `<<<NEXT_PARAGRAPH>>>` separator; retry on rate-limit |
| Builder | `src/docx_builder.py` | Write translated text back into runs; OMML / image elements are untouched because they are not `<w:r>` runs |
| PDF Exporter | `src/pdf_exporter.py` | `soffice --headless --convert-to pdf` subprocess; auto-detect LibreOffice path on Mac/Windows |
| Entrypoint | `main.py` | Glob `INPUT_DIR` for `.docx` files; orchestrate the four modules per file |
| Config | `config.py` | Load `OPENAI_API_KEY`, model name, and directory paths from `.env` |

### Math Equation Preservation Detail

DOCX stores inline math as `<m:oMath>` XML elements and display math as `<m:oMathPara>` elements. These are siblings of `<w:r>` (text run) elements within `<w:p>` (paragraph) nodes. `python-docx`'s `paragraph.runs` only yields `<w:r>` elements — OMML elements are never returned and therefore never modified. Modifying `.text` on a run touches only `<w:t>` nodes inside `<w:r>` nodes.

**Consequence**: A paragraph that mixes Chinese prose with inline math will have its text runs translated and its OMML elements preserved in place. In v1, translated text is collapsed into the first run; inline math elements retain their position in the XML but may render after the translated sentence. This is a known v1 limitation.

---

## Configuration

All configuration lives in a `.env` file at the project root (gitignored).

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. OpenAI API key. |
| `OPENAI_MODEL` | `gpt-4o` | Model used for translation. |
| `INPUT_DIR` | `input` | Directory containing source `.docx` files. |
| `OUTPUT_DIR` | `output` | Directory for translated DOCX and PDF output. |

Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` before running.

---

## Dependencies

| Package | Purpose |
|---|---|
| `openai >= 1.0.0` | GPT-4o API client |
| `python-docx >= 1.1.0` | DOCX read / write |
| `python-dotenv >= 1.0.0` | `.env` file loading |
| LibreOffice (system install) | DOCX → PDF conversion via headless subprocess |

Install Python packages: `pip install -r requirements.txt`  
Install LibreOffice: https://www.libreoffice.org/download/

---

## Running the Tool

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

# 3. Place input files
# Copy .docx chapter files into the input/ directory

# 4. Run
python main.py
```

Output files appear in `output/` as `<name>_translated.docx` and `<name>_translated.pdf`.

---

## Known Limitations (v1)

| Limitation | Impact | Planned Fix |
|---|---|---|
| Inline math position may shift to end of paragraph after text collapse | Visual only; math content preserved | v2: per-run translation with position mapping |
| Headers and footers not translated | Section headings in header may remain Chinese | v2: iterate `doc.sections[].header` paragraphs |
| Nested tables not supported | Rare in textbooks | v2: recursive cell walker |
| Scanned images with Chinese text (photos) not translated | OCR out of scope | Out of scope |
