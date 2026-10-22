---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 01
subsystem: cli
tags: [python, uv, curl_cffi, openpyxl, selectolax, woocommerce-store-api, decimal]

requires: []
provides:
  - "Pacote strata (uv, Python 3.13) com `python -m strata modelo` e `python -m strata pesquisar <xlsx> [--record DIR]`"
  - "Contrato de dados da fase em strata.models (Item, Invalida, Offer, Found, StoreResult, ItemResult)"
  - "Fetcher único (curl_cffi chrome) com limites por host, falhas classificadas e gravação de fixtures"
  - "Adaptador Allmat sobre a Store API (cêntimos -> Decimal com IVA, stock, link, paginação até 300)"
  - "search.STORES / search_store / run e report.print_item com o estado da loja primeiro"
affects: [01-02, 01-03, 01-04, 01-05, 01-06, phase-2, phase-4, phase-5]

actuals:
  tokens: 18200
  tasks: 2
  commits: 1
plan_head_before: 70c69d7d1def2fe53774ff0389b5f7e6ea6d6796
plan_head_after: 4c116bd1b01bb8c1db9648a9e53835a677f39d4e

tech-stack:
  added: [curl_cffi 0.16.3, openpyxl 3.1.5, selectolax 1.0.2 (pin >=1.0,<1.1), pytest 9.1.1 (dev)]
  patterns:
    - "Loja = módulo em src/strata/stores/ com NAME e async search(query, fetch) -> Found; o adaptador lança, search_store converte em estado"
    - "Dinheiro sempre Decimal: json.loads(parse_float=Decimal), from_minor para cêntimos, arredondar só ao mostrar"
    - "Folha só lida (load_workbook data_only=True, modo normal); modelo criado com open(path, 'xb')"
    - "Todo o texto de loja/folha passa por report.clean antes do terminal"

key-files:
  created:
    - pyproject.toml
    - uv.lock
    - .python-version
    - src/strata/__main__.py
    - src/strata/models.py
    - src/strata/text.py
    - src/strata/sheet.py
    - src/strata/money.py
    - src/strata/fetch.py
    - src/strata/search.py
    - src/strata/report.py
    - src/strata/stores/allmat.py
  modified: []

key-decisions:
  - "Tarefa 1 aprovada pelo utilizador ('aprovado'): curl_cffi, openpyxl, pytest e selectolax com pin >=1.0,<1.1 (resolveu para 1.0.2)"
  - "Allmat: rótulo 'Unid' -> content 1 un; 'M2' ou outro rótulo -> preço por unidade desconhecido com nota visível (a área da caixa entra no 01-03)"
  - "Prazo de 90 s por (item, loja) via asyncio.timeout; detalhe 'mais de 90 s' quando o prazo dispara"

patterns-established:
  - "Contrato de loja: NAME + async search(query, fetch) -> Found(offers, raw, hidden, notes); raw == 0 é o único caminho para 'sem resultados'"
  - "Comando devolve 2 para erros de entrada (folha, ficheiro em falta), 1 para modelo já existente, 0 quando a corrida acaba"

requirements-completed: [LIST-04, LIST-05, LIST-02, STORE-05, PRICE-01, RES-02]

coverage:
  - id: D1
    description: "`modelo` grava modelo.xlsx com os 7 cabeçalhos, 2 linhas de exemplo e a lista pendente D2:D1000; um segundo `modelo` sai com 1 e não toca no ficheiro"
    requirement: LIST-04
    verification:
      - kind: e2e
        ref: "verify 3 do plano: modelo duas vezes numa pasta temporária, sha256 igual, código 1, 'existe nesta pasta'"
        status: pass
    human_judgment: false
  - id: D2
    description: "O Excel mostra a lista pendente un, m², m, kg, L, saco com o '²' certo e o aviso 'Escolha da lista: ...' ao escrever 'caixa'"
    requirement: LIST-04
    verification: []
    human_judgment: true
    rationale: "Não há Excel nesta máquina (A8): o openpyxl relê sqref D2:D1000 e formula1 certos, mas só o Excel confirma o que o utilizador vê"
  - id: D3
    description: "`pesquisar lista.xlsx` mostra 'linha 4: unidade desconhecida: caixa', OSB 12 mm como 'Allmat: sem resultados' e cimento como 'Allmat: ok' com preço com IVA, origem do IVA, stock e link; nenhum ficheiro novo na pasta"
    requirement: LIST-05
    verification:
      - kind: e2e
        ref: "verify 2 do plano: corrida ao vivo contra allmat.pt (2026-10-23)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Falhas de loja viram estado visível (bloqueada / tempo esgotado / erro com detalhe) e nunca desaparecem; preço <= 0 nunca vira oferta"
    requirement: STORE-05
    verification:
      - kind: other
        ref: "verificação ad hoc com um fetch falso (StoreBlocked, StoreTimeout, KeyError, [], dict, preço 0); os testes pytest chegam no 01-02 tarefa 1"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 01: Esqueleto modelo -> folha -> Allmat -> terminal Summary

