"""Translate Chinese text to English using OpenAI GPT-4o or a local Ollama model."""

import time

from openai import OpenAI, RateLimitError, APIError

import config

# Separator used to batch multiple paragraphs in a single API call.
# Chosen to be unlikely to appear in Calculus textbook text.
_PARA_SEP = "\n<<<NEXT_PARAGRAPH>>>\n"

_SYSTEM_PROMPT = (
    "You are translating a university-level Calculus textbook from Chinese to English.\n\n"
    "Rules:\n"
    "- Translate Chinese text to formal, precise academic English.\n"
    "- Preserve ALL mathematical notation, variable names, and equation references exactly as written.\n"
    "- Preserve any non-Chinese text (English words, numbers, symbols) exactly as-is.\n"
    "- The input contains multiple paragraphs separated by <<<NEXT_PARAGRAPH>>>.\n"
    "- Return the translated paragraphs in the SAME ORDER, separated by <<<NEXT_PARAGRAPH>>>.\n"
    "- Do NOT add commentary, notes, or extra content.\n"
    "- Return ONLY the translated text."
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
        else:
            if not config.OPENAI_API_KEY:
                raise EnvironmentError(
                    "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
                )
            _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def _active_model() -> str:
    """Return the model name for the active provider."""
    if config.TRANSLATION_PROVIDER == "ollama":
        return config.OLLAMA_MODEL
    return config.OPENAI_MODEL


def _call_api(text: str, retries: int = 4) -> str:
    """Send *text* to the active provider and return the response string."""
    client = _get_client()
    model = _active_model()
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            wait = 2 ** attempt
            print(f"    Rate limited. Waiting {wait}s before retry {attempt + 1}/{retries}...")
            time.sleep(wait)
        except APIError as exc:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"OpenAI API error after {retries} retries: {exc}") from exc
    raise RuntimeError("Translation failed after maximum retries.")


def translate_batch(texts: list[str]) -> list[str]:
    """Translate a list of paragraph texts in a single API call.

    Falls back to one-at-a-time translation if the batch response cannot be
    split back into the expected number of paragraphs.
    """
    if not texts:
        return []

    combined = _PARA_SEP.join(texts)
    raw = _call_api(combined)
    parts = [p.strip() for p in raw.split("<<<NEXT_PARAGRAPH>>>")]

    if len(parts) == len(texts):
        return parts

    # Fallback: translate individually to guarantee alignment
    print(
        f"    WARNING: batch returned {len(parts)} parts for {len(texts)} inputs. "
        "Falling back to individual translation."
    )
    return [_call_api(t) for t in texts]
