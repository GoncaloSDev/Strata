---
phase: 02-obramat-e-cadeia-de-recurso
verified: 2026-10-31T14:30:00Z
status: gaps_found
score: 42/48 must-haves verified
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
  - ".planning/phases/02-obramat-e-cadeia-de-recurso/02-REVIEW.md"
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
covered_digest: "v3:sha256:9843ad63b64767028d900b5eafb10b14643f347b8f9bbbae8a2b6628ef5175ee"
behavior_unverified: 1
overrides_applied: 0
gaps:
  - truth: "SC2 / D-16: se todos os degraus falharem, a loja aparece como falhada com o motivo"
    status: failed
    reason: "CR-01 confirmado. Quando API, JSON-LD e browser falham e o degrau IA devolve [] ou só ofertas rejeitadas, offers_from devolve Found(raw=0) e search_store mostra 'sem resultados' com detail vazio. Os motivos dos degraus ficam só em 'nota:'. Reproduzido: status 'sem resultados', detail '', notas '1 ofertas da IA rejeitadas…' e 'antes da IA: API: HTTP 403; JSON-LD: …; browser: layout mudou'. O caminho é alcançável na máquina do utilizador: shutil.which('claude') = C:\\Users\\gonca\\.local\\bin\\claude.EXE, por isso o degrau IA corre sempre que os estruturados falham."
    artifacts:
      - path: "src/strata/ai.py"
        issue: "offers_from (linha 105) devolve Found(raw=valid) com valid=0 em vez de levantar StoreError"
      - path: "src/strata/search.py"
        issue: "found.raw == 0 (linha 129) vira 'sem resultados' mesmo quando o found veio do degrau IA depois de todos os outros falharem"
      - path: "tests/test_chain.py"
        issue: "test_degrau_ia_uma_so_chamada_sem_pesquisa_alargada (linha 351) fixa o comportamento errado: assert sr.status == 'sem resultados'"
    missing:
      - "Em ai.offers_from: se valid == 0, levantar StoreError('IA não leu nenhuma oferta válida na página; …notas')"
      - "Mudar o teste da linha 351 para sr.status == 'erro' (ou 'bloqueada' pela prioridade) e confirmar que o detail tem o motivo de cada degrau"
      - "Teste novo: todos os degraus falham e a IA devolve só ofertas rejeitadas → loja falhada com o motivo de cada degrau"
  - truth: "02-05 / D-11: a IA devolve até 5 ofertas com título, preço e link tirados da página; prohibition 'Nunca aceitar da IA um preço que não está no texto da página nem um link para fora da loja'"
    status: failed
    reason: "CR-02 e WR-07 confirmados com offers_from direto. Com o texto '… 28,50 € 1 resultado pagina 2 12.5' foram aceites: 'PLACA OSB inventada' a 2 € com o link inventado https://www.obramat.pt/produtos/inventado.html (o '2' vem de 'pagina 2'), e 'PLACA OSB X' a 125 € (a string '12.5' virou 125) com o link da própria página de pesquisa (url vazio). Nenhuma nota de rejeição. O preço de 125 € não está na página e o link inventado não está no texto enviado."
    artifacts:
      - path: "src/strata/ai.py"
        issue: "linha 87: 'price_s in text' procura uma substring em 20 000 caracteres; não liga o preço ao link nem ao título"
      - path: "src/strata/ai.py"
        issue: "linha 89: o link só tem de ser https no host da loja; nunca se confirma que '<url>' está no texto; url vazio dá a página de pesquisa"
      - path: "src/strata/ai.py"
        issue: "linhas 49 e 68-69: DOT_DECIMAL só aceita 2 casas, por isso '12.5' → 125; '1e3' → 1000"
    missing:
      - "Exigir '<url>' no texto enviado e o preço numa janela junto desse link (ver o fix do CR-02 no 02-REVIEW.md)"
      - "Recusar url vazio ou igual à página de pesquisa"
      - "parse_price: aceitar só formatos de preço reais (WR-07) e devolver None para '12.5' ambíguo e '1e3'"
      - "Testes: preço de outro produto, link fora do texto, url vazio, '12.5', '1e3'"
