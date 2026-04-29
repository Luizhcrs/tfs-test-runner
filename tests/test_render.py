import json
from pathlib import Path
import pytest

from tfs_test_runner.render import render, _safe_json, _logo_data_url


def test_safe_json_escapes_script_close():
    obj = {"x": "hello </script> world"}
    out = _safe_json(obj)
    assert "</script>" not in out
    assert "<\\/script>" in out


def test_safe_json_escapes_html_comment_open():
    obj = {"x": "before <!-- after"}
    out = _safe_json(obj)
    assert "<!--" not in out
    assert "<\\!--" in out


def test_safe_json_escapes_line_separators():
    obj = {"x": f"before{chr(0x2028)}after{chr(0x2029)}end"}
    out = _safe_json(obj)
    assert chr(0x2028) not in out
    assert chr(0x2029) not in out
    assert "\\u2028" in out
    assert "\\u2029" in out


def test_safe_json_round_trip_preserves_data():
    obj = {"a": "ok", "list": [1, 2, "três"]}
    out = _safe_json(obj)
    parsed = json.loads(out)
    assert parsed == obj


def test_logo_data_url_none_for_missing():
    assert _logo_data_url(None) is None
    assert _logo_data_url("/nonexistent/path.png") is None


def test_render_writes_html(tmp_path: Path):
    phase_data = [{
        "id": "p1", "title": "Phase 1", "level": "easy",
        "desc": "smoke", "cases": [{
            "id": "1", "title": "Case", "title_en": "Case",
            "assigned": "u", "state": "Design", "area": "X",
            "steps": [{"step": "1", "action": "do", "action_en": "do",
                       "expected": "ok", "expected_en": "ok"}]
        }]
    }]
    out = tmp_path / "plan.html"
    render(phase_data, out, page_title="My Test Plan")
    html = out.read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "Phase 1" in html
    assert "Case" in html
    assert "My Test Plan" in html


def test_render_subtitle_auto():
    """When subtitle is None, render derives it from totals."""
    phase_data = [{
        "id": "p1", "title": "P1", "level": "med", "desc": "",
        "cases": [
            {"id": "1", "title": "T1", "steps": [{"step": "1", "action": "a", "expected": ""}]},
            {"id": "2", "title": "T2", "steps": [{"step": "1", "action": "a", "expected": ""},
                                                  {"step": "2", "action": "b", "expected": ""}]},
        ],
    }]
    out = Path("test_render_subtitle_auto.html")
    try:
        render(phase_data, out)
        html = out.read_text(encoding="utf-8")
        assert "2 cases" in html
        assert "3 steps" in html
    finally:
        out.unlink(missing_ok=True)


def test_render_force_overwrite(tmp_path: Path):
    out = tmp_path / "plan.html"
    out.write_text("existing", encoding="utf-8")
    with pytest.raises(FileExistsError):
        render([], out, force=False)
    render([], out)
    assert "existing" not in out.read_text(encoding="utf-8")


# ---------- v1.1: status-in-PDF toggle ----------

def _render_html(tmp_path: Path) -> str:
    phase_data = [{
        "id": "p1", "title": "P1", "level": "easy", "desc": "",
        "cases": [{
            "id": "1", "title": "Case", "title_en": "Case",
            "assigned": "", "state": "", "area": "",
            "steps": [{"step": "1", "action": "a", "action_en": "a",
                       "expected": "", "expected_en": ""}],
        }],
    }]
    out = tmp_path / "plan.html"
    render(phase_data, out)
    return out.read_text(encoding="utf-8")


def test_v11_status_in_pdf_markup_present(tmp_path: Path):
    html = _render_html(tmp_path)
    assert 'id="toggle-status-pdf"' in html
    assert ".show-status-pdf" in html
    assert "data-pdf-summary" in html


# ---------- v1.2: blank xlsx template ----------

def test_v12_blank_template_exists_and_parses():
    from pathlib import Path as _P
    from tfs_test_runner.parse import parse_xlsx
    blank = _P(__file__).parent.parent / "examples" / "blank-template.xlsx"
    assert blank.exists(), "examples/blank-template.xlsx is missing"
    cases = parse_xlsx(blank)
    assert len(cases) >= 1
    for c in cases:
        assert c["id"]
        assert c["title"]
        assert len(c["steps"]) >= 1


# ---------- v1.3: theme system + settings panel ----------

def test_v13_theme_css_variables_present(tmp_path: Path):
    html = _render_html(tmp_path)
    assert ':root[data-theme="light"]' in html
    assert ':root[data-theme="dark"]' in html
    assert "prefers-color-scheme: light" in html


def test_v13_settings_panel_markup_present(tmp_path: Path):
    html = _render_html(tmp_path)
    assert 'id="settings-overlay"' in html
    assert 'id="open-settings"' in html
    assert 'id="settings-close"' in html
    # Three theme radios:
    assert 'value="auto"' in html
    assert 'value="light"' in html
    assert 'value="dark"' in html


# ---------- Storage key migration (v1.x → tfs-*) ----------

def test_storage_keys_use_new_prefix(tmp_path: Path):
    html = _render_html(tmp_path)
    assert '"tfs-tests-v1"' in html
    assert '"tfs-imgs"' in html
    # Migration code references the legacy names but only inside the migrate IIFE:
    assert "migrateLegacyImagesIfAny" in html
