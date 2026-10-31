---
phase: 02-obramat-e-cadeia-de-recurso
plan: 06
subsystem: pesquisa
status: complete
tags: [verificar, obramat, chrome-dedicado, list-03, readme]
requires:
  - phase: 02-05
    provides: "degrau IA e cadeia completa principal → JSON-LD → browser → IA"
provides:
  - "verificar com 5 canários (4 lojas), método da oferta mais barata em cada OK"
  - "Obramat pelo Chrome dedicado quando o pedido simples responde sem o armazém 201 (D-18)"
  - "README com as 4 lojas e a cadeia de recurso"
  - "prova ao vivo do LIST-03: 10 itens nas 4 lojas em 222,8 s"
affects: [phase-03, phase-04]
tech-stack:
  added: []
  patterns: ["resposta 'held': preços estruturados guardados enquanto se tenta o browser; se o browser falhar, ficam esses preços com o motivo"]
key-files:
  created:
    - .planning/phases/02-obramat-e-cadeia-de-recurso/deferred-items.md
  modified:
    - src/strata/search.py
    - tests/test_search.py
    - tests/test_chain.py
    - README.md
key-decisions:
  - "Pedido simples da Obramat sem o armazém 201 (nota NO_STORE) escala para o browser, sem passar pelo JSON-LD nem pela IA; se o browser falhar, ficam os preços do pedido simples"
  - "K, LIMITS e DEADLINE_S sem mudanças: a corrida de 10 itens coube nos 5 minutos sem mexer no ritmo"
requirements-completed: [LIST-03, STORE-04]
duration: 12min
completed: 2026-10-31
actuals:
  tokens: 3600
  tasks: 2
  commits: 2
plan_head_before: af4d708b8f81c7d8d5b3f52330bf50ca9a06ca4b
plan_head_after: 3c3ca3613b9e28c339decad225e51c6ef9fc7710
---

# Phase 2 Plan 06: Verificar com as 4 lojas e corrida de 10 itens Summary

**O `verificar` cobre as 4 lojas (5 canários) e diz o método de cada preço; a Obramat passa a ir ao Chrome dedicado quando o pedido simples vem sem o armazém de Alfragide; uma folha real de 10 itens resolveu-se nas 4 lojas em 222,8 s.**

## Desempenho

- Duração: ~12 min (inclui as duas corridas ao vivo)
- Tarefas: 2 de 2
- Ficheiros: 5 (4 alterados, 1 criado)
- START (HEAD antes da tarefa 1): `af4d708b8f81c7d8d5b3f52330bf50ca9a06ca4b`

## Feito

1. `CANARIES` ganha `(obramat, "osb")`; o OK diz `(método: …)` da oferta mais barata.
2. `_problem` falha com ofertas lidas por IA ("preços lidos por IA: os degraus estruturados falharam"), com ofertas sem o armazém e com a nota `NO_STORE` da Obramat.
3. `search_store`: quando um degrau sem browser devolve a nota `obramat.NO_STORE` e há browser, tenta o browser (D-18). Se o browser falhar, ficam os preços do pedido simples, com o motivo de cada degrau numa nota.
4. README: Obramat na 1.ª linha, secção "## Como cada loja é lida", `--sem-principal LOJA`, degrau IA (`ANTHROPIC_API_KEY` ou `claude`), tempo medido.

## Commits

| Tarefa | Commit | Ficheiros |
|---|---|---|
| 1. verificar com a Obramat + escalada para o browser | `31ec980` | src/strata/search.py, tests/test_search.py, tests/test_chain.py |
| 2. README e corrida de 10 itens | `3c3ca36` | README.md, deferred-items.md |

## Provas ao vivo (2026-10-31)

### `verificar` (tarefa 1)

Antes da correção: 4 OK e `Obramat (osb): FALHOU — armazém por escolher no Chrome dedicado (escalões e stock por ler)`, rc=1, 54 s. O canário fez o que devia: apanhou uma falha real.

Depois, rc=0 em 62 s:

```
Allmat (cimento): OK — 11 ofertas, mais barata 4,22 € (método: API)
Allmat (pavimento): OK — 24 ofertas, mais barata 7,50 € (método: API)
Bricomarché (cimento): OK — 10 ofertas, mais barata 0,79 € (método: API)
Obras 360 (osb): OK — 20 ofertas, mais barata 8,36 € (método: API)
Obramat (osb): OK — 6 ofertas, mais barata 6,90 € (método: browser)
```

### Folha de 10 itens (tarefa 2, LIST-03)

- Tempo de parede: **222,8 s** (3 min 43 s), abaixo dos 300 s. rc=0.
- 10 cabeçalhos "Linha N — …"; 10 linhas de estado para cada uma das 4 lojas.
- Porta 9222 antes: fechada; depois: fechada. O Chrome que a app abriu fechou-se no fim (D-06).
- Nenhum CAPTCHA, nenhum "abrir à mão", nenhuma oferta lida por IA. O degrau IA não foi preciso, por isso "IA não configurada" não apareceu.

| Loja | ok | sem resultados | bloqueada | erro | tempo esgotado | abrir à mão | Método |
|---|---|---|---|---|---|---|---|
| Allmat | 8 (3 com pesquisa alargada) | 2 (placa osb 12mm, tinta branca 15L) | 0 | 0 | 0 | 0 | API |
| Bricomarché | 10 (5 com pesquisa alargada) | 0 | 0 | 0 | 0 | 0 | API |
| Obras 360 | 10 (4 com pesquisa alargada) | 0 | 0 | 0 | 0 | 0 | API |
| Obramat | 10 | 0 | 0 | 0 | 0 | 0 | browser nos 10 itens |

Obramat por item: método `browser` nos 10 itens, com escalões e stock "em OBRAMAT Lisboa - Alfragide" nas 3 primeiras ofertas. Só o 1.º item teve a nota "antes do browser: API: sem o armazém OBRAMAT Lisboa - Alfragide na sessão"; daí em diante a loja ficou no browser (D-08).

STORE-04 (A5): o DataDome não bloqueou nada ao longo dos 10 itens. O pedido simples passou no 1.º item, e o browser passou os 10 sem CAPTCHA.

## Desvios ao plano

### Corrigidos automaticamente

**1. [Regra 1 - Bug] A Obramat nunca chegava ao Chrome dedicado**
- Encontrado na: tarefa 1, primeira corrida ao vivo do `verificar`
- Problema: hoje o `curl_cffi` passa o DataDome, por isso o degrau API respondia e a cadeia parava ali. A sessão simples não tem o armazém 201, logo a Obramat saía sempre sem escalões nem stock exato (nota `NO_STORE`), o que contraria o D-18 ("a Obramat lê-se pelo browser") e o que o plano esperava ("método: browser").
- Correção: em `search_store`, uma resposta com `obramat.NO_STORE` vinda de um degrau sem browser fica guardada e a cadeia salta para o browser, sem JSON-LD nem IA. Se o browser responder, vale o browser (e a loja fica no browser, D-08). Se falhar ou acabar o prazo, ficam os preços do pedido simples com o motivo numa nota. Dois testes novos em `tests/test_chain.py` cobrem os dois caminhos.
- Ficheiros: src/strata/search.py, tests/test_chain.py
- Commit: `31ec980`

**2. [Regra 3 - Bloqueio] Comandos da verificação reescritos**
- Os comandos `<automated>` do plano (variáveis e `python -c` dentro de `&&`) foram recusados pela sandbox do worktree. Corri o mesmo com scripts no scratchpad: a mesma folha de 10 itens, o mesmo `uv run python -m strata pesquisar`, cronómetro de parede, contagem de "Linha " e das 4 lojas, e a porta 9222 antes e depois.

## Itens adiados

- `src/strata/report.py:24` mostra percentagens de escalão sem arredondar (ex.: `−5,0021285653469561515538527% a partir de 324`). Só apresentação, de antes deste plano; registado em `deferred-items.md`.

## Próximo

A fase 2 tem os 6 planos feitos. Falta o verificador da fase.

## Self-Check: PASSED

- FOUND: src/strata/search.py, tests/test_search.py, tests/test_chain.py, README.md, deferred-items.md
- FOUND: 31ec980, 3c3ca36 (antepassados de HEAD)
- `uv run pytest -q`: 339 passed
