---
phase: quick-261023-lee
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/strata/stores/obras360.py
  - src/strata/words.py
  - tests/test_obras360.py
  - tests/test_search.py
autonomous: true
requirements: [LIST-02, STORE-03]

estimate:
  tokens: 30000
  raw_tokens: 30000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "Na Obras 360, em 'parafuso m8x40' com 25 parafusos genéricos mais baratos, o pai 'Parafuso Sextavado M8' (o mais caro, sem o '40' no nome) é expandido; continuam a ser exatamente 20 pedidos de detalhe e a nota '+6 produtos não expandidos (limite de 20 por pesquisa)'; 'parafuso m8' (CR-04) continua verde (CR-06, STORE-03, D-15)"
    - "Plurais que o filtro escondia passam a bater: mantas geotêxteis/Manta Geotêxtil, têxteis/Têxtil, coxins/Coxim, jardins/Jardim; continuam a bater painéis/Painel, pincéis/Pincel, papéis/Papel, listéis/Listel, plafons/Plafon LED, perfis/Perfil, táxis/Táxi, jacuzzis/Jacuzzi, lápis/Lápis; aquecimento/Cimento cola e porta/Portão seccionado continuam False (WR-12, D-15)"
    - "Unidades por extenso contam como unidade: 'tubo 3 metros' bate em 'Tubo 3m' e 'cimento 25 quilos' em 'Cimento 25kg'; a alargada dá 'tubo', 'cimento', 'tinta' ('tinta 15 l.') e 'parafuso' ('parafuso 10 unidades'), e 'metro articulado 2m' dá 'metro articulado' (WR-13, D-14, D-15)"
    - "Uma medida com várias partes na pesquisa tem de estar seguida no título: 'azulejo 30x30' não bate em 'Azulejo 30x60' e 'tubo 20x20' não bate em 'Tubo Quadrado 20x40x1,5'; batem 'Azulejo 30X30 cm', 'Azulejo 30 x 30 cm', 'Tubo Quadrado 20x20x1,5', 'Chapa Osb 2440X590X18Mm' (para 'osb 18mm') e 'Parafuso Sextavado M8 — 40' (para 'parafuso m8x40'); 'parafuso 4x40' contra 'Parafuso 4x40mm' continua False por causa do WR-09, fora do âmbito (WR-07, D-15)"
    - "Os 177 testes de HEAD continuam verdes e a suite passa a 200; nenhuma dependência nova (pyproject.toml e uv.lock sem mudanças)"
  artifacts:
    - path: "src/strata/stores/obras360.py"
      provides: "Corte K=20 pelos pais com mais palavras da pesquisa no nome, depois pelo preço da lista"
      contains: "need & words("
    - path: "src/strata/words.py"
      provides: "PLURAL com -xteis e sem o par -ens, -m final igual a -n; UNIT_WORDS e SPELLED para as unidades por extenso; broadened que tira unidades a seguir a um número; SIZE com os troços seguidos de cada medida"
      contains: "SPELLED"
    - path: "tests/test_obras360.py"
      provides: "pai M8 caro expandido em 'parafuso m8x40'"
      contains: "def test_pai_com_mais_palavras_da_pesquisa_passa_a_frente_do_corte"
    - path: "tests/test_search.py"
      provides: "17 casos novos em test_title_matches e 5 em test_broadened"
      contains: "azulejo 30x30"
  key_links:
    - from: "src/strata/stores/obras360.py"
      to: "src/strata/words.py"
      via: "a chave de ordenação dos pais conta as palavras de words(query) que words(nome do pai) tem, antes do preço"
      pattern: "need & words\\("
    - from: "src/strata/search.py"
      to: "src/strata/words.py"
      via: "search_store chama broadened(item.product) para a pesquisa alargada (D-14)"
      pattern: "broadened\\(item.product\\)"
    - from: "src/strata/stores/allmat.py, src/strata/stores/bricomarche.py, src/strata/stores/obras360.py"
      to: "src/strata/words.py"
      via: "title_matches -> words -> _stem / SPELLED / SIZE decide o que se mostra e o que se conta como escondido (D-15)"
      pattern: "title_matches"
  prohibitions:
    - statement: "Nunca esconder um produto sem o contar: as ofertas cortadas pelo filtro continuam a somar às 'ofertas escondidas' (D-02, D-15)"
      status: resolved
      verification: test
    - statement: "Nunca mais de K = 20 pedidos de detalhe por pesquisa na Obras 360 (ritmo por loja)"
      status: resolved
      verification: test
    - statement: "Nunca mexer no dinheiro: os preços continuam Decimal e as chaves de preço da ordenação não mudam"
      status: resolved
      verification: test
