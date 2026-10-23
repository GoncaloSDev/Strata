---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
reviewed: 2026-10-23T11:40:43Z
depth: standard
review_kind: incremental
diff_base: cc4fb5cf4f3d9b59f759acc6bf1936bb702881ac
files_reviewed: 5
files_reviewed_list:
  - src/strata/search.py
  - src/strata/stores/obras360.py
  - src/strata/words.py
  - tests/test_obras360.py
  - tests/test_search.py
findings:
  critical: 1
  warning: 11
  info: 11
  total: 23
status: issues_found
---

# Phase 1: Code Review Report (re-revisão depois do 01-09)

**Reviewed:** 2026-10-23T11:40:43Z
**Depth:** standard (incremental, diff `cc4fb5c..HEAD`)
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Revisto o diff do plano 01-09: a tabela `PLURAL` em `_stem` e o limite de 2 letras, `UNIT_TOKENS` com os sinónimos de litro, a nova chave do corte K=20 na Obras 360 e o ramo `if not found.offers` em `search_store`. A suite passa: `uv run python -m pytest -q` → 177 passed. `money.py`, `text.py`, `allmat.py`, `bricomarche.py`, `fetch.py`, `sheet.py` e `report.py` não mudaram desde `cc4fb5c`. Os achados que vivem nesses ficheiros passam sem nova análise; só as linhas citadas foram atualizadas onde o diff as deslocou.

O dinheiro não foi tocado. A chave nova do corte (`not title_matches(...)`, `_list_price(p) is None`, `_list_price(p) or 0`) compara `bool` e `Decimal`/`0` e não converte nada; `chosen = kept[:K]` continua a limitar os pedidos de detalhe a 20. O cabeçalho do WR-10 só aparece com `hidden == 0`, por isso nunca sai ao mesmo tempo que a linha "+N ofertas escondidas" do 01-07: não há contagem dupla.

**Estado dos achados que o 01-09 tinha como alvo**

| ID | Estado | Prova |
|----|--------|-------|
| CR-04 | Corrigido no caso citado ("parafuso m8") | `tests/test_obras360.py::test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte`: `id-m8` entre os 20 detalhes pedidos, só ofertas "Parafuso Sextavado M8". A regressão continua quando a pesquisa junta o código do pai e a medida da variante ("parafuso m8x40"): ver o CR-06, que é novo. |
| CR-05 | Corrigido nos casos citados | `tests/test_search.py::test_title_matches` (perfis, funis, canais, ferragens, lençóis, pás → `True`; lápis, jacuzzis, táxis continuam `True`) e `tests/test_obras360.py::test_perfis_mostra_o_pai_perfil`. Ficam plurais de fora: ver o WR-12. |
| WR-10 | Corrigido | `tests/test_search.py::test_zero_ofertas_sem_escondidas_nao_diz_so_ok`: "Allmat: ok — 0 ofertas mostradas de 3 resultados da loja" com a nota "3 produtos sem preço ignorados". Há um caso na Obras 360 em que o motivo não chega às notas: ver o IN-12. |
| IN-08 | Corrigido para litros | `tests/test_search.py::test_broadened` (`"tinta 15 litros"` → `"tinta"`). O mesmo defeito continua para "metros", "quilos", "unidades", "l." e "lt.": ver o WR-13. |

**Achados que passam sem mudança.** WR-02 a WR-06, WR-09, IN-01 a IN-07, IN-09 e IN-10 continuam abertos. WR-07, WR-08 e WR-11 continuam abertos e estão adiados para a Phase 3, conforme o bloco `deferred:` do `01-VERIFICATION.md`. Contam nos totais do frontmatter porque o defeito existe no código.

**Problemas novos.** Um BLOCKER: a correção do CR-04 só olha para a pesquisa completa, por isso "parafuso m8x40" volta a cortar o pai M8 e a mostrar 140 parafusos errados (CR-06, confirmado a correr o código). Dois WARNINGs: plurais que a tabela não cobre (geotêxteis, coxins, jardins) e unidades por extenso além de litros, que escondem o produto mesmo depois da alargada (WR-12, WR-13). Duas notas: colisões novas da tabela `PLURAL` (cais/cal, abs/ab) e "0 de N resultados" sem motivo na Obras 360 (IN-11, IN-12).

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-04: Obras 360 escolhe os pais sem os números e o corte K=20 por preço deita fora o produto pedido — CORRIGIDO no caso citado (resto no CR-06)

