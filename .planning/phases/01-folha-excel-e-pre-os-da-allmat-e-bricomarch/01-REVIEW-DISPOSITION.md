---
phase: 01
review: 01-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "O filtro de título ignora o género e as palavras de ligação: a loja diz \"ok\" e esconde tudo (problema conhecido, confirmado)"
  - id: CR-02
    severity: critical
    disposition: open
    title: "Obras 360 filtra pelo nome do pai e a medida está na variante: \"OSB 12 mm\" (a linha de exemplo do modelo) mostra zero ofertas"
  - id: CR-03
    severity: critical
    disposition: open
    title: "Medidas coladas por \"x\", sinónimos de unidade e sufixos de modelo nunca batem no filtro"
  - id: WR-01
    severity: warning
    disposition: open
    title: "Estado \"ok\" com zero ofertas mostradas, e sem nova tentativa"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`content_from_title` lê o primeiro número com unidade, por isso packs e especificações dão €/kg e €/L errados"
  - id: WR-03
    severity: warning
    disposition: open
    title: "\"1.000\" (mil, à portuguesa) é lido como quantidade 1"
  - id: WR-04
    severity: warning
    disposition: open
    title: "Allmat cai inteira com `InvalidOperation` se um produto vier com `price: \"\"`"
  - id: WR-05
    severity: warning
    disposition: open
    title: "Uma página de caixa bloqueada deita fora todas as ofertas da Allmat"
  - id: WR-06
    severity: warning
    disposition: open
    title: "Obras 360 usa `total_products` como `raw`: se o campo faltar, os produtos lidos passam a \"sem resultados\""
  - id: IN-01
    severity: info
    disposition: open
    title: "Texto colado \"Tinta branca 15L\" ou \"Tubo 3m\" perde a medida sem aviso"
  - id: IN-02
    severity: info
    disposition: open
    title: "`broadened` deita fora tokens com hífen inteiros"
  - id: IN-03
    severity: info
    disposition: open
    title: "Fórmulas sem valor guardado aparecem como \"Qty vazia\""
  - id: IN-04
    severity: info
    disposition: open
    title: "`write_template` deixa um ficheiro parcial se a gravação falhar"
  - id: IN-05
    severity: info
    disposition: open
    title: "HTTP 503 é sempre classificado como \"bloqueada\""
  - id: IN-06
    severity: info
    disposition: open
    title: "Dois `CONTENT_UNITS` com significados diferentes"
open: 15
total: 15
recorded: 2026-10-23T02:19:02.859Z
---

# Phase 01: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | open | - |
| CR-02 | critical | open | - |
| CR-03 | critical | open | - |
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| WR-06 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
