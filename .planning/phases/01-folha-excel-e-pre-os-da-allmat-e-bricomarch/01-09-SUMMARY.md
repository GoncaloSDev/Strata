---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 09
subsystem: search
tags: [title-filter, d-15, d-14, d-01, obras360, gap-closure, plurais]

requires:
  - phase: 01-07
    provides: "words() com STOP e _stem; search_store com contagem quando tudo fica escondido"
  - phase: 01-08
    provides: "filtro em dois níveis na Obras 360 (loose = broadened(query) or query); DIMS, LITRE, CLASS"
provides:
  - "words._stem com a tabela PLURAL (-oes, -aes, -eis, -ais, -ois, -uis, -ens, -is e -il para -i, -s) e limite de 2 letras"
  - "words.UNIT_TOKENS com 'lts', 'litro', 'litros'"
  - "obras360.search: pais que batem na pesquisa completa à frente do corte K=20, depois pelo preço da lista"
  - "search_store: detail '0 ofertas mostradas de N resultados da loja' quando não há ofertas nem escondidas"
affects: [report, verificar, phase-03-match]

actuals:
  tokens: 2324    # chars/4 sobre o diff aa5c6b7..7e8a8d4 (9295 caracteres)
  tasks: 3
  commits: 6
plan_head_before: aa5c6b73c5d2ab78f2872e7a75d10cede3da96b5
plan_head_after: 7e8a8d40edb99029f1200fb9e23351d30d807e16

tech-stack:
  added: []
  patterns:
    - "Plurais por tabela de sufixos (ganha o primeiro que bate), só biblioteca padrão"
    - "Corte K por relevância antes do preço: quem bate na pesquisa completa entra primeiro"

key-files:
  created: []
  modified:
    - src/strata/words.py
    - src/strata/stores/obras360.py
    - src/strata/search.py
    - tests/test_search.py
    - tests/test_obras360.py

key-decisions:
  - "_stem: -is e -il vão os dois para -i (não -is -> -il do 01-REVIEW.md), para perfis/Perfil e funis/Funil baterem sem perder táxis/Táxi e jacuzzis/Jacuzzi"
  - "Obras 360: chave do corte K=20 = (não bate na pesquisa completa, preço em falta, preço); continua a haver no máximo 20 pedidos de detalhe"
  - "Loja com resultados e zero ofertas sem nada escondido: estado continua 'ok', o cabeçalho diz '0 ofertas mostradas de N resultados da loja' e o motivo fica nas notas"
  - "Tracer da Tarefa 1: verify automático re-corrido (35/1/174 passed) e a corrida ao vivo 'perfis' fica para o human-check do fim da fase, como o orquestrador indicou"

patterns-established:
  - "Um filtro que corta para um limite (K) ordena primeiro pela relevância e só depois pelo preço"

requirements-completed: [LIST-02, STORE-03, STORE-05]

coverage:
  - id: D1
    description: "Plurais -ais/-eis/-ois/-uis/-ens/-aes/-is e palavras de 3 letras batem no singular do título (perfis/Perfil, funis/Funil, canais/Canal, ferragens/Ferragem, lençóis/Lençol, pás/Pá); lápis, jacuzzis, táxis continuam a bater; aquecimento/Cimento, porta/Portão e ip65/IP44 continuam False (CR-05)"
    requirement: "LIST-02"
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_title_matches (35 casos)"
        status: pass
    human_judgment: false
  - id: D2
    description: "'perfis' na Obras 360 expande o pai 'Perfil Montante 48mm …', mostra as variantes com preço, cabeçalho 'Obras 360: ok' e '+1 ofertas escondidas: título sem 'perfis''; a calha não é expandida (CR-05)"
    requirement: "STORE-03"
    verification:
      - kind: integration
        ref: "tests/test_obras360.py#test_perfis_mostra_o_pai_perfil"
        status: pass
    human_judgment: false
  - id: D3
    description: "'parafuso m8' com 25 parafusos genéricos mais baratos expande o 'Parafuso Sextavado M8' (o mais caro), mostra só as variantes dele, com exatamente 20 pedidos de detalhe e a nota '+6 produtos não expandidos' (CR-04)"
    requirement: "STORE-03"
    verification:
      - kind: integration
        ref: "tests/test_obras360.py#test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte"
        status: pass
      - kind: integration
        ref: "tests/test_obras360.py (27 passed, incl. test_paginas_por_total_e_so_20_detalhes_dos_mais_baratos e test_osb_12mm_so_a_variante_de_12mm)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Loja com resultados e zero ofertas sem nada escondido mostra 'Allmat: ok — 0 ofertas mostradas de 3 resultados da loja' com a nota '3 produtos sem preço ignorados' (WR-10)"
    requirement: "STORE-05"
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_zero_ofertas_sem_escondidas_nao_diz_so_ok"
        status: pass
    human_judgment: false
  - id: D5
    description: "broadened('tinta 15 litros') == 'tinta' (IN-08)"
    requirement: "LIST-02"
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_broadened (6 casos)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Corrida ao vivo 'perfis 10 un' pelo Fetcher normal: a Obras 360 mostra ofertas 'Perfil …' com IVA e a linha de escondidas fica muito abaixo das 122 que o verificador viu"
    requirement: "STORE-03"
    verification: []
    human_judgment: true
    rationale: "Human-check do plano (fim da fase): a lacuna foi vista ao vivo e só uma pessoa compara com o que o site mostra para 'perfis'"

