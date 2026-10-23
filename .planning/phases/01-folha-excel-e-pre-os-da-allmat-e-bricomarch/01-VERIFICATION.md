---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
verified: 2026-10-23T14:30:00Z
status: gaps_found
score: 48/50 must-haves verified
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
  - "tests/fixtures/obras360_product-list_no-results.json"
  - "tests/fixtures/obras360_product-list_osb.json"
  - "tests/test_allmat.py"
  - "tests/test_bricomarche.py"
  - "tests/test_e2e.py"
  - "tests/test_money.py"
  - "tests/test_obras360.py"
  - "tests/test_search.py"
  - "tests/test_sheet.py"
  - "tests/test_text.py"
  - "tests/test_tracer.py"
covered_digest: "v3:sha256:a16e1ca019865ddace41ff7bb2b6b926b999a02de932fb006bf83dcebdde5794"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "O utilizador recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360 (objetivo da fase; 01-06: 'mostra para cada linha o estado das três lojas e ofertas com preço com IVA...')"
    status: failed
    reason: "O filtro de título por palavras (D-15) esconde o próprio produto pedido e a loja continua a dizer 'ok'. Reproduzido AO VIVO hoje: folha com 'tinta branca' / L / 15 -> 'Obras 360: ok' sem nenhuma oferta, só '+8 ofertas escondidas: título sem 'tinta branca''. Entre as 8 escondidas estão pelo menos 4 tintas brancas de 15 L / 20 kg (Dyrup Dyrustar, Dyrup Super, Dycrilforce 15L Branco Mate, Mapei Colorite BRANCO), escondidas porque o título diz 'Branco' e a pesquisa diz 'branca'. Como a loja devolveu resultados (raw > 0), a pesquisa alargada (D-14) não corre. Uma pesquisa à mão no site ganha à ferramenta, contra o Core Value."
    artifacts:
      - path: "src/strata/words.py"
        issue: "words() só trata o plural em -s; title_matches exige todas as palavras da pesquisa (sem género, sem palavras de ligação como 'de', sem partir '2440X590X18Mm', '15 Lt', 'OSB3')"
      - path: "src/strata/search.py"
        issue: "search_store devolve status 'ok' com offers=[] quando o filtro esconde tudo; D-14 só alarga quando raw == 0"
      - path: "src/strata/stores/obras360.py"
        issue: "linha 123: filtra pelo nome do pai; a medida (ex.: 12 mm) só existe no título da variante, por isso uma pesquisa com medida esconde o pai inteiro sempre que a loja o devolve (hoje salvo ao vivo só porque a pesquisa da loja dá zero e entra a pesquisa alargada)"
      - path: "src/strata/report.py"
        issue: "o cabeçalho 'Obras 360: ok' não diz que nenhuma oferta ficou visível"
    missing:
      - "Normalizar género, palavras de ligação e plurais em -eis/-oes/-res em words() (CR-01): 'tinta branca' tem de bater em 'Tinta Plástica 15L Branco Mate'; 'cola de contacto' em 'Cola Contacto 1L'"
      - "Partir medidas por 'x', normalizar 'lt'/'litros' e separar sufixos de classe ('OSB3') antes de comparar (CR-03)"
      - "Na Obras 360, escolher os pais com a pesquisa sem medidas e filtrar as ofertas pela pesquisa completa no título da variante (CR-02)"
      - "Quando raw > 0 e nenhuma oferta passa o filtro: não mostrar só 'ok' (detalhe '0 ofertas mostradas; N escondidas pelo filtro de título') e tentar a pesquisa alargada ou mostrar as mais baratas das escondidas, marcadas como tal (WR-01)"
      - "Testes: fixture gravada com --record para 'tinta branca' na Obras 360 e caso 'OSB 12 mm' com uma lista que devolve o pai 'Placa OSB 9-30MM'; os casos de CR-01/CR-03 em test_title_matches"
