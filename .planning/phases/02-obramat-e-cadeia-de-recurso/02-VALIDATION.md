---
phase: "2"
slug: "obramat-e-cadeia-de-recurso"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-31"
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options] testpaths = ["tests"]`) |
| **Quick run command** | `uv run pytest -q -x` |
| **Full suite command** | `uv run pytest -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest -q -x`
- **After every plan wave:** Run `uv run pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green, `uv run python -m strata verificar` OK for the 4 stores, and a timed live 10-item run
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 2-xx | tbd | tbd | STORE-04 | — | Obramat main list only (no carousel/endcap), VAT check, tiers | unit | `uv run pytest tests/test_obramat.py -q` | ❌ W0 | ⬜ pending |
| 2-xx | tbd | tbd | STORE-04 / STORE-06 | — | CAPTCHA → "abrir à mão" with link; no further Obramat requests; fallback order and `method` per offer | unit | `uv run pytest tests/test_chain.py -q` | ❌ W0 | ⬜ pending |
| 2-xx | tbd | tbd | STORE-06 | — | AI step: ≤5 offers, price must appear in page text, URL on store host, "lido por IA" | unit | `uv run pytest tests/test_ai.py -q` | ❌ W0 | ⬜ pending |
| 2-xx | tbd | tbd | STORE-06 | — | JSON-LD step: Allmat product page parsed; JS-built pages fail with visible reason | unit | `uv run pytest tests/test_jsonld.py -q` | ❌ W0 | ⬜ pending |
| 2-xx | tbd | tbd | STORE-07 | — | `verificar` covers 4 stores | unit | `uv run pytest tests/test_search.py -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/obramat_*.html` — copied from `.planning/phases/02-obramat-e-cadeia-de-recurso/samples/`
- [ ] `tests/test_obramat.py`, `tests/test_chain.py`, `tests/test_ai.py`, `tests/test_jsonld.py`
- [ ] An Allmat product page fixture with intact `ld+json`
- [ ] `uv add playwright anthropic` (human checkpoint)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 10-item sheet resolved in 4 stores in < 5 min, each item shows the 4 store states | LIST-03 | Needs network and the dedicated Chrome | `uv run python -m strata pesquisar <sheet of 10>` timed |
| `claude -p` AI engine authenticates with the user's Pro login | STORE-06 | Auth lives in the user's terminal | `echo teste \| claude -p --model haiku --output-format json` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
