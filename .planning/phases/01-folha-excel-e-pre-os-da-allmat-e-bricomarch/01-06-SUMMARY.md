---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 06
subsystem: search
tags: [python, pytest, curl_cffi, cli, store-check]

requires:
  - phase: 01-02
    provides: "tests/conftest.py (FakeFetcher, fixture fake, rede bloqueada), `pesquisar` pelo stdin"
  - phase: 01-05
    provides: "search.STORES = (allmat, bricomarche, obras360), search_store, allmat.INCOHERENT, fixtures das três lojas"
provides:
  - "strata.search.CANARIES e verificar(fetch) -> list[(rótulo, ok, mensagem)]"
  - "Subcomando `uv run python -m strata verificar [--record DIR]` com código 1 quando alguma loja falha"
  - "tests/test_e2e.py: três itens colados contra as três lojas reais, sem rede"
  - "README.md com os três comandos"
affects: [phase-2, phase-3, phase-5]

actuals:
  tokens: 3877
  tasks: 2
  commits: 3
plan_head_before: 47e7de1cb70f6bb8d27b08e5ff3b48bf67781883
plan_head_after: eb9c373df5cf30ca8ee61605cb54d29af7cb5847

tech-stack:
  added: []
  patterns:
    - "Verificação de loja pelo mesmo search_store do dia a dia (com D-14 e D-15), sobre todas as ofertas devolvidas, parando no primeiro motivo"
    - "_with_fetch(work, fetch, record) abre a sessão curl_cffi uma vez por comando; os testes passam o FakeFetcher"

key-files:
  created:
    - tests/test_e2e.py
    - README.md
  modified:
    - src/strata/search.py
    - src/strata/__main__.py
    - tests/test_search.py

key-decisions:
  - "verificar devolve (rótulo, ok, mensagem); o comando imprime '<rótulo>: OK|FALHOU — <mensagem>'"
  - "Canários: Allmat cimento e pavimento (caixas M2), Bricomarché cimento, Obras 360 osb; corridos um a um"
  - "DEADLINE_S (90 s), K da Bricomarché (10), K da Obras 360 (20) e MAX_BOX_PAGES (10) ficam como estavam: a corrida ao vivo não mostrou tempo esgotado nem limites a cortar ofertas mais baratas"

patterns-established:
  - "Um adaptador novo entra em CANARIES com o seu termo e, se tiver uma regra própria (IVA, loja física, caixa), um ramo em search._problem"

requirements-completed: [STORE-07, STORE-05]

coverage:
  - id: D1
    description: "`verificar` dá OK nas quatro linhas com respostas boas e FALHOU com o motivo para: sem ofertas, IVA da Obras 360 a 6%, Bricomarché sem nome de loja, caixa Allmat incoerente, nenhuma área de caixa lida, loja bloqueada ou em erro; preço 0 num produto fica na nota e não falha"
    requirement: STORE-07
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_search.py -k verificar -q (10 testes)"
        status: pass
    human_judgment: false
  - id: D2
    description: "`uv run python -m strata verificar` ao vivo: Allmat (cimento), Allmat (pavimento), Bricomarché (cimento) e Obras 360 (osb) todas OK, código 0, 50 s"
    requirement: STORE-07
    verification:
      - kind: e2e
        ref: "uv run python -m strata verificar (ao vivo, 2026-10-23)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Três itens colados (placa osb, cimento, xyzqwkk) mostram as três lojas pela ordem Allmat, Bricomarché, Obras 360; xyzqwkk sem resultados nas três"
    requirement: STORE-05
    verification:
      - kind: e2e
        ref: "tests/test_e2e.py#test_tres_itens_tres_lojas_pela_ordem"
        status: pass
    human_judgment: false
  - id: D4
    description: "--record grava só corpos de resposta (36 ficheiros numa pesquisa de cimento, nenhum com Set-Cookie)"
    verification:
      - kind: e2e
        ref: "printf 'cimento 5 saco\\n\\n' | uv run python -m strata pesquisar --record $D; grep -rli Set-Cookie $D (ao vivo)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Folha modelo.xlsx com 3 linhas (OSB 12 mm / un / 30; cimento cola / saco / 10; tinta branca / L / 15) contra as lojas reais: estado das três lojas por linha, preço com IVA, origem do IVA, €/unidade, stock, pesquisa alargada marcada, 26 s"
    requirement: STORE-05
    verification:
      - kind: e2e
        ref: "modelo + fill + pesquisar modelo.xlsx (ao vivo, 2026-10-23, saída transcrita abaixo)"
        status: pass
    human_judgment: true
    rationale: "Human-check do plano: ler a tabela no terminal e julgar se os preços batem com o que se vê nos sites"

