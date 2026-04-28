# Guia de uso

Walkthrough end-to-end pra um tester executando um Azure DevOps test plan com `tfs-test-runner`.

## 1. Exportar do Azure DevOps

No **Azure Boards / Azure Test Plans**:

1. Abrir sua **Test Suite** ou **Test Plan**.
2. Clicar em **Export → Excel**.
3. Salvar o `.xlsx` resultante na sua máquina.

O arquivo exportado terá no mínimo essas colunas: `ID`, `Work Item Type`, `Title`, `Test Step`, `Step Action`, `Step Expected`, mais opcionais `Area Path`, `Assigned To`, `State`. O `tfs-test-runner` detecta pelo nome do header, então a ordem das colunas não importa.

## 2. Gerar o kit HTML

```bash
tfs-test-runner meu-export.xlsx -o plano.html
```

Abrir `plano.html` no Chrome, Edge ou Firefox.

### Com agrupamento em fases
Criar `phases.yaml` listando quais case IDs vão pra cada fase. Ver [examples/sample-phases.yaml](../examples/sample-phases.yaml). Daí:
```bash
tfs-test-runner meu-export.xlsx --phases phases.yaml -o plano.html
```

### Com tradução LLM
```bash
export OPENAI_API_KEY=sk-...
tfs-test-runner meu-export.xlsx --llm --lang pt-BR -o plano-pt.html
```
Adicionar `--glossary glossary.yaml` pra ensinar ao modelo termos a manter verbatim.

### Com logo da empresa
```bash
tfs-test-runner meu-export.xlsx --logo logo-empresa.png -o plano.html
```
O logo aparece no topo de cada página de test case no PDF.

## 3. Executar testes no kit HTML

Pra cada caso:

1. **Expandir** o caso (clicar no header).
2. Pra cada step:
   - **Ler** Ação e Esperado.
   - **Executar** o step no sistema sob teste.
   - **Tirar screenshot** (Print Screen / Snipping Tool / atalho do SO).
   - **Clicar** na paste-zone do step (fica verde = "pronto pra colar").
   - **Pressionar Ctrl+V** pra anexar o screenshot. Múltiplas screenshots por step são suportadas.
   - **Clicar na thumb** pra abrir o lightbox; digitar legenda e clicar fora pra salvar.
   - **Definir status**: PASS / FAIL / N/A no dropdown.
   - **Adicionar nota** se necessário no textarea ao lado do dropdown.
3. **Seguir adiante**. Estado salva automaticamente em `localStorage` (texto/state) e `IndexedDB` (imagens) a cada mudança.

### Filtros rápidos

A linha de chips no header filtra casos por status: **Pendentes / Em andamento / OK / Com falha**. Útil quando você tem 100+ casos e quer focar no que falta.

### Busca

Pressionar `/` foca a busca. Casa case ID e título (substring case-insensitive).

## 4. Gerar PDFs de evidência

### PDF por caso (entregável típico)
1. Abrir o caso.
2. Clicar **PDF deste caso** no toolbar do caso.
3. No diálogo de impressão: **desmarcar "Cabeçalhos e rodapés"**, escolher **Salvar como PDF**, clicar Salvar.

O resultado é a evidência do caso: logo + título + screenshots em ordem cronológica com legendas. Steps sem screenshots são omitidos automaticamente.

### PDF do plano completo
1. Clicar **PDF Geral (evidências)** no toolbar do topo (ou apertar `Ctrl+P`).
2. Aguardar a renderização da capa + cada caso.
3. **Desmarcar "Cabeçalhos e rodapés"**, salvar como PDF.

Inclui capa com data e tabela resumo (casos / steps / OK / falha / pendente por fase), depois uma página por caso.

## 5. Backup / restore / compartilhar estado

- **Exportar backup** (toolbar topo): baixa um JSON com todo o estado + data URLs das imagens. Round-trip safe.
- **Importar backup**: restaura do JSON. Útil quando:
  - Trocando de máquina no meio da execução.
  - Compartilhando trabalho parcial com colega.
  - Recuperando após limpeza de cache do navegador.

> ⚠ O arquivo de backup pode ser **grande** (dezenas de MB) porque inclui cada screenshot em base64. Não manda por email; usa file share.

## 6. Pegadinhas comuns

| Sintoma | Causa provável | Fix |
|---|---|---|
| "Cabeçalhos e rodapés" aparecem no PDF | Navegador injeta por default | Desmarcar no diálogo → *Mais configurações* |
| Screenshot colado não aparece | Paste-zone não focada | Clicar na zona primeiro (fica verde) → daí Ctrl+V |
| `OPENAI_API_KEY not set` | Variável de ambiente faltando | `export OPENAI_API_KEY=...` (ou `setx` no Windows) |
| `ValueError: missing required columns` | Export xlsx sem headers | Re-exportar do Azure DevOps com colunas default |
| Tradução estoura rate-limit | Muitas runs paralelas | Esperar, o chunk cai pro original; tentar de novo |

## 7. Dicas pra entrega tranquila

- **Smoke pass primeiro** com `--llm` se precisa traduzir; revisa algumas traduções antes de rodar tudo.
- **Manter casos organizados via YAML** (`--phases`) — muito mais fácil que rolar 50+ casos chapados.
- **Usar `--title`** pra um header significativo (ex. `"Sprint 42 — Aceite"`); aparece na aba do navegador e na capa do PDF.
- **Exportar backup periodicamente** por segurança; localStorage / IndexedDB pode ser limpo por ferramentas de limpeza.
- **Um HTML por ciclo**: não tente reusar o mesmo arquivo entre sprints. Re-gera de um xlsx fresh cada vez.
