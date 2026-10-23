---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
reviewed: 2026-10-23T23:07:17Z
depth: standard
review_kind: incremental
diff_base: b7dd488c52dc378fb171b85f766215bbbf116ed8
files_reviewed: 8
files_reviewed_list:
  - src/strata/search.py
  - src/strata/stores/allmat.py
  - src/strata/stores/bricomarche.py
  - src/strata/stores/obras360.py
  - src/strata/words.py
  - tests/test_allmat.py
  - tests/test_obras360.py
  - tests/test_search.py
findings:
  critical: 0
  warning: 11
  info: 15
  total: 26
status: issues_found
---

# Phase 1: Code Review Report (re-revisão depois do 01-12)

**Reviewed:** 2026-10-23T23:07:17Z
**Depth:** standard (incremental, diff `b7dd488..HEAD`)
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Revi o diff do 01-12: o `rank=item.product` na pesquisa alargada (Bricomarché, Obras 360 e Allmat), as medidas sem ordem com pares e "×" = "x" (WR-14), o "x" em `STOP` e fora da alargada (WR-15) e o cabeçalho "1.ª pesquisa:" (WR-16). `uv run python -m pytest -q` → 222 passed. `money.py`, `text.py`, `fetch.py`, `sheet.py`, `models.py` e `report.py` não mudaram desde `b7dd488`. Os achados que vivem nesses ficheiros passam sem nova análise.

**O que confirmei no `rank`.** Os três adaptadores e a loja falsa de `tests/test_search.py` aceitam `rank=None`. Nenhum outro sítio chama `store.search` (grep). A 1.ª pesquisa continua sem `rank` (`search.py:23`). Na alargada, a loja recebe `b` e o `rank` só entra numa chave de ordenação antes de um corte que já existia (K=10, K=20, `MAX_BOX_PAGES=10`), por isso não há pedidos a mais. Os testes contam os pedidos: 10 variações, 20 detalhes, 10 páginas. Sem `rank`, a ordem não muda: na Bricomarché e na Allmat, as linhas já passaram por `title_matches(query, …)`, por isso empatam todas na contagem e decide o preço. Na Obras 360, `need = words(query)` é o mesmo de antes. O dinheiro não foi tocado: nenhuma linha do diff mexe em `Decimal`, `from_minor` ou `_price`.

**Estado dos achados que o 01-12 tinha como alvo**

| ID | Estado | Prova |
|----|--------|-------|
| WR-14 | Corrigido, com um alargamento novo (WR-18) | `tests/test_search.py::test_title_matches`: `("pavimento 120x60", "Pavimento 60x120", True)`, `("azulejo 30x30", "Azulejo 30×30 cm", True)`, `("placa 1250x2500x12mm", "Placa OSB 2500x1250x12mm", True)`, `("azulejo 30 x 30", "Azulejo 30x30", True)`. As guardas `("azulejo 30x30", "Azulejo 30x60", False)` e `("tubo 20x20", "Tubo Quadrado 20x40x1,5", False)` continuam verdes. Corri à mão "60x60" contra "60x120": `False`. |
| WR-15 | Corrigido | `tests/test_search.py::test_broadened`: `("tela 1 m x 25 m", "tela")`, `("osb 12 mm x 2500 x 1250", "osb")`, `("tela 1 m × 25 m", "tela")`; a guarda `("metro articulado 2m", "metro articulado")` continua verde. |
| WR-16 | Corrigido | `test_tudo_escondido_com_medidas_tenta_a_alargada` e `test_tudo_escondido_alargada_com_ofertas_que_batem`: o cabeçalho diz "1.ª pesquisa: 5 escondidas pelo filtro de título com 'OSB 12mm'" e a linha "+1 ofertas escondidas: título sem 'OSB 12mm'" fica separada. As duas contagens já dizem a que pesquisa pertencem. |
| WR-17 | Corrigido, com um efeito lateral novo (WR-19) | Bricomarché: `tests/test_search.py::test_alargada_expande_o_pai_com_o_produto_da_linha` (a placa 60X120, a mais cara de 13, entra nos 10 expandidos e é a única mostrada; `store.ranks == [None, "OSB 12mm"]` em `test_pesquisa_alargada_quando_a_loja_da_zero`). Obras 360: `tests/test_obras360.py::test_rank_poe_o_pai_do_produto_da_linha_a_frente_do_corte`. Allmat: `tests/test_allmat.py::test_rank_le_primeiro_as_caixas_do_produto_da_linha`. Ao vivo (01-12-SUMMARY), "pavimento 60x120" mostra na Bricomarché as duas placas 60X120 a 34,55 €. A lacuna G-01-5 do `01-VERIFICATION.md` (`gaps:`) pode fechar. |

