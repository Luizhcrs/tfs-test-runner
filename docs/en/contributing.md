# Contributing

Thanks for considering a contribution. The project is small and intentionally simple — keep changes focused and well-tested.

## Development setup

```bash
git clone https://github.com/luizhcrs/tfs-test-runner.git
cd tfs-test-runner
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest -q
```

## Project conventions

- **Python ≥ 3.10**, type hints encouraged where they add clarity (`from __future__ import annotations`).
- **No formatter enforced** — match surrounding style (4-space indent, double quotes, trailing commas in multiline literals).
- **Tests first** for non-trivial bugs (open an issue, then a failing test, then fix).
- **No silent fallbacks** in CLI: every notable decision goes through `_log()` so users see what happened.
- **Commits**: short imperative subject, optional body explaining *why*. Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`) are appreciated but not enforced.

## What to test

Each module has a corresponding `tests/test_<module>.py`:

- `parse.py` — header detection, optional column tolerance, blank-row handling.
- `translate.py` — chunking, system prompt construction, passthrough behavior. (LLM call itself is not network-tested.)
- `classify.py` — default single phase, YAML id/match priority, leftover handling.
- `render.py` — JSON escaping (script injection), template wiring, force-overwrite guard.

For new features, add tests next to the matching module's tests. CI runs the suite on Linux / macOS / Windows × Python 3.10 / 3.11 / 3.12.

## Submitting changes

1. Fork → branch (`feat/short-name` or `fix/short-name`).
2. Run `pytest` locally; make sure CI is green after pushing.
3. Open a PR describing what changed and *why*. Link any related issue.
4. For UI / template changes, attach a before / after screenshot or a short clip.

## Out-of-scope (won't merge)

- SaaS lock-in (auth, telemetry, hosted backend).
- Mandatory cloud APIs — `--llm` stays optional.
- Vendor-specific glossaries hard-coded into the package — keep those in
  `examples/*.yaml` only.
- Rich client-side dependencies (React / Vue / a build step). The HTML kit is
  intentionally vanilla so it works offline forever.

## Reporting issues

When opening an issue please include:
- OS + Python version
- A minimal xlsx sample (or the smallest synthetic case that triggers the bug — see `examples/generate_sample.py` for the format)
- Exact CLI invocation
- Full output (stderr) and any traceback

## Releasing (maintainers)

1. Bump `__version__` in `tfs_test_runner/__init__.py` and `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` with the new entry.
3. Tag `vX.Y.Z` and push (`git tag -a vX.Y.Z -m "vX.Y.Z" && git push --tags`).
4. (Optional) Build and publish to PyPI:
   ```bash
   pip install build twine
   python -m build
   twine upload dist/*
   ```
