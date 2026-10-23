---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
verified: 2026-10-23T11:04:54Z
status: gaps_found
score: 60/61 must-haves verified
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
covered_digest: "v3:sha256:8994548964f43f93d8ad760753c6a4cebec73ec43b71099b35f2434227c92195"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 48/50
  gaps_closed:
    - "'tinta branca' na Obras 360: as 4 tintas brancas aparecem com preço e IVA da loja (confirmado ao vivo hoje e sobre respostas gravadas) — CR-01 nos casos citados"
    - "Loja com produtos e tudo escondido pelo filtro já não diz só 'ok': '0 ofertas mostradas; N escondidas pelo filtro de título' e pesquisa alargada uma vez com medidas — WR-01"
    - "'OSB 12 mm' na Obras 360 com o pai 'Placa OSB 9-30MM' devolvido mostra a variante de 12 mm a 19,37 € — CR-02; a coincidental reliance do SC3 fica fechada"
    - "Medidas LxCxE, '15 Lt'/'15 litros' e 'OSB3' batem no filtro; a Bricomarché expande 'Chapa Osb 2440X590X18Mm' para 'osb 18mm' — CR-03"
    - "01-06, 4.ª verdade: a folha de 3 linhas (OSB 12 mm / cimento cola / tinta branca) mostra ofertas por linha nas três lojas (corrida ao vivo hoje)"
  gaps_remaining:
    - "Objetivo G: o filtro de título continua a esconder o produto pedido para plurais em -is/-ais/-ens/-óis (CR-05). Confirmado ao vivo: 'perfis' na Obras 360 → 'ok' com 8 ofertas erradas (parafusos e pivots 'para perfis') e 122 escondidas, entre elas pelo menos 36 pais 'Perfil …' só na 1.ª página"
  regressions:
    - "CR-04 (01-08): a escolha dos pais da Obras 360 com broadened() tira também códigos de modelo (M8, E27) e o corte K=20 por preço pode deixar de fora o pai pedido. Classificado como aviso, não lacuna (ver Gaps Summary)"
    - "WR-07 (01-08): 'azulejo 30x30' bate em 'Azulejo 30x60' (antes não batia). Falso positivo; a separação de medidas é da Phase 3"
gaps:
  - truth: "O utilizador recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360 (objetivo da fase)"
    status: partial
    reason: "Os casos da lacuna anterior estão fechados, mas o mesmo mecanismo (filtro de título esconde o produto que a loja vende) continua com plurais que _stem não trata. Reproduzido AO VIVO hoje: 'perfis' (perfis de gesso cartonado, termo comum numa lista de obra) → 'Obras 360: ok' com 8 ofertas que não são perfis (parafusos 'para perfis', pivots, um kit de união) e '+122 ofertas escondidas: título sem 'perfis''. Uma leitura só da lista da loja mostra 36 pais 'Perfil …' escondidos na 1.ª página (130 produtos no total). Como passam algumas ofertas erradas, o detalhe do WR-01 não dispara e o cabeçalho diz só 'ok'. Uma pesquisa à mão no site ganha à ferramenta (Core Value)."
    artifacts:
      - path: "src/strata/words.py"
        issue: "_stem (linhas 25-35) só trata -oes, -eis e -s, e deixa iguais as palavras com 3 letras ou menos: perfis/perfil, canais/canal, terminais/terminal, ferragens/ferragem, lençóis/lençol e pás/pá dão False (reproduzido)"
    missing:
      - "Tratar em _stem os plurais -ais→al, -ois→ol, -uis→ul, -ens→em, -aes→ao e -is→il (o 01-REVIEW.md CR-05 traz a tabela PLURAL pronta) e baixar o limite para palavras de 2 letras, para 'pás' bater em 'Pá'"
      - "Casos em test_title_matches: ('perfis','Perfil alumínio',True), ('canais','Canal',True), ('ferragens','Ferragem',True), ('lençóis','Lençol',True), ('pás','Pá',True), e guardas: ('lápis','Lápis',True), ('aquecimento','Cimento cola',False)"
      - "Um teste de ponta a ponta na Obras 360 para 'perfis' (lista gravada com --record ou sintética com um pai 'Perfil Montante …') a provar que o pai Perfil é expandido e mostrado"
