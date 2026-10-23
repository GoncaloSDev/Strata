---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
verified: 2026-10-23T19:23:02Z
status: gaps_found
score: 80/82 must-haves verified
covered_files:
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-01-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-01-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-02-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-02-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-03-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-03-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-04-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-04-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-05-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-05-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-06-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-06-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-07-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-07-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-08-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-08-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-09-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-09-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-10-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-10-SUMMARY.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-11-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-11-SUMMARY.md"
  - ".python-version"
  - "README.md"
  - "pyproject.toml"
  - "src/strata/__init__.py"
  - "src/strata/__main__.py"
  - "src/strata/fetch.py"
  - "src/strata/models.py"
  - "src/strata/money.py"
  - "src/strata/report.py"
  - "src/strata/search.py"
  - "src/strata/sheet.py"
  - "src/strata/stores/__init__.py"
  - "src/strata/stores/allmat.py"
  - "src/strata/stores/bricomarche.py"
  - "src/strata/stores/obras360.py"
  - "src/strata/text.py"
  - "src/strata/words.py"
  - "tests/conftest.py"
  - "tests/fixtures/allmat_product-page_39233_box.html"
  - "tests/fixtures/allmat_products_search-cimento.json"
  - "tests/fixtures/allmat_products_search-osb_no-results.json"
  - "tests/fixtures/bricomarche_products_search-osb.json"
  - "tests/fixtures/bricomarche_variations_parent-47412.json"
  - "tests/fixtures/obras360_pesquisa-widget.html"
  - "tests/fixtures/obras360_product-details_osb-parent.json"
  - "tests/fixtures/obras360_product-details_tinta-colorite.json"
  - "tests/fixtures/obras360_product-details_tinta-dycrilforce.json"
  - "tests/fixtures/obras360_product-details_tinta-dyrup-super.json"
  - "tests/fixtures/obras360_product-details_tinta-dyrustar.json"
  - "tests/fixtures/obras360_product-list_no-results.json"
  - "tests/fixtures/obras360_product-list_osb.json"
  - "tests/fixtures/obras360_product-list_tinta-branca.json"
  - "tests/test_allmat.py"
  - "tests/test_bricomarche.py"
  - "tests/test_e2e.py"
  - "tests/test_money.py"
  - "tests/test_obras360.py"
  - "tests/test_search.py"
  - "tests/test_sheet.py"
  - "tests/test_text.py"
  - "tests/test_tracer.py"
covered_digest: "v3:sha256:503d3456149694c40c96f85387dfcfda908ed238d67070eb86a525d285076f24"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 67/67
  gaps_closed:
    - "G-01-3 (UAT teste 3), no código: offer_from escolhe a loja física mais barata COM stock; a mais barata sem stock fica na nota 'mais barata sem stock: X em Y' (bricomarche.py offer_from; 8 testes nomeados passam). Falta o re-teste do utilizador"
    - "G-01-5 (UAT teste 5), no caso citado: 'OSB 12 mm' pela alargada mostra só a placa de 12 MM (test_osb_12mm_alargada_mostra_so_a_placa_de_12mm; ao vivo no 01-11). Falta o re-teste do utilizador"
    - "CR-06: corte K=20 da Obras 360 pelos pais com mais palavras da pesquisa (test_pai_com_mais_palavras_da_pesquisa_passa_a_frente_do_corte)"
    - "WR-07: 'azulejo 30x30' já não bate em 'Azulejo 30x60' (sai do deferred)"
    - "WR-12: geotêxteis, coxins, jardins batem no singular"
    - "WR-13: 'tubo 3 metros' bate em 'Tubo 3m'; broadened('tubo 3 metros') == 'tubo'"
  gaps_remaining:
    - "G-01-5 fora do caso citado: com mais pais do que K na alargada, o pai certo pode nunca ser expandido (WR-17). Prova ao vivo: 'pavimento 60x120' na Bricomarché"
  regressions:
    - "WR-14 (quick 261023-lee): a medida passou a contar a ordem e ignora o '×': 'pavimento 120x60' já não bate em 'Pavimento 60x120'; 'azulejo 30x30' não bate em 'Azulejo 30×30 cm'. Reproduzido; sem efeito ao vivo observado hoje"
    - "WR-15 (quick 261023-lee): broadened('tela 1 m x 25 m') == 'tela x' (antes 'tela'); o 'x' esconde todas as ofertas da alargada. Reproduzido"
