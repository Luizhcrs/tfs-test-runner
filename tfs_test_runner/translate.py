"""Translate test case fields to a target language.

Backends:
 - 'none' (default): pass-through. Snapshots originals as title_en/action_en/expected_en.
 - 'llm': OpenAI GPT batch translation, JSON-mode, with retries and per-chunk fallback.

Public API:
    translate_cases(cases, backend='none', target_lang='pt-BR',
                    model='gpt-4o-mini', api_key=None, progress=None) -> list[dict]
"""
from __future__ import annotations
import os, json, time
from typing import Callable

DEFAULT_MODEL = "gpt-4o-mini"
LLM_CHUNK_DEFAULT = 80
LLM_CHUNK_MAX_BYTES = 12_000


def _build_system_prompt(target_lang: str, glossary: dict | None) -> str:
    """Build LLM system prompt with optional preserved-term glossary."""
    glossary = glossary or {}
    preserved = glossary.get("preserve", [])
    notes = glossary.get("notes", "")
    parts = [
        f"You translate technical test case fields from English to {target_lang}.",
        "",
        "Hard rules:",
        "1. Output ONLY a JSON object: {\"translations\": [\"...\", \"...\"]} matching input order.",
        "2. Preserve newlines, lists, $variables, code identifiers, numbers, punctuation structure.",
        "3. Empty input -> empty output.",
        "4. Use natural target-language phrasing. Imperative tone for actions.",
    ]
    if preserved:
        parts.append(f"5. Preserve verbatim (do NOT translate) these technical terms / UI labels: {', '.join(preserved)}.")
    if notes:
        parts.append(f"6. Domain notes: {notes}")
    return "\n".join(parts)


def translate_cases(
    cases: list[dict],
    backend: str = "none",
    target_lang: str = "pt-BR",
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    glossary: dict | None = None,
    progress: Callable[[str], None] | None = None,
) -> list[dict]:
    """Translate titles + step.action + step.expected in-place. Returns same list.

    Each case + step gets _en suffixed snapshots of originals.
    """
    for c in cases:
        c["title_en"] = c.get("title", "")
        for s in c["steps"]:
            s["action_en"] = s.get("action", "")
            s["expected_en"] = s.get("expected", "")

    if backend == "none":
        for c in cases:
            c.setdefault("title", c["title_en"])
            for s in c["steps"]:
                s.setdefault("action", s["action_en"])
                s.setdefault("expected", s["expected_en"])
        return cases

    if backend == "llm":
        unique: dict[str, None] = {}
        for c in cases:
            unique.setdefault(c["title_en"], None)
            for s in c["steps"]:
                unique.setdefault(s["action_en"], None)
                unique.setdefault(s["expected_en"], None)
        unique.pop("", None)
        items = list(unique.keys())
        if progress is not None:
            progress(f"LLM: {len(items)} unique strings to translate")

        translations = _gpt_batch(items, model=model, api_key=api_key,
                                  target_lang=target_lang, glossary=glossary,
                                  progress=progress)
        tmap = dict(zip(items, translations))
        tmap[""] = ""

        for c in cases:
            c["title"] = tmap.get(c["title_en"], c["title_en"])
            for s in c["steps"]:
                s["action"] = tmap.get(s["action_en"], s["action_en"])
                s["expected"] = tmap.get(s["expected_en"], s["expected_en"])
        return cases

    raise ValueError(f"unknown backend: {backend!r} (use 'none' or 'llm')")


# ---------- LLM machinery ----------

def _make_chunks(strings: list[str], max_count: int = LLM_CHUNK_DEFAULT,
                 max_bytes: int = LLM_CHUNK_MAX_BYTES) -> list[list[str]]:
    """Split strings into chunks bounded by both count and serialized byte size."""
    chunks: list[list[str]] = []
    current: list[str] = []
    current_bytes = 0
    for s in strings:
        size = len(s.encode("utf-8")) + 4
        if current and (len(current) >= max_count or current_bytes + size > max_bytes):
            chunks.append(current)
            current, current_bytes = [], 0
        current.append(s)
        current_bytes += size
    if current:
        chunks.append(current)
    return chunks


def _gpt_call_with_retry(client, model: str, system: str, user: str,
                         max_retries: int = 3, progress=None) -> str:
    """Call Chat Completions with exponential backoff."""
    delay = 2.0
    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
            )
            return resp.choices[0].message.content or "{}"
        except Exception as e:
            last_err = e
            if progress is not None:
                progress(f"WARN: API attempt {attempt}/{max_retries} failed: {type(e).__name__}: {e}")
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
    raise RuntimeError(f"OpenAI call failed after {max_retries} attempts: {last_err}")


def _gpt_batch(strings: list[str], model: str, api_key: str | None,
               target_lang: str, glossary: dict | None, progress=None) -> list[str]:
    """Translate a batch of strings via OpenAI Chat Completions JSON mode."""
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError("Install openai: pip install 'tfs-test-runner[llm]' or pip install openai") from e

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=key)
    system = _build_system_prompt(target_lang, glossary)

    chunks = _make_chunks(strings)
    out: list[str] = []
    total = len(chunks)
    for ci, chunk in enumerate(chunks, 1):
        if progress is not None:
            progress(f"LLM chunk {ci}/{total} ({len(chunk)} strings)")
        user = "Translate this JSON array:\n" + json.dumps({"strings": chunk}, ensure_ascii=False)
        try:
            content = _gpt_call_with_retry(client, model, system, user, progress=progress)
            obj = json.loads(content)
            t = obj.get("translations", [])
            if not isinstance(t, list):
                raise ValueError("translations is not a list")
        except (RuntimeError, json.JSONDecodeError, ValueError) as e:
            if progress is not None:
                progress(f"WARN: chunk {ci} fell back to original strings: {e}")
            t = list(chunk)
        if len(t) != len(chunk):
            if progress is not None:
                progress(f"WARN: chunk {ci} length mismatch, padding with originals")
            while len(t) < len(chunk):
                t.append(chunk[len(t)])
            t = t[:len(chunk)]
        out.extend(str(x) for x in t)
    return out


def load_glossary_yaml(path: str) -> dict:
    """Load glossary YAML.

    Format:
        preserve: ["TermA", "TermB"]
        notes: "Free text added to system prompt for context."
    """
    import yaml  # type: ignore
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
