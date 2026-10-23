---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
reviewed: 2026-10-23T13:30:00Z
depth: standard
review_kind: incremental
diff_base: 47165c31e1697c8e02d82fcbb81d36ee65ae878d
files_reviewed: 11
files_reviewed_list:
  - src/strata/search.py
  - src/strata/stores/obras360.py
  - src/strata/words.py
  - tests/fixtures/obras360_product-details_tinta-colorite.json
  - tests/fixtures/obras360_product-details_tinta-dycrilforce.json
  - tests/fixtures/obras360_product-details_tinta-dyrup-super.json
  - tests/fixtures/obras360_product-details_tinta-dyrustar.json
  - tests/fixtures/obras360_product-list_tinta-branca.json
  - tests/test_bricomarche.py
  - tests/test_obras360.py
  - tests/test_search.py
findings:
  critical: 2
  warning: 10
  info: 10
  total: 22
status: issues_found
---

# Phase 1: Code Review Report (re-revisão depois do 01-07 e 01-08)

**Reviewed:** 2026-10-23T13:30:00Z
**Depth:** standard (incremental, diff `47165c3..HEAD`)
**Files Reviewed:** 11
**Status:** issues_found

## Summary

Revisto o diff dos planos 01-07 e 01-08: `words.py` (STOP, `_stem`, DIMS, LITRE, CLASS), o caminho WR-01 em `search_store` e o filtro em dois níveis da Obras 360. A suite passa: `uv run python -m pytest -q` → 161 passed. `money.py`, `text.py`, `allmat.py`, `fetch.py`, `sheet.py` e `report.py` não mudaram desde `47165c3` (`git diff --stat` vazio). Por isso os achados WR-02 a WR-06 e IN-01 a IN-06 passam para aqui sem nova análise.

As fixtures novas não têm segredos: `is_logged_in:false`, `user_email:""`/`null`, sem cookies, tokens, nonces nem cabeçalhos. O dinheiro continua em `Decimal` de ponta a ponta: `_list_price` faz `Decimal(v)` sobre JSON lido com `parse_float=Decimal` e `offers_from_details` não mudou. O caminho WR-01 não entra em ciclo, faz no máximo uma pesquisa extra por loja e não conta nada duas vezes. A contagem da 1.ª pesquisa vai para o `detail` e a da alargada para a linha "+N escondidas", cada uma com a sua pesquisa.

**Estado dos achados anteriores**

| ID | Estado | Prova |
|----|--------|-------|
| CR-01 | Corrigido nos casos citados | `tests/test_search.py::test_title_matches` (linhas 57-67) e `tests/test_obras360.py::test_tinta_branca_gravada_mostra_as_tintas_brancas`. Há plurais que ainda falham: ver o CR-05, que é novo. |
| CR-02 | Corrigido | `tests/test_obras360.py::test_osb_12mm_so_a_variante_de_12mm` (só "1 Placa 12 MM", 19,37 €, hidden 6). O desenho novo trouxe uma regressão: ver o CR-04, que é novo. |
| CR-03 | Corrigido em 3 de 4 casos | `test_title_matches` (linhas 69-74) e `tests/test_bricomarche.py::test_medidas_coladas_por_x_batem_no_filtro`. O caso "OSB 12,0 mm" continua `False` porque o 01-08 o adiou de propósito. Passa para o IN-07. |
| WR-01 | Corrigido quando o filtro esconde tudo | `test_tudo_escondido_diz_quantas_no_cabecalho`, `test_tudo_escondido_com_medidas_tenta_a_alargada` e `test_tudo_escondido_alargada_sem_ofertas_fica_a_primeira[x2]`. Continua a aparecer "ok" sozinho com zero ofertas quando `hidden == 0`: ver o WR-10. |
| WR-02 a WR-06 | Abertos (código igual) | Ficaram fora dos planos de fecho de lacunas. |
| IN-01 a IN-06 | Abertos (código igual) | Ficaram fora dos planos de fecho de lacunas. |

