---
phase: 02-obramat-e-cadeia-de-recurso
verified: 2026-10-31T14:40:39Z
status: human_needed
score: 50/54 must-haves verified
covered_files:
  - ".planning/WINDOWS.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-01-PLAN.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-01-SUMMARY.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-02-PLAN.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-02-SUMMARY.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-03-PLAN.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-03-SUMMARY.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-04-PLAN.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-04-SUMMARY.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-05-PLAN.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-05-SUMMARY.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-06-PLAN.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-06-SUMMARY.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-07-PLAN.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-07-SUMMARY.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-REVIEW-DISPOSITION.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-REVIEW.md"
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/deferred-items.md"
  - "README.md"
  - "pyproject.toml"
  - "src/strata/__main__.py"
  - "src/strata/ai.py"
  - "src/strata/browser.py"
  - "src/strata/fetch.py"
  - "src/strata/jsonld.py"
  - "src/strata/models.py"
  - "src/strata/report.py"
  - "src/strata/search.py"
  - "src/strata/stores/allmat.py"
  - "src/strata/stores/bricomarche.py"
  - "src/strata/stores/obramat.py"
  - "src/strata/stores/obras360.py"
  - "tests/conftest.py"
  - "tests/fixtures/allmat_product-page_liz-branco_jsonld.html"
  - "tests/fixtures/allmat_products_search-cimento.json"
  - "tests/fixtures/allmat_search-page_cimento.html"
  - "tests/fixtures/obramat_curl-403-datadome.html"
  - "tests/fixtures/obramat_product-osb-18_ctx201_tiers.html"
  - "tests/fixtures/obramat_product-tijolo_ctx201_tiers.html"
  - "tests/fixtures/obramat_search-cimento-cola_endcap_browser.html"
  - "tests/fixtures/obramat_search-no-results_browser.html"
  - "tests/fixtures/obramat_search-osb_browser.html"
  - "tests/test_ai.py"
  - "tests/test_chain.py"
  - "tests/test_e2e.py"
  - "tests/test_fetch.py"
  - "tests/test_jsonld.py"
  - "tests/test_obramat.py"
  - "tests/test_obras360.py"
  - "tests/test_search.py"
covered_digest: "v3:sha256:34a1002d5c976012e0ca052e3d538cbbb4264d8152aeed6935d2c055c4bff4d2"
behavior_unverified: 1
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 42/48
  gaps_closed:
    - "SC2 / D-16: se todos os degraus falharem, a loja aparece como falhada com o motivo (CR-01)"
    - "02-05 / D-11: a IA devolve até 5 ofertas com preço e link tirados da página; prohibition 'Nunca aceitar da IA um preço que não está no texto da página nem um link para fora da loja' (CR-02 + WR-07)"
  gaps_remaining: []
  regressions: []
advisory: []
behavior_unverified_items:
  - truth: "02-02 / D-06: se o Chrome dedicado não estava a correr, a app abre-o e fecha-o no fim; se já estava aberto, fica aberto e só os separadores da app fecham"
    test: "Com a porta 9222 fechada, correr 'printf \"placa osb 1 un\\n\\n\" | uv run python -m strata pesquisar' e ver http://127.0.0.1:9222/json/version antes e depois; repetir com o Chrome dedicado aberto por .claude\\claude-chrome.cmd"
    expected: "1.º caso: porta fechada antes e depois. 2.º caso: porta aberta depois, com os mesmos separadores do início"
    why_human: "Nenhum teste exercita BrowserFetcher.close nem _opened (browser.py sem mudanças desde a verificação anterior). O WR-03 continua aberto: há um caminho (Popen correu, ligação falhou) em que o Chrome aberto pela app fica aberto"