**File:** `src/strata/stores/obras360.py:127-131`
**Issue:** a chave do `kept.sort` passou a ser `(not title_matches(query, nome), preço em falta, preço)`. Os pais que batem na pesquisa completa entram primeiro no corte K=20. Confirmado em `test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte` (25 parafusos genéricos baratos e o M8 a 99 €: `id-m8` expandido, exatamente 20 pedidos de detalhe, nota "+6 produtos não expandidos"). Corri também o cenário original por `search_store`: "parafuso m8" → 7 ofertas M8, 20 pedidos, sem alargada.
**Fix:** nenhum aqui. Quando a pesquisa tem uma medida que só existe na variante, nenhum pai bate na pesquisa completa e o corte volta a ser só por preço: ver o CR-06.

### CR-05: `_stem` não tratava os plurais -ais, -is, -ens, -óis nem palavras de 3 letras — CORRIGIDO nos casos citados (resto no WR-12)

**File:** `src/strata/words.py:23-37`
**Issue:** a tabela `PLURAL` e o limite `len(w) <= 2` resolvem os casos da revisão anterior. Confirmado em `test_title_matches`: `("perfis", "Perfil alumínio")`, `("canais", "Canal")`, `("ferragens", "Ferragem")`, `("lençóis", "Lençol")` e `("pás", "Pá")` → `True`. Os guardas `("projetor ip65", "Projetor LED IP44", False)` e `("lápis", "Lápis", True)` continuam certos. Sobre a Obras 360, `test_perfis_mostra_o_pai_perfil` mostra as variantes "Perfil Montante 48mm …" e esconde só a calha (`hidden == 1`).
**Fix:** nenhum aqui. Os plurais que ficaram de fora estão no WR-12 e as colisões novas no IN-11.

### CR-06: A correção do CR-04 falha quando a pesquisa junta o código do pai e a medida da variante: "parafuso m8x40" volta a esconder o M8 (novo, 01-09)

**File:** `src/strata/stores/obras360.py:129-131`
**Issue:** a chave só põe à frente os pais que batem na pesquisa **completa**. Numa lista de obra, a forma normal de pedir um parafuso é "parafuso M8x40". O `DIMS` parte isto em `{"parafus", "m8", "40"}`, e o nome do pai "Parafuso Sextavado M8" não tem o "40", porque o comprimento está na variante. Resultado: `title_matches("parafuso m8x40", "Parafuso Sextavado M8")` → `False`. Todos os pais ficam empatados no 1.º campo, o corte volta a ser só por preço e o M8 fica de fora outra vez. Corrido com o `FakeFetcher` (os mesmos 25 parafusos genéricos e o M8 a 99 € do teste do 01-09), por `search_store`:

```
parafuso m8x40 | status ok | detail 140 escondidas pelo filtro de título com 'parafuso m8x40' | bq parafuso | offers 140 | hidden 0
   m8 expanded: False detail calls 40 notes ['+6 produtos não expandidos (limite de 20 por pesquisa)']
```

É a mesma saída do CR-04 original: 140 parafusos errados mostrados como "pesquisa alargada", 40 pedidos de detalhe e o produto pedido nunca é expandido. O mesmo acontece com `("lâmpada e27 10w", "Lâmpada LED E27")` → `False` quando a potência está na variante. O teste do 01-09 só cobre a pesquisa em que todos os tokens estão no nome do pai.
**Fix:** ordenar pelo número de palavras da pesquisa que o nome do pai tem, e só depois pelo preço. Continua a haver no máximo K pedidos de detalhe e o dinheiro não muda:
```python
need = words(query)
kept.sort(key=lambda p: (-len(need & words(p["product"]["name"])), _list_price(p) is None,
                         _list_price(p) or 0))
```
Com isto, "parafuso m8x40" dá 2 palavras ao M8 (`parafus`, `m8`) e 1 aos genéricos. "OSB 12mm" continua empatado em `osb` e decide pelo preço, como hoje. Juntar ao lado de `test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte` o mesmo cenário com a pesquisa "parafuso m8x40" (rota `LIST_URL + "parafuso+m8x40"`), e verificar que `id-m8` está entre os detalhes e que não houve alargada.

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
**Issue:** passa sem mudança. Um `StoreBlocked`/`StoreTimeout` numa página de caixa (leitura opcional) faz a loja inteira ficar "bloqueada", e perdem-se as ofertas da API.
**Fix:** apanhar `(StoreError, StoreBlocked, StoreTimeout)` em `_read_box`, deixar nota na oferta e uma nota na loja se todas falharem.

