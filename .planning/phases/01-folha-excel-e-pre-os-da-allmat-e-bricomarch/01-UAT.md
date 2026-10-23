---
status: testing
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
source: [01-VERIFICATION.md]
started: 2026-10-23T14:08:58Z
updated: 2026-10-23T14:08:58Z
---

## Current Test

number: 1
name: Lista "m²" da coluna Unidade no Excel
expected: |
  `uv run python -m strata modelo`, abrir no Excel, clicar na coluna Unidade e escrever 'caixa':
  lista un, m², m, kg, L, saco com o '²' certo e o aviso 'Escolha da lista: …'
awaiting: user response

## Tests

### 1. Lista "m²" da coluna Unidade no Excel
expected: `uv run python -m strata modelo`, abrir no Excel, clicar na coluna Unidade e escrever 'caixa': lista un, m², m, kg, L, saco com o '²' certo e o aviso 'Escolha da lista: …'
result: [pending]

### 2. Colar texto numa consola normal do Windows
expected: `uv run python -m strata pesquisar` numa consola normal, colar 'azulejo 2,5 m²' e Enter duas vezes: "Linha 1 — azulejo (2,5 m²)"
result: [pending]

### 3. Link da Bricomarché (Coina - Barreiro)
expected: o link da 1.ª oferta de OSB abre a página do produto nessa loja, com 14,49 € (placa 9 mm) ou 18,49 € (PLACA OSB 12 MM), e o preço tem IVA incluído (A9)
result: [pending]

### 4. Variante de 12 mm da Obras 360
expected: o link da variante '1 Placa 12 MM' mostra 19,37 € com IVA (15,75 € sem IVA)
result: [pending]

### 5. Folha de 3 linhas comparada com os sites
expected: folha com OSB 12 mm / un / 30; cimento cola / saco / 10; tinta branca / L / 15 e `pesquisar modelo.xlsx`: os preços batem com os dos sites e nenhuma loja diz 'ok' sem ofertas sem a frase da contagem (D5 do 01-08-SUMMARY)
result: [pending]

### 6. "perfis" contra o site da Obras 360
expected: `printf "perfis 10 un\n\n" | uv run python -m strata pesquisar`: os perfis mais baratos do site estão entre as ofertas mostradas (ao vivo pelo verificador: 'Obras 360: ok', 1,45 € Perfil Cantoneira L, +33 escondidas, +77 pais não expandidos) (D6 do 01-09-SUMMARY)
result: [pending]

### 7. O .xlsx do utilizador não muda
expected: SHA1 do .xlsx igual antes e depois de `pesquisar`
result: [pending]

### 8. Proibições de nível judgment
expected: em src/strata/fetch.py e nos SUMMARY do 01-07/01-09, sem retentativas, proxies nem troca de identidade (veredicto não autoritativo do verificador: cumpridas)
result: [pending]

## Summary

total: 8
passed: 0
issues: 0
pending: 8
skipped: 0
blocked: 0

## Gaps
