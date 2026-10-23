---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
verified: 2026-10-23T12:05:00Z
status: human_needed
score: 67/67 must-haves verified
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
covered_digest: "v3:sha256:859c9ed98fd732e617c61501608ebf0c2f34a92e2df05b8d887e26ae57ac25d7"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 60/61
  gaps_closed:
    - "Objetivo G / CR-05 ('perfis'): fechado. Ao vivo hoje, 'perfis' na Obras 360 mostra ofertas 'Perfil …' com preço e IVA da loja (1,45 € Perfil Cantoneira L, 1,49 € Perfil Canto Esquina, 1,55 € Perfil de Remate) e as escondidas descem de 122 para 33. Sobre fixtures: test_perfis_mostra_o_pai_perfil e 12 casos novos em test_title_matches"
    - "CR-04 (regressão do 01-08) no caso citado: 'parafuso m8' expande o pai M8 mesmo sendo o mais caro (test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte)"
    - "WR-10: loja com resultados e zero ofertas sem escondidas diz 'ok — 0 ofertas mostradas de N resultados da loja' (test_zero_ofertas_sem_escondidas_nao_diz_so_ok)"
    - "IN-08: broadened('tinta 15 litros') == 'tinta'"
  gaps_remaining: []
  regressions: []
deferred:
  - truth: "WR-07: 'azulejo 30x30' bate em 'Azulejo 30x60' (DIMS parte a medida e o conjunto perde a repetição)"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC3: 'o Tamanho (ex.: \"2500×1250×12 mm\") decide se as medidas de um anúncio batem'; SC2: 'os parecidos aparecem à parte dos exatos, com a diferença escrita'"
  - truth: "WR-08: o género junta barra/barro, banco/banca, tampo/tampa, lixa/lixo"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC2: 'Cada anúncio fica classificado como exato / parecido / outro'"
  - truth: "WR-11: 'osb 30mm' mostra as 7 espessuras pela gama '9-30MM' do nome do pai"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC1/SC2: especificações extraídas (espessura) e classificação exato/parecido; aceite no 01-08 (T-01-36) com shortcut: no código"
  - truth: "IN-11: colisões novas da tabela PLURAL (cal/Cais, mal/Mais, dois/Dol, abs/AB, eps/EP) e falsos positivos do mesmo tipo vistos ao vivo ('Varão Roscado … Fixação Perfil Teto' em 'perfis')"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC2: 'Cada anúncio fica classificado como exato / parecido / outro'; mesma família do WR-08; listado em Known Limitations do 01-09-SUMMARY e aceite em T-01-40"
behavior_unverified_items: []
coincidental_reliance_items: []
human_verification:
  - test: "uv run python -m strata modelo, abrir no Excel, clicar na coluna Unidade e escrever 'caixa'"
    expected: "Lista un, m², m, kg, L, saco com o '²' certo e o aviso 'Escolha da lista: …'"
    why_human: "Não há Excel nesta máquina"
  - test: "uv run python -m strata pesquisar numa consola normal do Windows, colar 'azulejo 2,5 m²' e Enter duas vezes"
    expected: "Linha 1 — azulejo (2,5 m²)"
    why_human: "Só o pipe foi testado; o '²' colado na consola depende da página de código"
  - test: "Abrir o link da Bricomarché de Coina - Barreiro da 1.ª oferta de OSB"
    expected: "Página do produto nessa loja, 14,49 € (placa 9 mm) ou 18,49 € (PLACA OSB 12 MM), preço com IVA (A9)"
    why_human: "O preço é desenhado por JavaScript e o IVA não está escrito na API"
  - test: "Abrir o link da variante '1 Placa 12 MM' da Obras 360"
    expected: "19,37 € com IVA (15,75 € sem IVA)"
    why_human: "Confirmar o que o comprador vê no site"
  - test: "Folha de 3 linhas (OSB 12 mm / un / 30; cimento cola / saco / 10; tinta branca / L / 15) e pesquisar modelo.xlsx; comparar com os sites (D5 do 01-08-SUMMARY)"
    expected: "Os preços mostrados batem com os dos sites; nenhuma loja 'ok' sem ofertas sem a frase da contagem"
    why_human: "Só uma pessoa compara com o que os sites mostram"
  - test: "Comparar a saída de 'printf \"perfis 10 un\\n\\n\" | uv run python -m strata pesquisar' com a pesquisa 'perfis' no site da Obras 360 (D6 do 01-09-SUMMARY)"
    expected: "Os perfis mais baratos do site estão entre as ofertas mostradas (o verificador correu-a hoje: 'Obras 360: ok', 1,45 € Perfil Cantoneira L, +33 escondidas, +77 pais não expandidos)"
    why_human: "A parte automática passou ao vivo; só uma pessoa confirma que o site não tem um perfil mais barato fora dos 20 pais expandidos"
  - test: "Correr pesquisar sobre uma folha e comparar o SHA1 do .xlsx antes e depois"
    expected: "Bytes iguais"
    why_human: "Proibição de nível test sem teste ligado (só inspeção: o único .save( está em write_template com open(path, 'xb'))"
  - test: "Ler src/strata/fetch.py e os SUMMARY do 01-07/01-09 (gravação --record; nenhum pedido ao vivo no 01-09)"
    expected: "Sem retentativas, proxies nem troca de identidade"
    why_human: "Proibições de nível judgment (veredicto do verificador não autoritativo: cumpridas)"