**Já corrigidos em revisões anteriores:** CR-04, CR-05, CR-06, WR-07, WR-10, WR-12, WR-13 e IN-08 (ver o `01-REVIEW-DISPOSITION.md`). Com esta revisão juntam-se WR-14, WR-15, WR-16 e WR-17. Não contam nos totais.

**Achados que passam sem mudança.** WR-02 a WR-06, WR-09, IN-01 a IN-07, IN-09, IN-10, IN-12, IN-13 e IN-15 continuam abertos. WR-08, WR-11, IN-11 e IN-14 continuam abertos e adiados para a Phase 3 (bloco `deferred:` do `01-VERIFICATION.md`). Contam nos totais porque o defeito continua no código. Só atualizei as linhas citadas onde o diff as deslocou (`words.py` ganhou um `import`; `search.py` ganhou uma linha de comentário).

**Problemas novos.** Nenhum BLOCKER. Três WARNINGs:
1. Os pares de `combinations(p, 2)` juntam a 1.ª e a última parte de uma medida de 3: "tubo 20x2" passa a bater em "Tubo Retangular 20x40x2" e "caixa 20x40" em "Caixa 20x30x40" (WR-18).
2. A Allmat e a Bricomarché ordenam pelo número de palavras do `rank` em comum. Quando nenhuma linha bate o produto inteiro, um "60" solto chega para passar à frente de caixas mais baratas, que perdem a área e caem para "não convertível" (WR-19).
3. Na Bricomarché, num empate de preço, um pai esgotado em todas as lojas aparece antes de um com stock. É o caso da Siena/Casablanca da corrida ao vivo (WR-20, vem do 01-10).

Há ainda uma nota nova (IN-16).

## Narrative Findings (AI reviewer)

## Warnings

### WR-02: `content_from_title` lê o primeiro número com unidade, por isso packs e especificações dão €/kg e €/L errados — ABERTO

**File:** `src/strata/money.py:22-32` (usado em `src/strata/stores/allmat.py:89` e `src/strata/stores/bricomarche.py:84`)
**Issue:** passa sem mudança. "2x25kg" → 25 kg, "6 x 1L" → 1 L, "150 kg" de carga lido como conteúdo. O €/kg inventado decide a ordem (D-03).
**Fix:** recusar o conteúdo quando há `\d\s*x\s*\d` (ou multiplicar N×M) e marcar "conteúdo lido do título".

### WR-03: "1.000" (mil, à portuguesa) é lido como quantidade 1 — ABERTO

**File:** `src/strata/text.py:34`, `src/strata/text.py:44`
**Issue:** passa sem mudança. `parse_line("cimento 1.000 un")` → `qty=1.000`, sem aviso.
**Fix:** `re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", s)` → separador de milhares, ou recusar com motivo. Testar "1.000", "1.000,5", "2.5" e "2,5".

### WR-04: Allmat cai inteira com `InvalidOperation` se um produto vier com `price: ""` — ABERTO

**File:** `src/strata/stores/allmat.py:81`
**Issue:** passa sem mudança. `from_minor("")` lança `InvalidOperation` e a loja inteira fica "erro".
**Fix:** a mesma guarda do `_minor` da Bricomarché (`value in (None, "")` → sem preço).

### WR-05: Uma página de caixa bloqueada deita fora todas as ofertas da Allmat — ABERTO

**File:** `src/strata/stores/allmat.py:115-122`, `src/strata/stores/allmat.py:144-148`
**Issue:** passa sem mudança (as linhas do `gather` passaram de 143-147 para 144-148). Um `StoreBlocked`/`StoreTimeout` numa página de caixa (leitura opcional) põe a loja inteira como "bloqueada" e perdem-se as ofertas da API.
**Fix:** apanhar `(StoreError, StoreBlocked, StoreTimeout)` em `_read_box`, deixar nota na oferta e uma nota na loja se todas falharem.

