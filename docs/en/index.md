---
title: tfs-test-runner — overview
description: Single-file HTML test execution kit from Azure DevOps / TFS xlsx exports.
---

# tfs-test-runner

> **Convert Azure DevOps / TFS test case `xlsx` exports into a self-contained HTML test execution kit** with screenshot capture, status tracking, observation notes, and PDF evidence export. No server, works offline, zero config. Optional GPT translation to any language.

[![Tests](https://github.com/luizhcrs/tfs-test-runner/actions/workflows/test.yml/badge.svg)](https://github.com/luizhcrs/tfs-test-runner/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Luizhcrs/tfs-test-runner/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/Luizhcrs/tfs-test-runner)](https://github.com/Luizhcrs/tfs-test-runner/releases)

## What it does

```mermaid
graph LR
    A[xlsx export<br/>from ADO/TFS] --> B[parse]
    B --> C[translate<br/>passthrough or LLM]
    C --> D[group by phases<br/>YAML or default]
    D --> E[render]
    E --> F[plano.html<br/>single-file]
    F --> G[Tester:<br/>paste screenshots,<br/>mark PASS/FAIL,<br/>add notes]
    G --> H[PDF per case<br/>or full plan]
```

Each stage is a pure function over plain dicts. Intermediate JSON dumpable via `--dump-json`.

## Why

If your team uses **Azure DevOps Test Plans** or **TFS** (e.g. `*.tfs.<company>.net`), you can already export test cases to xlsx. But running them by hand and assembling evidence — screenshots per step, status, notes, packaged as a deliverable PDF — is tedious and error-prone.

`tfs-test-runner` takes that xlsx and produces a single HTML file you open in any browser. Testers paste screenshots step-by-step (Ctrl+V), mark PASS / FAIL / N/A, write notes, then click one button to print a clean evidence PDF.

State persists in `localStorage` (text/status) and `IndexedDB` (images). Backup/restore as JSON. Zero server, zero auth.

## Get started

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Quickstart**

    ---

    Install in 30 seconds, generate your first HTML kit from the synthetic sample.

    [:octicons-arrow-right-24: Quickstart](quickstart.md)

-   :material-cog:{ .lg .middle } **Usage**

    ---

    End-to-end walkthrough for testers running real plans.

    [:octicons-arrow-right-24: Usage guide](usage.md)

-   :material-tune:{ .lg .middle } **Configuration**

    ---

    YAML phase grouping, glossaries, custom logo, LLM models.

    [:octicons-arrow-right-24: Configuration](configuration.md)

-   :material-source-branch:{ .lg .middle } **Architecture**

    ---

    Pipeline, data shapes, design choices, and trade-offs.

    [:octicons-arrow-right-24: Architecture](architecture.md)

</div>

## Screenshots

| Overview with progress + filters | Single case w/ evidence + status |
|---|---|
| ![Hero](images/02-hero-progress.png) | ![Case](images/04-case-detail.png) |

??? note "More screenshots"

    | Filter "Failures" | PDF evidence (default) |
    |---|---|
    | ![Filter](images/05-filter-failures.png) | ![PDF](images/06-pdf-evidence.png) |

    | PDF with status pills (toggle ON) | Mobile / narrow viewport |
    |---|---|
    | ![PDF status](images/06b-pdf-evidence-status.png) | ![Narrow](images/07-narrow-view.png) |

    | Empty state | Full plan (long screenshot) |
    |---|---|
    | ![Empty](images/01-empty-overview.png) | [03-full-plan.png](images/03-full-plan.png) |

## Don't have an xlsx yet?

Two options:

1.  **Use the bundled synthetic sample** — `python examples/generate_sample.py` creates a fake plan to play with.
2.  **Use the blank template** — download [blank-template.xlsx](https://github.com/Luizhcrs/tfs-test-runner/raw/main/examples/blank-template.xlsx) and fill it manually. Same schema as Azure DevOps export.

[:material-download: Download blank template](https://github.com/Luizhcrs/tfs-test-runner/raw/main/examples/blank-template.xlsx){ .md-button .md-button--primary }
[:material-github: View on GitHub](https://github.com/Luizhcrs/tfs-test-runner){ .md-button }
