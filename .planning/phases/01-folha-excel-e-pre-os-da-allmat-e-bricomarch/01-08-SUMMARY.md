---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 08
subsystem: search
tags: [title-filter, d-15, d-16, obras360, bricomarche, gap-closure]

requires:
  - phase: 01-04
    provides: "adaptador da Bricomarché com D-15 sobre o nome do pai"
  - phase: 01-05
    provides: "adaptador da Obras 360 (pais da lista, uma oferta por variante do detalhe)"
  - phase: 01-07
    provides: "words() com STOP e _stem; search_store com contagem quando tudo fica escondido"
provides:
  - "obras360.search: pais escolhidos com broadened(query) or query; ofertas filtradas com title_matches(query, o.title); variantes cortadas somam a hidden"
  - "words(): DIMS (LxCxE), LITRE ('15 Lt'/'15 litros' = '15l') e CLASS ('OSB3' = 'osb 3') antes do JOIN"
affects: [report, verificar, phase-03-match]

actuals:
  tokens: 1680    # chars/4 sobre o diff 692a4ee..44b0328 (6718 caracteres)
  tasks: 2
  commits: 4
plan_head_before: 692a4ee3219fdbb488c1a553bb8b7d124687b18b
plan_head_after: 44b0328f26a760bd054d2de271bee954c925ee03

tech-stack:
  added: []
  patterns:
    - "Filtro D-15 em dois níveis na Obras 360: pai sem medidas, variante com a pesquisa completa"

key-files:
  created: []
  modified:
    - src/strata/stores/obras360.py
    - src/strata/words.py
    - tests/test_obras360.py
    - tests/test_search.py
    - tests/test_bricomarche.py

key-decisions:
  - "Obras 360: o pai escolhe-se com broadened(query) or query porque a medida só existe na designação da variante; a pesquisa completa filtra o título pai + designação"
  - "hidden da Obras 360 = pais escondidos + variantes cortadas, para nenhuma variante sumir sem contagem (D-02, D-15)"
  - "words(): DIMS, LITRE e CLASS por esta ordem antes do JOIN; CLASS sem \\b à esquerda para '2,5mm2' e '2,5 mm2' darem o mesmo"

patterns-established:
  - "Uma oferta cortada por um filtro conta sempre como escondida, seja pai ou variante"

requirements-completed: [STORE-03, STORE-01, LIST-02]

coverage:
  - id: D1
    description: "'OSB 12 mm' na Obras 360 mostra só a variante '1 Placa 12 MM' a 19,37 € quando a loja devolve o pai 'Placa OSB 9-30MM', com as outras 6 contadas como escondidas e sem pesquisa alargada (CR-02)"
    requirement: "STORE-03"
    verification:
      - kind: integration
        ref: "tests/test_obras360.py#test_osb_12mm_so_a_variante_de_12mm"
        status: pass
    human_judgment: false
  - id: D2
    description: "Pesquisas sem medidas na Obras 360 dão as mesmas ofertas e contagens de antes ('placa osb' 7/1, 'osb' 7/0, 'tinta branca' 4 tintas/4)"
    requirement: "STORE-03"
    verification:
      - kind: integration
        ref: "tests/test_obras360.py (25 passed: test_search_placa_osb_le_o_widget_uma_vez, test_produto_sem_detalhe_vai_para_a_nota, test_tinta_branca_gravada_mostra_as_tintas_brancas)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Filtro de título reconhece medidas LxCxE, '15 Lt'/'15 litros' e 'OSB3'; 'osb 12mm' continua a não bater em 'Chapa Osb 2440X590X18Mm' (CR-03)"
    requirement: "LIST-02"
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_title_matches (23 casos)"
        status: pass
    human_judgment: false
  - id: D4
    description: "'osb 18mm' na Bricomarché expande o pai 37387 'Chapa Osb 2440X590X18Mm' (raw 4, hidden 3, um pedido de variações)"
    requirement: "STORE-01"
    verification:
      - kind: integration
        ref: "tests/test_bricomarche.py#test_medidas_coladas_por_x_batem_no_filtro"
        status: pass
      - kind: e2e
        ref: "uv run python -m strata verificar (corrida ao vivo única, 2026-10-23, 4 linhas OK)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Folha de 3 linhas ('OSB 12 mm', 'cimento cola', 'tinta branca') pelo fluxo real, com os preços comparados com os sites"
    requirement: "STORE-03"
    verification: []
    human_judgment: true
    rationale: "Human-check do plano (fim da fase): só uma pessoa compara os preços mostrados com os que os sites mostram"

