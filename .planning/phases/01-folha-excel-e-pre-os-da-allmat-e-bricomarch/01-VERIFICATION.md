---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
verified: 2026-10-23T23:14:25Z
status: human_needed
score: 90/91 must-haves verified
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
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-12-PLAN.md"
  - ".planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-12-SUMMARY.md"
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
covered_digest: "v3:sha256:372d5a2affa0d7661b9e4dc0a29bb633f495ab1fbc7362b39d59c3b7f8462de1"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 80/82
  gaps_closed:
    - "G-01-5 fora do caso citado (WR-17): na alargada, o produto da linha (rank) ordena os pais antes dos cortes K nas três lojas. Teste nomeado test_alargada_expande_o_pai_com_o_produto_da_linha (placa 60X120, a mais cara de 13, entra nos 10 expandidos e é a única mostrada). Ao vivo nesta verificação (2026-10-23T23:11Z): 'pavimento 60x120 10 m²' dá na Bricomarché, em 1.º e 2.º, a Siena e a Casablanca 60X120 a 34,55 € (23,99 €/m²)"
    - "WR-14: 'pavimento 120x60' bate em 'Pavimento 60x120'; 'azulejo 30x30' bate em 'Azulejo 30×30 cm'; 'azulejo 30x30' continua sem bater em 'Azulejo 30x60' (reproduzido com script)"
    - "WR-15: broadened('tela 1 m x 25 m') == 'tela' (reproduzido com script)"
    - "WR-16: o cabeçalho do ramo 'tudo escondido' diz '1.ª pesquisa: …' (tests/test_search.py, linhas 196 e 245)"
  gaps_remaining: []
  regressions:
    - "WR-18 (01-12): os pares de combinations juntam a 1.ª e a última parte de uma medida de 3. 'tubo 20x2' bate em 'Tubo Retangular 20x40x2' e 'caixa 20x40' em 'Caixa 20x30x40' (reproduzido). É sobre-correspondência: mostra um produto a mais, nunca esconde. Aviso não bloqueante, ver deferred"
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
  - truth: "WR-18: uma medida de 2 partes bate numa de 3 com a 1.ª e a última parte iguais ('tubo 20x2' em 'Tubo Retangular 20x40x2'); sobre-correspondência, o título fica à vista"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC2 (exato / parecido com a diferença escrita) e SC3 ('o Tamanho … decide se as medidas de um anúncio batem'). A correção de ~5 linhas do 01-REVIEW.md (WR-18) fecha-o já, se se preferir"
  - truth: "Allmat: os 52 mosaicos '60X120' da loja não têm 'pavimento' no título (ex.: 'SOSPIRO 60X120 BLANCO RET'); 'pavimento 60x120' mostra pavimentos 45X45 marcados 'pesquisa alargada'"
    addressed_in: "Phase 3"
    evidence: "Phase 3 SC3: 'A Família, o Tamanho e a Referência da folha entram na pesquisa e na classificação'. A pesquisa na loja com as mesmas palavras ('pavimento 60x120') também dá 0"
behavior_unverified_items: []
coincidental_reliance_items: []
human_verification:
  - test: "Re-teste 3 do UAT (G-01-3): printf 'placa osb 9mm 1 un\\n\\n' | uv run python -m strata pesquisar e abrir o link da 1.ª oferta da Bricomarché"
    expected: "Uma loja física com stock, com o preço igual ao do site; se a mais barata não tiver stock, aparece a nota 'mais barata sem stock: X em Y'"
    why_human: "O preço da Bricomarché é desenhado por JavaScript e os stocks mudam; só uma pessoa compara com o site"
  - test: "Re-teste 5 do UAT (G-01-5, 01-11 e 01-12): pesquisar modelo.xlsx com OSB 12 mm / un / 30; cimento cola / saco / 10; tinta branca / L / 15; pavimento 60x120 / m² / 10. Abrir os links da Siena e da Casablanca 60X120 da Bricomarché"
    expected: "OSB 12 mm: a placa de 12 mm em 1.º na Obras 360, sem cola nem espuma, o resto contado em '+N ofertas escondidas'. Pavimento 60x120: na Bricomarché, as duas placas 60X120 a 34,55 € (23,99 €/m²), com preço igual ao do site e 'Esgotado' na Siena"
    why_human: "Só uma pessoa decide se o resultado é igual ou melhor do que a pesquisa à mão nos sites"
  - test: "Teste 1 do UAT (ignorado, sem Excel): uv run python -m strata modelo, abrir no Excel e escrever 'caixa' na Unidade"
    expected: "Lista de unidades com 'm²' bem escrito e o aviso de valor inválido"
    why_human: "Não há Excel nesta máquina"
  - test: "Decisão sobre o SC3 do ROADMAP e o STORE-01: a oferta da Bricomarché é a loja mais barata com stock, e a mais barata absoluta sem stock fica na nota (sem link)"
    expected: "Atualizar o texto do SC3 e do STORE-01 (recomendado, foi o pedido do UAT) ou aceitar com um override"
    why_human: "Decisão de produto: o texto do requisito diz 'o preço mais barato entre todas as lojas físicas'"
  - test: "Proibições judgment: 01-10 (nenhum pedido novo por causa do stock) e 01-12 (uma só corrida ao vivo no executor)"
    expected: "Ler offer_from em src/strata/stores/bricomarche.py (só usa as rows já lidas) e o 01-12-SUMMARY (uma corrida, 22:59:22Z a 22:59:45Z)"
    why_human: "O veredicto do verificador (cumpridas) não é autoritativo para proibições judgment"