coincidental_reliance_items:
  - truth: "SC3: a Obras 360 devolve todas as variantes do produto como ofertas separadas (ex.: OSB 9, 12 e 15 mm) também para a linha 'OSB 12 mm' do próprio modelo"
    reason: undeclared-precondition
    harden: "Ao vivo só funciona porque a pesquisa interna da Obras 360 devolve zero para 'OSB 12 mm' e a pesquisa alargada 'OSB' entra; se a loja passar a devolver o pai, o filtro sobre o nome do pai esconde a placa de 12 mm (reproduzido com fixtures). Filtrar no título da variante (CR-02)."
---

# Phase 1: Folha Excel e preços da Allmat, Bricomarché e Obras 360 — Relatório de verificação

**Objetivo da fase:** O utilizador preenche o modelo Excel da app, passa o caminho do `.xlsx` à linha de comandos e recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360, já com IVA 23% e preço unitário normalizado, com o estado de cada loja sempre visível; para uma pesquisa rápida pode colar texto em vez da folha
**Verificado:** 2026-10-23T14:30:00Z
**Estado:** gaps_found
**Reverificação:** Não — verificação inicial

## Resposta curta

A estrutura toda existe, está ligada e funciona ao vivo: modelo, leitura da folha, texto colado, as três lojas, IVA, preço unitário, estados e `verificar`. Falha uma coisa, e falha no centro do objetivo: o filtro de palavras esconde o produto pedido e a loja diz "ok" sem mostrar nenhum preço. Confirmado ao vivo com "tinta branca" na Obras 360. Por isso o estado é **gaps_found**, com uma lacuna (uma causa, três sintomas: CR-01, CR-02, CR-03, mais o WR-01).

## Nota sobre o modo MVP

O ROADMAP marca a fase com `**Mode:** mvp`, mas o objetivo não está no formato de história de utilizador (`user-story.validate` → `valid: false`: falta "As a …, I want to …, so that …."). A regra do modo MVP manda recusar a verificação nesse caso. Não recusei: o orquestrador pediu a verificação e o objetivo descreve um fluxo de utilizador claro, que usei para a tabela abaixo. Se quiser o formato certo, correr `/gsd-mvp-phase 1` antes da próxima verificação.

## User Flow Coverage

Fluxo derivado do objetivo (sem história formal; ver nota acima).

| Passo | Esperado | Evidência | Estado |
|-------|----------|-----------|--------|
| 1. Obter o modelo | `modelo` grava modelo.xlsx com os 7 cabeçalhos, 2 exemplos e a lista da Unidade; não sobrescreve | Corrido numa pasta nova: código 0; 2.ª vez código 1 e SHA1 igual (`5b6858e6…`); cabeçalhos e `D2:D1000` lidos com openpyxl | ✓ |
| 2. Preencher e passar o `.xlsx` | Cada linha válida vira item; linha inválida aparece "linha N: motivo" sem parar as outras | Ao vivo: "linha 5: unidade desconhecida: caixa" e as 3 linhas válidas pesquisadas, código 0 | ✓ |
| 3. Receber os preços das 3 lojas para cada linha | Para cada linha, ofertas da Allmat, Bricomarché e Obras 360 quando a loja vende o produto | Ao vivo (26 s): "OSB 12 mm" e "cimento" com ofertas; **"tinta branca": `Obras 360: ok` sem ofertas, 8 escondidas, entre elas 4 tintas brancas de 15 L** | ✗ |
| 4. Preço com IVA 23% e preço unitário | Cada oferta com preço, origem do IVA, €/unidade e stock | `report._offer_lines`; ao vivo "IVA: indicado pela loja (tax_percentage=23) · 6,20 €/m² · 1416 em stock" | ✓ |
| 5. Estado de cada loja visível | As 3 lojas sempre presentes, estado primeiro | Ao vivo e em `test_e2e.py`; "Allmat: sem resultados — também sem resultados com 'OSB'" | ✓ (ver WR-01: "ok" com zero ofertas) |
| 6. Pesquisa rápida colada | Linhas coladas lidas com descrição, quantidade e unidade | `parse_line("OSB 12mm 30 un")` → OSB 12mm / 30 / un; `cimento 10 saco` → cimento / 10 / saco | ✓ |

## Goal Achievement

### Observable Truths — critérios do ROADMAP e objetivo

