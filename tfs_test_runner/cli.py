"""CLI entry point — Click multi-command group.

Subcommands:
    plan         Generate single-file HTML execution kit from xlsx (main action).
    validate     Validate xlsx schema and print summary.
    init         Initialize a new test plan directory with templates.
    screenshots  Regenerate docs screenshots via Playwright (maintainers).

Run `tfs-test-runner --help` for the command list and `tfs-test-runner <cmd> --help`
for command-specific options.
"""
from __future__ import annotations
import sys, json, shutil, subprocess
from pathlib import Path

import click

from . import __version__
from .parse import parse_xlsx
from .translate import translate_cases, load_glossary_yaml, DEFAULT_MODEL
from .classify import assign_phases, load_yaml_phases, apply_yaml_phases
from .render import render


CONTEXT = {"help_option_names": ["-h", "--help"]}


def _log(msg: str):
    print(f"[tfs-test-runner] {msg}", file=sys.stderr)


@click.group(
    context_settings=CONTEXT,
    invoke_without_command=False,
    help="""tfs-test-runner — generate HTML test execution kits from Azure DevOps / TFS xlsx exports.

\b
Common workflows:

  tfs-test-runner plan cases.xlsx -o plan.html
  tfs-test-runner plan cases.xlsx --llm --lang pt-BR
  tfs-test-runner validate cases.xlsx
  tfs-test-runner init my-plan

Each subcommand has its own --help. Documentation: https://luizhcrs.github.io/tfs-test-runner/
""",
)
@click.version_option(version=__version__, prog_name="tfs-test-runner")
def cli():
    pass


# ---------- plan ----------

@cli.command(context_settings=CONTEXT)
@click.argument("input_xlsx", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", type=click.Path(), default="test-plan.html",
              help="Output HTML path.")
@click.option("-f", "--force", is_flag=True, default=False,
              help="Overwrite output file if it already exists.")
@click.option("--llm", "use_llm", is_flag=True, default=False,
              help="Translate via OpenAI GPT (needs OPENAI_API_KEY).")
@click.option("--argos", "use_argos", is_flag=True, default=False,
              help="Translate via argos-translate (offline, free; auto-installs language pair).")
@click.option("--lang", "target_lang", default="pt-BR", show_default=True,
              help="Target language for --llm/--argos translation (e.g. pt-BR, es, fr).")
@click.option("--model", default=DEFAULT_MODEL, show_default=True,
              help="OpenAI model when --llm is set.")
@click.option("--glossary", type=click.Path(exists=True, dir_okay=False), default=None,
              help="YAML glossary refining --llm translation (preserve terms, domain notes).")
@click.option("--logo", type=click.Path(exists=True, dir_okay=False), default=None,
              help="Custom logo for HTML / PDF header. Default: no logo.")
@click.option("--phases", "phases_path", type=click.Path(exists=True, dir_okay=False), default=None,
              help="YAML phase config to group cases.")
@click.option("--title", "page_title", default="Test Execution Plan", show_default=True,
              help="Page title shown in browser tab and HTML header.")
@click.option("--dump-json", type=click.Path(), default=None,
              help="Also write intermediate translated JSON for debugging.")
def plan(input_xlsx, output, force, use_llm, use_argos, target_lang, model,
         glossary, logo, phases_path, page_title, dump_json):
    """Generate single-file HTML execution kit from xlsx."""
    if use_llm and use_argos:
        _log("ERROR: --llm and --argos are mutually exclusive.")
        sys.exit(2)

    out_path = Path(output)
    if out_path.exists() and not force:
        _log(f"ERROR: {out_path} already exists. Use -f / --force to overwrite.")
        sys.exit(1)

    _log(f"parsing {input_xlsx}")
    cases = parse_xlsx(input_xlsx)
    _log(f"found {len(cases)} test cases, {sum(len(c['steps']) for c in cases)} steps")

    backend = "llm" if use_llm else ("argos" if use_argos else "none")
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


# ---------- validate ----------

@cli.command(context_settings=CONTEXT)
@click.argument("input_xlsx", type=click.Path(exists=True, dir_okay=False))
@click.option("--strict", is_flag=True, default=False,
              help="Exit non-zero on warnings (e.g. cases without steps).")
