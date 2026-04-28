"""CLI entry point: xlsx -> translated HTML test plan."""
from __future__ import annotations
import sys, json
from pathlib import Path

import click

from . import __version__
from .parse import parse_xlsx
from .translate import translate_cases, load_glossary_yaml, DEFAULT_MODEL
from .classify import assign_phases, load_yaml_phases, apply_yaml_phases
from .render import render


def _log(msg: str):
    print(f"[tfs-test-runner] {msg}", file=sys.stderr)


@click.command()
@click.version_option(version=__version__, prog_name="tfs-test-runner")
@click.argument("input_xlsx", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", type=click.Path(), default="test-plan.html",
              help="Output HTML path. Default: test-plan.html")
@click.option("-f", "--force", is_flag=True, default=False,
              help="Overwrite output file if it already exists.")
@click.option("--llm", "use_llm", is_flag=True, default=False,
              help="Translate via OpenAI GPT (needs OPENAI_API_KEY).")
@click.option("--lang", "target_lang", default="pt-BR", show_default=True,
              help="Target language for --llm translation (e.g. pt-BR, es, fr).")
@click.option("--model", default=DEFAULT_MODEL, show_default=True,
              help="OpenAI model when --llm is set.")
@click.option("--glossary", type=click.Path(exists=True, dir_okay=False), default=None,
              help="YAML glossary to refine LLM translation (preserve terms, domain notes).")
@click.option("--logo", type=click.Path(exists=True, dir_okay=False), default=None,
              help="Custom logo PNG for HTML header. Default: no logo.")
@click.option("--phases", "phases_path", type=click.Path(exists=True, dir_okay=False), default=None,
              help="YAML phase config to group cases.")
@click.option("--title", "page_title", default="Test Execution Plan", show_default=True,
              help="Page title shown in browser tab and HTML header.")
@click.option("--dump-json", type=click.Path(), default=None,
              help="Also write intermediate JSON for debugging.")
def main(input_xlsx, output, force, use_llm, target_lang, model, glossary,
         logo, phases_path, page_title, dump_json):
    """Generate single-file HTML test execution plan from Azure DevOps / TFS xlsx export."""
    out_path = Path(output)
    if out_path.exists() and not force:
        _log(f"ERROR: {out_path} already exists. Use -f / --force to overwrite.")
        sys.exit(1)

    _log(f"parsing {input_xlsx}")
    cases = parse_xlsx(input_xlsx)
    _log(f"found {len(cases)} test cases, {sum(len(c['steps']) for c in cases)} steps")

    backend = "llm" if use_llm else "none"
    glossary_obj = load_glossary_yaml(glossary) if glossary else None
    _log(f"translating ({backend}, target={target_lang})…")
    translate_cases(cases, backend=backend, target_lang=target_lang, model=model,
                    glossary=glossary_obj,
                    progress=lambda m: _log("  " + m))

    if phases_path:
        _log(f"applying phase config from {phases_path}")
        cfg = load_yaml_phases(phases_path)
        phase_data = apply_yaml_phases(cases, cfg)
    else:
        phase_data = assign_phases(cases)
    _log(f"phases: {[(p['id'], len(p['cases'])) for p in phase_data]}")

    if dump_json:
        Path(dump_json).write_text(
            json.dumps(phase_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        _log(f"wrote {dump_json}")

    out = render(phase_data, output, logo=logo, force=True, page_title=page_title)
    _log(f"wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
