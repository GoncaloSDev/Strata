---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 07
subsystem: search
tags: [title-filter, d-15, d-14, obras360, fixtures, record]

requires:
  - phase: 01-03
    provides: "search_store com D-14 (pesquisa alargada) e o filtro de título D-15 (words/title_matches)"
  - phase: 01-05
    provides: "adaptador da Obras 360 (lista de pais + detalhe por variante) com o filtro D-15 sobre o nome do pai"
  - phase: 01-06
    provides: "pesquisar --record e o verificar; a lacuna 'tinta branca' observada ao vivo"
provides:
  - "words(): STOP (palavras de ligação) e _stem (género e plurais em -eis/-ões/-res/-s)"
  - "search_store: D-14 também quando D-15 esconde todas as ofertas; detalhe com a contagem no cabeçalho"
  - "fixtures reais da Obras 360 para 'tinta branca' (lista + 4 detalhes)"
affects: [01-08, report, verificar]

actuals:
  tokens: 76129    # chars/4: 2330 do diff de código e testes + 73799 das 5 fixtures gravadas
  tasks: 2
  commits: 4
plan_head_before: 4521711cf500e3c44939314810b57859e1dcaddd
plan_head_after: 4d69607e97353764c8a924a27c9f2889e2f79b1e

tech-stack:
  added: []
  patterns:
    - "Normalização de palavras só com biblioteca padrão (STOP + _stem), sem stemmer externo"
    - "Fixtures gravadas ao vivo com --record e renomeadas com nomes descritivos; só os corpos usados entram no git"

key-files:
  created:
    - tests/fixtures/obras360_product-list_tinta-branca.json
    - tests/fixtures/obras360_product-details_tinta-dyrustar.json
    - tests/fixtures/obras360_product-details_tinta-dyrup-super.json
    - tests/fixtures/obras360_product-details_tinta-dycrilforce.json
    - tests/fixtures/obras360_product-details_tinta-colorite.json
  modified:
    - src/strata/words.py
    - src/strata/search.py
    - tests/test_search.py
    - tests/test_obras360.py

key-decisions:
  - "WR-01: com tudo escondido pelo filtro, o cabeçalho diz '0 ofertas mostradas; N escondidas pelo filtro de título' e a pesquisa alargada de D-14 tenta uma vez (só com números/medidas); substitui a resolução n.º 2 das Open Questions do 01-RESEARCH.md"
  - "Se a alargada também não traz ofertas, fica a 1.ª pesquisa (contagem e palavras escritas pelo utilizador) com a nota 'também sem ofertas com <alargada>'"
  - "_stem: tokens com dígitos ou com 3 letras ou menos ficam iguais; -oes→ao, -eis→el, senão tira o -s; depois tira a/o/e final se ficarem mais de 3 letras"

patterns-established:
  - "Uma loja com produtos e zero ofertas visíveis nunca aparece como 'ok' sozinho: o detail leva a contagem"

requirements-completed: [STORE-03, STORE-05, LIST-02, PRICE-01]

coverage:
  - id: D1
    description: "Filtro de título iguala o género, ignora palavras de ligação e trata plurais em -eis/-ões/-res, mantendo palavras inteiras (aquecimento ≠ cimento, porta ≠ portão)"
    requirement: "LIST-02"
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_title_matches (17 casos)"
        status: pass
    human_judgment: false
  - id: D2
    description: "'tinta branca' na Obras 360 mostra as 4 tintas brancas com preço com IVA indicado pela loja e conta 4 escondidas, sobre respostas reais gravadas"
    requirement: "STORE-03"
    verification:
      - kind: integration
        ref: "tests/test_obras360.py#test_tinta_branca_gravada_mostra_as_tintas_brancas"
        status: pass
      - kind: e2e
        ref: "printf 'tinta branca 15 L\\n\\n' | uv run python -m strata pesquisar --record <dir> (corrida ao vivo única, 2026-10-23)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Com tudo escondido pelo filtro, o cabeçalho da loja diz quantas e, com medidas, a pesquisa alargada tenta uma vez sem perder a contagem da 1.ª"
    requirement: "STORE-05"
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_tudo_escondido_* (4 testes)"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 07: filtro de título com género e plurais, e contagem quando tudo fica escondido — Summary

**"tinta branca" volta a mostrar as quatro tintas brancas da Obras 360 (56,02 € a 135,41 €, IVA indicado pela loja): `words()` passou a ignorar "de/da/para…" e a juntar branca/branco, painéis/painel e portões/portão. Uma loja com produtos e nenhuma oferta visível passa a dizer no cabeçalho quantas o filtro escondeu, e tenta a pesquisa alargada uma vez.**

