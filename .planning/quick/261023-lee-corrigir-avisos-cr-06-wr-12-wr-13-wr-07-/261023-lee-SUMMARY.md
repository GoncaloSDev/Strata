---
phase: quick-261023-lee
plan: 01
subsystem: filtro de título e Obras 360
tags: [words, obras360, title_matches, broadened, regex]
status: complete

requires:
  - phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
    provides: words.py (D-14, D-15) e obras360.search com o corte K=20 (01-09, CR-04)
provides:
  - "Corte K=20 da Obras 360 pelos pais com mais palavras da pesquisa, depois pelo preço (CR-06)"
  - "Plurais -xteis e regra -m/-n no _stem (WR-12)"
  - "Unidades por extenso no filtro e na alargada (WR-13)"
  - "Medida AxB/AxBxC da pesquisa tem de estar seguida no título (WR-07)"
affects: [01-REVIEW.md, 01-VERIFICATION.md, phase 3 (exato/parecido)]

actuals:
  tokens: 2434
  tasks: 3
  commits: 6
plan_head_before: 9262daa1a9d910542582988ccec5e4fc4397c412
plan_head_after: 9511c8181697eef1cb8cbf1aaa6f7dc175ff4ffa

tech-stack:
  added: []
  patterns: ["medidas guardadas partidas e também inteiras (cada troço seguido)"]

key-files:
  created: []
  modified:
    - src/strata/stores/obras360.py
    - src/strata/words.py
    - tests/test_obras360.py
    - tests/test_search.py

key-decisions:
  - "Regra única -m final = -n (antes da linha do género) em vez dos pares -ins/-ons/-uns: não parte plafons/Plafon"
  - "-eis átono só em -xteis: -teis partia listéis/Listel"
  - "broadened tira uma unidade só a seguir a um token com número: 'metro articulado 2m' fica 'metro articulado'"
  - "SIZE com lookbehind [a-z\\d.,] (o plano tinha só [a-z]): 'm12x40' não lê '2x40'"

metrics:
  duration: 12min
  completed: 2026-10-23
---

# Quick 261023-lee: CR-06, WR-12, WR-13 e WR-07 no filtro de título

O corte K=20 da Obras 360 passa a ordenar os pais pelo número de palavras da pesquisa no nome antes do preço. O `words.py` passa a juntar geotêxteis/coxins/jardins ao singular, lê "3 metros"/"25 quilos" como unidade e só aceita uma medida AxB da pesquisa se estiver seguida no título.

## Contagem de testes por tarefa

| Tarefa | RED | GREEN | Suite |
|---|---|---|---|
| 1 (CR-06, tracer) | 1 falha (40d6271) | 72a284b | 178 passed |
| 2 (WR-12, WR-13) | 10 falhas (271c765) | 58ffd5b | 193 passed |
| 3 (WR-07) | 2 falhas (83c836f) | 9511c81 | 201 passed |

A suite fecha com 201 em vez dos 200 do plano: um caso extra na Tarefa 3 (ver Desvios). `pyproject.toml` e `uv.lock` sem mudanças (`git diff --quiet 9262daa` sai com 0). O aviso de pytest ("1 warning") já existia em HEAD.

## Desvios em relação aos fixes sugeridos no 01-REVIEW.md

Todos decididos no plano, com a guarda que os prova:

1. **WR-12, regra -m/-n em vez de três pares** (-ins/-ons/-uns). Guarda: `("plafons", "Plafon LED", True)`; o par -ens saiu da tabela e `("ferragens", "Ferragem", True)` continua verde.
2. **WR-12, só "-xteis"** em vez de "-teis". Guarda: `("listéis", "Listel", True)`, mais pincéis/Pincel e papéis/Papel.
3. **WR-13, unidade só a seguir a um número** na alargada. Guarda: `("metro articulado 2m", "metro articulado")`.
4. **WR-07, troços seguidos e letra antes do número.** Guardas: `("tubo 20x20", "Tubo Quadrado 20x20x1,5", True)` e `("parafuso m8x40", "Parafuso Sextavado M8 — 40", True)`.

### Auto-corrigido durante a execução

**1. [Rule 1 - Bug] Rosca de 2 dígitos lida como medida**
- **Encontrado na:** Tarefa 3
- **Problema:** com a lookbehind do plano, `(?<![a-z])`, "m12x40" lia a medida "2x40" (o "2" vem depois de um dígito, não de uma letra). "parafuso m12x40" deixava de bater em "Parafuso Sextavado M12 — 40".
- **Correção:** lookbehind `(?<![a-z\d.,])`, mais o caso `("parafuso m12x40", "Parafuso Sextavado M12 — 40", True)`. Confirmado: com a regex do plano o caso dá False, com a corrigida dá True.
- **Ficheiros:** src/strata/words.py, tests/test_search.py
- **Commit:** 9511c81

## Limitações conhecidas

- O CR-06 ao vivo depende das designações da Obras 360. Com "M8x40" ou "40" na variante, as ofertas M8 aparecem. Com "40 MM", o WR-09 esconde-as e a alargada "parafuso" corre; aí todos os pais empatam com 1 palavra e o corte volta a ser pelo preço. Fecha-se com o WR-09.
- A regra -m/-n junta palavras como "fim"/"fino". O título fica à vista (família do WR-08).
- O -eis átono fora de "-xteis" continua sem bater (fáceis/Fácil, úteis/Útil, frágeis/Frágil). Não são nomes de produto comuns.
- `("parafuso 4x40", "Parafuso 4x40mm")` continua False por causa do WR-09 (fora do âmbito).

## Nota para a próxima re-revisão

O WR-07 sai do `deferred:` da Phase 3 no caso de uma medida AxB/AxBxC na pesquisa. A próxima re-revisão deve atualizar o 01-REVIEW.md e o 01-VERIFICATION.md (não mexidos aqui). CR-06, WR-12 e WR-13 também ficam corrigidos.

## Threat Flags

Nenhuma superfície nova: só funções puras de texto e a ordem dos pais antes do corte. Continuam no máximo 20 pedidos de detalhe (o teste do CR-06 exige exatamente 20).

## Self-Check: PASSED

- Ficheiros: src/strata/stores/obras360.py, src/strata/words.py, tests/test_obras360.py, tests/test_search.py existem
- Commits 40d6271, 72a284b, 271c765, 58ffd5b, 83c836f, 9511c81 estão em HEAD