deferred:
  - truth: "WR-07: 'azulejo 30x30' bate em 'Azulejo 30x60' (DIMS parte a medida e o conjunto perde a repetição)"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC3: 'o Tamanho (ex.: \"2500×1250×12 mm\") decide se as medidas de um anúncio batem'; SC2: 'os parecidos aparecem à parte dos exatos, com a diferença escrita'"
  - truth: "WR-08: o género junta barra/barro, banco/banca, tampo/tampa, lixa/lixo"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC2: 'Cada anúncio fica classificado como exato / parecido / outro'"
  - truth: "WR-11: 'osb 30mm' mostra as 7 espessuras pela gama '9-30MM' do nome do pai"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC1/SC2: especificações extraídas (espessura) e classificação exato/parecido; o 01-08 aceitou-o em T-01-36 com shortcut: no código"
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
    why_human: "Só uma pessoa compara com o que os sites mostram (a corrida ao vivo do verificador mostrou ofertas nas 3 linhas)"
  - test: "Ler src/strata/fetch.py e o 01-07-SUMMARY (gravação --record)"
    expected: "Sem retentativas, proxies nem troca de identidade; a gravação foi uma só corrida pelo Fetcher normal"
    why_human: "Proibições de nível judgment (veredicto do verificador não autoritativo: cumpridas)"
  - test: "Correr pesquisar sobre uma folha e comparar o SHA1 do .xlsx antes e depois"
    expected: "Bytes iguais"
    why_human: "Proibição de nível test sem teste ligado (só inspeção: o único .save( está em write_template com open(path, 'xb'))"
---

# Phase 1: Folha Excel e preços da Allmat, Bricomarché e Obras 360 — Relatório de verificação

**Objetivo da fase:** O utilizador preenche o modelo Excel da app, passa o caminho do `.xlsx` à linha de comandos e recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360, já com IVA 23% e preço unitário normalizado, com o estado de cada loja sempre visível; para uma pesquisa rápida pode colar texto em vez da folha
**Verificado:** 2026-10-23T11:04:54Z
**Estado:** gaps_found
**Reverificação:** Sim — depois dos planos de fecho 01-07 e 01-08

## Resposta curta

A lacuna anterior está fechada nos casos que a definiam: "tinta branca" mostra as 4 tintas brancas da Obras 360 ao vivo, "OSB 12 mm" mostra a placa de 12 mm mesmo quando a loja devolve o pai, e uma loja com tudo escondido já não diz só "ok". Fica uma lacuna estreita, com a mesma causa: o `_stem` não conhece os plurais em -is/-ais/-ens/-óis. Confirmei ao vivo: "perfis" na Obras 360 dá "ok" com 8 produtos errados e esconde pelo menos 36 perfis. A correção cabe numa função (a tabela `PLURAL` do CR-05). O CR-04 é uma regressão real do 01-08, mas fica como aviso: ao vivo não esconde o mais barato e, quando morde, a app avisa.

## Nota sobre o modo MVP

O ROADMAP marca a fase com `**Mode:** mvp`, mas o objetivo no ROADMAP não está no formato de história de utilizador. Os planos 01-07 e 01-08 já trazem a história ("As a comprador de materiais de obra…, I want to…, so that vejo para cada linha os preços…"). Usei esse `[outcome]` para a tabela abaixo. Para o ROADMAP ficar coerente, correr `/gsd-mvp-phase 1`.

## User Flow Coverage

| Passo | Esperado | Evidência | Estado |
|-------|----------|-----------|--------|
| 1. Obter o modelo | `modelo` grava o modelo; não sobrescreve | Pasta nova: código 0; 2.ª vez código 1 | ✓ |
| 2. Preencher e passar o `.xlsx` | Cada linha válida vira item | Modelo preenchido com openpyxl (3 linhas) → `pesquisar modelo.xlsx` ao vivo, código 0, 26 s | ✓ |
| 3. Preços das 3 lojas por linha | Ofertas de cada loja que vende o produto | Ao vivo: as 3 linhas com ofertas (Obras 360 "tinta branca": 56,02 € a 135,41 €). **"perfis": Obras 360 "ok" com produtos errados e 36+ perfis escondidos** | ✗ parcial |
| 4. IVA 23% e preço unitário | Preço, origem do IVA, €/unidade, stock | "IVA: indicado pela loja (tax_percentage=23)", "regra da loja (DL 138/90)" | ✓ |
| 5. Estado de cada loja visível | As 3 lojas sempre presentes | "Allmat: sem resultados — também sem resultados com 'OSB'"; `verificar` 4 × OK | ✓ (aviso WR-10) |
| 6. Pesquisa rápida colada | Descrição, quantidade e unidade | `parse_line("azulejo 2,5 m²")` → azulejo / 2.5 / m² | ✓ |