---

# Phase 1: Folha Excel e preços da Allmat, Bricomarché e Obras 360 — Relatório de verificação

**Objetivo da fase:** O utilizador preenche o modelo Excel da app, passa o caminho do `.xlsx` à linha de comandos e recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360, já com IVA 23% e preço unitário normalizado, com o estado de cada loja sempre visível; para uma pesquisa rápida pode colar texto em vez da folha
**Verificado:** 2026-10-23T12:05:00Z
**Estado:** human_needed
**Reverificação:** Sim, a segunda, depois do plano de fecho 01-09

## Resposta curta

A lacuna anterior (CR-05, "perfis") está fechada, e confirmei-o ao vivo: `printf 'perfis 10 un\n\n' | uv run python -m strata pesquisar` deu código 0 em 20 s, com "Obras 360: ok" e ofertas "Perfil …" com preço e IVA da loja. As escondidas desceram de 122 para 33. Não há lacunas bloqueantes. O CR-06, o WR-12 e o WR-13 são reais mas ficam como avisos: ao vivo não morderam e, quando mordem, a app mostra a contagem em vez de esconder em silêncio. O estado é human_needed só por causa das verificações manuais do fim da fase.

## User Flow Coverage

| Passo | Esperado | Evidência | Estado |
|-------|----------|-----------|--------|
| 1. Obter o modelo | `modelo` grava o modelo; não sobrescreve | `test_sheet.py`; inalterado desde a última verificação | ✓ |
| 2. Preencher e passar o `.xlsx` | Cada linha válida vira item | `read_sheet`, `test_sheet.py`, `test_e2e.py`; corrida ao vivo da folha de 3 linhas na verificação anterior (código não mudou) | ✓ |
| 3. Preços das 3 lojas por linha | Ofertas de cada loja que vende o produto | Ao vivo hoje: "perfis" → Bricomarché 5 ofertas "Perfis …", Obras 360 5 ofertas "Perfil …"; Allmat "sem resultados" | ✓ |
| 4. IVA 23% e preço unitário | Preço, origem do IVA, €/unidade, stock | Ao vivo: "IVA: indicado pela loja (tax_percentage=23) · 1,45 €/un · 2503 em stock · escalões …" | ✓ |
| 5. Estado de cada loja visível | As 3 lojas sempre presentes | As 3 secções na corrida "perfis"; `verificar` ao vivo 4 × OK (código 0, 51 s); WR-10 fechado | ✓ |
| 6. Pesquisa rápida colada | Descrição, quantidade e unidade | A corrida ao vivo usou a entrada colada ("Linha 1 — perfis (10 un)") | ✓ |

## Goal Achievement

