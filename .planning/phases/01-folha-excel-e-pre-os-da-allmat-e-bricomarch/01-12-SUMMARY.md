---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
plan: 12
subsystem: search
tags: [wr-17, rank, k-cut, words, title-match, broadened, bricomarche, obras360, allmat]

requires:
  - phase: 01-11
    provides: "passo D-15 emendado em search_store (title_matches com o produto da linha e wide_only)"
  - phase: 261023-lee
    provides: "words() com troços seguidos (WR-07), _stem e unidades por extenso"
provides:
  - "search_store passa o produto da linha como rank só na pesquisa alargada: store.search(b, fetch, rank=item.product)"
  - "bricomarche.search(query, fetch, rank=None): pais por palavras de rank or query e depois pelo preço do pai, antes de keyed[:K]"
  - "obras360.search(..., rank=None): need = words(rank or query) antes do corte K=20"
  - "allmat.search(..., rank=None): páginas de caixa por palavras de rank or query e depois pelo preço, dentro de MAX_BOX_PAGES"
  - "words(): '×' = 'x', medidas com as partes ordenadas (troços seguidos e pares), 'x' em STOP; broadened() tira o 'x'/'×' solto"
  - "cabeçalho do ramo 'tudo escondido' começa por '1.ª pesquisa:'"
affects: [phase-03-match, verify-work-01]

actuals:
  tokens: 5100
  tasks: 3
  commits: 6
plan_head_before: 3959e7f19c245356193f4910f34f109e0cd5101c
plan_head_after: 346f8a4c5f761588f7b00644ff5a09bf6d842889

tech-stack:
  added: []
  patterns:
    - "rank: o produto da linha só ordena antes de um corte que já existia; a pesquisa enviada à loja e o número de pedidos não mudam"
    - "medidas comparadas com as partes ordenadas, simétrico entre pesquisa e título"

key-files:
  created: []
  modified:
    - src/strata/search.py
    - src/strata/stores/bricomarche.py
    - src/strata/stores/obras360.py
    - src/strata/stores/allmat.py
    - src/strata/words.py
    - tests/test_search.py
    - tests/test_obras360.py
    - tests/test_allmat.py

key-decisions:
  - "WR-17: na pesquisa alargada, o produto da linha (rank) ordena os pais da Bricomarché e da Obras 360 e as páginas de caixa da Allmat antes dos cortes K; a pesquisa enviada continua a alargada e o número de pedidos não muda"
  - "WR-14/WR-15: medidas comparadas com as partes ordenadas (troços seguidos e pares), '×' = 'x', e o 'x' solto nunca é palavra de produto (STOP e broadened)"

patterns-established:
  - "Adaptador de loja: async search(query, fetch, rank=None) -> Found; rank só entra numa chave de ordenação"

requirements-completed: [LIST-02, STORE-01, STORE-02, STORE-03, STORE-05]