---

# Phase 1: Folha Excel e preços da Allmat, Bricomarché e Obras 360 — Relatório de verificação

**Objetivo da fase:** O utilizador preenche o modelo Excel da app, passa o caminho do `.xlsx` à linha de comandos e recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360, já com IVA 23% e preço unitário normalizado, com o estado de cada loja sempre visível; para uma pesquisa rápida pode colar texto em vez da folha
**Verificado:** 2026-10-23T23:14:25Z
**Estado:** human_needed
**Reverificação:** Sim, a quarta, depois do plano de fecho 01-12 (WR-17, WR-14, WR-15, WR-16)

## Resposta curta

1. **O WR-17 está fechado.** Corri ao vivo, uma vez, `printf 'pavimento 60x120 10 m²\n\n' | uv run python -m strata pesquisar` (código 0, 22 s). A Bricomarché mostra em 1.º e 2.º a "PAVIMENTO CERÂMICO SIENA HEKLA 60X120 1.44M2" e a "Pavimento/Revestimento Cerâmico Casablanca Mate 60X120 1.44M2", a 34,55 € (23,99 €/m²). Antes mostrava pavês de betão a 0,21 €. O teste nomeado do tracer também passa.
2. **O WR-14, o WR-15 e o WR-16 estão corrigidos.** Reproduzi cada caso com script e os testes passam.
3. **WR-18, WR-19 e WR-20 são avisos e não bloqueiam.** Nenhum esconde o produto pedido. A classificação de cada um está na tabela do fim.
4. **Não há lacunas.** O estado é `human_needed` por 5 itens humanos: re-testes 3 e 5, teste 1, a decisão do STORE-01 e as proibições judgment.
5. Suite: `uv run python -m pytest -q` → 222 passed.

## User Flow Coverage

| Passo | Esperado | Evidência | Estado |
|-------|----------|-----------|--------|
| 1. Obter o modelo | `modelo` grava o modelo e não sobrescreve | `sheet.py` sem mudança desde 701e356 (`git diff --quiet`); `test_sheet.py` verde | ✓ |
| 2. Preencher e passar o `.xlsx` | Cada linha válida passa a ser um item | `read_sheet` sem mudança; o UAT teste 7 passou | ✓ |
| 3. Preços das 3 lojas por linha | Ofertas do produto pedido, mais baratas primeiro | Ao vivo: Bricomarché com os dois 60X120 a 34,55 €. Allmat e Obras 360 não vendem nenhum título "pavimento … 60x120" (ver Deferred e Spot-checks), por isso mostram a alargada marcada | ✓ |
| 4. IVA 23% e preço unitário | Preço, origem do IVA, €/unidade, stock | Ao vivo: "IVA: regra da loja (…) · 23,99 €/m² · 3 em stock · loja: São Domingos de Rana" | ✓ |
| 5. Estado de cada loja visível | As 3 lojas sempre presentes | As 3 secções "ok (pesquisa alargada: 'pavimento')" na corrida ao vivo | ✓ |
| 6. Pesquisa rápida colada | Descrição, quantidade e unidade | "Linha 1 — pavimento 60x120 (10 m²)" a partir do texto colado | ✓ |