### Observable Truths — critérios do ROADMAP e objetivo

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| G | O utilizador recebe, para cada linha, os preços na hora das três lojas | ✓ VERIFIED | Fechado para "tinta branca", "OSB 12 mm", "osb 18mm" (01-07/01-08) e agora "perfis" (ao vivo hoje). Plurais comuns de obra testados: 60 pares (buchas, varões, painéis, pincéis, tampões, ferragens, canais, lençóis…), todos True |
| SC1 | Modelo Excel, linha de comandos com o `.xlsx`, linhas inválidas com número e motivo | ✓ VERIFIED | `sheet.py`, `test_sheet.py`; ficheiros fora do diff do 01-09 |
| SC2 | Lista colada lida com descrição, quantidade e unidade; texto livre sem categoria | ✓ VERIFIED | `text.parse_line`; corrida ao vivo por texto colado |
| SC3 | Bricomarché loja física mais barata com nome e link; Allmat caixa convertida; Obras 360 todas as variantes, IVA, escalões | ✓ VERIFIED | Ao vivo: "loja: Fafe · com stock: 1,59 € em Arrifana", variantes "— 28X28MM com 3,00 m", escalões "−3% a partir de 30"; `test_osb_12mm_so_a_variante_de_12mm` |
| SC4 | Preço com IVA, origem do IVA, preço unitário, stock, sem filtrar | ✓ VERIFIED | `report._offer_lines`; ao vivo em todas as ofertas. Ofertas "ML" dizem "unidade da loja 'ML' sem conversão" (não inventam €/m) |
| SC5 | Estado das três lojas por item; `verificar` por adaptador | ✓ VERIFIED | `verificar` ao vivo hoje: 4 × OK, código 0 |

### Observable Truths — must_haves dos planos

| Plano | Verdades | Estado | Evidência |
|-------|----------|--------|-----------|
| 01-01 (8) | modelo, secções por loja, "sem resultados", preço/IVA/stock/link, linhas inválidas, ordem, "+N não mostradas", sem ficheiros | 8/8 ✓ | Suite 177 passed; ficheiros sem mudança |
| 01-02 (12) | testes sem rede, folha, texto colado, avisos | 12/12 ✓ | `test_sheet.py`, `test_text.py` |
| 01-03 (7) | D-14, D-15 contado, ordem, estados | 7/7 ✓ | `test_pesquisa_alargada_*`, `test_estados_*` |
| 01-04 (6) | Bricomarché | 6/6 ✓ | `test_bricomarche.py`; ao vivo hoje |
| 01-05 (7) | Obras 360 variantes, IVA, escalões | 7/7 ✓ | `test_obras360.py` (27 passed) |
| 01-06 (4) | `verificar`; folha de 3 linhas | 4/4 ✓ | `verificar` ao vivo hoje; folha de 3 linhas ao vivo na verificação anterior |
| 01-07 (5) | "tinta branca", género/plurais, palavras inteiras, cabeçalho com escondidas, alargada com medidas | 5/5 ✓ | `test_tinta_branca_gravada_mostra_as_tintas_brancas`, `test_tudo_escondido_*` |
| 01-08 (6) | "OSB 12 mm" com o pai; dois níveis; LxCxE; Lt/OSB3; `verificar` | 6/6 ✓ | `test_osb_12mm_so_a_variante_de_12mm`, `test_medidas_coladas_por_x_batem_no_filtro` |
| 01-09 (6) | ver abaixo | 6/6 ✓ | ver abaixo |

**01-09, verdade a verdade:**

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| 1 | "perfis" na Obras 360 expande o pai "Perfil …", mostra variantes com preço, "ok" e "+1 ofertas escondidas: título sem 'perfis'" | ✓ VERIFIED | `test_perfis_mostra_o_pai_perfil` passa; ao vivo hoje, ofertas "Perfil …" com IVA |
| 2 | Plurais -ais/-eis/-ois/-uis/-ens/-aes/-oes e -is/-il → -i; guardas lápis/jacuzzis/táxis True, aquecimento/porta/ip65 False | ✓ VERIFIED | `words.py:24-37` (`PLURAL`, `len(w) <= 2`, ciclo); `test_title_matches` 35 casos; reproduzido à mão |
| 3 | "parafuso m8" expande o M8 mais caro; 20 pedidos de detalhe | ✓ VERIFIED | `obras360.py:129-130`; `test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte`. Limite: CR-06 (aviso) |
| 4 | Zero ofertas sem escondidas → "ok — 0 ofertas mostradas de N resultados da loja" | ✓ VERIFIED | `search.py:53-56`; `test_zero_ofertas_sem_escondidas_nao_diz_so_ok` |
| 5 | `broadened('tinta 15 litros') == 'tinta'` | ✓ VERIFIED | `UNIT_TOKENS` na linha 13; reproduzido à mão |
| 6 | Os 161 testes de HEAD continuam verdes | ✓ VERIFIED | `uv run python -m pytest -q` → 177 passed (161 + 16) |

**Score:** 67/67 verdades verificadas (0 presentes sem prova de comportamento). As verdades de comportamento têm testes com nome, corridos hoje (43 + 5 passed), e a do "perfis" também passou ao vivo.