coverage:
  - id: D1
    description: "Bricomarché: na alargada, 'pavimento 60x120' expande a placa 60X120 (a mais cara de 13) dentro de K=10 e mostra só essa; o resto fica contado"
    requirement: STORE-03
    verification:
      - kind: integration
        ref: "tests/test_search.py#test_alargada_expande_o_pai_com_o_produto_da_linha"
        status: pass
      - kind: unit
        ref: "tests/test_search.py#test_pesquisa_alargada_quando_a_loja_da_zero"
        status: pass
    human_judgment: false
  - id: D2
    description: "Obras 360 e Allmat: o rank põe o pai 60x120 nos 20 detalhes e a caixa 60X120 nas 10 páginas, sem pedidos a mais"
    requirement: STORE-02
    verification:
      - kind: unit
        ref: "tests/test_obras360.py#test_rank_poe_o_pai_do_produto_da_linha_a_frente_do_corte"
        status: pass
      - kind: unit
        ref: "tests/test_allmat.py#test_rank_le_primeiro_as_caixas_do_produto_da_linha"
        status: pass
    human_judgment: false
  - id: D3
    description: "WR-14/WR-15: medidas em qualquer ordem, com '×' ou espaços; a alargada nunca guarda um 'x' solto"
    requirement: LIST-02
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_title_matches"
        status: pass
      - kind: unit
        ref: "tests/test_search.py#test_broadened"
        status: pass
    human_judgment: false
  - id: D4
    description: "WR-16: o cabeçalho do ramo 'tudo escondido' diz '1.ª pesquisa:' e a linha wide_only fica igual"
    requirement: STORE-05
    verification:
      - kind: unit
        ref: "tests/test_search.py#test_tudo_escondido_com_medidas_tenta_a_alargada"
        status: pass
      - kind: unit
        ref: "tests/test_search.py#test_tudo_escondido_alargada_com_ofertas_que_batem"
        status: pass
    human_judgment: false
  - id: D5
    description: "Corrida ao vivo de 'pavimento 60x120 10 m²': a 1.ª oferta da Bricomarché é um pavimento 60X120 a 34,55 €, com link para a página da loja física"
    requirement: STORE-01
    verification:
      - kind: e2e
        ref: "printf 'pavimento 60x120 10 m²\\n\\n' | uv run python -m strata pesquisar (exit 0 no verificador do plano)"
        status: pass
    human_judgment: true
    rationale: "O preço da Bricomarché é desenhado por JavaScript e stocks e preços mudam ao vivo; só uma pessoa compara o link com o site (human-check da Tarefa 3)"

duration: 6min
completed: 2026-10-23
status: complete
---

# Phase 1 Plan 12: Produto da linha antes dos cortes K (WR-17) Summary

**Na pesquisa alargada, o produto da linha passa às três lojas como `rank` e escolhe os pais (Bricomarché, Obras 360) e as páginas de caixa (Allmat) antes dos cortes; ao vivo, "pavimento 60x120" já mostra na Bricomarché as duas placas 60X120 a 34,55 €. Junta medidas em qualquer ordem (WR-14), o "x" solto fora da alargada (WR-15) e o cabeçalho "1.ª pesquisa:" (WR-16).**

## Performance

- **Duration:** cerca de 6 min de execução (mais a leitura inicial)
- **Started:** 2026-10-23T22:54:21Z
- **Completed:** 2026-10-23T22:59:55Z
- **Tasks:** 3 de 3
- **Files modified:** 8

## Accomplishments

- WR-17 fechado nas três lojas: na alargada, a loja continua a receber a pergunta alargada ("pavimento") e o produto da linha ("pavimento 60x120") só ordena antes do corte. K = 10, K = 20 e MAX_BOX_PAGES = 10 ficam iguais, e o número de pedidos também.
- Sem rank (pesquisa direta) a ordem não muda: os pais já passaram por `title_matches(query, …)`, empatam na contagem e decide o preço. Os testes de corte antigos passam sem mudança.
- WR-14: "pavimento 120x60", "60 x 120", "30×30" e "1250x2500x12mm" batem na medida escrita pela loja; "30x30" continua sem bater em "30x60".
- WR-15: `broadened()` tira sempre o "x" ou "×" solto ("tela 1 m x 25 m" dá "tela").
- WR-16: as duas contagens do ramo "tudo escondido" dizem a que pesquisa pertencem (D-02).

## Task Commits

1. **Tarefa 1 (tracer): rank na Bricomarché, de search_store ao terminal.** RED `7a857ca` (test), GREEN `5248b64` (feat)
2. **Tarefa 2: Obras 360 e Allmat também ordenam pelo rank.** RED `896a642` (test), GREEN `3fcfb1f` (feat)
3. **Tarefa 3: WR-14, WR-15, WR-16 e a corrida ao vivo.** RED `97c8be7` (test), GREEN `346f8a4` (fix)

**Plan metadata:** commit docs a seguir a este ficheiro.

## TDD