duration: 3min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 09: plurais no filtro de título, corte K=20 por relevância e "ok" com zero ofertas — Summary

**"perfis" passa a bater em "Perfil" (tabela `PLURAL` em `_stem`, com -is e -il para -i), por isso a Obras 360 expande e mostra os perfis em vez de os esconder. O pai que bate na pesquisa completa ("Parafuso Sextavado M8") entra sempre nos 20 expandidos, mesmo sendo o mais caro. Uma loja com resultados e zero ofertas diz "0 ofertas mostradas de N resultados da loja", e "tinta 15 litros" alarga para "tinta".**

## Performance

- **Duração:** 3 min
- **Início:** 2026-10-23T11:31:06Z
- **Fim:** 2026-10-23T11:33:41Z
- **Tarefas:** 3
- **Ficheiros:** 5 alterados (3 de código, 2 de testes)

## Accomplishments

- CR-05 fechado (a lacuna do 01-VERIFICATION.md): `_stem` com a tabela `PLURAL` e limite de 2 letras. perfis, funis, canais, ferragens, lençóis e pás batem no singular.
- CR-04 fechado: na Obras 360, a chave do corte K=20 põe à frente os pais que batem na pesquisa completa. O número de pedidos de detalhe não muda (20).
- WR-10 fechado: nenhuma loja com resultados e zero ofertas aparece como "ok" sozinho.
- IN-08 fechado: `UNIT_TOKENS` com "lts", "litro" e "litros".
- Suite: 161 → 177 testes, todos verdes.

## Task Commits

1. **Tarefa 1 (tracer): "perfis" na Obras 360 expande e mostra o pai "Perfil …" (CR-05)**
   - RED `1fdf744` (test): 12 casos em `test_title_matches`, `parent()` e `test_perfis_mostra_o_pai_perfil`
   - GREEN `b7f068d` (feat): `PLURAL` e o ciclo em `_stem`
2. **Tarefa 2: "parafuso m8" expande o pai M8 mesmo sendo o mais caro (CR-04)**
   - RED `78de8cd` (test): `test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte`
   - GREEN `3e03ce3` (fix): chave de ordenação dos pais em `obras360.search`
3. **Tarefa 3: zero ofertas explicado no cabeçalho (WR-10) e "tinta 15 litros" (IN-08)**
   - RED `52a5261` (test): `test_zero_ofertas_sem_escondidas_nao_diz_so_ok` e o caso em `test_broadened`
   - GREEN `7e8a8d4` (fix): `detail` em `search_store` e `UNIT_TOKENS`

Sem REFACTOR: nada a limpar. As Tarefas 2 e 3 usam `fix(...)` no GREEN porque corrigem defeitos da revisão; a sequência test → código está em todas.

## TDD