---

<objective>
Fechar quatro achados do 01-REVIEW.md no filtro de título, pela ordem pedida: CR-06 (o corte K=20 da Obras 360 volta a perder o pai M8 em "parafuso m8x40"), WR-12 (plurais geotêxteis, coxins, jardins), WR-13 (unidades por extenso: "metros", "quilos", "unidades", "l.") e WR-07 ("azulejo 30x30" bate em "Azulejo 30x60").

Purpose: hoje a ferramenta esconde produtos que a loja vende (WR-12, WR-13), mostra azulejos de outra medida (WR-07) e, num pedido normal de obra ("parafuso M8x40"), nem pede o detalhe do parafuso certo (CR-06). Uma pesquisa à mão ganha à ferramenta, o que falha o Core Value.
Output: a chave de ordenação dos pais da Obras 360; `_stem`, `UNIT_WORDS`/`SPELLED`, `broadened` e `SIZE` em `src/strata/words.py`; 23 testes novos. Só biblioteca padrão, cerca de 20 linhas de código de produção.
</objective>

<execution_context>
@~/.claude/gsd-core/workflows/execute-plan.md
@~/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-REVIEW.md
@.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-09-SUMMARY.md
@src/strata/words.py
@src/strata/stores/obras360.py

<interfaces>
Em HEAD (9262daa), ler os ficheiros para o detalhe:
- strata.words: DIMS (linha 8, parte "AxBxC" nas partes); a regex dos litros na linha 9 ("15 lt", "15 litros" -> "15l"); CLASS (10); JOIN (11, "12 mm" -> "12mm"); TOKEN (12); UNIT_TOKENS (13); plain(s); STOP (22); comentário e tabela PLURAL (23-25); _stem(w) (28-37: guarda de 2 letras e dígitos, ciclo `for suf, rep in PLURAL`, linha do género); words(s) (40-45); title_matches(query, title) = words(query) <= words(title) (48-50); broadened(query) (53-57: tira tokens com dígitos e os que, passados por text.norm, estão em UNIT_TOKENS)
- strata.text.norm(s): sem acentos, minúsculas, sem espaços; mantém o ponto ("l." fica "l.")
- strata.stores.obras360.search(query, fetch) -> Found: `loose = broadened(query) or query`; kept = pais com title_matches(loose, nome); comentário nas linhas 126-128 e `kept.sort(...)` nas linhas 129-130, com a 1.ª chave a dizer se o nome do pai bate na pesquisa completa; chosen = kept[:K]; shown = ofertas com title_matches(query, o.title), o.title = nome do pai + " — " + designação da variante; hidden conta pais e variantes cortados
- tests/test_obras360.py: listing(products, total), parent(pid, name, price), run(query, fetch), WIDGET, LIST_URL, DETAIL_URL; test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte (CR-04, linhas 389-402) é o modelo do teste novo
- tests/test_search.py: test_title_matches (35 casos, linhas 49-90), test_broadened (6 casos, linhas 93-102)
- tests/conftest.py: fixture `fake` (FakeFetcher: route(substring, alvo), calls, cache; falha no fim se faltar uma fixture)
</interfaces>
</context>

## Assumptions

