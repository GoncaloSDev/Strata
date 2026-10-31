---
phase: 02-obramat-e-cadeia-de-recurso
plan: 03
subsystem: search
tags: [datadome, captcha, cadeia-de-recurso, playwright, abrir-a-mao]

requires:
  - phase: 02-02
    provides: "BrowserFetcher no Chrome dedicado, cadeia API → browser em search_store, cache partilhada"
provides:
  - "strata.fetch: StoreCaptcha(StoreBlocked), DD, challenge_kind; Fetcher distingue CAPTCHA de verificação do dispositivo no 403"
  - "strata.models: Status 'abrir à mão' e StoreResult.link"
  - "strata.browser.past_challenge(read, wait_s=10.0, step=0.5)"
  - "search_page(query) nas 4 lojas fixas"
  - "Chaves de cache 'captcha' (nomes de loja) e 'captcha_hosts' (hosts, partilhada pelo Fetcher e pelo BrowserFetcher)"
  - "Linha 'abrir à mão: <link>' no relatório"
affects: [02-04, 02-05, 02-06]

actuals:
  tokens: 5800  # chars/4 do diff de src/ e tests/ (23 227 caracteres)
  tasks: 2
  commits: 3
plan_head_before: bb2e424337cd8c947ffa1636eb31a63ed69f01de
plan_head_after: 7f53b06a0476758edbcd71bba06521202727c88b

tech-stack:
  added: []
  patterns:
    - "O CAPTCHA é uma exceção própria (StoreCaptcha) que a cadeia apanha antes do StoreBlocked e que os 'except StoreError' dos adaptadores deixam subir"
    - "Guarda no transporte: um host com CAPTCHA recusa os pedidos que já estavam em fila"
    - "past_challenge recebe só uma função de leitura: testa-se sem Playwright a correr"

key-files:
  created:
    - tests/test_fetch.py
    - tests/fixtures/obramat_curl-403-datadome.html
  modified:
    - src/strata/fetch.py
    - src/strata/models.py
    - src/strata/search.py
    - src/strata/report.py
    - src/strata/browser.py
    - src/strata/stores/obramat.py
    - src/strata/stores/allmat.py
    - src/strata/stores/bricomarche.py
    - src/strata/stores/obras360.py
    - tests/test_chain.py

key-decisions:
  - "StoreCaptcha herda de StoreBlocked (decisão do plano): quem só conhece StoreBlocked trata-o como bloqueio; a cadeia testa StoreCaptcha primeiro"
  - "O Fetcher e o BrowserFetcher recusam pedidos a um host que já deu CAPTCHA (cache['captcha_hosts']), além da regra por loja em search_store"
  - "No browser, uma falha de leitura do Playwright durante a verificação conta como 'ainda a carregar' e marca que houve desafio"

requirements-completed: [STORE-04, STORE-06]

coverage:
  - id: D1
    description: "CAPTCHA da Obramat no pedido simples: 'abrir à mão — CAPTCHA em API: …' com o link da pesquisa; o item seguinte diz 'CAPTCHA antes nesta execução' com o seu link; 1 só pedido à Obramat em 2 itens, browser sem chamadas; a Allmat responde nos dois"
    requirement: STORE-04
    verification:
      - kind: e2e
        ref: "tests/test_chain.py#test_captcha_obramat_abrir_a_mao_e_lista_continua"
        status: pass
    human_judgment: false
  - id: D2
    description: "Um 403 com 'rt':'i' é 'bloqueada' com 'HTTP 403 (verificação DataDome)' e nunca CAPTCHA"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_chain.py#test_verificacao_do_dispositivo_nao_e_captcha"
        status: pass
      - kind: unit
        ref: "tests/test_fetch.py#test_verificacao_do_dispositivo_e_bloqueio_e_nao_captcha"
        status: pass
    human_judgment: false
  - id: D3
    description: "No browser: verificação que passa sozinha é esperada; CAPTCHA dá StoreCaptcha; verificação presa dá 'não passou em N s'; página a recarregar não rebenta"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_fetch.py (5 testes past_challenge)"
        status: pass
      - kind: other
        ref: "printf 'placa osb 1 un\\n\\n' | uv run python -m strata pesquisar --sem-principal obramat (ao vivo: 'Obramat: ok', 'método: browser', escalões e stock lidos)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Link 'abrir à mão' das 4 lojas e CAPTCHA no degrau browser da Allmat"
    requirement: STORE-06
    verification:
      - kind: unit
        ref: "tests/test_chain.py#test_search_page_das_4_lojas"
        status: pass
      - kind: unit
        ref: "tests/test_chain.py#test_captcha_no_browser_da_allmat"
        status: pass
    human_judgment: false
  - id: D5
    description: "Um CAPTCHA real da DataDome visto ao vivo"
    requirement: STORE-04
    verification: []
    human_judgment: true
    rationale: "Não se provoca a pedido; a prova é o Fetcher real sobre o corpo real do 403 com 'rt':'c'. A2 ('rt':'c' = CAPTCHA) vem de fontes de terceiros"

duration: 5min
completed: 2026-10-31
status: complete
---

# Phase 2 Plan 03: CAPTCHA dá "abrir à mão" com o link, e a loja pára Summary

