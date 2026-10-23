---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
reviewed: 2026-10-23T19:30:00Z
depth: standard
review_kind: incremental
diff_base: 04334c557f15fdc5f5e1e1ed46c12fb30fce5c3c
files_reviewed: 10
files_reviewed_list:
  - src/strata/models.py
  - src/strata/report.py
  - src/strata/search.py
  - src/strata/stores/bricomarche.py
  - src/strata/stores/obras360.py
  - src/strata/words.py
  - tests/test_bricomarche.py
  - tests/test_e2e.py
  - tests/test_obras360.py
  - tests/test_search.py
findings:
  critical: 0
  warning: 12
  info: 14
  total: 26
status: issues_found
---

# Phase 1: Code Review Report (re-revisão depois do quick 261023-lee, 01-10 e 01-11)

**Reviewed:** 2026-10-23T19:30:00Z
**Depth:** standard (incremental, diff `04334c5..HEAD`)
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Revi o diff do quick 261023-lee (chave do corte K=20, plurais -xteis e -m/-n, unidades por extenso, regex `SIZE`), do 01-10 (`offer_from` da Bricomarché escolhe a loja com stock) e do 01-11 (passo final da pesquisa alargada, `StoreResult.wide_only` e a linha nova no report). `uv run python -m pytest -q` → 209 passed. `money.py`, `text.py`, `allmat.py`, `fetch.py` e `sheet.py` não mudaram desde `04334c5`. Os achados que vivem nesses ficheiros passam sem nova análise.

O dinheiro não foi tocado. No 01-10, `_price` continua a devolver `Decimal`. A nota só aparece com `_price(low) < _price(best)` (estritamente menor) e, como `low` é o mínimo global, a loja da nota nunca tem stock. Num empate ganha a loja com stock e não sai nota (`test_offer_from_empate_prefere_a_loja_com_stock`, com a loja sem stock à frente na lista). Sem stock em nenhuma loja, `best = low` e não sai nota (`test_offer_from_nenhuma_loja_com_stock`). No 01-11, a linha nova passa `it.product` por `clean()` e nenhuma oferta some sem contagem: as que saem vão para `wide_only` e aparecem numa linha "+N ofertas escondidas". O passo corre sobre as ofertas já lidas e não faz pedidos novos.

**Estado dos achados que o quick 261023-lee tinha como alvo**

| ID | Estado | Prova |
|----|--------|-------|
| CR-06 | Corrigido | `tests/test_obras360.py::test_pai_com_mais_palavras_da_pesquisa_passa_a_frente_do_corte`: com "parafuso m8x40", `id-m8` (o mais caro) está entre os 20 detalhes pedidos e sai a nota "+6 produtos não expandidos". A chave é `-len(words(query) & words(nome))`; "OSB 12mm" continua a decidir pelo preço. |
| WR-07 | Corrigido no caso citado, mas com uma regressão nova | `tests/test_search.py::test_title_matches`: `("azulejo 30x30", "Azulejo 30x60", False)` e `("tubo 20x20", "Tubo Quadrado 20x40x1,5", False)`. A medida inteira passou a ser comparada como texto, por isso a ordem conta e o "×" deixa de bater: ver o WR-14. Já pode sair do `deferred:` do `01-VERIFICATION.md`. |
| WR-12 | Corrigido | `test_title_matches`: `("mantas geotêxteis", "Manta Geotêxtil", True)`, `("coxins", "Coxim", True)`, `("jardins", "Jardim", True)`, com as guardas `("listéis", "Listel", True)` e `("plafons", "Plafon LED", True)`. Fáceis/úteis continuam de fora; o SUMMARY aceita isso. As colisões novas da regra -m/-n estão no IN-14. |
| WR-13 | Corrigido para metros, quilos, gramas, litros, "l." e "unidades" na alargada | `test_title_matches`: `("tubo 3 metros", "Tubo 3m", True)`, `("cimento 25 quilos", "Cimento 25kg", True)`. `test_broadened`: `("tubo 3 metros", "tubo")`, `("tinta 15 l.", "tinta")`, `("parafuso 10 unidades", "parafuso")`. A regra nova da alargada trouxe uma regressão (WR-15); ficam abreviaturas de fora (IN-13). |

**Já corrigidos em revisões anteriores:** CR-04, CR-05, WR-10 e IN-08 (ver o `01-REVIEW-DISPOSITION.md`). Não contam nos totais.

