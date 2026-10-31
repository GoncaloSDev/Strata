---
phase: 02-obramat-e-cadeia-de-recurso
plan: 05
subsystem: cadeia de recurso (degrau IA)
status: complete
tags: [ia, claude-p, anthropic, cadeia, validacao]
requires:
  - "02-04: degrau JSON-LD e cadeia API → JSON-LD → browser"
  - "02-02: BrowserFetcher (Chrome dedicado por CDP) e aprovação do pacote anthropic"
provides:
  - "strata.ai: SCHEMA, PROMPT, page_text, parse_price, offers_from, ask, _ask_claude, _ask_api, rung"
  - "Degrau IA no fim da cadeia: principal → JSON-LD → browser → IA"
  - "BrowserFetcher.get_html(url, params=None, idle=False)"
  - "obras360.PAGE_PRICES_WITHOUT_VAT"
  - "Fixture autouse no_ai em tests/conftest.py"
affects: [search_store, report (método: IA, lido por IA)]
tech-stack:
  added: ["anthropic 2.3.0 (>=2.3,<3)"]
  patterns:
    - "Um esquema JSON partilhado pelos dois motores (API e claude -p)"
    - "Saída da IA tratada como dado não confiável: preço tem de estar no texto, link https no host da loja"
key-files:
  created:
    - src/strata/ai.py
    - tests/test_ai.py
  modified:
    - src/strata/search.py
    - src/strata/browser.py
    - src/strata/stores/obras360.py
    - tests/conftest.py
    - tests/test_chain.py
    - pyproject.toml
    - uv.lock
key-decisions:
  - "Degrau IA corre no transporte do browser (a página de pesquisa da Bricomarché e da Obras 360 é montada com JavaScript); sem browser o motivo é 'IA: sem browser nesta execução'"
  - "Motor da API: messages.create com output_config {format: json_schema, effort: low}, confirmado pelo skill claude-api; max_tokens 4096 em vez de 2048 porque o Haiku 5.5 pensa por omissão"
  - "Recusa (stop_reason refusal) e resposta cortada (max_tokens) viram motivo legível em vez de JSON partido"
  - "Ofertas IA com raw 0 (a IA não viu nada ou tudo rejeitado) dão 'sem resultados' com a nota das rejeitadas"
requirements-completed: [STORE-06]
duration: 9 min
completed: 2026-10-31
estimate:
  tokens: 65000
  tasks: 2
actuals:
  tokens: 6100
  tasks: 2
  commits: 3
plan_head_before: edfa7b8597eb514dfd4d796521c05e94b6d564f5
plan_head_after: fe4d5e8a4da53d0329f84c346cd99ab1f7bb3e88
coverage:
  - deliverable: "Degrau IA ponta a ponta: todos os degraus falham, a IA lê a página e a oferta sai com 'método: IA' e 'lido por IA'"
    human_judgment: false
    verification:
      - kind: test
        ref: "tests/test_ai.py#test_ponta_a_ponta_todos_os_degraus_falham_e_a_ia_le_a_pagina"
        status: pass
  - deliverable: "Validação das ofertas IA (preço no texto, > 0, https no host da loja, filtro de título, máx. 5)"
    human_judgment: false
    verification:
      - kind: test
        ref: "tests/test_ai.py#test_offers_from_rejeita_e_conta"
        status: pass
      - kind: test
        ref: "tests/test_ai.py#test_offers_from_no_maximo_5"
        status: pass
  - deliverable: "D-09 (IA no fim da loja) e D-10 (1 chamada por item e loja)"
    human_judgment: false
    verification:
      - kind: test
        ref: "tests/test_chain.py#test_oferta_ia_fica_depois_da_estruturada_mesmo_mais_barata"
        status: pass
      - kind: test
        ref: "tests/test_chain.py#test_degrau_ia_uma_so_chamada_sem_pesquisa_alargada"
        status: pass
  - deliverable: "Motores: claude -p (sem shell, sem ferramentas, texto pelo stdin) e API com chave"
    human_judgment: false
    verification:
      - kind: test
        ref: "tests/test_ai.py#test_ask_claude_sem_shell_sem_ferramentas_texto_pelo_stdin"
        status: pass
      - kind: test
        ref: "tests/test_ai.py#test_ask_api_saida_estruturada_com_o_esquema"
        status: pass
  - deliverable: "Leitura real de páginas pela IA e autenticação da conta Pro no claude -p"
    human_judgment: true
    rationale: "Os testes trocam o motor por um falso; o login da conta Pro (e a chave, se existir) só vive no terminal do utilizador"
