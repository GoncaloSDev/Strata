---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 04
subsystem: search
tags: [python, decimal, woocommerce-store-api, curl_cffi, pytest, bricomarche]

requires:
  - phase: 01-02
    provides: "tests/conftest.py (FakeFetcher, fixture fake, rede bloqueada)"
  - phase: 01-03
    provides: "words.title_matches, money.content_from_title, search_store com pesquisa alargada e ordenação pela unidade pedida"
provides:
  - "strata.stores.bricomarche: NAME, BASE, SEARCH_URL, PER_PAGE, MAX_PAGES, K, parent_key, cheapest, has_stock, store_link, offer_from, search"
  - "search.STORES = (allmat, bricomarche) pela ordem D-01"
  - "Fixtures reais tests/fixtures/bricomarche_products_search-osb.json e bricomarche_variations_parent-47412.json"
affects: [01-05, 01-06, phase-2, phase-3]

actuals:
  tokens: 36500
  tasks: 2
  commits: 4
plan_head_before: c33c3925c3cb5f57cc87d003e20fe5d9abb96e3b
plan_head_after: c82a5253bb13a82f657078985a140b227922c925

tech-stack:
  added: []
  patterns:
    - "Loja com preço por loja física: pais -> top K pelo preço do pai -> variações por pai; o número mostrado vem sempre de uma variação"
    - "Variações pedidas com type=variation&parent=<id>, um pedido por pai, em paralelo com gather(return_exceptions=True) e a 1.ª falha relançada no fim (como as páginas da Allmat)"
    - "Paginação até página curta com limite de 3 páginas e nota visível quando o limite corta"

key-files:
  created:
    - src/strata/stores/bricomarche.py
    - tests/test_bricomarche.py
    - tests/fixtures/bricomarche_products_search-osb.json
    - tests/fixtures/bricomarche_variations_parent-47412.json
  modified:
    - src/strata/search.py

key-decisions:
  - "Bricomarché: oferta = variação mais barata entre lojas físicas com o stock dela, sem filtrar; se não tem stock, nota 'com stock: X em Y' com a mais barata que tem"
  - "Sem stock = classe out-of-stock ou texto 'N em stock' com N = 0 (a loja escreve '0 em stock' com a classe in-stock)"
  - "Variação 'master' fica fora da escolha (shortcut no código); pais expandidos sem variação válida contam em 'N produtos sem preço'"
  - "Variações também paginadas com o limite de 3 páginas (300 linhas por pai), com nota se o limite cortar"

patterns-established:
  - "Adaptador com várias lojas físicas preenche Offer.location; o report já mostra 'loja: <nome>'"

requirements-completed: [STORE-01, PRICE-01, RES-02]

coverage:
  - id: D1
    description: "Oferta da Bricomarché com o preço mais barato entre lojas físicas (variação > 0, nunca o preço do pai, master fora), o nome da loja e o link /{loja}/produto/{slug}/"
    requirement: STORE-01
    verification:
      - kind: unit
        ref: "tests/test_bricomarche.py#test_parent_key, test_cheapest_e_a_loja_fisica_mais_barata, test_cheapest_ignora_master_e_precos_a_zero, test_store_link, test_offer_from_amostra_47412, test_preco_do_pai_nunca_e_mostrado, test_pai_sem_variacoes_com_preco_nao_da_oferta"
        status: pass
    human_judgment: false
  - id: D2
    description: "Stock da loja escolhida tal como o site o escreve, sem filtrar; dica 'com stock: 19,99 € em Monção' quando a mais barata não tem"
    requirement: RES-02
    verification:
      - kind: unit
        ref: "tests/test_bricomarche.py#test_has_stock, test_offer_from_amostra_47412, test_offer_from_sem_dica_quando_a_mais_barata_tem_stock"
        status: pass
    human_judgment: false
  - id: D3
    description: "IVA: regra da loja com a evidência (loja B2C, DL 138/90; o site não mostra o IVA)"
    requirement: PRICE-01
    verification:
      - kind: unit
        ref: "tests/test_bricomarche.py#test_offer_from_amostra_47412"
        status: pass
    human_judgment: true
    rationale: "A9: que o preço da Bricomarché inclui IVA só se confirma num talão ou na loja; o site não o escreve"
  - id: D4
    description: "Pesquisa: pais com filtro de título, só os 10 mais baratos expandidos (resto na nota), variações por pai com type=variation&parent=<id>, nota 'N produtos sem preço'"
    requirement: STORE-01
    verification:
      - kind: unit
        ref: "tests/test_bricomarche.py#test_search_osb, test_variacoes_pedidas_por_pai, test_so_os_10_pais_mais_baratos_sao_expandidos, test_pais_sem_as_palavras_ficam_escondidos"
        status: pass
    human_judgment: false
  - id: D5
    description: "Bricomarché registada a seguir à Allmat; ponta a ponta folha -> terminal e corrida ao vivo"
    requirement: STORE-01
    verification:
      - kind: e2e
        ref: "tests/test_bricomarche.py#test_ponta_a_ponta_allmat_e_bricomarche, test_stores_tem_bricomarche_a_seguir_a_allmat"
        status: pass
      - kind: e2e
        ref: "printf 'placa osb 3 un\\n\\n' | uv run python -m strata pesquisar (ao vivo, 2026-10-23): 'Allmat: sem resultados', 'Bricomarché: ok', 14,49 € loja: Coina - Barreiro, 5,6 s"
        status: pass
    human_judgment: true
    rationale: "Human-check do plano: abrir o link no browser e ver que o preço desenhado por JavaScript é o da linha"

