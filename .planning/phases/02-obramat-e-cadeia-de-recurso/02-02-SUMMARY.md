---
phase: 02-obramat-e-cadeia-de-recurso
plan: 02
subsystem: search
tags: [playwright, cdp, chrome, cadeia-de-recurso, datadome]

requires:
  - phase: 02-01
    provides: "Adaptador strata.stores.obramat, LIMITS da Obramat, STORES com 4 lojas"
provides:
  - "strata.browser.BrowserFetcher (get_json, get_html, cache, record, close) no Chrome dedicado por CDP"
  - "search_store(store, item, fetch, browser=None) com degraus API → browser, _attempt e _rungs"
  - "Offer.method e 'método: …' no relatório"
  - "Chaves de cache browser_only (D-08) e sem_principal (D-17)"
  - "--sem-principal LOJA em pesquisar e verificar"
  - "main(argv=None, fetch=None, browser=None)"
affects: [02-03, 02-04, 02-05, 02-06]

actuals:
  tokens: 5500  # chars/4 das linhas acrescentadas, sem o uv.lock
  tasks: 3
  commits: 3
plan_head_before: 00bba988e6aa1da7187a974adda045399b5add9f
plan_head_after: 6d16b4780abe2d8652e758156bd4a03c1dec530d

tech-stack:
  added: ["playwright>=1.64,<1.65 (1.64.1)"]
  patterns:
    - "Degraus (nome, store.search, transporte) com a mesma assinatura dos adaptadores; o BrowserFetcher tem a interface do Fetcher"
    - "Um separador novo por pedido, fechado no finally; ritmo pelos mesmos Host do Fetcher"
    - "Import do Playwright dentro das funções: os testes e o 'modelo' não o carregam"

key-files:
  created:
    - src/strata/browser.py
    - tests/test_chain.py
  modified:
    - pyproject.toml
    - uv.lock
    - src/strata/models.py
    - src/strata/search.py
    - src/strata/report.py
    - src/strata/__main__.py
    - tests/test_search.py
    - tests/test_e2e.py

key-decisions:
  - "Pacotes aprovados pelo utilizador no checkpoint da tarefa 1: 'Aprovado (os dois)' (playwright 1.64.1 e anthropic 2.3.0); o 02-05 pode fazer o uv add do anthropic sem novo checkpoint"
  - "Estado quando todos os degraus falham, por prioridade: bloqueada, depois tempo esgotado, depois erro; detail com o motivo de cada degrau pela ordem"
  - "--sem-principal grava cache['sem_principal'] em _with_fetch (nos dois ramos), antes de work correr"

patterns-established:
  - "Nota 'antes do <degrau>: <motivos>' quando um degrau posterior responde"
  - "Testes da cadeia com transportes SimpleNamespace(kind=..., cache=partilhada)"

requirements-completed: [STORE-06, STORE-04]

coverage:
  - id: D1
    description: "Obramat pelo Chrome dedicado: 'Obramat: ok' com 'método: browser', armazém de Alfragide, escalões e stock exato"
    requirement: STORE-04
    verification:
      - kind: e2e
        ref: "tests/test_e2e.py#test_obramat_bloqueada_vai_ao_browser_e_fica_la"
        status: pass
      - kind: other
        ref: "printf 'placa osb 1 un\\n\\n' | uv run python -m strata pesquisar --sem-principal obramat (ao vivo: 5 ofertas 'método: browser', '282 em stock em OBRAMAT Lisboa - Alfragide', '−5% a partir de 120')"
        status: pass
    human_judgment: false
  - id: D2
    description: "Cadeia API → browser: sem resultados e tudo escondido não escalam; bloqueio vai ao browser e a loja fica no browser; estados e motivos quando tudo falha; prazo partilhado"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_chain.py (14 testes)"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-06: o Chrome que a app abriu fecha no fim; o que já estava aberto fica aberto e só os separadores da app fecham"
    requirement: STORE-06
    verification:
      - kind: other
        ref: "ao vivo: porta 9222 fechada antes e depois de 3 corridas (P0=P1=000); com o Chrome já aberto, porta 200 e 1 separador depois da corrida"
        status: pass
    human_judgment: false
  - id: D4
    description: "--sem-principal allmat mostra a Allmat com 'método: browser' (JSON da Store API lido no Chrome, A4)"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_chain.py#test_sem_principal_na_linha_de_comandos"
        status: pass
      - kind: other
        ref: "printf 'cimento 1 un\\n\\n' | uv run python -m strata pesquisar --sem-principal allmat (ao vivo)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Ao vivo, a Obramat leva 403 no pedido simples e passa sozinha ao browser"
    requirement: STORE-04
    verification:
      - kind: other
        ref: "printf 'placa osb 1 un\\n\\n' | uv run python -m strata pesquisar (ao vivo hoje: 'método: API', o curl_cffi passou o DataDome)"
        status: fail
    human_judgment: true
    rationale: "Depende do DataDome bloquear ou não no dia; o caminho está provado pelo teste e2e e pelo --sem-principal, mas o 403 real não apareceu"

duration: 9min
completed: 2026-10-31
status: complete
---

# Phase 2 Plan 02: cadeia API → browser no Chrome dedicado Summary

**Quando o pedido simples de uma loja falha, o mesmo adaptador corre no Chrome dedicado (CDP, porta 9222) dentro do mesmo prazo de 90 s; cada oferta diz o método e a Obramat dá escalões e stock exato pelo browser.**

## Performance

- Duração: 9 min (12:48 a 12:57 UTC, 2026-10-31)
- Tarefas: 3 de 3 (a tarefa 1 já vinha resolvida)
- Ficheiros: 2 criados, 8 alterados