| # | Verdade | Estado | Evidência |
|---|---------|--------|-----------|
| G | O utilizador recebe, para cada linha, os preços na hora das três lojas | ✗ FAILED | Ao vivo: "tinta branca" → `Obras 360: ok` + "+8 ofertas escondidas"; `title_matches("tinta branca", "Tinta Plástica 15L Branco Mate")` → False |
| SC1 | Modelo Excel, linha de comandos com o `.xlsx`, linhas inválidas com número e motivo sem parar as outras | ✓ VERIFIED | `sheet.py` (`write_template`, `read_sheet`, `find_table`); `test_sheet.py` (20+ casos); corrida ao vivo acima |
| SC2 | Lista colada multilinha lida com descrição, quantidade e unidade; texto livre sem categoria | ✓ VERIFIED | `text.parse_line`/`read_pasted`, `__main__.cmd_pesquisar` sem ficheiro; `test_text.py`; só o Produto vai para a pesquisa (`search.py:21`) |
| SC3 | Bricomarché: mais barato entre lojas físicas com nome e link; Allmat: caixa convertida com a área; Obras 360: todas as variantes, IVA convertido, escalões | ✓ VERIFIED (coincidental-reliance) | Ao vivo: "18,49 € PLACA OSB 12 MM · loja: Coina - Barreiro · com stock: 19,99 € em Monção"; Allmat `parse_box` + `test_allmat.py`; Obras 360 9/12/15/18/22 mm com "escalões: −2,5% a partir de 90". A linha "OSB 12 mm" só mostra as variantes porque a pesquisa da loja dá zero (ver coincidental_reliance_items) |
| SC4 | Cada oferta mostra preço com IVA, origem do IVA, preço unitário normalizado e stock, sem filtrar | ✓ VERIFIED | `report._offer_lines`; ao vivo em todas as ofertas mostradas. WR-02 (packs "2x25kg") fica como aviso |
| SC5 | Estado das três lojas por item ("OSB" na Allmat = "sem resultados"); `verificar` diz por adaptador se ainda devolve preços válidos | ✓ VERIFIED | `search_store` converte qualquer falha num estado; `verificar` ao vivo: 4 × OK, código 0, 28 s. Aviso WR-01: "ok" com zero ofertas engana quem lê só o estado |

### Observable Truths — must_haves dos planos (resumidas)

| Plano | Verdades | Estado | Evidência |
|-------|----------|--------|-----------|
| 01-01 (8) | modelo D-05/06/07; secção "Allmat: <estado>"; "sem resultados" para osb; preço/IVA/stock/link; linhas inválidas; ordem por STORES; máx. 5 + "+N ofertas não mostradas"; `pesquisar` não cria ficheiros | 8/8 ✓ | `test_tracer.py`, `test_sheet.py`; ao vivo a pasta ficou só com `lista.xlsx`, `modelo.xlsx`, `out.txt` |
| 01-02 (12) | testes sem rede; folha cimento/osb/caixa; cabeçalho na linha 3, ordem e acentos; 2.ª folha; motivos de linha inválida; folha vazia → código 2; ordem; duplicados; texto colado; avisos D-12; só o Produto pesquisado | 12/12 ✓ | `conftest.no_network` + `FakeFetcher`; `test_sheet.py`, `test_text.py`; `pesquisar nao-existe.xlsx` → "Erro na folha: ficheiro não encontrado", código 2 |
| 01-03 (7) | pesquisa alargada D-14; ofertas escondidas contadas D-15; ordem pela unidade pedida; ordenação estável; preço unitário; caixa M2 da Allmat; estados bloqueada/tempo esgotado/erro | 7/7 ✓ | `test_search.py` (`test_pesquisa_alargada_*`, `test_ordem_estavel_*`, `test_estados_da_loja_*`, `test_prazo_esgotado`), `test_allmat.py`. O filtro faz o que D-15 diz; o defeito está no efeito sobre o objetivo (lacuna G) |
| 01-04 (6) | secção a seguir à Allmat; loja física mais barata com nome e link; preço sempre de variação > 0; stock e "com stock: … em …"; IVA regra da loja; nota de não expandidos | 6/6 ✓ | `test_bricomarche.py` (`test_preco_do_pai_nunca_e_mostrado`, `test_offer_from_amostra_47412`, `test_so_os_10_pais_*`); ao vivo |
| 01-05 (7) | secção a seguir à Bricomarché; uma oferta por variante; IVA da loja confirmado ±0,01; IVA ≠ 23% com nota; escalões; preço unitário e stock; notas de não expandidos/detalhe falhado | 7/7 ✓ | `test_obras360.py` (`test_iva_diferente_de_23_nao_e_convertido`, `test_escaloes_por_variante`, `test_todos_os_detalhes_falham_e_erro`); ao vivo |
| 01-06 (4) | `verificar` OK/FALHOU e código 1; regras de falha por loja; 'placa osb'/'cimento'/'xyzqwkk' pela ordem das lojas; folha de 3 linhas contra as lojas reais com ofertas por linha | 3/4 ✓, 1 ✗ | `test_search.py::test_verificar_*`, `test_e2e.py`; `verificar` ao vivo 4 × OK. **Falha** a 4.ª: a folha do próprio human-check do plano ("tinta branca" / L / 15) não mostra ofertas da Obras 360 (mesma causa da lacuna G) |

