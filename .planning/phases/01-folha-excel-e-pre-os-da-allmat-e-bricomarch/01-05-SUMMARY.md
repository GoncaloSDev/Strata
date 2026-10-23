---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 05
subsystem: search
tags: [python, decimal, beevo, curl_cffi, pytest, obras360]

requires:
  - phase: 01-04
    provides: "padrão de adaptador (NAME, search, MAX_PAGES, K, notas de limite, gather com return_exceptions), search.STORES"
  - phase: 01-02
    provides: "Fetcher.cache por execução, limite www.obras360.pt (3 pedidos, 0,3 s), FakeFetcher com rotas e cache"
provides:
  - "strata.stores.obras360: NAME, BASE, PER_PAGE, MAX_PAGES, K, DETAILS_PATH, UNIT_MAP, widget_id, parse_list, offers_from_details, search"
  - "strata.money.add_vat"
  - "search.STORES = (allmat, bricomarche, obras360) pela ordem D-01"
  - "Chave de cache por execução: fetch.cache['obras360_widget']"
affects: [01-06, phase-3, phase-4]

actuals:
  tokens: 37118    # chars/4 sobre o diff inteiro; 5069 sem as três amostras JSON copiadas
  tasks: 2
  commits: 4
plan_head_before: d68da5e343bc7c73e4e7e906a5f82e6ce78c6846
plan_head_after: b5cae043fa2253460bb6e9ac4da70839f2e6fd7e

tech-stack:
  added: []
  patterns:
    - "Loja com IVA à parte: preço = sem IVA × (1 + taxa da loja) em Decimal, confirmado contra o preço com IVA que a loja publica (±0,01 €)"
    - "Lista de pais só escolhe quem expandir; todos os preços mostrados vêm do detalhe por variante"
    - "Falha de um produto vai para a nota com a contagem e o 1.º motivo; todos a falhar sobe o 1.º StoreError; bloqueio/tempo sobem sempre"

key-files:
  created:
    - src/strata/stores/obras360.py
    - tests/test_obras360.py
    - tests/fixtures/obras360_product-list_osb.json
    - tests/fixtures/obras360_product-list_no-results.json
    - tests/fixtures/obras360_product-details_osb-parent.json
    - tests/fixtures/obras360_pesquisa-widget.html
  modified:
    - src/strata/money.py
    - src/strata/search.py
    - tests/test_money.py

key-decisions:
  - "Obras 360: lista paginada pelo número de páginas de total_products (ceil(total/48), no máximo 3), não pela contagem de produtos lidos"
  - "Obras 360: variante sem designação legível fica com o título '<pai> — ref. <sku>'; nunca sem título"
  - "Obras 360: só StoreError de um produto vai para a nota; KeyError/TypeError (layout novo) põem a loja inteira em erro"

patterns-established:
  - "Taxa de IVA mostrada com fmt_qty (23, 6), igual na evidência e na nota"

requirements-completed: [STORE-03, PRICE-01, PRICE-02, RES-02]

