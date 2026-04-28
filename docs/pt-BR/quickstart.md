# Início rápido

Gere seu primeiro kit HTML em 30 segundos.

## Instalação

=== "Do source"

    ```bash
    git clone https://github.com/luizhcrs/tfs-test-runner.git
    cd tfs-test-runner
    pip install -e .
    ```

=== "Com tradução LLM"

    ```bash
    pip install -e ".[llm]"
    export OPENAI_API_KEY=sk-...
    ```

=== "Dev / contribuindo"

    ```bash
    pip install -e ".[dev]"
    pytest -q
    ```

Python ≥ 3.10 obrigatório.

## Gerar seu primeiro plano

### Opção A — Sample sintético (sem dado real)

```bash
python examples/generate_sample.py
tfs-test-runner examples/sample.xlsx -o sample-out.html
```

Abre `sample-out.html` no navegador. Verá um plano funcional com 3 casos / 13 steps.

### Opção B — Export real do Azure DevOps / TFS

1.  Abrir Test Plan / Test Suite no Azure DevOps ou TFS.
2.  Clicar **Export → Excel**.
3.  Rodar o CLI:

    ```bash
    tfs-test-runner meu-export.xlsx -o plano.html
    ```

### Opção C — Template em branco (sem Azure DevOps)

Se você não tem Azure DevOps:

1.  Baixar [blank-template.xlsx](https://github.com/Luizhcrs/tfs-test-runner/raw/main/examples/blank-template.xlsx).
2.  Preencher rows seguindo o schema (ver comentários na primeira linha).
3.  Rodar o CLI:

    ```bash
    tfs-test-runner blank-template.xlsx -o plano.html
    ```

## O que você obtém

Um arquivo HTML único (~50–500 KB dependendo do tamanho do plano) que contém:

- Árvore fase / caso / step (expandível)
- Status PASS / FAIL / N/A por step
- Textarea de notas por step
- Paste-zone pra screenshots (Ctrl+V ou clicar "Anexar arquivo")
- Busca (`/`) e filter chips
- Backup / restore como JSON
- PDF por caso + PDF do plano completo

State salva automaticamente em `localStorage` (texto) e `IndexedDB` (imagens). Fechar a aba e reabrir continua de onde parou.

## Flags comuns

```bash
# Tradução GPT pra português brasileiro
tfs-test-runner cases.xlsx --llm --lang pt-BR -o plano.html

# Agrupar casos em fases via YAML
tfs-test-runner cases.xlsx --phases examples/sample-phases.yaml -o plano.html

# Logo customizado e título
tfs-test-runner cases.xlsx \
    --logo logo-empresa.png \
    --title "Sprint 42 — Aceite" \
    -o sprint42.html

# Ver todas as opções
tfs-test-runner --help
```

## Próximos passos

- [Guia de uso](usage.md) — walkthrough completo pro tester
- [Configuração](configuration.md) — configs YAML, glossários, logos
- [Arquitetura](architecture.md) — como o pipeline funciona por baixo
