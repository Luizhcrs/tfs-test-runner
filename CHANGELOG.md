# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-04-28

Initial public release. Generic Azure DevOps / TFS test case xlsx → HTML
execution kit. Removed all vendor-specific glossary content from the prior
internal version; the tool is now domain-agnostic.

### Added
- `parse_xlsx` — generic Azure DevOps export parser (header-driven column
  detection, supports any worksheet schema with `ID`, `Work Item Type`,
  `Title`, `Step Action` at minimum).
- `translate_cases` — two backends:
  - `none` (default): pass-through, snapshots originals as `*_en` fields.
  - `llm`: OpenAI Chat Completions with JSON-mode, 80-string / 12 KB chunks,
    exponential-backoff retries (3 attempts), per-chunk fallback to original
    text on failure, optional YAML glossary (preserve terms + domain notes).
- `assign_phases` / `apply_yaml_phases` — group cases into phases via YAML
  (`case_ids` and/or keyword `match`). Default groups all cases into a single
  "All cases" phase.
- `render` — Jinja2-based single-file HTML generator. Embeds optional logo
  as base64 data URL. Escapes `</`, `<!--`, `U+2028`, `U+2029` in JSON
  payload to prevent script injection.
- HTML kit features: per-step status (PASS / FAIL / N/A), notes, paste /
  drop / pick screenshot capture (IndexedDB), per-image captions, search,
  filter chips, expand / collapse, backup / restore JSON (including images),
  per-case PDF export (evidence-only), full PDF export with cover sheet,
  keyboard shortcuts (`/`, `Ctrl+P`, `Esc`).
- CLI: `tfs-test-runner` console script via `pip install -e .`.
- Test suite: 29 pytest tests covering parser, translator, classifier,
  renderer.
- CI: GitHub Actions matrix (Ubuntu / macOS / Windows × Python 3.10 /
  3.11 / 3.12).
- Examples: synthetic `sample.xlsx`, `sample-phases.yaml`,
  `sample-glossary.yaml` plus generator script.

### Security
- Embedded JSON in `<script>` is escaped against `</script>` and HTML
  comment injection.

[1.0.0]: https://github.com/luizhcrs/tfs-test-runner/releases/tag/v1.0.0
