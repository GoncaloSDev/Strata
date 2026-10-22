---
phase: "1"
slug: "folha-excel-e-pre-os-da-allmat-e-bricomarch"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-22"
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | none — Wave 0 adds `[tool.pytest.ini_options] testpaths = ["tests"]` to `pyproject.toml` |
| **Quick run command** | `uv run pytest -q -x` |
| **Full suite command** | `uv run pytest -q` (plus `uv run python -m strata verificar` as the live network canary) |
| **Estimated runtime** | ~10 seconds (no network: fixtures + `FakeFetcher`, network blocked by an autouse fixture) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -q -x`
- **After every plan wave:** Run `uv run pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green and `uv run python -m strata verificar` reports the three stores OK
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

Task IDs are assigned by the planner; each requirement below must map to at least one task whose `<automated>` verify runs the listed command.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-02-T2 | 01-02 | 2 | LIST-01 | — | N/A | unit | `uv run pytest tests/test_text.py -q` | ❌ W0 | ⬜ pending |
| 01-03-T1 | 01-03 | 2 | LIST-02 | — | N/A | unit | `uv run pytest tests/test_search.py -q` | ❌ W0 | ⬜ pending |
| 01-01-T3 | 01-01 | 1 | LIST-04 | T-01-03 | template never overwritten (`open(path, "xb")`) | unit | `uv run pytest tests/test_sheet.py -k modelo -q` | ❌ W0 | ⬜ pending |
| 01-02-T1 | 01-02 | 2 | LIST-05 | T-01-10 | malformed sheet rows flagged, never crash | unit | `uv run pytest tests/test_sheet.py -q` | ❌ W0 | ⬜ pending |
| 01-04-T1/T2 | 01-04 | 3 | STORE-01 | T-01-19 | N/A | unit | `uv run pytest tests/test_bricomarche.py -q` | ❌ W0 | ⬜ pending |
| 01-03-T3 | 01-03 | 2 | STORE-02 | T-01-14 | N/A | unit | `uv run pytest tests/test_allmat.py -q` | ❌ W0 | ⬜ pending |
| 01-05-T1/T2 | 01-05 | 4 | STORE-03 | T-01-23 | N/A | unit | `uv run pytest tests/test_obras360.py -q` | ❌ W0 | ⬜ pending |
| 01-03-T1 | 01-03 | 2 | STORE-05 | T-01-18 | failures surfaced as a status, never omitted | unit | `uv run pytest tests/test_search.py -q` | ❌ W0 | ⬜ pending |
| 01-06-T1 | 01-06 | 5 | STORE-07 | T-01-28 | N/A | unit + live | `uv run pytest tests/test_search.py -k verificar -q` | ❌ W0 | ⬜ pending |
| 01-05-T1 | 01-05 | 4 | PRICE-01 | T-01-23 | money as `Decimal`, never float | unit | `uv run pytest tests/test_money.py -q` | ❌ W0 | ⬜ pending |
| 01-03-T2 | 01-03 | 2 | PRICE-02 | T-01-17 | N/A | unit | `uv run pytest tests/test_money.py -q` | ❌ W0 | ⬜ pending |
| 01-04-T1 | 01-04 | 3 | RES-02 | T-01-19 | N/A | unit | `uv run pytest tests/test_obras360.py tests/test_bricomarche.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pyproject.toml` (`uv init --package`) + deps (curl_cffi, openpyxl, selectolax `>=1.0,<1.1`, pytest) + `[tool.pytest.ini_options]`
- [ ] `tests/conftest.py` — `FakeFetcher` (same `get`/`get_json` interface, reads `tests/fixtures/`) and autouse network block
- [ ] `tests/fixtures/` — seeded from `.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/samples/`, later from `--record`
- [ ] `tests/test_text.py`, `test_sheet.py`, `test_money.py`, `test_allmat.py`, `test_bricomarche.py`, `test_obras360.py`, `test_search.py`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Unidade dropdown shows "m²" correctly in Excel | LIST-04 | Excel is not installed on this machine | Run `uv run python -m strata modelo`, open `modelo.xlsx` in Excel, click a Unidade cell |
| Live prices from the three stores | STORE-01, STORE-02, STORE-03 | Needs network and the real sites | Run `uv run python -m strata verificar`; all three adapters report OK |
| End-to-end run with a filled sheet | LIST-05, STORE-05 | Real user flow | Fill `modelo.xlsx` with 3 lines, run the search command on it, check every item shows the three store statuses |
| Bricomarché prices include VAT (A9) | PRICE-01 | No VAT label on the site | Compare one product price with a physical store or receipt |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