duration: 4min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 04: Bricomarché Summary

**Bricomarché ligada à pesquisa a seguir à Allmat: pais pela Store API, os 10 mais baratos expandidos com `type=variation&parent=<id>`, oferta com o preço da loja física mais barata (14,49 € em Coina - Barreiro), o stock dessa loja, a dica "com stock: 15,49 € em Ponte de Sor" e o link `/{loja}/produto/{slug}/`**

## Performance

- **Duration:** 4 min
- **Started:** 2026-10-23T00:15:31Z
- **Completed:** 2026-10-23T00:19:30Z
- **Tasks:** 2 (ambas TDD: RED e GREEN em commits separados)
- **Files modified:** 5 (4 criados, 1 alterado)

## Accomplishments

- `offer_from` mostra sempre o preço de uma variação por loja física com preço acima de zero. O preço do pai só serve para escolher que pais expandir (T-01-19). A variação "master" nunca é escolhida.
- O link aponta para `https://www.bricomarche.pt/{loja}/produto/{slug}/`. Ao vivo, o link de Coina dá 200 e vai parar à página do produto nessa loja, não a `/escolher-loja/` (T-01-20). O HTML traz `14.49`.
- O stock aparece tal como vem ("0 em stock", "Esgotado"). Quando a mais barata não tem stock, a oferta diz onde há stock e a que preço.
- `search` faz no máximo 3 páginas de pais e expande 10 pais. As variações vão ao ritmo do host (2 pedidos, 0,5 s). A corrida "placa osb 3 un" demorou 5,6 s ao todo (T-01-21).
- A pesquisa alargada, a ordenação e os estados de falha vêm do `search_store` sem mudanças: "OSB 12mm" -> "Bricomarché: ok (pesquisa alargada: 'OSB')" no teste ponta a ponta.

## Task Commits

1. **Tarefa 1: Mais barata entre lojas físicas, com loja, link e stock (parsers)**: RED `9b2053c` (test), GREEN `109922e` (feat)
2. **Tarefa 2: Bricomarché na pesquisa (pais, top 10, variações e registo em STORES)**: RED `5b0e09c` (test), GREEN `c82a525` (feat)

Sem commits de REFACTOR: não houve limpeza a fazer.

## Files Created/Modified

- `src/strata/stores/bricomarche.py`: adaptador completo (`parent_key`, `cheapest`, `has_stock`, `store_link`, `offer_from`, `search`, `K = 10` e `shortcut:` no K e no master).
- `src/strata/search.py`: `STORES = (allmat, bricomarche)`.
- `tests/test_bricomarche.py`: 15 testes (9 de parsers, 6 de pesquisa e ponta a ponta).
- `tests/fixtures/bricomarche_products_search-osb.json`, `tests/fixtures/bricomarche_variations_parent-47412.json`: cópias das amostras da fase.

## TDD

- **Tarefa 1, RED (`9b2053c`):** 8 de 9 falharam em asserções. Os stubs devolvem None, "" ou True; nos testes de `offer_from` a falha aparece como `AttributeError` sobre o None. Passou só `test_pai_sem_variacoes_com_preco_nao_da_oferta`, porque o stub já devolve None. Avaliação: RED válido.
- **Tarefa 2, RED (`5b0e09c`):** os 6 testes novos falharam em asserções (`0 == 4` pais, 0 pedidos de variações, `STORES` sem a Bricomarché). Os 9 da tarefa 1 continuaram a passar. Avaliação: RED válido.
- GREEN: `109922e` 9/9, `c82a525` 15/15. A suite inteira passou de 87 para 102 testes.
- O classificador `check tdd-red-evidence` não foi corrido: o pytest não produz nenhum dos formatos que ele aceita e `workflow.tdd_mode` está desligado. A avaliação acima foi feita a ler a saída.

