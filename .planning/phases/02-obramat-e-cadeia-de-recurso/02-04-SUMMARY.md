---
phase: 02-obramat-e-cadeia-de-recurso
plan: 04
subsystem: search
tags: [json-ld, cadeia-de-recurso, allmat, obramat, store-06]

requires:
  - phase: 02-03
    provides: "Cadeia API → browser com CAPTCHA 'abrir à mão', search_page nas 4 lojas, cache['captcha_hosts'] no Fetcher"
provides:
  - "strata.jsonld: MAX_PAGES, JS_PAGE, products(page), offer_of(node), rung(store)"
  - "strata.stores.allmat: PRODUCT_LINK, product_links(page)"
  - "strata.stores.obramat: PRODUCT_LINK, product_links(page), JSONLD_VAT_EVIDENCE"
  - "strata.search._rungs: degrau 'JSON-LD' entre 'API' e 'browser'"
  - "search_store: motivos de StoreError sem o nome da classe ('API: HTTP 500')"
affects: [02-05, 02-06]

tech-stack:
  added: []
  patterns:
    - "Um degrau genérico construído a partir do módulo da loja: rung(store) devolve uma função com a assinatura dos adaptadores"
    - "A loja entra no degrau JSON-LD só se definir product_links; quem não o define falha sem pedidos (D-19)"
    - "Links sem nenhum Product com preço são falha do degrau (escala), nunca 'sem resultados'"

key-files:
  created:
    - src/strata/jsonld.py
    - tests/test_jsonld.py
    - tests/fixtures/allmat_search-page_cimento.html
    - tests/fixtures/allmat_product-page_liz-branco_jsonld.html
  modified:
    - src/strata/search.py
    - src/strata/stores/allmat.py
    - src/strata/stores/obramat.py
    - tests/test_chain.py
    - tests/test_search.py

key-decisions:
  - "search_store mostra os StoreError como 'degrau: mensagem', sem 'StoreError:', para a nota dizer 'JSON-LD: página montada com JavaScript, sem links de produto'"
  - "Páginas de produto lidas sem nenhum Product com preço levantam StoreError: um layout mudado não pode virar 'sem resultados' (D-14)"
  - "As ofertas JSON-LD da Obramat levam JSONLD_VAT_EVIDENCE ('price do ld+json = unitprice_ati, com IVA'), porque o degrau não confere com o unitprice_tf"
  - "Os links da Obramat passam por regex no URL absoluto (só www.obramat.pt/produtos/<slug>.html), além do seletor da lista principal"

requirements-completed: [STORE-06]

coverage:
  - id: D1
    description: "Leitor JSON-LD: Product no topo, em listas e em @graph; JSON inválido ignorado; só EUR; preço em offers.price ou priceSpecification (dict ou lista); preço 0, negativo, NaN, texto ou null fica None"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_jsonld.py (test_products_*, test_offer_of_*, test_moeda_*, test_preco_*, test_json_invalido_*)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Degrau da Allmat: 1 + 5 pedidos, oferta a 4,72 € com 'regra da loja' e evidência '(JSON-LD)', nota '+7 produtos não lidos (limite de 5 páginas)'; título que não bate fica escondido; páginas sem Product e pesquisa sem links escalam"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_jsonld.py#test_degrau_da_allmat, test_titulo_que_nao_bate_fica_escondido, test_paginas_sem_product_com_preco_escalam, test_pagina_de_pesquisa_sem_links_escala"
        status: pass
      - kind: other
        ref: "uv run python -m strata pesquisar --sem-principal allmat ('cimento cola 1 saco'), ao vivo: Allmat ok, 5 ofertas 'método: JSON-LD', nota 'antes do JSON-LD: API: desativado com --sem-principal'"
        status: pass
    human_judgment: false
  - id: D3
    description: "Obramat: links só da lista principal (7 na pesquisa osb, 0 na página sem resultados apesar do carrossel, endcap fora); degrau com LOCATION e evidência do IVA"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_jsonld.py#test_links_de_produto_da_obramat_so_da_lista_principal, test_products_da_pagina_osb_da_obramat, test_degrau_da_obramat"
        status: pass
      - kind: other
        ref: "uv run python -m strata pesquisar --sem-principal obramat ('placa osb 1 un'), ao vivo: o pedido simples passou hoje e a Obramat saiu pelo JSON-LD (5 ofertas, 'antes do JSON-LD: API: desativado com --sem-principal')"
        status: pass
    human_judgment: false
  - id: D4
    description: "Ordem API → JSON-LD → browser nos motivos; Obramat com 403 no API e no JSON-LD vai ao browser com os dois motivos; Bricomarché e Obras 360 falham o JSON-LD sem pedidos"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_chain.py#test_ordem_api_json_ld_browser, test_obramat_bloqueada_no_api_e_no_json_ld_vai_ao_browser, test_bricomarche_sem_principal_salta_o_json_ld_sem_pedidos, test_allmat_sem_principal_responde_pelo_json_ld, test_sem_principal_na_linha_de_comandos"
        status: pass
      - kind: unit
        ref: "tests/test_jsonld.py#test_loja_montada_com_javascript_falha_sem_pedidos[bricomarche|obras360]"
        status: pass
    human_judgment: false