### WR-06: Obras 360 usa `total_products` como `raw`: se o campo faltar, os produtos lidos passam a "sem resultados" — ABERTO

**File:** `src/strata/stores/obras360.py:39`, `src/strata/stores/obras360.py:112`, `src/strata/stores/obras360.py:121`, `src/strata/stores/obras360.py:152`
**Issue:** passa sem mudança (só as linhas mudaram). `raw` conta SKUs e `hidden` conta pais e variantes, por isso mistura três unidades. O `report` atribui tudo a "título sem '<pesquisa completa>'", quando os pais foram escondidos pela pesquisa solta. Desde o 01-09, o mesmo `raw` aparece no cabeçalho "0 ofertas mostradas de N resultados da loja" (ver o IN-12).
**Fix:** `raw=max(total, len(products))`, e decidir "há mais" com `len(rows) == PER_PAGE`.

### WR-07: DIMS parte "30x30" em dois "30" iguais: "azulejo 30x30" bate em "30x60" — ABERTO, adiado para a Phase 3

**File:** `src/strata/words.py:8`, `src/strata/words.py:40-45`
**Issue:** passa sem mudança. `("azulejo 30x30", "Azulejo 30x60")`, `("pavimento 60x60", "Pavimento 60x120")` e `("tubo 20x20", "Tubo Quadrado 20x40x1,5")` → `True`. Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC3: o Tamanho decide se as medidas batem).
**Fix:** o da revisão anterior: guardar também o token inteiro das medidas (`DIMS_TOKEN`) ao lado das partes. Juntar `("azulejo 30x30", "Azulejo 30x60", False)` a `test_title_matches`.

### WR-08: O género junta produtos diferentes: barra/barro, banco/banca, tampo/tampa, lixa/lixo — ABERTO, adiado para a Phase 3

**File:** `src/strata/words.py:37`
**Issue:** passa sem mudança (a linha do género passou de 35 para 37). Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC2: exato/parecido/outro). O 01-09 juntou à mesma família as colisões do IN-11.
**Fix:** o da revisão anterior: só igualar o género a partir da 2.ª palavra da pesquisa.

### WR-09: Número sem unidade na pesquisa nunca bate num número com unidade no título — ABERTO

**File:** `src/strata/words.py:11-12`, `src/strata/words.py:48-50`
**Issue:** passa sem mudança. `("tubo pvc 32", "Tubo PVC 32mm")` e `("parafuso 4x40", "Parafuso 4x40mm")` → `False`.
**Fix:** do lado do título, juntar também o número sem a unidade (`tw |= {m[0] for w in tw if (m := re.match(r"\d+(?:[.,]\d+)?", w))}`). Juntar `("tubo pvc 32", "Tubo PVC 32mm", True)`.

### WR-11: Uma gama no nome do pai ("9-30MM") faz "osb 30mm" mostrar as 7 espessuras, com a de 9 mm em 1.º — ABERTO, adiado para a Phase 3

**File:** `src/strata/stores/obras360.py:149-150`
**Issue:** passa sem mudança (linhas deslocadas). Adiado no `01-VERIFICATION.md` (`deferred:`, Phase 3 SC1/SC2; `shortcut:` no código, aceite em T-01-36). A chave nova do CR-04 não muda este caso: "Placa OSB 9-30MM" bate na pesquisa completa por causa do token "30mm" da gama, por isso continua a ser expandido primeiro.
**Fix:** o da revisão anterior: exigir na designação da variante as palavras que a pesquisa solta não tem.

### WR-12: Plurais que a tabela `PLURAL` não cobre: geotêxteis, coxins, jardins (resto do CR-05, novo no 01-09)