coverage:
  - id: D1
    description: "Cada variante do produto Obras 360 é uma oferta separada (7 espessuras de OSB), nenhum preço sai da linha-pai"
    requirement: STORE-03
    verification:
      - kind: unit
        ref: "tests/test_obras360.py#test_offers_from_details_uma_oferta_por_variante, test_search_placa_osb_le_o_widget_uma_vez"
        status: pass
    human_judgment: false
  - id: D2
    description: "Preço sem IVA convertido com o tax_percentage da loja, confirmado a ±0,01 €; 'IVA incoerente' dá erro; taxa ≠ 23 fica com nota e sem recálculo"
    requirement: PRICE-01
    verification:
      - kind: unit
        ref: "tests/test_money.py#test_add_vat_sem_arredondar; tests/test_obras360.py#test_variante_9mm_preco_com_iva_da_loja_unidade_e_stock, test_iva_incoerente_e_erro, test_iva_diferente_de_23_nao_e_convertido"
        status: pass
    human_judgment: false
  - id: D3
    description: "Preço por unidade da loja (3,125 m² a 15,02 € -> 4,81 €/m²), unidade desconhecida com nota, escalões '−2,5% a partir de N'"
    requirement: PRICE-02
    verification:
      - kind: unit
        ref: "tests/test_obras360.py#test_variante_9mm_preco_com_iva_da_loja_unidade_e_stock, test_escaloes_por_variante, test_unidade_da_loja_sem_conversao_fica_desconhecida, test_desconto_por_quantidade_noutro_formato_vai_para_a_nota"
        status: pass
    human_judgment: false
  - id: D4
    description: "Stock por variante ('1843 em stock' ou 'esgotado (Previsão em Armazém Lisboa: 6 dias úteis)')"
    requirement: RES-02
    verification:
      - kind: unit
        ref: "tests/test_obras360.py#test_variante_9mm_preco_com_iva_da_loja_unidade_e_stock, test_variante_esgotada_mostra_a_previsao_sem_html"
        status: pass
    human_judgment: false
  - id: D5
    description: "Pesquisa: widget uma vez por execução, paginação por total_products (3 páginas no máximo), top 20 pelo preço do artigo, notas de produtos sem detalhe e não expandidos"
    requirement: STORE-03
    verification:
      - kind: unit
        ref: "tests/test_obras360.py#test_widget_em_cache_nao_pede_a_pagina, test_produto_sem_detalhe_vai_para_a_nota, test_todos_os_detalhes_falham_e_erro, test_bloqueio_num_detalhe_sobe, test_paginas_por_total_e_so_20_detalhes_dos_mais_baratos, test_sem_resultados"
        status: pass
    human_judgment: false
  - id: D6
    description: "Obras 360 registada a seguir à Bricomarché; ponta a ponta folha -> terminal e corrida ao vivo"
    requirement: STORE-03
    verification:
      - kind: e2e
        ref: "tests/test_obras360.py#test_ponta_a_ponta_tres_lojas, test_stores_tem_obras360_a_seguir_a_bricomarche"
        status: pass
      - kind: e2e
        ref: "printf 'placa osb 3 un\\n\\n' | uv run python -m strata pesquisar (ao vivo, 2026-10-23): 'Obras 360: ok', 9/12/15/18/22 MM, 15,02 € a 35,87 €, 6,6 s"
        status: pass
    human_judgment: true
    rationale: "Confirmar no browser que o preço com IVA da variante de 12 mm na página da Obras 360 é 19,37 €"

duration: 5min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 05: Obras 360 Summary

**Obras 360 ligada à pesquisa a seguir à Bricomarché: ID do widget lido uma vez por execução, lista paginada por `total_products`, os 20 pais mais baratos expandidos no `product-details/27`, e uma oferta por variante com o preço sem IVA × taxa da loja confirmado pela própria loja (9 mm a 15,02 €, 4,81 €/m², 1843 em stock, −2,5% a partir de 108)**

## Performance

- **Duration:** 5 min
- **Started:** 2026-10-23T00:21:39Z
- **Completed:** 2026-10-23T00:26:48Z
- **Tasks:** 2 (ambas TDD: RED e GREEN em commits separados)
- **Files modified:** 9 (6 criados, 3 alterados)

## Accomplishments

- Cada variante é uma oferta. A placa OSB "9-30MM" (que a lista mostra a 15,02 €) passa a 7 linhas: 9, 12, 15, 18, 22, 25 e 30 mm, cada uma com o seu preço. O preço da lista só escolhe que pais expandir (T-01-24).
- O IVA vem da loja: `add_vat(sem IVA, tax_percentage)` em Decimal e comparado com o preço com IVA publicado. Mais de 0,01 € de diferença dá "IVA incoerente na variante <sku>" (T-01-23). Uma taxa de 6% fica com "IVA da loja 6%: não convertido para 23%".
- A oferta mostra o €/m² da loja (`conversion_factor` 3,125), o stock da variante ou "esgotado (Previsão em Armazém Lisboa: 6 dias úteis)" sem HTML (T-01-27), e os escalões "−2,5% a partir de N".
- Volume (T-01-26): no máximo 3 páginas de 48 e 20 detalhes por pesquisa, widget uma vez por execução. Ao vivo, "placa osb 3 un" nas três lojas demorou 6,6 s.
- Falhas visíveis: widget ausente ou `success: false` dão StoreError (T-01-25); produto sem detalhe fica em "N produtos sem detalhe: <motivo>"; todos a falhar põem a loja em "erro".