### WR-06: Obras 360 usa `total_products` como `raw`: se o campo faltar, os produtos lidos passam a "sem resultados" — ABERTO

**File:** `src/strata/stores/obras360.py:39`, `src/strata/stores/obras360.py:112`, `src/strata/stores/obras360.py:121`, `src/strata/stores/obras360.py:153`
**Issue:** passa sem mudança. `raw` conta SKUs e `hidden` conta pais e variantes, por isso mistura três unidades.
**Fix:** `raw=max(total, len(products))`, e decidir "há mais" com `len(rows) == PER_PAGE`.

### WR-08: O género junta produtos diferentes: barra/barro, banco/banca, tampo/tampa, lixa/lixo — ABERTO, adiado para a Phase 3

**File:** `src/strata/words.py:45`
**Issue:** passa sem mudança (a linha do género passou de 44 para 45). Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC2: exato/parecido/outro).
**Fix:** o da revisão anterior: só igualar o género a partir da 2.ª palavra da pesquisa.

### WR-09: Número sem unidade na pesquisa nunca bate num número com unidade no título — ABERTO

**File:** `src/strata/words.py:16`, `src/strata/words.py:63-65`
**Issue:** passa sem mudança (linhas deslocadas). `("tubo pvc 32", "Tubo PVC 32mm")` e `("parafuso 4x40", "Parafuso 4x40mm")` → `False`. Com o WR-14 corrigido aparece um caso novo da mesma família: `title_matches("placa 2500x12", "Placa OSB 2500x1250x12mm")` → `False`, porque a pesquisa exige o "12" solto e o título só tem "12mm".
**Fix:** do lado do título, juntar também o número sem a unidade (`tw |= {m[0] for w in tw if (m := re.match(r"\d+(?:[.,]\d+)?", w))}`). Juntar `("tubo pvc 32", "Tubo PVC 32mm", True)` e mudar o caso `("parafuso 4x40", "Parafuso 4x40mm", False)` para `True`.

### WR-11: Uma gama no nome do pai ("9-30MM") faz "osb 30mm" mostrar as 7 espessuras, com a de 9 mm em 1.º — ABERTO, adiado para a Phase 3

**File:** `src/strata/stores/obras360.py:150-151`
**Issue:** passa sem mudança. Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC1/SC2; `shortcut:` no código, aceite em T-01-36).
**Fix:** o da revisão anterior: exigir na designação da variante as palavras que a pesquisa solta não tem.

### WR-14: A medida inteira contava a ordem e ignorava o "×" — CORRIGIDO (alargamento novo no WR-18)

**File:** `src/strata/words.py:53-57`
**Issue:** `plain(s).replace("×", "x")` e as partes ordenadas antes de juntar resolvem os quatro casos da revisão anterior. Prova na tabela do topo (`test_title_matches`). "20x20" contra "20x40x1,5", "30x30" contra "30x60" e "60x60" contra "60x120" continuam `False`: um par só aparece se as duas partes existirem na mesma medida do título, e "60x120" não tem dois "60".
**Fix:** nenhum aqui. Os pares não seguidos trazem um alargamento novo: ver o WR-18.

### WR-15: A alargada guardava o "x" depois de uma unidade — CORRIGIDO

**File:** `src/strata/words.py:76-78`, `src/strata/words.py:27`
**Issue:** `norm(t) not in ("x", "×")` tira sempre o "x" solto, em maiúscula ou minúscula, e o `STOP` tira-o também de `words()`, por isso "azulejo 30 x 30" já não exige um token "x" no título. Prova na tabela do topo (`test_broadened`). Verifiquei à mão `broadened("tubo 20 X 20")` → `"tubo"` e `broadened("kit x2")` → `"kit"` (o "x2" sai por ter dígito, como antes). O "x" em `STOP` não interfere com `DIMS`, `SIZE` nem `CLASS`: os três trabalham sobre o texto antes do `TOKEN`, e o `STOP` só filtra tokens inteiros iguais a "x".
**Fix:** nenhum aqui. Ver o IN-16 para o caso raro de um "X" que é nome de produto.

