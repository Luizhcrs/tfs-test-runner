# tfs-test-runner

> Converte exports `xlsx` de test cases do **Azure DevOps / TFS** em um **kit HTML auto-contido** com captura de screenshots, status, anotações e PDF de evidência. Sem servidor, funciona offline. Tradução GPT opcional.

[![Tests](https://github.com/luizhcrs/tfs-test-runner/actions/workflows/test.yml/badge.svg)](https://github.com/luizhcrs/tfs-test-runner/actions/workflows/test.yml)
[![Docs](https://github.com/Luizhcrs/tfs-test-runner/actions/workflows/docs.yml/badge.svg)](https://luizhcrs.github.io/tfs-test-runner/pt-BR/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![English](https://img.shields.io/badge/lang-en-blue)](README.md)

📖 **Documentação completa**: [luizhcrs.github.io/tfs-test-runner/pt-BR](https://luizhcrs.github.io/tfs-test-runner/pt-BR/) ([EN](https://luizhcrs.github.io/tfs-test-runner/))

| Tema escuro (default) | Tema claro |
|---|---|
| ![Hero dark](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/02-hero-progress.png) | ![Tema claro](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/08-light-theme.png) |

| Painel de configurações (tema + PDF) | Caso detalhado com evidências |
|---|---|
| ![Configurações](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/09-settings-panel.png) | ![Caso](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/04-case-detail.png) |

<details>
<summary><b>Mais screenshots</b> — filtro com falha, PDF, PDF com status, plano cheio, mobile, vazio</summary>

<br>

| Filtro "Com falha" | PDF de evidências (default) |
|---|---|
| ![Filtro](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/05-filter-failures.png) | ![PDF](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/06-pdf-evidence.png) |

| PDF com selos de status (toggle LIGADO) | Mobile / viewport estreito |
|---|---|
| ![PDF status](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/06b-pdf-evidence-status.png) | ![Mobile](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/07-narrow-view.png) |

| Estado vazio | Plano completo (screenshot longa) |
|---|---|
| ![Vazio](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/01-empty-overview.png) | [03-full-plan.png](https://raw.githubusercontent.com/Luizhcrs/tfs-test-runner/main/docs/images/03-full-plan.png) |

</details>

## Início rápido

```bash
pip install tfs-test-runner

# Scaffold pasta com templates
tfs-test-runner init meu-plano-qa
cd meu-plano-qa
# … preenche cases.xlsx …

# Valida schema
tfs-test-runner validate cases.xlsx

# Gera kit HTML
tfs-test-runner plan cases.xlsx -o plano.html
```

Abre `plano.html` no navegador. O tester cola screenshots (Ctrl+V) a cada step, marca PASS/FAIL/N/A, escreve observações, clica **PDF** pra entregável.

### Sem Azure DevOps? Use `init`

`tfs-test-runner init` cria pasta com xlsx em branco (com comentários nas colunas) + `phases.yaml` + `glossary.yaml` exemplo. Preenche manualmente — mesmo schema do **Azure DevOps Test Plans → Export to Excel**.

### Subcommands

```bash
tfs-test-runner --help                    # lista de comandos
tfs-test-runner plan cases.xlsx           # gera HTML
tfs-test-runner validate cases.xlsx       # checa schema + stats
tfs-test-runner init meu-plano            # scaffold novo plano
tfs-test-runner screenshots               # regenera prints (maintainers)
```

## Flags comuns

```bash
# Tradução GPT (paga, melhor qualidade)
export OPENAI_API_KEY=sk-...
tfs-test-runner plan cases.xlsx --llm --lang pt-BR -o plano.html

# Tradução argos (offline, grátis; auto-instala par de idiomas)
pip install 'tfs-test-runner[argos]'
tfs-test-runner plan cases.xlsx --argos --lang pt-BR -o plano.html

# Fases + título + logo
tfs-test-runner plan cases.xlsx \
    --phases phases.yaml \
    --title "Sprint 42 — Aceite" \
    --logo empresa.png -o plano.html

# Valida antes de gerar
tfs-test-runner validate cases.xlsx --strict
```

## Funcionalidades

- Árvore fase / caso / step, busca (`/`), chips de filtro, expandir/recolher
- Por step: **PASS / FAIL / N/A**, observação, paste/drop/pick de screenshot
- Legenda por imagem, lightbox zoom
- **PDF por caso** (só evidências) e **PDF do plano completo** com capa
- **Painel de configurações** (ícone engrenagem): tema claro/escuro/auto + toggle status no PDF
- Backup/restore JSON (estado + imagens)
- Atalhos: `/` busca, `Ctrl+P` PDF, `Esc` fecha lightbox/painel

> 💡 No diálogo de impressão, **desmarque "Cabeçalhos e rodapés"** pra evitar `file:///…` e data/hora em cada página.

## Documentação

- [docs/USAGE.pt-BR.md](docs/USAGE.pt-BR.md) — passo-a-passo pro tester
- [docs/ARCHITECTURE.pt-BR.md](docs/ARCHITECTURE.pt-BR.md) — pipeline e decisões
- [CONTRIBUTING.md](CONTRIBUTING.md) — setup dev
- [CHANGELOG.md](CHANGELOG.md) — notas de release

### Configs YAML (exemplos em [`examples/`](examples/))

```yaml
# phases.yaml — agrupar casos
phases:
  - id: p1
    title: "Phase 1 — Smoke"
    level: easy
    case_ids: ["101", "104"]
  - id: p2
    title: "Phase 2 — Falhas"
    match: ["failure", "invalid", "error"]
```

```yaml
# glossary.yaml — refinar tradução LLM (opcional)
preserve: ["Sign In", "Save", "Cancel"]
notes: "Domínio: QA web. Tom: técnico, imperativo."
```

## API Python

```python
from tfs_test_runner import parse_xlsx, translate_cases, assign_phases, render

cases = parse_xlsx("cases.xlsx")
translate_cases(cases, backend="llm", target_lang="pt-BR")
render(assign_phases(cases), "plano.html", page_title="Meu Plano")
```

## Desenvolvimento

```bash
pip install -e .[dev]
pytest -q
```

CI matrix: Ubuntu / macOS / Windows × Python 3.10 / 3.11 / 3.12.

## Licença

[MIT](LICENSE) — © 2026 luizhcrs. PRs bem-vindos.