## Goal Achievement

### Observable Truths — critérios do ROADMAP e objetivo

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| G | O utilizador recebe, para cada linha, os preços na hora das três lojas | ✗ FAILED (parcial) | Fechado para "tinta branca", "OSB 12 mm", "osb 18mm", "cola de contacto". Continua para plurais -is/-ais/-ens/-óis: "perfis" ao vivo (ver Gaps Summary) |
| SC1 | Modelo Excel, linha de comandos com o `.xlsx`, linhas inválidas com número e motivo | ✓ VERIFIED | `sheet.py`, `test_sheet.py`; corrida ao vivo com o modelo preenchido |
| SC2 | Lista colada lida com descrição, quantidade e unidade; texto livre sem categoria | ✓ VERIFIED | `text.parse_line`; `test_text.py`; só o Produto vai para a pesquisa |
| SC3 | Bricomarché loja física mais barata com nome e link; Allmat caixa convertida; Obras 360 todas as variantes, IVA, escalões | ✓ VERIFIED | Ao vivo "18,49 € PLACA OSB 12 MM", escalões na Colorite; `test_osb_12mm_so_a_variante_de_12mm` prova o caminho do pai devolvido, por isso a coincidental reliance anterior fica fechada |
| SC4 | Preço com IVA, origem do IVA, preço unitário, stock, sem filtrar | ✓ VERIFIED | `report._offer_lines`; ao vivo em todas as ofertas. WR-02 (packs) continua aviso |
| SC5 | Estado das três lojas por item; `verificar` por adaptador | ✓ VERIFIED | `verificar` ao vivo hoje: 4 × OK, código 0, 28 s. Aviso WR-10 |

### Observable Truths — must_haves dos planos

| Plano | Verdades | Estado | Evidência |
|-------|----------|--------|-----------|
| 01-01 (8) | modelo, secções por loja, "sem resultados", preço/IVA/stock/link, linhas inválidas, ordem, "+N não mostradas", sem ficheiros | 8/8 ✓ | Suite 161 passed; sem regressão |
| 01-02 (12) | testes sem rede, folha, texto colado, avisos | 12/12 ✓ | `test_sheet.py`, `test_text.py`; `pesquisar nao-existe.xlsx` → código 2 |
| 01-03 (7) | D-14, D-15 contado, ordem, estados | 7/7 ✓ | `test_pesquisa_alargada_*`, `test_estados_*`; D-14 agora também com tudo escondido |
| 01-04 (6) | Bricomarché | 6/6 ✓ | `test_bricomarche.py`; ao vivo |
| 01-05 (7) | Obras 360 variantes, IVA, escalões | 7/7 ✓ | `test_obras360.py` (25 passed) |
| 01-06 (4) | `verificar`; folha de 3 linhas com ofertas por linha | 4/4 ✓ | A 4.ª, que falhava, passa ao vivo hoje (ver User Flow passo 3); comparação com os sites fica para humano |
| 01-07 (5) | "tinta branca" 4 tintas + 4 escondidas; género/ligação/-eis/-ões/-res; palavras inteiras; cabeçalho "0 ofertas mostradas; N escondidas"; alargada com medidas | 5/5 ✓ | `test_tinta_branca_gravada_mostra_as_tintas_brancas`, `test_title_matches` (23), `test_tudo_escondido_*` (4); ao vivo "+4 ofertas escondidas: título sem 'tinta branca'" |
| 01-08 (6) | "OSB 12 mm" com o pai devolvido; pais por broadened e variantes pela pesquisa completa; sem medidas igual a antes; LxCxE; Lt/litros/OSB3; `verificar` 4 OK | 6/6 ✓ | `test_osb_12mm_so_a_variante_de_12mm`, `test_medidas_coladas_por_x_batem_no_filtro`; `verificar` ao vivo. A 2.ª verdade está cumprida tal como escrita, mas é ela que causa o CR-04 (aviso) |

**Score:** 60/61 verdades verificadas (0 presentes sem prova de comportamento). As verdades de comportamento têm testes com nome, corridos hoje: 13 testes do fecho mais os 23 casos de `test_title_matches`, 36 passed.

### Deferred Items