### Deferred Items

| # | Item | Fase | Evidência |
|---|------|------|-----------|
| 1 | WR-07 "azulejo 30x30" bate em "30x60" | Phase 3 | SC3: o Tamanho decide se as medidas batem |
| 2 | WR-08 barra/barro, tampo/tampa | Phase 3 | SC2: exato / parecido / outro |
| 3 | WR-11 "osb 30mm" mostra as 7 espessuras | Phase 3 | SC1/SC2; aceite no 01-08 (T-01-36) |
| 4 | IN-11 cal/Cais, mal/Mais, abs/AB, eps/EP; "Varão Roscado … Fixação Perfil Teto" em 1.º lugar ao vivo em "perfis" | Phase 3 | SC2; aceite no 01-09 (T-01-40) |

Os quatro são falsos positivos: aparece um produto a mais, com o título à vista. A Phase 3 separa-os.

### Advisory (New Scope, Unevidenced)

Nenhum. Reproduzi de forma determinística todos os achados novos da revisão (CR-06, WR-12, WR-13, IN-11) e classifiquei-os abaixo.

### Required Artifacts

`verify.artifacts`: 01-01 7/7, 01-02 6/6, 01-03 4/4, 01-04 2/2, 01-05 2/3, 01-06 3/3, 01-07 4/4, 01-08 4/4, 01-09 5/5.

| Artefacto | Esperado | Estado | Detalhe |
|-----------|----------|--------|---------|
| `src/strata/words.py` | `PLURAL`, `len(w) <= 2`, `UNIT_TOKENS` com litros | ✓ VERIFIED | Ligado: `title_matches` → `words` → `_stem`, usado por `obras360.py`, `bricomarche.py`, `allmat.py` |
| `src/strata/stores/obras360.py` | `not title_matches(query` na chave do corte | ✓ VERIFIED | 3 `shortcut:` mantidos; `hidden` continua a contar pais e variantes cortados |
| `src/strata/search.py` | "resultados da loja" | ✓ VERIFIED | Chega ao cabeçalho por `StoreResult.detail` → `report.print_item` |
| `tests/test_obras360.py` | `test_perfis_mostra_o_pai_perfil`, `test_pai_com_a_pesquisa_completa_…` | ✓ VERIFIED | Passam |
| `tests/test_search.py` | `test_zero_ofertas_sem_escondidas_nao_diz_so_ok`, 12 casos novos | ✓ VERIFIED | Passam |
| `tests/test_obras360.py` (01-05) | contém "DiscountByQuantity" | ℹ️ padrão em falta | Igual às verificações anteriores: os escalões são testados sobre a fixture; não é stub |

### Key Link Verification

`verify.key-links`: 01-01 4/4, 01-02 3/3, 01-03 3/3, 01-04 3/3, 01-05 3/3, 01-06 2/2, 01-07 3/3, 01-08 2/2, 01-09 3/3. Confirmado à mão: `for suf, rep in PLURAL` (words.py:33), `not title_matches(query` (obras360.py:129), "resultados da loja" (search.py:56) e o `detail` no cabeçalho da corrida ao vivo.

### Data-Flow Trace (Level 4)

| Artefacto | Dado | Origem | Dados reais | Estado |
|-----------|------|--------|-------------|--------|
| `report.print_item` | `sr.offers[].price` | APIs das 3 lojas (Decimal) | Sim, ao vivo hoje ("perfis", `verificar`) | ✓ FLOWING |
| `report.print_item` | `sr.detail` | `search_store` | Sim, no teste WR-10 e nos `tudo_escondido` | ✓ FLOWING |
| `obras360.search` | `hidden` | pais escondidos + variantes cortadas | Sim ("+33 ofertas escondidas" ao vivo) | ✓ FLOWING |

### Behavioral Spot-Checks