duration: 3min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 08: filtro em dois níveis na Obras 360 e medidas LxCxE, "Lt" e "OSB3" — Summary

**"OSB 12 mm", a linha de exemplo do modelo, mostra na Obras 360 a placa de 12 mm a 19,37 € mesmo quando a loja devolve o pai "Placa OSB 9-30MM"; as outras 6 espessuras ficam contadas como escondidas. O filtro de título passou a partir "2440X590X18Mm" pelo "x", a ler "15 Lt"/"15 litros" como "15l" e "OSB3" como "osb", e a Bricomarché já expande a chapa de 18 mm para "osb 18mm".**

## Performance

- **Duração:** 3 min (execução das tarefas)
- **Início:** 2026-10-23T10:44:39Z
- **Fim:** 2026-10-23T10:48:07Z
- **Tarefas:** 2
- **Ficheiros:** 5 alterados

## Accomplishments

- CR-02 fechado: a Obras 360 escolhe os pais com a pesquisa sem medidas e filtra as variantes pela pesquisa completa. O SC3 deixa de depender de a loja dar zero e entrar a pesquisa alargada (a coincidental reliance do 01-VERIFICATION.md).
- CR-03 fechado: `words()` com `DIMS`, `LITRE` e `CLASS`. Os 17 casos antigos de `test_title_matches` continuam iguais.
- `verificar` ao vivo verde depois das mudanças (ver abaixo).
- Suite: 153 → 161 testes, todos verdes.

## Task Commits

1. **Tarefa 1 (tracer): "OSB 12 mm" na Obras 360 mostra a placa de 12 mm**
   - RED `324175b` (test): `test_osb_12mm_so_a_variante_de_12mm`
   - GREEN `efa734f` (feat): `obras360.search` com o filtro em dois níveis
2. **Tarefa 2: medidas coladas por "x", "Lt" e "OSB3"**
   - RED `8ba693b` (test): 6 casos em `test_title_matches` e `test_medidas_coladas_por_x_batem_no_filtro`
   - GREEN `44b0328` (feat): `DIMS`, `LITRE`, `CLASS` em `words()`

Sem REFACTOR: nada a limpar.

## TDD

- **RED Tarefa 1:** `uv run python -m pytest tests/test_obras360.py -k osb_12mm -q` → código 1, "1 failed, 1 error". O teste-alvo falhou em `assert sr.status == "ok"` (`'erro' == 'ok'`). Causa: o nome do pai não tem "12mm", o filtro escondeu tudo, `search_store` tentou a pesquisa alargada "OSB" e essa URL não tem rota no `fake` (daí também o erro de teardown "fixture em falta"). Avaliação semântica: RED válido. A falha mostra exatamente a lacuna, porque o resultado só podia vir da alargada.
- **RED Tarefa 2:** `-k "title_matches or medidas_coladas"` → código 1, "6 failed, 18 passed". Falharam os 5 casos novos que devem bater (`False is True`) e o teste da Bricomarché em `found.hidden == 3` (era 4, sem pedidos de variações). O caso False novo ("osb 12mm" vs "Chapa Osb 2440X590X18Mm") já passava, como guarda. Avaliação semântica: RED válido.
- O classificador `gsd_run check tdd-red-evidence` não foi corrido: a saída do pytest não está nos formatos suportados e o plano não é `type: tdd` nem há `workflow.tdd_mode`. A avaliação semântica acima fica como registo.
- **GREEN:** 1 passed (osb_12mm), 25 passed (test_obras360.py), 24 passed (title_matches + medidas_coladas), 161 passed na suite.
- **Tracer:** `<verify>` só automático, modo interativo `end-of-phase`: re-corrido depois do GREEN (1 passed, 25 passed) antes da Tarefa 2.