**CLI `uv run python -m strata` com `modelo` (modelo.xlsx com lista pendente, criação exclusiva) e `pesquisar <xlsx>` que lê a folha pelo nome dos cabeçalhos e mostra a Allmat ao vivo (Store API, cêntimos -> Decimal com IVA, estado da loja primeiro, até 5 ofertas)**

## Performance

- **Duration:** 4 min (execução da tarefa 2; a tarefa 1 foi resolvida antes pelo orquestrador)
- **Started:** 2026-10-22T23:49:29Z
- **Completed:** 2026-10-22T23:53:42Z
- **Tasks:** 2 (tarefa 1 checkpoint aprovado, tarefa 2 tracer)
- **Files modified:** 14 criados

## Accomplishments

- `uv run python -m strata modelo` grava `modelo.xlsx` (folha "Lista", cabeçalhos D-06, exemplos "OSB 12 mm" e "cimento", lista pendente un/m²/m/kg/L/saco em D2:D1000). Se o ficheiro já existir, fica igual e a saída é "modelo.xlsx já existe nesta pasta; não foi alterado." (código 1).
- `uv run python -m strata pesquisar lista.xlsx` encontra a tabela pelo nome dos cabeçalhos nas 10 primeiras linhas de qualquer folha, lista as linhas inválidas com o número do Excel e o motivo e pesquisa as restantes.
- Corrida ao vivo: "OSB 12 mm" -> "Allmat: sem resultados"; "cimento" -> "Allmat: ok" com 4,22 € "LIZ CIMENTO COLA CINZA SACO 25 KG", "IVA: regra da loja (...)", "4,22 €/un", "186 em stock", link e "+6 ofertas não mostradas".
- Fetcher com ritmo por host (Allmat 2 / 0,5 s), timeout (10, 30), `StoreBlocked`/`StoreError`/`StoreTimeout`, `parse_float=Decimal` e `--record` que grava só o corpo.

## Task Commits

1. **Tarefa 1: Confirmar os 4 pacotes PyPI antes do uv add** — sem commit (checkpoint `blocking-human`). Resposta do utilizador: **"aprovado"**, o que fixa `selectolax>=1.0,<1.1`. Evidência mostrada pelo orquestrador (PyPI JSON API, 2026-10-23): curl-cffi 0.16.3 (2026-09-02, github.com/lexiforest/curl_cffi); openpyxl 3.1.5 (2024-06-28, foss.heptapod.net/openpyxl/openpyxl); selectolax 1.0.2 (2026-10-22, github.com/rushter/selectolax); pytest 9.1.1 (2026-06-19, github.com/pytest-dev/pytest).
2. **Tarefa 2: Ponta a ponta "modelo -> folha .xlsx -> Allmat -> terminal"** — `4c116bd` (feat)

## Files Created/Modified

- `pyproject.toml`: projeto uv com as 3 dependências, pytest no grupo dev e `testpaths = ["tests"]`. Sem `[project.scripts]`.
- `uv.lock`, `.python-version` (3.13): gerados pelo uv.
- `src/strata/models.py`: Status, VatOrigin, Item, Invalida, Offer, Found, StoreResult, ItemResult.
- `src/strata/text.py`: `norm`, `UNITS` (sinónimos D-07), `to_decimal` (rejeita bool, vazio, NaN/inf).
- `src/strata/sheet.py`: `SheetError`, `find_table`, `read_sheet` (só leitura, erros de abertura em PT-PT), `write_template` (`open(path, "xb")`).
- `src/strata/money.py`: `from_minor`, `per_unit`, `fmt_eur`, `fmt_unit_price`, `fmt_qty` (ROUND_HALF_UP só ao mostrar).
- `src/strata/fetch.py`: `LIMITS`, `CHALLENGE`, `full_url`, `fixture_name`, `Host`, `Fetcher` (`get`, `get_json`, `get_html`, `cache`, `record`).
- `src/strata/stores/allmat.py`: `parse_products` (puro) e `search` (paginação até 3 × 100, nota quando há mais).
- `src/strata/search.py`: `STORES = (allmat,)`, `DEADLINE_S = 90`, `search_store` (um só try/except), `run` (gerador assíncrono, item a item).
- `src/strata/report.py`: `clean`, `MAX_SHOWN = 5`, `print_invalid`, `print_item`.
- `src/strata/__main__.py`: `main(argv=None, fetch=None)`, subcomandos `pesquisar` e `modelo`, stdout/stderr em UTF-8.

## Decisions Made

