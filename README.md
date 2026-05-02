# Document Translator

Translate a Chinese university Calculus textbook (DOCX) into North American English while preserving all mathematical equations, images, and document structure.

**Key features**: Uses your active GitHub Copilot model for translation and AI audit — no API key required. Translation voice and tone are configurable via `translation_config.json`.

---

## Quick Start

### 1. Install dependencies
```bash
cd document-translator
pip install -r requirements.txt
```

### 2. (Optional) Set your translation style

Open `translation_config.json` and set `"active"` to the preset you want:

```json
{
  "active": "storytelling",

  "presets": {
    "storytelling": "Chinese storytelling teach-and-learn calculus textbook — conversational, everyday analogies...",
    "formal":       "Formal North American academic textbook — precise, concise, third-person...",
    "study_guide":  "Friendly undergraduate study guide — supportive, explains the why...",
    "none":         ""
  }
}
```

Change `"active"` to `"formal"`, `"study_guide"`, or `"none"` to switch instantly. See [Translation Style](#translation-style) for details.

### 3. Place your DOCX file
Copy your Chinese DOCX file to the `input/` directory:
```
input/
└── my-chapter.docx
```

### 4. Translate (choose one method below)

**Method A: Using Copilot Skill (Easiest)**

Open VS Code Copilot Chat and type:
```
@document-translator translate first 5 pages
```
or
```
@document-translator full translation
```

The skill orchestrates all steps automatically.

**Method B: Command Line**

```bash
# Extract Chinese segments
python src/extract.py input/my-chapter.docx

# Translate (uses built-in dictionary + Copilot model if available)
python src/translate.py

# Rebuild DOCX with translations + punctuation normalization
python src/rebuild.py input/my-chapter.docx

# AI audit: extract paragraphs, review in Copilot Chat, apply fixes
python src/audit.py extract output/my-chapter_translated.docx
# (Copilot reviews work/audit_segments.json → writes work/audited_segments.json)
python src/audit.py apply output/my-chapter_translated.docx

# Export to PDF (optional)
python src/to_pdf.py output/my-chapter_translated.docx
```

### 5. Find your output
- **Translated DOCX**: `output/my-chapter_translated.docx`
- **Translated PDF**: `output/my-chapter_translated.pdf` (if LibreOffice installed)

---

## How It Works

### Data Flow
```
Input DOCX
    ↓
extract.py        → Detect all Chinese text segments
    ↓
translate.py      → Apply translation dictionary
    ↓
rebuild.py        → Patch translations back into DOCX + paragraph-level
                    punctuation spacing normalization + NA formatting
    ↓
audit.py extract  → Pull all English paragraphs for AI review
    ↓
Copilot AI        → Review spacing, word boundaries, phrasing
                    writes work/audited_segments.json
    ↓
audit.py apply    → Patch AI-fixed paragraphs back into DOCX
    ↓
to_pdf.py         → Convert to PDF via LibreOffice (optional)
    ↓
Output DOCX + PDF
```

### What Gets Translated & Fixed
- ✅ All Chinese prose (chapters, definitions, theorems, proofs, examples)
- ✅ Paragraph-level punctuation spacing normalization (e.g., `"chapters ,we"` → `"chapters, we"`)
- ✅ AI audit fixes spacing, word boundaries, and phrasing after rebuild
- ✅ North American formatting applied (Times New Roman, 12pt, 1.5× line spacing)

### What Gets Preserved
- ✅ All mathematical equations (inline and display)
- ✅ Graphs, images, and diagrams
- ✅ Tables and document structure
- ✅ Page layout and formatting

---

## Test Mode

Translate only the first N pages to verify quality before processing the full document:

```bash
python src/extract.py input/my-chapter.docx --test --pages 5
python src/translate.py
python src/rebuild.py input/my-chapter.docx
python src/audit.py extract output/my-chapter_translated.docx
# (run AI audit via Copilot Chat, then:)
python src/audit.py apply output/my-chapter_translated.docx
```

Or via Copilot Chat:
```
@document-translator test mode, first 5 pages
```

---

## Compare Copilot Models

Since the tool uses your active Copilot model, you can compare translation quality:

1. **Model A**: Select in VS Code model picker (e.g., Claude Sonnet 4.6)
2. **Run**: `@document-translator test mode, first 5 pages`
3. **Inspect**: Review `output/storytelling/my-chapter_translated.docx`
4. **Reset work**: Delete `work/` folder: `rm -rf work/`
5. **Model B**: Switch model in VS Code picker (e.g., GPT-5.3-Codex)
6. **Re-run**: `@document-translator test mode, first 5 pages`
7. **Compare**: Open both outputs side-by-side

---

## Directory Structure

```
document-translator/
├── README.md                              ← You are here
├── requirements.txt                       ← Python dependencies
├── translation_config.json               ← Edit this to set translation voice/tone
├── input/
│   └── *.docx                            ← Place source files here
├── output/
│   ├── storytelling/                     ← Output when active preset = "storytelling"
│   │   ├── *_translated.docx
│   │   └── *_translated.pdf
│   ├── formal/                           ← Output when active preset = "formal"
│   │   ├── *_translated.docx
│   │   └── *_translated.pdf
│   └── study_guide/                      ← Output when active preset = "study_guide"
├── work/
│   ├── extracted_segments.json           ← Intermediate: Chinese segments
│   ├── translated_segments.json          ← Intermediate: English translations
│   ├── audit_segments.json               ← Intermediate: English paragraphs + style for AI review
│   └── audited_segments.json             ← Intermediate: AI-fixed + styled paragraphs
├── src/
│   ├── config.py                         ← Paths and formatting constants
│   ├── extract.py                        ← Extract Chinese text from DOCX
│   ├── translate.py                      ← Apply translations
│   ├── rebuild.py                        ← Patch DOCX with translations + spacing fix
│   ├── audit.py                          ← Extract paragraphs for AI review & apply fixes
│   └── to_pdf.py                         ← Convert to PDF
└── .github/
    ├── PRD/
    │   └── document-translator.md        ← Product requirements document
    └── skills/
        └── document-translator/
            └── SKILL.md                  ← Copilot skill definition
```

> **Output isolation**: each preset gets its own subfolder under `output/`. Switching `"active"` in `translation_config.json` never overwrites a previous run.

---

## Features

### Punctuation Spacing Normalization
Automatically fixes punctuation spacing at the paragraph level during rebuild:
- Removes spaces before punctuation: `"chapters ,we"` → `"chapters,we"`
- Ensures space after punctuation: `"chapters,we"` → `"chapters, we"`
- Works across segment boundaries — fixes issues between joined translation runs

### Translation Style

Control the voice and tone of the translated output via `translation_config.json`. The file uses an `"active"` key to select from named presets — no commenting/uncommenting needed, just change one word:

```json
{
  "active": "storytelling",

  "presets": {
    "storytelling": "Chinese storytelling teach-and-learn calculus textbook — conversational and engaging tone, uses everyday analogies from Chinese life, warm and encouraging, explains concepts through vivid stories and relatable examples, occasional light humour, addresses the reader directly as a fellow learner",

    "formal": "Formal North American academic textbook — precise, concise, third-person passive voice, no analogies, no humour, definitions and theorems stated rigorously",

    "study_guide": "Friendly undergraduate study guide — supportive and motivating tone, explains the 'why' behind each concept, uses 'you' and 'we', highlights common mistakes and exam tips",

    "none": ""
  }
}
```

**Built-in presets:**

| `"active"` value | Voice / Tone |
|---|---|
| `"storytelling"` | Warm, conversational, Chinese-life analogies, light humour |
| `"formal"` | Precise, academic, third-person, no analogies |
| `"study_guide"` | Supportive, explains the why, exam tips, uses "you" |
| `"none"` | No style — neutral output |

**To add your own preset**, add a new key under `"presets"` and set `"active"` to that key.

The style is applied in the **AI audit phase** only — it never changes math notation, technical terms, or sentence meaning.

### AI Audit (Post-Rebuild)
After rebuild, the Copilot model reviews every English paragraph and fixes:
- Extra spaces between words: `"We also  spent"` → `"We also spent"`
- Broken word boundaries from segment joins: `"spentconsiderable"` → `"spent considerable"`
- Missing space after sentence-ending period before capital letter
- Awkward phrasing at translation segment boundaries
- **Applies `translation_config.json` style** to rewrite prose in the desired voice
- **Does not** change meaning, math, or technical terminology

### North American Textbook Formatting
Applied automatically by `rebuild.py`:
- **Page size**: US Letter (8.5" × 11")
- **Margins**: 1 inch on all sides
- **Body font**: Times New Roman, 12pt
- **Chapter heading**: Times New Roman, 14pt, Bold
- **Section heading**: Times New Roman, 12pt, Bold
- **Line spacing**: 1.5×
- **Paragraph spacing**: 6pt after

### Math Preservation
- Inline math (`$...$` or OMML XML) → **preserved exactly**
- Display math (`$$...$$` or OMML XML blocks) → **preserved exactly**
- Variable names and operators → **never translated**

---

## Installation & Setup

### Requirements
- Python 3.9+
- `python-docx >= 1.1.0` (installed via `pip`)
- LibreOffice (optional, for PDF export)

### Install Python dependencies
```bash
cd document-translator
pip install -r requirements.txt
```

### Install LibreOffice (optional, for PDF export)
- **macOS**: `brew install libreoffice` or download from https://www.libreoffice.org/download/
- **Windows**: Download from https://www.libreoffice.org/download/
- **Linux**: `apt install libreoffice` or equivalent

---

## Usage Examples

### Example 1: Translate first 5 pages via Copilot Chat
```
@document-translator test mode, first 5 pages
```
Output: `output/my-chapter_translated.docx` (5 pages only)

### Example 2: Full translation via command line
```bash
cd document-translator
python src/extract.py input/my-chapter.docx
python src/translate.py
python src/rebuild.py input/my-chapter.docx
python src/audit.py extract output/my-chapter_translated.docx
# (Copilot reviews work/audit_segments.json → writes work/audited_segments.json)
python src/audit.py apply output/my-chapter_translated.docx
python src/to_pdf.py output/my-chapter_translated.docx
```
Output:
- `output/my-chapter_translated.docx` (full document, AI-audited)
- `output/my-chapter_translated.pdf` (full document)

### Example 3: Manual extraction only
```bash
python src/extract.py input/my-chapter.docx --test --pages 3
```
Output: `work/extracted_segments.json` (segments from first 3 pages)

---

## Troubleshooting

### ❌ "No .docx found in input/"
**Solution**: Place a `.docx` file in the `input/` directory.

### ❌ "python-docx import error"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### ❌ "work/extracted_segments.json is empty (0 segments)"
**Solution**: The document may have no detectable Chinese text. Verify:
- File is a valid DOCX
- File actually contains Chinese text (not scanned images)

### ❌ "LibreOffice not found" (when exporting PDF)
**Solution**: Install LibreOffice from https://www.libreoffice.org/download/  
**Note**: DOCX output still works without LibreOffice.

### ❌ "Rebuild fails with KeyError"
**Solution**: Segment IDs in `translated_segments.json` don't match `extracted_segments.json`. 
- Delete `work/` folder
- Re-run extraction and translation:
```bash
rm -rf work/
python src/extract.py input/my-chapter.docx
python src/translate.py
python src/rebuild.py input/my-chapter.docx
```

---

## Workflow: Edit & Re-translate

If you edit translations manually in `work/translated_segments.json`, just rebuild:

```bash
python src/rebuild.py input/my-chapter.docx
```

No need to extract or translate again — rebuild will use your manual edits.

---

## API Details

### `extract.py`
Extracts Chinese text segments and writes `work/extracted_segments.json`.

```bash
python src/extract.py input/my-chapter.docx [--test] [--pages N]
```

**Options**:
- `--test`: Enable test mode
- `--pages N`: Limit to first N pages (only in test mode)

**Output**: `work/extracted_segments.json`
```json
[
  {
    "id": "seg_00000",
    "source": "如前所述",
    "location": "body",
    "para_index": 0,
    "run_index": 0
  },
  ...
]
```

### `translate.py`
Applies translations to extracted segments.

```bash
python src/translate.py
```

**Input**: `work/extracted_segments.json`  
**Output**: `work/translated_segments.json`

**Normalization applied**:
- Removes spaces before punctuation
- Collapses multiple spaces
- Ensures space after punctuation

```json
[
  {
    "id": "seg_00000",
    "source": "如前所述",
    "translation": "As mentioned earlier"
  },
  ...
]
```

### `rebuild.py`
Patches translations back into DOCX and applies North American formatting.

```bash
python src/rebuild.py input/my-chapter.docx
```

**Input**: 
- `input/my-chapter.docx` (original)
- `work/translated_segments.json` (translations)

**Output**: `output/my-chapter_translated.docx` (formatted DOCX)

### `audit.py`
Extracts English paragraphs for Copilot AI review, then patches fixes back into the DOCX. The style from `translation_config.json` is automatically embedded into the extract output.

```bash
# Step 1: Extract paragraphs for AI review
python src/audit.py extract output/my-chapter_translated.docx

# Step 2: (Copilot reviews work/audit_segments.json → writes work/audited_segments.json)

# Step 3: Apply AI fixes back into DOCX
python src/audit.py apply output/my-chapter_translated.docx
```

**`extract` input**: `output/my-chapter_translated.docx`  
**`extract` output**: `work/audit_segments.json`

```json
{
  "style_instruction": "Chinese storytelling teach-and-learn calculus textbook...",
  "segments": [
    {
      "id": "audit_00001",
      "location": "body",
      "para_index": 1,
      "text": "In the first two chapters, we clarified..."
    }
  ]
}
```

The `style_instruction` is read from `translation_config.json` at extract time. Copilot uses it in Step 2 to apply the desired voice and tone while writing `audited_segments.json`.

**`apply` input**: `work/audited_segments.json` (written by Copilot)

```json
[
  {
    "id": "audit_00002",
    "original": "We also spentconsiderable effort",
    "fixed": "We also spent considerable effort"
  }
]
```

**`apply` output**: Updates `output/my-chapter_translated.docx` in-place  
Only paragraphs where `fixed ≠ original` are changed.

### `to_pdf.py`
Converts DOCX to PDF using LibreOffice headless.

```bash
python src/to_pdf.py output/my-chapter_translated.docx
```

**Input**: `output/my-chapter_translated.docx`  
**Output**: `output/my-chapter_translated.pdf`

---

## Advanced: Custom Translations

To manually edit translations:

1. Open `work/translated_segments.json`
2. Edit the `"translation"` field for any segment
3. Rebuild:
   ```bash
   python src/rebuild.py input/my-chapter.docx
   ```

The rebuild will patch your custom translations back into the DOCX.

---

## Advanced: Changing Translation Style

The translation style is applied during the AI audit phase, so you can switch styles and re-audit **without re-translating**.

**To switch to a different built-in preset**, just change `"active"` in `translation_config.json`:

```json
{ "active": "formal" }
```

**To add a custom preset**, add it under `"presets"` and set `"active"` to its key:

```json
{
  "active": "my_style",
  "presets": {
    "my_style": "Describe your desired voice and tone here",
    "storytelling": "..."
  }
}
```

**Workflow to re-audit with a new style (no re-translation needed):**

```bash
# 1. Change "active" in translation_config.json
# 2. Re-run the audit
python src/audit.py extract output/my-chapter_translated.docx
# (Copilot reviews work/audit_segments.json → writes work/audited_segments.json)
python src/audit.py apply output/my-chapter_translated.docx
# 3. Export PDF (optional)
python src/to_pdf.py output/my-chapter_translated.docx
```

Or via Copilot Chat after updating `translation_config.json`:
```
@document-translator re-audit with new style
```

---

## Known Limitations

| Issue | Workaround |
|---|---|
| Headers/footers not translated | Translate manually in output DOCX if needed |
| Nested tables may miss some cells | Check output; edit manually if needed |
| OCR text in images not translated | Out of scope (requires external OCR) |
| AI audit requires Copilot Chat interaction | Run `audit.py extract`, switch to Copilot Chat for the review step, then `audit.py apply` |}

---

## Contributing

To improve the translator:

1. Test on new documents
2. Report issues with specific Chinese text patterns
3. Suggest new punctuation rules or formatting options

---

## License

This project is part of the A-Team GitHub Copilot agent orchestration platform.

---

## Support

- **Skill usage**: See `.github/skills/document-translator/SKILL.md`
- **Architecture**: See `.github/PRD/document-translator.md`
- **Issues**: Check the Troubleshooting section above

---

**Ready to translate?** Start with:
```
@document-translator translate first 5 pages
```