| Comportamento | Comando | Resultado | Estado |
|---------------|---------|-----------|--------|
| Suite sem rede (uma vez) | `uv run python -m pytest -q` | 177 passed | ✓ PASS |
| Testes nomeados do 01-09 | `pytest tests/test_search.py -k "title_matches or broadened or zero_ofertas or verificar_todos_a_zero"`; `pytest tests/test_obras360.py -k "perfis or frente_do_corte or osb_12mm or tinta_branca or so_20_detalhes"` | 43 passed; 5 passed | ✓ PASS |
| **CR-05 ao vivo (D6)** | `printf 'perfis 10 un\n\n' \| uv run python -m strata pesquisar` | código 0, 20 s. Obras 360 "ok": 1,45 € Perfil Cantoneira L, 1,49 € e 1,51 € Perfil Canto Esquina, 1,55 € Perfil de Remate; "+21 não mostradas", "+33 escondidas" (antes 122), "+77 pais não expandidos". Bricomarché 5 "Perfis …"; Allmat "sem resultados" | ✓ PASS |
| `verificar` ao vivo | `uv run python -m strata verificar` | 4 × OK, código 0, 51 s | ✓ PASS |
| Plurais de obra | script com `title_matches` (60 pares: buchas, varões, tubos, painéis, tijolos, rodapés, pincéis, tampões, dobradiças, disjuntores…) | todos True; guardas aquecimento/porta False | ✓ PASS |
| CR-06 sintético | `FakeFetcher`: 25 parafusos genéricos + M8 a 99 €, "parafuso m8x40" | M8 não expandido, 40 pedidos, 140 ofertas marcadas "pesquisa alargada", detail "140 escondidas pelo filtro de título com 'parafuso m8x40'". Com 10 genéricos (≤ K) o M8 é expandido | ✗ (aviso) |
| CR-06 ao vivo (só listas, 1 pedido cada) | Obras 360: "parafuso m8x40", "parafuso m6x60", "lâmpada e27 10w", "varão roscado m8", "bucha 8x50" | Todos `total_products = 0`: a pesquisa da loja com números é estreita e o caso do CR-06 (mais de 20 pais soltos) não aparece. "parafuso" sozinho dá 42 produtos | ⚠️ sem efeito observado |
| WR-12/WR-13/IN-11 | script com `title_matches`/`broadened` | Reproduzidos como na revisão (geotêxteis, coxins, jardins False; "tubo 3 metros" → alargada "tubo metros"; cal/Cais, abs/AB True) | — |

### Probe Execution

Não há probes (`scripts/*/tests/probe-*.sh`) nem probes declarados nos planos. Passo não aplicável.

### Requirements Coverage

Os 12 IDs da fase aparecem no `requirements` de pelo menos um plano (01-09: LIST-02, STORE-03, STORE-05). Nenhum órfão.

| Requisito | Planos | Estado | Evidência |
|-----------|--------|--------|-----------|
| LIST-01 | 01-02 | ✓ SATISFIED | `text.py`, `test_text.py`; entrada colada ao vivo |
| LIST-02 | 01-01/02/03/07/08/09 | ✓ SATISFIED (avisos WR-12, WR-13) | Qualquer produto vai à pesquisa sem categoria; plurais comuns batem; "perfis" ao vivo |
| LIST-04 | 01-01/02 | ✓ SATISFIED | `write_template` |
| LIST-05 | 01-01/02 | ✓ SATISFIED | `read_sheet` |
| STORE-01 | 01-04/08 | ✓ SATISFIED | Loja física mais barata e loja com stock ao vivo |
| STORE-02 | 01-03 | ✓ SATISFIED | `parse_box`; `verificar` (pavimento) OK |
| STORE-03 | 01-05/07/08/09 | ✓ SATISFIED (aviso CR-06) | Variantes, IVA e escalões ao vivo; pai pedido à frente do corte |
| STORE-05 | 01-01/02/03/06/07/09 | ✓ SATISFIED | Estado sempre visível; zero ofertas → contagem no cabeçalho (WR-10 fechado) |
| STORE-07 | 01-06 | ✓ SATISFIED | 4 × OK ao vivo |
| PRICE-01 | 01-01/02/04/05/07 | ✓ SATISFIED | Três origens do IVA |
| PRICE-02 | 01-03/05 | ✓ SATISFIED (aviso WR-02) | `per_unit`, `in_unit` |
| RES-02 | 01-01/02/04/05 | ✓ SATISFIED | Stock ao vivo |

ℹ️ A tabela de rastreio do REQUIREMENTS.md continua incoerente: LIST-01, LIST-04, LIST-05, STORE-01, STORE-02, STORE-07, PRICE-01, PRICE-02 e RES-02 aparecem como "Gaps Found" e sem visto. Nenhuma lacuna lhes tocou. Acertar ao fechar a fase.

### Anti-Patterns Found

