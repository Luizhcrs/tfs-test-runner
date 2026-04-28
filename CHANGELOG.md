# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.3.0] — 2026-04-28

### Added
- **Light theme** with a complete CSS-variable override set; alongside the
  existing **dark theme** and a new **auto** mode that follows the OS
  `prefers-color-scheme`. Theme is set via `:root[data-theme="light|dark|auto"]`
  on the document root.
- **Settings panel** (gear icon ⚙ in the toolbar) groups configurable options
  in one floating dialog:
  - Theme selector (Auto / Light / Dark) as radio buttons
  - "Show status in PDF" checkbox (replaces the old standalone toolbar toggle)
  - Keyboard-shortcut reference inline
  - Closes on backdrop click or `Esc`
- New screenshots `08-light-theme.png` and `09-settings-panel.png`.

### Changed
- Removed the standalone "Status no PDF" toolbar checkbox; the same control
  lives inside the new settings panel. Existing localStorage value
  (`*-status-pdf`) is reused, so user preferences carry over.
- README and docs site (EN + PT-BR) updated with the new screenshots and
  the consolidated "Settings panel" feature description.
- `Esc` keyboard shortcut now closes the settings panel as well as the
  lightbox.
- `screenshots.py` regenerated 8 → 10 screenshots; adds light theme and
  settings panel views.

## [1.2.0] — 2026-04-28

### Added
- **Documentation site** powered by MkDocs Material at
  [luizhcrs.github.io/tfs-test-runner](https://luizhcrs.github.io/tfs-test-runner/),
  with bilingual content (EN + PT-BR) via `mkdocs-static-i18n`. Pages: Home,
  Quickstart, Usage, Configuration, Architecture, Contributing, Changelog.
  Material theme with dark/light toggle, search, code-copy buttons.
- **Blank xlsx template** at `examples/blank-template.xlsx` for users
  without an Azure DevOps export. Includes header comments documenting each
  column's expected content. Regenerate via `python examples/generate_blank_template.py`.
- **GitHub Actions docs workflow** (`.github/workflows/docs.yml`) builds
  MkDocs and deploys to GitHub Pages on every push to `main` that touches
  `docs/` or `mkdocs.yml`.
- New logo SVG and favicon PNG at `docs/assets/`.

### Changed
- Reorganized `docs/` into `docs/en/` and `docs/pt-BR/` subfolders to match
  i18n plugin's "folder" structure. Old flat `docs/USAGE.md` and
  `docs/ARCHITECTURE.md` removed.
- README and README.pt-BR: added Docs badge, link to hosted docs site,
  call-out section for the blank template option.
- `.gitignore`: ignore `site/` (MkDocs build output).

## [1.1.0] — 2026-04-28

### Added
- **Status badges in PDF** (opt-in toggle). New "Status no PDF" toggle in the
  toolbar adds PASS / FAIL / N/A pills to each step in the exported PDF, plus
  a per-case summary line ("X/Y steps · A PASS · B FAIL · C N/A"). Default
  off — preserves the clean evidence-only layout. Preference persists in
  `localStorage`.
- New screenshot `06b-pdf-evidence-status.png` showing toggle ON state.

### Changed
- README + README.pt-BR: added screenshot section for the toggle feature with
  call-out about when to use it.
- `screenshots.py` regenerated 7 → 8 screenshots, adds `06b-pdf-evidence-status`.

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
