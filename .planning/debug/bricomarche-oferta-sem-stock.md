---
status: diagnosed
trigger: "UAT teste 3 (G-01-3): A oferta principal da Bricomarché não devia ser uma loja com 0 em stock: devia mostrar primeiro a mais barata que tem stock (15,49 € em Ponte de Sor)"
created: 2026-10-23T19:00:00Z
updated: 2026-10-23T19:25:00Z
goal: find_root_cause_only
---

## Current Focus

hypothesis: CONFIRMADA. offer_from() (src/strata/stores/bricomarche.py:73-83) escolhe a variação de cabeçalho com cheapest(rows), que não olha para o stock; has_stock só entra depois, para construir a nota "com stock". A loja mais barata COM stock já é calculada (linha 81), mas vai para a nota em vez de ser a oferta.
bug_class: Bohrbug (determinístico; reproduz-se sempre sobre a fixture gravada)
known_pattern_candidate: nenhum (não há knowledge-base.md)
test: feito. offer_from sobre tests/fixtures/bricomarche_variations_parent-47412.json dá 18,49 € Coina - Barreiro "0 em stock" + nota "com stock: 19,99 € em Monção"; a seleção alternativa dá 19,99 € Monção "118 em stock".
expecting: n/a (diagnóstico concluído)
next_action: devolver ROOT CAUSE FOUND ao orquestrador; a correção fica para /gsd-plan-phase --gaps

reasoning_checkpoint:
  hypothesis: "A oferta principal da Bricomarché é uma loja sem stock porque offer_from() usa best = cheapest(rows) (menor preço > 0 entre lojas físicas, sem filtro de stock) como cabeçalho, e só usa has_stock() para a nota; isto foi decidido de propósito no 01-04 (Open Question 1 do RESEARCH, 'mais barata absoluta'), e o UAT rejeita essa decisão."
  confirming_evidence:
    - "Fixture 47412: as 2 variações mais baratas (18,49 Coina '0 em stock'; 19,24 Arco do Cego 'Esgotado') são sem stock; offer_from devolve Coina 18,49 '0 em stock' e nota 'com stock: 19,99 € em Monção'."
    - "Corrida ao vivo do orquestrador (9 mm): cabeçalho 14,49 € Coina '0 em stock', nota 'com stock: 15,49 € em Ponte de Sor' — o valor que o utilizador quer é exatamente o with_stock da linha 81."
    - "01-04-PLAN.md:91 e 01-RESEARCH.md:604-607: decisão 'mostra-se a variação mais barata absoluta com o stock dela' marcada 'EDGE ... unresolved — rever à mão'."
    - "Testes que trancam o comportamento: test_offer_from_amostra_47412 (18,49 Coina '0 em stock'), test_offer_from_sem_dica_quando_a_mais_barata_tem_stock (14,00 X 'Esgotado')."
  falsification_test: "Se has_stock(Coina) desse True, ou se a seleção já preferisse stock, o cabeçalho não seria Coina; has_stock(Coina) = False e cheapest(rows) devolve Coina: não falsificado."
  fix_rationale: "Escolher o cabeçalho entre as variações com stock (cair na mais barata absoluta só quando nenhuma loja tem stock) ataca a seleção, que é a causa; manter a mais barata sem stock numa nota cumpre RES-02 (nada escondido)."
  blind_spots: "Não vi as variações ao vivo do pai 9 mm (47411) nem das linhas cimento cola/tinta branca (não há fixture); confio na saída ao vivo do orquestrador, cujas notas 'com stock' provam que há loja com stock no mesmo pai. Não testei pais em que nenhuma loja tem stock na ordenação entre pais."
  candidate_causes:
    - "code: offer_from usa cheapest(rows) sem filtro de stock (bricomarche.py:74)"
    - "spec/config: decisão 01-04 / RESEARCH OQ1 leu RES-02 'sem filtrar' como 'não preferir stock no cabeçalho'"
    - "data: a loja escreve '0 em stock' com classe in-stock; eliminada como causa (has_stock trata bem)"
    - "data: preço de Coina mudou ao vivo; eliminada (fixture de 01:16 já tinha Coina '0 em stock', JSON-LD ainda diz 14.49)"
  and_gate: "Sim, dois fatores ao mesmo tempo: (1) seleção cega ao stock (defeito de código/spec) E (2) a variação mais barata está sem stock (condição dos dados, frequente: na fixture as 2 mais baratas de 64 estão sem stock, e lojas esgotadas tendem a ficar com preços antigos/baixos). (2) é gatilho, não defeito; a causa a corrigir é (1)."