human_verification:
  - test: "Correr de novo a folha de 10 itens e o verificar, com cronómetro: 'Measure-Command { uv run python -m strata pesquisar <folha-10-itens>.xlsx }' e 'uv run python -m strata verificar'"
    expected: "Folha: menos de 300 s, 10 cabeçalhos 'Linha N', 4 linhas de estado por item. verificar: rc=0 e 5 linhas OK, a da Obramat com 'método: browser'"
    why_human: "Os 222,8 s e o rc=0 em 62 s estão só no 02-06-SUMMARY, sem log gravado. Correr 4 min com rede e o Chrome dedicado não cabe numa verificação automática. É a prova do LIST-03"
  - test: "Decidir se o caminho 'API: HTTP 403 → browser' da Obramat (WINDOWS.md #2) fica aceite pelo teste test_obramat_bloqueada_vai_ao_browser_e_fica_la e pela corrida com --sem-principal obramat, ou se espera por um 403 real"
    expected: "Decisão registada: 'gsd-tools windows waive 2 \"<motivo>\"' ou manter aberto"
    why_human: "O DataDome não bloqueou o curl_cffi em nenhuma corrida; o 403 real não se pode forçar"
  - test: "Confirmar a regra nova do 02-06: uma resposta da Obramat com a nota NO_STORE vinda de um degrau sem browser salta para o browser (não está no D-14)"
    expected: "O utilizador aceita (fica como emenda ao D-14/D-18 no CONTEXT) ou pede outra regra"
    why_human: "Muda as regras de escalada acordadas no discuss-phase; só o utilizador decide"
  - test: "Prova ao vivo do degrau IA pelo claude -p: 'printf \"placa osb 1 un\\n\\n\" | uv run python -m strata pesquisar --sem-principal obramat' com o browser a falhar de propósito (ex.: Chrome dedicado com a porta ocupada)"
    expected: "A Obramat aparece com ofertas 'método: IA' e 'lido por IA' no fim, ou falhada com o motivo de cada degrau a acabar em 'IA: …'; nunca 'sem resultados'"
    why_human: "O degrau IA nunca correu ao vivo. A validação nova (link no texto, preço junto do link) só foi exercitada com respostas falsas. A forma output_config da API também não tem teste contra o SDK real (IN-02)"
  - test: "Decidir sobre o título da oferta IA, que não é validado contra a página: aceitar como risco (a oferta sai 'lido por IA' e no fim da loja) ou abrir um gap pequeno"
    expected: "Decisão registada. Se for gap: exigir que o título venha no texto logo antes de '<URL>' (o page_text escreve 'TÍTULO <URL>') e juntar um teste com o título de outro produto"
    why_human: "Reproduzido com a página gravada 'osb': o link e o preço da 'TINTA PARA PISCINAS … 4L AZUL' (33,60 €) com o título 'PLACA OSB 3 250X125X1,8CM' é aceite e mostrado como oferta de OSB, porque o filtro de título (D-15) corre sobre o título que a IA escreveu. A must-have 02-05 diz 'título, preço e link tirados da página'; o 02-07 só ancorou o link e o preço. Fica fora dos gaps anteriores, por isso a decisão é do utilizador"
  - test: "Rever as 5 proibições judgment (lista na secção 'Proibições'): veredito do verificador é cumpridas, não autoritativo"
    expected: "O utilizador confirma ou aponta a que falha"
    why_human: "Proibições de tipo judgment pedem resolução humana"
---

# Phase 2: Obramat e cadeia de recurso Verification Report

**Phase Goal:** As 4 lojas fixas respondem na hora para uma lista inteira em menos de 5 minutos, e uma loja que falha pelo método principal é tentada por outras vias antes de ser marcada como falhada
**Verified:** 2026-10-31T14:40:39Z
**Status:** human_needed
**Re-verification:** Sim, depois do plano de correção 02-07

Resposta curta: os dois gaps bloqueantes estão fechados, e confirmei-o com scripts meus, não pelo SUMMARY. Com tudo em falha e a IA sem ofertas válidas, a loja sai `bloqueada` com o motivo de cada degrau. A IA já não consegue meter um link inventado, um url vazio, o preço do vizinho, "12.5" nem "1e3". Faltam só verificações humanas, mais uma decisão nova: o título da oferta IA não é validado (ver item humano 5).

Nota MVP: a fase tem `Mode: mvp`, mas o objetivo não está no formato "As a …, I want to …, so that …". Segui o precedente da fase 1 e verifico o objetivo tal como está escrito. Para o formato certo: `/gsd-mvp-phase 2`.

## User Flow Coverage

