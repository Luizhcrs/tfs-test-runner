# Configuração

Toda configuração é opt-in via flags ou arquivos YAML. Defaults funcionam sem nenhuma config.

## Agrupamento em fases (`--phases phases.yaml`)

Agrupa test cases em fases pra execução organizada. Sem essa flag, todos os casos caem numa única fase "All cases".

```yaml title="phases.yaml"
phases:
  - id: "p1"
    title: "Fase 1 — Smoke"
    level: easy            # easy | med | hard (cor do badge, cosmético)
    desc: "Cenários positivos críticos rodados em cada build."
    case_ids: ["101", "104", "108"]   # IDs explícitos

  - id: "p2"
    title: "Fase 2 — Cenários de falha"
    level: med
    desc: "Caminhos negativos e tratamento de erros."
    match: ["failure", "invalid", "error"]   # substring case-insensitive no título

  - id: "p3"
    title: "Fase 3 — Casos de borda"
    level: hard
    desc: "Concorrência, fronteira e condições raras."
    case_ids: ["201", "202"]
    match: ["edge", "boundary", "concurrent"]   # combina ambos
```

### Regras de match

- Um caso é atribuído a **no máximo uma fase** (primeira fase no YAML que matcha vence).
- `case_ids` e `match` podem ser combinados; caso matcha se qualquer condição for verdadeira.
- Casos não matchados por nenhuma fase caem na **"Others"** automática ao final.

### Levels

`easy`, `med`, `hard` afetam apenas a cor do badge no HTML (verde / amarelo / vermelho). Sem impacto funcional.

## Glossário LLM (`--glossary glossary.yaml`, requer `--llm`)

Refina o comportamento da tradução LLM com guidance específica do domínio.

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
  Domínio: QA de aplicação web. Users executam test cases manualmente.
  Tom: técnico, imperativo ("Clicar", "Digitar", "Verificar").
  Manter labels de botão no idioma original já que a UI é em inglês.
```

`preserve` terms vão verbatim no system prompt do LLM — modelo é instruído a nunca traduzir. Útil pra nomes de produto, labels de UI, jargão técnico.

`notes` é texto livre acrescentado como contexto de domínio. Ajuda o modelo a pegar o tom e terminologia certos.

## Logo (`--logo logo-empresa.png`)

Logo customizado aparece no topo de cada página de test case no PDF.

- Suportado: PNG, JPG, SVG, GIF
- Tamanho recomendado: 200×60 px (renderiza a 42px de altura no PDF)
- Embedded como base64 data URL — sem link externo, funciona offline
- Default: sem logo (toolkit não vem com branding)

```bash
tfs-test-runner cases.xlsx --logo minha-empresa.png -o plano.html
```

## Título (`--title "..."`)

Define o título da aba do navegador e o H1 no header da página. Default: `"Test Execution Plan"`.

```bash
tfs-test-runner cases.xlsx --title "Sprint 42 — Aceite" -o plano.html
```

## Modelo LLM (`--model gpt-4o-mini`)

Com `--llm` setado, você pode escolher qualquer modelo OpenAI-compatível.

| Modelo | Custo (run típica, 36 casos) | Velocidade | Qualidade |
|---|---|---|---|
| `gpt-4o-mini` (default) | ~$0.05 | ~30s | Boa |
| `gpt-4o` | ~$0.50 | ~45s | Melhor |
| `gpt-4-turbo` | ~$0.30 | ~40s | Excelente |

```bash
export OPENAI_API_KEY=sk-...
tfs-test-runner cases.xlsx --llm --lang pt-BR --model gpt-4o-mini -o plano.html
```

Backend LLM usa Chat Completions JSON mode, batches de tradução em chunks de 80 strings ou 12 KB (o que vier primeiro), e tenta cada chunk até 3 vezes com exponential backoff. Chunks falhos caem pra strings originais.

## Arquivo de saída (`-o output.html`, `--output output.html`)

Default: `test-plan.html` no diretório atual.

```bash
tfs-test-runner cases.xlsx -o ~/Desktop/sprint42-plano.html
```

## Force overwrite (`-f`, `--force`)

Sem essa flag, o CLI recusa sobrescrever arquivo existente.

```bash
tfs-test-runner cases.xlsx -o plano.html --force
```

## Debug JSON dump (`--dump-json intermediate.json`)

Escreve os dados translated/classified como JSON. Útil pra debugar output do LLM ou construir tools downstream customizadas.

```bash
tfs-test-runner cases.xlsx --dump-json debug.json -o plano.html
```

## Referência CLI completa

```bash
tfs-test-runner --help
```
