---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 10
subsystem: stores
tags: [bricomarche, woocommerce, stock, gap-closure, pytest]

requires:
  - phase: 01-04
    provides: "bricomarche.offer_from, cheapest, has_stock, store_link sobre as variações por loja física"
  - phase: 01-09
    provides: "suite de 201 testes verde e corrida e2e das três lojas"
provides:
  - "offer_from: a loja física mais barata com stock; se nenhuma tiver, a mais barata com o stock dela"
  - "nota 'mais barata sem stock: X em Y' quando a mais barata absoluta fica de fora"
  - "3 testes de borda do stock (prefere stock, nenhuma com stock, empate)"
affects: [01-11, verify-work, report, search]

actuals:
  tokens: 2200
  tasks: 2
  commits: 3
plan_head_before: ebeafc2891e4cfbfe2efd3b5b95d9d87364b24c4
plan_head_after: 5f12ac47eb5ceb2015e278381a839e58c02c1763

tech-stack:
  added: []
  patterns:
    - "Escolha por stock dentro da loja: cheapest(com stock) or cheapest(todas); o preço escondido vai para a nota (RES-02)"

key-files:
  created: []
  modified:
    - src/strata/stores/bricomarche.py
    - tests/test_bricomarche.py
    - tests/test_e2e.py
    - .planning/STATE.md

key-decisions:
  - "G-01-3: a oferta da Bricomarché é a loja física mais barata com stock; se nenhuma tiver stock, a mais barata com o stock dela; uma loja mais barata sem stock fica na nota 'mais barata sem stock: X em Y' (substitui a decisão do 01-04)"

patterns-established:
  - "Nota de preço escondido: só aparece quando a alternativa é estritamente mais barata do que a oferta mostrada; num empate ganha a com stock e não há nota"

requirements-completed: [STORE-01, RES-02]

coverage:
  - id: D1
    description: "A oferta da Bricomarché é a loja física mais barata com stock (amostra 47412: 19,99 € em Monção, 118 em stock)"
    requirement: STORE-01
    verification:
      - kind: unit
        ref: "tests/test_bricomarche.py#test_offer_from_amostra_47412"
        status: pass
      - kind: unit
        ref: "tests/test_bricomarche.py#test_offer_from_prefere_a_loja_com_stock"
        status: pass
      - kind: unit
        ref: "tests/test_bricomarche.py#test_search_osb"
        status: pass
    human_judgment: false
  - id: D2
    description: "A mais barata sem stock nunca some: nota 'mais barata sem stock: X em Y'; sem stock em nenhuma loja a oferta continua a existir, sem nota; empate e mais barata com stock sem nota"
    requirement: RES-02
    verification:
      - kind: unit
        ref: "tests/test_bricomarche.py#test_offer_from_nenhuma_loja_com_stock"
        status: pass
      - kind: unit
        ref: "tests/test_bricomarche.py#test_offer_from_empate_prefere_a_loja_com_stock"
        status: pass
      - kind: unit
        ref: "tests/test_bricomarche.py#test_offer_from_sem_dica_quando_a_mais_barata_tem_stock"
        status: pass
    human_judgment: false
  - id: D3
    description: "Corrida completa sem rede das três lojas: bloco 'placa osb' com 'loja: Monção' e a nota da Coina"
    requirement: STORE-01
    verification:
      - kind: e2e
        ref: "tests/test_e2e.py#test_tres_itens_tres_lojas_pela_ordem"
        status: pass
    human_judgment: false
  - id: D4
    description: "Ao vivo, o link da 1.ª oferta da Bricomarché abre a página do produto numa loja com stock, com o preço mostrado"
    requirement: STORE-01
    verification:
      - kind: manual_procedural
        ref: "printf 'placa osb 9mm 1 un\\n\\n' | uv run python -m strata pesquisar"
        status: pass
    human_judgment: true
    rationale: "Os stocks mudam ao vivo; só uma pessoa confirma no site que a loja escolhida (Ponte de Sor) tem o artigo e o preço"

duration: 2 min
completed: 2026-10-23
status: complete
---

# Phase 01 Plan 10: Oferta da Bricomarché pela loja mais barata com stock Summary

**`offer_from` da Bricomarché passa a escolher a loja física mais barata com stock (só cai na mais barata absoluta quando nenhuma loja tem stock) e mostra a mais barata sem stock numa nota "mais barata sem stock: X em Y" (G-01-3)**

## Performance