## Symptoms

expected: o link da 1.ª oferta de OSB da Bricomarché abre a página do produto nessa loja, com o preço mostrado e IVA incluído; o utilizador quer que a oferta principal seja a loja mais barata COM stock.
actual: "A oferta principal da Bricomarché não devia ser uma loja com 0 em stock: devia mostrar primeiro a mais barata que tem stock (15,49 € em Ponte de Sor)". Corrida ao vivo 2026-10-23: "14,49 € Placa Osb Lisa 2.50X1.25 9Mm … 0 em stock · loja: Coina - Barreiro · com stock: 15,49 € em Ponte de Sor". A página de Coina diz "Artigo temporariamente indisponível" e esconde o preço (o JSON-LD ainda diz 14.49). Mesmo padrão em cimento cola (Esgotado · Guarda · com stock 1,99 € em Felgueiras) e tinta branca (Esgotado · Vila Real).
errors: nenhum
reproduction: printf 'placa osb 9mm 1 un\n\n' | uv run python -m strata pesquisar ; UAT teste 3
started: descoberto no UAT; a fixture de 2026-10-23 01:16 já tinha Coina "0 em stock" (não é mudança da loja)

## Eliminated

- hypothesis: has_stock() classifica mal "0 em stock" (classe in-stock) como com stock
  evidence: has_stock(Coina) = False na fixture; a regex STOCK_N (bricomarche.py:21, 62-63) trata "0 em stock" antes da classe; tests/test_bricomarche.py:62-65 cobre o caso. A classificação está certa; o problema é onde ela é usada.
  timestamp: 2026-10-23T19:10:00Z

- hypothesis: a loja mudou o stock/preço de Coina depois da gravação (problema de dados ao vivo)
  evidence: a fixture gravada já tem Coina "0 em stock" classe in-stock, is_in_stock true; o comportamento reproduz-se sem rede, sempre.
  timestamp: 2026-10-23T19:10:00Z

- hypothesis: a ordenação por unidade em search.py (search_store, linhas 46-52) põe a oferta sem stock à frente de outra oferta com stock do mesmo produto
  evidence: a Bricomarché devolve UMA oferta por pai (offer_from por pai, bricomarche.py:131-140); a escolha da loja física acontece dentro de offer_from, antes da ordenação. A ordenação só compara pais diferentes pelo o.price já escolhido. Não é a causa do sintoma observado (todos os casos têm nota "com stock", logo mesmo pai).
  timestamp: 2026-10-23T19:15:00Z

## Evidence

- timestamp: 2026-10-23T19:05:00Z
  checked: src/strata/stores/bricomarche.py:52-54 (cheapest), 57-64 (has_stock), 73-98 (offer_from)
  found: offer_from faz best = cheapest(rows) (linha 74) — menor preço > 0 entre lojas físicas, sem olhar para stock. url, location, price e stock saem todos de best (linhas 78, 85, 90). has_stock só é chamado nas linhas 80-81, e o resultado (with_stock = a mais barata com stock) vai só para note (linha 83).
  implication: a loja mais barata com stock já é calculada, mas fica relegada à nota; o cabeçalho é sempre a mais barata absoluta, com ou sem stock.

- timestamp: 2026-10-23T19:08:00Z
  checked: reprodução sem rede (scratchpad/repro.py) com offer_from(pai 47412, fixture de 65 variações)
  found: 64 variações válidas; 60 com stock, 4 sem. Ordenadas por preço: #0 Coina 18,49 "0 em stock" (has_stock False), #1 Arco do Cego 19,24 "Esgotado" (False), #2 Monção 19,99 "118 em stock" (True). Oferta = 18,49 € Coina - Barreiro "0 em stock", nota "com stock: 19,99 € em Monção".
  implication: sintoma reproduzido de forma determinística a partir da fixture gravada; Bohrbug.