### WR-16: No ramo "tudo escondido", as duas contagens não diziam a que pesquisa pertenciam — CORRIGIDO

**File:** `src/strata/search.py:64-65`
**Issue:** o cabeçalho passou a "1.ª pesquisa: N escondidas pelo filtro de título com '<produto>'". A linha `wide_only` do report não mudou, e as duas frases já não se confundem. Prova na tabela do topo.
**Fix:** nenhum.

### WR-17: Os cortes K escolhiam os pais pela pesquisa alargada — CORRIGIDO (efeito lateral novo no WR-19)

**File:** `src/strata/search.py:28`, `src/strata/stores/bricomarche.py:128-129`, `src/strata/stores/obras360.py:129-131`, `src/strata/stores/allmat.py:141-142`
**Issue:** a alargada passa `rank=item.product` e cada adaptador ordena por `-len(words(rank or query) & words(nome))` antes do corte. Prova na tabela do topo. Na Obras 360, quando a medida só existe na designação da variante, os pais continuam empatados nas palavras soltas e decide o preço. É a mesma regra da 1.ª pesquisa (CR-04/CR-06), por isso não é regressão.
**Fix:** nenhum aqui. A contagem de palavras em comum também decide quando nenhuma linha bate o produto inteiro: ver o WR-19.

### WR-18: Os pares de `combinations` juntam a 1.ª e a última parte de uma medida de 3: "tubo 20x2" bate em "Tubo Retangular 20x40x2" (novo, 01-12)

**File:** `src/strata/words.py:56-57`
**Issue:** para a placa permutada ("1250x2500x12" contra "2500x1250x12") bater, `words()` passou a juntar, dos dois lados, todos os pares de partes, e não só os troços seguidos. Mas `title_matches` é um teste de subconjunto. Basta que um par da pesquisa exista em qualquer posição de uma medida do título. Corri o código de HEAD:

```
'tubo 20x2'    'Tubo Retangular 20x40x2'   True   (antes do 01-12: False)
'caixa 20x40'  'Caixa 20x30x40'            True   (antes do 01-12: False)
'tubo 20x20'   'Tubo Quadrado 20x40x1,5'   False  (guarda do WR-07, continua bem)
'azulejo 30x30' 'Azulejo 30x60'            False
```

`words("Tubo Retangular 20x40x2")` dá `2x20` (par não seguido), por isso um tubo redondo 20×2 (diâmetro × parede) e um retangular 20×40×2 passam a ser o mesmo produto para o filtro D-15 e para o passo final do 01-11. O retangular pode então aparecer como a oferta mais barata da linha, sem nada que o distinga além do título. Antes do 01-12, a ordem decidia ao acaso: "40x20x2" já batia (o troço "20x2" era seguido) e "20x40x2" não. Os pares tornaram o alargamento sistemático. Os casos que a revisão pedia para vigiar ("20x20"/"20x40x1,5", "30x30"/"30x60", "60x60"/"60x120") continuam `False`, porque nenhum tem a parte repetida no título.
**Fix:** a medida da pesquisa compara-se inteira (ordenada) e o título dá os troços seguidos ordenados. Assim, a permutação de 3 partes bate sem precisar de pares:

```python
def words(s, whole_sizes=False) -> set[str]:
    ...
    if whole_sizes:  # pesquisa: a medida inteira, com as partes ordenadas
        sizes = {"x".join(sorted(p)) for p in parts}
    else:            # título (e rank): cada troço seguido, com as partes ordenadas
        sizes = {"x".join(sorted(p[i:j])) for p in parts for i in range(len(p)) for j in range(i + 2, len(p) + 1)}
    ...

def title_matches(query: str, title: str) -> bool:
    return words(query, whole_sizes=True) <= words(title)
```

"1250x2500x12" dá `12x1250x2500` dos dois lados; "30x30" continua a bater em "30x30x0,8" (troço seguido). Tirar o `from itertools import combinations`. Juntar a `test_title_matches` `("tubo 20x2", "Tubo Retangular 20x40x2", False)` e `("caixa 20x40", "Caixa 20x30x40", False)`. Em alternativa, registar o caso no `deferred:` junto do WR-08 (Phase 3, exato/parecido), mas a correção acima é pequena e fecha-o já.