**Problemas novos que o diff trouxe.** Há dois BLOCKERs. O 1.º: na Obras 360, o pai passa a ser escolhido com a pesquisa sem números, e assim o corte K=20 por preço pode deitar fora o produto certo (CR-04, confirmado a correr o código). O 2.º: `_stem` não trata os plurais em -ais, -is (de -il), -ens, -óis nem palavras de 3 letras. "perfis", "canais", "terminais", "ferragens" e "pás" escondem o produto que a loja vende (CR-05). A normalização também passou a juntar produtos diferentes. "azulejo 30x30" bate em "30x60", e o género junta barra/barro, banco/banca, tampo/tampa e lixa/lixo (WR-07, WR-08).

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: O filtro de título ignora o género e as palavras de ligação — CORRIGIDO

**File:** `src/strata/words.py:22-43`
**Issue:** `STOP` e `_stem` resolvem os casos citados: "tinta branca"/"Branco Mate", "cola de contacto", "painéis", "luzes", "colheres" e "portões" dão todos `True`. "aquecimento"/"Cimento" e "porta"/"Portão" continuam `False`. Confirmado em `test_title_matches` e, sobre respostas reais gravadas, em `test_tinta_branca_gravada_mostra_as_tintas_brancas` (4 tintas mostradas, hidden 4).
**Fix:** nenhum. Os plurais que ainda falham estão no CR-05.

### CR-02: Obras 360 filtrava pelo nome do pai, e a medida está na variante — CORRIGIDO

**File:** `src/strata/stores/obras360.py:124-148`
**Issue:** os pais escolhem-se com `broadened(query) or query` e as variantes filtram-se com `title_matches(query, o.title)`. As variantes cortadas somam a `hidden`. Confirmado em `test_osb_12mm_so_a_variante_de_12mm`.
**Fix:** nenhum. A regressão que este desenho trouxe está no CR-04.

### CR-03: Medidas coladas por "x", sinónimos de unidade e sufixos de classe — CORRIGIDO (resto no IN-07)

**File:** `src/strata/words.py:8-10,41`
**Issue:** `DIMS`, `LITRE` e `CLASS` tratam "Chapa Osb 2440X590X18Mm", "Tinta 15 Lt" e "Placa OSB3 12 mm". Confirmado em `test_title_matches` e em `test_medidas_coladas_por_x_batem_no_filtro`. Fica a faltar `title_matches("osb 12mm", "OSB 12,0 mm")`, que continua `False` e passa para o IN-07.
**Fix:** nenhum aqui.

### CR-04: Obras 360 escolhe os pais sem os números e o corte K=20 por preço deita fora o produto pedido (regressão do 01-08)

**File:** `src/strata/stores/obras360.py:124-128`
**Issue:** `loose = broadened(query) or query` tira **todos** os tokens que têm um dígito, não só as medidas da variante. Códigos de modelo que estão no nome do pai também saem: "M8", "E27", "IP65", "OSB3", "C2", "CAT6". Exemplos: `broadened("parafuso m8")` → `"parafuso"`, `broadened("Lâmpada E27")` → `"Lâmpada"` e `broadened("Placa OSB3 12mm")` → `"Placa"`. Depois, `kept.sort(...)` por preço e `kept[:K]` ficam com os 20 pais genéricos mais baratos. Corrido com o `FakeFetcher` (25 parafusos genéricos baratos e 1 "Parafuso Sextavado M8" a 99 €, pesquisa "parafuso m8"):

```
parafuso m8: ok | 140 escondidas pelo filtro de título com 'parafuso m8' | offers 140 | hidden 0
  notes ['+6 produtos não expandidos (limite de 20 por pesquisa)']
  detail calls: 40   m8 expanded: False
```