- Provado no planeamento sem tocar no repo: cópia de `src/` e `tests/` no scratchpad, com o código deste plano e os 23 testes novos, a correr com `PYTHONPATH` apontado para a cópia. Contra o código de HEAD: 13 testes novos falham (o M8, geotêxteis, têxteis, coxins, jardins, "tubo 3 metros", "cimento 25 quilos", azulejo 30x60, tubo 20x40x1,5 e 4 casos da alargada) e as 10 guardas passam. Com o código do plano: 200 passed. Por fases: depois da Tarefa 1, 178; depois da Tarefa 2, 193 (os 2 casos False do WR-07 continuam vermelhos e as 5 guardas dele já passam); depois da Tarefa 3, 200. Os números dos critérios vêm daqui.
- WR-12, plurais nasais: o pedido sugere três pares na tabela (-ins→-im, -ons→-om, -uns→-um). O plano faz o mesmo emparelhamento com uma só regra: um -m final passa a -n depois do ciclo dos sufixos e antes da linha do género. Assim "jardins" e "jardim" dão os dois "jardin". Com os três pares, "plafons" passava a "plafom" e deixava de bater em "Plafon LED", que hoje bate (provado; o mesmo com "neons"/"Neon" e "pins"/"Pin"). A regra fica antes da linha do género porque, depois dela, "forma" e "forno" davam os dois "forn" (provado). O par do sufixo -ens sai da tabela: com a regra nova é redundante, e "ferragens"/"Ferragem" continua verde.
- WR-12, -eis átono: depois de `plain()`, "geotêxteis" e "painéis" acabam os dois em "eis", por isso não há regra geral. O plano junta só o sufixo "-xteis" → "-xti" à frente da tabela (têxteis, geotêxteis). "-teis" → "-ti" apanhava mais casos, mas partia "listéis"/"Listel" (listel cerâmico, material de obra comum), que hoje bate (provado). O sufixo inteiro "texteis" não chegava: a guarda `len(w) > len(suf)` deixava "têxteis" sozinho de fora.
- WR-13: a alargada passa a tirar uma unidade só quando vem logo a seguir a um token com número. Sem isto, "metro articulado 2m" (ferramenta comum) alargava para "articulado". "unidade"/"unidades" só entram em `UNIT_TOKENS` (alargada): em `words()`, "10 unidades" não tem par colado no título ("10 un" são dois tokens), por isso não se normaliza.
- WR-07: a medida inteira guarda-se só com os números ("30X30 cm" e "30 x 30 cm" dão "30x30"). As unidades continuam nas partes, como hoje. Guardam-se todos os troços seguidos com 2 ou mais partes ("20x20x1,5" dá 20x20, 20x1,5 e 20x20x1,5), porque "tubo 20x20" tem de continuar a bater no tubo 20x20 com parede de 1,5 (hoje bate). Uma letra antes do primeiro número tira a medida inteira ("m8x40" é rosca e comprimento): na Obras 360 o pai diz "M8" e a variante "40", e o título montado "Parafuso Sextavado M8 — 40" nunca levaria "8x40". A ordem conta, como pedido: "30x60" não é "60x30".
- WR-07, caso pedido sem valor: `("parafuso 4x40", "Parafuso 4x40mm", False)`. A medida inteira "4x40" está nos dois lados. O que falha é a parte "40" da pesquisa contra "40mm" do título, que é o WR-09 (número sem unidade), fora do âmbito. Fica False, com um comentário no teste a apontar o WR-09.
- CR-06: o teste corre `obras360.search` direto (`run`) e só verifica a expansão. As variantes do detalhe gravado ("1 Placa 9 MM", …) não têm o "40", por isso não há ofertas a verificar. Ao vivo, se a variante disser "40 MM", o WR-09 esconde-a e a alargada corre na mesma (ver Limitações).

## Fora do âmbito

WR-02 a WR-06, WR-08, WR-09, WR-11 e todos os IN-* ficam como estão no 01-REVIEW.md: o código deles não muda. O 01-REVIEW.md, o 01-REVIEW-DISPOSITION.md e o bloco `deferred:` do 01-VERIFICATION.md também não mudam neste plano. A próxima re-revisão regista o que ficou corrigido.

## Limitações conhecidas (para o verificador e o SUMMARY)

- CR-06 ao vivo depende das designações da Obras 360. Com "M8x40" ou "40" na variante, as ofertas M8 aparecem. Com "40 MM", o WR-09 esconde-as e a alargada "parafuso" corre. Aí todos os pais empatam com 1 palavra e o corte volta a ser pelo preço. Fecha-se com o WR-09.
- A regra -m/-n junta palavras como "fim"/"fino". O título fica à vista, da família do WR-08.
- -eis átono fora de "-xteis" continua sem bater (fáceis/Fácil, úteis/Útil, frágeis/Frágil). Não são nomes de produto comuns.

<tasks>

