---
status: complete
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
source: [01-VERIFICATION.md]
started: 2026-10-23T14:08:58Z
updated: 2026-10-24T00:31:10.908Z
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

### 9. Re-teste 3: Bricomarché mostra a loja mais barata com stock (G-01-3, plano 01-10)
expected: `printf 'placa osb 9mm 1 un\n\n' | uv run python -m strata pesquisar` e abrir o link da 1.ª oferta da Bricomarché: uma loja física com stock (ex.: 15,49 € em Ponte de Sor), preço igual ao do site; se a mais barata não tiver stock, aparece a nota 'mais barata sem stock: X em Y'
result: pass

### 10. Re-teste 5: folha com 4 linhas mostra o produto pedido (G-01-5, planos 01-11 e 01-12)
expected: folha com OSB 12 mm / un / 30; cimento cola / saco / 10; tinta branca / L / 15; pavimento 60x120 / m² / 10 e `pesquisar`: OSB 12 mm mostra a placa de 12 mm em 1.º na Obras 360, sem cola nem espuma, o resto contado em '+N ofertas escondidas'; pavimento 60x120 mostra na Bricomarché as placas 60X120 a 34,55 € (23,99 €/m²), com preço igual ao do site
result: pass

### 11. Proibições judgment do 01-10 e do 01-12
expected: offer_from em src/strata/stores/bricomarche.py só usa as linhas já lidas (nenhum pedido novo por causa do stock) e o 01-12 fez uma só corrida ao vivo (veredicto não autoritativo do verificador: cumpridas)
result: pass
reason: offer_from (bricomarche.py:74-102) só usa as linhas recebidas, sem fetch; 01-12 fez uma só corrida ao vivo

## Summary

total: 11
passed: 8
issues: 2
pending: 0
skipped: 1
blocked: 0

## Gaps

- gap_id: G-01-3
  truth: "O link da 1.ª oferta de OSB da Bricomarché abre a página do produto na loja da oferta, com o preço mostrado (14,49 € / 18,49 €) e IVA incluído"
  status: resolved
  resolved_by: 01-10-PLAN
  resolved_at: 2026-10-24
  reason: "User reported: A oferta principal da Bricomarché não devia ser uma loja com 0 em stock: devia mostrar primeiro a mais barata que tem stock (15,49 € em Ponte de Sor)"
  severity: major
  test: 3
  root_cause: "src/strata/stores/bricomarche.py:74 offer_from() escolhe a variação principal com cheapest(rows), que ignora o stock; has_stock() só alimenta a nota 'com stock: X em Y' (linhas 80-83). Cumpre a resolução da Open Question 1 do 01-RESEARCH (mostrar a mais barata absoluta), que o 01-04-PLAN deixou como EDGE por rever à mão e que o UAT rejeitou. RES-02 só proíbe esconder ofertas, não preferir lojas com stock."
  artifacts:
    - path: "src/strata/stores/bricomarche.py"
      issue: "offer_from (73-83): oferta principal = mais barata entre lojas físicas sem olhar para o stock; a mais barata com stock só entra na nota"
    - path: "tests/test_bricomarche.py"
      issue: "test_offer_from_amostra_47412, test_offer_from_sem_dica_quando_a_mais_barata_tem_stock e test_search_osb fixam o comportamento rejeitado"
    - path: "tests/test_e2e.py"
      issue: "linha 52 espera 'loja: Coina - Barreiro' no bloco 'placa osb'"
  missing:
    - "Oferta principal da Bricomarché = a variação mais barata COM stock; só se nenhuma loja tiver stock, a mais barata absoluta com o stock dela"
    - "Quando a mais barata absoluta está sem stock e é mais barata que a escolhida, mostrá-la numa nota (ex.: 'mais barata sem stock: 18,49 € em Coina - Barreiro') — nada escondido (RES-02)"
    - "Atualizar os testes que fixam o comportamento antigo; testes novos: nenhuma loja com stock; empate de preço com e sem stock"
    - "Registar a nova decisão em STATE.md (substitui a decisão do 01-04)"
  debug_session: ".planning/debug/bricomarche-oferta-sem-stock.md"