- **Duration:** 2 min
- **Started:** 2026-10-23T18:59:29Z
- **Completed:** 2026-10-23T19:01:27Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Na amostra 47412, a oferta é 19,99 € em Monção, "118 em stock", com a nota "mais barata sem stock: 18,49 € em Coina - Barreiro"
- Ao vivo (`placa osb 9mm`): 15,49 € em Ponte de Sor, "68 em stock", com a nota "mais barata sem stock: 14,49 € em Coina - Barreiro". É o resultado que o utilizador pediu no UAT
- Casos de borda fixados por testes: ninguém com stock (fica a mais barata, sem nota), empate (ganha a com stock, sem nota), mais barata com stock (sem nota)
- A decisão do 01-04 aparece no STATE.md como "substituída pelo 01-10"

## Task Commits

1. **Tarefa 1 (tracer), RED:** testes reescritos (amostra 47412, sem dica, search osb, e2e) - `b99e34a` (test)
2. **Tarefa 1 (tracer), GREEN:** `offer_from` com escolha por stock e nota nova - `6d3f211` (feat)
3. **Tarefa 2:** 3 testes de borda e a decisão do 01-04 marcada como substituída - `5f12ac4` (test)

## TDD

- **RED (`b99e34a`):** `uv run python -m pytest tests/test_bricomarche.py tests/test_e2e.py -q` deu 3 failed, 14 passed, igual à baseline do plano. As 3 falhas (test_offer_from_amostra_47412, test_search_osb, test_tres_itens_tres_lojas_pela_ordem) caem nas asserções planeadas: o código antigo devolvia 18,49 € em Coina - Barreiro onde o teste pede 19,99 € em Monção. Não houve erros de import, de recolha nem de fixtures. Avaliação semântica: RED válido. Não gravei o registo para `check tdd-red-evidence`: `workflow.tdd_mode` não está ligado e o plano não é `type: tdd`.
- **GREEN (`6d3f211`):** 17 passed; suite completa 201 passed.
- **REFACTOR:** não foi preciso.

## Files Created/Modified

- `src/strata/stores/bricomarche.py` - `offer_from`: `low = cheapest(rows)`, `best = cheapest([r for r in rows if has_stock(r)]) or low`, nota só quando `_price(low) < _price(best)`
- `tests/test_bricomarche.py` - 3 testes reescritos e 3 novos
- `tests/test_e2e.py` - bloco "placa osb" pede "loja: Monção" e a nota nova
- `.planning/STATE.md` - linha do 01-04 marcada "substituída pelo 01-10"

## Decisions Made

- G-01-3: a oferta da Bricomarché é a loja física mais barata com stock; se nenhuma tiver stock, fica a mais barata com o stock dela; uma loja mais barata sem stock fica na nota "mais barata sem stock: X em Y". Substitui a decisão do 01-04. RES-02 proíbe esconder ofertas, não proíbe preferir a loja com stock.

## Deviations from Plan

None - plan executed exactly as written.

O human-check da Tarefa 1 (tracer) ficou para o fim da fase, como pede a secção `<verification>` do plano e `workflow.human_verify_mode: end-of-phase`. Fiz a única corrida ao vivo que o plano prevê; o resultado está em Accomplishments. Falta uma pessoa abrir o link no site.

## Issues Encountered

None. O aviso `CurlCffiWarning` em `tests/test_tracer.py::test_rede_bloqueada` já existia e não tem a ver com este plano.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Pronto para o 01-11 (G-01-5), que também mexe em `tests/test_bricomarche.py`.
- Para o `/gsd-verify-work`: abrir https://www.bricomarche.pt/ponte-de-sor/produto/placa-osb-lisa-2-50x1-25-9mm/ e confirmar 15,49 € com stock.
- Continua fora do âmbito: ordenar pais pelo stock (um pai sem stock em nenhuma loja ainda pode ficar em 1.º) e o corte K = 10 pelo preço do pai.

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*

## Self-Check: PASSED

- FOUND: src/strata/stores/bricomarche.py, tests/test_bricomarche.py, tests/test_e2e.py, .planning/STATE.md
- FOUND: b99e34a, 6d3f211, 5f12ac4 (ancestrais de HEAD)
- `uv run python -m pytest -q`: 204 passed
- `grep -c 'note = f"mais barata sem stock: '` = 1; `grep -cF 'has_stock(r)]) or low'` = 1; `grep -c "substituída pelo 01-10" .planning/STATE.md` = 1
