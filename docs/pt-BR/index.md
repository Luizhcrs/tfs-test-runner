---
title: tfs-test-runner — visão geral
description: Kit HTML single-file de execução de testes a partir de exports xlsx do Azure DevOps / TFS.
---

# tfs-test-runner

> **Converte exports `xlsx` de test cases do Azure DevOps / TFS em um kit HTML auto-contido** com captura de screenshots, controle de status, anotações e exportação de evidências em PDF. Sem servidor, funciona offline, zero configuração. Tradução opcional via GPT pra qualquer idioma.

[![Tests](https://github.com/luizhcrs/tfs-test-runner/actions/workflows/test.yml/badge.svg)](https://github.com/luizhcrs/tfs-test-runner/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Luizhcrs/tfs-test-runner/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/Luizhcrs/tfs-test-runner)](https://github.com/Luizhcrs/tfs-test-runner/releases)

## O que faz

```mermaid
graph LR
    A[xlsx export<br/>do ADO/TFS] --> B[parse]
    B --> C[traduzir<br/>passthrough ou LLM]
    C --> D[agrupar por fases<br/>YAML ou default]
    D --> E[render]
    E --> F[plano.html<br/>single-file]
    F --> G[Tester:<br/>cola screenshots,<br/>marca PASS/FAIL,<br/>adiciona notas]
    G --> H[PDF por caso<br/>ou plano completo]
```

Cada estágio é função pura sobre dicts. JSON intermediário dumpável via `--dump-json`.

## Por quê

Se seu time usa **Azure DevOps Test Plans** ou **TFS** (ex. `*.tfs.<empresa>.net`), você já consegue exportar test cases pra xlsx. Mas executar manualmente e juntar evidências — screenshots por step, status, notas, empacotar como PDF entregável — é tedioso e propenso a erro.

`tfs-test-runner` pega esse xlsx e gera um arquivo HTML único pra abrir em qualquer navegador. Os testers colam screenshots step-a-step (Ctrl+V), marcam PASS / FAIL / N/A, escrevem notas, depois clicam um botão pra imprimir um PDF de evidência limpo.

State persiste em `localStorage` (texto/status) e `IndexedDB` (imagens). Backup/restore como JSON. Sem servidor, sem auth.

## Comece aqui

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Início rápido**

    ---

    Instale em 30 segundos, gere seu primeiro kit HTML do sample sintético.

    [:octicons-arrow-right-24: Início rápido](quickstart.md)

-   :material-cog:{ .lg .middle } **Uso**

    ---

    Walkthrough end-to-end pro tester rodando planos reais.

    [:octicons-arrow-right-24: Guia de uso](usage.md)

-   :material-tune:{ .lg .middle } **Configuração**

    ---

    Agrupamento YAML, glossários, logo customizado, modelos LLM.

    [:octicons-arrow-right-24: Configuração](configuration.md)

-   :material-source-branch:{ .lg .middle } **Arquitetura**

    ---

    Pipeline, formatos, decisões de design e trade-offs.

    [:octicons-arrow-right-24: Arquitetura](architecture.md)

</div>

## Screenshots

| Visão geral + filtros | Caso com evidências |
|---|---|
| ![Hero](../images/02-hero-progress.png) | ![Caso](../images/04-case-detail.png) |

??? note "Mais screenshots"

    | Filtro "Com falha" | PDF de evidências (default) |
    |---|---|
    | ![Filtro](../images/05-filter-failures.png) | ![PDF](../images/06-pdf-evidence.png) |

    | PDF com selos de status (toggle LIGADO) | Mobile / viewport estreito |
    |---|---|
    | ![PDF status](../images/06b-pdf-evidence-status.png) | ![Mobile](../images/07-narrow-view.png) |

    | Estado vazio | Plano completo (screenshot longa) |
    |---|---|
    | ![Vazio](../images/01-empty-overview.png) | [03-full-plan.png](../images/03-full-plan.png) |

## Não tem xlsx ainda?

Duas opções:

1.  **Sample sintético embutido** — `python examples/generate_sample.py` cria plano fake pra brincar.
2.  **Template em branco** — baixa [blank-template.xlsx](https://github.com/Luizhcrs/tfs-test-runner/raw/main/examples/blank-template.xlsx) e preenche manualmente. Mesmo schema do export Azure DevOps.

[:material-download: Baixar template em branco](https://github.com/Luizhcrs/tfs-test-runner/raw/main/examples/blank-template.xlsx){ .md-button .md-button--primary }
[:material-github: Ver no GitHub](https://github.com/Luizhcrs/tfs-test-runner){ .md-button }
