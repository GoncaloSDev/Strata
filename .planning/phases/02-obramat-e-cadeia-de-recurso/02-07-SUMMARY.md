---
phase: 02-obramat-e-cadeia-de-recurso
plan: 07
subsystem: cadeia de recurso (degrau IA)
status: complete
gap_closure: true
tags: [ia, validacao, cadeia, gap-closure]
requires:
  - "02-05: degrau IA (offers_from, parse_price, rung)"
  - "02-06: cadeia completa e linha de comandos"
provides:
  - "strata.ai.offers_from levanta StoreError('IA não leu nenhuma oferta válida na página; …') quando valid == 0"
  - "strata.ai.PRICE_FORMAT, TEXT_PRICE, PRICE_WINDOW = 300"
  - "parse_price só com formatos de preço reais"
affects: [search_store (estado pela prioridade quando a IA falha), report]
tech-stack:
  added: []
  patterns:
    - "Oferta da IA ancorada ao link: o preço, por valor, tem de estar em € nos 300 caracteres a seguir à 1.ª ocorrência de '<URL>'"
    - "Degrau sem nenhuma oferta válida é falha do degrau (como o jsonld.py), nunca 'sem resultados'"
key-files:
  created: []
  modified:
    - src/strata/ai.py
    - tests/test_ai.py
    - tests/test_chain.py
    - .planning/phases/02-obramat-e-cadeia-de-recurso/deferred-items.md
key-decisions:
  - "Preço comparado por valor contra os TEXT_PRICE da janela (não por substring): '62,00 €' da IA bate com '62 €' da página, e '8,50' dentro de '28,50' ou o '2' de 'Recolha 2 horas' deixam de passar"
  - "Url com o mesmo caminho da página de pesquisa é recusado: cobre o url vazio, a própria página e os links dela para si própria"
  - "search.py sem mudanças: o except StoreError de search_store já dá o estado pela prioridade com o motivo de cada degrau"
requirements-completed: [STORE-06]
duration: 5 min
completed: 2026-10-31
estimate:
  tokens: 40000
  tasks: 2
actuals:
  tokens: 4200
  tasks: 2
  commits: 3
plan_head_before: adc3527a7648dabd32ff0e28f4b9e9b1f33f3926
plan_head_after: c4e728c0392022b397bff856fe2be35c6903e3ba
coverage:
  - deliverable: "IA sem ofertas válidas: a loja sai falhada pela prioridade com o motivo de cada degrau no terminal (CR-01)"
    human_judgment: false
    verification:
      - kind: test
        ref: "tests/test_ai.py#test_ponta_a_ponta_ia_sem_ofertas_validas_loja_falha_com_o_motivo"
        status: pass
      - kind: test
        ref: "tests/test_chain.py#test_ia_so_com_ofertas_rejeitadas_loja_falha_com_o_motivo_de_cada_degrau"
        status: pass
      - kind: test
        ref: "tests/test_chain.py#test_degrau_ia_uma_so_chamada_sem_pesquisa_alargada"
        status: pass
  - deliverable: "Oferta da IA só com o link no texto e o preço em € junto dele; url vazio e página de pesquisa recusados (CR-02)"
    human_judgment: false
    verification:
      - kind: test
        ref: "tests/test_ai.py#test_offers_from_rejeita_o_que_nao_esta_junto_do_link"
        status: pass
      - kind: test
        ref: "tests/test_ai.py#test_offers_from_caso_da_verificacao_falha_o_degrau"
        status: pass
  - deliverable: "Ofertas reais das páginas gravadas continuam a passar (Obramat 7 + 18, Allmat 3)"
    human_judgment: false
    verification:
      - kind: test
        ref: "tests/test_ai.py#test_offers_from_aceita_as_ofertas_reais_das_paginas_gravadas"
        status: pass
      - kind: test
        ref: "tests/test_ai.py#test_offers_from_aceita_as_ofertas_reais_da_allmat"
        status: pass
  - deliverable: "parse_price só com formatos reais (WR-07)"
    human_judgment: false
    verification:
      - kind: test
        ref: "tests/test_ai.py#test_parse_price"
        status: pass
---

# Phase 2 Plan 07: Contrato de saída do degrau IA — Summary

**Quando a IA não lê nenhuma oferta válida, a loja aparece falhada com o motivo de cada degrau. Uma oferta da IA só entra se o link estiver na página enviada e o preço estiver escrito em € nos 300 caracteres a seguir a esse link.**