A loja devolveu o M8 na lista, mas ele nunca é expandido. As 140 variantes dos parafusos errados ficam todas escondidas, o que dispara a alargada "parafuso". Essa volta a pedir os mesmos 20 detalhes e mostra 140 parafusos errados, marcados "pesquisa alargada". Antes do 01-08 o filtro do pai era a pesquisa completa, o pai M8 era o único escolhido e aparecia. Basta que a loja devolva mais de 20 pais que batem na pesquisa solta, o que é normal em termos genéricos (parafuso, lâmpada, cabo, tinta). O produto existe, a ferramenta não o mostra e mostra outros no lugar dele: isto viola o Core Value.
**Fix:** os pais que batem na pesquisa completa passam à frente no corte, e a pesquisa solta só serve para não perder os pais cuja medida está na variante:
```python
name = lambda p: p["product"]["name"]
kept = [p for p in products if title_matches(loose, name(p))]
kept.sort(key=lambda p: (not title_matches(query, name(p)), _list_price(p) is None, _list_price(p) or 0))
chosen = kept[:K]
```
Juntar um teste com 25 pais genéricos baratos e 1 "Parafuso Sextavado M8" caro, e verificar que `id-m8` está entre os detalhes pedidos.

### CR-05: `_stem` não trata os plurais -ais, -is, -ens, -óis nem palavras de 3 letras: o produto fica escondido (resto do CR-01)

**File:** `src/strata/words.py:25-35`
**Issue:** só `-oes`, `-eis` e `-s` são tratados, e palavras com `len <= 3` saem sem mudança antes de se tirar o "s". Confirmado com `title_matches`:
- `("perfis", "Perfil")` → `False` (`perfi` ≠ `perfil`)
- `("canais", "Canal")`, `("terminais", "Terminal")` e `("metais", "Metal")` → `False` (`canai` ≠ `canal`)
- `("ferragens", "Ferragem")` → `False` (`ferragen` ≠ `ferragem`)
- `("lençóis", "Lençol")` → `False`
- `("pás", "Pá")` → `False` (`pas` tem 3 letras e não é tocado; `pa` ≠ `pas`)

São plurais normais numa lista de obra (perfis de alumínio, calhas e canais, terminais elétricos, ferragens, pás). É o mesmo defeito do CR-01: a loja tem o produto, o filtro esconde-o, e sem números na pesquisa a alargada de D-14 não corre. O cabeçalho já dá a contagem (WR-01), mas o preço continua a não aparecer.
**Fix:**
```python
PLURAL = (("oes", "ao"), ("aes", "ao"), ("eis", "el"), ("ais", "al"), ("ois", "ol"), ("uis", "ul"),
          ("ens", "em"), ("is", "il"), ("s", ""))

def _stem(w: str) -> str:
    if len(w) <= 2 or any(c.isdigit() for c in w):
        return w
    for suf, rep in PLURAL:
        if w.endswith(suf) and len(w) > len(suf):
            w = w[: -len(suf)] + rep
            break
    return w[:-1] if len(w) > 3 and w[-1] in "aoe" else w
```
Juntar a `test_title_matches` os casos perfis/Perfil, canais/Canal, ferragens/Ferragem, lençóis/Lençol e pás/Pá. Confirmar que "lápis" continua a bater em "Lápis", porque a regra -is→-il dá o mesmo nos dois lados.

## Warnings

### WR-01: Estado "ok" com zero ofertas mostradas, e sem nova tentativa — CORRIGIDO (resto no WR-10)

**File:** `src/strata/search.py:23-34,53-57`
**Issue:** quando o filtro esconde tudo, o cabeçalho diz "0 ofertas mostradas; N escondidas pelo filtro de título", ou "N escondidas pelo filtro de título com '<pesquisa>'" quando a alargada entrou. A alargada tenta uma única vez, sem ciclo. Se a alargada falha, fica a 1.ª pesquisa com a nota "também sem ofertas com '…'". Confirmado nos 4 testes `test_tudo_escondido_*`.
**Fix:** nenhum aqui. O caso `hidden == 0` está no WR-10.

### WR-02: `content_from_title` lê o primeiro número com unidade, por isso packs e especificações dão €/kg e €/L errados — ABERTO

**File:** `src/strata/money.py:22-32` (usado em `src/strata/stores/allmat.py:89` e `src/strata/stores/bricomarche.py:84`)
**Issue:** passa sem mudança da revisão anterior. "2x25kg" → 25 kg, "6 x 1L" → 1 L, "150 kg" de carga lido como conteúdo. O €/kg inventado decide a ordem (D-03).
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

