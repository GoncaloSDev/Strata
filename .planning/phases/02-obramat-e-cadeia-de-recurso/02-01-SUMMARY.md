---
phase: 02-obramat-e-cadeia-de-recurso
plan: 01
subsystem: stores
tags: [obramat, selectolax, datatms, curl_cffi, escalões]

requires:
  - phase: 01
    provides: "Fetcher com limites por host, search_store, report, filtro de título D-15 e FakeFetcher"
provides:
  - "Adaptador strata.stores.obramat: parse_search, offer_from, product_info, parse_tiers, search"
  - "LIMITS['www.obramat.pt'] = (1, 3.0, 2.0) e Host(n, gap, jitter=0.0)"
  - "STORES = (allmat, bricomarche, obras360, obramat)"
  - "README com a secção 'Âmbito e acesso às lojas'"
affects: [02-02, 02-03, 02-06]

actuals:
  tokens: 5000  # chars/4 sobre código, testes e README alterados; as 5 fixtures copiadas tal e qual (~17 mil linhas) ficam de fora
  tasks: 2
  commits: 3
plan_head_before: ded65f5d54fc010ac25dcc7618ea8fc9ef3bee14
plan_head_after: 9881aa5f8f2fca714c876404cb689357e08bb2b0

tech-stack:
  added: []
  patterns:
    - "Lista de resultados só pelos filhos diretos de ol#guidance-product-list (carrossel e bloco promocional ficam de fora)"
    - "Escalão calculado do total da palete com IVA, conferido com o total sem IVA"
    - "Páginas de produto só para as K primeiras ofertas; falha StoreError de uma página vira nota"

key-files:
  created:
    - src/strata/stores/obramat.py
    - tests/test_obramat.py
    - tests/fixtures/obramat_search-osb_browser.html
    - tests/fixtures/obramat_search-no-results_browser.html
    - tests/fixtures/obramat_search-cimento-cola_endcap_browser.html
    - tests/fixtures/obramat_product-osb-18_ctx201_tiers.html
    - tests/fixtures/obramat_product-tijolo_ctx201_tiers.html
  modified:
    - src/strata/fetch.py
    - src/strata/search.py
    - README.md
    - tests/test_e2e.py
    - tests/test_obras360.py

key-decisions:
  - "Obramat com LOCATION fixo 'OBRAMAT Lisboa - Alfragide' (um só armazém, shortcut comentado); a nota 'mais barata sem stock' não se aplica"
  - "IVA da Obramat conferido em euros com tolerância de 0,02 € (nunca pelo rácio)"
  - "Escalões e stock exato só nas 3 primeiras ofertas (K = 3), ordenadas por palavras da pesquisa e depois preço"

patterns-established:
  - "Host com jitter opcional: o próximo início fica a gap + uniform(0, jitter) s"

requirements-completed: [STORE-04]

coverage:
  - id: D1
    description: "A Obramat é a 4.ª loja: 'placa osb' mostra 'Obramat: ok' com as placas a preço com IVA, armazém de Alfragide e links; 'cimento' dá 'sem resultados'"
    requirement: STORE-04
    verification:
      - kind: e2e
        ref: "tests/test_e2e.py#test_tres_itens_tres_lojas_pela_ordem"
        status: pass
      - kind: other
        ref: "printf 'placa osb 1 un\\n\\n' | uv run python -m strata pesquisar (ao vivo: 'Obramat: ok')"
        status: pass
    human_judgment: false
  - id: D2
    description: "Armadilhas da página: carrossel 'vistos recentemente' dá raw 0, bloco promocional fica de fora (18, não 24), página sem lista e N resultados sem produtos dão erro"
    requirement: STORE-04
    verification:
      - kind: unit
        ref: "tests/test_obramat.py#test_sem_resultados_ignora_o_carrossel_vistos_recentemente"
        status: pass
      - kind: unit
        ref: "tests/test_obramat.py#test_cimento_cola_sem_o_bloco_promocional"
        status: pass
      - kind: unit
        ref: "tests/test_obramat.py#test_total_sem_lista_da_erro_e_nunca_sem_resultados"
        status: pass
    human_judgment: false
  - id: D3
    description: "IVA conferido (0,02 €) e escalões do total da palete: OSB 18 mm → −5% a partir de 48, tijolo → −5% a partir de 270; escalão incoerente fica em nota"
    requirement: STORE-04
    verification:
      - kind: unit
        ref: "tests/test_obramat.py#test_offer_from_iva_conferido_e_na_fronteira"
        status: pass
      - kind: unit
        ref: "tests/test_obramat.py#test_parse_tiers_do_total_da_palete"
        status: pass
      - kind: unit
        ref: "tests/test_obramat.py#test_parse_tiers_com_iva_do_escalao_incoerente"
        status: pass
    human_judgment: false
  - id: D4
    description: "Só 3 páginas de produto por pesquisa; stock exato '327 em stock em OBRAMAT Lisboa - Alfragide'; nota NO_STORE sem o armazém 201"
    requirement: STORE-04
    verification:
      - kind: unit
        ref: "tests/test_obramat.py#test_search_so_le_3_paginas_de_produto"
        status: pass
      - kind: unit
        ref: "tests/test_obramat.py#test_search_le_escaloes_e_stock_da_oferta_certa"
        status: pass
      - kind: unit
        ref: "tests/test_obramat.py#test_sem_armazem_na_sessao_da_nota_e_nao_le_escaloes"
        status: pass
    human_judgment: false
  - id: D5
    description: "Ritmo da Obramat: um pedido de cada vez, 3 a 5 s entre inícios"
    requirement: STORE-04
    verification:
      - kind: unit
        ref: "tests/test_obramat.py#test_ritmo_da_obramat"
        status: pass
    human_judgment: false
  - id: D6
    description: "README com a nota de âmbito (uso pessoal, sem CAPTCHA, sem proxies, robots.txt da Obramat)"
    verification: []
    human_judgment: true
    rationale: "Texto para pessoas: o tom e o âmbito legal pedem leitura humana"