gaps:
  - truth: "Para cada linha da folha, as ofertas mostradas são o produto pedido, mais baratas primeiro, e não outros produtos que só partilham uma palavra (G-01-5, fora do caso citado 'OSB 12 mm')"
    status: partial
    reason: "Na pesquisa alargada, a loja recebe só a pergunta alargada e os cortes K (Bricomarché K=10 pelo preço do pai; Obras 360 K=20 com need = words(pergunta alargada), todos empatados) escolhem os pais sem olhar para a pergunta completa. O passo final do 01-11 só filtra o que já foi expandido. Ao vivo hoje: 'pavimento 60x120 10 m²' dá 0 na pesquisa da Bricomarché (a pesquisa da loja não junta 'pavimento' e '60x120', embora os títulos tenham as duas palavras), a alargada 'pavimento' lê 149 pais e os 2 que batem a pergunta completa ('PAVIMENTO CERÂMICO SIENA HEKLA 60X120 1.44M2' e 'Pavimento/Revestimento Cerâmico Casablanca Mate 60X120 1.44M2', 34,55 €) ficam nas posições 132 e 133 da ordem por preço. Resultado: a Bricomarché mostra pavês de betão a 0,21 €/un ('não convertível para m²') e '+138 produtos não expandidos'. Está marcado 'pesquisa alargada', por isso não é silencioso, mas é exatamente o que o utilizador rejeitou no UAT teste 5, numa linha comum de obra, e uma pesquisa à mão por '60x120' na loja encontra 34 pavimentos"
    artifacts:
      - path: "src/strata/search.py"
        issue: "linha 27: store.search(b, fetch) não passa o produto da linha; o passo final (36-40) não recupera pais fora do corte"
      - path: "src/strata/stores/bricomarche.py"
        issue: "search: keyed.sort só pelo preço do pai antes do corte K=10"
      - path: "src/strata/stores/obras360.py"
        issue: "need = words(query): na alargada é a pergunta alargada, por isso todos os pais empatam e o corte K=20 volta a ser pelo preço"
      - path: "src/strata/words.py"
        issue: "WR-14: com o WR-17 corrigido, 'pavimento 120x60' passa a expandir os pavimentos '60X120' (as lojas escrevem o lado menor primeiro) mas o passo final não os aceita, porque a medida inteira conta a ordem"
    missing:
      - "Passar o produto da linha à loja só para ordenar os pais antes do corte, sem mudar a pesquisa enviada (ex.: store.search(b, fetch, rank=item.product); obras360 need = words(rank or query); bricomarche ordena por -len(words(rank or query) & words(nome)) e depois pelo preço; allmat aceita e ignora)"
      - "Teste: 11+ pais 'pavimento' baratos e a placa 60x120 como a mais cara; a placa tem de estar entre os expandidos e ser a única oferta mostrada, com os restantes contados"
      - "WR-14 no mesmo plano: plain(s).replace('×', 'x') e cada troço com as partes ordenadas; casos ('pavimento 120x60', 'Pavimento 60x120', True), ('azulejo 30x30', 'Azulejo 30×30 cm', True), mantendo ('azulejo 30x30', 'Azulejo 30x60', False)"
      - "Corrida ao vivo de 'pavimento 60x120 10 m²': a Bricomarché mostra os pavimentos 60X120 a 34,55 €"
deferred:
  - truth: "WR-08: o género junta barra/barro, banco/banca, tampo/tampa, lixa/lixo (e IN-14: a regra -m/-n junta fim/fino)"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC2: 'Cada anúncio fica classificado como exato / parecido / outro'"
  - truth: "WR-11: 'osb 30mm' mostra as 7 espessuras pela gama '9-30MM' do nome do pai"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC1/SC2: especificações extraídas (espessura) e classificação exato/parecido; aceite no 01-08 (T-01-36) com shortcut: no código"
  - truth: "IN-11: colisões da tabela PLURAL (cal/Cais, mal/Mais, abs/AB, eps/EP) e 'Varão Roscado … Fixação Perfil Teto' em 'perfis'"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC2: 'Cada anúncio fica classificado como exato / parecido / outro'; aceite no 01-09 (T-01-40)"
  - truth: "Produto contra menção quando todas as palavras pedidas estão no título (cola 'para OSB' quando se pede só 'OSB'; misturador de cimento cola)"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC2; listado em 'Fora do âmbito' do 01-11-PLAN"
behavior_unverified_items: []
coincidental_reliance_items: []
---

# Phase 1: Folha Excel e preços da Allmat, Bricomarché e Obras 360 — Relatório de verificação

**Objetivo da fase:** O utilizador preenche o modelo Excel da app, passa o caminho do `.xlsx` à linha de comandos e recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360, já com IVA 23% e preço unitário normalizado, com o estado de cada loja sempre visível; para uma pesquisa rápida pode colar texto em vez da folha
**Verificado:** 2026-10-23T19:23:02Z
**Estado:** gaps_found
**Reverificação:** Sim, a terceira, depois do quick 261023-lee e dos planos de fecho do UAT 01-10 e 01-11

## Resposta curta

1. **G-01-3 está fechado no código.** `offer_from` (bricomarche.py) escolhe a loja mais barata com stock, e a mais barata sem stock aparece na nota. Os 8 testes nomeados passam. Falta o utilizador repetir o teste 3.
2. **G-01-5 só está fechado no caso citado.** "OSB 12 mm" mostra só a placa de 12 mm (teste nomeado passa). Mas o WR-17 deixa a mesma falha aberta sempre que a alargada traz mais pais do que o corte K. Provei-o ao vivo com uma linha comum: em "pavimento 60x120", a Bricomarché mostra pavês de betão a 0,21 € e vende pavimentos 60X120 a 34,55 €, que ficam nas posições 132 e 133 da ordem por preço e nunca são expandidos. Esta é a lacuna que bloqueia.
3. **O WR-14 e o WR-15 são regressões reais do quick**, reproduzidas. Ao vivo hoje não morderam, porque as três lojas escrevem "60X120" (o lado menor primeiro) e não usam "×". O WR-14 fica no mesmo plano do WR-17: quando o WR-17 for corrigido, "pavimento 120x60" passa a expandir os pavimentos "60X120", e é o WR-14 que os rejeita. O WR-16 é um aviso.
4. Suite: `uv run python -m pytest -q` → 209 passed.