duration: 98min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 06: Verificar as lojas e corrida completa Summary

**Comando `uv run python -m strata verificar`: um termo de teste por loja (Allmat cimento e pavimento, Bricomarché cimento, Obras 360 osb) passa pelo mesmo `search_store` do dia a dia. O comando falha a loja quando falta estado ok, ofertas, preço acima de zero, IVA ou unidade coerentes, IVA da Obras 360 a 23%, nome da loja Bricomarché ou caixa Allmat coerente, e sai com 1. Ao vivo: 4/4 OK em 50 s. A fase fecha com uma corrida sem rede das três lojas e uma folha real de 3 linhas em 26 s.**

## Performance

- **Duration:** 98 min de relógio. Inclui a pausa do limite de uso a meio do plano; o trabalho em si foi bem menos.
- **Started:** 2026-10-23T00:29:39Z
- **Completed:** 2026-10-23T02:08:23Z
- **Tasks:** 2
- **Files modified:** 5 (2 criados, 3 alterados)

## Accomplishments

- `search.verificar(fetch)` corre os quatro canários um a um e verifica todas as ofertas devolvidas, não só as 5 mostradas. Para no primeiro motivo e devolve `(rótulo, ok, mensagem)`.
- `uv run python -m strata verificar` imprime, por exemplo, `Allmat (cimento): OK — 11 ofertas, mais barata 4,22 €` ou `Obras 360 (osb): FALHOU — IVA da loja não é 23%`. Sai com 1 se alguma linha falhar. Aceita `--record DIR` para gravar fixtures novas.
- `tests/test_e2e.py` cola "placa osb 3 un", "cimento 10 saco" e "xyzqwkk 1 un" com o `STORES` real. Cada item mostra as três lojas pela ordem certa, e "xyzqwkk" sai "sem resultados" nas três.
- `README.md` na raiz com os comandos `modelo`, `pesquisar modelo.xlsx` (ou lista colada) e `verificar`.
- Suite: 126 → 137 testes, todos verdes, em ~1 s.

## Task Commits

1. **Tarefa 1: Comando `verificar`**: RED `02aa29f` (test), GREEN `a9b1c95` (feat)
2. **Tarefa 2: Corrida completa das três lojas**: `eb9c373` (test)

Sem commits de REFACTOR: não houve limpeza a fazer.

## Files Created/Modified

- `src/strata/search.py`: `CANARIES`, `VAT_ORIGINS`, `CONTENT_UNITS`, `_problem` e `verificar`.
- `src/strata/__main__.py`: subcomando `verificar` com ajuda em PT-PT. `_with_fetch` passa a ser partilhado por `pesquisar` e `verificar` (abre a sessão curl_cffi quando não há fetch de teste).
- `tests/test_search.py`: 10 testes `verificar` (4 OK, preço 0 na nota, todos a 0, IVA 6%, sem loja, caixa incoerente, sem área, bloqueada/erro).
- `tests/test_e2e.py`: corrida ponta a ponta sem rede com as três lojas.
- `README.md`: o que a ferramenta faz e os três comandos.

## TDD

- **Tarefa 1, RED (`02aa29f`):** os 10 testes falharam com o stub (`CANARIES = ()`, `verificar` devolve `[]`). Oito falharam em asserções sobre a lista vazia. `test_verificar_preco_zero_fica_na_nota` falhou ao desempacotar essa lista vazia. Os dois que chamam `main(["verificar"])` falharam porque o argparse ainda não conhecia o subcomando (SystemExit). As falhas vêm todas do comportamento em falta, nenhuma da importação. Avaliação: RED válido.
- **Tarefa 1, GREEN (`a9b1c95`):** 10/10; suite 136/136.
- O classificador `check tdd-red-evidence` não foi corrido: o pytest não produz nenhum dos formatos que ele aceita, e `workflow.tdd_mode` está desligado. A avaliação acima foi feita a ler a saída.

## Corrida ao vivo (2026-10-23)

Pré-condição: allmat.pt, www.bricomarche.pt e www.obras360.pt responderam 200 antes das corridas.