**File:** `src/strata/stores/obras360.py:39`, `src/strata/stores/obras360.py:112`, `src/strata/stores/obras360.py:121`, `src/strata/stores/obras360.py:149`
**Issue:** passa sem mudança no essencial. `raw` conta SKUs e `hidden` conta pais. Desde o 01-08, `hidden` (linha 148) também soma variantes, e por isso mistura três unidades. Além disso, o `report` atribui tudo a "título sem '<pesquisa completa>'", quando os pais foram escondidos pela pesquisa solta.
**Fix:** `raw=max(total, len(products))`, e decidir "há mais" com `len(rows) == PER_PAGE`.

### WR-07: DIMS parte "30x30" em dois "30" iguais: "azulejo 30x30" bate em "30x60" (novo, 01-08)

**File:** `src/strata/words.py:8`, `src/strata/words.py:41-43`
**Issue:** `DIMS.sub(" ", …)` transforma "30x30" em `{"30"}`, porque é um conjunto e os repetidos colapsam. A ordem e a combinação perdem-se. Confirmado: `("azulejo 30x30", "Azulejo 30x60")`, `("pavimento 60x60", "Pavimento 60x120")` e `("tubo 20x20", "Tubo Quadrado 20x40x1,5")` → `True`. Antes do 01-08, "30x30" era um token só e batia apenas em "30x30". Agora um mosaico ou um perfil com outra medida aparece como resultado normal, sem a marca "pesquisa alargada". Ordenado por €/m², pode ficar em 1.º lugar como "o mais barato".
**Fix:** partir as medidas e guardar também o token inteiro. Assim quem pede "30x30" exige "30x30", e "18mm" continua a bater em "2440x590x18mm":
```python
DIMS_GLUE = re.compile(r"(?<=\d)\s*x\s*(?=\d)")
DIMS_TOKEN = re.compile(r"\d+(?:[.,]\d+)?(?:x\d+(?:[.,]\d+)?)+")

def words(s) -> set[str]:
    s = DIMS_GLUE.sub("x", plain(s))          # "20 x 20" -> "20x20"
    dims = set(DIMS_TOKEN.findall(s))          # "30x30", "2440x590x18"
    s = CLASS.sub(r"\1 \2", LITRE.sub(r"\1l", DIMS.sub(" ", s)))
    s = JOIN.sub(r"\1\2", s)
    return dims | {_stem(w) for w in TOKEN.findall(s) if w not in STOP}
```
Juntar `("azulejo 30x30", "Azulejo 30x60", False)` e `("tubo 20x20", "Tubo 20 x 20", True)` a `test_title_matches`.

### WR-08: O género junta produtos diferentes: barra/barro, banco/banca, tampo/tampa, lixa/lixo (novo, 01-07)

**File:** `src/strata/words.py:35`
**Issue:** `w[:-1] if … w[-1] in "aoe"` aplica-se a todas as palavras, incluindo o substantivo que identifica o produto. Confirmado → `True`: `("barro", "Barra aço")`, `("banco", "Banca cozinha")`, `("tampo", "Tampa")`, `("rodo", "Roda")`, `("malho", "Malha sol")`, `("lixa", "Saco lixo")`, e também cano/cana, caixa/caixo e grade/grado. Uma pesquisa por "barro" deixa passar barras de aço, e uma por "tampo" deixa passar tampas. Os títulos aparecem como resultados normais e a ordem por preço pode pôr um deles em 1.º.
**Fix:** só igualar o género a partir da 2.ª palavra da pesquisa (em português o substantivo vem primeiro: "tinta **branca**", "barra **aço**"). O título dá as duas formas:
```python
def words(s, gender=True) -> set[str]: ...  # gender=False: só plural, sem tirar a/o/e

def title_matches(query, title):
    first, *rest = query.split(maxsplit=1) or [""]
    need = words(first, gender=False) | (words(rest[0]) if rest else set())
    return need <= (words(title, gender=False) | words(title))
```
Juntar `("barro", "Barra aço", False)`, `("tampo", "Tampa", False)` e manter `("tinta branca", "Tinta … Branco Mate", True)`.