**File:** `src/strata/words.py:24-25`
**Issue:** a tabela só trata -oes, -aes, -eis, -ais, -ois, -uis, -ens, -is, -il e -s. Ficam de fora duas famílias, confirmadas com `title_matches`:
- adjetivos em -il átono, cujo plural é -eis: `("mantas geotêxteis", "Manta Geotêxtil 150g")` → `False` (`geotextel` ≠ `geotexti`). O mesmo com `("fáceis", "Fácil")` e `("úteis", "Útil")`. A manta geotêxtil é um material de obra comum.
- plurais em -ins, -ons e -uns de palavras em -im, -om e -um: `("coxins", "Coxim borracha")`, `("jardins", "Jardim")` e `("comuns", "Comum")` → `False` (`coxin` ≠ `coxim`).

O efeito é o do CR-05: a loja tem o produto e o filtro esconde-o. Sem números na pesquisa, a alargada não corre e o preço não aparece (o cabeçalho dá a contagem).
**Fix:** juntar os pares -ins, -ons e -uns à tabela, antes de `("is", "i")`:
```python
PLURAL = (("oes", "ao"), ("aes", "ao"), ("eis", "el"), ("ais", "al"), ("ois", "ol"), ("uis", "ul"),
          ("ens", "em"), ("ins", "im"), ("ons", "om"), ("uns", "um"), ("is", "i"), ("il", "i"), ("s", ""))
```
Para o -eis átono não há regra de sufixo: depois de `plain()`, "fáceis" e "painéis" acabam os dois em "eis". A forma mais curta é uma tabela pequena de exceções antes do ciclo (`{"geotexteis": "geotexti", "texteis": "texti", "faceis": "faci", "uteis": "uti"}`), ou aceitar o resto na Phase 3. Juntar a `test_title_matches` `("coxins", "Coxim", True)`, `("jardins", "Jardim", True)` e `("mantas geotêxteis", "Manta Geotêxtil", True)`.

### WR-13: Unidades por extenso além de litros ("metros", "quilos", "unidades") escondem o produto mesmo depois da alargada (resto do IN-08, novo no 01-09)

**File:** `src/strata/words.py:9`, `src/strata/words.py:13`, `src/strata/words.py:53-57`
**Issue:** o 01-09 juntou "lts", "litro" e "litros" a `UNIT_TOKENS`, e o `LITRE` já os lia em `words()`. As outras unidades por extenso não têm nenhum dos dois. `parse_line("tubo pvc 3 metros 10 m")` guarda o produto como `"tubo pvc 3 metros"`. Depois:
- 1.ª pesquisa: `("tubo 3 metros", "Tubo 3m")` → `False` (`{"3", "metr"}` contra `{"3m"}`);
- alargada: `broadened("tubo 3 metros")` → `"tubo metros"`, que exige "metr" no título e volta a esconder "Tubo 3m".

O mesmo com `broadened("cimento 25 quilos")` → `"cimento quilos"`, `broadened("parafuso 10 unidades")` → `"parafuso unidades"`, e com a unidade seguida de ponto: `broadened("tinta 5 l.")` → `"tinta l."` (`norm("l.")` não está em `UNIT_TOKENS`). Fica "também sem ofertas com '…'" e o produto que a loja vende não aparece.
**Fix:** tratar as unidades por extenso como o `LITRE` trata os litros, nos dois sítios:
```python
UNIT_WORDS = re.compile(r"(\d)\s*(?:metros?|mts?)\b|(\d)\s*(?:quilos?|kgs)\b")  # ou uma tabela palavra -> unidade
UNIT_TOKENS = {..., "metro", "metros", "mt", "mts", "quilo", "quilos", "kgs", "unidade", "unidades", "uni"}
keep = [t for t in toks if not any(c.isdigit() for c in t) and norm(t).rstrip(".") not in UNIT_TOKENS]
```
Juntar `("tubo 3 metros", "Tubo 3m", True)` a `test_title_matches` e `("tubo 3 metros", "tubo")`, `("tinta 5 l.", "tinta")` a `test_broadened`.

## Info

### IN-01: Texto colado "Tinta branca 15L" ou "Tubo 3m" perde a medida sem aviso — ABERTO

**File:** `src/strata/text.py:53-55`
**Issue:** passa sem mudança.
**Fix:** `warns.append(f"'{tok}' lido como quantidade e unidade")` no ramo `GLUED`.

### IN-02: `broadened` deita fora tokens com hífen inteiros — ABERTO

**File:** `src/strata/words.py:53-57`
**Issue:** passa sem mudança (linhas deslocadas). `broadened("OSB-12mm")` → `None`, e a Obras 360 escolhe os pais com a pesquisa completa (`loose = query`).
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