**Achados que passam sem mudança.** WR-02 a WR-06, WR-09, IN-01 a IN-07, IN-09, IN-10 e IN-12 continuam abertos. WR-08, WR-11 e IN-11 continuam abertos e adiados para a Phase 3 (bloco `deferred:` do `01-VERIFICATION.md`). Contam nos totais do frontmatter porque o defeito continua no código. Só atualizei as linhas citadas onde o diff as deslocou.

**Problemas novos.** Nenhum BLOCKER. Quatro WARNINGs:
1. A medida passou a depender da ordem: "120x60" já não bate em "60x120", e "30x30" não bate em "30×30" (WR-14, regressão do WR-07).
2. A alargada guarda o "x" quando ele vem depois de uma unidade: "tela 1 m x 25 m" → "tela x", e o "x" esconde todas as ofertas (WR-15, regressão do WR-13).
3. No ramo "tudo escondido", os mesmos produtos contam no cabeçalho e outra vez na linha `wide_only`, com o mesmo motivo (WR-16, 01-11).
4. O passo final do 01-11 corre depois dos cortes K, que escolhem pela pesquisa alargada (WR-17, limitação que o 01-11-SUMMARY regista).

Há ainda três notas (IN-13 a IN-15).

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-06: A correção do CR-04 falhava quando a pesquisa juntava o código do pai e a medida da variante ("parafuso m8x40") — CORRIGIDO

**File:** `src/strata/stores/obras360.py:129-132`
**Issue:** a chave passou a ser `(-len(need & words(nome)), preço em falta, preço)`, com `need = words(query)`. "parafuso m8x40" dá 2 palavras ao pai M8 (`parafus`, `m8`) e 1 aos genéricos, por isso o M8 entra no corte mesmo sendo o mais caro. Confirmado em `test_pai_com_mais_palavras_da_pesquisa_passa_a_frente_do_corte`: exatamente 20 pedidos de detalhe, com `id-m8` entre eles. O `SIZE` não lê "m8x40" (o lookbehind `(?<![a-z\d.,])` corta a rosca), por isso `need` não ganha um "8x40" que nenhum pai teria.
**Fix:** nenhum aqui. Com a designação "40 MM", o WR-09 continua a esconder as variantes; o SUMMARY do quick regista isso.

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

**File:** `src/strata/stores/allmat.py:115-122`, `src/strata/stores/allmat.py:143-147`
**Issue:** passa sem mudança. Um `StoreBlocked`/`StoreTimeout` numa página de caixa (leitura opcional) põe a loja inteira como "bloqueada" e perdem-se as ofertas da API.
**Fix:** apanhar `(StoreError, StoreBlocked, StoreTimeout)` em `_read_box`, deixar nota na oferta e uma nota na loja se todas falharem.

### WR-06: Obras 360 usa `total_products` como `raw`: se o campo faltar, os produtos lidos passam a "sem resultados" — ABERTO

**File:** `src/strata/stores/obras360.py:39`, `src/strata/stores/obras360.py:112`, `src/strata/stores/obras360.py:121`, `src/strata/stores/obras360.py:153`
**Issue:** passa sem mudança (a última linha passou de 152 para 153). `raw` conta SKUs e `hidden` conta pais e variantes, por isso mistura três unidades.
**Fix:** `raw=max(total, len(products))`, e decidir "há mais" com `len(rows) == PER_PAGE`.

### WR-07: DIMS partia "30x30" em dois "30" iguais: "azulejo 30x30" batia em "30x60" — CORRIGIDO (regressão nova no WR-14)

**File:** `src/strata/words.py:10`, `src/strata/words.py:51-53`
**Issue:** o `SIZE` guarda cada troço seguido da medida ("20x20x1,5" → "20x20", "20x1,5", "20x20x1,5") ao lado das partes soltas. Confirmado em `test_title_matches`: `("azulejo 30x30", "Azulejo 30x60", False)`, `("tubo 20x20", "Tubo Quadrado 20x40x1,5", False)`, `("azulejo 30x30", "Azulejo 30 x 30 cm", True)` e `("parafuso m12x40", "Parafuso Sextavado M12 — 40", True)`. O lookbehind `(?<![a-z\d.,])` impede que o regex comece a meio de "m12x40". Pode sair do `deferred:` do `01-VERIFICATION.md`.
**Fix:** nenhum aqui. A comparação como texto ficou sensível à ordem e ao "×": ver o WR-14.