## Performance

- **Duração:** 4 min (execução das tarefas)
- **Início:** 2026-10-23T10:36:58Z
- **Fim:** 2026-10-23T10:40:56Z
- **Tarefas:** 2
- **Ficheiros:** 9 (4 alterados, 5 fixtures novas)

## Accomplishments

- CR-01 fechado: `title_matches("tinta branca", "Tinta Plástica 15L Branco Mate")` dá True, e também "cola de contacto", "painéis", "luzes", "colheres", "portões", "lustres". "aquecimento" continua a não bater em "Cimento cola", e "porta" não bate em "Portão".
- Corrida ao vivo única: a Obras 360 mostra as 4 tintas brancas com preço e IVA da loja (ver "Saída ao vivo").
- WR-01 fechado: `search_store` nunca devolve "ok" sozinho quando o filtro escondeu tudo. O cabeçalho diz "0 ofertas mostradas; N escondidas pelo filtro de título", ou "N escondidas pelo filtro de título com '<pesquisa>'" quando a alargada entrou.
- Suite: 137 → 153 testes, todos verdes.

## Task Commits

1. **Tarefa 1 (tracer): filtro com género, palavras de ligação e plurais + fixture gravada**
   - RED `b5458f4` (test): 11 casos novos em `test_title_matches`
   - GREEN `eaaf390` (feat): `STOP`, `_stem`, fixtures e `test_tinta_branca_gravada_mostra_as_tintas_brancas`
2. **Tarefa 2: tudo escondido → contagem no cabeçalho e alargada uma vez**
   - RED `17c6465` (test): 4 testes `tudo_escondido`
   - GREEN `4d69607` (feat): `search_store`

Sem REFACTOR: nada a limpar.

## TDD

- **RED Tarefa 1:** `uv run python -m pytest tests/test_search.py -k title_matches -q` → código 1, "6 failed, 11 passed". Falharam exatamente os 6 casos novos que devem bater (tinta branca, cola de contacto, painéis, luzes, colheres, portões), todos em `assert title_matches(...) is expected` com `False is True`. "lustres" já passava (lustres→lustre pelo -s antigo), e os 4 casos False são guardas de regressão que já passavam. Avaliação semântica: RED válido, a falha é a do comportamento planeado e não de importação ou fixture.
- **RED Tarefa 2:** `-k tudo_escondido` → código 1, "4 failed". O 1.º falhou em `sr.detail == "0 ofertas mostradas; 8 …"` (detail vazio); os outros 3 em `store.calls == ["OSB 12mm", "OSB"]` (sem 2.ª pesquisa). Avaliação semântica: RED válido.
- O classificador `gsd_run check tdd-red-evidence` não foi corrido: a saída do pytest não está nos formatos suportados (TAP, JUnit, unittest, go, swift) e o plano não é `type: tdd` nem há `workflow.tdd_mode`. A avaliação semântica acima fica como registo.
- **GREEN:** 17 passed (title_matches), 1 passed (tinta_branca), 4 passed (tudo_escondido), 153 passed na suite.

## Saída ao vivo (corrida única com --record, 2026-10-23)

Pré-condição: um GET a `https://www.obras360.pt/` deu 200. Depois uma só corrida de `tinta branca 15 L` pelo Fetcher normal (LIMITS por host), sem repetir. Secção da Obras 360, transcrita:

```
  Obras 360: ok
    56,02 €  Tinta Interior/Exterior Plástica Acrílica Lisa Dyrup Super 15L Branco Mate Lavável Alto Rendimento — Branco Mate - 15 L
      IVA: indicado pela loja (tax_percentage=23) · 56,02 €/un · 22 em stock · não convertível para L: vendido em un
      https://www.obras360.pt/0530010003-tinta-interior-exterior-plastica-acrilica-lisa-dyrup-super-15l-branco-mate-lavavel-alto-rendimento
    116,14 €  Tinta Interior Vinílica Dyrup Dyrustar 15L Branco Mate Aquosa Lavável Anti Fungos Elevada Qualidade — Branco Mate - 15 L
      IVA: indicado pela loja (tax_percentage=23) · 116,14 €/un · 17 em stock · não convertível para L: vendido em un
      https://www.obras360.pt/0530010002-tinta-interior-vinilica-dyrup-dyrustar-15l-branco-mate-aquosa-lavavel-elevada-qualidade
    134,28 €  Tinta Exterior 100% Acrílica Dyrup Dycrilforce 15L Branco Mate Elevada Repelência Água Anti Fungos — Branco Mate - 15 L
      IVA: indicado pela loja (tax_percentage=23) · 134,28 €/un · 17 em stock · não convertível para L: vendido em un
      https://www.obras360.pt/0530010004-tinta-exterior-100-acrilica-dyrup-dycrilforce-15l-branco-mate-elevada-repelencia-Agua-anti-fungos
    135,41 €  Tinta 100% Acrílica Lisa Mate Exterior/Interior Fachadas Mapei Colorite Performance BRANCO 20KG — Branco - 20Kg
      IVA: indicado pela loja (tax_percentage=23) · 135,41 €/un · 16 em stock · escalões: −4,91505% a partir de 3 · não convertível para L: vendido em un
      https://www.obras360.pt/0080140027-tinta-100-acrilica-lisa-mate-exterior-interior-fachadas-mapei-colorite-performance-branco-20kg
    +4 ofertas escondidas: título sem 'tinta branca'
```