actuals:
  tokens: 6100  # chars/4 do diff de src/ e tests/ sem fixtures (24 351 caracteres)
  tasks: 2
  commits: 3
plan_head_before: 6f34c2c24d9e2b0dc31ff13fcbbc605f8d3e34ec
plan_head_after: 20a565d3f42b45c5b703986be02f8cb9bb449abf

duration: 9min
completed: 2026-10-31
status: complete
---

# Phase 2 Plan 04: Degrau JSON-LD entre o principal e o browser Summary

**A cadeia passa a ser API → JSON-LD → browser nas 4 lojas. A Allmat e a Obramat leem o Product/Offer do ld+json de até 5 páginas de produto tiradas da página de pesquisa. A Bricomarché e a Obras 360 falham logo, sem pedidos, com "página montada com JavaScript, sem links de produto".**

## Performance

- Duração: 9 min (13:09 a 13:18 UTC, 2026-10-31)
- Tarefas: 2 de 2
- Ficheiros: 4 criados, 5 alterados

## Accomplishments

- `strata.jsonld`: leitor de `script[type="application/ld+json"]` com `parse_float=Decimal`. Aceita o preço em `offers.price` ou em `priceSpecification` e só em EUR, como Decimal finito e maior que 0.
- `rung(store)`: página de pesquisa, depois `store.product_links`, depois até 5 páginas de produto em paralelo, ao ritmo do Fetcher. Cada oferta passa pelo filtro de título D-15. Quando há mais links fica a nota "+N produtos não lidos".
- Allmat: `product_links` por regex no HTML da pesquisa `/?s=…&post_type=product` (12 links na fixture "cimento").
- Obramat: `product_links` só de `ol#guidance-product-list > li[data-reflm]`. Ficam de fora o carrossel "vistos recentemente" e o bloco promocional (endcap).
- Ao vivo, `--sem-principal allmat` deu a Allmat "ok" com 5 ofertas "método: JSON-LD". O LIZ branco saiu a 4,72 €, o mesmo preço da Store API.
- Ao vivo, `--sem-principal obramat`: hoje o pedido simples passou o DataDome, por isso a Obramat respondeu pelo JSON-LD (5 placas OSB, a de 18 mm a 28,50 €, o mesmo `unitprice_ati` da API). A nota diz "antes do JSON-LD: API: desativado com --sem-principal". Os testes cobrem o caso do 403 ("antes do browser: API: HTTP 403 (verificação DataDome); JSON-LD: HTTP 403 (verificação DataDome)").

## Task Commits

1. **Tarefa 1: degrau JSON-LD de ponta a ponta na Allmat** - `f765e56` (feat). Tracer verificado de ponta a ponta antes da tarefa 2.
2. **Tarefa 2: Obramat pela lista principal e falha rápida nas lojas com JavaScript**
   - `d197fda` (test, RED)
   - `20a565d` (feat, GREEN)

## Files Created/Modified