## Task Commits

1. **Tarefa 1: Uma oferta por variante, com IVA da loja, escalões e stock (parsers)**: RED `0b15968` (test), GREEN `23d552b` (feat)
2. **Tarefa 2: Obras 360 na pesquisa (widget, lista, top 20, detalhes e registo em STORES)**: RED `f4d6fe7` (test), GREEN `b5cae04` (feat)

Sem commits de REFACTOR: não houve limpeza a fazer.

## Files Created/Modified

- `src/strata/stores/obras360.py`: adaptador (`widget_id`, `parse_list`, `offers_from_details`, `search`, `UNIT_MAP`, `K = 20` e `DETAILS_PATH` com `shortcut:`).
- `src/strata/money.py`: `add_vat(net, rate)`.
- `src/strata/search.py`: `STORES = (allmat, bricomarche, obras360)`.
- `tests/test_obras360.py`: 23 testes (14 de parsers, 9 de pesquisa e ponta a ponta).
- `tests/test_money.py`: teste de `add_vat`.
- `tests/fixtures/obras360_*.json`: cópias das amostras da fase; `obras360_pesquisa-widget.html`: excerto de 6 linhas com o bloco JSON do widget.

## TDD

- **Tarefa 1, RED (`0b15968`):** 15 de 15 testes novos falharam com os stubs (None, lista vazia): asserções, "DID NOT RAISE", StopIteration ao procurar a variante de 9 mm numa lista vazia e TypeError ao desempacotar o None de `parse_list`. Todas as falhas vêm do comportamento em falta, nenhuma de importação. Avaliação: RED válido.
- **Tarefa 2, RED (`f4d6fe7`):** 7 de 9 testes novos falharam em asserções (0 ofertas, "DID NOT RAISE", nenhuma página pedida, STORES sem a Obras 360). `test_widget_em_cache_nao_pede_a_pagina` e `test_sem_resultados` passaram com o stub, porque o stub não faz pedidos; são guardas para a implementação, não o alvo do RED.
- GREEN: `23d552b` 29/29 (obras360 + money), `b5cae04` 23/23. A suite inteira passou de 102 para 126 testes.
- O classificador `check tdd-red-evidence` não foi corrido: o pytest não produz nenhum dos formatos que ele aceita e `workflow.tdd_mode` está desligado. A avaliação acima foi feita a ler a saída.

## Decisions Made

- A lista é paginada pelo número de páginas de `total_products` (ceil(total/48), no máximo 3). A amostra tem `total_products` 13 com só 2 produtos (cortada), e contar produtos lidos pedia uma página 2 que não existe.
- Variante sem designação legível: título "<pai> — ref. <sku>".
- Só um StoreError de um produto (detalhe vazio, IVA incoerente, HTTP 4xx) vai para a nota. Outros erros de leitura (KeyError, TypeError) são layout novo e põem a loja inteira em erro, com o motivo.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] RED sem erro de importação**
- **Found during:** Tarefa 1 e Tarefa 2 (RED)
- **Issue:** sem `stores/obras360.py`, `money.add_vat` e `obras360.search`, o pytest falhava na recolha ou com AttributeError (RED inválido).
- **Fix:** stubs no commit de teste, substituídos no GREEN (o mesmo padrão do 01-02 ao 01-04).
- **Files modified:** src/strata/stores/obras360.py, src/strata/money.py
- **Verification:** as falhas do RED são do comportamento em falta.
- **Committed in:** 0b15968, f4d6fe7