### WR-09: Número sem unidade na pesquisa nunca bate num número com unidade no título

**File:** `src/strata/words.py:11-12`, `src/strata/words.py:46-48`
**Issue:** `JOIN` cola a unidade e o token fica "32mm", por isso "32" ≠ "32mm". Confirmado → `False`: `("tubo pvc 32", "Tubo PVC 32mm")` e `("parafuso 4x40", "Parafuso 4x40mm")`. Com o DIMS do 01-08, este último dá `{"4","40"}` contra `{"4","40mm"}`. Quem escreve a medida sem unidade (o normal numa lista de compras) vê esconder exatamente o produto pedido. A alargada só entra se **todas** as ofertas ficarem escondidas, por isso uma loja com um título "32" e outro "32mm" mostra um e esconde o outro.
**Fix:** do lado do título, juntar também o número sem a unidade:
```python
def title_matches(query, title):
    tw = words(title)
    tw |= {m[0] for w in tw if (m := re.match(r"\d+(?:[.,]\d+)?", w))}
    return words(query) <= tw
```
Juntar `("tubo pvc 32", "Tubo PVC 32mm", True)` e manter `("osb 12mm", "Chapa Osb 2440X590X18Mm", False)`.

### WR-10: "ok" sozinho com zero ofertas quando nada foi escondido pelo filtro (resto do WR-01)

**File:** `src/strata/search.py:53-58`
**Issue:** o `detail` só é preenchido quando `found.hidden > 0`. Se todas as ofertas forem descartadas por outro motivo, o cabeçalho diz "Allmat: ok" sem preço nenhum. Acontece com todos os produtos da Allmat sem preço (`no_price`) e com a Obras 360 a devolver `total_products > 0` sem linhas. O teste `tests/test_search.py::test_verificar_todos_a_zero_sem_ofertas` prova que o estado sai "ok" com `offers=[]`: só o `verificar` diz "sem ofertas", a pesquisa normal não. A nota "N produtos sem preço ignorados" aparece, mas o estado vem primeiro (D-01).
**Fix:**
```python
if not found.offers:
    detail = (f"0 ofertas mostradas; {found.hidden} escondidas pelo filtro de título"
              if found.hidden else "0 ofertas mostradas (ver notas)")
elif first_hidden:
    ...
```

### WR-11: Uma gama no nome do pai ("9-30MM") faz "osb 30mm" mostrar as 7 espessuras, com a de 9 mm em 1.º

**File:** `src/strata/stores/obras360.py:146-147`
**Issue:** o `shortcut:` documenta o problema, mas o efeito é um preço errado apresentado como resultado. Corrido contra as fixtures: `search("osb 30mm")` → 7 ofertas, `hidden 0`. Depois da ordenação, aparece primeiro "1 Placa 9 MM" a 15,02 €, sem marca de alargada. O desenho em dois níveis do 01-08 já separa o pai da variante, por isso a correção é pequena e não precisa de esperar pela Phase 3.
**Fix:** as palavras que a pesquisa solta não tem (as medidas) têm de estar na designação da variante, quando esta tem números:
```python
need = words(query) - words(loose)
def ok(o):
    desig = o.title.split(" — ", 1)[1]
    if need and any(c.isdigit() for c in desig):
        return title_matches(loose, o.title) and need <= words(desig)
    return title_matches(query, o.title)
shown = [o for o in offers if ok(o)]
```
Juntar um teste: `search("osb 30mm")` sobre `obras360_product-details_osb-parent.json` → só "1 Placa 30 MM".

## Info

### IN-01: Texto colado "Tinta branca 15L" ou "Tubo 3m" perde a medida sem aviso — ABERTO

**File:** `src/strata/text.py:53-55`
**Issue:** passa sem mudança.
**Fix:** `warns.append(f"'{tok}' lido como quantidade e unidade")` no ramo `GLUED`.

### IN-02: `broadened` deita fora tokens com hífen inteiros — ABERTO