| Corrida | Resultado | Tempo |
|---|---|---|
| `uv run python -m strata verificar` | Allmat (cimento) OK, 11 ofertas, 4,22 €; Allmat (pavimento) OK, 24 ofertas, 7,50 €; Bricomarché (cimento) OK, 10 ofertas, 0,58 €; Obras 360 (osb) OK, 15 ofertas, 8,36 €; código 0 | 50 s |
| `printf 'cimento 5 saco\n\n' \| … pesquisar --record $D` | 36 ficheiros, nenhum com `Set-Cookie`; código 0 | 18 s |
| Folha `modelo.xlsx` com 3 linhas | as três lojas por linha, código 0 | 26 s |
| "placa osb" (só para ler os títulos escondidos) | Allmat sem resultados, Bricomarché ok, Obras 360 ok | 6 s |

Folha de 3 linhas, o que apareceu:

- **OSB 12 mm / un / 30:** Allmat "sem resultados — também sem resultados com 'OSB'". Bricomarché ok, 18,49 € PLACA OSB 12 MM em Coina - Barreiro (0 em stock; com stock 19,99 € em Monção). Obras 360 "ok (pesquisa alargada: 'OSB')", com a placa OSB 9 mm a 15,02 € (4,81 €/m²) e a de 12 mm a 19,37 € (6,20 €/m²). Antes delas aparecem a cola SikaBond (8,36 €) e as espumas Sika Boom, que têm "OSB" no título.
- **cimento cola / saco / 10:** Allmat ok, 4,22 € LIZ 25 kg (0,1688 €/kg, 186 em stock). Bricomarché ok, 1,49 € 1,5 kg na Guarda (esgotado, com stock 1,99 € em Felgueiras), "+31 produtos não expandidos (limite de 10 por pesquisa)". Obras 360 ok, 4,04 € SecilTek 25 kg, "+17 produtos não expandidos (limite de 20 por pesquisa)".
- **tinta branca / L / 15:** Allmat sem resultados. Bricomarché ok, 44,95 € "Tinta Branca Especial 15000Ml" a 3,00 €/L. Obras 360 "ok" sem nenhuma oferta mostrada, só "+8 ofertas escondidas: título sem 'tinta branca'".

### Afinação de DEADLINE_S, K e limites de páginas (A1–A3)

Nenhuma. Nada chegou perto dos 90 s (a corrida mais longa, o `verificar`, demorou 50 s para quatro pesquisas seguidas). Os limites K cortaram pais na Bricomarché (+31) e na Obras 360 (+17). Os dois adaptadores expandem os pais mais baratos pelo preço mínimo do pai (`price_range.min_amount` e o preço da variante mais barata da lista), por isso um pai não expandido não devia ter oferta mais barata do que os expandidos. As caixas da Allmat em "pavimento" ficaram todas lidas dentro das 10 páginas.

### Títulos escondidos pelo filtro de palavras (observação do 01-05)

Registados com um invólucro de diagnóstico à volta de `title_matches` (script só no scratchpad, nada no repositório). A Allmat e a Bricomarché não esconderam nenhum título nestas corridas. Só a Obras 360 escondeu:

- **"placa osb" (6 escondidos):** Placa Duripanel (base cimentícia), Parafuso Autoperfurante LSF, 2× Membrana Líquida Hybrid Fiber, 2× Espuma Sika Boom com "OSB" no título. Nenhum é uma placa OSB. Os 6 de 7 que o 01-05 viu esconder estão bem escondidos.
- **"OSB" (pesquisa alargada de "OSB 12 mm", 6 escondidos):** Placa Duripanel, **Painel Sandwich Cobertura Thermochip TOH OSB3**, Cola Fassa AX 91, Parafuso LSF, 2× Membrana Líquida. O Thermochip é um painel sandwich com face OSB3. Não é a placa pedida, mas mostra que "OSB3" não conta como a palavra "OSB".
- **"cimento cola" (2):** Talocha Inox e Reboco SecilTek Redur. Bem escondidos.
- **"tinta branca" (8 de 8):** Dyrup Dyrustar 15L Branco Mate, Dyrup Super 15L Branco Mate, Dyrup Dycrilforce 15L Branco Mate, Primário Dyrup Dyprolite 15L Branco, Mapei Colorite Performance BRANCO 20KG, SecilTek Isovit Rev SP 15L, 2× Fita Pintura Branca.

