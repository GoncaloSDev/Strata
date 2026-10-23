---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 02
subsystem: testing
tags: [python, pytest, openpyxl, curl_cffi, stdin, decimal]

requires:
  - phase: 01-01
    provides: "Esqueleto strata (models, text, sheet, fetch, search, report, stores/allmat, __main__)"
provides:
  - "tests/conftest.py: FakeFetcher (route, calls, missing, cache), fixture fake e bloqueio de rede autouse para todos os testes da fase"
  - "tests/fixtures/ com as respostas da Allmat (cimento, osb sem resultados) pelo nome usado nas rotas"
  - "Testes sem rede do esqueleto: folha -> Allmat -> terminal, corte a 5 ofertas, modelo"
  - "Matriz de casos da folha do utilizador (LIST-05) e mensagem única para .xls/.xlsx corrompido"
  - "strata.text.parse_line e read_pasted; `pesquisar` sem ficheiro lê linhas coladas do stdin (LIST-01)"
affects: [01-03, 01-04, 01-05, 01-06, phase-3, phase-4]

actuals:
  tokens: 8100
  tasks: 3
  commits: 5
plan_head_before: e1bd38bfb14608092105bc471417adb095978109
plan_head_after: 17608d6270dc95c87c2084dab9dc0a8a5ec462c2

tech-stack:
  added: []
  patterns:
    - "Testes ponta a ponta fixam `strata.search.STORES` com monkeypatch e encaminham cada URL com fake.route(substring, fixture)"
    - "Fixture `fake` falha no fim do teste se algum URL ficou sem fixture (fake.missing)"
    - "Texto colado lido a partir do fim: unidade, depois quantidade, o resto é a descrição"

key-files:
  created:
    - .gitignore
    - tests/conftest.py
    - tests/test_tracer.py
    - tests/test_sheet.py
    - tests/test_text.py
    - tests/fixtures/allmat_products_search-cimento.json
    - tests/fixtures/allmat_products_search-osb_no-results.json
  modified:
    - src/strata/sheet.py
    - src/strata/text.py
    - src/strata/__main__.py

key-decisions:
  - "Linha colada só com número ('30 un', '30') -> 'linha sem descrição', em vez de virar um produto chamado '30'"
  - "Texto colado sem nenhuma linha válida (mas com inválidas) -> 'Nenhuma linha válida para pesquisar.' e código 2; a folha mantém 'A folha não tem linhas para pesquisar.'"
  - ".xls, zip corrompido e outros erros de abertura dão a mesma mensagem: 'não consegui abrir <nome>: é .xls ou não é um .xlsx válido (guarde a folha como .xlsx)'"

patterns-established:
  - "FakeFetcher: alvo str = ficheiro em tests/fixtures/, bytes = corpo, Exception = lançada, outro objeto = devolvido pelo get_json; sem rota usa fixture_name(full_url)"

requirements-completed: [LIST-01, LIST-05, LIST-02, LIST-04, STORE-05, PRICE-01, RES-02]

coverage:
  - id: D1
    description: "A suite corre sem rede: pedidos reais lançam 'rede bloqueada nos testes' e as respostas da Allmat vêm de tests/fixtures/"
    requirement: STORE-05
    verification:
      - kind: unit
        ref: "tests/test_tracer.py#test_rede_bloqueada"
        status: pass
    human_judgment: false
  - id: D2
    description: "Folha com cimento/osb/caixa mostra 'linha 4: unidade desconhecida: caixa', 'Allmat: ok' com 4,22 €, 'IVA: regra da loja', '186 em stock' e 'Allmat: sem resultados', pela ordem das linhas; corte a 5 ofertas com '+2 ofertas não mostradas'"
    requirement: PRICE-01
    verification:
      - kind: e2e
        ref: "tests/test_tracer.py#test_folha_allmat_terminal"
        status: pass
      - kind: unit
        ref: "tests/test_tracer.py#test_corte_a_5_ofertas"
        status: pass
    human_judgment: false
  - id: D3
    description: "modelo.xlsx com os cabeçalhos D-06, os dois exemplos e a lista pendente D2:D1000; um modelo existente fica byte a byte igual e o comando sai com 1"
    requirement: LIST-04
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_sheet.py -k modelo -q (5 testes)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Folha do utilizador: cabeçalho fora da linha 1, colunas por nome, segunda folha, cada motivo de linha inválida (juntos com '; '), sinónimos de unidade, vírgula decimal, linhas vazias ignoradas, duplicados mantidos, ficheiros ilegíveis com código 2 sem traceback, folha vazia sem pedidos às lojas"
    requirement: LIST-05
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_sheet.py -q (20 testes)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Família, Tamanho, Referência e Notas ficam no item; só o Produto, tal como escrito, vai para a pesquisa"
    requirement: LIST-02
    verification:
      - kind: unit
        ref: "tests/test_sheet.py#test_opcionais_guardados_e_produto_tal_como_escrito"
        status: pass
    human_judgment: false
  - id: D6
    description: "`pesquisar` sem ficheiro lê linhas coladas até uma linha vazia, com descrição/quantidade/unidade e avisos 'unidade assumida: un' / 'quantidade assumida: 1'"
    requirement: LIST-01
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_text.py -q (16 testes)"
        status: pass
      - kind: e2e
        ref: "printf 'cimento 10 saco\\n\\n' | uv run python -m strata pesquisar (ao vivo, 2026-10-23)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Colar texto na consola interativa do Windows (não em pipe) mostra 'm²' e acentos certos"
    requirement: LIST-01
    verification: []
    human_judgment: true
    rationale: "Suposição A8 do research: só o pipe foi testado (com reconfigure para UTF-8); a consola interativa precisa de uma pessoa a colar texto"

