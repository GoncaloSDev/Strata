---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 03
subsystem: search
tags: [python, decimal, selectolax, lexbor, woocommerce-store-api, pytest]

requires:
  - phase: 01-01
    provides: "models, fetch (Fetcher e falhas classificadas), search_store, report.print_item, stores/allmat"
  - phase: 01-02
    provides: "tests/conftest.py (FakeFetcher, fixture fake, rede bloqueada) e fixtures da Allmat"
provides:
  - "strata.words: plain, words, title_matches, UNIT_TOKENS, broadened (D-14, D-15)"
  - "strata.money: content_from_title (kg, g, L, ml, m²) e in_unit (preço na unidade pedida, só Decimal)"
  - "search_store: uma pesquisa alargada quando a loja dá zero, ordenação estável pelo preço na unidade pedida com o motivo na nota"
  - "stores/allmat: filtro de título com contagem, conteúdo pelo título nos 'Unid', parse_box e leitura das páginas das caixas 'M2' (até 10)"
  - "Matriz de estados de loja testada (403, cf-mitigated, 500, página de desafio, JSON inválido, timeout, prazo)"
affects: [01-04, 01-05, 01-06, phase-3]

actuals:
  tokens: 25900
  tasks: 3
  commits: 6
plan_head_before: 1888b257befe19c4567165c59da885b40e47ac1d
plan_head_after: f4674d153afc9465a4ab0bb99bfd562896095eaa

tech-stack:
  added: []
  patterns:
    - "Filtro D-15 dentro do adaptador: raw = devolvidos pela loja, hidden = raw - mantidos; o report mostra '+N ofertas escondidas'"
    - "A pesquisa alargada e a ordenação ficam em search_store, comuns a todas as lojas; os adaptadores só devolvem Found"
    - "Notas acumulam-se com '; ' (nota da loja + motivo de não conversão)"
    - "Páginas de produto lidas em paralelo com gather(return_exceptions=True) e a 1.ª falha bloqueante relançada depois de todas acabarem"

key-files:
  created:
    - src/strata/words.py
    - tests/test_search.py
    - tests/test_money.py
    - tests/test_allmat.py
    - tests/fixtures/allmat_product-page_39233_box.html
  modified:
    - src/strata/search.py
    - src/strata/money.py
    - src/strata/stores/allmat.py

key-decisions:
  - "Pesquisa alargada que continua a zero: estado 'sem resultados' com detail \"também sem resultados com '<b>'\" e broadened_query vazio, para o cabeçalho não repetir a pesquisa duas vezes"
  - "Caixas M2 começam com a nota 'área da caixa não lida (limite de 10 páginas por pesquisa)'; a leitura da página troca-a pela nota certa, por isso as que ficam além do limite já saem com o motivo"
  - "Preço da página lido com vírgula decimal e sem pontos (formato da loja: decimal ',' e milhares ' '); se a loja mudar o formato, o bloco deixa de bater e a oferta fica com 'área da caixa não encontrada', nunca com um número errado"
  - "plain() (normalização com espaços) vive em words.py e é usada também por money.content_from_title"

patterns-established:
  - "Contrato de loja mantém-se: NAME + async search(query, fetch) -> Found; Bricomarché e Obras 360 ganham D-14 e D-03 de graça em search_store, mas têm de aplicar title_matches e preencher hidden"

requirements-completed: [LIST-02, STORE-02, PRICE-02, STORE-05]

