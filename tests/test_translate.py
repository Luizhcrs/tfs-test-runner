from tfs_test_runner.translate import (
    _make_chunks,
    _build_system_prompt,
    translate_cases,
)


def test_make_chunks_count_limit():
    items = [f"s{i}" for i in range(200)]
    chunks = _make_chunks(items, max_count=80, max_bytes=10**9)
    assert len(chunks) == 3
    assert sum(len(c) for c in chunks) == 200
    assert all(len(c) <= 80 for c in chunks)


def test_make_chunks_byte_limit():
    items = ["x" * 1000 for _ in range(20)]
    chunks = _make_chunks(items, max_count=100, max_bytes=4000)
    # Each item ~1004 bytes; ensure each chunk fits within budget+1 item slack
    assert all(sum(len(s) for s in c) <= 4000 + 1000 for c in chunks)
    assert sum(len(c) for c in chunks) == 20


def test_make_chunks_empty():
    assert _make_chunks([]) == []


def test_build_system_prompt_includes_lang():
    prompt = _build_system_prompt("pt-BR", None)
    assert "pt-BR" in prompt
    assert "JSON object" in prompt


def test_build_system_prompt_includes_glossary():
    prompt = _build_system_prompt("pt-BR", {"preserve": ["FooBar", "BazQux"], "notes": "Domain X."})
    assert "FooBar" in prompt
    assert "BazQux" in prompt
    assert "Domain X." in prompt


def test_translate_cases_passthrough():
    cases = [{
        "id": "1",
        "title": "Login flow",
        "steps": [
            {"step": "1", "action": "Open URL", "expected": "Page loads"},
            {"step": "2", "action": "Type credentials", "expected": ""},
        ],
    }]
    out = translate_cases(cases, backend="none")
    assert out is cases  # in-place
    assert cases[0]["title"] == "Login flow"
    assert cases[0]["title_en"] == "Login flow"
    assert cases[0]["steps"][0]["action"] == "Open URL"
    assert cases[0]["steps"][0]["action_en"] == "Open URL"
    assert cases[0]["steps"][1]["expected_en"] == ""


def test_translate_cases_unknown_backend():
    import pytest
    with pytest.raises(ValueError, match="unknown backend"):
        translate_cases([], backend="zzz")
