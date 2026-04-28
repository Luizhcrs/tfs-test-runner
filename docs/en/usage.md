# Usage guide

End-to-end walkthrough for a tester running an Azure DevOps test plan with `tfs-test-runner`.

## 1. Export from Azure DevOps

In **Azure Boards / Azure Test Plans**:

1. Open your **Test Suite** or **Test Plan**.
2. Click **Export → Excel**.
3. Save the resulting `.xlsx` somewhere on your machine.

The exported file will have at minimum these columns: `ID`, `Work Item Type`, `Title`, `Test Step`, `Step Action`, `Step Expected`, plus optional `Area Path`, `Assigned To`, `State`. `tfs-test-runner` detects them by header name, so column order doesn't matter.

## 2. Generate the HTML kit

```bash
tfs-test-runner my-export.xlsx -o plan.html
```

Open `plan.html` in Chrome, Edge, or Firefox.

### With phase grouping
Create a `phases.yaml` that lists which case IDs belong to which phase. See [examples/sample-phases.yaml](https://github.com/Luizhcrs/tfs-test-runner/blob/main/examples/sample-phases.yaml). Then:
```bash
tfs-test-runner my-export.xlsx --phases phases.yaml -o plan.html
```

### With LLM translation
```bash
export OPENAI_API_KEY=sk-...
tfs-test-runner my-export.xlsx --llm --lang pt-BR -o plan-pt.html
```
Add `--glossary glossary.yaml` to teach the model what terms to keep verbatim.

### With company logo
```bash
tfs-test-runner my-export.xlsx --logo company-logo.png -o plan.html
```
The logo appears at the top of each test case page in the PDF.

## 3. Run tests in the HTML kit

For each case:

1. **Expand** the case (click the header).
2. For each step:
   - **Read** Action and Expected.
   - **Execute** the step in the system under test.
   - **Take a screenshot** (Print Screen / Snipping Tool / OS shortcut).
   - **Click** the step's paste-zone (it turns green = "ready to paste").
   - **Press Ctrl+V** to attach the screenshot. Multiple screenshots per step are supported.
   - **Click the thumbnail** to open the lightbox; type a caption and click outside to save.
   - **Set status**: PASS / FAIL / N/A from the dropdown.
   - **Add a note** if needed in the textarea next to the dropdown.
3. **Move on**. State auto-saves to `localStorage` (text/state) and `IndexedDB` (images) on every change.

### Quick filters

The chip row in the header filters cases by status: **Pending / In progress / OK / Failure**. Useful when you have 100+ cases and want to focus on what's left.

### Search

Press `/` to focus the search box. Matches case ID and title (case-insensitive substring).

## 4. Generate evidence PDFs

### Per-case PDF (typical deliverable)
1. Open the case.
2. Click **PDF deste caso** in the per-case toolbar.
3. In the print dialog: **uncheck "Headers and footers"**, choose **Save as PDF**, click Save.

The result is the case's evidence: logo + title + screenshots in chronological order with their captions.  Steps without screenshots are omitted automatically.

### Full plan PDF
1. Click **PDF Geral (evidências)** in the top toolbar (or press `Ctrl+P`).
2. Wait for the cover page + every case to render.
3. **Uncheck "Headers and footers"**, save as PDF.

Includes a cover sheet with date and a summary table (cases / steps / OK / failure / pending per phase), then one page per case.

## 5. Backup / restore / share state

- **Export backup** (top toolbar): downloads a JSON file containing all state + image data URLs. Round-trip safe.
- **Import backup**: restores from the JSON file. Useful when:
  - Switching machines mid-execution.
  - Sharing partial work with a teammate.
  - Recovering after a browser cache clear.

> ⚠ The backup file can be **large** (tens of MB) because it includes every screenshot as base64. Don't email it; use a file share.

## 6. Common gotchas

| Symptom | Likely cause | Fix |
|---|---|---|
| "Cabeçalhos e rodapés" appear in the PDF | Browser injects them by default | Uncheck the option in the print dialog → *Mais configurações* |
| Pasted screenshot doesn't appear | Paste-zone wasn't focused | Click the zone first (it turns green) → then Ctrl+V |
| `OPENAI_API_KEY not set` | Env var missing | `export OPENAI_API_KEY=...` (or `setx` on Windows) |
| `ValueError: missing required columns` | xlsx export missing headers | Re-export from Azure DevOps with default columns |
| Translation hits rate-limit | Too many parallel runs | Wait, the chunk falls back to original; retry the command |

## 7. Tips for a smooth deliverable

- **Run a smoke pass first** with `--llm` if translation is needed; review a few translations before running the full suite.
- **Keep cases organized via YAML** (`--phases`) — far easier than scrolling through 50+ flat cases.
- **Use `--title`** to set a meaningful header (e.g. `"Sprint 42 — Acceptance"`); it appears in browser tab and PDF cover.
- **Periodically Export backup** for safety; localStorage / IndexedDB can be cleared by browser cleanup tools.
- **One HTML file per cycle**: don't try to reuse the same file across sprints. Re-generate from a fresh xlsx each time.