**File:** `src/strata/words.py:51-55`
**Issue:** passa sem mudança. `broadened("OSB-12mm")` → `None`. Com o CR-02, este `None` também faz a Obras 360 escolher os pais com a pesquisa completa (`loose = query`).
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

**File:** `src/strata/search.py:72`, `src/strata/money.py:23`
**Issue:** passa sem mudança (a linha mudou de 58 para 72).
**Fix:** renomear o de `search.py` para `VALID_CONTENT_UNITS`.

### IN-07: "12,0 mm" não bate em "12mm" (resto do CR-03, adiado pelo 01-08)

**File:** `src/strata/words.py:12`
**Issue:** `title_matches("osb 12mm", "OSB 12,0 mm")` → `False`. O plano 01-08 listou o caso em Known Limitations.
**Fix:** antes do `JOIN`, `re.sub(r"(\d)[.,]0+\b", r"\1", s)`.

### IN-08: `broadened` não conhece os sinónimos novos do LITRE: "tinta 15 litros" alarga para "tinta litros"

**File:** `src/strata/words.py:13`, `src/strata/words.py:54`
**Issue:** o 01-08 passou a ler "litros"/"lts" como unidade em `words()`, mas `UNIT_TOKENS` não mudou. Confirmado: `broadened("tinta 15 litros")` → `"tinta litros"`. Essa pesquisa vai à loja e o filtro exige "litr" no título, por isso a alargada esconde as tintas "15L".
**Fix:** `UNIT_TOKENS = {..., "lts", "litro", "litros"}`.

### IN-09: A alargada deita fora as notas da 1.ª pesquisa e, na Obras 360, pede os mesmos detalhes duas vezes

**File:** `src/strata/search.py:30-32`, `src/strata/stores/obras360.py:129-131`
**Issue:** `found = wide` substitui o `Found` inteiro. Confirmado: notas "2 produtos sem detalhe: HTTP 500" e "mais produtos na loja não lidos" na 1.ª pesquisa → `sr.notes == []` depois da alargada. Uma falha da 1.ª pesquisa só volta a aparecer se se repetir na 2.ª. Na Obras 360, o gatilho novo "tudo escondido" faz a alargada correr depois de a 1.ª já ter pedido até 20 detalhes. São até 2×(3+20) = 46 pedidos por artigo, com os mesmos `product_id` pedidos duas vezes (40 pedidos de detalhe no cenário do CR-04). Fica dentro de `LIMITS` (3 em simultâneo, 0,3 s), mas gasta ≥14 s dos 90 s de `DEADLINE_S`.
**Fix:** `wide.notes[:0] = [f"1.ª pesquisa: {n}" for n in found.notes]` antes de `found = wide`. Na Obras 360, guardar os detalhes em `fetch.cache` por `product_id`.

### IN-10: Assimetrias de tokenização: "ip65"/"IP 65", "e27"/"E 27", unidade solta depois de decimal

**File:** `src/strata/words.py:10`, `src/strata/words.py:12`
**Issue:** `CLASS` só parte 2 ou mais letras seguidas de **um** dígito. `("ip65", "Projetor IP 65")` e `("lâmpada e27", "Lâmpada E 27")` → `False`. `TOKEN` corta a unidade depois de um decimal: "2,5mm" → `{"2,5","mm"}`. Por isso `("placa 2,5mm", "Placa 2,5cm 1,2mm")` → `True`. E `CLASS` deixa um "2" solto em "6mm2": `("cabo 6mm2", "Cabo 6mm 2 un")` → `True`.
**Fix:** `TOKEN = re.compile(r"[a-z0-9]+(?:[.,][0-9]+[a-z0-9]*)*")`, para "2,5mm" ficar um token só. Excluir as unidades do `CLASS` (`(?!mm|cm)` antes do grupo). Juntar letra+número também quando há espaço (`re.sub(r"\b([a-z]{1,3}) (\d+)\b", r"\1\2", s)`) nos dois lados.

---

_Reviewed: 2026-10-23T13:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard (incremental)_
