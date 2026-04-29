# Document Translator

A Python tool that translates Chinese Calculus textbooks (DOCX format) into English, while preserving all mathematical equations, graphs, images, and formatting. Outputs both a translated DOCX and a PDF.

Supports two translation backends:
- **OpenAI GPT-4o** — cloud-based, highest quality
- **Ollama (local)** — fully offline, no API key required (recommended model: `qwen2.5:72b`)

---

## How It Works

1. Reads `.docx` files from the `input/` directory
2. Detects paragraphs and table cells containing Chinese text
3. Translates them in batches via OpenAI GPT-4o or a local Ollama model
4. Writes translations back into the document — OMML math equations and images are never touched
5. Saves a translated `.docx` and converts it to `.pdf` via LibreOffice

---

## Prerequisites

- Python 3.10+
- [LibreOffice](https://www.libreoffice.org/download/) (for PDF export)
- **OpenAI provider**: An OpenAI API key with access to `gpt-4o`
- **Ollama provider**: [Ollama](https://ollama.com) installed locally with `qwen2.5:72b` pulled (no API key needed)

---

## Translation Providers

The tool supports two providers, switchable via the `TRANSLATION_PROVIDER` variable in `.env`.

| Provider | Setting | Best for |
|---|---|---|
| **OpenAI GPT-4o** | `TRANSLATION_PROVIDER=openai` | Best quality, requires API key and internet |
| **Ollama (local)** | `TRANSLATION_PROVIDER=ollama` | Offline, private, no API cost |

### Which Ollama model to use?

**Recommended: `qwen2.5:72b`** — Alibaba's Qwen2.5 is purpose-built for Chinese language tasks and matches GPT-4 quality on Chinese→English academic translation. It understands mathematical terminology and academic register.

| Model | VRAM | Quality |
|---|---|---|
| `qwen2.5:72b` | ~45 GB | Best — recommended |
| `qwen2.5:32b` | ~20 GB | Very good |
| `qwen2.5:14b` | ~10 GB | Good — runs on 16 GB RAM |

Pull your chosen model before running:
```bash
ollama pull qwen2.5:72b
```

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and set your key:

```
OPENAI_API_KEY=sk-...
```

Optional settings in `.env`:

| Variable | Default | Description |
|---|---|---|
| `TRANSLATION_PROVIDER` | `openai` | `openai` or `ollama` |
| `OPENAI_API_KEY` | — | **Required when using OpenAI.** Your API key |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama API endpoint |
| `OLLAMA_MODEL` | `qwen2.5:72b` | Ollama model to use |
| `INPUT_DIR` | `input` | Folder containing source `.docx` files |
| `OUTPUT_DIR` | `output` | Folder where translated files are saved |

### 3. Install LibreOffice

Download and install from https://www.libreoffice.org/download/

- **macOS**: Install the `.dmg` to `/Applications/LibreOffice.app` (default location, detected automatically)
- **Windows**: Install to `C:\Program Files\LibreOffice` (default location, detected automatically)

### 4. (Optional) Set up Ollama for local translation

If you prefer local/offline translation, install [Ollama](https://ollama.com) and pull the recommended model:

```bash
ollama pull qwen2.5:72b
```

Then set in `.env`:
```
TRANSLATION_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:72b
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
python main.py
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
│   ├── translator.py      # Batches paragraphs → GPT-4o or Ollama; handles retries
│   ├── docx_builder.py    # Writes translations back into the DOCX
│   └── pdf_exporter.py    # Converts DOCX → PDF via LibreOffice (headless)
├── main.py                # Entry point — orchestrates the pipeline
├── config.py              # Loads settings from .env
├── requirements.txt
├── .env.example
└── input/                 # Drop .docx files here before running
```

---

## Notes

- **Math equations are always preserved.** OMML (`<m:oMath>`) elements are XML siblings of text runs and are never modified by the translation step.
- **Images, graphs, and diagrams are preserved.** They are binary blobs in the DOCX XML and pass through untouched.
- PDF conversion requires LibreOffice. If it is not installed, the tool still saves the translated DOCX and prints a warning.
- Headers and footers are not translated in v1.