---

# Phase 2 Plan 5: Degrau IA Summary

**Último degrau da cadeia: a página de pesquisa da loja, lida no Chrome dedicado, vai ao `claude -p` (conta Pro) ou à API Haiku 5.5 com esquema JSON; as até 5 ofertas só entram com o preço presente no texto e o link https na loja, e saem marcadas "lido por IA", sempre depois das estruturadas.**

Início 2026-10-31T13:22:12Z, fim 2026-10-31T13:31Z (~9 min). 2 tarefas, 9 ficheiros.

## Accomplishments

- `src/strata/ai.py`: `page_text` (links como "texto <URL absoluto>", sem script/style, cortado a 20 000), `parse_price` (formatos PT e ponto decimal), `offers_from` (validação T-02-18, máx. 5, filtro de título, IVA da loja), `ask` (API com chave, senão `claude -p`, senão "IA não configurada (sem ANTHROPIC_API_KEY nem claude no PATH)").
- `_ask_claude`: `create_subprocess_exec` com lista de argumentos, `--json-schema`, `--tools ""`, `--no-session-persistence`, `--system-prompt`, pasta temporária vazia, texto pelo stdin; `.cmd`/`.bat` recusados; o processo é morto se o prazo de 90 s cancelar o degrau.
- `_ask_api`: `AsyncAnthropic().messages.create(model="claude-haiku-5-5", output_config={"format": {"type": "json_schema", "schema": SCHEMA}, "effort": "low"})`, sem ferramentas; erros da API, recusa, corte e JSON inválido viram "IA (API): …".
- `search.py`: degrau `("IA", ai.rung(store), browser)` no fim (também em `browser_only`), sem pesquisa alargada, nota "antes da IA: …", e a chave de ordenação põe `o.method == "IA"` primeiro (D-09).
- `browser.py`: `get_html(..., idle=True)` espera até 5 s pelo `networkidle` e segue com o que houver.
- Obras 360: `PAGE_PRICES_WITHOUT_VAT = True`; as ofertas IA levam +23% e a evidência "página da loja sem IVA, +23%".

## O que o skill `claude-api` confirmou

- `output_config={"format": {"type": "json_schema", "schema": …}}` em `messages.create` é a forma atual (o `output_format` está obsoleto); o texto lê-se com `next(b.text for b in r.content if b.type == "text")` e `json.loads`.
- `effort` fica dentro de `output_config` (GA, sem beta); no Haiku 5.5 o padrão é `medium`, por isso fica `low` explícito.
- ID `claude-haiku-5-5` ($0,10 / $0,50 por MTok). O Haiku 5.5 pensa por omissão (adaptativo), e o pensamento conta para o `max_tokens`: daí 4096 em vez de 2048.
- O Haiku 5.5 não tem fallback do lado do servidor em recusas: tratei `stop_reason == "refusal"` como motivo.
- O `anthropic` 2.3.0 instalado tem `output_config` na assinatura de `AsyncMessages.create` (confirmado com `inspect`).

## Task Commits

| Tarefa | Commit | Mensagem |
|---|---|---|
| 1 (tracer) | 17da420 | feat(02-05): degrau IA no fim da cadeia, pelo claude -p |
| 2 RED | 4003fda | test(02-05): motor da API, IVA da página da Obras 360 e regras D-09/D-10/D-11 |
| 2 GREEN | fe4d5e8 | feat(02-05): motor da API com ANTHROPIC_API_KEY e IVA da página da Obras 360 |