behavior_unverified_items:
  - truth: "02-02 / D-06: se o Chrome dedicado não estava a correr, a app abre-o e fecha-o no fim; se já estava aberto, fica aberto e só os separadores da app fecham"
    test: "Com a porta 9222 fechada, correr 'printf \"placa osb 1 un\\n\\n\" | uv run python -m strata pesquisar' e ver http://127.0.0.1:9222/json/version antes e depois; repetir com o Chrome dedicado aberto por .claude\\claude-chrome.cmd"
    expected: "1.º caso: porta fechada antes e depois. 2.º caso: porta aberta depois, com os mesmos separadores do início"
    why_human: "Nenhum teste exercita BrowserFetcher.close nem _opened; a prova é só a narração do 02-02-SUMMARY. O WR-03 mostra um caminho (Popen correu, ligação falhou) em que o Chrome aberto pela app fica aberto"
human_verification:
  - test: "Correr de novo a folha de 10 itens e o verificar, com cronómetro: 'Measure-Command { uv run python -m strata pesquisar <folha-10-itens>.xlsx }' e 'uv run python -m strata verificar'"
    expected: "Folha: menos de 300 s, 10 cabeçalhos 'Linha N', 4 linhas de estado por item. verificar: rc=0 e 5 linhas OK, a da Obramat com 'método: browser'"
    why_human: "Os 222,8 s e o rc=0 em 62 s estão só no 02-06-SUMMARY, sem log gravado. Correr 4 min com rede e o Chrome dedicado não cabe numa verificação automática"
  - test: "Decidir se o caminho 'API: HTTP 403 → browser' da Obramat (WINDOWS.md #2) fica aceite pelo teste test_obramat_bloqueada_vai_ao_browser_e_fica_la e pela corrida com --sem-principal obramat, ou se espera por um 403 real"
    expected: "Decisão registada: 'gsd-tools windows waive 2 \"<motivo>\"' ou manter aberto"
    why_human: "O DataDome não bloqueou o curl_cffi em nenhuma corrida; o 403 real não se pode forçar"
  - test: "Confirmar a regra nova do 02-06: uma resposta da Obramat com a nota NO_STORE vinda de um degrau sem browser salta para o browser (não está no D-14)"
    expected: "O utilizador aceita (fica como emenda ao D-14/D-18 no CONTEXT) ou pede outra regra"
    why_human: "Muda as regras de escalada acordadas no discuss-phase; só o utilizador decide"
  - test: "Prova ao vivo do degrau IA pelo claude -p: 'printf \"placa osb 1 un\\n\\n\" | uv run python -m strata pesquisar --sem-principal obramat' com o browser a falhar de propósito (ex.: Chrome dedicado com a porta ocupada), depois de corrigir CR-01 e CR-02"
    expected: "A Obramat aparece com ofertas 'método: IA' e 'lido por IA' no fim, ou falhada com o motivo de cada degrau; nunca 'sem resultados'"
    why_human: "O degrau IA nunca correu ao vivo (sem ANTHROPIC_API_KEY e o claude -p não corria no executor). A forma output_config da API também não tem teste contra o SDK real (IN-02)"
  - test: "Rever as 5 proibições judgment (lista na secção 'Proibições'): veredito do verificador é cumpridas, não autoritativo"
    expected: "O utilizador confirma ou aponta a que falha"
    why_human: "Proibições de tipo judgment pedem resolução humana"
---

# Phase 2: Obramat e cadeia de recurso Verification Report

**Phase Goal:** As 4 lojas fixas respondem na hora para uma lista inteira em menos de 5 minutos, e uma loja que falha pelo método principal é tentada por outras vias antes de ser marcada como falhada
**Verified:** 2026-10-31T14:30:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

Resposta curta: a Obramat, o ritmo, o CAPTCHA e a cadeia API → JSON-LD → browser estão feitos e testados. A cadeia falha no fim, no degrau IA. Quando tudo falha e a IA não lê nada, a loja aparece como "sem resultados" em vez de falhada (CR-01). E a IA pode meter um preço ou um link que não está na página (CR-02 + WR-07). Reproduzi os dois com script.

Nota MVP: a fase tem `Mode: mvp`, mas o objetivo não está no formato "As a …, I want to …, so that …" (`user-story.validate` → `valid: false`). Segui o precedente da fase 1: verifico o objetivo tal como está escrito, com a tabela de fluxo abaixo. Para o formato certo: `/gsd-mvp-phase 2`.

## User Flow Coverage

