# Configuration

All configuration is opt-in via flags or YAML files. Defaults work without any config.

## Phase grouping (`--phases phases.yaml`)

Group test cases into phases for organized execution. Without this flag, all cases land in a single "All cases" phase.

```yaml title="phases.yaml"
phases:
  - id: "p1"
    title: "Phase 1 — Smoke"
    level: easy            # easy | med | hard (drives badge color, cosmetic)
    desc: "Critical positive scenarios run on every build."
    case_ids: ["101", "104", "108"]   # explicit IDs

  - id: "p2"
    title: "Phase 2 — Failure scenarios"
    level: med
    desc: "Negative paths and error handling."
    match: ["failure", "invalid", "error"]   # case-insensitive substring on title

  - id: "p3"
    title: "Phase 3 — Edge cases"
    level: hard
    desc: "Concurrency, boundary, and rare conditions."
    case_ids: ["201", "202"]
    match: ["edge", "boundary", "concurrent"]   # combine both
```

### Matching rules

- A case is assigned to **at most one phase** (first matching phase in YAML order wins).
- `case_ids` and `match` can be combined; case matches if either condition is true.
- Cases not matched by any phase fall into an automatically appended **"Others"** phase.

### Levels

`easy`, `med`, `hard` only affect the badge color in the HTML (green / yellow / red). They have no functional impact.

## LLM glossary (`--glossary glossary.yaml`, requires `--llm`)

Refine the LLM translation behavior with domain-specific guidance.

```yaml title="glossary.yaml"
preserve:
  - "Sign In"
  - "Save"
  - "Cancel"
  - "Profile"
  - "Email"
  - "Password"
  - "Full Name"

notes: |
  Domain: web application QA testing. Users execute test cases manually.
  Tone: technical, imperative ("Click", "Type", "Verify").
  Keep button labels in the original language since the UI is English.
```

`preserve` terms are added verbatim to the LLM system prompt — the model is instructed never to translate them. Useful for product names, UI labels, technical jargon.

`notes` is free-text appended as domain context. Helps the model pick the right tone and terminology.

## Logo (`--logo company-logo.png`)

A custom logo appears at the top of each test case page in the PDF export.

- Supported: PNG, JPG, SVG, GIF
- Maximum recommended size: 200×60 px (rendered at 42px height in PDF)
- Embedded as base64 data URL — no external link, works offline
- Default: no logo (toolkit ships without branding)

```bash
tfs-test-runner cases.xlsx --logo my-company.png -o plan.html
```

## Title (`--title "..."`)

Sets the browser tab title and the H1 in the page header. Default: `"Test Execution Plan"`.

```bash
tfs-test-runner cases.xlsx --title "Sprint 42 — Acceptance Tests" -o plan.html
```

## LLM model (`--model gpt-4o-mini`)

When `--llm` is set, you can choose any OpenAI-compatible chat model.

| Model | Cost (typical run, 36 cases) | Speed | Quality |
|---|---|---|---|
| `gpt-4o-mini` (default) | ~$0.05 | ~30s | Good |
| `gpt-4o` | ~$0.50 | ~45s | Best |
| `gpt-4-turbo` | ~$0.30 | ~40s | Excellent |

```bash
export OPENAI_API_KEY=sk-...
tfs-test-runner cases.xlsx --llm --lang pt-BR --model gpt-4o-mini -o plan.html
```

The LLM backend uses Chat Completions JSON mode, batches translations into chunks of 80 strings or 12 KB (whichever comes first), and retries each chunk up to 3 times with exponential backoff. Failed chunks fall back to original strings.

## Output file (`-o output.html`, `--output output.html`)

Default: `test-plan.html` in the current directory.

```bash
tfs-test-runner cases.xlsx -o ~/Desktop/sprint42-plan.html
```

## Force overwrite (`-f`, `--force`)

Without this flag, the CLI refuses to overwrite an existing output file.

```bash
tfs-test-runner cases.xlsx -o plan.html --force
```

## Debug JSON dump (`--dump-json intermediate.json`)

Writes the translated, classified phase data as JSON. Useful for debugging LLM output or building custom downstream tools.

```bash
tfs-test-runner cases.xlsx --dump-json debug.json -o plan.html
```

## Full CLI reference

```bash
tfs-test-runner --help
```

```text
Usage: tfs-test-runner [OPTIONS] INPUT_XLSX

  Generate single-file HTML test execution plan from Azure DevOps / TFS xlsx export.

Options:
  --version                Show the version and exit.
  -o, --output PATH        Output HTML path. Default: test-plan.html
  -f, --force              Overwrite output file if it already exists.
  --llm                    Translate via OpenAI GPT (needs OPENAI_API_KEY).
  --lang TEXT              Target language for --llm translation. [default: pt-BR]
  --model TEXT             OpenAI model when --llm is set. [default: gpt-4o-mini]
  --glossary PATH          YAML glossary to refine LLM translation.
  --logo PATH              Custom logo for HTML/PDF header. Default: no logo.
  --phases PATH            YAML phase config to group cases.
  --title TEXT             Page title shown in browser tab and HTML header.
                           [default: Test Execution Plan]
  --dump-json PATH         Also write intermediate JSON for debugging.
  --help                   Show this message and exit.
```
