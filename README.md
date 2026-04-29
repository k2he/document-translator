# Document Translator

A Python tool that translates Chinese Calculus textbooks (DOCX format) into English, while preserving all mathematical equations, graphs, images, and formatting. Outputs both a translated DOCX and a PDF.

Supports two translation backends:
- **Google Gemini** — cloud-based, highest quality
- **Ollama (local)** — fully offline, no API key required (recommended model: `qwen2.5:72b`)

---

## How It Works

1. Reads `.docx` files from the `input/` directory
2. Detects paragraphs and table cells containing Chinese text
3. Translates them in batches via Google Gemini or a local Ollama model
4. Writes translations back into the document — OMML math equations and images are never touched
5. Saves a translated `.docx` and converts it to `.pdf` via LibreOffice

---

## Prerequisites

- Python 3.10+
- [UV](https://docs.astral.sh/uv/) (Python package manager)
- [LibreOffice](https://www.libreoffice.org/download/) (for PDF export)
- **Gemini provider**: A Google AI Studio API key (get one free at https://aistudio.google.com/app/apikey)
- **Ollama provider**: [Ollama](https://ollama.com) installed locally with `qwen3.6:35b` pulled (no API key needed)

---

## Translation Providers

The tool supports two providers, switchable via the `TRANSLATION_PROVIDER` variable in `.env`.

| Provider | Setting | Best for |
|---|---|---|
| **Google Gemini 2.5 Pro** | `TRANSLATION_PROVIDER=gemini` | Best quality, requires API key and internet |
| **Ollama (local)** | `TRANSLATION_PROVIDER=ollama` | Offline, private, no API cost |

### Which Ollama model to use?

**Recommended: `qwen3.6:35b`** — Alibaba's Qwen3 is the latest generation, with significantly improved Chinese→English translation quality over Qwen2.5. It handles academic register, mathematical terminology, and mixed Chinese/formula text well.

| Model | VRAM | Quality |
|---|---|---|
| `qwen3:72b` | ~45 GB | Best quality |
| `qwen3.6:35b` | ~22 GB | **Recommended** — excellent quality, practical VRAM |
| `qwen3:14b` | ~10 GB | Good — runs on 16 GB RAM |
| `qwen3:8b` | ~6 GB | Acceptable for lighter use |

Pull your chosen model before running:
```bash
ollama pull qwen3:32b
```

---

## Setup

### 1. Install UV

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or via pip: `pip install uv`

### 2. Install project dependencies

```bash
uv sync
```

This creates a `.venv` and installs all dependencies in one step.

### 3. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and set your key:

```
GOOGLE_API_KEY=AIza...
```

Optional settings in `.env`:

| Variable | Default | Description |
|---|---|---|
| `TRANSLATION_PROVIDER` | `gemini` | `gemini` or `ollama` |
| `GOOGLE_API_KEY` | — | **Required when using Gemini.** Google AI Studio key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `GEMINI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` | Gemini API endpoint |
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama API endpoint |
| `OLLAMA_MODEL` | `qwen3.6:35b` | Ollama model to use |
| `INPUT_DIR` | `input` | Folder containing source `.docx` files |
| `OUTPUT_DIR` | `output` | Folder where translated files are saved |

### 4. Install LibreOffice

Download and install from https://www.libreoffice.org/download/

- **macOS**: Install the `.dmg` to `/Applications/LibreOffice.app` (default location, detected automatically)
- **Windows**: Install to `C:\Program Files\LibreOffice` (default location, detected automatically)

### 5. (Optional) Set up Ollama for local translation

If you prefer local/offline translation, install [Ollama](https://ollama.com) and pull the recommended model:

```bash
ollama pull qwen3:32b
```

Then set in `.env`:
```
TRANSLATION_PROVIDER=ollama
OLLAMA_MODEL=qwen3:32b
```

No API key is required when using Ollama.

---

## Usage

### 1. Add your chapter files

Copy your `.docx` chapter files into the `input/` directory:

```
input/
├── chapter-1.docx
├── chapter-2.docx
└── charpter-4-word.docx
```

### 2. Run the translator

```bash
uv run python main.py
```

### 3. Collect output

Translated files are saved to `output/`:

```
output/
├── chapter-1_translated.docx
├── chapter-1_translated.pdf
├── chapter-2_translated.docx
├── chapter-2_translated.pdf
└── ...
```

---

## Project Structure

```
document-translator/
├── src/
│   ├── docx_parser.py     # Detects Chinese text; skips OMML math / images
│   ├── translator.py      # Batches paragraphs → Gemini or Ollama; handles retries
│   ├── docx_builder.py    # Writes translations back into the DOCX
│   └── pdf_exporter.py    # Converts DOCX → PDF via LibreOffice (headless)
├── main.py                # Entry point — orchestrates the pipeline
├── config.py              # Loads settings from .env
├── pyproject.toml
├── uv.lock
├── .env.example
└── input/                 # Drop .docx files here before running
```

---

## Notes

- **Math equations are always preserved.** OMML (`<m:oMath>`) elements are XML siblings of text runs and are never modified by the translation step.
- **Images, graphs, and diagrams are preserved.** They are binary blobs in the DOCX XML and pass through untouched.
- PDF conversion requires LibreOffice. If it is not installed, the tool still saves the translated DOCX and prints a warning.
- Headers and footers are not translated in v1.