**Ao primeiro CAPTCHA da DataDome, a loja fica "abrir à mão" com o link da sua página de pesquisa, nesse item e nos seguintes, sem mais pedidos. A verificação do dispositivo ('rt':'i') escala para o browser, que espera até 10 s que ela passe sozinha sem tocar na página.**

## Performance

- Duração: 5 min (13:01 a 13:06 UTC, 2026-10-31)
- Tarefas: 2 de 2
- Ficheiros: 2 criados, 10 alterados

## Accomplishments

1. `fetch.py`: `StoreCaptcha`, `challenge_kind` e o 403 classificado em CAPTCHA, verificação ou bloqueio simples.
2. `search.py`: `except StoreCaptcha` antes do `except StoreBlocked`; `cache["captcha"]` faz os itens seguintes responderem sem pedidos.
3. `browser.py`: `past_challenge` só lê a página (o grep de `.click(`, `.fill(`, `.type(` e `mouse.` não devolve nada). O estado HTTP da 1.ª resposta só conta quando não houve verificação.
4. `search_page` nas 4 lojas, com o produto por `urlencode`. O link passa por `clean()` antes de ir para o terminal.
5. `uv run pytest -q`: 273 passed (eram 255).

## Task Commits

1. Tarefa 1 (tracer), ponta a ponta do CAPTCHA na Obramat: `8c09654` (feat)
2. Tarefa 2, RED: `3ae0468` (test)
3. Tarefa 2, GREEN: `7f53b06` (feat)

Gate do tracer: verificação automática corrida outra vez depois do commit, 2 passed com `-k captcha` e a suite toda verde.

## TDD Gate Compliance

- RED `3ae0468`: `tests/test_fetch.py` não carregava (ImportError: `past_challenge` não existe) e 4 testes do `test_chain.py` falharam (AttributeError: `search_page` em falta na Allmat, Bricomarché e Obras 360).
- GREEN `7f53b06`: 11 de 11 em `test_fetch.py` e 21 de 21 em `test_chain.py`. REFACTOR não foi preciso.

## Verificação ao vivo

- `placa osb 1 un --sem-principal obramat`: "Obramat: ok", 6 ofertas com "método: browser", "282 em stock em OBRAMAT Lisboa - Alfragide", escalões lidos. Isto confirma que o `get_html` com `past_challenge` funciona numa página real. 1 pesquisa e 3 páginas de produto.
- Porta 9222 fechada antes e depois da corrida, como estava.
- Não apareceu nenhum CAPTCHA nem verificação ao vivo. As regras ficam provadas por testes sobre o corpo real do 403.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Correção] Pedidos já em fila não saem depois de um CAPTCHA**
- Encontrado na tarefa 1.
- Problema: a regra por loja em `search_store` só trava o item seguinte. Dentro da mesma pesquisa, as páginas de produto da Obramat ficam em fila no `Host` (1 de cada vez) e sairiam depois do CAPTCHA. Isso fura a proibição "nunca voltar a pedir nada a uma loja depois de um CAPTCHA".
- Correção: `cache["captcha_hosts"]`. O `Fetcher.get` e o `BrowserFetcher._open` levantam `StoreCaptcha("CAPTCHA antes nesta execução")` sem fazer o pedido quando o host já deu CAPTCHA. A cache é a mesma nos dois transportes.
- Ficheiros: `src/strata/fetch.py`, `src/strata/browser.py`. Teste: `tests/test_fetch.py#test_captcha_no_pedido_simples_e_depois_nenhum_pedido` (1 pedido em 2 chamadas).
- Commits: `8c09654`, `7f53b06`.

**2. [Rule 1 - Correção] CAPTCHA num 403 de JSON no browser**
- O plano pedia o `challenge_kind` só quando o corpo não é JSON. Com um 403, o `_open` levantaria `StoreBlocked` antes de chegar lá. Passei a verificação para a leitura do corpo no `get_json`, antes do estado HTTP.
- Ficheiro: `src/strata/browser.py`. Commit: `7f53b06`.

## Issues Encountered

- Um heredoc do bash transformou `\\n` em quebras de linha reais no 1.º rascunho dos testes da tarefa 1. Reescrevi o bloco com o Edit antes do commit.

## Known Stubs

None.

## Threat Flags

None. A superfície é a do `<threat_model>`: T-02-11 (o browser só lê), T-02-12 (nenhum pedido depois do CAPTCHA, agora também no transporte) e T-02-13 (`urlencode` mais `clean()`).

## Next Phase Readiness

Os degraus novos dos planos 02-04 e 02-05 herdam a regra sem mudanças: qualquer `StoreCaptcha` num degrau acaba a cadeia dessa loja, e o transporte recusa novos pedidos ao host. Um degrau que não passe pelo `Fetcher` nem pelo `BrowserFetcher` (por exemplo, uma chamada à IA sobre texto já lido) não faz pedidos à loja, por isso não precisa da guarda.

## Self-Check: PASSED

- `tests/test_fetch.py` e `tests/fixtures/obramat_curl-403-datadome.html` existem.
- Commits `8c09654`, `3ae0468` e `7f53b06` estão no HEAD.
- `uv run pytest -q`: 273 passed.
