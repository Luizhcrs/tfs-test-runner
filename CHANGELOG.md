# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.1.0] — 2026-04-29

### Added
- **Mobile / narrow viewport polish.** New `@media (max-width: 640px)` block
  in the HTML kit reflows the layout for phone screens: actions wrap to
  two-column grid, search and filter chips stretch full-width, paste-zone
  becomes vertical with a full-width "Attach file" button, thumbs grid
  switches to 50/50 columns, settings panel goes full-screen.
- **CONTRIBUTING.pt-BR.md** — Portuguese translation of the contributing
  guide for parity with README EN/PT-BR.
- **`.gitattributes`** — normalizes line endings (LF in repo, native
  checkout), marks binaries (PNG / JPG / SVG / xlsx / docx / pdf) as
  binary so Git skips diffs and merges, and tags `docs/`+`examples/` as
  documentation for GitHub linguist stats.

### Changed
- **Image footprint reduced 2.8 MB → 1.2 MB** (-58%) via PIL palette
  quantization (256 colors, Floyd-Steinberg dither). Visually identical
  for screenshots; no quality loss noticeable.
- **Image deduplication**: removed `docs/en/images/` and
  `docs/pt-BR/images/` (~9 MB redundant copies). Only `docs/images/`
  remains as canonical source. MkDocs i18n indexes use `../images/`
  paths.

### Deferred to v3.0
- Full UI i18n (EN strings table + `--ui-lang` flag). Currently the HTML
  kit's UI strings remain hardcoded in pt-BR.

## [2.0.0] — 2026-04-29

### Breaking
- **CLI restructured into a Click multi-command group.** The previous
  single-command form (`tfs-test-runner cases.xlsx -o plan.html`) is no
  longer valid — use `tfs-test-runner plan cases.xlsx -o plan.html`.
  All existing flags are preserved on the `plan` subcommand.

### Added
- **`tfs-test-runner` is now a multi-command CLI** with subcommands:
  - `plan` — generate the HTML kit (formerly the default behavior).
  - `validate` — parse xlsx, print summary report (case/step counts,
    breakdown by area/state), flag missing IDs/titles/duplicates.
    `--strict` exits non-zero on warnings.
  - `init [PATH]` — scaffold a new test plan directory with
    `cases.xlsx` (blank template), `phases.yaml`, `glossary.yaml`,
    and a starter `README.md`. `--with-sample` also copies the
    filled sample.xlsx for reference.
  - `screenshots` — regenerate `docs/images/*.png` via Playwright
    (maintainer-only; only available in source checkouts).
- **Argos-translate backend** for offline, free translation
  (`tfs-test-runner plan cases.xlsx --argos --lang pt-BR`). Auto-installs
  the requested language pair on first use (~150 MB). Listed as optional
  extra: `pip install 'tfs-test-runner[argos]'`.
- **`-h` short option** for `--help` everywhere.
- **GitHub Actions release workflow** (`.github/workflows/release.yml`)
  builds sdist + wheel on `v*` tag push and publishes to PyPI via
  Trusted Publishing (OIDC, no API token in repo).
- 10 new CLI tests (Click `CliRunner`-based) covering top-level help,
  `plan`/`validate`/`init` subcommand help, version, validate happy path,
  plan happy path, force guard, mutually-exclusive `--llm`/`--argos`,
  init-creates-files. Total tests: 34 → 44 passing.

### Changed
- `validate` and `init` commands replace the implicit "did the CLI
  succeed" diagnostic. Recommended workflow:
  `validate` first, then `plan`.
- README and docs site updated for the new subcommand structure.

### Migration from 1.x
Any script using the old form needs the `plan` subcommand:

```diff
- tfs-test-runner cases.xlsx -o plan.html --llm --lang pt-BR
+ tfs-test-runner plan cases.xlsx -o plan.html --llm --lang pt-BR
```

All flags (`-o`, `-f`, `--llm`, `--lang`, `--model`, `--glossary`,
`--logo`, `--phases`, `--title`, `--dump-json`) keep their previous
names and semantics.

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