- `src/strata/jsonld.py`: `products`, `offer_of`, `rung`, `MAX_PAGES`, `JS_PAGE`
- `src/strata/search.py`: degrau "JSON-LD" em `_rungs`; `except StoreError` com a mensagem sem a classe
- `src/strata/stores/allmat.py`: `PRODUCT_LINK`, `product_links`
- `src/strata/stores/obramat.py`: `PRODUCT_LINK`, `product_links`, `JSONLD_VAT_EVIDENCE`
- `tests/test_jsonld.py`: 21 testes do leitor e do degrau
- `tests/test_chain.py`, `tests/test_search.py`: motivos com o degrau novo e 5 testes de cadeia novos
- `tests/fixtures/allmat_search-page_cimento.html`, `tests/fixtures/allmat_product-page_liz-branco_jsonld.html`: gravadas ao vivo com o Fetcher da app (`record`, só o corpo, sem `Set-Cookie`)

## Decisions Made

Ver `key-decisions` no topo.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Motivo do degrau aparecia como "JSON-LD: StoreError: página montada…"**
- **Found during:** Tarefa 1
- **Issue:** `search_store` só apanhava os StoreError no `except Exception`, que junta o nome da classe. O plano pede a nota "JSON-LD: página montada com JavaScript, sem links de produto".
- **Fix:** `except StoreError` próprio, com `f"{stage}: {e}"`. Três asserções antigas passaram de "StoreError: x" para "x".
- **Files modified:** src/strata/search.py, tests/test_chain.py, tests/test_search.py
- **Commit:** f765e56

**2. [Rule 2 - Correção] Links sem nenhum Product com preço davam "sem resultados"**
- **Found during:** Tarefa 1
- **Issue:** com `raw = 0`, `search_store` dizia "sem resultados" e não escalava, mesmo quando as páginas falharam ou perderam o ld+json.
- **Fix:** o degrau levanta `StoreError("nenhum Product com preço nas N páginas de produto; K páginas falharam: …")` e a cadeia segue para o browser. Teste `test_paginas_sem_product_com_preco_escalam`.
- **Files modified:** src/strata/jsonld.py, tests/test_jsonld.py
- **Commit:** f765e56

**3. [Rule 1 - Bug] Evidência do IVA da Obramat dizia "conferido com unitprice_tf" nas ofertas JSON-LD**
- **Found during:** verificação ao vivo da tarefa 2
- **Issue:** `vat_evidence = f"{store.VAT_EVIDENCE} (JSON-LD)"` reaproveitava um texto de uma conferência que o degrau não faz.
- **Fix:** `obramat.JSONLD_VAT_EVIDENCE = "price do ld+json = unitprice_ati, com IVA"`. O degrau usa-o quando existe e, se não, o `VAT_EVIDENCE` da loja (Allmat).
- **Files modified:** src/strata/stores/obramat.py, src/strata/jsonld.py, tests/test_jsonld.py
- **Commit:** 20a565d

**4. [Ajuste ao plano] Teste da linha de comandos `--sem-principal obramat` mudado na tarefa 2**
- O plano punha esta mudança na tarefa 1. Antes do `obramat.product_links` o JSON-LD da Obramat não faz pedidos, por isso "exatamente 1 pedido simples" só passa a valer na tarefa 2. Entrou no commit RED da tarefa 2.

## Issues Encountered

- O `test_degrau_da_obramat` contava com `o.url` igual ao URL da OSB 18 mm, mas o Product da Obramat não tem `url` no topo (só `offers.url`), por isso a oferta fica com o link da pesquisa. Corrigido o teste.

## Known Stubs

Nenhum.

## Notas para o verificador

- Conteúdo da embalagem nas ofertas JSON-LD vem só do título (assumido no plano). Na Obramat, títulos como "PLACA OSB 3 250X125X1,8CM" não dão conteúdo, por isso aparece "preço por unidade desconhecido" e essas ofertas vão para o fim da ordenação. O API da Obramat assume 1 un. Se o 02-05/02-06 precisar, o degrau pode usar o mesmo fallback `(1, "un")` da loja.
- O Chrome dedicado não estava aberto antes das corridas ao vivo e continua fechado (nenhuma corrida chegou ao browser).

## Next Phase Readiness

- O 02-05 (degrau IA) entra depois do "JSON-LD" em `_rungs`. O formato dos motivos já está estável: "degrau: mensagem".

## Self-Check: PASSED

- FOUND: src/strata/jsonld.py, tests/test_jsonld.py, as 2 fixtures novas
- FOUND: f765e56, d197fda, 20a565d (antepassados de HEAD)
- `uv run pytest -q`: 298 passed