### WR-08: O género junta produtos diferentes: barra/barro, banco/banca, tampo/tampa, lixa/lixo — ABERTO, adiado para a Phase 3

**File:** `src/strata/words.py:44`
**Issue:** passa sem mudança (a linha do género passou de 37 para 44). Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC2: exato/parecido/outro). A regra -m/-n do quick junta mais colisões a esta família (IN-14).
**Fix:** o da revisão anterior: só igualar o género a partir da 2.ª palavra da pesquisa.

### WR-09: Número sem unidade na pesquisa nunca bate num número com unidade no título — ABERTO

**File:** `src/strata/words.py:15`, `src/strata/words.py:59-61`
**Issue:** passa sem mudança. `("tubo pvc 32", "Tubo PVC 32mm")` e `("parafuso 4x40", "Parafuso 4x40mm")` → `False`. O quick fixou o 2.º caso como `False` em `test_title_matches`, com o comentário "WR-09 (fora do âmbito)". Também limita o CR-06 ao vivo quando a designação da variante é "40 MM".
**Fix:** do lado do título, juntar também o número sem a unidade (`tw |= {m[0] for w in tw if (m := re.match(r"\d+(?:[.,]\d+)?", w))}`). Juntar `("tubo pvc 32", "Tubo PVC 32mm", True)` e mudar o caso do quick para `True`.

### WR-11: Uma gama no nome do pai ("9-30MM") faz "osb 30mm" mostrar as 7 espessuras, com a de 9 mm em 1.º — ABERTO, adiado para a Phase 3

**File:** `src/strata/stores/obras360.py:150-151`
**Issue:** passa sem mudança (linhas deslocadas). Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC1/SC2; `shortcut:` no código, aceite em T-01-36). O passo do 01-11 não muda este caso, porque a 1.ª pesquisa já mostra ofertas e a alargada não corre.
**Fix:** o da revisão anterior: exigir na designação da variante as palavras que a pesquisa solta não tem.

### WR-12: Plurais que a tabela `PLURAL` não cobria: geotêxteis, coxins, jardins — CORRIGIDO

**File:** `src/strata/words.py:29-30`, `src/strata/words.py:42-43`
**Issue:** o par `("xteis", "xti")` e a regra "-m final = -n" resolvem os casos citados. Confirmado em `test_title_matches`: geotêxteis/Geotêxtil, têxteis/Têxtil, coxins/Coxim e jardins/Jardim → `True`. Saiu o par -ens; `("ferragens", "Ferragem", True)` continua verde porque as duas formas acabam em "ferragen". Fáceis/úteis/frágeis continuam sem bater, como o SUMMARY aceita.
**Fix:** nenhum aqui. As colisões que a regra -m/-n traz estão no IN-14.

### WR-13: Unidades por extenso além de litros escondiam o produto mesmo depois da alargada — CORRIGIDO no essencial (regressão no WR-15, resto no IN-13)

**File:** `src/strata/words.py:11-13`, `src/strata/words.py:17`, `src/strata/words.py:68-74`
**Issue:** o `SPELLED` junta "3 metros" → "3m", "25 quilos" → "25kg" e "500 gramas" → "500g" em `words()`. A alternância está bem ordenada: "lt" falha no `\b` de "lts" e o regex recua para "lts", o mesmo com "metro"/"metros" e "quilo"/"quilograma(s)". A alargada tira uma unidade a seguir a um número e aceita "l.". Confirmado nos casos citados na tabela do topo.
**Fix:** nenhum aqui. A regra "só a seguir a um número" deixa passar o "x" (WR-15). "mts", "mt" e "kgs" continuam de fora (IN-13).

### WR-14: A medida inteira passou a contar a ordem e ignora o "×": "pavimento 120x60" já não bate em "Pavimento 60x120" (novo, regressão do WR-07)

**File:** `src/strata/words.py:10`, `src/strata/words.py:51-53`
**Issue:** os troços guardam-se como texto pela ordem escrita, por isso a mesma medida em ordem inversa deixa de bater. Corri o código de `04334c5` e o de HEAD lado a lado:

```
pavimento 120x60 | Pavimento 60x120          base True  now False
azulejo 30x60    | Azulejo 60x30             base True  now False
placa 1250x2500  | Placa OSB 2500x1250x12mm  base True  now False
azulejo 30x30    | Azulejo 30×30 cm          base True  now False
```