| Passo | Esperado | Evidência | Estado |
|-------|----------|-----------|--------|
| 1. Passar a folha à linha de comandos | Cada item procurado nas 4 lojas | `search.STORES` com as 4; `run` faz `gather` das 4 por item | ✓ |
| 2. Obramat pela pesquisa do site | Ofertas com IVA, Alfragide, 1 pedido de cada vez | `obramat.search`; `LIMITS["www.obramat.pt"] == (1, 3.0, 2.0)` | ✓ |
| 3. CAPTCHA | "abrir à mão" com link, sem mais pedidos, lista continua | `test_captcha_obramat_abrir_a_mao_e_lista_continua` | ✓ |
| 4. Método principal falha | JSON-LD → browser → IA, método em cada oferta | `_rungs`; `test_ordem_api_json_ld_browser` | ✓ |
| 5. Tudo falha | Loja falhada com o motivo | Reproduzido: `status='bloqueada'`, detail com os 4 degraus a acabar em `IA: IA não leu nenhuma oferta válida na página` | ✓ (era ✗) |
| 6. 10 itens em < 5 min | 4 estados por item, < 300 s | Código certo; os 222,8 s só existem no 02-06-SUMMARY | ? |

## Goal Achievement

### Estado dos gaps anteriores

| Gap anterior | Estado agora | Evidência (corrida minha) |
|--------------|--------------|---------------------------|
| CR-01: IA vazia ou toda rejeitada → "sem resultados" | ✓ FECHADO | `search_store` com API `StoreBlocked("HTTP 403")`, browser `StoreError("layout mudou")` e `ask` falso. IA `[]`: `bloqueada`, detail `API: HTTP 403; JSON-LD: página montada com JavaScript, sem links de produto; browser: layout mudou; IA: IA não leu nenhuma oferta válida na página`. IA só com uma linha rejeitada: o mesmo, mais `; 1 ofertas da IA rejeitadas (…)`. `ai.py:118-119` levanta `StoreError`; `search.py` sem mudanças (`git diff adc3527 HEAD -- src/strata/search.py` vazio) |
| CR-02 + WR-07: link inventado, url vazio, preço de outro sítio, "12.5" → 125 € | ✓ FECHADO | Texto da verificação anterior (`… 28,50 € 1 resultado pagina 2 12.5`): link inventado a "2" → rejeitado; url vazio a "12.5" → rejeitado; os dois juntos → `StoreError … 2 ofertas da IA rejeitadas`. Página gravada "osb": link do produto i com o preço do i+1 → rejeitado nos 6 pares; `?page=2`, `http://`, outro host → rejeitados. `parse_price`: `12.5`→None, `1e3`→None, `NaN`→None, `-5`→None, `0,00`→None, `62 €`→62, `1 299,60 €`→1299.60 |

### Observable Truths

