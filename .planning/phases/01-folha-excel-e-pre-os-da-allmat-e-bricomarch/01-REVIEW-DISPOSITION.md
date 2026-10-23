---
phase: 01
review: 01-REVIEW.md
titles: json
findings:
  - id: CR-04
    severity: critical
    disposition: fixed
    title: "Obras 360 escolhe os pais sem os números e o corte K=20 por preço deita fora o produto pedido — CORRIGIDO no caso citado (resto no CR-06)"
  - id: CR-05
    severity: critical
    disposition: fixed
    title: "`_stem` não tratava os plurais -ais, -is, -ens, -óis nem palavras de 3 letras — CORRIGIDO nos casos citados (resto no WR-12)"
  - id: CR-06
    severity: critical
    disposition: open
    title: "A correção do CR-04 falha quando a pesquisa junta o código do pai e a medida da variante: \"parafuso m8x40\" volta a esconder o M8 (novo, 01-09)"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`content_from_title` lê o primeiro número com unidade, por isso packs e especificações dão €/kg e €/L errados — ABERTO"
  - id: WR-03
    severity: warning
    disposition: open
    title: "\"1.000\" (mil, à portuguesa) é lido como quantidade 1 — ABERTO"
  - id: WR-04
    severity: warning
    disposition: open
    title: "Allmat cai inteira com `InvalidOperation` se um produto vier com `price: \"\"` — ABERTO"
  - id: WR-05
    severity: warning
    disposition: open
    title: "Uma página de caixa bloqueada deita fora todas as ofertas da Allmat — ABERTO"
  - id: WR-06
    severity: warning
    disposition: open
    title: "Obras 360 usa `total_products` como `raw`: se o campo faltar, os produtos lidos passam a \"sem resultados\" — ABERTO"
  - id: WR-07
    severity: warning
    disposition: open
    title: "DIMS parte \"30x30\" em dois \"30\" iguais: \"azulejo 30x30\" bate em \"30x60\" — ABERTO, adiado para a Phase 3"
  - id: WR-08
    severity: warning
    disposition: open
    title: "O género junta produtos diferentes: barra/barro, banco/banca, tampo/tampa, lixa/lixo — ABERTO, adiado para a Phase 3"
  - id: WR-09
    severity: warning
    disposition: open
    title: "Número sem unidade na pesquisa nunca bate num número com unidade no título — ABERTO"
  - id: WR-11
    severity: warning
    disposition: open
    title: "Uma gama no nome do pai (\"9-30MM\") faz \"osb 30mm\" mostrar as 7 espessuras, com a de 9 mm em 1.º — ABERTO, adiado para a Phase 3"
  - id: WR-12
    severity: warning
    disposition: open
    title: "Plurais que a tabela `PLURAL` não cobre: geotêxteis, coxins, jardins (resto do CR-05, novo no 01-09)"
  - id: WR-13
    severity: warning
    disposition: open
    title: "Unidades por extenso além de litros (\"metros\", \"quilos\", \"unidades\") escondem o produto mesmo depois da alargada (resto do IN-08, novo no 01-09)"
  - id: IN-01
    severity: info
    disposition: open
    title: "Texto colado \"Tinta branca 15L\" ou \"Tubo 3m\" perde a medida sem aviso — ABERTO"
  - id: IN-02
    severity: info
    disposition: open
    title: "`broadened` deita fora tokens com hífen inteiros — ABERTO"
  - id: IN-03
    severity: info
    disposition: open
    title: "Fórmulas sem valor guardado aparecem como \"Qty vazia\" — ABERTO"
  - id: IN-04
    severity: info
    disposition: open
    title: "`write_template` deixa um ficheiro parcial se a gravação falhar — ABERTO"
  - id: IN-05
    severity: info
    disposition: open
    title: "HTTP 503 é sempre classificado como \"bloqueada\" — ABERTO"
  - id: IN-06
    severity: info
    disposition: open
    title: "Dois `CONTENT_UNITS` com significados diferentes — ABERTO"
  - id: IN-07
    severity: info
    disposition: open
    title: "\"12,0 mm\" não bate em \"12mm\" (resto do CR-03, adiado pelo 01-08) — ABERTO"
  - id: IN-08
    severity: info
    disposition: fixed
    title: "`broadened` não conhecia os sinónimos do LITRE: \"tinta 15 litros\" alargava para \"tinta litros\" — CORRIGIDO (resto no WR-13)"
  - id: IN-09
    severity: info
    disposition: open
    title: "A alargada deita fora as notas da 1.ª pesquisa e, na Obras 360, pede os mesmos detalhes duas vezes — ABERTO"
  - id: IN-10
    severity: info
    disposition: open
    title: "Assimetrias de tokenização: \"ip65\"/\"IP 65\", \"e27\"/\"E 27\", unidade solta depois de decimal — ABERTO"
  - id: IN-11
    severity: info
    disposition: open
    title: "A tabela `PLURAL` e o limite de 2 letras trazem colisões novas: cais/cal, mais/mal, dois/dol, abs/ab, eps/ep (novo, 01-09)"
  - id: IN-12
    severity: info
    disposition: open
    title: "Obras 360 diz \"0 ofertas mostradas de N resultados da loja\" sem nota quando a lista vem vazia com `total_products > 0` (novo, 01-09)"
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "O filtro de título ignora o género e as palavras de ligação — CORRIGIDO"
  - id: CR-02
    severity: critical
    disposition: fixed
    title: "Obras 360 filtrava pelo nome do pai, e a medida está na variante — CORRIGIDO"
  - id: CR-03
    severity: critical
    disposition: fixed
    title: "Medidas coladas por \"x\", sinónimos de unidade e sufixos de classe — CORRIGIDO (resto no IN-07)"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Estado \"ok\" com zero ofertas mostradas, e sem nova tentativa — CORRIGIDO (resto no WR-10)"
  - id: WR-10
    severity: warning
    disposition: fixed
    title: "\"ok\" sozinho com zero ofertas quando nada foi escondido pelo filtro (resto do WR-01)"
open: 27
total: 31
recorded: 2026-10-23T11:42:57.017Z
---

# Phase 01: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-04 | critical | fixed | 01-09, re-review (casos citados) |
| CR-05 | critical | fixed | 01-09, re-review (casos citados) |
| CR-06 | critical | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| WR-07 | warning | open | - |
| WR-08 | warning | open | - |
| WR-09 | warning | open | - |
| WR-11 | warning | open | - |
| WR-12 | warning | open | - |
| WR-13 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | fixed | 01-09, re-review (casos citados) |
| IN-09 | info | open | - |
| IN-10 | info | open | - |
| IN-11 | info | open | - |
| IN-12 | info | open | - |
| CR-01 | critical | fixed | 01-07/01-08, re-review cc4fb5c (not in the current review) |
| CR-02 | critical | fixed | 01-07/01-08, re-review cc4fb5c (not in the current review) |
| CR-03 | critical | fixed | 01-07/01-08, re-review cc4fb5c (not in the current review) |
| WR-01 | warning | fixed | 01-07/01-08, re-review cc4fb5c (not in the current review) |
| WR-10 | warning | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
