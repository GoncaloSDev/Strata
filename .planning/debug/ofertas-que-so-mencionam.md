---
status: diagnosed
trigger: "G-01-5 (UAT teste 5): 'OSB 12 mm' na Obras 360 mostra cola e espuma 'para OSB' antes da placa de 12 mm; goal: find_root_cause_only"
created: 2026-10-23T19:00:00Z
updated: 2026-10-23T19:40:00Z
---

## Current Focus

bug_class: Bohrbug (determinístico; reproduzido sem rede com as fixtures)
hypothesis: CONFIRMADA. (a) Depois da pesquisa alargada D-14, a pergunta completa ('OSB 12 mm') deixa de entrar em qualquer filtro ou ordenação: o adaptador só recebe 'OSB' e search_store ordena só pelo preço. Isto, sozinho, explica o caso reportado. (b) O filtro de palavras D-15 não distingue o produto de uma menção; explica 'cimento cola' -> MISTURADOR e 'perfis' -> Varão, mas não é preciso para o caso OSB.
test: repro sem rede (scratchpad/repro_g01_5.py) e experiência diferencial (scratchpad/repro_g01_5_direct.py)
expecting: n/a (diagnóstico fechado)
next_action: devolver ROOT CAUSE FOUND ao orquestrador; a correção é planeada por /gsd-plan-phase --gaps

reasoning_checkpoint:
  hypothesis: "A cola aparece antes da placa de 12 mm porque, quando a Obras 360 dá 0 resultados para 'OSB 12 mm', search_store refaz a pesquisa só com 'OSB' (search.py:25-26), o adaptador filtra os pais e as variantes só com 'OSB' (obras360.py:124-125, 151) e search_store ordena só pelo preço por artigo (search.py:46-52, money.py:37-38); nenhum passo volta a comparar com 'OSB 12 mm'."
  confirming_evidence:
    - "Repro sem rede: chamadas ao adaptador ['OSB 12 mm', 'OSB']; ordem final 8,36 cola (full=False), 15,02 placa 9 MM (False), 19,37 placa 12 MM (True), ..."
    - "Diferencial: com a mesma lista e os mesmos detalhes, mas a loja a responder à pergunta completa, só aparece a placa 12 MM (19,37 €) e as outras 7 ofertas, cola incluída, ficam escondidas e contadas (hidden=7)"
    - "Saída ao vivo: cabeçalho 'Obras 360: ok (pesquisa alargada: 'OSB')' sem a frase 'N escondidas pelo filtro de título com ...', logo found.raw == 0 na 1.ª pesquisa (o ramo all_hidden escreveria essa frase em search.py:57-58)"
  falsification_test: "Se a cola passasse no filtro com a pergunta completa (title_matches('OSB 12 mm', título da cola) == True) ou se a loja devolvesse resultados para 'OSB 12 mm', a hipótese (a) caía. Ambos medidos: False, e raw == 0."
  fix_rationale: "Voltar a comparar as ofertas da pesquisa alargada com a pergunta completa (já existe title_matches) e pôr à frente as que batem, num só sítio comum às 3 lojas (search_store). Repõe para a pesquisa alargada o comportamento que o caso direto já tem."
  blind_spots: "Não pedi ao vivo à Obras 360 (inferido do cabeçalho). O corte K=20 do adaptador usa as palavras da alargada para escolher os pais (obras360.py:129-132): numa alargada muito larga, o pai que tem a variante certa pode nem ser expandido, e um passo final em search_store não o recupera. Para 'OSB' não acontece (não há nota '+N produtos não expandidos')."
  candidate_causes:
    - "code: search_store perde a pergunta completa depois de alargar (search.py:25-34, 46-52)"
    - "design/config: D-15 manda, na alargada, comparar com as palavras dessa pesquisa (01-CONTEXT.md:39); o código cumpre a decisão"
    - "data: a pesquisa da loja dá 0 para 'OSB 12 mm' e o nome do pai ('Placa OSB 9-30MM') não tem a espessura pedida, só a designação da variante"
    - "code: title_matches é um subconjunto de palavras (words.py:168-170), cego ao papel da palavra (produto vs menção)"
  and_gate: "sim: o sintoma reportado precisa de (1) a loja dar 0 para a pergunta completa, disparando D-14, E (2) search_store filtrar e ordenar só com a alargada e o preço, E (3) existir um produto mais barato que só menciona 'OSB'. Sem (1), obras360.py:151 já escondia a cola (diferencial). (2) é o único elo do lado da app que se corrige em código."