**Score:** 48/50 verdades verificadas (0 presentes sem prova de comportamento). As verdades de comportamento (ordem das lojas qualquer que seja a que responde primeiro, ordenação estável, prazo esgotado, bloqueio) têm testes com nome que correram verdes na suite (137 passed).

### Required Artifacts

| Artefacto | Esperado | Estado | Detalhe |
|-----------|----------|--------|---------|
| `pyproject.toml` | uv, curl_cffi, openpyxl, selectolax, pytest | ✓ VERIFIED | `verify.artifacts` 01-01: 7/7 |
| `src/strata/models.py` | Item, Invalida, Offer, Found, StoreResult, ItemResult | ✓ VERIFIED | usados em todos os módulos |
| `src/strata/fetch.py` | limites por host, classificação de falhas, `--record`, `parse_float=Decimal` | ✓ VERIFIED | `LIMITS`, `Host`, `StoreBlocked/StoreError/StoreTimeout` |
| `src/strata/sheet.py` | `read_sheet`, `write_template`, `SheetError` | ✓ VERIFIED | criação exclusiva `open(path, "xb")` |
| `src/strata/text.py` | `parse_line`, `read_pasted` | ✓ VERIFIED | |
| `src/strata/words.py` | `words`, `title_matches`, `broadened` | ⚠️ VERIFIED com defeito | existe e está ligado; é a origem da lacuna G |
| `src/strata/money.py` | `from_minor`, `in_unit`, `content_from_title`, `add_vat` | ✓ VERIFIED | WR-02 em packs |
| `src/strata/search.py` | `STORES`, `search_store`, `run`, `verificar` | ✓ VERIFIED | `STORES = (allmat, bricomarche, obras360)` |
| `src/strata/report.py` | secção por loja, `MAX_SHOWN` | ✓ VERIFIED | |
| `src/strata/stores/allmat.py`, `bricomarche.py`, `obras360.py` | adaptadores | ✓ VERIFIED | ao vivo os três devolvem preços |
| `tests/test_obras360.py` | contém "DiscountByQuantity" | ℹ️ padrão em falta | `verify.artifacts` 01-05: 2/3. O texto literal não está no ficheiro de teste, mas os escalões são testados (`test_escaloes_por_variante`, `test_desconto_por_quantidade_noutro_formato_vai_para_a_nota`) sobre a fixture com `DiscountByQuantity`. Não é stub |

### Key Link Verification

`verify.key-links` deu todos verdes: 01-01 4/4, 01-02 3/3, 01-03 3/3, 01-04 3/3, 01-05 3/3, 01-06 2/2. Confirmado à mão: `__main__` → `search.run` → `report.print_item`; `search_store` → `broadened`/`in_unit`; cada adaptador → `title_matches` e `fetch.get_json`; `verificar` → `search_store` e `allmat.INCOHERENT`.