## User Flow Coverage

| Passo | Esperado | Evidência | Estado |
|-------|----------|-----------|--------|
| 1. Obter o modelo | `modelo` grava o modelo; não sobrescreve | `sheet.py` inalterado; `test_sheet.py` verde | ✓ |
| 2. Preencher e passar o `.xlsx` | Cada linha válida vira item | `read_sheet` inalterado; UAT teste 7 passou (o `.xlsx` não muda) | ✓ |
| 3. Preços das 3 lojas por linha | Ofertas do produto pedido, mais baratas primeiro | Ao vivo hoje (3 linhas, código 0, 61 s): as três lojas respondem. Em "pavimento 60x120" a Bricomarché e a Obras 360 mostram pavês de betão, não o pavimento pedido (WR-17) | ✗ parcial |
| 4. IVA 23% e preço unitário | Preço, origem do IVA, €/unidade, stock | Ao vivo: "IVA: indicado pela loja (tax_percentage=23) · 10,88 €/m² · 123 em stock" | ✓ |
| 5. Estado de cada loja visível | As 3 lojas sempre presentes | As 3 secções em cada linha da corrida ao vivo | ✓ |
| 6. Pesquisa rápida colada | Descrição, quantidade e unidade | Corrida ao vivo por texto colado ("Linha 1 — pavimento 120x60 (10 m²)") | ✓ |

## Goal Achievement

### Observable Truths — critérios do ROADMAP, objetivo e lacunas do UAT

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| G | O utilizador recebe, para cada linha, os preços na hora das três lojas | ✓ VERIFIED | Ao vivo hoje, as 3 lojas "ok" com preço em cada linha. Se o produto certo aparece é a verdade G-01-5 |
| SC1 | Modelo Excel, linha de comandos, linhas inválidas com número e motivo | ✓ VERIFIED | `sheet.py` sem mudança desde a última verificação; testes verdes |
| SC2 | Lista colada com descrição, quantidade e unidade; texto livre sem categoria | ✓ VERIFIED | `text.py` sem mudança; corrida ao vivo por texto colado |
| SC3 | Bricomarché: o preço mais barato entre as lojas físicas, com o nome da loja e o link; Allmat: caixa convertida; Obras 360: variantes, IVA e escalões | ? UNCERTAIN | Allmat e Obras 360 sem mudança. Na Bricomarché, depois do 01-10, a oferta (preço, nome e link) é a loja mais barata **com stock**. A mais barata absoluta, se não tiver stock, aparece só na nota, com preço e nome mas sem link. Foi o utilizador que o pediu no UAT, mas o texto do SC3 e do STORE-01 não mudou. Precisa de decisão: ver o item humano 4 |
| SC4 | Preço com IVA, origem do IVA, preço unitário, stock, sem filtrar | ✓ VERIFIED | `report._offer_lines`; ao vivo em todas as ofertas. O 01-10 não filtra pelo stock (`test_offer_from_nenhuma_loja_com_stock`) |
| SC5 | Estado das três lojas por item; `verificar` por adaptador | ✓ VERIFIED | Ao vivo hoje; `search.verificar` e os canários sem mudança |
| G-01-3 | A 1.ª oferta da Bricomarché é a loja mais barata com stock; a mais barata sem stock não some | ✓ VERIFIED (no código) | `offer_from`: `best = cheapest([r for r in rows if has_stock(r)]) or low`; nota só com `_price(low) < _price(best)`. Testes: amostra 47412 (19,99 € em Monção, nota de 18,49 € em Coina), prefere stock, nenhuma com stock, empate, sem dica, `test_search_osb`, e2e "loja: Monção". Ao vivo no 01-10: 15,49 € em Ponte de Sor com a nota de 14,49 €. Falta o re-teste 3 |
| G-01-5 | Para cada linha, as ofertas mostradas são o produto pedido, mais baratas primeiro | ✗ FAILED (parcial) | Fechado no caso citado (`test_osb_12mm_alargada_mostra_so_a_placa_de_12mm`; ao vivo no 01-11: só a placa de 12 MM a 19,37 €). Aberto quando a alargada tem mais pais do que K: em "pavimento 60x120", ao vivo, a Bricomarché mostra pavês a 0,21 € e deixa de fora os 2 pavimentos 60X120 que vende (posições 132 e 133 de 148, com K=10). Ver Gaps |

### Observable Truths — must_haves dos planos