- **RED Tarefa 1:** 2 falhas, 208 passaram. `test_pesquisa_alargada_quando_a_loja_da_zero` falhou na asserção nova (`[None, None] == [None, 'OSB 12mm']`) e o tracer falhou em `assert 0 == 1` (o pai 200 não foi expandido). Avaliação: as duas falham na asserção planeada, pelo motivo certo.
- **RED Tarefa 2:** 2 falhas, 210 passaram. Os detalhes da Obras 360 eram os 20 pais baratos, sem `id-60x120`, e as páginas da Allmat eram p1 a p10, sem `p60x120`. Motivo certo.
- **RED Tarefa 3:** 10 falhas (5 casos WR-14, 3 WR-15 e os 2 testes do cabeçalho), 69 passaram na seleção. Os guardas "tela 1m x 25m" e "tela 1 x 25 m" já passavam, como o plano previa.
- **GREEN:** 210, 212 e 222 passed, como o plano previa. `workflow.tdd_mode` está desligado, por isso não correu o classificador `tdd-red-evidence`; as falhas RED foram confirmadas à mão nas linhas `E` do pytest.

## Corrida ao vivo

Comando (uma só vez, 2026-10-23T22:59:22Z a 22:59:45Z, cerca de 23 s): `printf 'pavimento 60x120 10 m²\n\n' | uv run python -m strata pesquisar`, passado pelo verificador do plano. **Saída 0.**

**Veredicto da Bricomarché:** a 1.ª oferta é "PAVIMENTO CERÂMICO SIENA HEKLA 60X120 1.44M2" a **34,55 €** (23,99 €/m²) e a 2.ª é "Pavimento/Revestimento Cerâmico Casablanca Mate 60X120 1.44M2", também a 34,55 €. As outras 8 expandidas ficam contadas ("+8 ofertas escondidas: título sem 'pavimento 60x120'"). A Siena aparece "Esgotado" em Coina - Barreiro: nenhuma loja física tinha stock e `offer_from` mostra então a mais barata com o stock dela (RES-02). A Casablanca tem 3 em stock em São Domingos de Rana.

Allmat e Obras 360: nenhuma oferta da alargada tem "60x120" no título, por isso aparecem as da alargada, como antes.