- gap_id: G-01-5
  truth: "Para cada linha da folha, as ofertas mostradas são o produto pedido (ex.: 'OSB 12 mm' mostra a placa de 12 mm), mais baratas primeiro, e não outros produtos que só mencionam a palavra (cola/espuma 'para OSB')"
  status: resolved
  resolved_by: 01-12-PLAN
  resolved_at: 2026-10-24
  reason: "User reported: Confirmo os preços, mas admito que o facto da cola aparecer antes da placa de 12mm é um problema, o objetivo desta aplicação é encontrar o que eu procuro e com o preço mais barato se procurar algo e aparecer outra coisa a aplicaão nao esta a cumprir o proposito, arranja isto para garantir que a aplicação cumpri o objetivo, o metodo como fara isto deixo a sua decisão, mas talvez fazer uma filtragem no fim possa ser uma solução nao sei."
  severity: major
  test: 5
  root_cause: "(a) Quando a loja dá 0 resultados, search_store (src/strata/search.py:25-34) refaz a pesquisa e passa ao adaptador só a pergunta alargada ('OSB'), junta as ofertas sem as voltar a comparar com item.product e ordena só pelo preço (search.py:46-52); na Obras 360 o filtro de dois níveis do 01-08 fica reduzido a 'OSB' (obras360.py:124, :151). Cumpre a cláusula de D-15 'na pesquisa alargada compara com as palavras dessa pesquisa' (01-CONTEXT.md:39), que tem de ser emendada. (b) title_matches (words.py:168-170) não distingue o produto de uma menção (misturador de cimento cola, varão 'Fixação Perfil', cola 'para OSB') — isso é a classificação exato/parecido/outro da Phase 3 (IA)."
  artifacts:
    - path: "src/strata/search.py"
      issue: "25-34 e 46-52: o resultado alargado é montado e ordenado sem nenhum nível de relevância face à pergunta completa"
    - path: "src/strata/stores/obras360.py"
      issue: "124-132 e 151: os dois níveis só funcionam com a pergunta completa; na alargada os 20 pais (K=20) também são escolhidos com as palavras alargadas"
    - path: "src/strata/report.py"
      issue: "60-62: a linha '+N ofertas escondidas: título sem …' só conhece um motivo"
    - path: "src/strata/words.py"
      issue: "168-170: filtro por palavras — mecanismo (b), Phase 3"
  missing:
    - "Phase 1: em search_store, depois da pesquisa alargada, comparar cada oferta com title_matches(item.product, o.title); se pelo menos uma bater a pergunta completa, mostrar só essas (mais baratas primeiro) e contar as que só batem a alargada numa linha própria (ex.: '+7 ofertas escondidas: título sem 'OSB 12 mm''), nada escondido em silêncio (D-02/STORE-05); se nenhuma bater, fica como hoje, marcado 'pesquisa alargada'"
    - "report.py com dois motivos de 'escondida' (pergunta completa vs alargada)"
    - "Emendar D-15 em 01-CONTEXT.md (a pesquisa alargada passa a dar prioridade às ofertas que batem a pergunta completa) e registar em STATE.md"
    - "Teste de regressão a partir de scratchpad/repro_g01_5.py (lista osb + detalhe da placa + cola sintética): a placa de 12 MM (19,37 €) é a 1.ª oferta da Obras 360; casos vizinhos: nenhuma bate, todas batem, ramo 'tudo escondido'"
    - "Phase 3 (fora deste fecho): produto vs menção quando todas as palavras estão no título; Tamanho em unidades diferentes; gamas no nome do pai ('9-30MM')"
  debug_session: ".planning/debug/ofertas-que-so-mencionam.md"