def validate(input_xlsx, strict):
    """Validate xlsx schema and print a summary report."""
    _log(f"parsing {input_xlsx}")
    try:
        cases = parse_xlsx(input_xlsx)
    except Exception as e:
        _log(f"ERROR: parse failed — {type(e).__name__}: {e}")
        sys.exit(1)

    total_steps = sum(len(c["steps"]) for c in cases)
    issues = []
    seen_ids: dict[str, int] = {}
    for c in cases:
        cid = str(c.get("id", ""))
        if not cid:
            issues.append(f"case '{c.get('title','?')}' has empty ID")
        else:
            seen_ids[cid] = seen_ids.get(cid, 0) + 1
        if not c.get("title"):
            issues.append(f"case {cid} has empty title")
        if not c["steps"]:
            issues.append(f"case {cid} has no steps")

    duplicates = [cid for cid, n in seen_ids.items() if n > 1]
    for cid in duplicates:
        issues.append(f"duplicate case ID '{cid}' appears {seen_ids[cid]}x")

    print(f"\n  Test cases : {len(cases)}")
    print(f"  Total steps: {total_steps}")
    if cases:
        avg = total_steps / len(cases)
        print(f"  Avg steps  : {avg:.1f} per case")
    states = {}
    areas = {}
    for c in cases:
        states[c.get("state", "—")] = states.get(c.get("state", "—"), 0) + 1
        areas[c.get("area", "—")] = areas.get(c.get("area", "—"), 0) + 1
    if any(s != "" for s in states):
        print(f"  States     : {dict(states)}")
    if any(a != "" for a in areas):
        print(f"  Areas      : {dict(areas)}")

    if issues:
        print(f"\n  Issues ({len(issues)}):")
        for i in issues[:20]:
            print(f"    • {i}")
        if len(issues) > 20:
            print(f"    … and {len(issues) - 20} more")
    else:
        print("\n  No issues found. [OK]")

    print()
    if strict and issues:
        sys.exit(1)


# ---------- init ----------

@cli.command(context_settings=CONTEXT)
@click.argument("path", type=click.Path(file_okay=False), default="qa-plan")
@click.option("--with-sample", is_flag=True, default=False,
              help="Also generate a filled-in sample.xlsx alongside the blank template.")
@click.option("-f", "--force", is_flag=True, default=False,
              help="Overwrite existing files in PATH.")
def init(path, with_sample, force):
    """Initialize a directory with blank xlsx + YAML templates."""
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    pkg_root = Path(__file__).parent.parent

    sources = [
        ("examples/blank-template.xlsx", "cases.xlsx"),
        ("examples/sample-phases.yaml", "phases.yaml"),
        ("examples/sample-glossary.yaml", "glossary.yaml"),
    ]
    if with_sample:
        sources.append(("examples/sample.xlsx", "sample.xlsx"))

    written = 0
    for src_rel, dst_name in sources:
        src = pkg_root / src_rel
        dst = target / dst_name
        if not src.exists():
            _log(f"WARN: source {src} not found in package; skipping")
            continue
        if dst.exists() and not force:
            _log(f"skip {dst} (already exists, use -f to overwrite)")
            continue
        shutil.copy(src, dst)
        _log(f"wrote {dst}")
        written += 1

    readme = target / "README.md"
    if not readme.exists() or force:
        readme.write_text(_INIT_README, encoding="utf-8")
        _log(f"wrote {readme}")
        written += 1

    print(f"\n  Initialized {target} ({written} file{'s' if written != 1 else ''} written)")
    print(f"\n  Next steps:")
    print(f"    1. Edit {target}/cases.xlsx with your test cases")
    print(f"    2. (Optional) Tweak {target}/phases.yaml")
    print(f"    3. Run: tfs-test-runner plan {target}/cases.xlsx -o plan.html\n")


_INIT_README = """# QA test plan

Generated by `tfs-test-runner init`.

## Files

- `cases.xlsx` — fill with your test cases. Schema: `ID`, `Work Item Type`,
  `Title`, `Test Step`, `Step Action`, `Step Expected`, `Area Path`,
  `Assigned To`, `State`. Hover the header cells for column comments.
- `phases.yaml` — group cases into phases (optional).
- `glossary.yaml` — refine LLM translation (optional, only used with `--llm`).

## Generate the HTML kit

```bash
tfs-test-runner plan cases.xlsx -o plan.html
# with phases:
tfs-test-runner plan cases.xlsx --phases phases.yaml -o plan.html
# with GPT translation (needs OPENAI_API_KEY):
tfs-test-runner plan cases.xlsx --llm --lang pt-BR -o plan.html
```

Open `plan.html` in any browser to start executing tests.

## Validate the xlsx

```bash
tfs-test-runner validate cases.xlsx
```

Documentation: https://luizhcrs.github.io/tfs-test-runner/
"""


# ---------- screenshots ----------

@cli.command(context_settings=CONTEXT)
def screenshots():
    """Regenerate docs/images/*.png via Playwright (maintainers only)."""
    pkg_root = Path(__file__).parent.parent
    script = pkg_root / "docs" / "screenshots.py"
    if not script.exists():
        _log(f"ERROR: {script} not found. This command is only available in a checkout, not after pip install.")
        sys.exit(1)
    _log("running Playwright screenshot script…")
    rc = subprocess.call([sys.executable, str(script)])
    sys.exit(rc)


# ---------- backwards-compat shim ----------
# Allow `python -m tfs_test_runner.cli` to keep working.
def main():
    cli()


if __name__ == "__main__":
    cli()