### WR-19: Quando nenhuma linha bate o produto inteiro, um número solto do `rank` empurra caixas mais baratas para fora das 10 páginas, e elas perdem a área (novo, 01-12)

**File:** `src/strata/stores/allmat.py:141-142`, `src/strata/stores/bricomarche.py:128-129`
**Issue:** a chave é `-len(need & words(título))`, uma contagem de palavras em comum. Com "pavimento 60x120", `need = {pavimento, 60, 120, 120x60}`. Fiz a conta:

```
1  STATUARIO PAVIMENTO 45X45 BRILHO
2  PAVIMENTO 60X60 GREY            (o "60" solto conta)
2  PAVIMENTO 120X20 MADEIRA        (o "120" solto conta)
4  PAVIMENTO 60X120 RETIFICADO
```

Quando há um 60x120, ele passa à frente e está certo: é o WR-17. Quando não há nenhum (foi o caso da Allmat na corrida ao vivo do 01-12), a ordem fica decidida por números soltos sem significado. Na Allmat todas as ofertas da alargada são mostradas, e só as 10 primeiras caixas têm a área lida. Uma caixa mais barata sem "60" nem "120" fica fora das 10, mostra "área da caixa não lida (limite de 10 páginas por pesquisa)" e cai para o fim como "não convertível para m²", atrás de caixas mais caras por m². Reproduzi com o `FakeFetcher` de `tests/conftest.py` e `search_store`: 1 caixa "STATUARIO PAVIMENTO 45X45" à frente na loja e 10 "PAVIMENTO 60X60" ao mesmo preço. Antes do 01-12, a 45X45 era a 1.ª página lida. Agora fica sem área e em último. Não esconde nenhuma oferta, mas a ordem por €/m² (D-03) deixa de ser a do preço. Na Bricomarché passa-se o mesmo com o corte K=10: sem pai que bata o produto inteiro, expandem-se os pais com "60" ou "120" soltos em vez dos 10 mais baratos, e os outros vão para "+N produtos não expandidos".
**Fix:** nestas duas lojas, o nome do pai (ou da caixa) é o título final, por isso basta pôr à frente os que batem o produto inteiro e, de resto, manter a ordem pelo preço de antes do 01-12:

```python
# allmat.search
boxes.sort(key=lambda b: (bool(rank) and not title_matches(rank, b[1].title), b[1].price))
# bricomarche.search
keyed.sort(key=lambda t: (bool(rank) and not title_matches(rank, html.unescape(t[1].get("name") or "")), t[0]))
```

Os testes de rank do 01-12 continuam verdes (o 60X120 bate o produto inteiro). Tirar o `words` dos imports das duas lojas. A Obras 360 fica com a contagem, porque lá a medida pode estar só na variante (CR-06). Juntar um teste na Allmat: alargada sem nenhuma caixa que bata o `rank`, 11 caixas, e a mais barata tem de ter a área lida.

### WR-20: Bricomarché: num empate de preço, um pai esgotado em todas as lojas aparece antes de um com stock (Siena/Casablanca ao vivo; vem do 01-10)

**File:** `src/strata/stores/bricomarche.py:73-83`, `src/strata/stores/bricomarche.py:133-143`, `src/strata/search.py:59`
**Issue:** na corrida ao vivo do 01-12, "PAVIMENTO CERÂMICO SIENA HEKLA 60X120" (Esgotado em todas as lojas físicas) aparece em 1.º e a "Casablanca Mate 60X120", ao mesmo preço (34,55 €, 23,99 €/m²) e com 3 em stock, em 2.º. Causa: `offer_from` cai para `low` quando nenhuma loja tem stock (RES-02), e a oferta fica sem nenhuma marca de "sem stock" que a ordenação possa ler. Depois, o `keyed.sort` de `search_store` é estável e só olha para o preço unitário, por isso o empate fica pela ordem dos pais (rank e depois preço do pai, também empatados). O 01-10 registou o caso geral como limitação ("um pai sem stock em nenhuma loja ordena pelo preço esgotado"). O empate é a forma mais barata de o resolver, e foi a que apareceu ao vivo. O texto "Esgotado" está à vista, por isso nada é escondido. Mesmo assim, a 1.ª oferta da linha é uma que não se pode comprar, quando há outra igual que se pode. Classifico como WARNING e não como BLOCKER: o preço mostrado é verdadeiro e o stock aparece ao lado.
**Fix:** desempatar pelo stock dentro do adaptador. A ordenação de `search_store` é estável, por isso o preço continua a mandar e só os empates mudam:

```python
# bricomarche.search, no ciclo
if (o := offer_from(p, rows)) is None:
    no_price += 1
else:
    offers.append((not any(has_stock(r) for r in _valid(rows)), o))
...
offers = [o for _, o in sorted(offers, key=lambda t: t[0])]  # estável: sem stock em lado nenhum vai para o fim dos empates
```

Juntar um teste com dois pais ao mesmo preço, o 1.º esgotado em todas as lojas: a oferta com stock tem de sair em 1.º em `search_store`. Mudar o caso geral (um esgotado mais barato à frente de um com stock mais caro) é decisão de produto (RES-02 pede que o mais barato nunca suma) e fica fora deste achado.

## Info

### IN-01: Texto colado "Tinta branca 15L" ou "Tubo 3m" perde a medida sem aviso — ABERTO

**File:** `src/strata/text.py:53-55`
**Issue:** passa sem mudança.
**Fix:** `warns.append(f"'{tok}' lido como quantidade e unidade")` no ramo `GLUED`.

### IN-02: `broadened` deita fora tokens com hífen inteiros — ABERTO

**File:** `src/strata/words.py:72-79`
**Issue:** passa sem mudança (linhas deslocadas). `broadened("OSB-12mm")` → `None` (o token tem dígito e sai inteiro), e a Obras 360 escolhe os pais com a pesquisa completa (`loose = query`).
**Fix:** `re.split(r"[\s-]+", query)` antes de filtrar.

### IN-03: Fórmulas sem valor guardado aparecem como "Qty vazia" — ABERTO

**File:** `src/strata/sheet.py:57`, `src/strata/sheet.py:91-92`
**Issue:** passa sem mudança.
**Fix:** distinguir "fórmula sem valor calculado".

### IN-04: `write_template` deixa um ficheiro parcial se a gravação falhar — ABERTO

**File:** `src/strata/sheet.py:125-126`
**Issue:** passa sem mudança.
**Fix:** `path.unlink(missing_ok=True)` no `except` e relançar.

### IN-05: HTTP 503 é sempre classificado como "bloqueada" — ABERTO

**File:** `src/strata/fetch.py:82`
**Issue:** passa sem mudança.
**Fix:** só o 503 com `cf-mitigated` ou com marcador de desafio conta como bloqueio.

### IN-06: Dois `CONTENT_UNITS` com significados diferentes — ABERTO

**File:** `src/strata/search.py:80`, `src/strata/money.py:23`
**Issue:** passa sem mudança (a linha passou de 79 para 80).
**Fix:** renomear o de `search.py` para `VALID_CONTENT_UNITS`.

### IN-07: "12,0 mm" não bate em "12mm" (resto do CR-03, adiado pelo 01-08) — ABERTO

**File:** `src/strata/words.py:16`
**Issue:** passa sem mudança. `title_matches("osb 12mm", "OSB 12,0 mm")` → `False`.
**Fix:** antes do `JOIN`, `re.sub(r"(\d)[.,]0+\b", r"\1", s)`.

### IN-09: A alargada deita fora as notas da 1.ª pesquisa e, na Obras 360, pede os mesmos detalhes duas vezes — ABERTO

**File:** `src/strata/search.py:28-34`, `src/strata/stores/obras360.py:132-135`
**Issue:** passa sem mudança (linhas deslocadas).
**Fix:** `wide.notes[:0] = [f"1.ª pesquisa: {n}" for n in found.notes]` antes de `found = wide`. Na Obras 360, guardar os detalhes em `fetch.cache` por `product_id`.

### IN-10: Assimetrias de tokenização: "ip65"/"IP 65", "e27"/"E 27", unidade solta depois de decimal — ABERTO

**File:** `src/strata/words.py:15`, `src/strata/words.py:17`
**Issue:** passa sem mudança (linhas deslocadas).
**Fix:** o da revisão anterior (`TOKEN` com a unidade colada ao decimal, `CLASS` sem as unidades, juntar letra+número com espaço).