No último caso, o `SIZE` e o `DIMS` só aceitam o "x" latino. O "×" (U+00D7) não se decompõe em `plain()`, por isso o título não dá nenhum troço e a pesquisa exige "30x30". Num azulejo ou numa placa, 60x120 e 120x60 são o mesmo produto, e as lojas não escrevem sempre pela mesma ordem. Se a loja vende os dois sentidos, o mais barato com a ordem inversa fica em "+N ofertas escondidas" e o utilizador perde o preço mais baixo, que é o que a ferramenta existe para mostrar. Se todos ficarem escondidos, a alargada corre e o passo do 01-11 não encontra nenhum que bata, por isso mostra todos os "pavimento", misturados.
**Fix:** normalizar o "×" e guardar cada troço com as partes ordenadas, dos dois lados (é simétrico, por isso "20x20" continua sem bater em "20x40x1,5"):
```python
s = plain(s).replace("×", "x")
parts = ["".join(m.split()).split("x") for m in SIZE.findall(s)]
sizes = {"x".join(sorted(p[i:j])) for p in parts for i in range(len(p)) for j in range(i + 2, len(p) + 1)}
```
Juntar a `test_title_matches` `("pavimento 120x60", "Pavimento 60x120", True)` e `("azulejo 30x30", "Azulejo 30×30 cm", True)`, mantendo `("azulejo 30x30", "Azulejo 30x60", False)`.

### WR-15: A alargada guarda o "x" quando ele vem depois de uma unidade: "tela 1 m x 25 m" → "tela x", que esconde tudo (novo, regressão do WR-13)

**File:** `src/strata/words.py:72-73`
**Issue:** a regra nova só tira um token de `UNIT_TOKENS` quando o token anterior tem um dígito. Em "1 m x 25 m", o "x" vem depois de "m", que não tem dígito, por isso fica:

```
'tela 1 m x 25 m'          base 'tela'   now 'tela x'
'osb 12 mm x 2500 x 1250'  base 'osb'    now 'osb x'
'placa 2,5 m x 1,2 m'      base 'placa'  now 'placa x'
```

Depois, `title_matches("tela x", "Tela Pitonada 1x25m")` → `False`, porque o `DIMS` tira o "x" das medidas coladas e o título nunca tem o token "x". A alargada esconde todas as ofertas e sai "0 ofertas mostradas; N escondidas pelo filtro de título". A loja também recebe "tela x" como pesquisa. Antes do quick, o "x" saía sempre e a alargada era "tela".
**Fix:** o "x" nunca é palavra de produto; tirá-lo sempre, como antes:
```python
keep = [t for prev, t in zip([""] + toks, toks)
        if not _digit(t) and norm(t) != "x" and not (_digit(prev) and norm(t).rstrip(".") in UNIT_TOKENS)]
```
Juntar a `test_broadened` `("tela 1 m x 25 m", "tela")` e `("osb 12 mm x 2500 x 1250", "osb")`. A guarda `("metro articulado 2m", "metro articulado")` continua verde.

### WR-16: No ramo "tudo escondido", os mesmos produtos contam no cabeçalho e outra vez em `wide_only`, com o mesmo motivo (novo, 01-11)

**File:** `src/strata/search.py:32`, `src/strata/search.py:37-40`, `src/strata/search.py:63-64`, `src/strata/report.py:63-64`
**Issue:** quando a 1.ª pesquisa esconde tudo (ramo do 01-07/WR-01), `first_hidden` vai para o cabeçalho como "N escondidas pelo filtro de título com '<produto>'". Se a alargada devolver os mesmos produtos (o caso normal: "OSB" devolve outra vez a placa de 9 mm que "OSB 12mm" já tinha trazido), o passo do 01-11 volta a contá-los em `wide_only`, e o report escreve "+M ofertas escondidas: título sem '<produto>'". São duas contagens com o mesmo motivo e a mesma frase, sobre produtos que se repetem. Reproduzido com as ajudas de `tests/test_search.py` (1.ª pesquisa com 3 escondidas, alargada com essas 3 mais a placa de 12 mm):

```
  Allmat: ok — 3 escondidas pelo filtro de título com 'OSB 12mm' (pesquisa alargada: 'OSB')
    20,00 €  PLACA OSB 12MM
    +3 ofertas escondidas: título sem 'OSB 12mm'
```