duration: 5min
completed: 2026-10-31
status: complete
---

# Phase 2 Plan 01: Obramat como 4.ª loja fixa Summary

**A Obramat entra pela pesquisa `/search?q=`: lista principal do `dataTms`, preço com IVA conferido a 0,02 €, armazém de Alfragide, e escalões do total da palete e stock exato nas 3 primeiras ofertas.**

## Performance

- Duração: 5 min (12:39 a 12:45 UTC, 2026-10-31)
- Tarefas: 2 de 2
- Ficheiros: 7 criados, 5 alterados

## Accomplishments

- `src/strata/stores/obramat.py`: `parse_search` (só filhos diretos de `ol#guidance-product-list`), `offer_from`, `product_info`, `parse_tiers`, `_read_product` e `search`.
- `fetch.py`: `LIMITS["www.obramat.pt"] = (1, 3.0, 2.0)`; `Host` ganhou `jitter`.
- `search.STORES` com as 4 lojas; o e2e cobre a ordem das 4 e o bloco da Obramat.
- `tests/test_obramat.py`: 18 testes sem rede; `uv run pytest -q` dá 240 passed.
- README com a secção "## Âmbito e acesso às lojas".

## Task Commits

1. Tarefa 1 (tracer), Obramat ponta a ponta: `be6abb0` (feat)
2. Tarefa 2, RED: `b47fc70` (test)
3. Tarefa 2, GREEN: `9881aa5` (feat)

## TDD Gate Compliance

- RED `b47fc70`: 9 testes novos falharam (AttributeError em `product_info`/`parse_tiers`/`_read_product`, notas em falta); os 9 que passaram cobrem o que a tarefa 1 já fazia.
- GREEN `9881aa5`: 18 de 18 passam. REFACTOR não foi preciso.

## Verificação ao vivo

- Precondição: `https://www.obramat.pt/` respondeu (curl simples: 403).
- Depois da tarefa 1: `placa osb 1 un` deu "Obramat: ok" com 6 placas (o plano esperava "bloqueada — HTTP 403"; o critério aceita os dois).
- Depois da tarefa 2 (1 pesquisa + 3 páginas de produto, 14 s ao todo): "Obramat: ok" com a nota NO_STORE, porque a sessão `curl_cffi` não tem o armazém 201. Nenhuma oferta ganhou escalões sem o armazém.

## Deviations from Plan

None - plan executed exactly as written.

Nota: o `curl_cffi` com `impersonate="chrome"` passou hoje o DataDome nas duas corridas. Não muda o código; o plano 02-02 continua a precisar do browser para o armazém 201 (escalões e stock).

## Issues Encountered

None.

## Known Stubs

None.

## Next Phase Readiness

Pronto para o 02-02 (BrowserFetcher no Chrome dedicado). O adaptador já devolve NO_STORE quando falta o armazém, que é o caso do pedido simples.

## Self-Check: PASSED

- 7 ficheiros criados existem; `cmp` das 5 fixtures com as amostras sem diferenças.
- Commits `be6abb0`, `b47fc70`, `9881aa5` estão no HEAD.
- `uv run pytest -q`: 240 passed.