```
Linha 1 — pavimento 60x120 (10 m²)
  Allmat: ok (pesquisa alargada: 'pavimento')
    15,85 €  STATUARIO PAVIMENTO 45X45 BRILHO 1ª
      IVA: regra da loja (páginas de produto da Allmat: IVA incluído) · 12,99 €/m² · 88 em stock · pesquisa alargada
      https://allmat.pt/produto/statuario-pavimento-45x45-brilho-1a/
    15,85 €  JAZZ PAVIMENTO 45X45 CREME AD 1ªESCOLHA
      IVA: regra da loja (páginas de produto da Allmat: IVA incluído) · 12,99 €/m² · 287 em stock · pesquisa alargada
      https://allmat.pt/produto/jazz-pavimento-45x45-creme-ad-1aescolha/
    15,85 €  BUXIEL PAVIMENTO 45X45 GREY 1ª ESCOLHA
      IVA: regra da loja (páginas de produto da Allmat: IVA incluído) · 12,99 €/m² · 350 em stock · pesquisa alargada
      https://allmat.pt/produto/buxiel-pavimento-45x45-grey-1a-escolha/
    15,85 €  BUXIEL PAVIMENTO 45X45 SILVER 1ªESCOLHA
      IVA: regra da loja (páginas de produto da Allmat: IVA incluído) · 12,99 €/m² · 612 em stock · pesquisa alargada
      https://allmat.pt/produto/buxiel-pavimento-45x45-silver-1aescolha/
    32,51 €  EXCLUSIVE PAVIMENTO FLUTUANTE 1203X191X8MM 32 AC4 CARVALHO REN
      IVA: regra da loja (páginas de produto da Allmat: IVA incluído) · 13,99 €/m² · 244 em stock · pesquisa alargada
      https://allmat.pt/produto/exclusive-pavimento-flutuante-1203x191x8mm-32-ac4-carvalho-ren/
    +19 ofertas não mostradas
  Bricomarché: ok (pesquisa alargada: 'pavimento')
    34,55 €  PAVIMENTO CERÂMICO SIENA HEKLA 60X120 1.44M2
      IVA: regra da loja (loja B2C: preço final com IVA (DL 138/90); o site não mostra o IVA) · 23,99 €/m² · Esgotado · loja: Coina - Barreiro · pesquisa alargada
      https://www.bricomarche.pt/coina-barreiro/produto/pavimento-ceramico-siena-hekla-60x120-1-44m2/
    34,55 €  Pavimento/Revestimento Cerâmico Casablanca Mate 60X120 1.44M2
      IVA: regra da loja (loja B2C: preço final com IVA (DL 138/90); o site não mostra o IVA) · 23,99 €/m² · 3 em stock · loja: São Domingos de Rana · pesquisa alargada
      https://www.bricomarche.pt/sao-domingos-de-rana/produto/pavimento-revestimento-ceramico-casablanca-mate-60x120-1-44m2/
    +8 ofertas escondidas: título sem 'pavimento 60x120'
    nota: 1 produtos sem preço
    nota: +138 produtos não expandidos (limite de 10 por pesquisa)
  Obras 360: ok (pesquisa alargada: 'pavimento')
    39,85 €  Cartão Canelado Rolo 60 M2 - 60x1M - TECpaper Embalamento Proteção Pavimento Obra Mudança — Rolo de 60M X 1M - 60 M2
      IVA: indicado pela loja (tax_percentage=23) · 0,6642 €/m² · 542 em stock · escalões: −15% a partir de 12 · escalões: −25% a partir de 36 · pesquisa alargada
      https://www.obras360.pt/0260080001-cartao-canelado-rolo-60-m2---60x1m---tecpaper-embalamento-protecao-pavimento-obra-mudanca
    16,38 €  Mosaico Cerâmico Porcelânico Belgravia Pearl Mate Esmaltado 60x60cm 1ªEscolha Retificado Pavimento — 60 x 60cm - 9,5mm - Palete n/ Incluída - Limitado ao stock
      IVA: indicado pela loja (tax_percentage=23) · 11,37 €/m² · 4 em stock · pesquisa alargada
      https://www.obras360.pt/0100140009-mosaico-ceramico-natural-cinza-claro-porcelanico-mate-esmaltado-60-x-60cm
    17,02 €  Mosaico Cerâmico Porcelânico Belgravia Grey Mate Esmaltado 60x60cm 1ªEscolha Retificado Pavimento — 60 x 60cm - 9,5mm - Palete n/ Incluída - Limitado ao stock
      IVA: indicado pela loja (tax_percentage=23) · 11,82 €/m² · 31 em stock · pesquisa alargada
      https://www.obras360.pt/0100140010-mosaico-ceramico-natural-cinza-escuro-porcelanico-mate-esmaltado-60-x-60cm
    0,22 €  Pavê Bloco Pavimento PARALELO Betão Cinza Exterior Passeio Estacionamento - 200x100x80MM - 0,02M2 — 1 Unid. - 200(C)x100(L)x80(A)mm - Palete Não Incluída - Limitado stock
      IVA: indicado pela loja (tax_percentage=23) · 0,2214 €/un · 106 em stock · pesquisa alargada · não convertível para m²: vendido em un
      https://www.obras360.pt/0100120003-pave-bloco-pavimento-paralelo-betao-cinza-exterior-passeio-estacionamento---200x100x80mm---0-02m2
    0,24 €  Pavê Bloco Pavimento Holanda Betão Cinza Exterior Passeio Estacionamento - 200x100x50mm - 0,02m2 — 200(C)x100(L)x50(A)mm - Palete Não Incluída - Limitado ao stock
      IVA: indicado pela loja (tax_percentage=23) · 0,2449 €/un · 7647 em stock · escalões: −5% a partir de 540 · pesquisa alargada · não convertível para m²: vendido em un
      https://www.obras360.pt/0100120002-pave-bloco-pavimento-paralelo-betao-cinza-exterior-passeio-estacionamento---200x100x50mm---0-02m2
    +15 ofertas não mostradas
    +47 ofertas escondidas: título sem 'pavimento'
    nota: mais produtos na loja não lidos (limite de 144)
    nota: +77 produtos não expandidos (limite de 20 por pesquisa)
```