- timestamp: 2026-10-23T19:12:00Z
  checked: .planning/phases/01-.../01-RESEARCH.md:339 e 602-607; 01-04-PLAN.md:27, 91, 115, 121; 01-04-SUMMARY.md key-decisions; STATE.md:94
  found: Open Question 1 "mais barata absoluta ou mais barata com stock?" foi resolvida como "mostra-se a variação mais barata absoluta com o stock dela" com a dica na mesma oferta. O plano marca-a como "EDGE STORE-01 (unclassified, unresolved — rever à mão)". RES-02 (REQUIREMENTS.md:56) diz só "vê o stock ... sem filtrar" e REQUIREMENTS.md:87 explica "Esconder linhas esconde preços".
  implication: o comportamento é o especificado, não um erro de implementação. A causa é a decisão de desenho: RES-02 proíbe esconder ofertas, não proíbe escolher a loja com stock como cabeçalho. O UAT era a revisão à mão que o plano pedia, e rejeitou a decisão.

- timestamp: 2026-10-23T19:15:00Z
  checked: src/strata/search.py:46-52 (ordenação) e money.in_unit (money.py:35-43)
  found: search_store ordena as ofertas da loja por in_unit(o, unit) — o.price para un/saco, o.price/o.content para m²/kg/L — com chave (None no fim, valor). Não usa stock. Para a Bricomarché há uma oferta por pai; o preço que entra na chave é o da variação escolhida em offer_from.
  implication: corrigir offer_from muda também a ordenação entre pais para o preço comprável (efeito desejado). Resta um caso não observado no UAT: um pai em que NENHUMA loja tem stock continua a ordenar pelo preço sem stock e pode ficar em 1.º na lista da loja (o mesmo vale para Allmat/Obras 360, cuja ordenação também ignora stock). É decisão separada (chave de ordenação com nível de stock, precisaria de um sinal de stock comum em Offer).

- timestamp: 2026-10-23T19:18:00Z
  checked: contrafactual sem alterar código: cheapest([r for r in rows if has_stock(r)]) or cheapest(rows) sobre a fixture 47412; e o mesmo só com as 4 variações sem stock
  found: com stock disponível → 19,99 € Monção "118 em stock", link https://www.bricomarche.pt/moncao/produto/plc-osb-lisa-2-50x1-25-12mm/. Só sem stock → continua 18,49 € Coina "0 em stock" (nada escondido).
  implication: a mudança mínima dá o resultado pedido pelo utilizador e preserva RES-02 para pais todos sem stock.

- timestamp: 2026-10-23T19:20:00Z
  checked: testes que trancam o comportamento atual (grep por Coina/com stock/offer_from em tests/)
  found: tests/test_bricomarche.py:76-87 test_offer_from_amostra_47412 (18,49 Coina "0 em stock", nota Monção); :90-96 test_offer_from_sem_dica_quando_a_mais_barata_tem_stock (14,00 X "Esgotado", nota Coina 15,00); :123-129 test_search_osb (preços [14.49, 18.49] e todas em Coina); tests/test_e2e.py:52 ("loja: Coina - Barreiro" no bloco placa osb, onde o único pai com variações é o 47412). test_ponta_a_ponta (47411 sintético, Coina "12 em stock") e test_cheapest_* não mudam. Suite atual: 201 passed.
  implication: a correção tem de atualizar estes 4 testes (esperam o comportamento rejeitado) e acrescentar um teste para "nenhuma loja com stock → mostra a mais barata sem stock, sem nota".

## Resolution

root_cause: offer_from() em src/strata/stores/bricomarche.py:74 escolhe a variação de cabeçalho com cheapest(rows), que ignora o stock (linhas 52-54); has_stock() só é usado nas linhas 80-83 para pôr a mais barata COM stock numa nota. Isto implementa fielmente a decisão do 01-04 / RESEARCH Open Question 1 ("mais barata absoluta com o stock dela"), que leu RES-02 "sem filtrar" como proibição de preferir lojas com stock no cabeçalho; RES-02 só proíbe esconder ofertas. Gatilho nos dados: a variação mais barata está muitas vezes esgotada (na fixture, as 2 mais baratas de 64).
fix: (não aplicado — goal find_root_cause_only)
verification: (n/a)
files_changed: []