## Goal Achievement

### Observable Truths — critérios do ROADMAP, objetivo e lacunas do UAT

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| G | O utilizador recebe, para cada linha, os preços na hora das três lojas | ✓ VERIFIED | Ao vivo hoje, as 3 lojas "ok" com preço |
| SC1 | Modelo Excel, linha de comandos, linhas inválidas com número e motivo | ✓ VERIFIED | `sheet.py` e `__main__.py` sem mudança; testes verdes |
| SC2 | Lista colada com descrição, quantidade e unidade; texto livre sem categoria | ✓ VERIFIED | `text.py` sem mudança; entrada colada ao vivo |
| SC3 | Bricomarché: o mais barato entre as lojas físicas, com a loja e o link; Allmat: caixa convertida; Obras 360: variantes, IVA e escalões | ? UNCERTAIN | Allmat e Obras 360 como antes ("escalões: −15% a partir de 12" ao vivo). Na Bricomarché, a oferta é a loja mais barata **com stock** desde o 01-10, e o texto do SC3 e do STORE-01 não mudou. Precisa de decisão (item humano 4) |
| SC4 | Preço com IVA, origem do IVA, preço unitário, stock, sem filtrar | ✓ VERIFIED | Ao vivo, a Siena "Esgotado" aparece (não é filtrada) |
| SC5 | Estado das três lojas por item; `verificar` por adaptador | ✓ VERIFIED | Ao vivo; `search.verificar` e os canários sem mudança |
| G-01-3 | A 1.ª oferta da Bricomarché é a loja mais barata com stock; a mais barata sem stock não some | ✓ VERIFIED (no código) | `offer_from` sem mudança desde o 01-10; 15 testes nomeados passam. Falta o re-teste 3 |
| G-01-5 | Para cada linha, as ofertas mostradas são o produto pedido, mais baratas primeiro | ✓ VERIFIED | Caso citado: `test_osb_12mm_alargada_mostra_so_a_placa_de_12mm`. Caso geral (WR-17): `test_alargada_expande_o_pai_com_o_produto_da_linha` e ao vivo "pavimento 60x120" na Bricomarché. Falta o re-teste 5 |

### Observable Truths — must_haves dos planos

| Plano | Verdades | Estado | Evidência |
|-------|----------|--------|-----------|
| 01-01 a 01-07 (49) | como nas verificações anteriores | 49/49 ✓ | `fetch`, `money`, `models`, `report`, `sheet`, `text` sem mudança desde 701e356; suite verde |
| 01-08 (6) | "OSB 12 mm" com o pai; LxCxE; Lt/OSB3 | 6/6 ✓ | Falta o padrão `LITRE` (trocado por `UNIT_WORDS` no quick); o comportamento mantém-se (`test_title_matches`) |
| 01-09 (6) | perfis, plurais, M8 à frente do corte, "0 de N", litros | 6/6 ✓ | Falta o padrão `not title_matches(query` (trocado no CR-06); os testes do 01-09 passam |
| 01-10 (6) | loja com stock, nota, empates, ordem, e2e, suite | 6/6 ✓ | Testes nomeados verdes |
| 01-11 (7) | alargada mostra só as que batem a pergunta completa | 7/7 ✓ | Testes nomeados verdes; a verdade 7 (209 passed) mantém-se: hoje 222, sem testes a falhar |
| 01-12 (9) | ver abaixo | 9/9 ✓ | |