## Symptoms

expected: para cada linha da folha, as ofertas mostradas são o produto pedido ('OSB 12 mm' mostra a placa de 12 mm), mais baratas primeiro, sem produtos que só mencionam a palavra (cola/espuma 'para OSB')
actual: "Obras 360: ok (pesquisa alargada: 'OSB')" com 8,36 € Cola SikaBond-52 ... OSB, 14,61 € Espuma Sika Boom-182 ... OSB, 15,02 € Placa OSB ... 9 MM, 15,06 € Espuma ... OSB, 19,37 € Placa OSB ... 12 MM, "+15 ofertas não mostradas", "+5 ofertas escondidas: título sem 'OSB'". Mesma classe: Allmat 'cimento cola' mostra MISTURADOR CIMENTO COLA 85/100/120MM logo a seguir aos sacos; 'perfis' na Obras 360 já mostrou um varão roscado "Fixação Perfil Teto"
errors: nenhum
reproduction: UAT teste 5 (01-UAT.md); `printf 'OSB 12 mm 1 un\n\n' | uv run python -m strata pesquisar`; saída gravada em C:/Users/gonca/AppData/Local/Temp/claude/C--DEV-Strata/54361641-9c68-4a97-b927-a2966922053e/scratchpad/uat-teste5/saida.txt
started: descoberto na UAT da Phase 1 (2026-10-23)

## Eliminated

- hypothesis: "O Tamanho da folha ('2500x1250x12 mm') entra na pesquisa e chega para separar a placa"
  evidence: "Item.size só é escrito em sheet.py:102 e não é lido em mais lado nenhum (grep). D-13 adia o Tamanho para a Phase 3. E mesmo que entrasse, title_matches('2500x1250x12 mm', variante 12 MM) == False, porque a loja escreve '2,5 M x 1,25 M': comparar medidas em unidades diferentes precisa da extração de especificações da Phase 3."
  timestamp: 2026-10-23T19:25:00Z

- hypothesis: "O filtro de dois níveis do 01-08 está partido no caso direto"
  evidence: "Diferencial: com a loja a responder a 'OSB 12 mm', obras360.search escolhe os pais com 'OSB' e filtra as variantes com 'OSB 12 mm'; só a placa 12 MM fica (hidden=7). O filtro funciona; é só contornado na alargada, porque o adaptador recebe a alargada como pergunta."
  timestamp: 2026-10-23T19:30:00Z

## Evidence

- timestamp: 2026-10-23T19:00:00Z
  checked: .planning/debug/knowledge-base.md
  found: não existe (sem MemPalace); sem padrão conhecido
  implication: investigação do zero

- timestamp: 2026-10-23T19:05:00Z
  checked: src/strata/search.py:17-60 (search_store)
  found: "Linha 22: store.search(item.product). Linhas 25-26: se raw == 0 ou tudo escondido, b = broadened(item.product) e wide = await store.search(b, fetch); só b vai para o adaptador. Linhas 31-34: found = wide e cada oferta fica broadened=True; nenhuma comparação com item.product. Linhas 46-52: ordenação só por in_unit(o, item.unit), estável."
  implication: depois de alargar, a pergunta completa não volta a ser usada; este é o sítio onde se monta e ordena o resultado alargado

- timestamp: 2026-10-23T19:06:00Z
  checked: src/strata/money.py:35-43 (in_unit)
  found: "para 'un' e 'saco' a chave é o preço de um artigo (linha 37-38): cola 8,36 < placa 12 mm 19,37"
  implication: só o preço decide; não há nível de relevância na chave

- timestamp: 2026-10-23T19:08:00Z
  checked: src/strata/stores/obras360.py:105-153 (search)
  found: "loose = broadened(query) or query (124); need = words(query) para ordenar os pais (129-131); variantes filtradas com title_matches(query, o.title) (151). Na chamada alargada query = 'OSB', por isso loose == query == 'OSB' e os dois níveis colapsam num só: o '12mm' nunca chega ao filtro das variantes nem à ordenação dos pais."
  implication: o filtro de dois níveis do 01-08 é contornado na pesquisa alargada (confirmado)

- timestamp: 2026-10-23T19:10:00Z
  checked: 01-CONTEXT.md:38-39 (D-14, D-15) e :37 (D-13)
  found: "D-15: 'Na pesquisa alargada, compara com as palavras dessa pesquisa.' D-13: só o Produto vai para a pesquisa; Tamanho/Família/Referência só na Phase 3."
  implication: o comportamento atual cumpre a decisão escrita; a correção obriga a emendar a cláusula da alargada em D-15

