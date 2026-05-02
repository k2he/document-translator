---
description: Translates a Chinese university Calculus textbook (DOCX) into North American English using the active GitHub Copilot model. Orchestrates extract → translate → rebuild → AI audit → PDF export. No API key required.
tools:
  - run_in_terminal
  - read_file
  - create_file
  - replace_string_in_file
---

# Document Translator Skill

You are the **Document Translator** skill. Your job is to translate a Chinese Calculus DOCX file into North American English while preserving all mathematical equations, images, and document structure.

---

## Execution Protocol

Follow these phases **in order**. Do not skip a phase.

---

### Phase 0 — Locate the source DOCX

Scan the `input/` directory for `.docx` files.

```bash
ls document-translator/input/*.docx
```

If no DOCX file is found, stop and tell the user to place a `.docx` file in `document-translator/input/`.

Record the path as `DOCX_PATH` (e.g., `document-translator/input/charpter-4.docx`).

---

### Phase 1 — Install dependencies

```bash
cd document-translator && pip install -r requirements.txt -q
```

---

### Phase 2 — Extract Chinese segments

Run the extractor. If the user requested **test mode** (e.g., "test mode", "first N pages", "--test"), pass `--test --pages N`; otherwise run without flags.

**Full run:**
```bash
cd document-translator && python src/extract.py input/charpter-4.docx
```

**Test mode (e.g., first 5 pages):**
```bash
cd document-translator && python src/extract.py input/charpter-4.docx --test --pages 5
```

After the command completes, confirm how many segments were extracted.

---

### Phase 3 — Translate segments

Read the extracted segments file:

```
work/extracted_segments.json
```

The file contains a JSON array. Each element has:
- `id` — stable segment ID (e.g., `"seg_00042"`)
- `source` — Chinese text to translate
- `location` — context hint (`"body"` or `"table_N"`)
- `para_index` — paragraph index
- `run_index` — run index within paragraph

#### Translation rules

Translate **only** the `source` field value. For each segment:

1. Render the Chinese text into fluent **North American English** suitable for a university-level Calculus textbook.
2. Preserve all mathematical symbols, variable names, and notation exactly (e.g., `f(x)`, `∞`, `lim`, `∫`, `dx`).
3. Use standard North American mathematical terminology:
   - 微积分 → Calculus
   - 极限 → limit
   - 导数 → derivative
   - 积分 → integral
   - 定理 → theorem
   - 证明 → proof
   - 推论 → corollary
   - 引理 → lemma
   - 定义 → definition
   - 命题 → proposition
   - 注记 / 注 → remark
   - 例 → Example
   - 解 → Solution
4. Keep translations concise — do not add explanations or commentary.
5. Do **not** translate mathematical expressions that appear inline (numbers, operators, LaTeX-style notation, variable names).

#### Output format

Write the translated segments to `work/translated_segments.json` as a JSON array where each element is:

```json
{
  "id": "<same id as source>",
  "source": "<original Chinese text>",
  "translation": "<English translation>"
}
```

Produce **all** segments from `extracted_segments.json` in the same order. Do not drop or reorder segments.

Create the `work/` directory first if it does not exist:

```bash
mkdir -p document-translator/work
```

Write the file using the `create_file` tool or `replace_string_in_file` if the file already exists.

---

### Phase 4 — Rebuild the translated DOCX

```bash
cd document-translator && python src/rebuild.py input/charpter-4.docx
```

The rebuild script:
1. Patches all translated segments back into the DOCX document
2. **Automatically normalizes punctuation spacing** across segment boundaries
   - Removes spaces before Western punctuation (,.)
   - Ensures proper spacing after punctuation
   - Example: "chapters ,we clarified" → "chapters, we clarified"
3. Applies North American textbook formatting (Times New Roman, 1.5× line spacing, margins, etc.)

Confirm the output path printed by the script (e.g., `output/charpter-4_translated.docx`).

---

### Phase 4.5 — AI Audit & Spacing Fix

This phase uses the active Copilot model to review every English paragraph for spacing, punctuation, and natural phrasing issues that could not be fixed deterministically.

#### Step 1 — Extract paragraphs

```bash
cd document-translator && python src/audit.py extract output/charpter-4_translated.docx
```