| Plano | Verdades | Estado | Evidência |
|-------|----------|--------|-----------|
| 01-01 a 01-07 (49) | como nas verificações anteriores | 49/49 ✓ | Testes nomeados verdes; os ficheiros que mudaram (search, report, models, words, obras360, bricomarche) mantêm os testes dessas verdades |
| 01-08 (6) | "OSB 12 mm" com o pai; LxCxE; Lt/OSB3 | 6/6 ✓ | `verify.artifacts` diz que falta o padrão `LITRE` em words.py: o quick trocou-o por `UNIT_WORDS`/`SPELLED`. O comportamento mantém-se: `title_matches('tinta 15 lt','Tinta Plástica 15L')`, `('tinta 15 litros','Tinta 15 L')` e `('osb3','Placa OSB 3')` dão True |
| 01-09 (6) | perfis, plurais, M8 à frente do corte, "0 de N", litros | 6/6 ✓ | `verify.key-links` diz que falta `not title_matches(query` em obras360.py: o CR-06 trocou-o por `-len(need & words(nome))`. `test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte` e `test_perfis_mostra_o_pai_perfil` passam |
| 01-10 (6) | ver abaixo | 6/6 ✓ | |
| 01-11 (7) | ver abaixo | 7/7 ✓ | As 7 estão escritas para o caso citado e casos vizinhos; a falha geral fica na verdade G-01-5 |

**01-10, verdade a verdade:**

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| 1 | Amostra 47412: 19,99 € em Monção, "118 em stock", link da loja | ✓ VERIFIED | `test_offer_from_amostra_47412` passa |
| 2 | A mais barata sem stock fica na nota com preço e loja | ✓ VERIFIED | `note = f"mais barata sem stock: …"`; mesmo teste |
| 3 | Ninguém com stock → a mais barata, sem nota; empate → a com stock, sem nota | ✓ VERIFIED | `test_offer_from_nenhuma_loja_com_stock`, `test_offer_from_empate_prefere_a_loja_com_stock`, `test_offer_from_sem_dica_quando_a_mais_barata_tem_stock` |
| 4 | Ordem com o preço da loja com stock (14,49 € Coina pai 47411, 19,99 € Monção) | ✓ VERIFIED | `test_search_osb` passa; `Offer.price = _price(best)` entra em `in_unit` |
| 5 | e2e: "loja: Monção" e a nota da Coina | ✓ VERIFIED | `test_tres_itens_tres_lojas_pela_ordem` passa |
| 6 | Suite verde | ✓ VERIFIED | 209 passed (204 + 5 do 01-11) |

**01-11, verdade a verdade:**

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| 1 | "OSB 12 mm" na Obras 360 pela alargada: só a placa de 12 MM, "+7 ofertas escondidas: título sem 'OSB 12 mm'" | ✓ VERIFIED | `test_osb_12mm_alargada_mostra_so_a_placa_de_12mm` passa |
| 2 | Várias que batem: só essas, mais baratas primeiro | ✓ VERIFIED | `test_alargada_mostra_so_as_que_batem_a_pergunta_completa` |
| 3 | Nenhuma ou todas batem: como antes, sem linha nova | ✓ VERIFIED | `test_alargada_sem_mistura_fica_como_antes` (2 casos); ao vivo hoje em "azulejo 30x30" e "pavimento …" (nenhuma bate, sem linha nova) |
| 4 | Nada some sem contagem: duas linhas de escondidas | ✓ VERIFIED | `report.py`: `sr.hidden` e `sr.wide_only`, cada um com a sua linha. Contagem dupla no ramo "tudo escondido": WR-16 (aviso) |
| 5 | Nenhum pedido novo às lojas | ✓ VERIFIED | `search.py:36-40` corre sobre `found.offers`; `store.calls == ['OSB 12mm', 'OSB']` em `test_tudo_escondido_alargada_com_ofertas_que_batem` |
| 6 | Bricomarché "OSB 12mm" pela alargada: só a PLACA OSB 12 MM, a de 9 mm contada | ✓ VERIFIED | `test_ponta_a_ponta_allmat_e_bricomarche` passa |
| 7 | Suite com 209 passed | ✓ VERIFIED | `uv run python -m pytest -q` → 209 passed |

**Score:** 80/82 verdades verificadas (G-01-5 falha em parte; SC3 fica à espera de decisão). Nenhuma verdade está só presente sem prova de comportamento: as do 01-10 e do 01-11 têm testes com nome, corridos hoje (8 + 5 + 75 passed).

### Deferred Items

| # | Item | Fase | Evidência |
|---|------|------|-----------|
| 1 | WR-08 barra/barro, tampo/tampa (e IN-14 fim/fino, da regra -m/-n) | Phase 3 | SC2: exato / parecido / outro |
| 2 | WR-11 "osb 30mm" mostra as 7 espessuras | Phase 3 | SC1/SC2; aceite no 01-08 (T-01-36) |
| 3 | IN-11 cal/Cais, abs/AB; "Varão … Fixação Perfil Teto" em "perfis" | Phase 3 | SC2; aceite no 01-09 (T-01-40) |
| 4 | Produto contra menção com todas as palavras no título | Phase 3 | SC2; "Fora do âmbito" do 01-11 |