**Achado para o verificador da fase:** em "tinta branca", pelo menos 4 títulos são claramente o produto pedido (tinta branca de 15 L ou 20 kg: Dyrustar, Dyrup Super, Dycrilforce, Mapei Colorite). O filtro escondeu-os porque o título diz "Branco" e a pesquisa diz "branca": o plural simples é tratado, o género não. O resultado é "Obras 360: ok" sem nenhuma oferta, para um produto que a loja vende. Também "OSB3" não bate com "OSB". O filtro não foi mexido neste plano, como pedido. Fica para o verificador decidir se entra como lacuna da fase ou vai para a Phase 3 (classificação exato/parecido).

## Decisions Made

- `verificar` devolve `(rótulo, ok, mensagem)`. A mensagem OK é "N ofertas, mais barata X €", e é o comando que acrescenta "OK —" ou "FALHOU —".
- O item de teste usa a unidade "un". Assim a ordem é a do preço do artigo e "mais barata" é a 1.ª oferta.
- DEADLINE_S, K e MAX_BOX_PAGES ficam como estavam (ver acima).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] RED sem erro de importação**
- **Found during:** Tarefa 1 (RED)
- **Issue:** sem `search.verificar`, o pytest falhava com AttributeError e não em asserções.
- **Fix:** stub (`CANARIES = ()`, `verificar` devolve `[]`) no commit de teste, substituído no GREEN, como nos planos 01-02 a 01-05.
- **Files modified:** src/strata/search.py
- **Verification:** as falhas do RED vêm do comportamento em falta.
- **Committed in:** 02aa29f

**2. [Rule 2 - Missing Critical] Texto da loja limpo antes do terminal**
- **Found during:** Tarefa 1 (GREEN)
- **Issue:** a mensagem de falha leva títulos e detalhes vindos da loja ("caixa incoerente em <título>", "estado erro: <detalhe>").
- **Fix:** `report.clean` no rótulo e na mensagem, como o `print_item` já faz com todo o texto de loja (tira sequências de controlo/ANSI).
- **Files modified:** src/strata/__main__.py
- **Verification:** testes `verificar` verdes; saída ao vivo normal.
- **Committed in:** a9b1c95

---

**Total deviations:** 2 auto-fixed (1 bloqueio, 1 correção em falta)
**Impact on plan:** nenhum âmbito novo.

## Issues Encountered

- O executor parou a meio por limite de uso, antes de qualquer alteração. Retomou do mesmo HEAD (47e7de1), sem trabalho a meio.
- O aviso `CurlCffiWarning` em `tests/test_tracer.py::test_rede_bloqueada` já existia e fica fora do âmbito.
- A corrida da folha foi feita uma vez, pelo invólucro de diagnóstico, que chama o mesmo `main(["pesquisar", ...])`. Correr outra vez só com o comando simples dobrava a carga nas lojas sem mostrar nada de novo.

## Pending Human Check (end-of-phase)

- Correr `uv run python -m strata modelo` numa pasta nova, preencher 3 linhas (ex.: "OSB 12 mm" / un / 30; "cimento cola" / saco / 10; "tinta branca" / L / 15) e correr `uv run python -m strata pesquisar modelo.xlsx`. **Esperado:** cada linha mostra Allmat, Bricomarché e Obras 360 com o estado primeiro; ofertas com preço com IVA, "IVA: ..." com a origem, €/unidade e stock; "pesquisa alargada" quando foi usada; termina em poucos minutos (ao vivo: 26 s). Falta uma pessoa comparar os preços com os sites.

## Known Stubs

Nenhum.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Os 6 planos da fase 1 estão feitos. Pronta para a verificação da fase (`/gsd-verify-work 01`).
- A ter em conta na verificação: o achado do filtro de palavras ("Branco" ≠ "branca", "OSB3" ≠ "OSB") na Obras 360.

## Verification

- `uv run pytest tests/test_search.py -k verificar -q` → 10 passed. PASS
- `uv run pytest -q` → 137 passed (1 aviso antigo). PASS
- `uv run python -m strata verificar` → 4 linhas OK, código 0. PASS
- `--record` → 36 ficheiros, nenhum com Set-Cookie. PASS
- Critérios por grep: `CANARIES` e `async def verificar` em search.py; `verificar` em `__main__.py`; `pesquisar modelo.xlsx` e `verificar` no README; "IVA da loja não é 23%", "sem nome de loja" e "caixa incoerente" em tests/test_search.py; "xyzqwkk", "Obras 360:" e "Bricomarché:" em tests/test_e2e.py. PASS

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*

## Self-Check: PASSED