**01-12, verdade a verdade:**

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| 1 | WR-17 na Bricomarché: a placa 60X120 (a mais cara de 13) está entre os 10 expandidos e é a única mostrada; "+9 escondidas" e "+3 não expandidos" | ✓ VERIFIED | `test_alargada_expande_o_pai_com_o_produto_da_linha`: 10 pedidos de variações, 1 deles do pai 200; oferta única a 34,55 €; as 4 linhas do report |
| 2 | A pesquisa enviada continua a alargada; só a 2.ª pesquisa leva rank | ✓ VERIFIED | `store.ranks == [None, "OSB 12mm"]` (test_search.py:151); `search.py:107` `store.search(b, fetch, rank=item.product)` |
| 3 | Obras 360 e Allmat também ordenam pelo rank | ✓ VERIFIED | `test_rank_poe_o_pai_do_produto_da_linha_a_frente_do_corte` (20 detalhes, com `id-60x120`, e só `search=pavimento&`); `test_rank_le_primeiro_as_caixas_do_produto_da_linha` (10 páginas, com `p60x120`) |
| 4 | Sem rank, a ordem fica pelo preço; K e limites iguais; pedidos não crescem | ✓ VERIFIED | `K = 10`, `K = 20`, `MAX_BOX_PAGES = 10`; `fetch.py` sem mudança; os testes de corte antigos passam sem mudança |
| 5 | WR-14: medidas em qualquer ordem, com "×" ou espaços; guardas 30x30/30x60 e 20x20/20x40x1,5 em False | ✓ VERIFIED | Script: os 5 casos dão True, as 2 guardas dão False, `osb 18mm` dá True |
| 6 | WR-15: `broadened` tira o "x"/"×" solto | ✓ VERIFIED | Script: 'tela 1 m x 25 m', 'osb 12 mm x 2500 x 1250' e 'tela 1 m × 25 m' dão 'tela'/'osb'; 'metro articulado 2m' e 'tinta 15 litros' como antes |
| 7 | WR-16: cabeçalho "1.ª pesquisa: …" e a linha `wide_only` igual | ✓ VERIFIED | test_search.py:196 e 245 |
| 8 | Corrida ao vivo: 1.º da Bricomarché é um 60X120 (~34,55 €) | ✓ VERIFIED | Repetida pelo verificador às 23:11Z: Siena e Casablanca 60X120 a 34,55 € |
| 9 | Suite 222 passed | ✓ VERIFIED | `uv run python -m pytest -q` → 222 passed |

**Score:** 90/91 verdades verificadas. Fica 1 UNCERTAIN (SC3, à espera da decisão do item humano 4). Nenhuma verdade ficou só presente: as do 01-12 que dependem de comportamento (ordem antes do corte, número de pedidos) têm testes nomeados corridos hoje (80 + 15 passed).

### Deferred Items

| # | Item | Fase | Evidência |
|---|------|------|-----------|
| 1 | WR-08 barra/barro, tampo/tampa (e IN-14 fim/fino) | Phase 3 | SC2: exato / parecido / outro |
| 2 | WR-11 "osb 30mm" mostra as 7 espessuras | Phase 3 | SC1/SC2; aceite no 01-08 |
| 3 | IN-11 cal/Cais, abs/AB; "Varão … Fixação Perfil Teto" | Phase 3 | SC2; aceite no 01-09 |
| 4 | Produto contra menção com todas as palavras no título | Phase 3 | SC2; "Fora do âmbito" do 01-11 |
| 5 | WR-18 "tubo 20x2" bate em "Tubo Retangular 20x40x2" | Phase 3 | SC2 (parecido com a diferença escrita) e SC3 (o Tamanho decide as medidas). Correção de ~5 linhas disponível no 01-REVIEW.md |
| 6 | Allmat: mosaicos "60X120" sem "pavimento" no título | Phase 3 | SC3: o Tamanho da folha entra na pesquisa |

### Advisory (New Scope, Unevidenced)

Nenhum. Os três achados novos têm evidência determinística. O WR-18 reproduzi-o com script, o WR-19 com a contagem de palavras do `rank` e o WR-20 na corrida ao vivo (a Siena esgotada aparece antes da Casablanca, ao mesmo preço). Estão classificados mais abaixo.

### Required Artifacts

`verify.artifacts`: 01-01 7/7, 01-02 6/6, 01-03 4/4, 01-04 2/2, 01-05 2/3, 01-06 3/3, 01-07 4/4, 01-08 3/4, 01-09 4/5, 01-10 4/4, 01-11 6/6, 01-12 8/8. As 3 falhas são padrões que uma correção posterior substituiu. Estão explicadas nas verificações anteriores e o comportamento foi mantido.

