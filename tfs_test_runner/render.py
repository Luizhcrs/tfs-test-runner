"""Render translated cases + phase data to single-file HTML via Jinja2."""
from __future__ import annotations
import base64, json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


HERE = Path(__file__).parent


def _logo_data_url(logo_path: str | None) -> str | None:
    """Return data URL for logo, or None if no logo file is provided."""
    if not logo_path:
        return None
    p = Path(logo_path)
    if not p.exists():
        return None
    data = p.read_bytes()
    suffix = p.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "svg": "image/svg+xml", "gif": "image/gif"}.get(suffix, "image/png")
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def _safe_json(obj) -> str:
    """JSON for embedding inside <script>. Escapes </, <!-- and U+2028/U+2029."""
    s = json.dumps(obj, ensure_ascii=False)
    return (s.replace("</", "<\\/")
             .replace("<!--", "<\\!--")
             .replace(chr(0x2028), "\\u2028")
             .replace(chr(0x2029), "\\u2029"))


def _summary(phase_data: list[dict]) -> tuple[int, int]:
    cases = sum(len(p.get("cases", [])) for p in phase_data)
    steps = sum(len(c.get("steps", [])) for p in phase_data for c in p.get("cases", []))
    return cases, steps


def render(phase_data: list[dict],
           output: str | Path,
           logo: str | None = None,
           force: bool = True,
           page_title: str = "Test Execution Plan",
           subtitle: str | None = None) -> Path:
    """Render phase_data to a single-file HTML at output path.

    Args:
        phase_data: list of {id, title, level, desc, cases:[...]}
        output: destination .html path
        logo: optional path to logo image (PNG/JPG/SVG)
        force: overwrite if file exists
        page_title: appears in <title>, header h1, and PDF cover
        subtitle: shown next to header h1; auto-derived from totals if None
    """
    out = Path(output)
    if out.exists() and not force:
        raise FileExistsError(f"{out} already exists (force=False)")

    cases_n, steps_n = _summary(phase_data)
    if subtitle is None:
        subtitle = f"{cases_n} case{'s' if cases_n != 1 else ''} · {steps_n} step{'s' if steps_n != 1 else ''}"

    env = Environment(
        loader=FileSystemLoader(str(HERE / "template")),
        autoescape=select_autoescape(["html"]),
        variable_start_string="{{",
        variable_end_string="}}",
    )
    tpl = env.get_template("plano.html.j2")
    html = tpl.render(
        data_json=_safe_json(phase_data),
        logo_url=_logo_data_url(logo) or "",
        page_title=page_title,
        subtitle=subtitle,
    )
    out.write_text(html, encoding="utf-8")
    return out