- **RED Tarefa 1:** `-k title_matches` → código 1, "6 failed, 29 passed": os 6 casos True novos (perfis, funis, canais, ferragens, lençóis, pás) deram `False is True`; os 6 guardas (lápis, jacuzzis, táxis, ip65 ×2, m²) já passavam. `-k perfis` → código 1, falhou em `sr.detail == ""` com "0 ofertas mostradas; 2 escondidas pelo filtro de título" (o pai "Perfil …" ficou escondido). Avaliação semântica: RED válido, as duas falhas são a lacuna.
- **RED Tarefa 2:** `-k frente_do_corte` → código 1, falhou em `"id-m8" in details` (só id-00..id-19 expandidos). RED válido.
- **RED Tarefa 3:** `-k "zero_ofertas or broadened or verificar_todos_a_zero"` → código 1, "2 failed, 6 passed": `'tinta litros' == 'tinta'` e `'' == '0 ofertas mostradas de 3 resultados da loja'`. RED válido.
- O classificador `gsd_run check tdd-red-evidence` não foi corrido: a saída do pytest não está nos formatos suportados e o plano não é `type: tdd`. A avaliação semântica fica como registo, como no 01-08.
- **GREEN:** title_matches 35 passed; perfis 1 passed; frente_do_corte 1 passed; test_obras360.py 27 passed; Tarefa 3 8 passed; suite 174 → 175 → 177 passed.
- **Tracer:** o `<verify>` tem um `<human-check>` (corrida ao vivo "perfis"). O verify automático foi re-corrido depois do GREEN (35 / 1 / 174 passed) e a corrida ao vivo ficou para o human-check do fim da fase, como pedia o orquestrador. Nenhum pedido ao vivo foi feito neste plano.

## Files Created/Modified

- `src/strata/words.py`: `PLURAL` ao lado de `STOP`; `_stem` com limite `len(w) <= 2` e ciclo `for suf, rep in PLURAL`; docstring com perfis/perfil e ferragens; `UNIT_TOKENS` com "lts", "litro", "litros".
- `src/strata/stores/obras360.py`: chave do `kept.sort` = `(not title_matches(query, nome), preço em falta, preço)` e comentário sobre a pesquisa solta. Os 3 `shortcut:` ficam.
- `src/strata/search.py`: ramo `if not found.offers` com as duas frases (escondidas / resultados da loja).
- `tests/test_search.py`: 12 casos em `test_title_matches`, 1 em `test_broadened`, `test_zero_ofertas_sem_escondidas_nao_diz_so_ok`.
- `tests/test_obras360.py`: `parent()`, `test_perfis_mostra_o_pai_perfil`, `test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte`.

## Decisions Made

As do frontmatter (`key-decisions`). O código segue o plano tal como escrito.

## Deviations from Plan

Nenhuma no código. Um ajuste de texto:

- O comentário da `PLURAL` tinha o literal `("il", "i")`, o que dava 2 no critério `grep -c '("il", "i")'` (esperado 1). Mudei o comentário para "O par -il -> -i" antes do commit GREEN. Sem efeito no comportamento.

**Total:** 0 correções automáticas (Rules 1–3).

## Issues Encountered

Nenhum.

## Known Limitations (para o verificador)

- Como o plano previa: a tabela junta mais palavras diferentes ("cal"/"cais", "mal"/"mais"). São falsos positivos com o título à vista, da família do WR-08 (Phase 3).
- `print_item` mostra no máximo 5 ofertas por loja. Ao vivo, os parafusos "para perfis" podem ficar à frente dos perfis. Isso é o exato/parecido da Phase 3.

## User Setup Required

Nenhum.

## Next Phase Readiness

- Último plano da Phase 1: fase pronta para re-verificação. Fica pendente o human-check da corrida ao vivo "perfis 10 un" (D6), além do da folha de 3 linhas do 01-08.

## Self-Check: PASSED

- 5/5 ficheiros alterados presentes; commits 1fdf744, b7f068d, 78de8cd, 3e03ce3, 52a5261, 7e8a8d4 no HEAD; `git rev-list --count aa5c6b7..HEAD` = 6.
- Critérios de aceitação: title_matches 35 passed; perfis 1 passed; `PLURAL` ×2; `len(w) <= 2` ×1; `("il", "i")` ×1; frente_do_corte 1 passed; test_obras360.py 27 passed; `not title_matches(query` ×1; `shortcut:` ×3; Tarefa 3 8 passed; `resultados da loja` ×1; `"litros"` em `UNIT_TOKENS` ×1; suite 177 passed.

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*