### Data-Flow Trace (Level 4)

| Artefacto | Dado | Origem | Dados reais | Estado |
|-----------|------|--------|-------------|--------|
| `report.print_item` | `sr.offers[].price` | Allmat/Bricomarché Store API (cêntimos → Decimal), Obras 360 product-details (`add_vat`) | Sim, ao vivo | ✓ FLOWING |
| `report._offer_lines` | `per_unit(o)` | `content` da API/página/título | Sim (ex.: 6,20 €/m², 0,1688 €/kg) | ✓ FLOWING |
| `report.print_item` | `sr.status` | `search_store` | Sim | ✓ FLOWING, mas "ok" mesmo quando o filtro esconde tudo |

### Behavioral Spot-Checks

| Comportamento | Comando | Resultado | Estado |
|---------------|---------|-----------|--------|
| Suite sem rede | `uv run python -m pytest -q` (uma vez) | 137 passed | ✓ PASS |
| Modelo e não sobrescrever | `python -m strata modelo` ×2 numa pasta nova | 0 e 1; SHA1 igual | ✓ PASS |
| Ficheiro em falta | `python -m strata pesquisar nao-existe.xlsx` | mensagem de uma linha, código 2 | ✓ PASS |
| Texto colado | `parse_line` com "OSB 12mm 30 un", "cimento 10 saco", "mesa de jantar" | campos certos, avisos D-12 | ✓ PASS |
| Ponta a ponta ao vivo | folha OSB 12 mm / cimento / tinta branca / tijolo-caixa | 26 s, código 0; Obras 360 sem ofertas em "tinta branca" | ✗ FAIL (lacuna G) |
| Verificação das lojas ao vivo | `python -m strata verificar` | 4 × OK, código 0, 28 s | ✓ PASS |
| CR-02/CR-03 ao vivo | `search_store` real: Obras 360 "OSB 12 mm"/"osb 12mm", Bricomarché "osb 18mm"/"osb 12mm" | todos "ok" com ofertas, via pesquisa alargada (a loja devolveu zero) | ✓ PASS hoje; com fixtures em que a loja devolve o pai: 0 ofertas |

### Probe Execution

Não há probes (`scripts/*/tests/probe-*.sh`) nem probes declarados nos planos. Passo não aplicável.

### Requirements Coverage

Todos os 12 IDs da fase aparecem no campo `requirements` de pelo menos um plano. Nenhum requisito órfão: o REQUIREMENTS.md só mapeia estes 12 para a Phase 1.

| Requisito | Plano | Descrição | Estado | Evidência |
|-----------|-------|-----------|--------|-----------|
| LIST-01 | 01-02 | Lista colada multilinha | ✓ SATISFIED | `text.py`, `test_text.py` |
| LIST-02 | 01-01/02/03 | Qualquer produto em texto livre sem categoria | ✓ SATISFIED | só o Produto vai para a pesquisa; nenhuma categoria no código |
| LIST-04 | 01-01/02 | Modelo Excel de formato fixo | ✓ SATISFIED | `write_template` |
| LIST-05 | 01-01/02 | Folha → itens; inválidas com linha e motivo | ✓ SATISFIED | `read_sheet`, ao vivo |
| STORE-01 | 01-04 | Bricomarché, mais barato entre lojas físicas, com o nome | ✓ SATISFIED | ao vivo Coina - Barreiro |
| STORE-02 | 01-03 | Allmat, caixa convertida com a área | ✓ SATISFIED | `parse_box`; `verificar` (pavimento) OK |
| STORE-03 | 01-05 | Obras 360, todas as variantes e escalões | ⚠️ PARCIAL | variantes e escalões certos quando o pai passa o filtro; para "tinta branca" o utilizador não obtém nenhum preço da Obras 360 (lacuna G) |
| STORE-05 | 01-01/02/03/06 | Estado de cada loja, nenhuma omitida | ⚠️ PARCIAL | estado sempre visível e nenhuma loja omitida; mas "ok" aparece com zero ofertas e o produto existe (WR-01, parte da lacuna G) |
| STORE-07 | 01-06 | Verificação das lojas | ✓ SATISFIED | ao vivo 4 × OK |
| PRICE-01 | 01-01/02/04/05 | IVA 23% e origem do IVA | ✓ SATISFIED | três origens; Obras 360 confirmada ±0,01 |
| PRICE-02 | 01-03/05 | Preço unitário normalizado | ✓ SATISFIED (aviso WR-02) | `per_unit`, `in_unit` |
| RES-02 | 01-01/02/04/05 | Stock sem filtrar | ✓ SATISFIED | "0 em stock", "Esgotado", "esgotado (Previsão…)" |