coverage:
  - id: D1
    description: "Loja com zero resultados faz uma só pesquisa alargada sem números nem unidades; ofertas marcadas 'pesquisa alargada'; a zero dá 'sem resultados' com a pesquisa usada; sem alargada possível, um só pedido"
    requirement: LIST-02
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_broadened, test_pesquisa_alargada_quando_a_loja_da_zero, test_pesquisa_alargada_tambem_a_zero, test_sem_pesquisa_alargada_quando_nada_muda"
        status: pass
    human_judgment: false
  - id: D2
    description: "Ofertas cujo título não tem as palavras da pesquisa ficam escondidas e contadas ('+1 ofertas escondidas: título sem 'cimento''), comparando palavras e nunca substrings"
    requirement: LIST-02
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_title_matches, test_allmat_esconde_titulos_sem_as_palavras"
        status: pass
    human_judgment: false
  - id: D3
    description: "Ofertas do mais barato para o mais caro pelo preço na unidade pedida, ordenação estável, não convertíveis no fim com o motivo; €/kg, €/L, €/m² a partir do conteúdo da embalagem; money sem float"
    requirement: PRICE-02
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_money.py -q (14 testes)"
        status: pass
      - kind: unit
        ref: "tests/test_search.py#test_ordem_estavel_pelo_preco_na_unidade_pedida, test_allmat_cimento_saco_mais_barato_primeiro, test_allmat_conteudo_pelo_titulo"
        status: pass
    human_judgment: false
  - id: D4
    description: "Caixa M2 da Allmat com preço da caixa e €/m² pela área da página (13,74 € / 1,37 m² = 10,03 €/m²); bloco escolhido pelo preço da API; área derivada, incoerente, ausente, página a falhar e limite de 10 páginas com nota visível"
    requirement: STORE-02
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_allmat.py -q (8 testes)"
        status: pass
      - kind: e2e
        ref: "folha 'pavimento' / m2 / 30 -> uv run python -m strata pesquisar (ao vivo, 2026-10-23): 'Allmat: ok', 15,85 € · 12,99 €/m²"
        status: pass
    human_judgment: false
  - id: D5
    description: "Loja bloqueada (403, cf-mitigated, página de desafio), tempo esgotado (Timeout do curl_cffi e prazo) e erro com detalhe (500, resposta não JSON, ValueError) aparecem sempre, pela ordem de STORES"
    requirement: STORE-05
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_estados_da_loja_por_tipo_de_falha (6 casos), test_prazo_esgotado, test_tres_lojas_pela_ordem_de_stores"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 03: Resultados que servem Summary

**Pesquisa alargada única quando a loja dá zero ("OSB 12mm" -> "OSB"), filtro de título por palavras com contagem das escondidas, ofertas ordenadas pelo preço na unidade pedida (Decimal, estável, não convertíveis no fim com o motivo) e €/m² das caixas da Allmat lido na página do produto (13,74 € / 1,37 m² = 10,03 €/m²)**

## Performance

- **Duration:** 7 min
- **Started:** 2026-10-23T00:04:37Z
- **Completed:** 2026-10-23T00:11:44Z
- **Tasks:** 3 (todas TDD: RED e GREEN em commits separados)
- **Files modified:** 8 (5 criados, 3 alterados)

## Accomplishments

- `words.title_matches` compara palavras normalizadas ("12 mm" = "12mm", plural simples, sem acentos). "PAINEL AQUECIMENTO" não passa para "cimento". `broadened` tira números e unidades soltas e devolve None quando nada muda ou nada sobra.
- `search_store` faz no máximo uma pesquisa extra por loja e por item. As ofertas dessa pesquisa ficam com `broadened=True` e o cabeçalho mostra "(pesquisa alargada: 'OSB')". Depois ordena pelo preço na unidade da linha com `in_unit`.
- `money.content_from_title` lê kg, g, L, ml e m² do título ("600ML" -> 0,6 L). Os produtos "Unid" da Allmat passam a ter conteúdo: o saco LIZ fica com 25 kg, o que dá 0,1688 €/kg.
- `allmat.parse_box` procura só dentro de `#product-{id}` e escolhe o bloco cujo preço da caixa é igual ao da API (T-01-14). A coerência entre área e €/m² tem tolerância de 2%. As caixas além das 10 mais baratas saem com o motivo.
- Ao vivo, "pavimento" em m² dá 24 ofertas. As 7 caixas M2 foram todas lidas: 6 com área declarada e 1 com área derivada. As caixas aparecem primeiro, pelo €/m² (12,99 €/m²). Os 17 artigos à unidade ficam no fim com "não convertível para m²: vendido em un".