Quem lê soma 6 escondidas, mas só há 3 produtos diferentes. `test_tudo_escondido_alargada_com_ofertas_que_batem` fixa exatamente as duas frases juntas, sem dizer que se referem a pesquisas diferentes. Não esconde nenhuma oferta, mas a contagem engana, e o PROJECT.md pede resultados que não enganem.
**Fix:** dizer no cabeçalho a que pesquisa pertence a contagem, para as duas linhas não se confundirem:
```python
elif first_hidden:
    detail = f"1.ª pesquisa: {first_hidden} escondidas pelo filtro de título com '{item.product}'"
```
Atualizar as asserções de `detail` em `tests/test_search.py`. Uma alternativa é omitir o número do cabeçalho quando `wide_only > 0`.

### WR-17: O passo final do 01-11 corre depois dos cortes K, que escolhem os pais pela pesquisa alargada (novo, 01-11; limitação registada)

**File:** `src/strata/search.py:27`, `src/strata/search.py:36-40`, `src/strata/stores/obras360.py:129-132`, `src/strata/stores/bricomarche.py:124-127`
**Issue:** na alargada, a loja recebe só `b` ("OSB"). Na Obras 360, `need = words("OSB")` deixa todos os pais empatados com 1 palavra e o corte K=20 volta a ser só pelo preço. Na Bricomarché, o corte K=10 é sempre pelo preço do pai. Se o pai que bate a pergunta completa ("Placa OSB 12 MM") for mais caro do que 10 (ou 20) pais "OSB" (colas, espumas, outras espessuras), nunca é expandido. Aí `full` fica vazio e o `search_store` mostra todas as ofertas da alargada: é o caso da cola antes da placa que o G-01-5 queria fechar. O 01-11-SUMMARY regista isto como limitação conhecida e a nota "+N produtos não expandidos" fica à vista, por isso a falha não é silenciosa. Mesmo assim, o G-01-5 só fica garantido quando a loja tem poucos pais.
**Fix:** passar o produto da linha só para ordenar, sem mudar a pesquisa à loja:
```python
wide = await store.search(b, fetch, rank=item.product)            # search.py
need = words(rank or query)                                       # obras360.search(query, fetch, rank=None)
keyed.sort(key=lambda t: (-len(words(rank or query) & words(html.unescape(t[1]["name"]))), t[0]))  # bricomarche
```
A Allmat aceita e ignora `rank`, e as lojas falsas dos testes recebem `**kw`. Juntar um teste com 11 pais "OSB" baratos e a placa de 12 mm como a mais cara: a placa tem de estar entre os expandidos e ser a única oferta mostrada.

## Info

### IN-01: Texto colado "Tinta branca 15L" ou "Tubo 3m" perde a medida sem aviso — ABERTO

**File:** `src/strata/text.py:53-55`
**Issue:** passa sem mudança.
**Fix:** `warns.append(f"'{tok}' lido como quantidade e unidade")` no ramo `GLUED`.

### IN-02: `broadened` deita fora tokens com hífen inteiros — ABERTO

**File:** `src/strata/words.py:68-74`
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

**File:** `src/strata/search.py:79`, `src/strata/money.py:23`
**Issue:** passa sem mudança (a linha passou de 73 para 79).
**Fix:** renomear o de `search.py` para `VALID_CONTENT_UNITS`.

### IN-07: "12,0 mm" não bate em "12mm" (resto do CR-03, adiado pelo 01-08) — ABERTO

**File:** `src/strata/words.py:15`
**Issue:** passa sem mudança. `title_matches("osb 12mm", "OSB 12,0 mm")` → `False`.
**Fix:** antes do `JOIN`, `re.sub(r"(\d)[.,]0+\b", r"\1", s)`.

### IN-09: A alargada deita fora as notas da 1.ª pesquisa e, na Obras 360, pede os mesmos detalhes duas vezes — ABERTO

**File:** `src/strata/search.py:27-33`, `src/strata/stores/obras360.py:132-135`
**Issue:** passa sem mudança.
**Fix:** `wide.notes[:0] = [f"1.ª pesquisa: {n}" for n in found.notes]` antes de `found = wide`. Na Obras 360, guardar os detalhes em `fetch.cache` por `product_id`.

### IN-10: Assimetrias de tokenização: "ip65"/"IP 65", "e27"/"E 27", unidade solta depois de decimal — ABERTO