Sem `TBD`/`FIXME`/`XXX`/`TODO`/`HACK` em `src/`, `tests/`, `README.md` e `pyproject.toml`. Há 6 `shortcut:` em `src/` e todos dizem o limite e quando rever.

| Ficheiro | Linha | Achado | Gravidade | Classificação e motivo |
|----------|-------|--------|-----------|------------------------|
| `src/strata/stores/obras360.py` | 129-130 | CR-06: a chave só põe à frente os pais que batem na pesquisa **completa**; "parafuso m8x40" não bate em "Parafuso Sextavado M8" e o corte volta ao preço | ⚠️ Warning (limite) | **Aviso, não lacuna.** Reproduzido só com pais sintéticos. Precisa de a loja devolver mais de 20 pais soltos para uma pesquisa com uma medida que só existe na variante. Ao vivo, as 5 pesquisas com números deram 0 produtos, e com 0 o caminho é a alargada normal (D-14), igual a antes do 01-08. Quando morde, a app não esconde em silêncio: as ofertas vêm marcadas "pesquisa alargada: 'parafuso'" e o cabeçalho diz "N escondidas pelo filtro de título com 'parafuso m8x40'". Uma pesquisa à mão "parafuso m8x40" no site também dá zero, por isso a ferramenta não perde para ela. Correção de 2 linhas (contar palavras em comum, a do 01-REVIEW.md). Recomendo fazê-la num `/gsd-quick` antes da Phase 2, não bloquear |
| `src/strata/words.py` | 24-25 | WR-12: -ins/-ons/-uns e -eis átono (geotêxteis, coxins, jardins) | ⚠️ Warning | **Aviso.** O mesmo mecanismo do CR-05, mas em formas raras numa lista de obra: "manta geotêxtil" no singular bate. Testei 60 plurais comuns de obra e todos batem. Quando falha, a loja mostra "0 ofertas mostradas; N escondidas pelo filtro de título" no cabeçalho, por isso não é omissão silenciosa. Recomendo juntar `("ins","im"), ("ons","om"), ("uns","um")` no mesmo `/gsd-quick` |
| `src/strata/words.py` | 9, 13 | WR-13: "metros", "quilos", "unidades", "l." | ⚠️ Warning (no limite) | **Aviso, no limite.** "tubo 3 metros" esconde "Tubo 3m" e a alargada procura "tubo metros". Mas na folha a medida vai para a coluna Tamanho (D-13 só pesquisa o Produto), e as formas "3m" e "3 m" batem. Quando falha, aparece "também sem ofertas com 'tubo metros'" e a contagem. Recomendo corrigir no mesmo `/gsd-quick` (cerca de 5 linhas), porque o texto colado em português corrente pode trazer a unidade por extenso. Não é da Phase 3: a Phase 3 classifica o que aparece e não recupera o que o filtro escondeu |
| `src/strata/words.py` | 24-25, 31 | IN-11: cal/Cais, mal/Mais, abs/AB, eps/EP | ℹ️ Info | Falsos positivos com o título à vista. Passa para a Phase 3 (SC2), como o WR-08 |
| `src/strata/search.py`, `obras360.py` | 53-56, 118-122 | IN-12: "0 de N resultados" sem nota se a lista vier vazia com `total_products > 0` | ℹ️ Info | O "0 de N" está à vista; falta só o motivo. Mesmo campo do WR-06 |
| `src/strata/money.py`, `text.py`, `allmat.py`, `obras360.py`, `words.py` | — | WR-02 a WR-06, WR-09, IN-01 a IN-07, IN-09, IN-10 | ⚠️/ℹ️ | Sem mudança desde a verificação anterior; mesmos motivos |

### Proibições (must_haves.prohibitions)

| Proibição | Nível | Estado | Evidência |
|-----------|-------|--------|-----------|
| 01-09: nunca "ok" sozinho com resultados e zero ofertas | test | ✓ VERIFIED | `test_zero_ofertas_sem_escondidas_nao_diz_so_ok`; os `test_tudo_escondido_*` |
| 01-09: nunca esconder um pai ou variante sem o contar | test | ✓ VERIFIED | `obras360.py:151`; `test_perfis_…` (hidden == 1), `test_osb_12mm_…` (hidden == 6); pais fora do corte → "+N produtos não expandidos" |
| 01-09: nunca contornar a proteção nem passar o ritmo | judgment | ⚠️ veredicto não autoritativo: cumprida | `conftest.no_network` (autouse) bloqueia a rede nos testes; o 01-09 não fez pedidos ao vivo. Revisão humana recomendada |
| 01-07/01-08 e anteriores (test) | test | ✓ VERIFIED | Testes com nome inalterados e verdes |
| Nunca escrever o `.xlsx` do utilizador | test | ⚠️ sinalizada | Só inspeção (nenhum `.save(` fora de `write_template`); falta um teste de bytes iguais |
| Nunca contornar a proteção das lojas (gravação 01-07) | judgment | ⚠️ veredicto não autoritativo: cumprida | `fetch.py` sem retentativas nem proxies |

