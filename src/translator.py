"""Translate Chinese text to English using Google Gemini or a local Ollama model."""

import time

from openai import OpenAI, RateLimitError, APIError
from tqdm import tqdm

import config

# Separator used to batch multiple paragraphs in a single API call.
# Uses a numbered format so the model is less likely to echo or split it.
_PARA_SEP = "\n[[[PARAGRAPH_BREAK]]]\n"

_SYSTEM_PROMPT = (
    "You are translating a university-level Calculus textbook from Chinese to English.\n\n"
    "Rules:\n"
    "- Translate Chinese text to formal, precise academic English.\n"
    "- Preserve ALL mathematical notation, variable names, and equation references exactly as written.\n"
    "- Preserve any non-Chinese text (English words, numbers, symbols) exactly as-is.\n"
    "- The input contains multiple paragraphs separated by the exact token [[[PARAGRAPH_BREAK]]].\n"
    "- Return the translated paragraphs in the SAME ORDER, each separated by [[[PARAGRAPH_BREAK]]].\n"
    "- Output ONLY the translated text and [[[PARAGRAPH_BREAK]]] tokens. Nothing else.\n"
    "- Do NOT add commentary, numbering, bullets, or extra content."
)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Return an OpenAI-compatible client for the configured provider."""
    global _client
    if _client is None:
        if config.TRANSLATION_PROVIDER == "ollama":
            # Ollama exposes an OpenAI-compatible API — no real key needed.
            _client = OpenAI(
                base_url=config.OLLAMA_BASE_URL,
                api_key="ollama",
            )
        elif config.TRANSLATION_PROVIDER == "gemini":
            if not config.GOOGLE_API_KEY:
                raise EnvironmentError(
                    "GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key."
                )
            # Gemini exposes an OpenAI-compatible endpoint.
            _client = OpenAI(
                base_url=config.GEMINI_BASE_URL,
                api_key=config.GOOGLE_API_KEY,
            )
        else:
            raise EnvironmentError(
                f"Unknown TRANSLATION_PROVIDER '{config.TRANSLATION_PROVIDER}'. "
                "Valid options: gemini, ollama"
            )
    return _client


def _active_model() -> str:
    """Return the model name for the active provider."""
    if config.TRANSLATION_PROVIDER == "ollama":
        return config.OLLAMA_MODEL
    return config.GEMINI_MODEL


def _call_api(text: str, retries: int = 6) -> str:
    """Send *text* to the active provider and return the response string."""
    client = _get_client()
    model = _active_model()
    for attempt in range(retries):
        try:
            char_count = len(text)
            tqdm.write(f"  → Sending request to {model} ({char_count} chars)...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,
            )
            result = response.choices[0].message.content.strip()
            tqdm.write(f"  ✓ Response received ({len(result)} chars).")
            return result
        except RateLimitError:
            wait = min(15 * (2 ** attempt), 120)  # cap at 2 minutes
            tqdm.write(f"  ⚠ Rate limited. Waiting {wait}s (retry {attempt + 1}/{retries})...")
            time.sleep(wait)
        except APIError as exc:
            if attempt < retries - 1:
                wait = min(5 * (2 ** attempt), 60)
                tqdm.write(f"  ⚠ API error, retrying in {wait}s: {exc}")
                time.sleep(wait)
            else:
                raise RuntimeError(f"API error after {retries} retries: {exc}") from exc
    raise RuntimeError("Translation failed after maximum retries.")


def translate_batch(texts: list[str]) -> list[str]:
    """Translate a list of paragraph texts in a single API call.

    Falls back to one-at-a-time translation with a delay between calls if the
    batch response cannot be split back into the expected number of paragraphs.
    """
    if not texts:
        return []

    combined = _PARA_SEP.join(texts)
    raw = _call_api(combined)
    parts = [p.strip() for p in raw.split("[[[PARAGRAPH_BREAK]]]") if p.strip()]

    if len(parts) == len(texts):
        return parts

    # Fallback: translate individually with a small delay to respect rate limits
    print(
        f"    WARNING: batch returned {len(parts)} parts for {len(texts)} inputs. "
        "Falling back to individual translation."
    )
    results = []
    for i, t in enumerate(texts, 1):
        tqdm.write(f"    Translating paragraph {i}/{len(texts)} individually...")
        results.append(_call_api(t))
        time.sleep(1)  # 1s pause between individual calls to avoid rate limits
    return results