duration: 4min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 02: Testes sem rede, folha endurecida e texto colado Summary

**Rede de testes sem rede (FakeFetcher com fixtures pelo nome do `--record`, 39 testes em <1 s), leitura da folha com mensagem única para `.xls`/zip corrompido, e `pesquisar` sem ficheiro a ler linhas coladas como "OSB 12mm 30 un" com avisos quando assume un ou 1**

## Performance

- **Duration:** 4 min
- **Started:** 2026-10-22T23:57:19Z
- **Completed:** 2026-10-23T00:01:29Z
- **Tasks:** 3
- **Files modified:** 10 (7 criados, 3 alterados)

## Accomplishments

- `uv run pytest -q` corre 39 testes sem rede em menos de 1 s. Qualquer `AsyncSession.request` real lança "rede bloqueada nos testes".
- `tests/conftest.py` dá aos planos 01-03 a 01-06 o `FakeFetcher` (`route`, `calls`, `missing`, `cache`) e a fixture `fake`, que falha se faltar alguma fixture.
- O esqueleto do 01-01 ficou coberto: folha -> Allmat -> terminal, linha inválida, corte a 5 ofertas, modelo que nunca sobrescreve.
- `read_sheet` tem uma matriz de 15 casos (LIST-05). A única alteração de código foi a mensagem de abertura, porque o resto já funcionava como pedido.
- `uv run python -m strata pesquisar` sem ficheiro pede a lista e lê até uma linha vazia. Ao vivo, `cimento 10 saco` deu "Allmat: ok" com 4,22 €.

## Task Commits

1. **Tarefa 1: Testes sem rede do esqueleto e do modelo**: `0eb0bf4` (test)
2. **Tarefa 2: Folha do utilizador**: RED `80a0e96` (test), GREEN `2ddaf87` (feat)
3. **Tarefa 3: Pesquisa rápida por texto colado**: RED `c2d4e09` (test), GREEN `17608d6` (feat)

Sem commits de REFACTOR: não houve limpeza a fazer.

## Files Created/Modified

- `.gitignore`: `.venv/`, `__pycache__/`, `.pytest_cache/`.
- `tests/conftest.py`: bloqueio de rede autouse, `FakeFetcher`, fixture `fake`.
- `tests/test_tracer.py`: ponta a ponta folha -> Allmat, corte a 5 ofertas, rede bloqueada.
- `tests/test_sheet.py`: 5 testes do modelo e 15 da folha do utilizador.
- `tests/test_text.py`: 12 casos de `parse_line`, 2 de `read_pasted`, 2 ponta a ponta por stdin.
- `tests/fixtures/allmat_products_search-*.json`: cópia das amostras da fase.
- `src/strata/sheet.py`: erros de abertura (`InvalidFileException`, `BadZipFile`, etc.) com uma mensagem só.
- `src/strata/text.py`: `parse_line`, `read_pasted`, regex `NUM` e `GLUED`.
- `src/strata/__main__.py`: `pesquisar` sem ficheiro lê o stdin (reconfigurado para UTF-8), mostra o pedido no stderr e responde "Nenhuma linha colada." com código 2.

## TDD

