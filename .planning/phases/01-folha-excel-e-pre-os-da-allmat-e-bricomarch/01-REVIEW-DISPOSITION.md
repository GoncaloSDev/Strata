---
phase: 01
review: 01-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "O filtro de título ignora o género e as palavras de ligação — CORRIGIDO"
  - id: CR-02
    severity: critical
    disposition: open
    title: "Obras 360 filtrava pelo nome do pai, e a medida está na variante — CORRIGIDO"
  - id: CR-03
    severity: critical
    disposition: open
    title: "Medidas coladas por \"x\", sinónimos de unidade e sufixos de classe — CORRIGIDO (resto no IN-07)"
  - id: CR-04
    severity: critical
    disposition: open
    title: "Obras 360 escolhe os pais sem os números e o corte K=20 por preço deita fora o produto pedido (regressão do 01-08)"
  - id: CR-05
    severity: critical
    disposition: open
    title: "`_stem` não trata os plurais -ais, -is, -ens, -óis nem palavras de 3 letras: o produto fica escondido (resto do CR-01)"
  - id: WR-01
    severity: warning
    disposition: open
    title: "Estado \"ok\" com zero ofertas mostradas, e sem nova tentativa — CORRIGIDO (resto no WR-10)"
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
    title: "DIMS parte \"30x30\" em dois \"30\" iguais: \"azulejo 30x30\" bate em \"30x60\" (novo, 01-08)"
  - id: WR-08
    severity: warning
    disposition: open
    title: "O género junta produtos diferentes: barra/barro, banco/banca, tampo/tampa, lixa/lixo (novo, 01-07)"
  - id: WR-09
    severity: warning
    disposition: open
    title: "Número sem unidade na pesquisa nunca bate num número com unidade no título"
  - id: WR-10
    severity: warning
    disposition: open
    title: "\"ok\" sozinho com zero ofertas quando nada foi escondido pelo filtro (resto do WR-01)"
  - id: WR-11
    severity: warning
    disposition: open
    title: "Uma gama no nome do pai (\"9-30MM\") faz \"osb 30mm\" mostrar as 7 espessuras, com a de 9 mm em 1.º"
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
    title: "\"12,0 mm\" não bate em \"12mm\" (resto do CR-03, adiado pelo 01-08)"
  - id: IN-08
    severity: info
    disposition: open
    title: "`broadened` não conhece os sinónimos novos do LITRE: \"tinta 15 litros\" alarga para \"tinta litros\""
  - id: IN-09
    severity: info
    disposition: open
    title: "A alargada deita fora as notas da 1.ª pesquisa e, na Obras 360, pede os mesmos detalhes duas vezes"
  - id: IN-10
    severity: info
    disposition: open
    title: "Assimetrias de tokenização: \"ip65\"/\"IP 65\", \"e27\"/\"E 27\", unidade solta depois de decimal"
open: 26
total: 26
recorded: 2026-10-23T10:57:53.469Z
---

# Phase 01: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | open | - |
| CR-02 | critical | open | - |
| CR-03 | critical | open | - |
| CR-04 | critical | open | - |
| CR-05 | critical | open | - |
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| WR-07 | warning | open | - |
| WR-08 | warning | open | - |
| WR-09 | warning | open | - |
| WR-10 | warning | open | - |
| WR-11 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |
| IN-09 | info | open | - |
| IN-10 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
