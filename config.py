import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# --- Provider selection ---
# Set TRANSLATION_PROVIDER=gemini to use Google Gemini (default).
# Set TRANSLATION_PROVIDER=ollama to use a local Ollama model.
TRANSLATION_PROVIDER: str = os.environ.get("TRANSLATION_PROVIDER", "gemini").lower()

# --- Gemini settings (used when TRANSLATION_PROVIDER=gemini) ---
# Uses Google AI Studio API key with the OpenAI-compatible Gemini endpoint.
GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_BASE_URL: str = os.environ.get(
    "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
)

# --- Ollama settings ---
OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "qwen3.6:35b")

# --- Shared settings ---
INPUT_DIR: str = os.environ.get("INPUT_DIR", "input")
OUTPUT_DIR: str = os.environ.get("OUTPUT_DIR", "output")

# --- Concurrency ---
# Number of parallel API calls. Keep <= 3 on Gemini free tier (15 RPM limit).
MAX_WORKERS: int = int(os.environ.get("MAX_WORKERS", "3"))