<task type="tracer" tdd="true">
  <name>Tarefa 1 (tracer): "parafuso m8x40" na Obras 360 expande o pai M8 mesmo sendo o mais caro (CR-06)</name>
  <files>src/strata/stores/obras360.py, tests/test_obras360.py</files>
  <read_first>
    - src/strata/stores/obras360.py (import da linha 11; search, linhas 123-152: loose, kept, comentário e sort, K, notas, shown, hidden)
    - tests/test_obras360.py (parent, listing, run, test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte)
    - .planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-REVIEW.md (CR-06: reprodução e chave proposta)
  </read_first>
  <behavior>
    - obras360.search("parafuso m8x40") com 25 pais `parent(f"id-{i:02d}", "Parafuso Zincado Cabeça Chata", i + 1)` e `parent("id-m8", "Parafuso Sextavado M8", 99)` (total 26), rota `LIST_URL + "parafuso+m8x40"` e `"product-details/27"` → obras360_product-details_osb-parent.json: "id-m8" está entre os pedidos de detalhe, há exatamente 20 e as notas têm "+6 produtos não expandidos (limite de 20 por pesquisa)"
    - Sem mudança: test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte ("parafuso m8": M8 com 2 palavras, genéricos com 1), test_paginas_por_total_e_so_20_detalhes_dos_mais_baratos (todos empatados em "placa osb": decide o preço) e test_osb_12mm_so_a_variante_de_12mm
  </behavior>
  <action>
Teste primeiro, a falhar (em HEAD nenhum pai bate na pesquisa completa, porque o "40" só existe na variante, e o corte é só por preço): `test_pai_com_mais_palavras_da_pesquisa_passa_a_frente_do_corte(fake)` no fim de tests/test_obras360.py, num bloco com o comentário "quick 261023-lee: o pai com mais palavras da pesquisa passa à frente do corte K=20 (CR-06)". Copiar o cenário do teste do CR-04 (`fake.cache["obras360_widget"] = WIDGET`, a lista, a rota do detalhe para todos), trocar a pesquisa por "parafuso m8x40" e a rota por `LIST_URL + "parafuso+m8x40"`, correr `run(...)`. Ler os pedidos de detalhe como no teste do CR-04. Asserções de `<behavior>`. Não verificar ofertas: o detalhe gravado não tem variante "40" (ver Assumptions). Commit RED.

Código em src/strata/stores/obras360.py (CR-06, STORE-03, D-15):
- Juntar `words` ao import de `strata.words` (linha 11).
- Antes do `kept.sort`, calcular uma vez `need = words(query)`.
- A 1.ª chave da ordenação passa a `-len(need & words(p["product"]["name"]))`, no lugar do booleano atual sobre a pesquisa completa: primeiro os pais com mais palavras da pesquisa no nome. Um pai que bate na pesquisa completa tem todas as palavras e continua à frente, por isso o CR-04 fica coberto. As duas chaves de preço (preço em falta no fim, depois o preço Decimal da lista) não mudam.
- Atualizar o comentário das linhas 127-128: primeiro os pais com mais palavras da pesquisa ("M8" em "parafuso m8x40", onde o "40" só está na variante); a pesquisa solta só serve para não perder os pais cuja medida está na variante (CR-04, CR-06).
- O resto fica igual: `loose`, K = 20, as notas, o filtro das variantes, `hidden` e os 3 `shortcut:`. Commit GREEN.
  </action>
  <reversibility rating="reversible">Só muda a ordem dos pais antes do corte; volta atrás com um git revert.</reversibility>
  <verify>
    <automated>uv run python -m pytest tests/test_obras360.py -k mais_palavras -q</automated>
    <fails_when>non-zero exit (5 = nenhum teste selecionado), or the summary line lacks "1 passed"</fails_when>
    <automated>uv run python -m pytest tests/test_obras360.py -q</automated>
    <fails_when>non-zero exit, or the summary line does not start with "28 passed"</fails_when>
    <automated>uv run python -m pytest -q</automated>
    <fails_when>non-zero exit, or "failed" or "error" in the summary line, or the summary line does not start with "178 passed"</fails_when>
  </verify>
  <acceptance_criteria>
    - `uv run python -m pytest tests/test_obras360.py -k mais_palavras -q` sai com 0 e mostra "1 passed" (baseline at HEAD: código 5, 27 deselected)
    - `uv run python -m pytest tests/test_obras360.py -q` sai com 0 e mostra "28 passed" (baseline at HEAD: 27 passed)
    - `grep -c "need & words(" src/strata/stores/obras360.py` dá 1 (baseline at HEAD: 0)
    - `grep -c "shortcut:" src/strata/stores/obras360.py` continua 3 (baseline at HEAD: 3)
    - `uv run python -m pytest -q` sai com 0 e mostra "178 passed" (177 at HEAD + 1)
  </acceptance_criteria>
  <done>Quando a Obras 360 devolve mais de 20 pais para a pesquisa solta, o pai com o código pedido no nome ("M8") é expandido mesmo sendo o mais caro e mesmo que a medida ("40") só esteja na variante. Continuam a ser no máximo 20 pedidos de detalhe.</done>