**2. [Rule 1 - Bug] Paginação pela contagem de produtos lidos**
- **Found during:** Tarefa 2 (GREEN)
- **Issue:** a primeira versão continuava a paginar enquanto os produtos lidos fossem menos que `total_products`; com a amostra real (13 no total, 2 na resposta) pedia páginas que não existem.
- **Fix:** número de páginas = ceil(total/48), no máximo 3; pára também numa página vazia.
- **Files modified:** src/strata/stores/obras360.py
- **Verification:** `test_search_placa_osb_le_o_widget_uma_vez` (1 página) e `test_paginas_por_total_e_so_20_detalhes_dos_mais_baratos` (120 -> páginas 1, 2, 3).
- **Committed in:** b5cae04

**3. [Rule 2 - Missing Critical] Nota quando o limite de páginas corta**
- **Found during:** Tarefa 2
- **Issue:** o plano manda "nota se ficar produto por ler" sem texto; sem ela, um corte seria silencioso.
- **Fix:** "mais produtos na loja não lidos (limite de 144)", o mesmo texto da Bricomarché.
- **Files modified:** src/strata/stores/obras360.py
- **Committed in:** b5cae04

---

**Total deviations:** 3 auto-fixed (1 bloqueio, 1 bug, 1 correção em falta)
**Impact on plan:** nenhum âmbito novo.

## Issues Encountered

- A pré-condição da tarefa 2 (`https://www.obras360.pt/pesquisa?search=osb` responde 200) foi confirmada antes da corrida ao vivo: 200, 698 KB, com o bloco do widget.
- Ao vivo, "placa osb" devolveu 7 produtos e 6 ficaram escondidos pelo filtro de título (D-15). Os títulos reais desses 6 não foram lidos. Se forem placas OSB com outra grafia, é trabalho de correspondência da Phase 3.
- O aviso `CurlCffiWarning` em `tests/test_tracer.py::test_rede_bloqueada` já existia antes. Fica fora do âmbito.

## Known Stubs

Nenhum. Os stubs dos commits RED foram todos substituídos no GREEN.

## Verification

- `uv run pytest tests/test_obras360.py tests/test_money.py -q`: 38 passed (critério da tarefa 1: pelo menos 20). PASS
- `uv run pytest tests/test_obras360.py -q`: 23 passed (critério da tarefa 2: pelo menos 15). PASS
- `uv run pytest -q`: 126 passed. PASS
- Greps: `prices_with_convertion_factor`, `DiscountByQuantity`, `IVA incoerente`, `https://www.obras360.pt`, `fetch.cache`, `product-details/27`, `items_per_page`, `K = 20` e `add_vat(` em obras360.py; `obra360.pt` ausente; `def add_vat` em money.py; `STORES = (allmat, bricomarche, obras360)` em search.py. PASS
- Ao vivo: `printf 'placa osb 3 un\n\n' | uv run python -m strata pesquisar` -> código 0, ordem "Allmat: sem resultados", "Bricomarché: ok", "Obras 360: ok"; 5 variantes com "MM" no título (15,02 € a 35,87 €), "IVA: indicado pela loja (tax_percentage=23)", €/m², stock e escalões; "+2 ofertas não mostradas". PASS

## Human-check pendente (end-of-phase)

1. Abrir https://www.obras360.pt/0170280004-placa-osb-9-22mm-resistente-a-humidade-lsf-construcao-estrutural-tapume-decoracao-revestimento no browser.
2. Confirmar que a variante "1 Placa 12 MM" mostra 19,37 € com IVA (ou 15,75 € sem IVA).

## User Setup Required

Nenhum: não há serviços externos nem chaves.

## Next Phase Readiness

- Pronto para o 01-06. O `verificar` deve pedir o `product-details/27` (A4) e o regex do widget, para apanhar uma mudança da loja.
- O `unity` dos escalões é tratado como contagem de artigos (A6); aplicá-lo ao custo é da Phase 4.

## Self-Check: PASSED

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*