**File:** `src/strata/search.py:73`, `src/strata/money.py:23`
**Issue:** passa sem mudança (a linha passou de 72 para 73).
**Fix:** renomear o de `search.py` para `VALID_CONTENT_UNITS`.

### IN-07: "12,0 mm" não bate em "12mm" (resto do CR-03, adiado pelo 01-08) — ABERTO

**File:** `src/strata/words.py:11-12`
**Issue:** passa sem mudança. `title_matches("osb 12mm", "OSB 12,0 mm")` → `False`.
**Fix:** antes do `JOIN`, `re.sub(r"(\d)[.,]0+\b", r"\1", s)`.

### IN-08: `broadened` não conhecia os sinónimos do LITRE: "tinta 15 litros" alargava para "tinta litros" — CORRIGIDO (resto no WR-13)

**File:** `src/strata/words.py:13`
**Issue:** `UNIT_TOKENS` tem agora "lts", "litro" e "litros". Confirmado em `test_broadened`: `("tinta 15 litros", "tinta")`.
**Fix:** nenhum aqui. As outras unidades por extenso e a unidade com ponto estão no WR-13.

### IN-09: A alargada deita fora as notas da 1.ª pesquisa e, na Obras 360, pede os mesmos detalhes duas vezes — ABERTO

**File:** `src/strata/search.py:30-32`, `src/strata/stores/obras360.py:131-134`
**Issue:** passa sem mudança. O cenário do CR-06 volta a mostrar os 40 pedidos de detalhe (20 da 1.ª pesquisa e os mesmos 20 da alargada).
**Fix:** `wide.notes[:0] = [f"1.ª pesquisa: {n}" for n in found.notes]` antes de `found = wide`. Na Obras 360, guardar os detalhes em `fetch.cache` por `product_id`.

### IN-10: Assimetrias de tokenização: "ip65"/"IP 65", "e27"/"E 27", unidade solta depois de decimal — ABERTO

**File:** `src/strata/words.py:10`, `src/strata/words.py:12`
**Issue:** passa sem mudança.
**Fix:** o da revisão anterior (`TOKEN` com a unidade colada ao decimal, `CLASS` sem as unidades, juntar letra+número com espaço).

### IN-11: A tabela `PLURAL` e o limite de 2 letras trazem colisões novas: cais/cal, mais/mal, dois/dol, abs/ab, eps/ep (novo, 01-09)

**File:** `src/strata/words.py:24-25`, `src/strata/words.py:31`
**Issue:** confirmado com `title_matches` → `True`: `("cal", "Cais")`, `("mal", "Mais")`, `("tomada dois", "Tomada Dol")`, e, com as palavras de 3 letras agora sem o "s", `("abs", "Tubo AB")` e `("eps", "Placa EP")`. EPS, XPS e ABS são siglas de materiais de obra. O impacto real é pequeno, porque o título aparece ao lado do preço, e o 01-09-SUMMARY lista cal/cais e mal/mais em Known Limitations, na família do WR-08 (Phase 3). Fica aqui para o registo de disposições.
**Fix:** juntar a `test_title_matches` guardas `False` para as colisões que se quiserem impedir (ex.: `("cal", "Cais", False)`) com uma tabela de exceções em `_stem`, ou decidir na Phase 3 com o exato/parecido, como o WR-08.

### IN-12: Obras 360 diz "0 ofertas mostradas de N resultados da loja" sem nota quando a lista vem vazia com `total_products > 0` (novo, 01-09)

**File:** `src/strata/search.py:53-56`, `src/strata/stores/obras360.py:118-122`
**Issue:** o comentário do WR-10 diz "o motivo fica nas notas". Na Obras 360, se a 1.ª página vier com `products: []` e `total_products: 5`, o ciclo pára (`if not rows: break`), a nota "mais produtos na loja não lidos" não sai (exige `products`), e o resultado é "Obras 360: ok — 0 ofertas mostradas de 5 resultados da loja" sem nenhuma nota. Não omite a falha (o "0 de 5" está à vista), mas não diz porquê. É o mesmo campo do WR-06.
**Fix:** em `obras360.search`, `if total and not products: notes.append(f"a loja indica {total} resultados mas a lista veio vazia")`. Ou resolver junto com o WR-06.

---

_Reviewed: 2026-10-23T11:40:43Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard (incremental)_