### Human Verification Required

Ficam para o UAT do fim da fase. São a única razão para o estado não ser `passed`.

1. **Lista da Unidade no Excel.** `uv run python -m strata modelo`, abrir no Excel, escrever "caixa" na Unidade. Esperado: lista com "m²" certo e o aviso. Porquê: não há Excel aqui.
2. **Colar numa consola normal do Windows.** Colar `azulejo 2,5 m²` em `pesquisar`. Esperado: "Linha 1 — azulejo (2,5 m²)". Porquê: só o pipe foi testado.
3. **Link da Bricomarché (Coina - Barreiro).** Esperado: 14,49 € (9 mm) ou 18,49 € (12 mm), com IVA (A9). Porquê: preço desenhado por JavaScript.
4. **Variante de 12 mm da Obras 360.** Esperado: 19,37 € com IVA. Porquê: confirmar o que o comprador vê.
5. **Folha de 3 linhas contra os sites** (OSB 12 mm / cimento cola / tinta branca; D5 do 01-08). Porquê: só uma pessoa compara com os sites.
6. **"perfis" contra o site da Obras 360** (D6 do 01-09). A parte automática passou ao vivo hoje. Falta confirmar que não há um perfil mais barato fora dos 20 pais expandidos (+77 não expandidos, `shortcut:` K = 20).
7. **O `.xlsx` do utilizador fica igual:** SHA1 antes e depois de `pesquisar`.
8. **Proibições judgment** (ritmo, gravação): ler `fetch.py` e os SUMMARY.

### Gaps Summary

**Sem lacunas bloqueantes.**

**Lacuna anterior (CR-05, "perfis"): FECHADA.** O `_stem` tem agora a tabela `PLURAL` (words.py:24-37). Ao vivo, "perfis" mostra os perfis da Obras 360 com preço e IVA, e as escondidas descem de 122 para 33. Sobre fixtures, `test_perfis_mostra_o_pai_perfil` e os 12 casos novos passam. Os 60 plurais comuns de obra que testei batem todos.

**Classificação dos achados que o orquestrador pediu para pesar.** Usei o mesmo critério das duas verificações anteriores: só bloqueia o que faz a ferramenta perder para uma pesquisa à mão numa linha comum de obra, ao vivo.

| Achado | Classe | Motivo |
|--------|--------|--------|
| CR-06 | Aviso (recomendo corrigir antes da Phase 2) | Real, mas só com pais sintéticos. Ao vivo a Obras 360 devolve 0 para pesquisas com números, por isso o caso não aparece. Quando morde, o resultado vem marcado "pesquisa alargada" e com a contagem. A pesquisa à mão também dá zero. Correção de 2 linhas |
| WR-12 | Aviso | Mecanismo do CR-05, mas em plurais raros numa lista de obra (os singulares batem). Falha com a contagem no cabeçalho, não em silêncio |
| WR-13 | Aviso, no limite (recomendo corrigir já) | "tubo 3 metros" falha mesmo depois da alargada. Mas a medida vai para a coluna Tamanho na folha, "3m"/"3 m" batem e a falha mostra a contagem. Não é da Phase 3, que não recupera o que o filtro esconde |
| IN-11 | Phase 3 | Falsos positivos com o título à vista (SC2) |
| IN-12 | Info | "0 de N" à vista; falta só o motivo |
| WR-07, WR-08, WR-11 | Phase 3 | Como antes (`deferred:`) |

**Recomendação:** um `/gsd-quick` de cerca de 10 linhas antes da Phase 2: a chave do CR-06 (palavras em comum), os três pares do WR-12 e as unidades por extenso do WR-13, cada um com um caso em `test_title_matches`/`test_broadened`. Não bloqueia o fecho da fase.

---

_Verificado: 2026-10-23T12:05:00Z_
_Verificador: Claude (gsd-verifier)_