O REQUIREMENTS.md marca STORE-03 e STORE-05 como "Complete". Rever depois de fechar a lacuna.

### Anti-Patterns Found

Sem marcadores `TBD`/`FIXME`/`XXX`/`TODO` em `src/`, `tests/`, `README.md` e `pyproject.toml`. Os cinco `shortcut:` têm limite e condição de revisão escritos.

| Ficheiro | Linha | Padrão | Gravidade | Impacto |
|----------|-------|--------|-----------|---------|
| `src/strata/words.py` | 19-27 | filtro sem género/palavras de ligação/medidas com "x" (CR-01, CR-03) | 🛑 Blocker | esconde o produto pedido (lacuna G) |
| `src/strata/stores/obras360.py` | 123 | filtro sobre o nome do pai (CR-02) | 🛑 Blocker (latente) | mesma lacuna; hoje salvo pela pesquisa alargada |
| `src/strata/search.py` | 34-45 | "ok" com zero ofertas e sem nova tentativa (WR-01) | 🛑 Blocker (parte da lacuna G) | o estado engana |
| `src/strata/money.py` | 22-32 | `content_from_title` lê o 1.º número: "2x25kg" → 25 kg (WR-02, confirmado) | ⚠️ Warning | €/kg errado em packs; a Phase 3 extrai "quantidade por embalagem" |
| `src/strata/text.py` | 34, 44 | "1.000" lido como 1 (WR-03, confirmado) | ⚠️ Warning | quantidade errada sem aviso |
| `src/strata/stores/allmat.py` | 81 | `price: ""` → `InvalidOperation` derruba a loja (WR-04, confirmado) | ⚠️ Warning | Allmat inteira em "erro" por um produto |
| `src/strata/stores/allmat.py` | 115-118 | página de caixa bloqueada derruba a loja (WR-05) | ⚠️ Warning | perde ofertas com preço válido |
| `src/strata/stores/obras360.py` | 39, 144 | `raw` em SKUs e `hidden` em pais (WR-06) | ⚠️ Warning | contagens em unidades diferentes |

### Proibições (must_haves.prohibitions)

| Proibição | Nível | Estado | Evidência |
|-----------|-------|--------|-----------|
| Nunca escrever o `.xlsx` do utilizador nem um modelo.xlsx existente | test | ✓ modelo testado; ⚠️ folha do utilizador só por inspeção | `test_modelo_nunca_sobrescreve`, `test_modelo_comando_duas_vezes` (bytes iguais). Para a folha do utilizador não há teste: o único `.save(` do código está em `write_template` com `open(path, "xb")`, e `read_sheet` só lê. Sinalizado (falta um teste de bytes iguais depois de `pesquisar`) |
| Nunca contornar a proteção das lojas nem passar o ritmo por host | judgment | ⚠️ veredicto não autoritativo: cumprida | `fetch.py`: sem retentativas, sem proxies, uma identidade fixa (`impersonate="chrome"`, decisão da stack), `LIMITS` por host, 403/429/503/cf-mitigated/desafio → "bloqueada". Revisão humana recomendada |
| Nunca deixar desaparecer ofertas/produtos/páginas sem contagem ou nota | test | ✓ VERIFIED | "+N ofertas não mostradas", "+N ofertas escondidas", notas de limite; testes em `test_search.py`, `test_allmat.py`, `test_tracer.py` |
| Nunca mostrar o preço do pai da Bricomarché | test | ✓ VERIFIED | `test_preco_do_pai_nunca_e_mostrado` |
| Nunca mostrar o preço da linha-pai da Obras 360 | test | ✓ VERIFIED | `_list_price` só ordena; ofertas só de `offers_from_details`; `test_paginas_por_total_e_so_20_detalhes_dos_mais_baratos` |
| Nunca converter em silêncio IVA ≠ 23% | test | ✓ VERIFIED | `test_iva_diferente_de_23_nao_e_convertido` |

