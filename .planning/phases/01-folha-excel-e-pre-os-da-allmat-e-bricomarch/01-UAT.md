---
status: complete
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
source: [01-VERIFICATION.md]
started: 2026-10-23T14:08:58Z
updated: 2026-10-23T18:24:01.016Z
---

## Current Test

[testing complete]

## Tests

### 1. Lista "m²" da coluna Unidade no Excel
expected: `uv run python -m strata modelo`, abrir no Excel, clicar na coluna Unidade e escrever 'caixa': lista un, m², m, kg, L, saco com o '²' certo e o aviso 'Escolha da lista: …'
result: skipped
reason: "não tenho Excel nesta máquina"

### 2. Colar texto numa consola normal do Windows
expected: `uv run python -m strata pesquisar` numa consola normal, colar 'azulejo 2,5 m²' e Enter duas vezes: "Linha 1 — azulejo (2,5 m²)"
result: pass

### 3. Link da Bricomarché (Coina - Barreiro)
expected: o link da 1.ª oferta de OSB abre a página do produto nessa loja, com 14,49 € (placa 9 mm) ou 18,49 € (PLACA OSB 12 MM), e o preço tem IVA incluído (A9)
result: issue
reported: "A oferta principal da Bricomarché não devia ser uma loja com 0 em stock: devia mostrar primeiro a mais barata que tem stock (15,49 € em Ponte de Sor)"
severity: major

### 4. Variante de 12 mm da Obras 360
expected: o link da variante '1 Placa 12 MM' mostra 19,37 € com IVA (15,75 € sem IVA)
result: pass

### 5. Folha de 3 linhas comparada com os sites
expected: folha com OSB 12 mm / un / 30; cimento cola / saco / 10; tinta branca / L / 15 e `pesquisar modelo.xlsx`: os preços batem com os dos sites e nenhuma loja diz 'ok' sem ofertas sem a frase da contagem (D5 do 01-08-SUMMARY)
result: issue
reported: "Confirmo os preços, mas admito que o facto da cola aparecer antes da placa de 12mm é um problema, o objetivo desta aplicação é encontrar o que eu procuro e com o preço mais barato se procurar algo e aparecer outra coisa a aplicaão nao esta a cumprir o proposito, arranja isto para garantir que a aplicação cumpri o objetivo, o metodo como fara isto deixo a sua decisão, mas talvez fazer uma filtragem no fim possa ser uma solução nao sei."
severity: major

### 6. "perfis" contra o site da Obras 360
expected: `printf "perfis 10 un\n\n" | uv run python -m strata pesquisar`: os perfis mais baratos do site estão entre as ofertas mostradas (ao vivo pelo verificador: 'Obras 360: ok', 1,45 € Perfil Cantoneira L, +33 escondidas, +77 pais não expandidos) (D6 do 01-09-SUMMARY)
result: pass

### 7. O .xlsx do utilizador não muda
expected: SHA1 do .xlsx igual antes e depois de `pesquisar`
result: pass

### 8. Proibições de nível judgment
expected: em src/strata/fetch.py e nos SUMMARY do 01-07/01-09, sem retentativas, proxies nem troca de identidade (veredicto não autoritativo do verificador: cumpridas)
result: pass

## Summary

total: 8
passed: 5
issues: 2
pending: 0
skipped: 1
blocked: 0

## Gaps

- gap_id: G-01-3
  truth: "O link da 1.ª oferta de OSB da Bricomarché abre a página do produto na loja da oferta, com o preço mostrado (14,49 € / 18,49 €) e IVA incluído"
  status: failed
  reason: "User reported: A oferta principal da Bricomarché não devia ser uma loja com 0 em stock: devia mostrar primeiro a mais barata que tem stock (15,49 € em Ponte de Sor)"
  severity: major
  test: 3
  artifacts: []  # Filled by diagnosis
  missing: []    # Filled by diagnosis

- gap_id: G-01-5
  truth: "Para cada linha da folha, as ofertas mostradas são o produto pedido (ex.: 'OSB 12 mm' mostra a placa de 12 mm), mais baratas primeiro, e não outros produtos que só mencionam a palavra (cola/espuma 'para OSB')"
  status: failed
  reason: "User reported: Confirmo os preços, mas admito que o facto da cola aparecer antes da placa de 12mm é um problema, o objetivo desta aplicação é encontrar o que eu procuro e com o preço mais barato se procurar algo e aparecer outra coisa a aplicaão nao esta a cumprir o proposito, arranja isto para garantir que a aplicação cumpri o objetivo, o metodo como fara isto deixo a sua decisão, mas talvez fazer uma filtragem no fim possa ser uma solução nao sei."
  severity: major
  test: 5
  artifacts: []  # Filled by diagnosis
  missing: []    # Filled by diagnosis