- Pin do selectolax `>=1.0,<1.1`, aprovado pelo utilizador na tarefa 1. O uv resolveu para a 1.0.2.
- Rótulo de unidade da Allmat: "Unid" -> 1 un (€/un = preço); "M2" -> €/m² desconhecido com a nota "rótulo M2 da loja: área da caixa não lida"; outro rótulo ou nenhum -> nota com o rótulo. Nada fica escondido.
- `Host.__aenter__` liberta a vaga do semáforo se a tarefa for cancelada à espera do intervalo (o prazo de 90 s cancela tarefas). Sem isto, um "tempo esgotado" podia deixar o host com uma vaga a menos para o item seguinte.
- O commit foi feito em `master`, como o orquestrador indicou (sem remoto, `branching_strategy: none`, todos os commits anteriores estão lá). O guard genérico de "ramo protegido" do executor classifica `master` como protegido; segui a instrução explícita do despacho sequencial.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Vaga do semáforo perdida em cancelamento no `Host`**
- **Found during:** Tarefa 2 (fetch.py)
- **Issue:** no exemplo do research, se o `asyncio.timeout(90)` cancelar a tarefa enquanto espera pelo intervalo, `__aexit__` nunca corre e a vaga do semáforo não volta.
- **Fix:** `try/except BaseException` em `__aenter__` que liberta o semáforo e relança.
- **Files modified:** src/strata/fetch.py
- **Verification:** leitura do fluxo; o caminho normal foi exercido na corrida ao vivo.
- **Committed in:** 4c116bd

**2. [Rule 1 - Bug] `to_decimal` aceitava NaN/infinito**
- **Found during:** Tarefa 2 (text.py)
- **Issue:** `Decimal(str(float("nan")))` é válido, por isso uma Qty "nan" passaria a validação.
- **Fix:** devolver None quando o Decimal não é finito.
- **Files modified:** src/strata/text.py
- **Verification:** `to_decimal(float('nan'))` -> None, verificado à mão.
- **Committed in:** 4c116bd

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** correções pequenas, de correção, sem âmbito novo.

## Pending Human Check (end-of-phase)

- Correr `uv run python -m strata modelo` numa pasta qualquer, abrir `modelo.xlsx` no Excel e clicar numa célula da coluna Unidade. **Esperado:** a lista mostra un, m², m, kg, L, saco com o "²" certo; escrever "caixa" mostra o aviso "Escolha da lista: un, m², m, kg, L, saco". Motivo: não há Excel nesta máquina (A8). Fica para o UAT do fim da fase (`workflow.human_verify_mode = end-of-phase`), não bloqueou a execução.

## Known Stubs

| Ficheiro | Linha | Stub | Motivo / quem resolve |
|---|---|---|---|
| src/strata/stores/allmat.py | 33 | Rótulo "M2": `content` None, nota "área da caixa não lida", €/m² desconhecido | Intencional no esqueleto. A leitura da página com a área da caixa é a tarefa 3 do plano 01-03 (STORE-02). A oferta aparece sempre, com preço por caixa e a nota. |

## Issues Encountered

- Nenhum. A pré-condição (Allmat responde 200 a `search=cimento&per_page=1`) confirmou-se antes da corrida ao vivo.

## Verification

- `uv run python -m strata pesquisar --help` -> código 0, lista `--record`. PASS
- Corrida ao vivo (modelo -> linha 4 "tijolo/caixa/5" -> pesquisar): "linha 4: unidade desconhecida: caixa", "Allmat: sem resultados" (OSB 12 mm), "Allmat: ok" (cimento); a pasta ficou só com lista.xlsx, modelo.xlsx e out.txt. PASS
- Segundo `modelo`: código 1, "modelo.xlsx já existe nesta pasta; não foi alterado.", sha256 igual. PASS
- Critérios de aceitação por grep (testpaths, selectolax, parse_float=Decimal, cf-mitigated, obras360 (3, 0.3), sem requests/httpx/urllib.request, DEADLINE_S = 90, STORES = (allmat,), MAX_SHOWN = 5, unicodedata.category, data_only=True, "xb", D2:D1000, sem read_only=True). PASS
- Extra, à mão: cabeçalho na linha 3 de uma segunda folha, ordem trocada, maiúsculas e acentos, coluna extra, linha vazia ignorada, "3,5"/"Lt" aceites, Qty 0/"abc" inválidas; ficheiro em falta, `.txt` e zip corrompido -> mensagem de uma linha e código 2.

## User Setup Required

Nenhum: não há serviços externos nem chaves nesta fase.

## Next Phase Readiness

- Pronto para o 01-02: harness sem rede (`tests/conftest.py` com FakeFetcher que use `fetch.fixture_name`), testes do esqueleto e `.gitignore` (`__pycache__/`, `.venv/`).
- Os planos 01-04 e 01-05 acrescentam `bricomarche` e `obras360` a `search.STORES`; o `Fetcher` já tem os limites desses hosts.

## Self-Check: PASSED

- 14/14 ficheiros de `key-files` existem no disco.
- Commit `4c116bd` está no histórico de HEAD; `check evaluation-scope --plan 01-01 --commits-only` devolve 1 commit.

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*