## O que agora funciona

1. Obramat bloqueada, browser sem lista e IA sem ofertas válidas. A linha no terminal é
   `  Obramat: bloqueada — API: HTTP 403; JSON-LD: HTTP 403; browser: página da Obramat sem lista de resultados (layout mudou?); IA: IA não leu nenhuma oferta válida na página`.
   "sem resultados" fica só para respostas da própria loja.
2. O preço do produto anterior ou do seguinte, "8,50" dentro de "28,50", o "2" de "Recolha 2 horas", um link inventado, um url vazio e a própria página de pesquisa ficam rejeitados e contados na nota `N ofertas da IA rejeitadas (link fora da página da loja ou preço longe do link)`.
3. `parse_price('12.5')`, `parse_price('1e3')`, `parse_price('62 €')` e `parse_price('1 299,60 €')` dão `None None 62 1299.60` (antes `125 1E+3 62 1299.60`).
4. As 7 + 18 ofertas reais da Obramat (incluindo a de "62 €", sem cêntimos) e as 3 da Allmat continuam a passar.
5. Ofertas válidas todas escondidas pelo filtro de título continuam a dar "ok" com "0 ofertas mostradas; N escondidas" (D-14 sem mudança).

## Tarefas

| # | Tarefa | Commit | Ficheiros |
|---|--------|--------|-----------|
| 1 | Ponta a ponta: IA sem ofertas válidas → loja falhada com o motivo (CR-01) | 7e1c401 | src/strata/ai.py, tests/test_ai.py, tests/test_chain.py |
| 2 | RED: link no texto, preço junto do link, parse_price | 49e7d93 | tests/test_ai.py |
| 2 | GREEN: PRICE_FORMAT, TEXT_PRICE, PRICE_WINDOW e offers_from (CR-02, WR-07) | c4e728c | src/strata/ai.py, deferred-items.md |

Portão do tracer (tarefa 1): `<verify>` voltou a correr inteiro depois do commit e passou (4 testes escolhidos, 342 no total). Seguiu para a tarefa 2.

## Verificação

- `uv run pytest -q`: 360 passed (antes: 339)
- `uv run pytest tests/test_ai.py -q`: 55 passed (antes: 35)
- `git diff --stat adc3527 -- src/strata/search.py pyproject.toml uv.lock`: vazio
- `uv run python -m strata pesquisar --help` continua a mostrar `--sem-principal`
- `ask`, `_ask_api`, `_ask_claude`, `SCHEMA`, `PROMPT` e `MODEL` sem mudanças; os testes `test_ask_*` e `test_ponta_a_ponta_todos_os_degraus_falham_e_a_ia_le_a_pagina` não foram tocados

## TDD Gate Compliance

- RED: 49e7d93 (`test(02-07)`), 17 falhas pelos motivos esperados (parse_price aceitava "12.5"/"1e3", nota antiga, preço do vizinho e "8,50" aceites, url vazio aceite, "62,00 €" rejeitado na página "cimento cola", caso da verificação sem StoreError)
- GREEN: c4e728c (`fix(02-07)`), 55 passed em tests/test_ai.py
- REFACTOR: não foi preciso

## Deviations from Plan

### Auto-fixed Issues

Nenhum desvio de comportamento. Dois pormenores:

- `test_parse_price` tem mais 3 casos de None do que a lista do plano pedia ("NaN", "1.299.00", "12,345"). Estão no `<action>` da tarefa 2 como formatos a recusar.
- Saiu o `InvalidOperation` do import: com `PRICE_FORMAT` o `Decimal(...)` só recebe dígitos e já não pode falhar.

## Known Stubs

Nenhum.

## Itens adiados

Registados em `deferred-items.md`:
- `MAX_CHARS = 20_000` corta a página gravada da Allmat antes do 1.º produto (carácter ~21 850). O degrau IA da Allmat falha sempre, agora com o motivo.
- A janela de 300 caracteres ainda deixa entrar o preço sem IVA e o preço por m² da mesma oferta (WR-01). Ficam rejeitados com nota o formato "€ 28,50" e o preço escrito antes do link (os dois `shortcut:` novos).

## Self-Check: PASSED

- FOUND: src/strata/ai.py, tests/test_ai.py, tests/test_chain.py, deferred-items.md
- FOUND: 7e1c401, 49e7d93, c4e728c (antecessores de HEAD)