O **WR-07 saiu da lista**: o quick corrigiu-o no caso citado (`('azulejo 30x30', 'Azulejo 30x60')` → False) e a regressão que trouxe é o WR-14. **O WR-17 não foi adiado.** A Phase 3 classifica o que aparece, mas não expande pais que o corte deixou de fora. O SC3 da Phase 3 fala do Tamanho da folha e não da ordem dos pais antes do corte.

### Advisory (New Scope, Unevidenced)

Nenhum. Reproduzi todos os achados novos de forma determinística (WR-14, WR-15 e WR-16 com scripts e testes, WR-17 ao vivo) e classifiquei-os abaixo.

### Required Artifacts

`verify.artifacts`: 01-01 7/7, 01-02 6/6, 01-03 4/4, 01-04 2/2, 01-05 2/3, 01-06 3/3, 01-07 4/4, 01-08 3/4, 01-09 4/5, 01-10 4/4, 01-11 6/6.

| Artefacto | Esperado | Estado | Detalhe |
|-----------|----------|--------|---------|
| `src/strata/stores/bricomarche.py` | `note = f"mais barata sem stock: ` | ✓ VERIFIED | Ligado: `offer_from` → `Offer.note` → `report._offer_lines`; `Offer.price` → `in_unit` em `search_store` |
| `src/strata/search.py` | `title_matches(item.product` | ✓ VERIFIED | Só no ramo da alargada; `wide_only=wide_only` no StoreResult "ok" |
| `src/strata/models.py` | `wide_only: int = 0` | ✓ VERIFIED | |
| `src/strata/report.py` | `sr.wide_only` | ✓ VERIFIED | Linha própria com `clean(it.product)` |
| `tests/test_bricomarche.py`, `test_e2e.py`, `test_obras360.py`, `test_search.py` | testes do 01-10 e do 01-11 | ✓ VERIFIED | Passam |
| `.planning/STATE.md` | "substituída pelo 01-10" | ✓ VERIFIED | 1 ocorrência |
| `01-CONTEXT.md` | "Emenda 2026-10-23" | ✓ VERIFIED | 1 ocorrência |
| `src/strata/words.py` (01-08: `LITRE`) | padrão | ℹ️ substituído | Trocado pelo quick por `UNIT_WORDS`/`SPELLED`; comportamento mantido (ver acima) |
| `src/strata/stores/obras360.py` (01-09: `not title_matches(query`) | padrão | ℹ️ substituído | Trocado pelo CR-06 por `-len(need & words(...))`; testes do 01-09 passam |
| `tests/test_obras360.py` (01-05: `DiscountByQuantity`) | padrão | ℹ️ como antes | Os escalões são testados sobre a fixture |

### Key Link Verification

`verify.key-links`: 01-01 4/4, 01-02 3/3, 01-03 3/3, 01-04 3/3, 01-05 3/3, 01-06 2/2, 01-07 3/3, 01-08 2/2, 01-09 2/3 (padrão substituído pelo CR-06, ver acima), 01-10 2/2, 01-11 2/2.

### Data-Flow Trace (Level 4)

| Artefacto | Dado | Origem | Dados reais | Estado |
|-----------|------|--------|-------------|--------|
| `report.print_item` | `sr.offers[].price`, `note` | APIs das 3 lojas (Decimal) | Sim, ao vivo hoje ("mais barata sem stock: 0,18 € em Arco do Cego - Lisboa") | ✓ FLOWING |
| `report.print_item` | `sr.wide_only` | `search_store`, passo final | Sim nos testes; ao vivo no 01-11 ("+19 ofertas escondidas: título sem 'OSB 12 mm'") | ✓ FLOWING |
| `bricomarche.search` | pais expandidos | corte K=10 pelo preço do pai | Sim, mas na alargada escolhe pais sem olhar para a pergunta completa (WR-17) | ⚠️ ver Gaps |

### Behavioral Spot-Checks