</task>

<task type="auto" tdd="true">
  <name>Tarefa 2: plurais geotêxteis/coxins/jardins (WR-12) e unidades por extenso (WR-13)</name>
  <files>src/strata/words.py, tests/test_search.py</files>
  <read_first>
    - src/strata/words.py (inteiro: a regex dos litros, UNIT_TOKENS, PLURAL, _stem, words, broadened)
    - src/strata/text.py (norm, linhas 10-13)
    - tests/test_search.py (test_title_matches e test_broadened, linhas 49-102)
    - .planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-REVIEW.md (WR-12 e WR-13)
  </read_first>
  <behavior>
    - title_matches dá True (falham em HEAD): ("mantas geotêxteis", "Manta Geotêxtil"), ("têxteis", "Têxtil"), ("coxins", "Coxim"), ("jardins", "Jardim"), ("tubo 3 metros", "Tubo 3m"), ("cimento 25 quilos", "Cimento 25kg")
    - title_matches continua True (guardas, passam em HEAD): ("pincéis", "Pincel"), ("papéis", "Papel"), ("listéis", "Listel"), ("plafons", "Plafon LED"); os 35 casos de HEAD não mudam, entre eles painéis/Painel sandwich, ferragens/Ferragem, perfis, táxis, jacuzzis, lápis (True) e aquecimento/Cimento cola, porta/Portão seccionado (False)
    - broadened (falham em HEAD): "tubo 3 metros" → "tubo", "cimento 25 quilos" → "cimento", "tinta 15 l." → "tinta", "parafuso 10 unidades" → "parafuso"
    - broadened continua (guarda, passa em HEAD): "metro articulado 2m" → "metro articulado"; os 6 casos de HEAD não mudam
  </behavior>
  <action>
Testes primeiro, a falhar. Em tests/test_search.py:
- Em `test_title_matches`, depois do caso ("projetor ip65", "Projetor LED IP44", False), um bloco com o comentário "WR-12: -eis átono de têxtil e plurais nasais (-ins/-ons/-uns); -éis tónico continua -el" com os 8 casos WR-12 de `<behavior>`, e outro com o comentário "WR-13: unidades por extenso" com os 2 casos de metros e quilos.
- Em `test_broadened`, depois do caso IN-08, os 5 casos de `<behavior>`, com "# WR-13" no primeiro e "# unidade só a seguir a um número" no de "metro articulado 2m".
Correr e confirmar 10 falhas (6 title_matches + 4 broadened). Commit RED.

Código em src/strata/words.py (WR-12, D-15). Decisões e provas na secção Assumptions:
- `PLURAL`: juntar o par ("xteis", "xti") à frente da tabela e tirar o par do sufixo -ens. Os outros pares ficam pela mesma ordem. Juntar uma linha ao comentário de cima: o -eis átono (geotêxteis → geotêxtil) só se trata em "-xteis", porque depois de `plain()` não se distingue de painéis/listéis.
- `_stem`: depois do ciclo `for suf, rep in PLURAL` e antes da linha do género, se a palavra acabar em "m", trocar essa letra por "n". Comentário de uma linha: -m e -n finais são o mesmo som (jardim/jardins, coxim/coxins, plafon/plafons). Na docstring, "ferragens -> ferragem" passa a ferragens/ferragem -> "ferragen" e junta-se jardins/jardim -> "jardin".