| # | Item | Fase | Evidência |
|---|------|------|-----------|
| 1 | WR-07 "azulejo 30x30" bate em "30x60" | Phase 3 | SC3: "o Tamanho decide se as medidas de um anúncio batem" |
| 2 | WR-08 barra/barro, tampo/tampa | Phase 3 | SC2: classificação exato / parecido / outro |
| 3 | WR-11 "osb 30mm" mostra as 7 espessuras | Phase 3 | SC1/SC2; aceite no 01-08 (T-01-36, `shortcut:`) |

São falsos positivos: o produto errado aparece, com o título dele à vista (ex.: "1 Placa 9 MM", "30x60"). Esconder o certo e mostrar o errado não são o mesmo defeito. A Phase 3 separa os errados, mas nenhum critério dela recupera o que o filtro escondeu antes. Por isso o CR-05 fica nesta fase e estes três passam para a Phase 3.

### Advisory (New Scope, Unevidenced)

Nenhum. Reproduzi todos os achados novos da revisão de forma determinística e classifiquei-os abaixo.

### Required Artifacts

`verify.artifacts`: 01-01 7/7, 01-02 6/6, 01-03 4/4, 01-04 2/2, 01-05 2/3, 01-06 3/3, 01-07 4/4, 01-08 4/4.

| Artefacto | Esperado | Estado | Detalhe |
|-----------|----------|--------|---------|
| `src/strata/words.py` | `STOP`, `_stem`, `DIMS`, `LITRE`, `CLASS` | ✓ VERIFIED | É a origem da lacuna que fica (`_stem`) |
| `src/strata/search.py` | "escondidas pelo filtro de título", "também sem ofertas com" | ✓ VERIFIED | |
| `src/strata/stores/obras360.py` | `broadened` + `title_matches(query, o.title)`; 3 `shortcut:` | ✓ VERIFIED | Linha 127: o corte por preço é o CR-04 |
| `tests/fixtures/obras360_*tinta*` (5) | Lista e 4 detalhes gravados | ✓ VERIFIED | 22–201 KB; `grep set-cookie|authorization|bearer|csrf` vazio; nenhum `www.*` no git |
| `tests/test_obras360.py` | `test_tinta_branca_…`, `test_osb_12mm_…` | ✓ VERIFIED | |
| `tests/test_bricomarche.py` | `test_medidas_coladas_por_x_batem_no_filtro` | ✓ VERIFIED | |
| `tests/test_obras360.py` (01-05) | contém "DiscountByQuantity" | ℹ️ padrão em falta | Igual à verificação anterior: os escalões são testados sobre a fixture; não é stub |

### Key Link Verification

`verify.key-links`: 01-01 4/4, 01-02 3/3, 01-03 3/3, 01-04 3/3, 01-05 3/3, 01-06 2/2, 01-07 3/3, 01-08 2/2. Confirmado à mão: `search_store` → `broadened(item.product)` também com `all_hidden`; `detail=` chega ao cabeçalho de `report.print_item`; `obras360.search` → `broadened(query)` (pais) e `title_matches(query, o.title)` (variantes); `bricomarche.search` → `title_matches` com o novo `words()`.

### Data-Flow Trace (Level 4)

| Artefacto | Dado | Origem | Dados reais | Estado |
|-----------|------|--------|-------------|--------|
| `report.print_item` | `sr.offers[].price` | APIs das 3 lojas (Decimal) | Sim, ao vivo hoje | ✓ FLOWING |
| `report.print_item` | `sr.detail` | `search_store` (contagem da 1.ª pesquisa) | Sim, nos testes `tudo_escondido` | ✓ FLOWING |
| `obras360.search` | `hidden` | pais escondidos + variantes cortadas | Sim ("+6 ofertas escondidas" no teste, "+4" ao vivo) | ✓ FLOWING |

### Behavioral Spot-Checks