**File:** `src/strata/words.py:14`, `src/strata/words.py:16`
**Issue:** passa sem mudança (linhas deslocadas).
**Fix:** o da revisão anterior (`TOKEN` com a unidade colada ao decimal, `CLASS` sem as unidades, juntar letra+número com espaço).

### IN-11: A tabela `PLURAL` e o limite de 2 letras trazem colisões: cais/cal, mais/mal, dois/dol, abs/ab, eps/ep — ABERTO, adiado para a Phase 3

**File:** `src/strata/words.py:29-30`, `src/strata/words.py:36`
**Issue:** passa sem mudança. Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC2; aceite em T-01-40).
**Fix:** guardas `False` com uma tabela de exceções em `_stem`, ou decidir na Phase 3 com o exato/parecido.

### IN-12: Obras 360 diz "0 ofertas mostradas de N resultados da loja" sem nota quando a lista vem vazia com `total_products > 0` — ABERTO

**File:** `src/strata/search.py:59-62`, `src/strata/stores/obras360.py:118-122`
**Issue:** passa sem mudança (linhas deslocadas).
**Fix:** em `obras360.search`, `if total and not products: notes.append(f"a loja indica {total} resultados mas a lista veio vazia")`. Ou resolver junto com o WR-06.

### IN-13: Abreviaturas de unidade ainda fora: "mts", "mt", "kgs"; "unidades" só é tratado na alargada (resto do WR-13, novo)

**File:** `src/strata/words.py:11-13`, `src/strata/words.py:17`
**Issue:** confirmado a correr o código:
- `title_matches("tubo 3 mts", "Tubo 3m")` → `False` e `broadened("tubo 3 mts")` → `"tubo mts"`, que volta a exigir "mt" no título. O mesmo com `broadened("cimento 25 kgs")` → `"cimento kgs"`.
- "unidades" está em `UNIT_TOKENS` mas não em `UNIT_WORDS`, por isso `title_matches("parafuso 10 unidades", "Parafuso 10 un")` → `False` na 1.ª pesquisa. A alargada "parafuso" recupera o produto, mas misturado com os outros.

O revisor anterior pedia "mt", "mts" e "kgs" no fix do WR-13. "mts" é comum em listas de obra escritas à mão.
**Fix:** juntar a `UNIT_WORDS` `"mt": "m", "mts": "m", "kgs": "kg", "unidade": "un", "unidades": "un"` (o `JOIN` precisa de `un` na alternância para "10un" bater em "10 un"). Juntar `("tubo 3 mts", "Tubo 3m", True)` e `("tubo 3 mts", "tubo")`.

### IN-14: A regra "-m final = -n" junta pares novos: tom/tona, som/sono, sim/sino, bom/bono, fim/fino (novo)

**File:** `src/strata/words.py:42-43`
**Issue:** o "-m" passa a "-n" e o género tira o "-o/-a" final, por isso as duas formas de cada par dão o mesmo stem: `_stem("tom") == _stem("tona") == "ton"`, `_stem("som") == _stem("sono") == "son"`, `_stem("fim") == _stem("fino") == "fin"`. O SUMMARY só regista fim/fino. É a família do WR-08 e do IN-11: o título fica à vista e a Phase 3 separa com o exato/parecido.
**Fix:** juntar estes pares à entrada do IN-11 no `deferred:` do `01-VERIFICATION.md`, ou pôr guardas `False` com exceções em `_stem` se algum aparecer ao vivo.

### IN-15: O 01-10 chama "sem stock" ao que é stock desconhecido ou por encomenda, e não olha para a quantidade pedida (novo)

**File:** `src/strata/stores/bricomarche.py:57-64`, `src/strata/stores/bricomarche.py:78-83`
**Issue:** `has_stock` devolve `False` quando falta `stock_availability` ou quando a classe é outra (ex.: `available-on-backorder` do WooCommerce). A nota diz então "mais barata sem stock: X em Y" de uma loja cujo stock não se sabe. Na amostra, todas as variações têm `class` `in-stock` ou `out-of-stock`, por isso o caso ainda não apareceu. A escolha também aceita qualquer stock > 0: uma loja com "3 em stock" ganha a uma mais barata sem stock, mesmo quando a linha pede 30. O texto do stock aparece ao lado, por isso nada fica escondido.
**Fix:** trocar a frase da nota para "mais barata (sem stock confirmado)" quando `stock_availability` não traz texto. A comparação com a quantidade fica para a fase do custo total.

---

_Reviewed: 2026-10-23T19:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard (incremental)_