| Comportamento | Comando | Resultado | Estado |
|---------------|---------|-----------|--------|
| Suite sem rede (uma vez) | `uv run python -m pytest -q` | 209 passed | ✓ PASS |
| Testes do 01-10 | `pytest tests/test_bricomarche.py tests/test_e2e.py -k "offer_from or search_osb or tres_itens or ponta_a_ponta"` | 8 passed | ✓ PASS |
| Testes do 01-11 e do CR-06 | `pytest tests/test_obras360.py -k "alargada_mostra_so or frente_do_corte or perfis or osb_12mm or mais_palavras"` | 5 passed | ✓ PASS |
| Filtro e alargada | `pytest tests/test_search.py -k "alargada or tudo_escondido or title_matches or broadened"` | 75 passed | ✓ PASS |
| WR-14 (antes do quick vs HEAD) | script com `title_matches` de `9262daa` e de HEAD | `('pavimento 120x60','Pavimento 60x120')`, `('azulejo 30x60','Azulejo 60x30')`, `('placa 1250x2500','Placa OSB 2500x1250x12mm')`, `('tijolo 30x20x11','Tijolo 11x20x30')`, `('azulejo 30x30','Azulejo 30×30 cm')`: base True, HEAD False | ✗ regressão |
| WR-15 | mesmo script, `broadened` | `'tela 1 m x 25 m'` → base 'tela', HEAD 'tela x'; `'placa 2,5 m x 1,2 m'` → 'placa x'. Formas coladas ('1m x 10m', '1 x 25 m') continuam bem | ✗ regressão (forma estreita) |
| Ao vivo, 3 linhas coladas | `printf 'pavimento 120x60 10 m²\npavimento 60x120 10 m²\nazulejo 30x30 5 m²\n\n' \| uv run python -m strata pesquisar` | código 0, 61 s. As duas linhas de pavimento dão saída igual: as três lojas caem na alargada "pavimento". A Bricomarché mostra pavês a 0,21–1,89 €/un com "+138 produtos não expandidos"; a Obras 360 mostra pavês com "+77 não expandidos". Nenhum título com "×" | ✗ (WR-17) |
| Ordem das medidas nas lojas (4 pedidos) | pesquisa na API WooCommerce por "60x120" e por "120x60" | Allmat: 50 / 0; Bricomarché: 34 pavimentos "60X120" / 3 produtos sem ser pavimento. As lojas escrevem o lado menor primeiro | ℹ️ |
| Pesquisa da loja com a linha (2 pedidos) | "pavimento 60x120" na Allmat e na Bricomarché | 0 e 0, embora a Bricomarché tenha "PAVIMENTO CERÂMICO SIENA HEKLA 60X120" | ℹ️ (por isso corre a alargada) |
| Corte K=10 na alargada (2 pedidos) | pais de "pavimento" na Bricomarché, ordenados como o adaptador ordena | 149 pais, 148 com preço; os 2 que batem "pavimento 60x120" ficam nas posições 132 e 133 (34,55 €). Com K=10 nunca são expandidos | ✗ (WR-17, prova ao vivo) |

### Probe Execution

Não há probes (`scripts/*/tests/probe-*.sh`) nem probes declarados nos planos. Passo não aplicável.

### Requirements Coverage

Os 12 IDs da fase estão no `requirements` de pelo menos um plano (01-10: STORE-01, RES-02; 01-11: LIST-02, STORE-03). Não há órfãos.

| Requisito | Planos | Estado | Evidência |
|-----------|--------|--------|-----------|
| LIST-01 | 01-02 | ✓ SATISFIED | `text.py`; entrada colada ao vivo |
| LIST-02 | 01-01/02/03/07/08/09/11 | ⚠️ SATISFIED em parte | Qualquer produto é pesquisado sem categoria. Mas o produto certo pode não aparecer quando a alargada tem mais pais do que K (lacuna WR-17) |
| LIST-04 | 01-01/02 | ✓ SATISFIED | `write_template` |
| LIST-05 | 01-01/02 | ✓ SATISFIED | `read_sheet` |
| STORE-01 | 01-04/08/10 | ? NEEDS HUMAN | Loja com stock em vez de "o mais barato entre todas"; a mais barata absoluta fica na nota. Desvio pedido no UAT; o texto do requisito tem de ser atualizado ou aceite (item humano 4) |
| STORE-02 | 01-03 | ✓ SATISFIED | `parse_box`; ao vivo "12,99 €/m²" na Allmat |
| STORE-03 | 01-05/07/08/09/11 | ✓ SATISFIED | Variantes, IVA e escalões ao vivo ("escalões: −5% a partir de 540") |
| STORE-05 | 01-01/02/03/06/07/09 | ✓ SATISFIED | As 3 lojas em cada linha ao vivo |
| STORE-07 | 01-06 | ✓ SATISFIED | `verificar` sem mudança |
| PRICE-01 | 01-01/02/04/05/07 | ✓ SATISFIED | Três origens do IVA ao vivo |
| PRICE-02 | 01-03/05 | ✓ SATISFIED (aviso WR-02) | `per_unit`, `in_unit` |
| RES-02 | 01-01/02/04/05/10 | ✓ SATISFIED | O stock fica à vista e não filtra (`test_offer_from_nenhuma_loja_com_stock`) |

ℹ️ A tabela de rastreio do REQUIREMENTS.md continua a marcar LIST-01, LIST-04, LIST-05, STORE-02, STORE-07, PRICE-01 e PRICE-02 como "Gaps Found". Nenhuma lacuna lhes tocou. Acertar ao fechar a fase.

### Anti-Patterns Found

Não há `TBD`, `FIXME`, `XXX`, `TODO` nem `HACK` em `src/`, `tests/`, `README.md` e `pyproject.toml`. Há 6 `shortcut:` em `src/`, e todos dizem o limite.