Código em src/strata/words.py (WR-13, D-14, D-15):
- No lugar da regex dos litros (linha 9), duas constantes. `UNIT_WORDS`: dicionário palavra → abreviatura com lt, lts, litro, litros → "l"; metro, metros → "m"; quilo, quilos, quilograma, quilogramas → "kg"; grama, gramas → "g". `SPELLED`: regex compilada a partir das chaves, `r"(\d)\s*(" + "|".join(UNIT_WORDS) + r")\b"`, com um comentário de uma linha ("3 metros" -> "3m", "25 quilos" -> "25kg").
- Em `words()`, onde hoje se aplica a regex dos litros (entre DIMS e CLASS), aplicar `SPELLED.sub` com uma função que devolve o dígito seguido de `UNIT_WORDS[palavra]`. O resto do encadeamento fica igual. Juntar "3 metros" = "3m" à docstring.
- `UNIT_TOKENS` passa a {"mm", "cm", "m", "m2", "kg", "g", "l", "ml", "un", "unidade", "unidades", "x"} mais todas as chaves de `UNIT_WORDS` (`*UNIT_WORDS`). Os sinónimos de litro passam a vir do dicionário.
- `broadened`: um token sai se tiver um dígito, ou se `norm(t).rstrip(".")` estiver em `UNIT_TOKENS` e o token anterior tiver um dígito. Isto apanha "l." e "lt." e deixa "metro" em "metro articulado". Docstring: "Sem números nem unidades a seguir a um número". O retorno (None se nada sobra ou nada muda) fica igual.
- `title_matches` não muda. Só biblioteca padrão: sem biblioteca de stemming nem de unidades. Commit GREEN.
  </action>
  <reversibility rating="reversible">Funções puras de texto cobertas por testes; volta atrás com um git revert.</reversibility>
  <verify>
    <automated>uv run python -m pytest tests/test_search.py -k title_matches -q</automated>
    <fails_when>non-zero exit, "no tests ran", or the summary line does not start with "45 passed"</fails_when>
    <automated>uv run python -m pytest tests/test_search.py -k broadened -q</automated>
    <fails_when>non-zero exit, or the summary line does not start with "11 passed"</fails_when>
    <automated>uv run python -m pytest -q</automated>
    <fails_when>non-zero exit, or "failed" or "error" in the summary line, or the summary line does not start with "193 passed"</fails_when>
  </verify>
  <acceptance_criteria>
    - `uv run python -m pytest tests/test_search.py -k title_matches -q` sai com 0 e mostra "45 passed" (baseline at HEAD: 35 passed)
    - `uv run python -m pytest tests/test_search.py -k broadened -q` sai com 0 e mostra "11 passed" (baseline at HEAD: 6 passed)
    - `grep -c '("xteis", "xti")' src/strata/words.py` dá 1 (baseline at HEAD: 0)
    - `grep -c '("ens", "em")' src/strata/words.py` dá 0 (baseline at HEAD: 1)
    - `grep -c 'endswith("m")' src/strata/words.py` dá 1 (baseline at HEAD: 0)
    - `grep -c "SPELLED" src/strata/words.py` dá 2 ou mais (definição e uso; baseline at HEAD: 0)
    - `grep -c 'rstrip(".")' src/strata/words.py` dá 1 (baseline at HEAD: 0)
    - `uv run python -m pytest -q` sai com 0 e mostra "193 passed" (178 depois da Tarefa 1 + 15)
  </acceptance_criteria>
  <done>"mantas geotêxteis", "coxins" e "jardins" deixam de esconder o produto que a loja vende, sem partir painéis, pincéis, papéis, listéis nem plafons. "tubo 3 metros" bate em "Tubo 3m", e a alargada tira "metros", "quilos", "unidades" e "l." quando vêm a seguir a um número.</done>
</task>

<task type="auto" tdd="true">
  <name>Tarefa 3: medida com várias partes na pesquisa tem de estar seguida no título (WR-07)</name>
  <files>src/strata/words.py, tests/test_search.py</files>
  <read_first>
    - src/strata/words.py (DIMS, words, depois da Tarefa 2)
    - tests/test_search.py (test_title_matches, depois da Tarefa 2)
    - .planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-REVIEW.md (WR-07 e WR-09)
  </read_first>
  <behavior>
    - title_matches dá False (dão True em HEAD): ("azulejo 30x30", "Azulejo 30x60"), ("tubo 20x20", "Tubo Quadrado 20x40x1,5")
    - title_matches dá True (guardas, passam em HEAD): ("azulejo 30x30", "Azulejo 30X30 cm"), ("azulejo 30x30", "Azulejo 30 x 30 cm"), ("tubo 20x20", "Tubo Quadrado 20x20x1,5"), ("parafuso m8x40", "Parafuso Sextavado M8 — 40")
    - title_matches dá False (guarda, passa em HEAD; motivo WR-09, fora do âmbito): ("parafuso 4x40", "Parafuso 4x40mm")
    - Sem mudança: ("osb 18mm", "Chapa Osb 2440X590X18Mm", True), ("12mm", "Placa 2440x1220x12 mm", True), ("osb 12mm", "Chapa Osb 2440X590X18Mm", False) e o teste do CR-06 da Tarefa 1
  </behavior>
  <action>