### IN-11: A tabela `PLURAL` e o limite de 2 letras trazem colisões: cais/cal, mais/mal, dois/dol, abs/ab, eps/ep — ABERTO, adiado para a Phase 3

**File:** `src/strata/words.py:30-31`, `src/strata/words.py:37`
**Issue:** passa sem mudança (linhas deslocadas). Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC2; aceite em T-01-40).
**Fix:** guardas `False` com uma tabela de exceções em `_stem`, ou decidir na Phase 3 com o exato/parecido.

### IN-12: Obras 360 diz "0 ofertas mostradas de N resultados da loja" sem nota quando a lista vem vazia com `total_products > 0` — ABERTO

**File:** `src/strata/search.py:61-63`, `src/strata/stores/obras360.py:118-122`
**Issue:** passa sem mudança (linhas deslocadas).
**Fix:** em `obras360.search`, `if total and not products: notes.append(f"a loja indica {total} resultados mas a lista veio vazia")`. Ou resolver junto com o WR-06.

### IN-13: Abreviaturas de unidade ainda fora: "mts", "mt", "kgs"; "unidades" só é tratado na alargada — ABERTO

**File:** `src/strata/words.py:12-14`, `src/strata/words.py:18`
**Issue:** passa sem mudança (linhas deslocadas). `title_matches("tubo 3 mts", "Tubo 3m")` → `False`; `broadened("tubo 3 mts")` → `"tubo mts"`.
**Fix:** juntar a `UNIT_WORDS` `"mt": "m", "mts": "m", "kgs": "kg", "unidade": "un", "unidades": "un"` (com `un` na alternância do `JOIN`). Juntar `("tubo 3 mts", "Tubo 3m", True)` e `("tubo 3 mts", "tubo")`.

### IN-14: A regra "-m final = -n" junta pares novos: tom/tona, som/sono, sim/sino, bom/bono, fim/fino — ABERTO, adiado para a Phase 3

**File:** `src/strata/words.py:43-44`
**Issue:** passa sem mudança (linhas deslocadas). Adiado junto com o WR-08 no `deferred:` do `01-VERIFICATION.md`.
**Fix:** guardas `False` com exceções em `_stem` se algum aparecer ao vivo; de resto, a Phase 3 separa com o exato/parecido.

### IN-15: O 01-10 chama "sem stock" ao que é stock desconhecido ou por encomenda, e não olha para a quantidade pedida — ABERTO

**File:** `src/strata/stores/bricomarche.py:57-64`, `src/strata/stores/bricomarche.py:78-83`
**Issue:** passa sem mudança. `has_stock` devolve `False` quando falta `stock_availability` ou quando a classe é `available-on-backorder`. Se o WR-20 for corrigido com `has_stock`, esses pais também passam para o fim dos empates. Convém decidir as duas coisas juntas.
**Fix:** trocar a frase da nota para "mais barata (sem stock confirmado)" quando `stock_availability` não traz texto. A comparação com a quantidade fica para a fase do custo total.

### IN-16: O "x" em `STOP` também apaga um "X" que é nome de produto; `UNIT_TOKENS` ainda tem o "x" (novo, 01-12)

**File:** `src/strata/words.py:27`, `src/strata/words.py:18`, `src/strata/words.py:77`
**Issue:** com o "x" em `STOP`, "perfil x" passa a ser só `{perfi}` e bate em "Perfil U", "Perfil T" e "Perfil L". Antes do 01-12 exigia o token "x". O mesmo com "cruzeta x" e "junta x". É raro numa lista de obra, e o título fica à vista. Também ficou código morto: o "x" em `UNIT_TOKENS` (linha 18) já não decide nada, porque `broadened` tira o "x" antes, na linha 77, sem olhar para o token anterior.
**Fix:** tirar `"x"` de `UNIT_TOKENS`. O "X" de produto fica para a Phase 3 (exato/parecido). Tirar o "x" do `STOP` traria de volta o WR-15 do lado do título ("tela 1 m x 25 m" voltaria a exigir um token "x").

---

_Reviewed: 2026-10-23T23:07:17Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard (incremental)_