| Artefacto (01-12) | Esperado | Estado | Detalhe |
|-------------------|----------|--------|---------|
| `src/strata/search.py` | `rank=item.product` | ✓ VERIFIED | Só na alargada (linha 107); "1.ª pesquisa:" na linha 144 |
| `src/strata/stores/bricomarche.py` | `words(rank or query)` | ✓ VERIFIED | Ordena `keyed` antes de `keyed[:K]` (linhas 128-130) |
| `src/strata/stores/obras360.py` | `words(rank or query)` | ✓ VERIFIED | `need` antes de `kept[:K]` |
| `src/strata/stores/allmat.py` | `words(rank or query)` | ✓ VERIFIED | Ordena `boxes` antes de `boxes[:MAX_BOX_PAGES]` |
| `src/strata/words.py` | `replace("×", "x")` | ✓ VERIFIED | Mais `combinations(p, 2)` (origem do WR-18) e o "x" em `STOP` |
| `tests/test_search.py`, `test_obras360.py`, `test_allmat.py` | os 3 testes de rank e os casos WR-14/15/16 | ✓ VERIFIED | Passam |

### Key Link Verification

`verify.key-links`: 01-01 4/4, 01-02 3/3, 01-03 3/3, 01-04 3/3, 01-05 3/3, 01-06 2/2, 01-07 3/3, 01-08 2/2, 01-09 2/3 (padrão substituído pelo CR-06), 01-10 2/2, 01-11 2/2, 01-12 2/2.

| De | Para | Via | Estado |
|----|------|-----|--------|
| `search.py` | `bricomarche.py` | `store.search(b, fetch, rank=item.product)` | ✓ WIRED (as 3 lojas aceitam `rank: str \| None = None`) |
| `bricomarche.py` | `words.py` | `need = words(rank or query)` | ✓ WIRED |

### Data-Flow Trace (Level 4)

| Artefacto | Dado | Origem | Dados reais | Estado |
|-----------|------|--------|-------------|--------|
| `report.print_item` | `sr.offers[].price` | APIs das 3 lojas (Decimal) | Sim, ao vivo (34,55 €, 15,85 €, 16,38 €) | ✓ FLOWING |
| `bricomarche.search` | pais expandidos | `rank` → `need` → `keyed.sort` → `keyed[:K]` | Sim: ao vivo os 2 pais 60X120 entram nos 10 expandidos | ✓ FLOWING |
| `report.print_item` | `sr.wide_only` | passo final de `search_store` | Sim, ao vivo "+8 ofertas escondidas: título sem 'pavimento 60x120'" | ✓ FLOWING |

### Behavioral Spot-Checks

| Comportamento | Comando | Resultado | Estado |
|---------------|---------|-----------|--------|
| Suite sem rede (uma vez) | `uv run python -m pytest -q` | 222 passed | ✓ PASS |
| Testes do 01-12 | `pytest tests/test_search.py tests/test_obras360.py tests/test_allmat.py -k "alargada_expande_o_pai or pesquisa_alargada_quando or rank_poe or rank_le or tudo_escondido_… or test_title_matches or test_broadened"` | 80 passed | ✓ PASS |
| Testes do 01-10, 01-11 e CR-06 | `pytest tests/test_bricomarche.py tests/test_e2e.py tests/test_obras360.py -k "offer_from or search_osb or tres_itens or ponta_a_ponta or osb_12mm or frente_do_corte or perfis or mais_palavras or alargada_mostra_so"` | 15 passed | ✓ PASS |
| WR-14 / WR-15 / WR-18 | script com `title_matches` e `broadened` de HEAD | WR-14 e WR-15: todos como o plano pede. WR-18: `('tubo 20x2','Tubo Retangular 20x40x2')` e `('caixa 20x40','Caixa 20x30x40')` dão True; `('tubo 40x2','Tubo Retangular 40x20x2')` e `('viga 100x200','Viga 100x150x200')` também | ✓ / ⚠️ WR-18 |
| WR-19 | `len(words('pavimento 60x120') & words(título))` | 45X45 → 1; "60X60" → 2; "120X20" → 2; "60X120" → 4 | ⚠️ confirmado no código |
| Ao vivo, 1 linha colada | `printf 'pavimento 60x120 10 m²\n\n' \| uv run python -m strata pesquisar` | código 0, 22 s. Bricomarché: Siena (Esgotado) e Casablanca (3 em stock) 60X120 a 34,55 €; "+8 escondidas"; "+138 não expandidos". Allmat: pavimentos 45X45 a 12,99 €/m², alargada. Obras 360: mosaicos 60x60 e pavês, alargada | ✓ (WR-17 fechado) |
| Allmat, pesquisa "60x120" (1 pedido) | API WooCommerce | 52 produtos, nenhum com "pavimento" no título (ex.: "SOSPIRO 60X120 BLANCO RET") | ℹ️ deferred 6 |
| Allmat, caixas da alargada "pavimento" (1 pedido) | `parse_products` e as duas ordens | 24 produtos, 7 caixas, abaixo do limite de 10: o WR-19 não mordeu ao vivo | ℹ️ |
| Obras 360, pesquisa "60x120" (2 pedidos) | lista de produtos | total 0: a loja não tem 60x120 a esconder | ℹ️ |