## Task Commits

1. **Tarefa 1: Pesquisa alargada (D-14), filtro de título (D-15) e estados de loja**: RED `8c2dc5b` (test), GREEN `5c08e6b` (feat)
2. **Tarefa 2: Mais barato primeiro na unidade pedida (D-03, PRICE-02)**: RED `bd254b9` (test), GREEN `b3fd8db` (feat)
3. **Tarefa 3: Caixas da Allmat com área lida na página (STORE-02)**: RED `9a8d5b4` (test), GREEN `f4674d1` (feat)

Sem commits de REFACTOR: não houve limpeza a fazer.

## Files Created/Modified

- `src/strata/words.py`: `plain`, `words`, `title_matches`, `UNIT_TOKENS`, `broadened`.
- `src/strata/money.py`: `content_from_title` e `in_unit`. Continua sem float.
- `src/strata/search.py`: pesquisa alargada D-14 e ordenação estável D-03 com o motivo na nota.
- `src/strata/stores/allmat.py`: filtro de título com `hidden`, conteúdo pelo título, `parse_box`, `_read_box`, `MAX_BOX_PAGES = 10` (com `shortcut:`), `INCOHERENT`. `parse_products` devolve agora também as caixas `(id, oferta)` e só é usada dentro do módulo.
- `tests/test_search.py` (26 testes), `tests/test_money.py` (14), `tests/test_allmat.py` (8).
- `tests/fixtures/allmat_product-page_39233_box.html`: cópia da amostra da fase.

## TDD

- **Tarefa 1, RED (`8c2dc5b`):** 7 de 23 falharam, todos em asserções: um caso de `title_matches`, três de `broadened`, as duas pesquisas alargadas e o `hidden` da Allmat (4 ofertas em vez de 3). `words.py` entrou no commit de teste com funções vazias (`title_matches` -> True, `broadened` -> None), que é o comportamento sem a funcionalidade. Os 16 que passaram são a matriz de estados e os casos que já batiam: o `fetch.py` do 01-01 já classificava as falhas, e estes testes registam esse comportamento. Avaliação: RED válido.
- **Tarefa 2, RED (`bd254b9`):** 13 de 40 falharam em asserções (`content_from_title` -> None, `in_unit` -> `(None, "")`, ordem `a b c d`, conteúdo 1 un em vez de 25 kg). Os testes de formatação e a ordem 4,22/4,72/6,60 do cimento já passavam, porque a fixture vem por essa ordem. Avaliação: RED válido.
- **Tarefa 3, RED (`9a8d5b4`):** 7 de 8 falharam em asserções (`parse_box` vazio, nota antiga "rótulo M2 da loja: área da caixa não lida", 0 páginas pedidas). O teste das amostras cimento/osb passou porque cobre comportamento do 01-01. Avaliação: RED válido.
- GREEN: `5c08e6b` 23/23, `b3fd8db` 40/40, `f4674d1` 8/8. A suite inteira passou de 39 para 87 testes.
- O classificador `check tdd-red-evidence` não foi corrido: o pytest não produz nenhum dos formatos que ele aceita, e `workflow.tdd_mode` está desligado. A avaliação acima foi feita a ler a saída.

## Decisions Made