| Comportamento | Comando | Resultado | Estado |
|---------------|---------|-----------|--------|
| Suite sem rede (uma vez) | `uv run python -m pytest -q` | 161 passed | ✓ PASS |
| Testes do fecho | `pytest -k "title_matches or tudo_escondido or tinta_branca or osb_12mm or medidas_coladas …"` | 36 passed | ✓ PASS |
| Lacuna anterior ao vivo | modelo preenchido (OSB 12 mm / cimento cola / tinta branca) → `pesquisar` | código 0, 26 s; Obras 360 "tinta branca": 4 tintas brancas, "+4 escondidas" | ✓ PASS |
| `verificar` ao vivo | `uv run python -m strata verificar` | 4 × OK, código 0, 28 s | ✓ PASS |
| CR-05 ao vivo | `printf 'perfis 10 un\n\n' \| … pesquisar` + 1 leitura da lista | Obras 360 "ok", 8 ofertas erradas, "+122 escondidas"; 36 pais "Perfil …" escondidos na 1.ª página | ✗ FAIL |
| CR-04 sintético | `FakeFetcher`: 25 parafusos baratos + "Parafuso Sextavado M8" a 99 €, "parafuso m8" | pai M8 nunca expandido; 20 parafusos errados com "pesquisa alargada"; 40 pedidos de detalhe | ✗ (aviso) |
| CR-04 ao vivo (só listas) | 9 termos com números na Obras 360 | 7 dão ≤ 6 produtos ou zero (pesquisa da loja estreita). "cimento 25kg": 22 pais soltos e 2 dos 20 com "25kg" no nome ficam fora do K (os 2 mais caros), com a nota "+2 produtos não expandidos" | ⚠️ efeito real, sem perder o mais barato |
| Filtro de título | script com `title_matches`/`broadened` | Todos os casos do CR-05, WR-07, WR-08, WR-09 e IN-08 reproduzidos como na revisão | — |

### Probe Execution

Não há probes (`scripts/*/tests/probe-*.sh`) nem probes declarados nos planos. Passo não aplicável.

### Requirements Coverage

Os 12 IDs da fase aparecem no `requirements` de pelo menos um plano (01-07: STORE-03, STORE-05, LIST-02, PRICE-01; 01-08: STORE-03, STORE-01, LIST-02). Nenhum órfão.

| Requisito | Planos | Estado | Evidência |
|-----------|--------|--------|-----------|
| LIST-01 | 01-02 | ✓ SATISFIED | `text.py`, `test_text.py` |
| LIST-02 | 01-01/02/03/07/08 | ⚠️ PARCIAL | Qualquer produto vai à pesquisa sem categoria, mas um produto escrito no plural -is/-ais/-ens/-óis fica escondido pelo filtro (CR-05) |
| LIST-04 | 01-01/02 | ✓ SATISFIED | `write_template` |
| LIST-05 | 01-01/02 | ✓ SATISFIED | `read_sheet`, ao vivo |
| STORE-01 | 01-04/08 | ✓ SATISFIED | Coina - Barreiro ao vivo; "osb 18mm" expande a chapa de 18 mm |
| STORE-02 | 01-03 | ✓ SATISFIED | `parse_box`; `verificar` (pavimento) OK |
| STORE-03 | 01-05/07/08 | ✓ SATISFIED | variantes, IVA e escalões; o pai devolvido com medida resolvido (CR-02). Aviso CR-04 |
| STORE-05 | 01-01/02/03/06/07 | ✓ SATISFIED (aviso WR-10) | Estado sempre visível; tudo escondido → contagem no cabeçalho. Fica "ok" sozinho quando todos os produtos vêm sem preço, mas com a nota "N produtos sem preço" |
| STORE-07 | 01-06 | ✓ SATISFIED | 4 × OK ao vivo |
| PRICE-01 | 01-01/02/04/05/07 | ✓ SATISFIED | três origens do IVA |
| PRICE-02 | 01-03/05 | ✓ SATISFIED (aviso WR-02) | `per_unit`, `in_unit` |
| RES-02 | 01-01/02/04/05 | ✓ SATISFIED | stock ao vivo |

ℹ️ A tabela de rastreio do REQUIREMENTS.md está incoerente: LIST-01, LIST-04, LIST-05, STORE-02, STORE-07, PRICE-02 e RES-02 aparecem como "Gaps Found" e sem visto, quando a lacuna nunca lhes tocou. LIST-02 aparece como "Complete". Convém acertá-la ao fechar a fase.

### Anti-Patterns Found

Sem `TBD`/`FIXME`/`XXX`/`TODO` em `src/`, `tests/`, `README.md` e `pyproject.toml`. Há 6 `shortcut:` em `src/` e todos dizem o limite e quando rever.