### Probe Execution

Não há probes (`scripts/*/tests/probe-*.sh`) nem probes declarados nos planos. Passo não aplicável.

### Requirements Coverage

Os 12 IDs da fase aparecem no `requirements` de pelo menos um plano (o 01-12 cobre LIST-02, STORE-01, STORE-02, STORE-03 e STORE-05). Não há órfãos.

| Requisito | Planos | Estado | Evidência |
|-----------|--------|--------|-----------|
| LIST-01 | 01-02 | ✓ SATISFIED | `text.py`; entrada colada ao vivo |
| LIST-02 | 01-01/02/03/07/08/09/11/12 | ✓ SATISFIED | Qualquer produto é pesquisado sem categoria; o WR-17 fechou o caso de muitos pais. WR-18 fica como aviso (sobre-correspondência) |
| LIST-04 | 01-01/02 | ✓ SATISFIED | `write_template` |
| LIST-05 | 01-01/02 | ✓ SATISFIED | `read_sheet` |
| STORE-01 | 01-04/08/10/12 | ? NEEDS HUMAN | Loja mais barata com stock; a mais barata absoluta fica na nota. Falta decidir o texto (item humano 4) |
| STORE-02 | 01-03/12 | ✓ SATISFIED | `parse_box`; ao vivo "12,99 €/m²" |
| STORE-03 | 01-05/07/08/09/11/12 | ✓ SATISFIED | Variantes, IVA e escalões ao vivo |
| STORE-05 | 01-01/02/03/06/07/09/12 | ✓ SATISFIED | As 3 lojas em cada linha; "1.ª pesquisa:" no cabeçalho |
| STORE-07 | 01-06 | ✓ SATISFIED | `verificar` sem mudança |
| PRICE-01 | 01-01/02/04/05/07 | ✓ SATISFIED | Três origens do IVA ao vivo |
| PRICE-02 | 01-03/05 | ✓ SATISFIED (aviso WR-02) | `per_unit`, `in_unit` |
| RES-02 | 01-01/02/04/05/10 | ✓ SATISFIED | "Esgotado" à vista e sem filtro |

ℹ️ No REQUIREMENTS.md, o STORE-01 está `[x] Complete` com a decisão do texto ainda pendente. LIST-01, LIST-04, LIST-05, STORE-07, PRICE-01, PRICE-02 e RES-02 continuam como "Gaps Found" na tabela de rastreio, mas nenhuma lacuna lhes toca. Corrigir as duas coisas ao fechar a fase.

### Anti-Patterns Found

Não há `TBD`, `FIXME`, `XXX`, `TODO` nem `HACK` em `src/`, `tests/`, `README.md` e `pyproject.toml`. Há 6 `shortcut:` em `src/` e todos dizem o limite. Os comentários de K e de MAX_BOX_PAGES foram atualizados no 01-12.