## Saída ao vivo (`verificar`, corrida única, 2026-10-23)

Pré-condição: GET com `curl_cffi` (impersonate chrome) a allmat.pt, www.bricomarche.pt e www.obras360.pt → 200 nas três. Depois uma só corrida, 30 s:

```
Allmat (cimento): OK — 11 ofertas, mais barata 4,22 €
Allmat (pavimento): OK — 24 ofertas, mais barata 7,50 €
Bricomarché (cimento): OK — 10 ofertas, mais barata 0,58 €
Obras 360 (osb): OK — 20 ofertas, mais barata 8,36 €
```

Código de saída 0.

## Files Created/Modified

- `src/strata/stores/obras360.py`: importa `broadened`; pais com `loose = broadened(query) or query`; `shown = [o for o in offers if title_matches(query, o.title)]`; `hidden` soma as variantes cortadas; um `shortcut:` novo sobre gamas no nome do pai (3 no ficheiro).
- `src/strata/words.py`: `DIMS`, `LITRE`, `CLASS`; `words()` aplica-os antes do `JOIN`; docstring atualizada. `title_matches` e `broadened` não mudaram.
- `tests/test_obras360.py`: `test_osb_12mm_so_a_variante_de_12mm`.
- `tests/test_search.py`: 6 casos em `test_title_matches` (23 no total).
- `tests/test_bricomarche.py`: `test_medidas_coladas_por_x_batem_no_filtro`.

## Decisions Made

- Plano aplicado tal como escrito. As decisões estão no frontmatter (`key-decisions`).

## Deviations from Plan

Nenhuma. O plano foi executado tal como escrito.

**Total:** 0 correções automáticas (Rules 1–3).

## Issues Encountered

- Uma edição de `words.py` por script Python falhou na asserção por causa das barras invertidas dentro do heredoc. Não escreveu nada (a asserção vem antes da escrita) e a edição foi feita com a ferramenta Edit. Sem efeito no resultado.

## Known Limitations (fora do âmbito, para o verificador)

- Uma gama no nome do pai ("9-30MM") faz "30mm" bater em todas as variantes. Já acontecia antes; fica o `shortcut:` no código e a separação exato/parecido é da Phase 3 (MATCH-01/02).
- "12,0 mm" (zero decimal) continua a não bater em "12mm", como o plano deixou fora.
- As tintas da Obras 360 continuam com "não convertível para L: vendido em un" (nota do 01-07): os 15 L só estão no texto da variante. Este plano não mexe na unidade, só no filtro. Com `LITRE`, "tinta 15 litros" já bate num título com "15 L".

## User Setup Required

Nenhum.

## Next Phase Readiness

- Último plano da Phase 1: fase pronta para verificação, com o human-check da folha de 3 linhas pendente (D5).

## Self-Check: PASSED

- 5/5 ficheiros alterados presentes; commits 324175b, efa734f, 8ba693b, 44b0328 no HEAD; `git rev-list --count 692a4ee..HEAD` = 4.
- Critérios de aceitação: osb_12mm 1 passed; test_obras360.py 25 passed; `broadened` e `title_matches(query, o.title)` em obras360.py; `grep -c "shortcut:"` = 3; title_matches + medidas_coladas 24 passed; `DIMS`/`LITRE`/`CLASS` presentes; "parent=37387&" no teste novo; suite 161 passed; `verificar` com 4 linhas ": OK — ".

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*