| Passo | Esperado | Evidência | Estado |
|-------|----------|-----------|--------|
| 1. Passar a folha à linha de comandos | Cada item procurado nas 4 lojas | `search.STORES = (allmat, bricomarche, obras360, obramat)`; `run` faz `gather` das 4 por item | ✓ |
| 2. Obramat pela pesquisa do site | Ofertas com IVA, Alfragide, ritmo de 1 pedido | `obramat.search` → `/search?q=`; `LIMITS["www.obramat.pt"] == (1, 3.0, 2.0)` (`test_ritmo_da_obramat`) | ✓ |
| 3. CAPTCHA | "abrir à mão" com link, sem mais pedidos, lista continua | `test_captcha_obramat_abrir_a_mao_e_lista_continua`: 1 só pedido à Obramat em 2 itens, Allmat continua | ✓ |
| 4. Método principal falha | JSON-LD → browser → IA, método em cada oferta | `_rungs` pela ordem; `test_ordem_api_json_ld_browser`; `método: …` no report | ✓ |
| 5. Tudo falha | Loja falhada com o motivo | Falha quando a IA devolve vazio ou tudo rejeitado: "sem resultados", detail "" (CR-01) | ✗ |
| 6. 10 itens em < 5 min | 4 estados por item, tempo < 300 s | Código certo; os 222,8 s só existem no SUMMARY | ? |

## Goal Achievement

### Observable Truths

