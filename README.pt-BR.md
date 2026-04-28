# tfs-test-runner

> Converte exports `xlsx` de test cases do **Azure DevOps / TFS** em um **kit HTML de execução** auto-contido, com captura de screenshots, controle de status, anotações e exportação de evidências em PDF. Sem servidor, funciona offline, zero configuração. Tradução opcional via GPT pra qualquer idioma.

[![Tests](https://github.com/luizhcrs/tfs-test-runner/actions/workflows/test.yml/badge.svg)](https://github.com/luizhcrs/tfs-test-runner/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Read in English](https://img.shields.io/badge/lang-en-blue)](README.md)

## Screenshots

| Visão geral com progresso + filtros | Caso aberto com evidências e status |
|---|---|
| ![Hero com progresso](docs/images/02-hero-progress.png) | ![Detalhe do caso](docs/images/04-case-detail.png) |

| Filtro "Com falha" | Layout de evidência (PDF) |
|---|---|
| ![Filtro falhas](docs/images/05-filter-failures.png) | ![PDF de evidências](docs/images/06-pdf-evidence.png) |

| PDF com selos de status (toggle LIGADO) |
|---|
| ![PDF com status](docs/images/06b-pdf-evidence-status.png) |

> ℹ Toggle **"Status no PDF"** no toolbar adiciona selos PASS / FAIL / N/A ao lado de cada step no PDF exportado. Útil pra entregáveis que exigem veredito explícito por step.

<details>
<summary><b>Mais screenshots</b> (plano cheio, mobile, estado inicial)</summary>

| Estado vazio (logo após gerar) | Viewport estreito / mobile |
|---|---|
| ![Estado vazio](docs/images/01-empty-overview.png) | ![Mobile](docs/images/07-narrow-view.png) |

Plano completo (screenshot longa): [03-full-plan.png](docs/images/03-full-plan.png)

</details>

## Por quê

Se seu time usa **Azure DevOps Test Plans** (ou TFS, ex. `*.tfs.<empresa>.net`), você já consegue exportar test cases e steps pra xlsx. Mas executar manualmente e juntar evidências — screenshots por step, status, observações, e empacotar em PDF entregável — é tedioso e propenso a erro.

O `tfs-test-runner` pega esse xlsx e gera um arquivo HTML único pra abrir em qualquer navegador. Os testers colam screenshots step-a-step (Ctrl+V), marcam PASS / FAIL / N/A, escrevem observações e no fim clicam um botão pra imprimir um PDF de evidência limpo (por caso ou plano completo). Estado salvo em `localStorage`; imagens em `IndexedDB`. Backup / restore como JSON.

## Início rápido

```bash
git clone https://github.com/luizhcrs/tfs-test-runner.git
cd tfs-test-runner
pip install -e .

# Gera xlsx sintético + HTML
python examples/generate_sample.py
tfs-test-runner examples/sample.xlsx -o sample-out.html

# Abre sample-out.html no navegador
```

Pronto. Sem API key, sem tradução, sem firulas.

## Casos de uso comuns

### Traduzir para Português via GPT
```bash
export OPENAI_API_KEY=sk-...
tfs-test-runner cases.xlsx --llm --lang pt-BR -o plano.html
```

### Traduzir para qualquer idioma com glossário de domínio
```bash
tfs-test-runner cases.xlsx \
    --llm --lang es \
    --glossary examples/sample-glossary.yaml \
    -o plano-es.html
```

### Agrupar casos em fases
```bash
tfs-test-runner cases.xlsx \
    --phases examples/sample-phases.yaml \
    --title "Sprint 42 — Testes de Aceite" \
    -o sprint42.html
```

### Adicionar logo customizado (aparece em cada caso no PDF)
```bash
tfs-test-runner cases.xlsx --logo logo-empresa.png -o plano.html
```

## O que o kit HTML oferece pro tester

- **Árvore fase / caso / step** com seções dobráveis
- **Busca** (`/` foca) e **chips de filtro** (Pendentes / Em andamento / OK / Com falha)
- Por step: status **PASS / FAIL / N/A**, **textarea de observação**, **zona de paste de screenshot** (Ctrl+V ou clicar "Anexar arquivo")
- **Legendas por imagem** — clica na thumb, edita inline, aparece no PDF
- **Ações por caso**: marcar todos PASS, limpar caso (state + imagens), **exportar este caso como PDF**
- **PDF do plano completo** com capa (data + tabela resumo por fase)
- **Backup / Restore JSON** — round-trip do estado completo incluindo data URLs das imagens
- **Atalhos**: `/` busca, `Ctrl+P` PDF geral, `Esc` fecha lightbox

## Como o PDF fica

PDF por caso emula um documento de evidência limpo:
- **Logo** (se `--logo` foi setado) no topo de cada página de caso
- **Título do caso** em inglês (texto original)
- **Sequência de blocos [legenda + screenshot]**, um por step que tem ao menos uma imagem
- **Steps sem screenshot somem** automaticamente
- **Quebra de página por caso** pra cases nunca cortarem feio

> 💡 No diálogo de impressão, **desmarque "Cabeçalhos e rodapés"** — senão o navegador injeta `file:///…` e data/hora em cada quebra de página.

## Referência CLI

```text
Uso: tfs-test-runner [OPTIONS] INPUT_XLSX

  Gera plano de execução HTML single-file a partir de export xlsx do Azure DevOps / TFS.

Opções:
  --version                Mostra versão e sai.
  -o, --output PATH        Caminho do HTML. Default: test-plan.html
  -f, --force              Sobrescreve output se já existir.
  --llm                    Traduz via OpenAI GPT (precisa de OPENAI_API_KEY).
  --lang TEXT              Idioma alvo do --llm. [default: pt-BR]
  --model TEXT             Modelo OpenAI quando --llm está ativo. [default: gpt-4o-mini]
  --glossary PATH          YAML pra refinar tradução LLM (preserve terms, notes de domínio).
  --logo PATH              PNG do logo no header HTML. Default: sem logo.
  --phases PATH            YAML pra agrupar casos em fases.
  --title TEXT             Título da página exibido na aba e no header.
                           [default: Test Execution Plan]
  --dump-json PATH         Também salva JSON intermediário pra debug.
  --help                   Exibe esta mensagem e sai.
```

## Schema xlsx esperado

O parser detecta colunas pelo nome do header (case-insensitive, suporta aliases comuns). Colunas obrigatórias: `ID`, `Work Item Type`, `Title`, `Step Action`. Opcionais: `Test Step`, `Step Expected`, `Area Path`, `Assigned To`, `State`.

As linhas alternam: uma linha com `Work Item Type = Test Case` abre um novo caso; linhas seguintes (tipicamente com `Work Item Type` vazio ou `Shared Steps`) pertencem àquele caso como steps até o próximo test case. Combina com o layout padrão **Azure DevOps Test Plans → Export to Excel**.

## YAML de fases

```yaml
phases:
  - id: "p1"
    title: "Phase 1 — Smoke"
    level: easy            # easy | med | hard (cosmético)
    desc: "Caminho crítico."
    case_ids: ["101", "104"]

  - id: "p2"
    title: "Phase 2 — Falhas"
    level: med
    desc: "Caminhos negativos."
    match: ["failure", "invalid", "error"]    # substring case-insensitive no título
```

Casos não casados caem na fase automática **"Outros"** ao final.

## YAML de glossário (apenas LLM)

```yaml
preserve:
  - "Sign In"
  - "Save"
  - "Cancel"
notes: |
  Domínio: QA web. Tom: técnico, imperativo ("Clicar", "Digitar", "Verificar").
```

`preserve` entra no system prompt como termos a manter verbatim. `notes` é texto livre acrescentado como contexto de domínio.

## API Python

```python
from tfs_test_runner import parse_xlsx, translate_cases, assign_phases, render

cases = parse_xlsx("cases.xlsx")
translate_cases(cases, backend="llm", target_lang="pt-BR")
phases = assign_phases(cases)
render(phases, "plano.html", page_title="Meu Plano de Testes", logo="logo.png")
```

## Documentação

- [docs/USAGE.pt-BR.md](docs/USAGE.pt-BR.md) — passo-a-passo end-to-end pro tester
- [docs/ARCHITECTURE.pt-BR.md](docs/ARCHITECTURE.pt-BR.md) — pipeline, formatos, decisões de design
- [CONTRIBUTING.md](CONTRIBUTING.md) — setup dev e convenções
- [CHANGELOG.md](CHANGELOG.md) — notas de release

## Arquitetura

```
tfs_test_runner/
├── parse.py        # xlsx → list[dict] (openpyxl, header-driven)
├── translate.py    # passthrough ou LLM (OpenAI Chat Completions, JSON mode)
├── classify.py     # default 1-fase / agrupamento via YAML
├── render.py       # Jinja2 → HTML single-file, base64 logo, JSON escapado
├── cli.py          # CLI baseado em Click
├── template/
│   └── plano.html.j2   # CSS + JS + UI com IndexedDB
└── assets/         # vazio por default; --logo é opcional
build.py            # shim de conveniência pra `python build.py …`
examples/           # xlsx sintético + configs YAML
tests/              # suite pytest (29 testes)
```

## Desenvolvimento

```bash
git clone https://github.com/luizhcrs/tfs-test-runner.git
cd tfs-test-runner
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest -q
```

CI roda a suíte em Ubuntu / macOS / Windows × Python 3.10 / 3.11 / 3.12 mais um smoke test do CLI contra o sample gerado.

## Roadmap (PRs bem-vindos)

- [ ] **Outros provedores LLM**: Anthropic Claude, Ollama / llama.cpp local.
- [ ] **Input CSV** além de xlsx.
- [ ] **Adapters de import**: TestRail, Xray.
- [ ] **Sync multi-tester**: merge opcional via WebRTC / arquivo pra execução paralela.
- [ ] **Toggle de modo de impressão**: completo vs evidence-only como checkbox UI.
- [ ] **Tracking de tempo por step** pra analytics de execução.

## Contribuindo

PRs bem-vindos. Roda `pytest` antes de pushar. Manter o estilo de código existente (sem formatter forçado).

## Licença

[MIT](LICENSE) — © 2026 luizhcrs.

## Agradecimentos

Construído pra resolver uma dor real: transformar execução manual de QA contra Azure DevOps test plans num workflow de baixo atrito e rico em evidência sem mais um SaaS. Se economizar algumas horas pro seu time, deixa uma estrela ⭐.
