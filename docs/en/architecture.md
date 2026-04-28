# Architecture

A short tour of how the pipeline is wired together. Total source: ~700 LOC + ~600 LOC of HTML/CSS/JS template.

## Pipeline overview

```
xlsx file
   │
   ▼
parse.parse_xlsx          → list[Case]   (English source)
   │
   ▼
translate.translate_cases → list[Case]   (target language; *_en snapshots kept)
   │
   ▼
classify.assign_phases    → list[Phase]  (or apply_yaml_phases for explicit grouping)
   │
   ▼
render.render             → single .html file (CSS + JS + JSON-embedded data + base64 logo)
```

Each stage is a pure function over plain dicts; intermediate JSON can be dumped via `--dump-json` for debugging.

## Data shape

### Case (after parse)
```python
{
    "id": "101",
    "title": "Login - Successful sign-in",
    "assigned": "alice@example.com",
    "state": "Design",
    "area": "WebApp\\Auth",
    "steps": [
        {
            "step": "1",
            "action": "Open the application URL",
            "expected": "Login page is displayed",
            "shared_id": "",
        },
        ...
    ],
}
```

### Case (after translate)
Same shape plus snapshots of originals:
```python
{
    "id": "101",
    "title": "Login - Sign-in com sucesso",        # translated
    "title_en": "Login - Successful sign-in",      # original
    ...
    "steps": [
        {
            "step": "1",
            "action": "Abrir a URL do aplicativo",
            "action_en": "Open the application URL",   # original
            "expected": "A página de login é exibida",
            "expected_en": "Login page is displayed",
            "shared_id": "",
        },
    ],
}
```

The `*_en` fields are what the **PDF evidence layout** uses, since the customer-facing evidence is conventionally English.

### Phase
```python
{
    "id": "p1",
    "title": "Phase 1 — Smoke",
    "level": "easy",        # easy | med | hard (cosmetic badge color)
    "desc": "Critical path.",
    "cases": [Case, Case, ...],
}
```

## Module-by-module

### `parse.py`
- Uses `openpyxl` in `read_only=True, values_only=True` for memory efficiency.
- Header row is parsed once; columns mapped by case-insensitive alias lookup (`HEADER_ALIASES`). Missing required columns raise `ValueError` early so the user sees the failure before any translation cost.
- A row with `Work Item Type = Test Case` opens a new case; following rows append to its `steps` list until the next test case appears.
- Whitespace (including NBSP / zero-width) is normalized in `_clean()`.

### `translate.py`
Two backends:

**`backend="none"`** (default): pass-through. The function still snapshots `*_en` fields so the rest of the pipeline can rely on them.

**`backend="llm"`**:
1. Collects unique strings across all titles, actions, expecteds (deduplication is a big cost saver — most test plans have hundreds of repeated shared-step phrases).
2. Splits into chunks bounded by both **count** (≤ 80 strings) and **payload size** (≤ 12 KB UTF-8). Either limit triggers a chunk break.
3. Each chunk is sent via OpenAI Chat Completions with `response_format={"type": "json_object"}`. The system prompt is identical across chunks so OpenAI's automatic prompt caching kicks in after the first call.
4. Per-chunk **exponential backoff** (3 attempts, base delay 2s). On terminal failure or malformed JSON, the chunk falls back to the **original strings** (no translation, but the run continues).
5. Final translations are mapped back onto the cases (titles, actions, expecteds) using a deterministic dict lookup.

The optional `glossary` argument feeds the system prompt with `preserve` terms (must not translate) and `notes` (free-text domain context).

### `classify.py`
- **Default** (`assign_phases`): single phase containing all cases. Useful when no organization is needed or as a baseline.
- **YAML override** (`apply_yaml_phases`): each phase definition matches by:
  - `case_ids`: explicit list of case IDs
  - `match`: list of case-insensitive substrings tested against `title_en` (or `title` if `_en` absent)
- A case is assigned at most once (first matching phase wins, in YAML order).
- Unmatched cases land in an automatically appended **"Others"** phase.

### `render.py`
- Single Jinja2 template (`tfs_test_runner/template/plano.html.j2`).
- Phase data is JSON-serialized and embedded inside a `<script>` tag. **`_safe_json` escapes** `</`, `<!--`, U+2028, U+2029 to prevent script-tag breakout and JS parser errors.
- Logo (if `--logo` set) is read once, base64-encoded, embedded as a CSS variable `--logo-url`. If absent, the variable is omitted entirely so the CSS rules using it become inert.
- Output is one **fully self-contained HTML file** — no external links, no CDNs, works offline indefinitely.

### `template/plano.html.j2` (the runtime UI)
- **Vanilla JS** — no React, no build step, no npm.
- **State**: `localStorage` for text (status, notes, captions), **IndexedDB** for image data URLs (large blobs that would blow up `localStorage` quota).
- **Image capture**: paste-zone listens for `paste` / `drop` / file-picker click. Each image is keyed by `step:<caseId>:<stepIdx>:<timestamp>_<rand>` or `case:<caseId>:<timestamp>_<rand>`.
- **Print modes**:
  - `body.print-evidence` — hides everything except images + English step labels. Used by both per-case and full-plan PDF exports.
  - `body[data-print-case]` — additionally hides every case except the one with `.print-target`.
- **PDF cover page** is rendered into `#print-cover` only for full-plan exports.

## Why these choices

- **No SaaS, no backend, no auth.** A tester opens the HTML in any browser. Evidence stays on their machine until they export PDF / JSON. This works inside enterprise VPNs without any infra ask.
- **JSON backup format is round-trip safe** — including base64 image data URLs. Lets a tester pause work, share state with a peer, or move to another machine.
- **Single HTML file** dodges the operational cost of hosting anything. It's an artifact you can email, attach to a Jira ticket, or zip into a deliverable.
- **GPT translation is opt-in.** Free pass-through covers the case where the team works in English. Translation is a paid convenience, not a hard dependency.

## Performance

- `parse.py`: streams rows; tested on a 781-row export, parses in ~50ms.
- `translate.py` (LLM): ~430 unique strings → ~6 chunks → 6 sequential API calls. With `gpt-4o-mini` typical run is 30–60 seconds, ~$0.05.
- `render.py`: ~410 KB output for 36 cases / 744 steps. Embedded JSON dominates.
- Browser runtime: tested with 700+ steps and ~50 screenshots; 60fps scrolling. IndexedDB is the only place where total image volume becomes the bottleneck (most browsers cap at ~50 MB / origin without a quota request).