| Ficheiro | Linha | Achado | Gravidade | Classificação e motivo |
|----------|-------|--------|-----------|------------------------|
| `src/strata/words.py` | 25-35 | CR-05: `_stem` sem -is/-ais/-ens/-óis nem palavras de 3 letras | 🛑 Blocker | **Lacuna da fase.** Confirmado ao vivo com "perfis", termo comum numa lista de obra. A loja vende o produto, a app esconde-o e diz "ok" com produtos errados. Falha o objetivo e o Core Value. É a lacuna anterior (carried forward), num ficheiro mudado desde a última verificação |
| `src/strata/stores/obras360.py` | 124-128 | CR-04: pais por `broadened()`, que tira códigos de modelo; o corte K=20 por preço pode deixar de fora o pai pedido | ⚠️ Warning | **Aviso, não lacuna.** É uma regressão real (reproduzida com fixtures sintéticas). Ao vivo, a pesquisa da Obras 360 é estreita: 7 de 9 termos com números deram ≤ 6 produtos ou zero, e com zero o caminho é igual ao de antes do 01-08. Onde morde ("cimento 25kg"), saem os pais mais caros, o mais barato continua lá e aparece a nota "+N produtos não expandidos". No caso mau (pai pedido fora do corte), as ofertas vêm marcadas "pesquisa alargada" e o cabeçalho diz "N escondidas pelo filtro de título com '<pesquisa>'". O D-14 avisa, não esconde em silêncio. A correção é uma linha (chave `(not title_matches(query, name), preço)`) e convém ir no mesmo plano do CR-05 |
| `src/strata/search.py` | 53-57 | WR-10: "ok" sozinho com 0 ofertas quando `hidden == 0` (todos sem preço) | ⚠️ Warning | Aviso. A nota "N produtos sem preço" aparece logo abaixo, por isso não é omissão silenciosa (STORE-05). Caso de borda, não observado ao vivo. Correção de 2 linhas, junta-se ao plano |
| `src/strata/words.py` | 8, 41 | WR-07: "30x30" bate em "30x60" (regressão do 01-08) | ⚠️ Warning | Falso positivo, com a medida errada à vista no título. Passa para a Phase 3 (SC3) |
| `src/strata/words.py` | 35 | WR-08: género junta barra/barro | ⚠️ Warning | Falso positivo. Passa para a Phase 3 (SC2) |
| `src/strata/stores/obras360.py` | 146-147 | WR-11: gama "9-30MM" | ⚠️ Warning | Falso positivo, já existia, aceite no 01-08 (T-01-36). Passa para a Phase 3 |
| `src/strata/words.py` | 11-12 | WR-09: "tubo pvc 32" não bate em "32mm" | ⚠️ Warning | Falso negativo, mas só com o número sem unidade. Reproduzido com `title_matches`, não ao vivo ("tubo pvc 32" dá zero na Obras 360 e entra a alargada). Convém juntá-lo ao plano do CR-05 |
| `src/strata/money.py`, `text.py`, `allmat.py`, `obras360.py` | — | WR-02 a WR-06 | ⚠️ Warning | Sem mudança desde a verificação anterior; mesmos motivos |
| `src/strata/words.py` | 13 | IN-08: `broadened("tinta 15 litros")` → "tinta litros" | ℹ️ Info | Reproduzido. Uma palavra a mais em `UNIT_TOKENS` |

### Proibições (must_haves.prohibitions)

| Proibição | Nível | Estado | Evidência |
|-----------|-------|--------|-----------|
| 01-07: nunca deixar desaparecer ofertas escondidas sem contagem; com a alargada a contagem da 1.ª fica no cabeçalho | test | ✓ VERIFIED | `test_tudo_escondido_com_medidas_tenta_a_alargada` (detail "5 escondidas … com 'OSB 12mm'"), `test_tudo_escondido_diz_quantas_no_cabecalho` |
| 01-07: gravação sem contornar a proteção nem passar o ritmo | judgment | ⚠️ veredicto não autoritativo: cumprida | Fixtures só com corpos e sem segredos; uma corrida segundo o SUMMARY. Revisão humana recomendada |
| 01-08: nunca esconder uma variante sem a contar | test | ✓ VERIFIED | `obras360.py:148` soma as variantes cortadas; `test_osb_12mm_…` exige hidden == 6 e "+6 ofertas escondidas" |
| Anteriores (pai da Bricomarché, linha-pai da Obras 360, IVA ≠ 23%, ofertas contadas) | test | ✓ VERIFIED | Testes com nome inalterados e verdes |
| Nunca escrever o `.xlsx` do utilizador | test | ⚠️ sinalizada | Só inspeção (nenhum `.save(` fora de `write_template`); falta um teste de bytes iguais |
| Nunca contornar a proteção das lojas | judgment | ⚠️ veredicto não autoritativo: cumprida | `fetch.py` sem retentativas nem proxies |