Critérios do ROADMAP primeiro; depois os must_haves dos planos (duplicados retirados: 02-02 #7 está no SC2, 02-06 #4 é o SC3).

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| SC1 | Obramat pela pesquisa direta, um pedido de cada vez; ao 1.º CAPTCHA "abrir à mão" com o link e a lista continua | ✓ VERIFIED | `fetch.py:37`, `Host` partilhado com o `BrowserFetcher` (`browser.py:50`); `StoreCaptcha` grava `captcha_hosts` e o `search_store` pára a loja; testes `test_ritmo_da_obramat`, `test_captcha_obramat_abrir_a_mao_e_lista_continua`, `test_captcha_no_pedido_simples_e_depois_nenhum_pedido` passam. CAPTCHA real nunca visto ao vivo |
| SC2 | Principal falha → JSON-LD, browser e IA por esta ordem, método em cada oferta; se todos falharem, loja falhada com o motivo | ✗ FAILED | Ordem e método certos (`search.py:48-55`, `test_ordem_api_json_ld_browser`, `test_ponta_a_ponta_todos_os_degraus_falham_e_a_ia_le_a_pagina`). A última frase falha: IA vazia ou toda rejeitada → `sem resultados` (CR-01, reproduzido) |
| SC3 | Folha de 10 itens nas 4 lojas em < 5 min, 4 estados por item, verificar cobre as 4 | ? UNCERTAIN | `CANARIES` com `(obramat, "osb")` e `test_verificar_quatro_lojas_ok` passam. Tempo e corrida só no 02-06-SUMMARY (222,8 s), sem log |
| 01.1 | Página gravada: "Obramat: ok" com 6 OSB a `unitprice_ati`, Alfragide, links `/produtos/…html`, tinta escondida | ✓ VERIFIED | `tests/test_obramat.py`, `tests/test_e2e.py` passam |
| 01.2 | `ise_number_result = 0` → "sem resultados"; N > 0 sem lista → erro | ✓ VERIFIED | `obramat.py:46-54` + testes |
| 01.3 | Só filhos diretos de `ol#guidance-product-list` (18, não 24) | ✓ VERIFIED | `obramat.py:51` + teste da fixture endcap |
| 01.4 | IVA incoerente > 0,02 € não vira oferta; todos falham → erro | ✓ VERIFIED | `obramat.py:79-81, 180-181` |
| 01.5 | K = 3 páginas de produto: escalões e stock exato; restantes com nota | ✓ VERIFIED | `obramat.py:27, 190-197` + testes com fixtures ctx201 |
| 01.6 | Escalão pelo total da palete; incoerentes ficam em nota | ✓ VERIFIED | `parse_tiers` (`obramat.py:111-134`) |
| 01.7 | Sem armazém 201 → nota NO_STORE | ✓ VERIFIED | `obramat.py:145-146, 194-195` |
| 01.8 | `LIMITS['www.obramat.pt'] = (1, 3.0, 2.0)` | ✓ VERIFIED | `fetch.py:37`; sem mudanças desde `be6abb0` (`git log -L`) |
| 01.9 | Um só armazém: Alfragide sempre | ✓ VERIFIED | `LOCATION` em todas as ofertas; `_problem` falha sem ele |
| 01.10 | README com a nota de âmbito legal | ✓ VERIFIED | `README.md:26-28` |
| 02.1 | Ao vivo: 403 do DataDome → "método: browser" com "antes do browser: API: HTTP 403" | ? UNCERTAIN | Código e `test_obramat_bloqueada_vai_ao_browser_e_fica_la` certos; o 403 real nunca aconteceu (WINDOWS.md #2 aberto) |
| 02.2 | Browser por CDP a 127.0.0.1:9222, perfil dedicado, nunca `launch()` | ✓ VERIFIED | `browser.py:15-18, 68, 73`; grep sem `launch(` nem `headless` |
| 02.3 | Abre o Chrome se preciso e fecha-o; se já estava aberto, fica | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | `browser.py:56, 156-170` existe e está ligado em `__main__.py:53`; nenhum teste o exercita |
| 02.4 | D-08: depois do browser, itens seguintes vão logo ao browser | ✓ VERIFIED | `search.py:51-52, 112-113`; `test_loja_no_browser_salta_a_api_no_item_seguinte` |
| 02.5 | Cada oferta mostra o método | ✓ VERIFIED | `report.py:22-23`; `search.py:105-106` |
| 02.6 | "sem resultados" e tudo escondido não escalam | ✓ VERIFIED | `test_sem_resultados_nao_escala`, `test_tudo_escondido_pelo_filtro_nao_escala` |
| 02.8 | Prazo de 90 s partilhado, detail "mais de 90 s durante …" | ✓ VERIFIED | `test_prazo_partilhado_acaba_no_browser` |
| 02.9 | `--sem-principal LOJA` em pesquisar e verificar | ✓ VERIFIED | `__main__.py:29-33`; `--help` mostra a opção; `test_sem_principal_*` |
| 02.10 | Checkpoint de pacotes antes do `uv add` | ✓ VERIFIED | Resposta "Aprovado (os dois)" registada no 02-02-SUMMARY; `pyproject.toml` com `playwright>=1.64,<1.65` e `anthropic>=2.3,<3` |
| 03.1 | 1.º CAPTCHA → "abrir à mão — CAPTCHA em <degrau>" + link | ✓ VERIFIED | `search.py:83-88`; teste SC1 |
| 03.2 | Depois do CAPTCHA, nenhum pedido à loja nos itens seguintes | ✓ VERIFIED | `search.py:60-62`, `fetch.py:99-100`, `browser.py:99-100` |
| 03.3 | As outras 3 lojas continuam | ✓ VERIFIED | teste SC1 (`"  Allmat: " in second`) |
| 03.4 | `'rt':'i'` é "bloqueada" e escala, nunca CAPTCHA | ✓ VERIFIED | `fetch.py:43-49`; `test_verificacao_do_dispositivo_nao_e_captcha` |
| 03.5 | Browser espera a verificação até 10 s; CAPTCHA → "abrir à mão" | ✓ VERIFIED | `past_challenge` + 5 testes `test_past_challenge_*` |
| 03.6 | Regra do CAPTCHA nas 4 lojas, cada uma com o seu link | ✓ VERIFIED | `test_search_page_das_4_lojas` (4 casos), `test_captcha_no_browser_da_allmat` |
| 04.1 | Ordem principal → JSON-LD → browser nas 4 lojas | ✓ VERIFIED | `search.py:53-55`; `test_ordem_api_json_ld_browser` |
| 04.2 | `--sem-principal allmat` → "método: JSON-LD" | ✓ VERIFIED | `test_allmat_sem_principal_responde_pelo_json_ld`; corrida ao vivo só no 02-04-SUMMARY |
| 04.3 | Máx. 5 páginas, filtro de título, preço EUR em Decimal > 0 | ✓ VERIFIED | `jsonld.py:18, 63-69, 99`; testes `test_jsonld.py` |
| 04.4 | Bricomarché e Obras 360 falham logo, sem pedidos | ✓ VERIFIED | `jsonld.py:76-78`; `test_bricomarche_sem_principal_salta_o_json_ld_sem_pedidos` |
| 04.5 | Obramat: links só da lista principal | ✓ VERIFIED | `obramat.py:61-66` |
| 04.6 | Página sem links escala; "sem resultados" não | ✓ VERIFIED | `jsonld.py:80-81, 109-110`; `test_paginas_sem_product_com_preco_escalam` |
| 04.7 | Só lojas com JSON-LD com IVA têm `product_links` | ✓ VERIFIED | `product_links` só em `allmat.py` e `obramat.py` |
| 05.1 | IA lê a página e devolve até 5 ofertas com título, preço e link tirados da página, "método: IA" + "lido por IA" | ✗ FAILED | Marca e método certos; mas aceita link inventado e preço de outro sítio da página, e "12.5" vira 125 € (CR-02, WR-07, reproduzido) |
| 05.2 | Oferta IA nunca à frente de uma estruturada | ✓ VERIFIED | `search.py:137`; `test_oferta_ia_fica_depois_da_estruturada_mesmo_mais_barata` |
| 05.3 | 1 chamada de IA por (item, loja), texto a 20 000 caracteres | ✓ VERIFIED | `widen=stage != "IA"`; `MAX_CHARS`; `test_degrau_ia_uma_so_chamada_sem_pesquisa_alargada` (`len(calls) == 1`) |
| 05.4 | Regras de validação tal como escritas (string no texto, > 0, https no host, filtro de título), rejeitadas numa nota | ✓ VERIFIED | `ai.py:87-104`; as regras estão lá, mas não chegam para o 05.1 |
| 05.5 | IVA da IA pela regra da loja; +23% na Obras 360 | ✓ VERIFIED | `ai.py:80, 95-96`; `test_offers_from_obras360_soma_o_iva_da_pagina` |
| 05.6 | Motor D-12: API com chave, senão `claude -p`, senão "IA não configurada" | ✓ VERIFIED | `ai.py:108-115`; testes com mocks. Nunca correu ao vivo (item humano 4) |
| 05.7 | Token OAuth nunca lido fora do `claude` | ✓ VERIFIED | Só `create_subprocess_exec`; grep sem leitura de credenciais |
| 05.8 | Testes nunca chamam a API nem o `claude` | ✓ VERIFIED | `conftest.py` fixture autouse `no_ai` |
| 06.1 | Ao vivo: `verificar` rc=0 e 5 OK com método | ? UNCERTAIN | `test_verificar_comando_imprime_ok_e_sai_com_0` passa; a corrida ao vivo só no SUMMARY |
| 06.2 | Canário da Obramat falha sem Alfragide ou com NO_STORE | ✓ VERIFIED | `search.py:181-185`; teste em `test_search.py:505` |
| 06.3 | Canário com ofertas IA falha | ✓ VERIFIED | `search.py:168-169`; teste em `test_search.py:511` |
| 06.5 | K, LIMITS e prazo sem mudanças | ✓ VERIFIED | `K = 3`, `DEADLINE_S = 90`, LIMITS sem commits depois de `be6abb0` |
| 06.6 | README com método, Chrome dedicado, "abrir à mão", `--sem-principal`, IA | ✓ VERIFIED | `README.md:8-22` |

**Score:** 42/48 verdades verificadas (1 presente mas com o comportamento por testar; 3 por confirmar; 2 falhadas)

### Proibições

| Proibição | Tipo | Estado |
|-----------|------|--------|
| Obramat: nunca mais de 1 pedido nem menos de 3 s; nunca repetir pedido bloqueado em ciclo | test | ✓ `test_ritmo_da_obramat`. Nota: WR-02 repete o mesmo URL bloqueado uma vez no JSON-LD (não é ciclo) |
| Nunca contornar o DataDome no pedido simples | judgment | Veredito do verificador: cumprida (só `impersonate="chrome"`, sem proxies) — por confirmar |
| Nunca mostrar produtos do carrossel / bloco promocional | test | ✓ seletor de filhos diretos + teste 18 vs 24 |
| Nunca o Chrome pessoal nem browser sem janela | judgment | Veredito do verificador: cumprida (`PROFILE = ~/.claude-chrome`, sem `headless`) — por confirmar |
| Nunca deixar aberto o Chrome que a app abriu nem fechar o do utilizador | test | ⚠️ **unverified-prohibition**: nenhum teste ligado; WR-03 mostra um caminho em que fica aberto |
| Nunca escalar com "sem resultados" | test | ✓ `test_sem_resultados_nao_escala` |
| Nunca resolver/esperar/contornar um CAPTCHA | test | ✓ testes de `past_challenge` e da cadeia |
| Nunca voltar a pedir a uma loja depois de um CAPTCHA | test | ✓ `len(obramat urls) == 1` |
| Nunca ler JSON-LD sem IVA (Obras 360) nem fora de EUR | test | ✓ `test_moeda_que_nao_e_eur_nao_tem_preco` |
| Nunca preço IA sem marca nem à frente | test | ✓ |
| Nunca reutilizar o token OAuth | judgment | Veredito do verificador: cumprida — por confirmar |
| Nunca aceitar da IA um preço fora do texto nem link fora da loja | test | ✗ **violada**: "12.5" → 125 € aceite (gap 2) |
| Nunca cumprir os 5 min escondendo lojas | test | ✓ `search_store` devolve sempre um `StoreResult`; `test_prazo_partilhado_acaba_no_browser` |
| Nunca subir LIMITS para caber nos 5 min | judgment | Veredito do verificador: cumprida (sem commits em LIMITS) — por confirmar |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/strata/stores/obramat.py` | Adaptador Obramat | ✓ VERIFIED | 200 linhas, em `STORES` e `CANARIES` |
| `src/strata/fetch.py` | LIMITS, `StoreCaptcha`, `challenge_kind` | ✓ VERIFIED | usado por todos os degraus |
| `src/strata/browser.py` | `BrowserFetcher` por CDP, `past_challenge` | ✓ VERIFIED | criado e fechado em `__main__._with_fetch` |
| `src/strata/jsonld.py` | Degrau JSON-LD | ✓ VERIFIED | em `_rungs` |
| `src/strata/ai.py` | Degrau IA | ✓ VERIFIED (existe, ligado) | conteúdo com os gaps CR-01/CR-02 |
| `src/strata/search.py` | Cadeia, `CANARIES`, `_problem` | ✓ VERIFIED | |
| `src/strata/models.py` | `Offer.method`, "abrir à mão", `StoreResult.link` | ✓ VERIFIED | |
| `tests/test_chain.py`, `test_ai.py`, `test_fetch.py`, `test_jsonld.py`, `test_obramat.py` | Testes sem rede | ✓ VERIFIED | `verify.artifacts`: 22/22 em 6 planos |
| `README.md` | Uso com 4 lojas | ✓ VERIFIED | |

### Key Link Verification

`verify.key-links`: 17/17 ligações verificadas nos 6 planos (exit 0 em todos). Confirmado à mão: `BrowserFetcher(f)` + `b.close()` em `__main__.py:49-53`; `self.hosts = base.hosts` em `browser.py:50` (o mesmo ritmo nos dois transportes); `ai.rung(store)` no fim de `_rungs`.

### Data-Flow Trace (Level 4)

| Artifact | Dado | Fonte | Dados reais | Estado |
|----------|------|-------|-------------|--------|
| Ofertas da Obramat | `unitprice_ati` | `script.dataTms` da página `/search` | Sim (fixtures gravadas ao vivo) | ✓ FLOWING |
| Escalões/stock | `.o-priceByQuantity__tileItem`, `available_deliveries` | página de produto | Sim | ✓ FLOWING |
| Ofertas JSON-LD | `offers.price` | `application/ld+json` | Sim | ✓ FLOWING |
| Ofertas IA | `rows` da IA | `ask(text)` | Validação fraca (CR-02) | ⚠️ pode entrar valor que não está na página |

### Behavioral Spot-Checks

| Comportamento | Comando | Resultado | Estado |
|---------------|---------|-----------|--------|
| Suite inteira (1 vez) | `uv run pytest -q` | 339 passed em 8,27 s | ✓ PASS |
| CR-01: tudo falha, IA toda rejeitada | script com `search_store` e `strata.ai.ask` falso | `status: sem resultados`, `detail: ''` | ✗ FAIL |
| CR-02/WR-07: validação da IA | `ai.offers_from` com link inventado, "2" e "12.5" | aceites a 2 € e 125 €, 0 rejeitadas | ✗ FAIL |
| `--sem-principal` na CLI | `uv run python -m strata pesquisar --help` | opção presente | ✓ PASS |
| Motor IA disponível na máquina | `shutil.which('claude')` | `C:\Users\gonca\.local\bin\claude.EXE` (o CR-01 é alcançável) | ✓ (informação) |
| Commits do SUMMARY | `verify.commits` (12 hashes) | 12/12 válidos | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED (sem `scripts/*/tests/probe-*.sh` e nenhum plano declara probes).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| STORE-04 | 02-01, 02-02, 02-03, 02-06 | Obramat na hora pela pesquisa direta, um pedido de cada vez | ✓ SATISFIED | SC1 verificado; 403 real por ver (item humano 2) |
| STORE-06 | 02-02, 02-03, 02-04, 02-05 | Principal falha → JSON-LD, browser e IA antes de marcar a falha, e mostra o método | ✗ BLOCKED | CR-01: com a IA vazia a falha não é marcada; CR-02: a IA aceita valores que não estão na página |
| LIST-03 | 02-06 | 10 itens nas 4 lojas em < 5 min | ? NEEDS HUMAN | Código certo; tempo só no SUMMARY |

Nenhum requisito órfão: o REQUIREMENTS.md mapeia para a fase 2 só STORE-04, STORE-06 e LIST-03, e todos aparecem nos planos.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/strata/ai.py` | 105 | `Found(raw=0)` do degrau IA → "sem resultados" | 🛑 Blocker | Falha escondida (CR-01) |
| `src/strata/ai.py` | 87-89 | validação por substring e host | 🛑 Blocker | Preço/link que não estão na página (CR-02) |
| `src/strata/ai.py` | 49, 68 | `DOT_DECIMAL` só 2 casas | 🛑 Blocker (mesma causa) | "12.5" → 125 € (WR-07) |
| `src/strata/search.py` | 54, 89-92 | JSON-LD repete o URL que deu 403 | ⚠️ Warning | Mais um pedido bloqueado à Obramat (WR-02) |
| `src/strata/browser.py` | 59-86, 156-170 | falha do arranque não guardada; Chrome lançado pode ficar aberto | ⚠️ Warning | Até 10 s por loja e por item; D-06 (WR-03) |
| `src/strata/ai.py` | 152-159 | `proc.kill()` sem `wait()` | ⚠️ Warning | "erro" em vez de "tempo esgotado" no Windows (WR-04) |
| `src/strata/stores/obramat.py` | 75-80, 116 | `KeyError`/`InvalidOperation` fora do `except StoreError` | ⚠️ Warning | Um produto mal formado derruba a loja (WR-05) |
| `src/strata/jsonld.py` | 102 | `url` do ld+json sem validar | ⚠️ Warning | Link partido ou de fora (WR-06) |
| `src/strata/ai.py` | 95-97 | preço por m² da Obras 360 tratado como artigo | ⚠️ Warning | Preço unitário errado na IA (WR-01) |
| `src/strata/stores/obramat.py` | 129 | percentagem sem arredondar | ℹ️ Info | Só apresentação (IN-01, em `deferred-items.md`) |

Sem `TBD`/`FIXME`/`XXX` em `src/strata/` nem no `README.md`.

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

#### 4. Degrau IA ao vivo (depois dos fixes)

**Test:** forçar a falha dos degraus estruturados e ver a Obramat pelo `claude -p`
**Expected:** ofertas "lido por IA" no fim, ou loja falhada com os motivos
**Why human:** nunca correu ao vivo

#### 5. Chrome dedicado abre e fecha (D-06)

**Test:** porta 9222 antes e depois, com o Chrome fechado e aberto
**Expected:** igual antes e depois
**Why human:** sem teste automático

### Gaps Summary

Os dois gaps têm a mesma raiz: o contrato de saída do degrau IA (`src/strata/ai.py`, `offers_from`). Um plano de correção pequeno resolve os dois:

1. **CR-01** — `valid == 0` tem de ser falha do degrau (`StoreError`), não `Found(raw=0)`. Assim a loja aparece "bloqueada"/"erro" com o motivo de cada degrau (D-16, SC2). O teste `test_chain.py:351` passa a esperar `erro`.
2. **CR-02 + WR-07** — o link tem de estar no texto como `<url>`, o preço numa janela junto dele, url vazio recusado, e `parse_price` só com formatos de preço reais.

O resto da fase (Obramat, ritmo, CAPTCHA, JSON-LD, browser, verificar com 4 lojas, README) está verificado por código e testes. Os itens humanos não bloqueiam a correção, mas o 1 (tempo) é a prova do LIST-03.

---

_Verified: 2026-10-31T14:30:00Z_
_Verifier: Claude (gsd-verifier)_