Teste primeiro, a falhar. Em tests/test_search.py, no fim de `test_title_matches`, um bloco com o comentário "WR-07: medida com várias partes na pesquisa tem de estar seguida no título" com os 7 casos de `<behavior>`. O caso "parafuso 4x40" leva o comentário "WR-09 (fora do âmbito): "40" sem unidade não bate em "40mm"". Correr e confirmar 2 falhas (azulejo 30x60 e tubo 20x40x1,5). Commit RED.

Código em src/strata/words.py (WR-07, D-15). Decisões e provas na secção Assumptions:
- Constante `SIZE` ao lado de `DIMS`: `re.compile(r"(?<![a-z])\d+(?:[.,]\d+)?(?:\s*x\s*\d+(?:[.,]\d+)?)+")`, com um comentário de uma linha: medida com várias partes, só números ("30x30", "30 x 30", "2440x590x18"); não lê "m8x40" (rosca e comprimento, não medida).
- `words()`: primeiro `s = plain(s)`. Depois, para cada resultado de `SIZE.findall(s)`, tirar os espaços, partir em "x" e juntar ao conjunto todos os troços seguidos com 2 ou mais partes, unidos por "x" ("20x20x1,5" dá "20x20", "20x1,5" e "20x20x1,5"). Uma lista em compreensão para as partes e um conjunto em compreensão para os troços chegam. Só depois o encadeamento que já existe (DIMS, SPELLED, CLASS, JOIN, TOKEN, STOP, _stem), sem mudanças. Devolver a união dos dois conjuntos.
- Docstring de `words`: as medidas LxCxE ficam partidas e também inteiras (cada troço seguido).
- `title_matches` e `broadened` não mudam. Uma medida de uma só parte na pesquisa ("osb 18mm") continua a bater numa parte do LxCxE do título, como no 01-08. Commit GREEN.
  </action>
  <reversibility rating="reversible">Função pura de texto coberta por testes; volta atrás com um git revert.</reversibility>
  <verify>
    <automated>uv run python -m pytest tests/test_search.py -k title_matches -q</automated>
    <fails_when>non-zero exit, "no tests ran", or the summary line does not start with "52 passed"</fails_when>
    <automated>uv run python -m pytest -q</automated>
    <fails_when>non-zero exit, or "failed" or "error" in the summary line, or the summary line does not start with "200 passed"</fails_when>
  </verify>
  <acceptance_criteria>
    - `uv run python -m pytest tests/test_search.py -k title_matches -q` sai com 0 e mostra "52 passed" (baseline at HEAD: 35; depois da Tarefa 2: 45)
    - `grep -c "SIZE" src/strata/words.py` dá 2 ou mais (definição e uso; baseline at HEAD: 0)
    - `uv run python -m pytest tests/test_obras360.py -q` continua com "28 passed"
    - `uv run python -m pytest -q` sai com 0 e mostra "200 passed" (193 depois da Tarefa 2 + 7)
    - `git diff --quiet 9262daa -- pyproject.toml uv.lock` sai com 0 (nenhuma dependência nova; continua como em HEAD)
  </acceptance_criteria>
  <done>"azulejo 30x30" deixa de mostrar azulejos 30x60 e "tubo 20x20" deixa de mostrar tubos 20x40. O azulejo 30x30 escrito "30X30 cm" ou "30 x 30 cm" e o tubo 20x20 com parede continuam a aparecer.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| lojas → filtro de título | Nomes de pais e títulos/designações vindos das lojas decidem o que se mostra, o que se expande (Obras 360) e o que se conta como escondido |
