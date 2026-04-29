# Contribuindo

Obrigado por considerar contribuir. Projeto é pequeno e intencionalmente simples — mantenha mudanças focadas e bem testadas.

## Setup de desenvolvimento

```bash
git clone https://github.com/luizhcrs/tfs-test-runner.git
cd tfs-test-runner
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest -q
```

## Convenções do projeto

- **Python ≥ 3.10**, type hints encorajados onde agreguem clareza (`from __future__ import annotations`).
- **Sem formatter forçado** — match com estilo ao redor (indent 4 espaços, aspas duplas, trailing commas em literais multi-line).
- **Tests first** pra bugs não-triviais (abra issue, depois teste falhando, depois fix).
- **Sem fallbacks silenciosos** no CLI: toda decisão importante passa por `_log()` pro user ver o que aconteceu.
- **Commits**: subject curto imperativo, body opcional explicando o *porquê*. Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`) são apreciados mas não forçados.

## O que testar

Cada módulo tem `tests/test_<module>.py` correspondente:

- `parse.py` — detecção de header, tolerância de colunas opcionais, blank-row handling.
- `translate.py` — chunking, construção de system prompt, passthrough. (Chamada LLM em si não é testada via rede.)
- `classify.py` — fase default única, prioridade id/match em YAML, leftover handling.
- `render.py` — JSON escaping (script injection), template wiring, force-overwrite guard.
- `cli.py` — Click subcommand help, smoke tests de cada subcomando.

Pra features novas, adiciona testes ao lado dos do módulo correspondente. CI roda em Linux / macOS / Windows × Python 3.10 / 3.11 / 3.12.

## Submetendo mudanças

1. Fork → branch (`feat/nome-curto` ou `fix/nome-curto`).
2. Roda `pytest` local; garante que CI fica verde depois do push.
3. Abre PR descrevendo o quê e *porquê*. Linka issue relacionada se houver.
4. Pra mudanças UI / template, anexa screenshot before/after ou clip curto.

## Fora de escopo (não merga)

- SaaS lock-in (auth, telemetria, backend hospedado).
- APIs cloud obrigatórias — `--llm` continua opcional.
- Glossários vendor-specific hardcoded no pacote — manter só em `examples/*.yaml`.
- Dependências client-side pesadas (React / Vue / build step). HTML kit é vanilla por design — funciona offline pra sempre.

## Reportando issues

Ao abrir uma issue, inclua:
- OS + versão Python
- Sample xlsx mínima (ou caso sintético menor que reproduz o bug — veja `examples/generate_sample.py` pro formato)
- Invocação exata do CLI
- Output completo (stderr) e qualquer traceback

## Release (maintainers)

1. Bumpa `__version__` em `tfs_test_runner/__init__.py` e `version` em `pyproject.toml`.
2. Atualiza `CHANGELOG.md` com a nova entry.
3. Tag `vX.Y.Z` e push:

   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z" && git push --tags
   ```

4. GitHub Actions `release.yml` builda e publica no PyPI automaticamente via Trusted Publishing (OIDC). Se precisar manualmente:

   ```bash
   pip install build twine
   python -m build
   twine upload dist/*
   ```