## Accomplishments

- `src/strata/browser.py`: `BrowserFetcher` com `get_json`/`get_html`, os mesmos `Host`, `cache` e `record` do `Fetcher`. Liga-se a `127.0.0.1:9222`; se não houver Chrome, abre o `chrome.exe` com os argumentos do `.claude/claude-chrome.cmd` (lista, sem shell) e fecha-o no fim com `Browser.close`. Se o Chrome já estava aberto, só desliga.
- `search.py`: `_attempt` (1.ª pesquisa, alargada e filtro G-01-5, sem mudar a lógica), `_rungs` e a cadeia em `search_store`. A cadeia segue as regras D-08, D-14, D-15, D-16 e D-17.
- `Offer.method` e "método: API/browser" em cada oferta.
- `--sem-principal LOJA` em `pesquisar` e `verificar` (repetível, `choices` tirados de `search.STORES`).
- `uv run pytest -q`: 255 passed (eram 240).

## Task Commits

1. Tarefa 1, checkpoint dos pacotes: sem commit. Resposta do utilizador, tal e qual: "Aprovado (os dois)". O orquestrador confirmou no PyPI o playwright 1.64.1 (Microsoft Corporation, github.com/Microsoft/playwright-python) e o anthropic 2.3.0 (Anthropic, github.com/anthropics/anthropic-sdk-python). O plano 02-05 pode usar esta aprovação para o `uv add anthropic`.
2. Tarefa 2 (tracer), degrau browser e método por oferta: `e47b392` (feat)
3. Tarefa 3, RED: `5bb1c4d` (test)
4. Tarefa 3, GREEN: `6d16b47` (feat)

## TDD Gate Compliance

- RED `5bb1c4d`: 2 de 14 falharam, `test_sem_principal_salta_a_api` (AssertionError) e `test_sem_principal_na_linha_de_comandos` (SystemExit: opção desconhecida). Os outros 12 cobrem regras que a tarefa 2 já tinha, como o plano previa.
- GREEN `6d16b47`: 14 de 14. REFACTOR não foi preciso.

## Verificação ao vivo

Cinco corridas, todas com a porta 9222 fechada antes e depois, menos a quarta:

1. `placa osb 1 un` sem opções: "Obramat: ok" com "método: API". O `curl_cffi` passou o DataDome, como no 02-01, por isso o browser não foi chamado e a verificação automática da tarefa 2 (que procura "método: browser") falhou nesta forma.
2. Script de rascunho com a Obramat em `browser_only`: 6 ofertas pelo browser, "282 em stock em OBRAMAT Lisboa - Alfragide", escalões "−5% a partir de 120/48/102". O perfil dedicado tem o armazém 201, que a sessão `curl_cffi` não tem. Chrome aberto pela app e fechado no fim.
3. `cimento 1 un --sem-principal allmat`: Allmat "ok", 11 ofertas com "método: browser" e a nota "antes do browser: API: desativado com --sem-principal". A4 confirmado: o JSON da Store API lê-se no Chrome.
4. Chrome dedicado aberto antes da corrida: depois da corrida a porta continuava a responder (200) e havia 1 separador, o mesmo do início. Fechei-o a seguir para repor o estado inicial.
5. `placa osb 1 un --sem-principal obramat` pela linha de comandos real: "Obramat: ok", 5 ofertas com "método: browser", sem avisos no stderr.

## Deviations from Plan

1. Verificação ao vivo da tarefa 2. A verdade "o pedido simples levou 403 e passou ao browser" não se viu ao vivo, porque a Obramat não bloqueou o `curl_cffi` hoje. Provei o mesmo caminho de código com a loja em `browser_only` (corrida 2) e com `--sem-principal obramat` (corrida 5), e o salto 403 → browser está no teste `test_obramat_bloqueada_vai_ao_browser_e_fica_la`. Fica registado no `.planning/WINDOWS.md` como `unmet-truth`. Não houve mudança de código.
2. Para testar o ramo "Chrome já aberto" do D-06, o sandbox recusou correr o `.claude/claude-chrome.cmd` pelo `cmd`. Abri o Chrome dedicado com um script Python que usa o mesmo `CHROME`, `PROFILE` e argumentos do `browser.py`.
3. `--sem-principal` grava `cache["sem_principal"]` dentro de `_with_fetch`, nos dois ramos (testes e sessão real), em vez de no início de cada `work`. O efeito é o mesmo e evita repetir a linha no `_search` e no `verificar`.

## Issues Encountered

- No primeiro RED, os dois transportes falsos (`SimpleNamespace(cache=...)` com a mesma cache) eram iguais por `==` e as asserções sobre o transporte não provavam nada. Cada um ganhou um `kind`. Corrigido antes do commit do RED.

## Known Stubs

None.

## Threat Flags

None. A superfície nova (CDP local, `subprocess.Popen` do Chrome, `--record` no browser) é a do `<threat_model>`. As mitigações estão no código: `grep launch(` e `grep shell=True` sem resultados, só o corpo gravado em disco e `json.loads(..., parse_float=Decimal)`.

## Next Phase Readiness

O 02-03 (desafio do DataDome dentro do browser e `StoreCaptcha`) pode entrar no `_open` do `BrowserFetcher` e no ciclo de degraus. Os planos 02-04 e 02-05 acrescentam degraus a `_rungs`; os testes já comparam o detail por pedaços.

## Self-Check: PASSED

- `src/strata/browser.py` e `tests/test_chain.py` existem.
- Commits `e47b392`, `5bb1c4d` e `6d16b47` estão no HEAD.
- `uv run pytest -q`: 255 passed.
