---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-10-22T23:55:25.339Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 01 | stub | src/strata/stores/allmat.py | 33 | Allmat rótulo M2: área da caixa não lida, €/m² desconhecido (resolve 01-03 tarefa 3, STORE-02) | open |  | 2026-10-22T23:55:25.339Z |  |

````json
[
  {
    "id": 1,
    "kind": "stub",
    "phase": "01",
    "file": "src/strata/stores/allmat.py",
    "line": 33,
    "description": "Allmat rótulo M2: área da caixa não lida, €/m² desconhecido (resolve 01-03 tarefa 3, STORE-02)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-10-22T23:55:25.339Z",
    "resolved_at": null,
    "milestone": null
  }
]
````