- **Tarefa 2, RED (`80a0e96`):** 3 de 20 testes falharam, todos nas asserções da mensagem de abertura (`test_ficheiro_xls`, `test_ficheiro_corrompido`, `test_comando_com_ficheiro_ilegivel_sai_com_2_sem_traceback`). O texto antigo era "formato não suportado" / "não foi possível ler". Os outros 17 passaram logo, porque o 01-01 já fazia isso (o plano previa este caso: "se os testes o mostrarem"). Avaliação: RED válido, falha pelo motivo planeado.
- **Tarefa 2, GREEN (`2ddaf87`):** 20/20.
- **Tarefa 3, RED (`c2d4e09`):** a primeira corrida falhou na recolha (ImportError, RED inválido). Juntei assinaturas vazias de `parse_line`/`read_pasted` ao commit de teste e voltei a correr: os 16 falharam nas asserções (item `None`, erro `None`, listas vazias, código 2 em vez de 0). Avaliação: RED válido.
- **Tarefa 3, GREEN (`17608d6`):** 16/16, suite inteira 39/39.
- O classificador `check tdd-red-evidence` não foi corrido: o relatório do pytest não é um formato que ele suporte (TAP/JUnit/go/swift/unittest), e `workflow.tdd_mode` está desligado. A avaliação acima foi feita lendo a saída.

## Decisions Made

- "30 un" e "30" sozinhos dão "linha sem descrição". O Pattern 6 do research transformava "30" num produto chamado "30".
- Com texto colado só com linhas inválidas, a mensagem é "Nenhuma linha válida para pesquisar." (código 2). "A folha não tem linhas..." não faz sentido quando não há folha.
- A quantidade inválida mostra o texto que o utilizador escreveu ("quantidade não é um número positivo: 0").

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] "30 un" virava um produto chamado "30"**
- **Found during:** Tarefa 3 (parse_line)
- **Issue:** no Pattern 6 do research, a quantidade só é retirada se `len(toks) > 1`. Com "30 un", o "30" ficava como descrição, mas o plano pede "linha sem descrição".
- **Fix:** se o único token restante for um número, devolve "linha sem descrição".
- **Files modified:** src/strata/text.py
- **Verification:** `tests/test_text.py::test_parse_line_erros[30 un-...]`
- **Committed in:** 17608d6

**2. [Rule 3 - Blocking] RED da tarefa 3 não podia falhar numa asserção**
- **Found during:** Tarefa 3 (RED)
- **Issue:** sem `parse_line`/`read_pasted`, o pytest falhava na importação (RED inválido).
- **Fix:** assinaturas vazias em `text.py` no commit de teste, substituídas no GREEN.
- **Files modified:** src/strata/text.py
- **Verification:** 16 falhas por asserção no RED, 16 passagens no GREEN.
- **Committed in:** c2d4e09, 17608d6

---

**Total deviations:** 2 auto-fixed (1 bug, 1 bloqueio)
**Impact on plan:** nenhum âmbito novo.

## Issues Encountered

- O `test_rede_bloqueada` mostra um aviso do curl_cffi ("Proactor event loop does not implement add_reader") por abrir um `AsyncSession` verdadeiro no Windows. É inofensivo e não aparece nos outros testes, porque esses usam o `FakeFetcher`.

## Pending Human Check (end-of-phase)

- Correr `uv run python -m strata pesquisar` numa consola normal do Windows, colar `azulejo 2,5 m²` e carregar duas vezes em Enter. **Esperado:** "Linha 1 — azulejo (2,5 m²)". Motivo: só o pipe foi testado (A8).

## User Setup Required

Nenhum: não há serviços externos nem chaves.

## Next Phase Readiness

- Pronto para o 01-03. Os testes novos usam `fake.route(...)` e `monkeypatch.setattr(strata.search, "STORES", ...)`. A pesquisa alargada do 01-03 não faz pedidos extra nos testes ponta a ponta, porque os produtos têm uma só palavra ("cimento", "osb").
- O stub "M2" da Allmat (01-01) continua para o 01-03 tarefa 3.

## Self-Check: PASSED

- 10/10 ficheiros de `key-files` existem no disco.
- Os commits `0eb0bf4`, `80a0e96`, `2ddaf87`, `c2d4e09` e `17608d6` estão no histórico de HEAD, e `check evaluation-scope --plan 01-02 --commits-only` devolve-os.
- Critérios de aceitação: test_tracer 3 passed, test_sheet -k modelo 5 passed, test_sheet 20 passed, test_text 16 passed, suite 39 passed. `.save(` só uma vez em sheet.py, `BadZipFile` e `InvalidFileException` presentes, `git status` sem `__pycache__`/`.venv`. A corrida ao vivo mostrou "Linha 1 — cimento (10 saco)" e "Allmat: ok".

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*