| Ficheiro | Linha | Achado | Gravidade | Classificação e motivo |
|----------|-------|--------|-----------|------------------------|
| `src/strata/search.py`, `bricomarche.py`, `obras360.py` | 27; corte K | **WR-17**: na alargada, o corte K escolhe os pais sem a pergunta completa e o passo do 01-11 não recupera o que ficou de fora | 🛑 Blocker | **Lacuna bloqueante.** Prova ao vivo numa linha comum ("pavimento 60x120"): a Bricomarché vende 2 pavimentos 60X120 e a ferramenta mostra pavês de betão. A pesquisa à mão por "60x120" na loja ganha. Não é silencioso (vem "pesquisa alargada" e "+138 não expandidos"), mas é a falha que o utilizador rejeitou no UAT teste 5. Não é regressão: existia antes, e o 01-11 regista-a como limitação. Correção conhecida, de cerca de 5 linhas (01-REVIEW.md WR-17) |
| `src/strata/words.py` | 10, 51-53 | **WR-14**: a medida inteira conta a ordem e ignora o "×" | ⚠️ Warning (fica no mesmo plano do WR-17) | **Aviso, mas a corrigir com o WR-17.** É regressão reproduzida. Hoje não mordeu ao vivo: as lojas escrevem "60X120", não usam "×", e "pavimento 120x60" já dava 0 na pesquisa da loja antes de chegar ao filtro. Quando o WR-17 for corrigido, "pavimento 120x60" passa a expandir os "60X120", e o WR-14 rejeita-os. Medidas de azulejo e pavimento são comuns numa lista de obra, e o exemplo do SC3 da Phase 3 usa "×". Correção de 3 linhas |
| `src/strata/words.py` | 72-73 | **WR-15**: `broadened('tela 1 m x 25 m')` → 'tela x' | ⚠️ Warning | **Aviso.** É regressão reproduzida, mas numa forma estreita: unidade separada do número e "x" a seguir à unidade. "1m x 25m", "1 x 25 m" e "1x25m" continuam bem. Quando morde, sai "0 ofertas mostradas; N escondidas" e a nota "também sem ofertas com 'tela x'", não em silêncio. Correção de 1 condição; fazer no mesmo plano |
| `src/strata/search.py`, `report.py` | 63-64; 63-64 | **WR-16**: no ramo "tudo escondido", o cabeçalho e a linha `wide_only` contam os mesmos produtos com o mesmo motivo | ⚠️ Warning | **Aviso.** Nenhuma oferta some; a contagem engana (quem lê soma 5 + 1 quando há menos produtos diferentes). `test_tudo_escondido_alargada_com_ofertas_que_batem` fixa as duas frases. Correção de 1 linha (dizer "1.ª pesquisa: …" no cabeçalho) |
| `src/strata/words.py` | — | IN-13 (mts/mt/kgs), IN-14 (-m/-n junta fim/fino), IN-15 | ℹ️ Info | IN-14 vai para a Phase 3 com o WR-08; os outros são notas |
| `money.py`, `text.py`, `allmat.py`, `obras360.py`, `words.py` | — | WR-02 a WR-06, WR-09, IN-01 a IN-07, IN-09, IN-10, IN-12 | ⚠️/ℹ️ | Sem mudança desde a verificação anterior; os mesmos motivos |

### Proibições (must_haves.prohibitions)

| Proibição | Nível | Estado | Evidência |
|-----------|-------|--------|-----------|
| 01-10: nunca esconder a loja mais barata sem stock | test | ✓ VERIFIED | `test_offer_from_amostra_47412` (nota com 18,49 € em Coina) |
| 01-10: nunca filtrar pelo stock | test | ✓ VERIFIED | `test_offer_from_nenhuma_loja_com_stock` |
| 01-10: nunca fazer pedidos novos por causa do stock | judgment | ⚠️ veredicto não autoritativo: cumprida | `offer_from` só usa as `rows` que o adaptador já leu |
| 01-11: nunca esconder uma oferta sem a contar | test | ✓ VERIFIED | Testes `wide_only`; linha própria no report |
| 01-11: nunca mais do que uma tentativa extra (D-14) | test | ✓ VERIFIED | `store.calls == ["OSB 12mm", "OSB"]` |
| 01-11: alargada sem resultado quando nenhuma bate | test | ✓ VERIFIED | `test_alargada_sem_mistura_fica_como_antes`; ao vivo em "azulejo 30x30" |
| 01-01 a 01-09 | test/judgment | como antes | O UAT teste 7 (SHA1 do `.xlsx`) e o teste 8 (judgment) passaram |

### Testes do UAT que já passaram (2, 4, 6, 7, 8)

Não é preciso repeti-los. O código que mudou desde então não lhes toca:
- **Teste 2** (colar na consola): `text.py` não mudou. O report só ganhou uma linha nova.
- **Teste 4** (variante de 12 mm na Obras 360): o quick só mudou a ordem dos pais antes do corte. O preço e o link da variante não mudaram, e o 01-11 viu 19,37 € ao vivo.
- **Teste 6** ("perfis"): `_stem('perfis')` continua "perfi". Com uma só palavra, a chave nova do corte ordena como a antiga. `test_perfis_mostra_o_pai_perfil` passa.
- **Testes 7 e 8**: `sheet.py` e `fetch.py` não mudaram. O 01-10 e o 01-11 não fazem pedidos novos.

### Human Verification Required

Estes itens não entram no estado (gaps_found manda), mas ficam registados para o UAT:

1. **Re-teste 3 do UAT (G-01-3).** Correr `printf 'placa osb 9mm 1 un\n\n' | uv run python -m strata pesquisar` e abrir o link da 1.ª oferta da Bricomarché. Esperado: uma loja com stock (no 01-10 foi Ponte de Sor, 15,49 €, "68 em stock") e a nota "mais barata sem stock: 14,49 € em Coina - Barreiro". Porquê: o preço é desenhado por JavaScript e os stocks mudam.
2. **Re-teste 5 do UAT (G-01-5).** Correr a folha de 3 linhas (OSB 12 mm / un / 30; cimento cola / saco / 10; tinta branca / L / 15) com `pesquisar modelo.xlsx`. Esperado: em "OSB 12 mm", a placa de 12 mm em 1.º na Obras 360 (19,37 €), sem cola nem espuma; o resto contado em "+N ofertas escondidas: título sem 'OSB 12 mm'". Porquê: só uma pessoa compara com os sites. Atenção: este re-teste prova o caso citado, não a lacuna WR-17.
3. **Teste 1 do UAT (ignorado, sem Excel).** `uv run python -m strata modelo`, abrir no Excel e escrever "caixa" na Unidade. Esperado: lista com "m²" certo e o aviso. Porquê: não há Excel nesta máquina.
4. **Decisão sobre o SC3 e o STORE-01.** O texto ainda diz "o preço mais barato entre todas as lojas físicas, com o nome dessa loja e o link". Depois do 01-10, a oferta é a mais barata com stock, e a mais barata absoluta aparece na nota sem link. É preciso decidir entre atualizar o SC3 do ROADMAP e o STORE-01 (recomendado, porque foi o pedido do UAT) ou aceitar com um override:
   ```yaml
   overrides:
     - must_have: "A Bricomarché devolve o preço mais barato entre todas as lojas físicas, com o nome dessa loja e o link para a página do produto nessa loja"
       reason: "UAT teste 3 (G-01-3): a oferta é a loja mais barata com stock; a mais barata sem stock fica na nota com preço e loja (RES-02)"
       accepted_by: "<nome>"
       accepted_at: "<ISO>"
   ```
5. **Proibição judgment do 01-10** (nenhum pedido novo por causa do stock): ler `offer_from` em `src/strata/stores/bricomarche.py`. O veredicto do verificador (cumprida) não é autoritativo.

### Gaps Summary

**Uma lacuna bloqueante: o G-01-5 fora do caso citado (WR-17).**

O 01-11 pôs um filtro final que só olha para as ofertas já expandidas. Na alargada, a loja recebe só a palavra solta ("pavimento"), e os cortes K escolhem os pais pelo preço (Bricomarché) ou com todos empatados (Obras 360). Quando a palavra solta é genérica e a loja tem muitos produtos, o produto pedido nunca chega ao filtro. Ao vivo hoje, "pavimento 60x120" na Bricomarché mostra pavês de betão a 0,21 € e deixa de fora os pavimentos 60X120 que a loja vende a 34,55 €. É uma linha comum de obra, e uma pesquisa à mão por "60x120" na loja encontra-os. É também a falha que o utilizador rejeitou no UAT teste 5.

**Lacunas do UAT, no código:**
- **G-01-3: fechada.** Falta o re-teste 3.
- **G-01-5: fechada no caso citado** ("OSB 12 mm", poucos pais) **e aberta no caso geral** (WR-17). O re-teste 5 vai passar, porque o OSB tem poucos pais, mas não prova o caso geral.

**Classificação dos achados que o orquestrador pediu para pesar.** Usei o critério das verificações anteriores: só bloqueia o que faz a ferramenta perder para uma pesquisa à mão numa linha comum de obra, ao vivo, ou o que esconde ofertas em silêncio.

| Achado | Classe | Motivo |
|--------|--------|--------|
| WR-17 | **Lacuna bloqueante** | Prova ao vivo numa linha comum; a ferramenta perde para a pesquisa à mão. A Phase 3 não o recupera, porque classifica o que aparece e não expande pais |
| WR-14 | Aviso, a corrigir no mesmo plano do WR-17 | É regressão reproduzida, mas hoje não muda nada ao vivo (as lojas escrevem "60X120" e não usam "×"). Passa a morder assim que o WR-17 for corrigido, em "pavimento 120x60" |
| WR-15 | Aviso | É regressão numa forma estreita ("1 m x 25 m"), e falha à vista ("também sem ofertas com 'tela x'"). Correção de 1 condição |
| WR-16 | Aviso | A contagem engana, mas nada fica escondido |
| WR-07 | Corrigido | Sai do `deferred:` |

**Recomendação:** um plano de fecho, `/gsd-plan-phase 01 --gaps`, de cerca de 15 linhas. Leva o `rank=item.product` nos três adaptadores (WR-17), a medida sem ordem e com "×" (WR-14), o "x" sempre fora da alargada (WR-15) e "1.ª pesquisa:" no cabeçalho (WR-16). Cada um com um teste, mais uma corrida ao vivo de "pavimento 60x120 10 m²".

---

_Verificado: 2026-10-23T19:23:02Z_
_Verificador: Claude (gsd-verifier)_