### Human Verification Required

Ficam para o UAT do fim da fase. Não mudam o estado: a lacuna já o fixa em gaps_found.

1. **Lista da Unidade no Excel.** `uv run python -m strata modelo`, abrir no Excel, escrever "caixa" na Unidade. Esperado: lista com "m²" certo e o aviso. Porquê: não há Excel aqui.
2. **Colar numa consola normal do Windows.** Colar `azulejo 2,5 m²` em `pesquisar`. Esperado: "Linha 1 — azulejo (2,5 m²)". Porquê: só o pipe foi testado.
3. **Link da Bricomarché (Coina - Barreiro).** Esperado: página nessa loja, 14,49 € (9 mm) ou 18,49 € (12 mm), com IVA (A9). Porquê: preço desenhado por JavaScript.
4. **Variante de 12 mm da Obras 360.** Esperado: 19,37 € com IVA. Porquê: confirmar o que o comprador vê.
5. **Folha de 3 linhas contra os sites (D5 do 01-08).** A corrida ao vivo do verificador mostrou ofertas nas 3 linhas. Falta comparar os preços com os sites.
6. **Proibições judgment** (ritmo e gravação) e **o `.xlsx` do utilizador fica igual** (SHA1 antes/depois de `pesquisar`).

### Gaps Summary

**Lacuna anterior (filtro esconde o produto pedido e a loja diz "ok"): fechada nos casos que a definiam, aberta na causa.**

- Fechado e confirmado ao vivo: "tinta branca" mostra as 4 tintas brancas da Obras 360. "OSB 12 mm" mostra a placa de 12 mm (ao vivo pela alargada, e com o pai devolvido nos testes). Com tudo escondido, o cabeçalho dá a contagem. A Bricomarché expande a chapa 2440X590X18Mm para "osb 18mm".
- Aberto (BLOCKER, CR-05): o `_stem` falha os plurais -is/-ais/-ens/-óis. Ao vivo, "perfis" na Obras 360 dá "ok" com 8 produtos que não são perfis e esconde pelo menos 36 pais "Perfil …". Como passa alguma oferta errada, a frase do WR-01 não aparece. É uma só função e uma tabela de sufixos (o 01-REVIEW.md já traz o código), mais 5 casos em `test_title_matches` e um teste de ponta a ponta.

**Classificação dos achados que o orquestrador pediu para pesar:**

| Achado | Classe | Motivo |
|--------|--------|--------|
| CR-05 | Lacuna (blocker) | Confirmado ao vivo com um termo comum de obra; é a lacuna anterior por fechar |
| CR-04 | Aviso | Regressão real, mas sem perda do mais barato ao vivo; quando morde, a app avisa ("pesquisa alargada", contagem, "+N não expandidos"). Recomendado no mesmo plano (uma linha) |
| WR-07 | Aviso, Phase 3 | Falso positivo com a medida à vista; regressão do 01-08, barata de corrigir, mas a decisão sobre medidas é da Phase 3 (SC3) |
| WR-08 | Aviso, Phase 3 | Falso positivo; exato/parecido (SC2) |
| WR-10 | Aviso | Caso de borda com nota visível; não viola STORE-05 |
| WR-11 | Aviso, Phase 3 | Já existia e foi aceite no 01-08 |

**Plano de fecho sugerido (um plano, cerca de 30 linhas):** a tabela `PLURAL` em `_stem` (CR-05) com os testes, a chave de ordenação do CR-04 com um teste do pai M8 caro, o `detail` do WR-10 e `UNIT_TOKENS` com "litro/litros/lts" (IN-08). Opcionalmente WR-09.

**Se decidir aceitar e avançar**, acrescentar ao frontmatter:

```yaml
overrides:
  - must_have: "O utilizador recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360"
    reason: "Plurais -is/-ais/-ens/-óis ficam para depois; o utilizador escreve no singular e a contagem de escondidas é visível"
    accepted_by: "{nome}"
    accepted_at: "{ISO timestamp}"
```

---

_Verificado: 2026-10-23T11:04:54Z_
_Verificador: Claude (gsd-verifier)_