## TDD Gate Compliance

Tarefa 2: RED (4003fda) com 7 testes a falhar (motor da API e IVA da Obras 360); GREEN (fe4d5e8) com a suite toda verde (335). Os testes do corte a 5, de D-09 e de D-10 já passavam no RED, porque a tarefa 1 (tracer) implementou essas regras como o plano mandava; ficam como testes de regressão. Sem REFACTOR.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Testes da cadeia esperavam o browser como último degrau**
- **Found during:** Tarefa 1
- **Issue:** 3 testes de `test_chain.py` comparavam o `detail` terminado em "browser: x"; com o degrau IA, o browser falso (`SimpleNamespace` sem `get_html`) dava "IA: AttributeError: …".
- **Fix:** `transports()` ganhou um `get_html` que devolve uma página vazia, e os 3 testes esperam "; IA: IA desligada nos testes" no fim.
- **Files modified:** tests/test_chain.py
- **Commit:** 17da420

**2. [Rule 2 - Crítico] Recusa e resposta cortada na API**
- **Found during:** Tarefa 2 (skill `claude-api`)
- **Issue:** o plano só tratava `APIError` e JSON inválido; uma recusa ou um corte por `max_tokens` dava "resposta sem JSON", sem dizer porquê.
- **Fix:** motivos próprios para `stop_reason` `refusal` e `max_tokens`; `max_tokens` subiu para 4096 porque o Haiku 5.5 pensa por omissão.
- **Files modified:** src/strata/ai.py
- **Commit:** fe4d5e8

**3. [Rule 2 - Crítico] Saída do `claude -p` que não é JSON**
- **Found during:** Tarefa 1
- **Issue:** o plano lia `json.loads(stdout)` sem tratar uma saída vazia ou texto (ex.: erro antes do JSON).
- **Fix:** `StoreError("IA (claude -p): saída não é JSON (<início do stderr>)")`.
- **Files modified:** src/strata/ai.py
- **Commit:** 17da420

**Total deviations:** 3 auto-fixed (1 bug, 2 críticos). **Impact:** sem mudança de âmbito; só motivos de falha mais claros.

## Human checks (por fazer, no terminal do utilizador)

1. `echo teste | claude -p --model haiku --output-format json` → esperado `"is_error": false`. Não corrido: o `claude -p` lançado de dentro de uma sessão de agente deu "OAuth session expired" na pesquisa. Neste PC o `claude` está em `C:\Users\gonca\.local\bin\claude.EXE` (um .exe, por isso não é recusado como .cmd).
2. `uv run python -c "import asyncio; from strata import ai; print(asyncio.run(ai.ask('Placa OSB 12 mm 28,50 € <https://www.obramat.pt/produtos/placa-osb-1.html>')))"` → esperado uma oferta com "28,50 €". Não corrido: `ANTHROPIC_API_KEY` não está definida no ambiente deste executor (sem a chave, a app usa o `claude -p` e o check 1 aplica-se).

## Known Stubs

Nenhum.

## Threat Flags

Nenhuma superfície nova fora do `<threat_model>`: T-02-17 a T-02-21 estão mitigados no código e cobertos pelos testes (sem shell, `.cmd` recusado, texto pelo stdin, preço no texto, host da loja, máx. 5, 1 chamada por item e loja). `grep -rn "credentials\|shell=True" src/strata` não devolve nada.

## Next Phase Readiness

Cadeia completa: principal → JSON-LD → browser → IA. Pronto para o 02-06. A qualidade da leitura em páginas reais (sobretudo os preços por m² da Obras 360) só se vê ao vivo.

## Self-Check: PASSED

- FOUND: src/strata/ai.py, tests/test_ai.py
- FOUND: 17da420, 4003fda, fe4d5e8 (ancestrais de HEAD)
- `uv run pytest -q`: 335 passed