### Human Verification Required

Ficam para o UAT do fim da fase. Não mudam o estado (a lacuna já o fixa em gaps_found).

1. **Lista da Unidade no Excel.** Teste: `uv run python -m strata modelo`, abrir no Excel, clicar na coluna Unidade e escrever "caixa". Esperado: un, m², m, kg, L, saco com o "²" certo e o aviso "Escolha da lista: …". Porquê: não há Excel nesta máquina.
2. **Colar numa consola normal do Windows.** Teste: `uv run python -m strata pesquisar`, colar `azulejo 2,5 m²`, Enter duas vezes. Esperado: "Linha 1 — azulejo (2,5 m²)". Porquê: só o pipe foi testado.
3. **Link da Bricomarché.** Teste: abrir o link de Coina - Barreiro da 1.ª oferta. Esperado: página do produto nessa loja (não "escolher loja"), 14,49 € (placa 9 mm) ou 18,49 € (PLACA OSB 12 MM), preço com IVA (A9). Porquê: o preço é desenhado por JavaScript e o IVA não está escrito.
4. **Variante de 12 mm da Obras 360.** Teste: abrir o link da variante "1 Placa 12 MM". Esperado: 19,37 € com IVA (15,75 € sem IVA). Porquê: confirmar o que o comprador vê.
5. **Proibição de ritmo e proteção (judgment).** Teste: ler `src/strata/fetch.py` e confirmar que não há retentativas, proxies nem troca de identidade. Esperado: concordar com o veredicto acima. Porquê: proibição de nível judgment.

### Gaps Summary

Uma lacuna, uma causa: o filtro de título por palavras (`words.py`) é estrito demais e, quando esconde tudo, a loja continua "ok" e a pesquisa alargada não corre.

- **Confirmado ao vivo hoje:** "tinta branca" → `Obras 360: ok` sem ofertas; a loja vende pelo menos 4 tintas brancas de 15 L que o filtro escondeu ("Branco" ≠ "branca"). É uma linha do próprio human-check do plano 01-06.
- **Confirmado com fixtures, latente ao vivo:** "OSB 12 mm" (a linha de exemplo do modelo) e "osb 18mm" dão 0 ofertas quando a loja devolve o produto; ao vivo hoje passam só porque a pesquisa da loja dá zero e entra a pesquisa alargada. A reprodução do orquestrador para CR-02 usou a lista gravada para "placa osb", não uma resposta real a "OSB 12 mm"; o defeito do código existe na mesma.

**Classificação:** lacuna da fase (BLOCKER), não adiada. A Phase 3 classifica exato/parecido sobre as ofertas que lhe chegam, mas nenhum critério dela fala em mudar o filtro que as esconde antes; o pedido "recebe, para cada linha, os preços" é desta fase. Também não é uma "omissão silenciosa" no sentido estrito do STORE-05 (a contagem "+8 ofertas escondidas" aparece), mas o estado "ok" sem preço e o produto à venda falham o objetivo e o Core Value ("igual ou mais barato do que uma pesquisa feita à mão").

**Se decidir aceitar e passar para a Phase 3**, acrescentar ao frontmatter:

```yaml
overrides:
  - must_have: "O utilizador recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360"
    reason: "Filtro de título fica como está na Phase 1; a correspondência (género, medidas, variantes) passa para a Phase 3"
    accepted_by: "{nome}"
    accepted_at: "{ISO timestamp}"
```

Os avisos WR-02 a WR-06 não bloqueiam, mas WR-03 ("1.000" → 1) e WR-04 (Allmat em "erro" por um `price: ""`) são correções de poucas linhas que convém juntar ao plano de fecho.

---

_Verificado: 2026-10-23T14:30:00Z_
_Verificador: Claude (gsd-verifier)_