This writes `work/audit_segments.json` — a JSON array of all auditable paragraphs:

```json
[
  {
    "id": "audit_00000",
    "location": "body",
    "para_index": 0,
    "text": "In the first two chapters, we clarified..."
  }
]
```

#### Step 2 — AI Review: Read and fix each paragraph

Read `work/audit_segments.json`. For **every element** produce a corrected entry and write all results to `work/audited_segments.json`.

**Audit rules — fix only these issues:**
1. Remove extra spaces between words (e.g., `"We also  spent"` → `"We also spent"`)
2. Ensure single space after sentence-ending period before a capital letter
3. Fix spacing around punctuation (comma, period, semicolon, colon)
4. Remove leading/trailing whitespace per paragraph
5. Fix obviously broken word boundaries (e.g., `"spentconsiderable"` → `"spent considerable"`)
6. Ensure natural English phrasing — fix awkward joins between translated segments

**Do NOT:**
- Change mathematical notation, formulas, or variable names
- Change technical terminology (derivative, limit, theorem, etc.)
- Add, remove, or reorder sentences
- Alter the meaning of the text
- Fix stylistic preferences — only fix clear errors

**Output format** — write `work/audited_segments.json`:

```json
[
  {
    "id": "audit_00000",
    "original": "In the first two chapters ,we clarified ...",
    "fixed": "In the first two chapters, we clarified..."
  }
]
```

Include **every** paragraph from `audit_segments.json` in the output — even unchanged ones (set `"fixed"` equal to `"original"` for those).

Write the file using the `create_file` tool or `replace_string_in_file` if it already exists:

```
document-translator/work/audited_segments.json
```

#### Step 3 — Apply fixes

```bash
cd document-translator && python src/audit.py apply output/charpter-4_translated.docx
```

This patches only paragraphs where `fixed ≠ original` back into the DOCX. Confirm the number of fixes applied.

---

### Phase 5 — Export to PDF

```bash
cd document-translator && python src/to_pdf.py output/charpter-4_translated.docx
```

If LibreOffice is not installed, tell the user:

> LibreOffice is required for PDF export. Download from https://www.libreoffice.org/download/ and re-run Phase 5.

---

### Phase 6 — Summary

Report to the user:

| Item | Path |
|---|---|
| Translated DOCX | `output/<stem>_translated.docx` |
| Translated PDF | `output/<stem>_translated.pdf` |
| Extracted segments | `work/extracted_segments.json` |
| Translated segments | `work/translated_segments.json` |
| Audit input | `work/audit_segments.json` |
| Audit output | `work/audited_segments.json` |
| Segment count | N segments translated, M paragraphs audited |
| Mode | Full run / Test mode (pages 1–N) |

If test mode was used, remind the user they can switch Copilot models and re-run (deleting `work/` first) to compare translation quality.

---

## Error Handling

| Error | Resolution |
|---|---|
| No `.docx` in `input/` | Ask user to place DOCX in `input/` |
| `python-docx` import error | Run `pip install python-docx` |
| `work/extracted_segments.json` empty (0 segments) | The document may have no detectable Chinese text — verify the file |
| `work/translated_segments.json` missing after Phase 3 | Re-run Phase 3 |
| `work/audit_segments.json` missing before Phase 4.5 Step 2 | Run: `python src/audit.py extract output/<stem>_translated.docx` |
| `work/audited_segments.json` missing before Phase 4.5 Step 3 | Re-run Phase 4.5 Step 2 (AI review) |
| `AI audit made no changes` message | All paragraphs were already correct — proceed to Phase 5 |
| LibreOffice not found | Prompt user to install; DOCX output is still valid |
| Rebuild fails with KeyError on segment ID | Segment IDs in `translated_segments.json` don't match `extracted_segments.json` — re-translate |

---

## Model Comparison Workflow

To compare two Copilot models on the same test excerpt:

1. **Model A**: Select in VS Code model picker → invoke skill with `--test --pages 5` → inspect output.
2. **Reset**: Delete `work/` folder: `rm -rf document-translator/work/`
3. **Model B**: Switch model in picker → invoke skill again with same test mode.
4. Compare `output/<stem>_translated.docx` side-by-side.

Recommended test range: include at least one **theorem proof** (math-heavy) and one **worked example** (mixed prose + math).