Critérios do ROADMAP primeiro, depois os must_haves dos 7 planos (duplicados retirados: 02-02 #7 está no SC2, 02-06 #4 é o SC3, 02-07 #1 é o SC2). Verdades que passaram antes e cujos ficheiros não mudaram: só verificação de regressão (suite verde, 360 passed).

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| SC1 | Obramat pela pesquisa direta, um pedido de cada vez; ao 1.º CAPTCHA "abrir à mão" com o link e a lista continua | ✓ VERIFIED | Sem mudanças; testes do ritmo e do CAPTCHA passam |
| SC2 | Principal falha → JSON-LD, browser e IA por esta ordem, método em cada oferta; se todos falharem, loja falhada com o motivo | ✓ VERIFIED | Era ✗. `ai.py:118-119`; reproduzido acima; `test_ia_so_com_ofertas_rejeitadas_loja_falha_com_o_motivo_de_cada_degrau`, `test_degrau_ia_uma_so_chamada_sem_pesquisa_alargada` (agora `bloqueada`) passam |
| SC3 | Folha de 10 itens nas 4 lojas em < 5 min, 4 estados por item, verificar cobre as 4 | ? UNCERTAIN | Tempo só no 02-06-SUMMARY (item humano 1) |
| 01.1–01.10 | Obramat: lista principal, `ise_number_result`, filhos diretos, IVA incoerente, K = 3, escalões, NO_STORE, LIMITS, Alfragide, README legal (10 verdades) | ✓ VERIFIED | Sem mudanças em `obramat.py`/`fetch.py`/`README.md`; testes passam |
| 02.1 | Ao vivo: 403 do DataDome → "método: browser" | ? UNCERTAIN | 403 real nunca visto (item humano 2) |
| 02.2 | Browser por CDP a 127.0.0.1:9222, perfil dedicado, nunca `launch()` | ✓ VERIFIED | Sem mudanças |
| 02.3 | Abre o Chrome se preciso e fecha-o; se já estava aberto, fica | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Ligado em `__main__.py`; nenhum teste o exercita |
| 02.4–02.6, 02.8–02.10 | D-08, método por oferta, sem escalada em "sem resultados", prazo de 90 s, `--sem-principal`, checkpoint de pacotes (6 verdades) | ✓ VERIFIED | Sem mudanças; testes passam; `pesquisar --help` mostra `--sem-principal` |
| 03.1–03.6 | Regras do CAPTCHA nas 4 lojas (6 verdades) | ✓ VERIFIED | Sem mudanças; testes passam |
| 04.1–04.7 | Degrau JSON-LD (7 verdades) | ✓ VERIFIED | Sem mudanças; testes passam |
| 05.1 | IA devolve até 5 ofertas com título, preço e link tirados da página, "método: IA" + "lido por IA" | ✓ VERIFIED | Era ✗. Link e preço ancorados (`ai.py:95-104`). Ressalva: o título não é validado (item humano 5, Warning) |
| 05.2–05.8 | IA no fim da loja, 1 chamada, regras, IVA, motor D-12, OAuth, testes sem IA (7 verdades) | ✓ VERIFIED | Motor sem mudanças (hunks do diff só em constantes, `parse_price` e `offers_from`); 05.4 agora com as regras novas |
| 06.1 | Ao vivo: `verificar` rc=0 e 5 OK com método | ? UNCERTAIN | Só no SUMMARY (item humano 1) |
| 06.2, 06.3, 06.5, 06.6 | Canário Obramat, canário IA falha, K/LIMITS/prazo, README (4 verdades) | ✓ VERIFIED | Sem mudanças |
| 07.2 | Terminal: `  Obramat: bloqueada — API: HTTP 403; JSON-LD: HTTP 403; browser: página da Obramat sem lista de resultados (layout mudou?); IA: IA não leu nenhuma oferta válida na página` | ✓ VERIFIED | `test_ponta_a_ponta_ia_sem_ofertas_validas_loja_falha_com_o_motivo` (2 casos) passa via `main(["pesquisar"])` |
| 07.3 | IA válidas todas escondidas pelo filtro → "ok" com "0 ofertas mostradas; N escondidas" (D-14) | ✓ VERIFIED | `valid` conta antes do filtro (`ai.py:105-107`); `search.py:140-142`; `test_offers_from_titulo_que_nao_bate_fica_escondido` (raw 1, hidden 1) |
| 07.4 | Oferta IA só com `<URL>` no texto e o preço, por valor, entre os preços em € dos 300 caracteres a seguir à 1.ª ocorrência; vizinho, link inventado, url vazio e página de pesquisa rejeitados e contados | ✓ VERIFIED | `ai.py:95-104`; reproduzido (6 pares de vizinhos, `?page=2`, http, outro host); `test_offers_from_rejeita_o_que_nao_esta_junto_do_link` (7 casos) |
| 07.5 | `parse_price` só formatos reais; "12.5", "1e3", "abc", "0,00", "" → None | ✓ VERIFIED | Corrida minha (12 entradas, acima); `test_parse_price` |
| 07.6 | Ofertas reais das páginas gravadas passam (Obramat 7 + 18, Allmat 3) | ✓ VERIFIED | `test_offers_from_aceita_as_ofertas_reais_das_paginas_gravadas`, `…_da_allmat` passam; confirmei os 7 produtos da "osb" à mão |
| 07.7 | `ask`, `_ask_api`, `_ask_claude`, `SCHEMA`, `PROMPT`, `MODEL` iguais; `test_ask_*` sem alterações | ✓ VERIFIED | `git diff adc3527 HEAD -- src/strata/ai.py`: 4 hunks, nenhum nestas funções; em `tests/test_ai.py` nenhum hunk toca em `test_ask_*` |

**Score:** 50/54 verdades verificadas (1 presente mas com o comportamento por testar; 3 por confirmar; 0 falhadas)

### Proibições

| Proibição | Tipo | Estado |
|-----------|------|--------|
| Obramat: nunca mais de 1 pedido nem menos de 3 s; nunca repetir pedido bloqueado em ciclo | test | ✓ `test_ritmo_da_obramat` (WR-02 continua aberto, não é ciclo) |
| Nunca contornar o DataDome no pedido simples | judgment | Veredito do verificador: cumprida — por confirmar |
| Nunca mostrar produtos do carrossel / bloco promocional | test | ✓ |
| Nunca o Chrome pessoal nem browser sem janela | judgment | Veredito do verificador: cumprida — por confirmar |
| Nunca deixar aberto o Chrome que a app abriu nem fechar o do utilizador | test | ⚠️ **unverified-prohibition**: nenhum teste ligado (WR-03) |
| Nunca escalar com "sem resultados" | test | ✓ `test_sem_resultados_nao_escala` |
| Nunca resolver/esperar/contornar um CAPTCHA | test | ✓ |
| Nunca voltar a pedir a uma loja depois de um CAPTCHA | test | ✓ |
| Nunca ler JSON-LD sem IVA nem fora de EUR | test | ✓ |
| Nunca preço IA sem marca nem à frente | test | ✓ |
| Nunca reutilizar o token OAuth | judgment | Veredito do verificador: cumprida — por confirmar |
| Nunca aceitar da IA um preço fora do texto nem link fora da loja (02-05) | test | ✓ era violada; agora `test_offers_from_rejeita_o_que_nao_esta_junto_do_link`, `test_offers_from_caso_da_verificacao_falha_o_degrau` |
| Nunca mostrar "sem resultados" quando o degrau IA não leu nenhuma oferta válida (02-07) | test | ✓ teste ponta a ponta + teste da cadeia |
| Nunca aceitar da IA um preço que não está em € junto do link, nem link fora do texto ou a página de pesquisa (02-07) | test | ✓ ver 07.4. Residual aceite no T-02-28: o preço sem IVA e o por m² da mesma oferta estão na janela (WR-01) |
| Nunca transformar um preço ambíguo ("12.5", "1e3") num valor (02-07) | test | ✓ `test_parse_price` |
| Nunca cumprir os 5 min escondendo lojas | test | ✓ |
| Nunca subir LIMITS para caber nos 5 min | judgment | Veredito do verificador: cumprida — por confirmar |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/strata/ai.py` | `PRICE_FORMAT`, `TEXT_PRICE`, `PRICE_WINDOW`, `offers_from` ancorado, `StoreError` com valid == 0 | ✓ VERIFIED | Contém "IA não leu nenhuma oferta válida na página"; 3 `# shortcut:` |
| `tests/test_ai.py` | Ponta a ponta, páginas gravadas, rejeições, `parse_price` | ✓ VERIFIED | Usa as 3 fixtures pedidas |
| `tests/test_chain.py` | IA vazia/rejeitada → loja falhada | ✓ VERIFIED | `assert sr.status == "sem resultados"` só na linha 68 (`test_sem_resultados_nao_escala`) |
| `deferred-items.md` | Corte `MAX_CHARS` da Allmat e limites da janela | ✓ VERIFIED | 2 linhas novas |
| Artefactos dos planos 02-01 a 02-06 | (ver relatório anterior) | ✓ VERIFIED | `verify.artifacts`: 25/25 nos 7 planos |

### Key Link Verification

`verify.key-links`: 19/19 ligações verificadas nos 7 planos (exit 0 em todos). Confirmado à mão para o 02-07: o `StoreError` de `offers_from` cai no `except StoreError` de `search_store` (`search.py:97-100`), `found` fica `None` e o estado sai pela prioridade em `search.py:126-128`.

### Data-Flow Trace (Level 4)

| Artifact | Dado | Fonte | Dados reais | Estado |
|----------|------|-------|-------------|--------|
| Ofertas da Obramat | `unitprice_ati` | `script.dataTms` da página `/search` | Sim | ✓ FLOWING |
| Ofertas JSON-LD | `offers.price` | `application/ld+json` | Sim | ✓ FLOWING |
| Ofertas IA: link e preço | `rows` da IA | `ask(text)`, validado contra `<URL>` e `TEXT_PRICE` da janela | Sim | ✓ FLOWING |
| Ofertas IA: título | `rows[i].title` | `ask(text)`, sem validação | Não garantido | ⚠️ pode vir de outro produto (item humano 5) |

### Behavioral Spot-Checks

| Comportamento | Comando | Resultado | Estado |
|---------------|---------|-----------|--------|
| Suite inteira (1 vez) | `uv run pytest -q` | 360 passed em 8,09 s | ✓ PASS |
| Testes nomeados do 02-07 | `pytest tests/test_ai.py tests/test_chain.py -k "sem_ofertas_validas or so_com_ofertas_rejeitadas or uma_so_chamada or rejeita_o_que_nao_esta or caso_da_verificacao or reais or parse_price"` | 32 passed | ✓ PASS |
| CR-01: tudo falha, IA `[]` e IA toda rejeitada | script com `search_store` e `strata.ai.ask` falso | `bloqueada`, detail com os 4 degraus | ✓ PASS (era FAIL) |
| CR-02/WR-07: cenário exato da verificação anterior | `offers_from` com link inventado, "2", url vazio, "12.5" | `StoreError … 2 ofertas da IA rejeitadas` | ✓ PASS (era FAIL) |
| Vizinhos na página gravada "osb" | link i + preço i+1, 6 pares | 6/6 rejeitados | ✓ PASS |
| Título de outro produto | link e preço da tinta (33,60 €) com título "PLACA OSB 3 250X125X1,8CM", query "osb" | aceite e mostrado | ⚠️ (Warning, item humano 5) |
| `--sem-principal` na CLI | `uv run python -m strata pesquisar --help` | opção presente | ✓ PASS |
| Commits do 02-07 | `verify.commits 7e1c401 49e7d93 c4e728c` | 3/3 válidos | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED (sem `scripts/*/tests/probe-*.sh` e nenhum plano declara probes).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| STORE-04 | 02-01, 02-02, 02-03, 02-06 | Obramat na hora pela pesquisa direta, um pedido de cada vez | ✓ SATISFIED | SC1 verificado; 403 real por ver (item humano 2) |
| STORE-06 | 02-02, 02-03, 02-04, 02-05, 02-07 | Principal falha → JSON-LD, browser e IA antes de marcar a falha, e mostra o método | ✓ SATISFIED | Era BLOCKED. SC2 e 05.1 verificados; degrau IA ao vivo por ver (item humano 4) |
| LIST-03 | 02-06 | 10 itens nas 4 lojas em < 5 min | ? NEEDS HUMAN | Código certo; tempo só no SUMMARY (item humano 1) |

Nenhum requisito órfão: o REQUIREMENTS.md mapeia para a fase 2 só STORE-04, STORE-06 e LIST-03 (linhas 102, 109, 111), e todos aparecem nos planos.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/strata/ai.py` | 94, 101 | título da IA sem validação contra o texto | ⚠️ Warning | Link e preço de um produto podem sair com o título de outro e passar o filtro D-15 (reproduzido; item humano 5) |
| `src/strata/ai.py` | 99-102 | janela inclui o preço sem IVA e o por m² da mesma oferta | ⚠️ Warning | Residual aceite (T-02-28, WR-01 aberto, em `deferred-items.md`) |
| `src/strata/ai.py` | 21 | `MAX_CHARS = 20_000` corta a página da Allmat antes do 1.º produto | ⚠️ Warning | Degrau IA da Allmat falha sempre, agora com motivo (em `deferred-items.md`) |
| `src/strata/search.py` | 54, 89-92 | JSON-LD repete o URL que deu 403 | ⚠️ Warning | WR-02, sem mudança |
| `src/strata/browser.py` | 59-86, 156-170 | falha do arranque não guardada; Chrome lançado pode ficar aberto | ⚠️ Warning | WR-03, sem mudança |
| `src/strata/ai.py` | 169-174 | `proc.kill()` sem `wait()` | ⚠️ Warning | WR-04, sem mudança |
| `src/strata/stores/obramat.py` | 75-80, 116 | `KeyError`/`InvalidOperation` fora do `except StoreError` | ⚠️ Warning | WR-05, sem mudança |
| `src/strata/jsonld.py` | 102 | `url` do ld+json sem validar | ⚠️ Warning | WR-06, sem mudança |
| `src/strata/ai.py` | 117 | "1 ofertas da IA rejeitadas" | ℹ️ Info | Concordância no singular |

Sem `TBD`/`FIXME`/`XXX`/`TODO` em `src/strata/ai.py`, `tests/test_ai.py` nem `tests/test_chain.py`. Nenhum Blocker.

### Advisory (New Scope, Unevidenced)

Nenhum. O único achado novo (título não validado) tem evidência reproduzível e está como Warning com decisão humana (item 5).

### Human Verification Required

#### 1. Corrida de 10 itens e verificar

**Test:** `Measure-Command { uv run python -m strata pesquisar <folha-10-itens>.xlsx }` e depois `uv run python -m strata verificar`
**Expected:** menos de 300 s, 4 estados por item; `verificar` com rc=0 e 5 OK
**Why human:** os números só existem no 02-06-SUMMARY

#### 2. 403 real da Obramat (WINDOWS.md #2)

**Test:** decidir se o teste + `--sem-principal obramat` chegam
**Expected:** `waive 2` com motivo, ou manter aberto
**Why human:** o DataDome não bloqueou em nenhuma corrida

#### 3. Regra NO_STORE → browser (02-06)

**Test:** aceitar ou recusar a escalada extra, fora do D-14
**Expected:** decisão registada no CONTEXT
**Why human:** muda regras acordadas

#### 4. Degrau IA ao vivo

**Test:** `printf "placa osb 1 un\n\n" | uv run python -m strata pesquisar --sem-principal obramat` com o browser a falhar de propósito
**Expected:** ofertas "lido por IA" no fim, ou loja falhada com o motivo de cada degrau; nunca "sem resultados"
**Why human:** nunca correu ao vivo; a validação nova só viu respostas falsas

#### 5. Título da oferta IA (achado novo)

**Test:** decidir se o título não validado fica como risco aceite ou vira gap
**Expected:** decisão registada; se for gap, exigir o título no texto logo antes de `<URL>` e juntar um teste
**Why human:** reproduzido com a página gravada: a tinta a 33,60 € sai como "PLACA OSB 3 250X125X1,8CM"; fora dos gaps anteriores

#### 6. Chrome dedicado abre e fecha (D-06)

**Test:** porta 9222 antes e depois, com o Chrome fechado e aberto
**Expected:** igual antes e depois
**Why human:** sem teste automático (`behavior_unverified_items`)

#### 7. Proibições judgment

**Test:** rever as 5 proibições judgment da tabela acima
**Expected:** confirmar ou apontar a que falha
**Why human:** pedem resolução humana

### Gaps Summary

Os dois gaps bloqueantes da verificação anterior estão fechados no código, com testes e com reprodução minha:

1. **CR-01:** `offers_from` levanta `StoreError` quando `valid == 0`. A loja sai pela prioridade (bloqueada > tempo esgotado > erro) com o motivo de cada degrau. O `search.py` não mudou.
2. **CR-02 + WR-07:** o link tem de estar no texto como `<URL>`, o preço tem de ser, por valor, um preço em € dos 300 caracteres a seguir, e o caminho da página de pesquisa é recusado. `parse_price` só aceita formatos reais.

Sem gaps abertos. O estado é `human_needed`: 7 itens humanos, entre eles a prova do LIST-03 (item 1) e uma decisão nova sobre o título da IA (item 5).

---

_Verified: 2026-10-31T14:40:39Z_
_Verifier: Claude (gsd-verifier)_
