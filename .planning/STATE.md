---
gsd_state_version: "1.0"
current_phase: 02
current_phase_name: Obramat e cadeia de recurso
status: executing
stopped_at: Completed 02-01-PLAN.md
last_updated: "2026-10-31T13:20:51.039Z"
last_activity: 2026-10-31
last_activity_desc: Phase 02 execution started
state_head: 418a56582a4b78c51e3ae80579dd31629bf28cc7
progress:
  total_phases: 6
  completed_phases: 1
  total_plans: 18
  completed_plans: 16
  percent: 17
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-30)

**Core value:** Para cada produto da lista, mostrar o custo total mais baixo real (com IVA, para a quantidade pedida) entre as lojas portuguesas, com link para comprar: igual ou mais barato do que uma pesquisa feita à mão, e em minutos em vez de horas.
**Current focus:** Phase 02 — Obramat e cadeia de recurso

## Current Position

Phase: 02 (Obramat e cadeia de recurso) — EXECUTING
Plan: 5 of 6
Status: Ready to execute
Last activity: 2026-10-31 — Phase 02 execution started

Progress: [██░░░░░░░░] 17%

## Performance Metrics

**Velocity:**
- Total plans completed: 12
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 12 | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | 4 min | 2 tasks | 14 files |
| Phase 01 P02 | 4 min | 3 tasks | 10 files |
| Phase 01 P03 | 7 min | 3 tasks | 8 files |
| Phase 01 P04 | 4 min | 2 tasks | 5 files |
| Phase 01 P05 | 5 min | 2 tasks | 9 files |
| Phase 01 P06 | 98 min | 2 tasks | 5 files |
| Phase 01 P07 | 4 min | 2 tasks | 9 files |
| Phase 01 P08 | 3 min | 2 tasks | 5 files |
| Phase 01 P09 | 3 min | 3 tasks | 5 files |
| Phase 01 P10 | 2 min | 2 tasks | 4 files |
| Phase 01 P11 | 3 min | 2 tasks | 7 files |
| Phase 01 P12 | 6 min | 3 tasks | 8 files |
| Phase 02 P01 | 5 min | 2 tasks | 12 files |

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
- [Phase 01]: selectolax fixado em >=1.0,<1.1 (aprovado pelo utilizador; resolveu para 1.0.2)
- [Phase 01]: Allmat: rótulo Unid -> 1 un; M2 ou outro rótulo -> €/unidade desconhecido com nota visível até ao 01-03
- [Phase 01]: Linha colada só com número ('30 un') dá 'linha sem descrição'
- [Phase 01]: Erros de abertura da folha (.xls, zip corrompido) com uma só mensagem: 'não consegui abrir <nome>: é .xls ou não é um .xlsx válido'
- [Phase 01]: Texto colado só com linhas inválidas: 'Nenhuma linha válida para pesquisar.' e código 2
- [Phase 01]: 01-03: pesquisa alargada a zero dá 'sem resultados' com "também sem resultados com '<b>'"; broadened_query só quando há ofertas
- [Phase 01]: 01-03: caixas M2 da Allmat começam com a nota do limite de 10 páginas; só a leitura da página a troca (nenhuma caixa sem motivo)
- [Phase 01]: 01-03: preço da página Allmat lido no formato da loja (vírgula decimal); formato diferente -> 'área da caixa não encontrada', nunca um €/m² errado
- [Phase 01]: 01-04: Bricomarché mostra a variação mais barata entre lojas físicas com o stock dela, sem filtrar; sem stock -> nota 'com stock: X em Y' (substituída pelo 01-10, G-01-3: loja mais barata com stock; a mais barata sem stock fica na nota)
- [Phase 01]: 01-04: sem stock = classe out-of-stock ou 'N em stock' com N = 0; variação master fora da escolha (shortcut)
- [Phase 01]: 01-04: variações paginadas com o mesmo limite de 3 páginas dos pais, com nota se cortar
- [Phase 01]: 01-05: Obras 360 paginada por ceil(total_products/48), no máximo 3 páginas; contar produtos lidos pedia páginas inexistentes
- [Phase 01]: 01-05: Obras 360 só passa à nota um StoreError de um produto (detalhe vazio, IVA incoerente); KeyError/TypeError põem a loja em erro
- [Phase 01]: 01-05: variante Obras 360 sem designação fica '<pai> — ref. <sku>'
- [Phase 01]: 01-06: verificar corre 4 canários (Allmat cimento e pavimento, Bricomarché cimento, Obras 360 osb) pelo search_store do dia a dia e sai com 1 se algum falhar
- [Phase 01]: 01-06: DEADLINE_S 90 s, K 10/20 e MAX_BOX_PAGES 10 mantidos; corrida ao vivo sem tempo esgotado (verificar 50 s, folha de 3 linhas 26 s)
- [Phase 01]: WR-01: com tudo escondido pelo filtro de título, o cabeçalho diz '0 ofertas mostradas; N escondidas pelo filtro de título' e D-14 tenta a pesquisa alargada uma vez (só com números/medidas); substitui a resolução n.º 2 das Open Questions do 01-RESEARCH.md
- [Phase 01]: CR-01: words() ignora palavras de ligação (STOP) e normaliza género e plurais com _stem (só biblioteca padrão)
- [Phase 01]: Obras 360: pais escolhidos com broadened(query) or query; variantes filtradas pela pesquisa completa no título pai + designação; variantes cortadas somam a hidden (CR-02)
- [Phase 01]: words(): DIMS (LxCxE), LITRE (Lt/litros = l) e CLASS (OSB3 = osb 3) antes do JOIN (CR-03)
- [Phase 01]: 01-09: _stem com tabela PLURAL; -is e -il vão para -i (perfis/Perfil, funis/Funil, táxis/Táxi batem); limite de 2 letras (pás/Pá) (CR-05)
- [Phase 01]: 01-09: Obras 360 corta K=20 primeiro pelos pais que batem na pesquisa completa, depois pelo preço; continua 20 pedidos de detalhe (CR-04)
- [Phase 01]: 01-09: loja com resultados e zero ofertas sem escondidas: estado 'ok' com detail '0 ofertas mostradas de N resultados da loja' (WR-10); UNIT_TOKENS com lts/litro/litros (IN-08)
- [Phase 01]: G-01-3: a oferta da Bricomarché é a loja física mais barata com stock; se nenhuma tiver stock, a mais barata com o stock dela; uma loja mais barata sem stock fica na nota 'mais barata sem stock: X em Y' (substitui a decisão do 01-04)
- [Phase 01]: G-01-5 (emenda D-15): na pesquisa alargada, se alguma oferta bate a pergunta completa, só essas se mostram e as outras ficam contadas em '+N ofertas escondidas: título sem '<produto>''; se nenhuma bater, mostram-se as da alargada, marcadas 'pesquisa alargada'
- [Phase 01]: WR-17: na pesquisa alargada, o produto da linha (rank) ordena os pais da Bricomarché e da Obras 360 e as páginas de caixa da Allmat antes dos cortes K; a pesquisa enviada continua a alargada e o número de pedidos não muda
- [Phase 01]: WR-14/WR-15: medidas comparadas com as partes ordenadas (troços seguidos e pares), '×' = 'x', e o 'x' solto nunca é palavra de produto (STOP e broadened)
- [Phase 02]: Obramat com LOCATION fixo OBRAMAT Lisboa - Alfragide (um só armazém); IVA conferido a 0,02 € em euros; escalões e stock exato só nas 3 primeiras ofertas (K = 3)

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2]: Escrever uma nota curta de âmbito legal antes de começar (uso pessoal, ritmo humano, sem CAPTCHA, proxies nem sessões iniciadas)
- [Phase 2]: Resistência ao DataDome da Obramat ao longo de 10 itens não testada; recurso = Chrome dedicado (`.claude-chrome`) a ritmo humano
- [Phase 1]: Bricomarché demora cerca de 12 s por página; `orderby=price` não ordena com `type=variation` (confirmado na pesquisa) — os planos usam pais → top 10 → variações. Pesa no limite de 5 min da Phase 2
- [Phase 1]: 01-VALIDATION.md ainda em draft (auditoria Nyquist por fazer: `/gsd-validate-phase 1`)
- [Phase 1]: lista m² da coluna Unidade no Excel por testar (sem Excel na máquina; follow-up no 01-UAT.md)
- [Phase 3]: produto vs menção ("cola para OSB" com todas as palavras no título), gamas no nome do pai ("9-30MM") e Tamanho em unidades diferentes ficam para a classificação exato/parecido
- [Phase 5]: Correr o `ui-ux-pro-max` (design system com `--persist`) antes do primeiro ecrã

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 261023-lee | Corrigir avisos CR-06, WR-12, WR-13 e WR-07 do filtro de título | 2026-10-23 | 9511c81 | [261023-lee-corrigir-avisos-cr-06-wr-12-wr-13-wr-07-](./quick/261023-lee-corrigir-avisos-cr-06-wr-12-wr-13-wr-07-/) |

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-10-31T12:46:00.399Z
Stopped at: Completed 02-01-PLAN.md
Resume file: None