## Files Created/Modified

- `src/strata/search.py`: a chamada da alargada passa `rank=item.product`; o cabeçalho do ramo "tudo escondido" começa por "1.ª pesquisa:"
- `src/strata/stores/bricomarche.py`: `search(query, fetch, rank=None)`; pais por palavras de `rank or query` e depois pelo preço do pai; comentário `shortcut:` de K atualizado
- `src/strata/stores/obras360.py`: `search(..., rank=None)`; `need = words(rank or query)`
- `src/strata/stores/allmat.py`: `search(..., rank=None)`; caixas por palavras de `rank or query` e depois pelo preço; comentário `shortcut:` de MAX_BOX_PAGES atualizado
- `src/strata/words.py`: `combinations`, `"×"` = `"x"`, medidas ordenadas (troços e pares), `"x"` em STOP, `broadened()` sem `"x"`/`"×"` solto
- `tests/test_search.py`: `fake_store` com `ranks`, tracer da Bricomarché, 5 casos WR-14, 5 WR-15 e os 2 cabeçalhos reescritos
- `tests/test_obras360.py`, `tests/test_allmat.py`: um teste de rank cada

## Decisions Made

Seguiu-se o plano. As duas decisões de desenho (rank só para ordenar; medidas com as partes ordenadas, incluindo pares) já vinham do plano e estão em `key-decisions`.

## Deviations from Plan

None - plan executed exactly as written.

Notas sem efeito no código:
- O commit GREEN da Tarefa 3 usa o tipo `fix` (corrige os avisos WR-14/15/16 da revisão) em vez de `feat`. Os pares RED e GREEN existem nas três tarefas.
- Uma escrita por script em `allmat.py` falhou com `OSError: [Errno 22]` (ficheiro preso por outro processo, provavelmente o antivírus). O ficheiro ficou intacto; a última edição foi refeita com a ferramenta Edit antes de correr os testes.

## Issues Encountered

None.

## Known Stubs

Nenhum.

## Verificação do plano

- `uv run python -m pytest -q`: 222 passed
- Critérios das 3 tarefas: todos PASS (greps de `rank=item.product`, `words(rank or query)` nos 3 adaptadores, assinaturas com `rank: str | None = None`, `K = 10`, `K = 20`, `MAX_BOX_PAGES = 10`, `replace("×", "x")`, `combinations(p, 2)`, `norm(t) not in ("x", "×")`, `1.ª pesquisa: {first_hidden}`)
- `git diff --quiet 701e356 -- src/strata/fetch.py src/strata/money.py src/strata/models.py src/strata/report.py pyproject.toml uv.lock`: saída 0 (limites por host, dinheiro, contrato de dados, report e dependências iguais)
- Corrida ao vivo: saída 0, 1.ª oferta da Bricomarché é um 60X120 a 34,55 €
- Fica para o `/gsd-verify-work` (human-check): abrir o link da 1.ª oferta da Bricomarché e confirmar o preço e o IVA no site

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- G-01-5 (WR-17) e os avisos WR-14, WR-15 e WR-16 estão fechados com testes; fica para re-verificar a fase (`/gsd-verify-work 01`) e para os itens humanos já listados no 01-VERIFICATION.md.
- Ao vivo, a Siena 60X120 está esgotada em todas as lojas físicas. A app mostra-a em 1.º lugar com "Esgotado", e a Casablanca, ao mesmo preço e com stock, aparece logo a seguir. Ordenar por stock em caso de empate não estava no âmbito deste plano.

---
*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Completed: 2026-10-23*

## Self-Check: PASSED