- timestamp: 2026-10-23T19:12:00Z
  checked: saida.txt (ao vivo) e search.py:57-58
  found: "o cabeçalho da Obras 360 não tem 'N escondidas pelo filtro de título com ...' nem 'também sem ofertas com'; o ramo all_hidden escreveria a 1.ª frase"
  implication: a 1.ª pesquisa ('OSB 12 mm') deu raw == 0 na loja; D-14 disparou por zero resultados, não pelo filtro

- timestamp: 2026-10-23T19:20:00Z
  checked: repro sem rede scratchpad/repro_g01_5.py (FakeFetcher do conftest; lista 'OSB+12+mm' -> fixture no-results; lista 'OSB' -> fixture osb; detalhe da placa = fixture; detalhe da cola sintético a 8,36 €)
  found: "chamadas ao adaptador ['OSB 12 mm', 'OSB']; status ok, broadened_query 'OSB'; ordem 8,36 Cola (full=False) / 15,02 Placa 9 MM (False) / 19,37 Placa 12 MM (True) / 23,72 15 MM (False) / ... Só a variante 12 MM bate a pergunta completa."
  implication: sintoma reproduzido de forma determinística; um nível 'bate a pergunta completa' antes do preço põe a placa 12 MM em 1.º

- timestamp: 2026-10-23T19:28:00Z
  checked: diferencial scratchpad/repro_g01_5_direct.py (igual, mas a loja responde à pergunta completa com a lista osb)
  found: "chamadas ['OSB 12 mm']; uma só oferta mostrada: 19,37 € Placa 12 MM; hidden=7 (cola e as outras espessuras contadas)"
  implication: os mesmos dados dão o resultado certo quando a pergunta completa chega ao filtro; a diferença é só a perda da pergunta na alargada

- timestamp: 2026-10-23T19:32:00Z
  checked: words.title_matches em casos da mesma classe
  found: "True para 'cimento cola' vs 'MISTURADOR CIMENTO COLA 85MM' e vs 'LIZ CIMENTO COLA CINZA SACO 25 KG'; True para 'perfis' vs 'Varão Roscado M6 x 1M Fixação Perfil Teto'; True para 'OSB' vs a cola SikaBond; True para 'OSB 30 mm' vs a variante 9 MM (gama '9-30MM' no nome do pai, shortcut já anotado em obras360.py:150)"
  implication: quando todas as palavras pedidas estão no título do acessório, nenhum filtro de palavras os separa; o misturador e o saco LIZ têm 'cimento cola' na mesma posição (índice 1), por isso nem a posição serve. É a classificação exato/parecido/outro da Phase 3 (MATCH-01/02, LIST-06)

- timestamp: 2026-10-23T19:35:00Z
  checked: uv run python -m pytest -q
  found: 201 passed (linha de base, sem alterações ao código)
  implication: os testes atuais não cobrem a alargada com ofertas que batem e não batem a pergunta completa; test_pesquisa_alargada_quando_a_loja_da_zero e test_tudo_escondido_com_medidas_tenta_a_alargada só têm ofertas que não batem e continuam válidos com um nível de relevância

## Resolution

root_cause: "(a) Causa do caso reportado: na pesquisa alargada D-14, search_store (src/strata/search.py:25-34) passa ao adaptador só a pergunta alargada ('OSB') e depois ordena só pelo preço por artigo (search.py:46-52, money.py:37-38). A pergunta completa ('OSB 12 mm') nunca volta a ser comparada, por isso o filtro de dois níveis da Obras 360 (obras360.py:124-125, 151) colapsa num filtro só com 'OSB', e a cola (8,36 €) passa à frente da placa 12 MM (19,37 €), a única oferta que bate a pergunta completa. A decisão D-15 (01-CONTEXT.md:39) manda fazer exatamente isto na alargada. Dispara porque a loja dá 0 resultados para 'OSB 12 mm'. (b) Causa da classe geral, que não se fecha com código determinístico: title_matches (words.py:168-170) é um teste de subconjunto de palavras e não distingue o produto de uma menção quando todas as palavras pedidas estão no título do acessório ('MISTURADOR CIMENTO COLA', 'Varão ... Fixação Perfil', 'Cola ... OSB' para a pergunta 'OSB')."
fix: (fora de âmbito: goal find_root_cause_only)
verification: (n/a: diagnóstico)
files_changed: []