| Ficheiro | Linha | Achado | Gravidade | Classificação e motivo |
|----------|-------|--------|-----------|------------------------|
| `src/strata/words.py` | 57 | **WR-18**: `combinations(p, 2)` junta a 1.ª e a última parte de uma medida de 3 | ⚠️ Warning | **Aviso não bloqueante. É sobre-correspondência e regressão do 01-12.** Mostra um produto a mais (o retangular 20×40×2 ao lado do tubo 20×2) e nunca esconde o pedido: o filtro D-15 e o passo do 01-11 só acrescentam. O título fica à vista, por isso a pesquisa à mão não ganha por esconder nada. O risco é ficar em 1.º um produto parecido mais barato. É a mesma classe do WR-08 e fica no deferred para a Phase 3 (SC2 e SC3). A correção de ~5 linhas do 01-REVIEW.md fecha-o já, se se preferir |
| `src/strata/stores/allmat.py`, `bricomarche.py` | 141-142; 128-129 | **WR-19**: sem nenhum título que bata o produto inteiro, um "60"/"120" solto do `rank` decide que caixas são lidas (Allmat) e que pais são expandidos (Bricomarché) | ⚠️ Warning | **Aviso não bloqueante. Não é sub-correspondência do produto pedido.** Só atua quando nenhum título bate a linha inteira, e nessas lojas o título é o nome do pai ou da caixa. Por isso o produto pedido não existe nesse conjunto: o que muda é que vizinhos da alargada aparecem. Na Allmat, uma caixa mais barata pode ficar sem área ("área da caixa não lida", contada em "+N não mostradas"). Antes do 01-12, a escolha também era pelo preço da caixa e não pelo €/m², ou seja, já era uma heurística. Ao vivo não mordeu (7 caixas, abaixo de 10). Correção de 2 linhas no 01-REVIEW.md |
| `src/strata/stores/bricomarche.py` | 73-83, 140-143 | **WR-20**: num empate de preço, um pai esgotado em todas as lojas aparece antes de um com stock | ⚠️ Warning | **Aviso não bloqueante.** Reproduzido ao vivo: a Siena (Esgotado) em 1.º e a Casablanca (3 em stock) em 2.º, as duas a 34,55 €. As duas aparecem com o preço certo e o "Esgotado" está à vista, por isso nada fica escondido e a pesquisa à mão não ganha. Correção pequena (desempate pelo stock dentro do adaptador) |
| `src/strata/words.py` | 18, 27 | IN-16: o "x" em `STOP` apaga um "X" que é nome de produto; `UNIT_TOKENS` ainda tem o "x" | ℹ️ Info | Nota |
| `money.py`, `text.py`, `allmat.py`, `obras360.py`, `words.py` | — | WR-02 a WR-06, WR-09, IN-01 a IN-07, IN-09, IN-10, IN-12, IN-13, IN-15 | ⚠️/ℹ️ | Sem mudança desde a verificação anterior; os mesmos motivos |

### Proibições (must_haves.prohibitions)

| Proibição | Nível | Estado | Evidência |
|-----------|-------|--------|-----------|
| 01-12: nunca mudar a pesquisa enviada à loja | test | ✓ VERIFIED | `store.ranks == [None, "OSB 12mm"]`; `all("search=pavimento&" in c …)` no teste da Obras 360 |
| 01-12: nunca aumentar o número de pedidos | test | ✓ VERIFIED | Os testes de rank fixam 10 variações, 20 detalhes e 10 páginas; `fetch.py` sem mudança |
| 01-12: nunca esconder uma oferta sem a contar | test | ✓ VERIFIED | test_search.py:196, 245 (as duas contagens à vista) |
| 01-12: uma só corrida ao vivo no executor | judgment | ⚠️ veredicto não autoritativo: cumprida | O 01-12-SUMMARY regista uma corrida (22:59:22Z a 22:59:45Z). A corrida das 23:11Z é a do verificador |
| 01-10: nunca esconder a mais barata sem stock; nunca filtrar pelo stock | test | ✓ VERIFIED | Testes nomeados verdes |
| 01-10: nenhum pedido novo por causa do stock | judgment | ⚠️ veredicto não autoritativo: cumprida | `offer_from` só usa as `rows` já lidas |
| 01-11 e 01-01 a 01-09 | test/judgment | como antes | Testes verdes; UAT testes 7 e 8 passaram |

### Testes do UAT que já passaram (2, 4, 6, 7, 8)

Não é preciso repeti-los. O 01-12 não toca no `text.py` (teste 2), no preço nem no link das variantes da Obras 360 (teste 4), nem no `sheet.py` e no `fetch.py` (testes 7 e 8). No teste 6 ("perfis"), sem rank a ordem antes do corte é a de antes, e `test_perfis_mostra_o_pai_perfil` passa.

### Human Verification Required