Na mesma corrida: Allmat "sem resultados"; Bricomarché "ok" com 3 ofertas (Tinta Branca Especial 15000Ml 44,95 €, Especial Tinta Branca Interior/Exterior 0.75L 6,19 €, Especial Tinta Branca Interior 11,99 €).

A lista gravada é igual à das Assumptions: 8 pais; passam Dyrustar, Dyrup Super, Dycrilforce e Colorite; ficam escondidos o Primário Dyprolite, o SecilTek Isovit e as duas fitas de pintura. Sem diferenças a registar.

## Files Created/Modified

- `src/strata/words.py`: `STOP`, `_stem`; `words()` usa-os. `title_matches` e `broadened` não mudaram.
- `src/strata/search.py`: `search_store` com o 2.º gatilho de D-14, `first_hidden` e o `detail` do estado "ok".
- `tests/test_search.py`: 11 casos em `test_title_matches`; helper `heading`; 4 testes `tudo_escondido`.
- `tests/test_obras360.py`: `TINTAS` e `test_tinta_branca_gravada_mostra_as_tintas_brancas`.
- `tests/fixtures/obras360_product-list_tinta-branca.json` (lista, 201 KB) e 4 detalhes `obras360_product-details_tinta-*.json` (22–24 KB cada).

## Decisions Made

- Decisão WR-01 do plano aplicada tal como escrita (pesquisa alargada, não mostrar as escondidas).
- `found.notes.append(...)` sobre o `Found` da 1.ª pesquisa: cada chamada à loja devolve um objeto novo, por isso não há partilha entre itens.

## Deviations from Plan

1. **Pasta da gravação no scratchpad da sessão em vez de `${TMPDIR:-/tmp}`.** As regras do ambiente pedem o scratchpad para ficheiros temporários. O comando é o mesmo; só muda `$D`. A verificação (`awk … | grep -qi branco`) passou.
2. **Detalhes com 22–24 KB, não ~55 KB.** Só informativo. Os títulos e IDs foram lidos por um script no scratchpad, sem abrir os ficheiros inteiros.

**Total:** 0 correções automáticas (Rules 1–3); 2 notas sem impacto no código.

## Issues Encountered

- A edição de `words.py` por script Python falhou à primeira porque o ficheiro tem fins de linha CRLF; foi feita com a ferramenta Edit. Sem efeito no resultado.

## Known Limitations (fora do âmbito, para o verificador)

- As tintas da Obras 360 aparecem com "não convertível para L: vendido em un": a loja vende-as à unidade (`visible_sell_unit` UN), e os 15 L só estão no texto da variante ("Branco Mate - 15 L"). O preço com IVA está certo; o €/L fica por mostrar. As medidas no título e nas variantes são do plano 01-08 / fases seguintes.
- Numa pesquisa sem números ("tinta branca"), `broadened` dá None. Com tudo escondido fica só o detalhe com a contagem, como o plano previa.

## User Setup Required

Nenhum.

## Next Phase Readiness

- Pronto para o 01-08 (CR-02, CR-03), que também mexe em `words.py`, `tests/test_search.py` e `tests/test_obras360.py`. O novo `words()` mantém o contrato `set[str]`.

## Self-Check: PASSED

- 9/9 ficheiros presentes e não vazios; commits b5458f4, eaaf390, 17c6465, 4d69607 no HEAD.
- Critérios de aceitação: 17 passed (title_matches); 1 passed (tinta_branca); `STOP`/`def _stem` presentes; `grep -l -i -E "set-cookie|authorization|bearer|csrf"` nas 5 fixtures não imprime nada; nenhum `tests/fixtures/www.*` no git; 4 passed (tudo_escondido); "escondidas pelo filtro de título" e "também sem ofertas com" em search.py; as duas frases nos testes; 153 passed na suite.
- Verificação do plano: `-k "title_matches or tudo_escondido"` → 21 passed.

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*
