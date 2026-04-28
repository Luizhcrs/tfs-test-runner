# Arquitetura

Tour breve de como o pipeline está montado. Total: ~700 LOC + ~600 LOC de HTML/CSS/JS template.

## Visão geral do pipeline

```
arquivo xlsx
   │
   ▼
parse.parse_xlsx          → list[Case]   (origem em inglês)
   │
   ▼
translate.translate_cases → list[Case]   (idioma alvo; snapshots *_en preservados)
   │
   ▼
classify.assign_phases    → list[Phase]  (ou apply_yaml_phases para grupo explícito)
   │
   ▼
render.render             → arquivo .html único (CSS + JS + JSON embedded + logo base64)
```

Cada estágio é função pura sobre dicts; JSON intermediário pode ser dumped via `--dump-json` pra debug.

## Formato dos dados

### Case (após parse)
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

### Case (após translate)
Mesma forma + snapshots dos originais:
```python
{
    "id": "101",
    "title": "Login - Sign-in com sucesso",        # traduzido
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

Os campos `*_en` são o que o **layout de evidência do PDF** usa, já que evidência pro cliente é convencionalmente em inglês.

### Phase
```python
{
    "id": "p1",
    "title": "Phase 1 — Smoke",
    "level": "easy",        # easy | med | hard (cosmético, cor do badge)
    "desc": "Caminho crítico.",
    "cases": [Case, Case, ...],
}
```

## Módulo a módulo

### `parse.py`
- Usa `openpyxl` em `read_only=True, values_only=True` por eficiência de memória.
- Header parseado uma vez; colunas mapeadas por alias case-insensitive (`HEADER_ALIASES`). Colunas obrigatórias faltando lançam `ValueError` cedo, antes de qualquer custo de tradução.
- Linha com `Work Item Type = Test Case` abre novo caso; linhas seguintes empilham em `steps` até o próximo test case.
- Whitespace (incluindo NBSP / zero-width) normalizado em `_clean()`.

### `translate.py`
Dois backends:

**`backend="none"`** (default): pass-through. A função ainda snapshot os campos `*_en` pra que o resto do pipeline possa contar com eles.

**`backend="llm"`**:
1. Coleta strings únicas em todos os títulos, actions, expecteds (deduplicação economiza muito — a maioria dos test plans tem centenas de frases compartilhadas repetidas).
2. Quebra em chunks limitados por **count** (≤ 80 strings) e **tamanho do payload** (≤ 12 KB UTF-8). Qualquer um dos limites trigga corte.
3. Cada chunk vai via OpenAI Chat Completions com `response_format={"type": "json_object"}`. O system prompt é idêntico entre chunks pra pegar prompt cache automático da OpenAI a partir da segunda chamada.
4. Por chunk: **exponential backoff** (3 tentativas, base 2s). Se falhar terminal ou JSON malformado, o chunk cai pra **strings originais** (sem tradução, mas a run continua).
5. Traduções finais mapeadas de volta pros casos (titles, actions, expecteds) via lookup de dict determinístico.

O argumento opcional `glossary` alimenta o system prompt com `preserve` (termos a não traduzir) e `notes` (texto livre de contexto).

### `classify.py`
- **Default** (`assign_phases`): fase única com todos os casos. Útil quando não precisa organizar ou como baseline.
- **YAML override** (`apply_yaml_phases`): cada definição de fase casa por:
  - `case_ids`: lista explícita de case IDs
  - `match`: lista de substrings case-insensitive testadas contra `title_en` (ou `title` se `_en` ausente)
- Cada caso é atribuído no máximo uma vez (primeiro match na ordem do YAML ganha).
- Casos não casados caem na **"Outros"** automática no fim.

### `render.py`
- Template Jinja2 único (`tfs_test_runner/template/plano.html.j2`).
- Phase data serializado JSON e embedded dentro de `<script>`. **`_safe_json` escapa** `</`, `<!--`, U+2028, U+2029 pra prevenir breakout de script tag e erros de parse JS.
- Logo (se `--logo` setado) lido uma vez, base64-encoded, embedded como CSS variable `--logo-url`. Se ausente, a variável é omitida e as regras CSS que dependem dela ficam inertes.
- Output é **um arquivo HTML totalmente auto-contido** — sem links externos, sem CDN, funciona offline indefinidamente.

### `template/plano.html.j2` (a UI runtime)
- **JS vanilla** — sem React, sem build step, sem npm.
- **State**: `localStorage` pra texto (status, notas, legendas), **IndexedDB** pras data URLs de imagens (blobs grandes que estourariam quota do localStorage).
- **Captura de imagem**: paste-zone escuta `paste` / `drop` / clique no file-picker. Cada imagem é chaveada por `step:<caseId>:<stepIdx>:<timestamp>_<rand>` ou `case:<caseId>:<timestamp>_<rand>`.
- **Modos de impressão**:
  - `body.print-evidence` — esconde tudo exceto imagens + labels EN dos steps. Usado por export PDF por caso E geral.
  - `body[data-print-case]` — adicionalmente esconde todo caso exceto o que tem `.print-target`.
- **Capa do PDF** renderizada em `#print-cover` apenas pra exports do plano completo.

## Por que essas escolhas

- **Sem SaaS, sem backend, sem auth.** O tester abre o HTML em qualquer navegador. Evidência fica na máquina dele até exportar PDF / JSON. Funciona dentro de VPN corporativa sem pedido de infra.
- **Formato de backup JSON é round-trip safe** — incluindo data URLs base64. Permite ao tester pausar, compartilhar com colega ou trocar de máquina.
- **Arquivo HTML único** evita custo operacional de hospedagem. É um artefato pra mandar por email, anexar em ticket Jira ou empacotar em ZIP.
- **Tradução GPT é opt-in.** Pass-through gratuito cobre o caso onde o time trabalha em inglês. Tradução é conveniência paga, não dependência rígida.

## Performance

- `parse.py`: stream de rows; testado em export de 781 linhas, parseia em ~50ms.
- `translate.py` (LLM): ~430 strings únicas → ~6 chunks → 6 chamadas API sequenciais. Com `gpt-4o-mini` típico é 30–60 segundos, ~$0.05.
- `render.py`: ~410 KB de output pra 36 cases / 744 steps. JSON embedded domina.
- Runtime do navegador: testado com 700+ steps e ~50 screenshots; rolagem 60fps. IndexedDB é o único bottleneck (browsers limitam ~50 MB / origin sem pedido de quota).
