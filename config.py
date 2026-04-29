import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# --- Provider selection ---
# Set TRANSLATION_PROVIDER=ollama to use a local Ollama model instead of OpenAI.
TRANSLATION_PROVIDER: str = os.environ.get("TRANSLATION_PROVIDER", "openai").lower()

# --- OpenAI settings ---
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o")

# --- Ollama settings ---
OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "qwen3.6:35b")

# --- Shared settings ---
INPUT_DIR: str = os.environ.get("INPUT_DIR", "input")
OUTPUT_DIR: str = os.environ.get("OUTPUT_DIR", "output")