- Quando a alargada também dá zero, o estado é "sem resultados" com o detalhe "também sem resultados com 'OSB'". `broadened_query` fica vazio para o cabeçalho não mostrar a pesquisa duas vezes.
- As caixas M2 começam com a nota do limite de páginas. Só a leitura da página a troca, por isso uma caixa não lida nunca aparece sem motivo.
- O preço lido na página usa o formato da loja (vírgula decimal, espaço nos milhares). Se o formato mudar, o bloco deixa de bater com a API e a oferta mostra "área da caixa não encontrada". Nunca aparece um €/m² errado.
- Se o bloco existir mas não tiver €/m², vale a área declarada. Sem nenhuma das duas, a nota é "não encontrada".

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] RED sem erro de importação**
- **Found during:** Tarefas 1, 2 e 3 (RED)
- **Issue:** sem `words.py`, `content_from_title`/`in_unit` e `parse_box`, o pytest falhava na recolha (RED inválido).
- **Fix:** assinaturas vazias nos commits de teste, substituídas no GREEN (o mesmo padrão do 01-02).
- **Files modified:** src/strata/words.py, src/strata/money.py, src/strata/stores/allmat.py
- **Verification:** todas as falhas do RED são asserções.
- **Committed in:** 8c2dc5b, bd254b9, 9a8d5b4

**2. [Rule 2 - Missing Critical] Sem tarefas órfãs quando uma página bloqueia**
- **Found during:** Tarefa 3
- **Issue:** com `gather` simples, um `StoreBlocked` numa página relançava logo, e as outras leituras ficavam a correr sem dono, com avisos "exception never retrieved".
- **Fix:** `gather(..., return_exceptions=True)` e relançar a primeira exceção depois de todas acabarem (no máximo 10 pedidos, com o ritmo do host).
- **Files modified:** src/strata/stores/allmat.py
- **Verification:** `test_pagina_do_produto_falha` e corrida ao vivo.
- **Committed in:** f4674d1

---

**Total deviations:** 2 auto-fixed (1 bloqueio, 1 correção em falta)
**Impact on plan:** nenhum âmbito novo.

## Issues Encountered

- Nenhum. A pré-condição da tarefa 3 (`search=pavimento&per_page=1` na Allmat responde 200) foi confirmada antes da corrida ao vivo.

## Known Stubs

Nenhum. O stub do 01-01 (rótulo M2 sem área) ficou resolvido e foi marcado `fixed` no `.planning/WINDOWS.md` (entrada 1).

## Verification

- `uv run pytest tests/test_search.py -q`: 26 passed (critério: pelo menos 14). PASS
- `uv run pytest tests/test_money.py tests/test_search.py -q`: 40 passed (critério: pelo menos 24). PASS
- `uv run pytest tests/test_allmat.py -q`: 8 passed (critério: pelo menos 8). PASS
- `uv run pytest -q`: 87 passed. PASS
- Greps: `def title_matches`/`def broadened` em words.py; `broadened(` e `também sem resultados com` em search.py; `title_matches(`, `LexborHTMLParser`, `allmat-loop-price-box`, `MAX_BOX_PAGES = 10` e `shortcut:` em allmat.py; `def content_from_title`/`def in_unit` em money.py; `in_unit(` em search.py; `float(` ausente de money.py; "PAINEL AQUECIMENTO", "bloqueada", "tempo esgotado" e "página de desafio" em test_search.py; `product-39233` na fixture. PASS
- Ao vivo: folha com "pavimento" / m2 / 30 -> código 0, "Allmat: ok", 5 ofertas com "€/m²" e "+19 ofertas não mostradas". PASS

## User Setup Required

Nenhum: não há serviços externos nem chaves.

## Next Phase Readiness

- Pronto para o 01-04 (Bricomarché). O adaptador novo só precisa de `title_matches` e `hidden` no seu `search`. A pesquisa alargada e a ordenação já vêm do `search_store`. Para conteúdo pelo título, usar `money.content_from_title`.
- O limite de 10 páginas da Allmat não foi atingido com "pavimento" (7 caixas). Se o `verificar` do 01-06 mostrar caixas baratas por ler, sobe-se `MAX_BOX_PAGES`.

## Self-Check: PASSED

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*