## Decisions Made

- A oferta é a variação mais barata entre lojas físicas, com o stock dela. Não se filtra por stock (RES-02). A dica "com stock" usa a mais barata das que têm stock.
- Uma variação está sem stock quando a classe é `out-of-stock` ou quando o texto é "N em stock" com N = 0. A amostra traz "0 em stock" com a classe `in-stock`.
- As variações usam a mesma paginação dos pais: até uma página curta, no máximo 3 páginas. Se o limite cortar, sai uma nota.
- Uma falha num pedido de variações faz a loja inteira passar a erro, bloqueada ou tempo esgotado (o mesmo padrão das páginas da Allmat). Nunca sai uma oferta parcial em silêncio.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] RED sem erro de importação**
- **Found during:** Tarefa 1 (RED)
- **Issue:** sem `stores/bricomarche.py`, o pytest falhava na recolha (RED inválido).
- **Fix:** módulo com assinaturas vazias no commit de teste, substituídas no GREEN (o mesmo padrão do 01-02 e do 01-03).
- **Files modified:** src/strata/stores/bricomarche.py
- **Verification:** todas as falhas do RED são asserções.
- **Committed in:** 9b2053c

**2. [Rule 2 - Missing Critical] Limite de páginas também nas variações**
- **Found during:** Tarefa 2
- **Issue:** o plano manda paginar as variações até uma página curta, mas não põe teto. Uma API que devolvesse sempre 100 linhas faria pedidos sem fim à loja (T-01-21).
- **Fix:** `_pages` partilhado por pais e variações, com `MAX_PAGES = 3` e nota visível quando o limite corta.
- **Files modified:** src/strata/stores/bricomarche.py
- **Verification:** suite verde; 65 variações por pai cabem numa página.
- **Committed in:** c82a525

---

**Total deviations:** 2 auto-fixed (1 bloqueio, 1 correção em falta)
**Impact on plan:** nenhum âmbito novo.

## Issues Encountered

- Nenhum. A pré-condição da tarefa 2 (`search=osb&per_page=1` na Bricomarché responde 200) foi confirmada antes da corrida ao vivo.
- O aviso `CurlCffiWarning` (Proactor event loop) em `tests/test_tracer.py::test_rede_bloqueada` já existia antes. Fica fora do âmbito.

## Known Stubs

Nenhum.

## Verification

- `uv run pytest tests/test_bricomarche.py -q`: 15 passed (critérios: pelo menos 8 na tarefa 1 e pelo menos 11 na tarefa 2). PASS
- `uv run pytest -q`: 102 passed. PASS
- Greps: `def cheapest`, `def store_link`, `"master"`, `shortcut:`, `"variation"`, `K = 10` e `title_matches(` em bricomarche.py; `orderby` ausente; `STORES = (allmat, bricomarche)` em search.py; "Coina - Barreiro", "com stock: 19,99 € em Monção" e "coina-barreiro/produto/plc-osb-lisa-2-50x1-25-12mm/" em test_bricomarche.py. PASS
- Ao vivo: `printf 'placa osb 3 un\n\n' | uv run python -m strata pesquisar` -> código 0, "Allmat: sem resultados", "Bricomarché: ok", 1.ª oferta 14,49 € com "loja: Coina - Barreiro" e link `https://www.bricomarche.pt/coina-barreiro/produto/placa-osb-lisa-2-50x1-25-9mm/`. PASS
- Link ao vivo: 200, URL final `/coina-barreiro/produto/madeiras/madeiras-e-derivados-a-corte/placa-osb-lisa-2-50x1-25-9mm/`, sem `escolher-loja`, `14.49` no HTML. PASS

## Human-check pendente (end-of-phase)

1. Abrir https://www.bricomarche.pt/coina-barreiro/produto/placa-osb-lisa-2-50x1-25-9mm/ no browser.
2. Confirmar que o preço mostrado é 14,49 € (o preço é desenhado por JavaScript).
3. A9: confirmar num talão ou na loja que o preço inclui IVA.

## User Setup Required

Nenhum: não há serviços externos nem chaves.

## Next Phase Readiness

- Pronto para o 01-05 (Obras 360). O padrão de loja com várias lojas físicas (`Offer.location`) e o de pedidos em paralelo com a falha relançada no fim já estão disponíveis.
- Se o `verificar` do 01-06 mostrar produtos baratos fora do top 10 (o preço do pai pode ser antigo), sobe-se `K`.

## Self-Check: PASSED

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*