1. **Re-teste 3 do UAT (G-01-3).** Correr `printf 'placa osb 9mm 1 un\n\n' | uv run python -m strata pesquisar` e abrir o link da 1.ª oferta da Bricomarché. Esperado: uma loja com stock e o preço igual ao do site; se a mais barata não tiver stock, aparece a nota "mais barata sem stock: X em Y". Porquê: o preço é desenhado por JavaScript e os stocks mudam.
2. **Re-teste 5 do UAT (G-01-5, 01-11 e 01-12).** Correr `pesquisar modelo.xlsx` com 4 linhas: OSB 12 mm / un / 30; cimento cola / saco / 10; tinta branca / L / 15; pavimento 60x120 / m² / 10. Esperado: em "OSB 12 mm", a placa de 12 mm em 1.º na Obras 360, sem cola nem espuma. Em "pavimento 60x120", a Bricomarché mostra a Siena e a Casablanca 60X120 a 34,55 €. Abrir os dois links e confirmar o preço e o "Esgotado" da Siena no site. Porquê: só uma pessoa decide se o resultado é igual ou melhor do que a pesquisa à mão.
3. **Teste 1 do UAT (ignorado, sem Excel).** Correr `uv run python -m strata modelo`, abrir no Excel e escrever "caixa" na Unidade. Esperado: lista com "m²" bem escrito e o aviso. Porquê: não há Excel nesta máquina.
4. **Decisão sobre o SC3 e o STORE-01.** O texto diz "o preço mais barato entre todas as lojas físicas, com o nome dessa loja e o link". Desde o 01-10, a oferta é a loja mais barata com stock, e a mais barata absoluta aparece na nota sem link. Há duas saídas: atualizar o SC3 do ROADMAP e o STORE-01 (recomendado, porque foi o pedido do UAT) ou aceitar com um override:
   ```yaml
   overrides:
     - must_have: "A Bricomarché devolve o preço mais barato entre todas as lojas físicas, com o nome dessa loja e o link para a página do produto nessa loja"
       reason: "UAT teste 3 (G-01-3): a oferta é a loja mais barata com stock; a mais barata sem stock fica na nota com preço e loja (RES-02)"
       accepted_by: "<nome>"
       accepted_at: "<ISO>"
   ```
5. **Proibições judgment do 01-10 e do 01-12.** Ler `offer_from` em `src/strata/stores/bricomarche.py` (nenhum pedido novo por causa do stock) e confirmar no 01-12-SUMMARY que houve uma só corrida ao vivo. O veredicto do verificador (cumpridas) não é autoritativo.

### Gaps Summary

**Não há lacunas. O WR-17 está fechado.**

O 01-12 passa o produto da linha (`rank`) às três lojas só para ordenar antes dos cortes. A pesquisa enviada continua a alargada e os K não mudaram. O tracer prova-o com a placa 60X120 como a mais cara de 13. A corrida ao vivo desta verificação mostra-o na loja real: a Bricomarché passou de pavês de betão a 0,21 € para os dois pavimentos 60X120 a 34,55 €. O WR-14 (a ordem das medidas), o WR-15 (o "x" solto) e o WR-16 (o cabeçalho) também ficam corrigidos.

**Classificação dos achados novos, com o mesmo critério das verificações anteriores.** Bloqueia só o que faz a ferramenta perder para uma pesquisa à mão numa linha comum de obra, ao vivo, ou o que esconde ofertas ou preços em silêncio.

| Achado | Tipo | Classe | Motivo |
|--------|------|--------|--------|
| WR-18 | Sobre-correspondência (regressão do 01-12) | Aviso não bloqueante; deferred Phase 3 | Mostra um produto a mais com o título à vista e nunca esconde o pedido. A correção de ~5 linhas é barata, se se quiser fechar antes |
| WR-19 | Ordem dos vizinhos quando não há produto exato | Aviso não bloqueante | Não esconde o produto pedido, porque só atua quando nenhum título o tem. Pode tirar o €/m² a uma caixa vizinha (contada e com nota). Ao vivo não mordeu |
| WR-20 | Empate de preço esgotado/com stock | Aviso não bloqueante | As duas ofertas aparecem, com o preço certo e o "Esgotado" à vista |
| Allmat 60X120 sem "pavimento" | Sub-correspondência por nome da loja, anterior ao 01-12 | Deferred Phase 3 (SC3) | A pesquisa na loja com as mesmas palavras também dá 0; a ferramenta marca "pesquisa alargada". Para os encontrar é preciso pesquisar só pela medida, e a Phase 3 SC3 põe o Tamanho na pesquisa |

**Recomendação:** fazer os re-testes 3 e 5 do UAT (`/gsd-verify-work 01`) e decidir o texto do STORE-01. O WR-18, o WR-19 e o WR-20 cabem num quick de cerca de 10 linhas com 3 testes, mas não impedem fechar a fase.

---

_Verificado: 2026-10-23T23:14:25Z_
_Verificador: Claude (gsd-verifier)_
