# Quickstart

Get your first HTML execution kit in 30 seconds.

## Install

=== "From source"

    ```bash
    git clone https://github.com/luizhcrs/tfs-test-runner.git
    cd tfs-test-runner
    pip install -e .
    ```

=== "With LLM translation"

    ```bash
    pip install -e ".[llm]"
    export OPENAI_API_KEY=sk-...
    ```

=== "Dev / contributing"

    ```bash
    pip install -e ".[dev]"
    pytest -q
    ```

Python ≥ 3.10 required.

## Generate your first plan

### Option A — Synthetic sample (no real data)

```bash
python examples/generate_sample.py
tfs-test-runner examples/sample.xlsx -o sample-out.html
```

Open `sample-out.html` in your browser. You'll see a working plan with 3 cases / 13 steps.

### Option B — Real export from Azure DevOps / TFS

1.  Open your Test Plan / Test Suite in Azure DevOps or TFS.
2.  Click **Export → Excel**.
3.  Run the CLI:

    ```bash
    tfs-test-runner my-export.xlsx -o plan.html
    ```

### Option C — Blank template (no Azure DevOps)

If you don't have an Azure DevOps instance:

1.  Download [blank-template.xlsx](https://github.com/Luizhcrs/tfs-test-runner/raw/main/examples/blank-template.xlsx).
2.  Fill rows following the schema (see the comments in row 1).
3.  Run the CLI:

    ```bash
    tfs-test-runner blank-template.xlsx -o plan.html
    ```

## What you get

A single HTML file (~50–500 KB depending on plan size) that contains:

- Phase / case / step tree (expandable)
- Per-step PASS / FAIL / N/A status
- Notes textarea per step
- Paste-zone for screenshots (Ctrl+V or click "Attach file")
- Search (`/`) and filter chips
- Backup / restore as JSON
- Per-case + full-plan PDF export

State is saved automatically to `localStorage` (text) and `IndexedDB` (images). Closing the tab and reopening picks up where you left off.

## Common flags

```bash
# GPT translation to Brazilian Portuguese
tfs-test-runner cases.xlsx --llm --lang pt-BR -o plan.html

# Group cases into phases via YAML
tfs-test-runner cases.xlsx --phases examples/sample-phases.yaml -o plan.html

# Custom logo and title
tfs-test-runner cases.xlsx \
    --logo company-logo.png \
    --title "Sprint 42 — Acceptance Tests" \
    -o sprint42.html

# See all options
tfs-test-runner --help
```

## Next steps

- [Usage guide](usage.md) — full walkthrough for testers
- [Configuration](configuration.md) — YAML configs, glossaries, logos
- [Architecture](architecture.md) — how the pipeline works under the hood