| utilizador → pesquisa | O texto do produto (folha Excel ou texto colado) passa por words()/broadened() e pelas regex novas |
| app → lojas | Pedidos de detalhe da Obras 360, no máximo K = 20 por pesquisa |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01-43 | Tampering (produto diferente mostrado) | words._stem (regra -m/-n, par -xteis) | low | accept | Junta poucas palavras novas ("fim"/"fino"). O título de cada oferta fica à vista. Separar exato de parecido é da Phase 3 (WR-08 adiado) |
| T-01-44 | Repudiation (produto escondido) | words.words com SIZE (WR-07) | medium | mitigate | O filtro fica mais estrito só quando a pesquisa tem medida com várias partes. As ofertas cortadas continuam a somar às "ofertas escondidas" (D-02, D-15). As guardas "30X30 cm", "30 x 30 cm", "20x20x1,5" e "M8 — 40" provam que a mesma medida escrita de outra forma não se perde |
| T-01-45 | Denial of Service (contra a loja) | obras360.search, chave de ordenação | low | mitigate | A chave só muda quem entra nos K = 20. O teste do CR-06 exige exatamente 20 pedidos de detalhe. O ritmo por host do Fetcher fica igual |
| T-01-46 | Denial of Service (ReDoS) | words.SIZE, words.SPELLED sobre títulos das lojas | low | mitigate | Cada repetição de SIZE tem de consumir um "x", e SPELLED é uma alternância fixa ancorada num dígito: nenhum quantificador ambíguo aninhado. A suite inteira corre em menos de 2 s |
| T-01-SC | Tampering | instalação de pacotes | high | mitigate | Este plano não instala pacotes (só biblioteca padrão; sem biblioteca de stemming nem de unidades). `git diff --quiet 9262daa -- pyproject.toml uv.lock` sai com 0. Qualquer `uv add` passaria pelo gate de legitimidade com checkpoint blocking-human |
</threat_model>

<verification>
- `uv run python -m pytest -q` sai com 0 e mostra "200 passed" (177 at HEAD + 23)
- Os critérios das 3 tarefas, com as baselines de HEAD
- `git diff --quiet 9262daa -- pyproject.toml uv.lock` sai com 0
</verification>

<success_criteria>
- CR-06: o pai com o código pedido no nome nunca fica fora do corte K=20 por ser caro, mesmo com a medida só na variante (STORE-03)
- WR-12: geotêxteis, têxteis, coxins e jardins batem no singular, e os plurais em -éis tónico continuam a bater (LIST-02, D-15)
- WR-13: metros, quilos, gramas e litros por extenso contam como unidade no filtro, e a alargada tira-os, e também "unidades" e "l.", quando vêm a seguir a um número (D-14, D-15)
- WR-07: uma medida AxB/AxBxC na pesquisa só bate num título que a tenha seguida, pela mesma ordem (D-15)
</success_criteria>

## Cobertura das fontes

| Fonte | Item | Onde |
|-------|------|------|
| GOAL (pedido) | CR-06, WR-12, WR-13, WR-07, por esta ordem | Tarefas 1, 2 (WR-12 + WR-13) e 3 |
| REQ | LIST-02 (texto livre sem categoria: o filtro não esconde o produto) | Tarefas 2 e 3 |
| REQ | STORE-03 (Obras 360 com variantes expandidas) | Tarefa 1 |
| CONTEXT | D-15 (filtro de título contado) | Tarefas 1, 2 e 3 |
| CONTEXT | D-14 (alargada sem números nem unidades) | Tarefa 2 |
| CONTEXT | D-02 (nada some sem contagem) | `hidden` sem mudanças; T-01-44 |
| REVIEW | casos e fixes propostos do CR-06, WR-12, WR-13 e WR-07 | Tarefas 1-3; desvios justificados em Assumptions |

RESEARCH: não há (quick task). Checkpoints dos hooks do planeamento: api-coverage não se aplica (nenhuma API externa nova; o detetor corre sobre este plano), assumption-delta não tem secção de fase para ler (quick task), schema-gate sem ficheiros de ORM, security com `<threat_model>` (ASVS 1, bloqueio em high).

<output>
Create `.planning/quick/261023-lee-corrigir-avisos-cr-06-wr-12-wr-13-wr-07-/261023-lee-SUMMARY.md` when done. Incluir: as contagens de testes por tarefa; os desvios em relação aos fixes sugeridos no 01-REVIEW.md (regra -m/-n em vez de três pares, "-xteis", unidade só a seguir a um número, troços seguidos e letra antes do número no SIZE), com a guarda que prova cada um; as Limitações conhecidas acima; e uma nota de que o WR-07 sai do `deferred:` da Phase 3 para o caso AxB/AxBxC na pesquisa, para a próxima re-revisão atualizar o 01-REVIEW.md e o 01-VERIFICATION.md.
</output>
