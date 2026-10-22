---
gsd_state_version: "1.0"
current_phase: 1
current_phase_name: Folha Excel e preços da Allmat, Bricomarché e Obras 360
status: executing
stopped_at: Phase 1 context gathered
last_updated: "2026-10-22T22:27:30.898Z"
last_activity: 2026-10-22
last_activity_desc: "Roadmap revisto: folha Excel como entrada principal (6 fases, 36/36 requisitos mapeados)"
state_head: 87e41fa2411a2d9bcab1000243c49cc618da3bdb
progress:
  total_phases: 6
  completed_phases: 0
  total_plans: 6
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-22)

**Core value:** Para cada produto da lista, mostrar o custo total mais baixo real (com IVA, para a quantidade pedida) entre as lojas portuguesas, com link para comprar: igual ou mais barato do que uma pesquisa feita à mão, e em minutos em vez de horas.
**Current focus:** Phase 1 — Folha Excel e preços da Allmat, Bricomarché e Obras 360

## Current Position

Phase: 1 (Folha Excel e preços da Allmat, Bricomarché e Obras 360) — READY TO EXECUTE
Plan: 0 of TBD in current phase
Status: Ready to execute
Last activity: 2026-10-22 — Roadmap revisto: folha Excel como entrada principal (6 fases, 36/36 requisitos mapeados)

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Obramat pela pesquisa direta `/search?q=`, um pedido de cada vez (C1, opção A)
- [Init]: Bricomarché = preço mais barato entre todas as lojas físicas, com o nome da loja
- [Init]: Claude Haiku 5.5 para extração e classificação na v1; Jev só no teste comparativo (MATCH-06, Phase 3)
- [Roadmap]: Linha de comandos nas Phases 1–4; a app NiceGUI chega na Phase 5
- [Roadmap]: O degrau IA da cadeia de recurso fica na Phase 2 (STORE-06); o PDF fica com o Excel na Phase 5
- [Revisão]: Folha Excel de formato fixo é a entrada principal desde a Phase 1 (LIST-04, LIST-05); o texto colado fica como pesquisa rápida (LIST-01)
- [Revisão]: Família/Tamanho/Referência como contexto na Phase 3 (LIST-06); folha original preenchida na Phase 4 (RES-08), sempre numa cópia; Excel detalhado continua na Phase 5 (RES-06)
- [Revisão]: openpyxl entra na Phase 1 para ler a folha e na Phase 4 para escrever na do utilizador (o XlsxWriter só escreve ficheiros novos); o STACK.md ainda diz só XlsxWriter
- [Phase 1]: Obras 360 (STORE-03) passou da Phase 2 para a Phase 1, a pedido do utilizador (D-16)
- [Phase 1 plan]: O utilizador aceitou o aviso do verificador sobre o 01-01 (14 ficheiros, zona de aviso 10–14): é o custo do tracer ponta a ponta; 4 dos ficheiros são gerados pelo uv ou vazios

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2]: Escrever uma nota curta de âmbito legal antes de começar (uso pessoal, ritmo humano, sem CAPTCHA, proxies nem sessões iniciadas)
- [Phase 2]: Resistência ao DataDome da Obramat ao longo de 10 itens não testada; recurso = Chrome dedicado (`.claude-chrome`) a ritmo humano
- [Phase 1]: Bricomarché demora cerca de 12 s por página; `orderby=price` não ordena com `type=variation` (confirmado na pesquisa) — os planos usam pais → top 10 → variações
- [Phase 5]: Correr o `ui-ux-pro-max` (design system com `--persist`) antes do primeiro ecrã

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-10-22T18:36:35.931Z
Stopped at: Phase 1 context gathered
Resume file: .planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-CONTEXT.md
