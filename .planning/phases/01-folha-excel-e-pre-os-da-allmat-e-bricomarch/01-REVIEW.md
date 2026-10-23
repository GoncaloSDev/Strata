---
phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch
reviewed: 2026-10-23T12:00:00Z
depth: standard
files_reviewed: 37
files_reviewed_list:
  - .gitignore
  - .python-version
  - README.md
  - pyproject.toml
  - src/strata/__init__.py
  - src/strata/__main__.py
  - src/strata/fetch.py
  - src/strata/models.py
  - src/strata/money.py
  - src/strata/report.py
  - src/strata/search.py
  - src/strata/sheet.py
  - src/strata/stores/__init__.py
  - src/strata/stores/allmat.py
  - src/strata/stores/bricomarche.py
  - src/strata/stores/obras360.py
  - src/strata/text.py
  - src/strata/words.py
  - tests/conftest.py
  - tests/test_allmat.py
  - tests/test_bricomarche.py
  - tests/test_e2e.py
  - tests/test_money.py
  - tests/test_obras360.py
  - tests/test_search.py
  - tests/test_sheet.py
  - tests/test_text.py
  - tests/test_tracer.py
  - tests/fixtures/allmat_product-page_39233_box.html
  - tests/fixtures/allmat_products_search-cimento.json
  - tests/fixtures/allmat_products_search-osb_no-results.json
  - tests/fixtures/bricomarche_products_search-osb.json
  - tests/fixtures/bricomarche_variations_parent-47412.json
  - tests/fixtures/obras360_pesquisa-widget.html
  - tests/fixtures/obras360_product-details_osb-parent.json
  - tests/fixtures/obras360_product-list_no-results.json
  - tests/fixtures/obras360_product-list_osb.json
findings:
  critical: 3
  warning: 6
  info: 6
  total: 15
status: issues_found
---

# Phase 1: Code Review Report

**Reviewed:** 2026-10-23T12:00:00Z
**Depth:** standard
**Files Reviewed:** 37
**Status:** issues_found

## Summary

Revistos todos os ficheiros da fase. O código está limpo e bem defendido: dinheiro em `Decimal` de ponta a ponta (`parse_float=Decimal`, nunca `r.json()`), a folha do utilizador só é lida, `report.clean` tira caracteres de controlo vindos das lojas e da folha, o `Fetcher` só fala com hosts da lista `LIMITS` e as falhas de loja viram sempre um estado visível. Os 137 testes passam. As fixtures não têm cookies, cabeçalhos, tokens nem dados pessoais (só `is_password_protected: false`).

O problema central é o filtro de título (D-15). Esconde ofertas que a loja vende mesmo, em casos normais de uso, e a loja continua a dizer "ok". Há três causas independentes, todas confirmadas a correr o código contra as fixtures reais:

1. Género e palavras de ligação ("tinta branca" contra "Branco"). É o problema já conhecido, confirmado aqui.
2. Na Obras 360 o filtro corre sobre o nome do pai, mas a medida está na variante: a linha de exemplo do próprio modelo (`OSB 12 mm`) mostra zero ofertas na Obras 360.
3. Medidas coladas por "x" e sinónimos de unidade ("2440X590X18Mm", "15 Lt") nunca batem.

Depois disso, os problemas mais sérios são preços por unidade errados em packs (`2x25kg`, `6 x 1L`) e "1.000" (mil, à portuguesa) lido como quantidade 1.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: O filtro de título ignora o género e as palavras de ligação: a loja diz "ok" e esconde tudo (problema conhecido, confirmado)

**File:** `src/strata/words.py:19-27` (e `src/strata/search.py:22`, `src/strata/report.py:49-62`)
**Issue:** `words()` só trata o plural em `-s`, e `title_matches` exige que **todas** as palavras da pesquisa estejam no título (`words(query) <= words(title)`). Confirmado:
- `title_matches("tinta branca", "Tinta Plástica 15L Branco Mate")` → `False` (`branca` ≠ `branco`). É o caso conhecido: a Obras 360 escondeu as 8 ofertas e a secção diz `Obras 360: ok` sem nenhum preço.
- `title_matches("cola de contacto", "Cola Contacto 1L")` → `False`: "de" tem de aparecer no título.
- `title_matches("painéis", "Painel sandwich")` → `False` (`painei` ≠ `painel`). O mesmo acontece com `luzes`/`luz` e `colheres`/`colher`.

Como `raw > 0`, a pesquisa alargada de D-14 nunca corre, e `search_store` devolve `status="ok"` com `offers=[]`. Não é uma omissão silenciosa, porque a linha "+8 ofertas escondidas" aparece. Mas viola o Core Value: o produto existe na loja, a app não mostra o preço, e o estado "ok" diz ao utilizador que a loja respondeu bem. Para o caso "tinta branca", a pesquisa feita à mão ganha à ferramenta. Classificado como BLOCKER.
**Fix:** normalizar as palavras antes de comparar e ignorar as palavras de ligação:
```python
STOP = {"de", "da", "do", "das", "dos", "para", "com", "em", "e", "a", "o"}

def _stem(w: str) -> str:
    if w.isdigit() or any(c.isdigit() for c in w):
        return w
    for suf, rep in (("oes", "ao"), ("aes", "ao"), ("eis", "el"), ("res", "r"), ("zes", "z"), ("s", "")):
        if len(w) > 3 and w.endswith(suf):
            w = w[: -len(suf)] + rep
            break
    return w[:-1] if len(w) > 3 and w[-1] in "ao" else w  # branca/branco -> branc

def words(s) -> set[str]:
    s = JOIN.sub(r"\1\2", plain(s))
    return {_stem(w) for w in TOKEN.findall(s) if w not in STOP}
```
Acrescentar casos parametrizados em `tests/test_search.py::test_title_matches` ("tinta branca"/"Branco Mate", "cola de contacto"/"Cola Contacto", "painéis"/"Painel"). Corrigir também o WR-01 (estado com zero ofertas mostradas).

### CR-02: Obras 360 filtra pelo nome do pai e a medida está na variante: "OSB 12 mm" (a linha de exemplo do modelo) mostra zero ofertas

**File:** `src/strata/stores/obras360.py:123`
**Issue:** `kept = [p for p in products if title_matches(query, p["product"]["name"])]` compara a pesquisa com o nome do **pai** ("Placa OSB 9-30MM Resistente à Humidade…"). A espessura só existe na variante ("1 Placa 12 MM - 2,5 M x 1,25 M…", em `_selectionsAttributes`). Corrido contra as fixtures reais:
```
osb 12mm    raw 13 hidden 2 offers []
OSB 12 mm   raw 13 hidden 2 offers []
placa osb   raw 13 hidden 1 offers [... 30 MM, 22 MM, 15 MM, ...]
```
A fixture tem a variante "1 Placa 12 MM". A linha que `sheet.write_template` grava como exemplo (`src/strata/sheet.py:115`, `"OSB 12 mm"`) dá `Obras 360: ok` sem nenhuma oferta na loja que vende essa placa. O teste ponta a ponta só usa "placa osb", sem medida, e por isso não apanha o caso.
**Fix:** escolher os pais com a pesquisa sem medidas e filtrar as ofertas pela pesquisa completa sobre o título da variante:
```python
from strata.words import broadened, title_matches

loose = broadened(query) or query
kept = [p for p in products if title_matches(loose, p["product"]["name"])]
...
offers = [o for o in offers if title_matches(query, o.title)]  # o.title = pai + designação da variante
hidden = (len(products) - len(kept)) + (n_variantes - len(offers))
```
Juntar um teste com `search("osb 12mm", fake)` que espera exatamente a oferta "1 Placa 12 MM".

### CR-03: Medidas coladas por "x", sinónimos de unidade e sufixos de modelo nunca batem no filtro

**File:** `src/strata/words.py:8-10`
**Issue:** `TOKEN` junta letras e números num só token, e `JOIN` só conhece `mm|cm|m|m2|kg|g|l|ml`. Confirmado:
- `title_matches("osb 18mm", "Chapa Osb 2440X590X18Mm")` → `False`. É um título real da fixture `bricomarche_products_search-osb.json`: o token fica `2440x590x18mm`.
- `title_matches("tinta 15L", "Tinta 15 Lt")` → `False`: "15 lt" não é juntado e `lt` ≠ `l`.
- `title_matches("OSB 12mm", "Placa OSB3 12 mm")` → `False` (`osb3` ≠ `osb`).
- `title_matches("osb 12mm", "OSB 12,0 mm")` → `False`.

O formato `LxCxEmm` é o mais comum nos títulos de placas e perfis. Uma pesquisa com espessura esconde precisamente o produto pedido.
**Fix:** partir as medidas pelo "x" e normalizar os sinónimos de unidade antes de tokenizar:
```python
DIMS = re.compile(r"(?<=\d)x(?=\d)")
UNIT_ALIAS = re.compile(r"(\d)\s*(lts?|litros?)\b")

def words(s) -> set[str]:
    s = plain(s)
    s = DIMS.sub(" ", s)                    # 2440x590x18mm -> 2440 590 18mm
    s = UNIT_ALIAS.sub(r"\1l", s)           # 15 lt -> 15l
    s = JOIN.sub(r"\1\2", s)
    ...
```
Tratar `osb3` (sufixo de classe) como `osb` + `3` (`re.sub(r"([a-z]{2,})(\d)\b", r"\1 \2", s)`) e acrescentar estes quatro títulos aos testes.

## Warnings

### WR-01: Estado "ok" com zero ofertas mostradas, e sem nova tentativa

**File:** `src/strata/search.py:34-45`, `src/strata/report.py:49-62`
**Issue:** quando o filtro esconde tudo, `search_store` devolve `"ok"` com `offers=[]`. D-14 só alarga quando `raw == 0`, por isso não há segunda tentativa. Quem lê só a linha de estado (D-01 diz que o estado vem primeiro) vê "ok" e passa à frente. O `verificar` apanha o caso como "sem ofertas", mas a pesquisa normal não avisa.
**Fix:** quando `found.offers == []` e `found.hidden > 0`, mostrar isso no cabeçalho, por exemplo `detail=f"0 ofertas mostradas; {found.hidden} escondidas pelo filtro de título"`, ou usar um estado próprio. Opcionalmente, mostrar as N mais baratas das escondidas, marcadas como tal (D-15 diz "escondidas, mas contadas", e a lista vazia derrota o objetivo).

### WR-02: `content_from_title` lê o primeiro número com unidade, por isso packs e especificações dão €/kg e €/L errados

**File:** `src/strata/money.py:22-32` (usado em `src/strata/stores/allmat.py:89` e `src/strata/stores/bricomarche.py:84`)
**Issue:** confirmado:
- `"Cimento cola 2x25kg"` → `(25, kg)`, mas o preço é de 50 kg: o €/kg sai a dobrar.
- `"Pack 6 x 1L Lixivia"` → `(1, L)`: o €/L sai 6× mais alto.
- `"Tinta 4 x 750ml"` → `(0.75, L)`.
- `"Escadote 4 degraus 150 kg"` → `(150, kg)`: a carga máxima vira conteúdo e aparece um "€/kg" sem sentido.

O valor é mostrado como facto (`report._offer_lines`) e, numa linha em kg ou L, decide a ordem (`in_unit`, D-03). Preço é dinheiro: um €/kg inventado é pior do que "desconhecido".
**Fix:** recusar o conteúdo quando há multiplicador e marcar o caso:
```python
MULTI = re.compile(r"\d\s*x\s*\d")
def content_from_title(title):
    t = plain(title)
    if MULTI.search(t):
        return None  # pack NxM: conteúdo por ler até à Phase 3
    ...
```
Ou multiplicar `N x M`. Nos adaptadores, `None` cai para `(1, "un")`. Na Allmat e na Bricomarché, juntar uma nota "conteúdo lido do título" para que o €/kg não pareça vir da loja.

### WR-03: "1.000" (mil, à portuguesa) é lido como quantidade 1

**File:** `src/strata/text.py:34`, `src/strata/text.py:44`
**Issue:** `to_decimal("1.000")` → `Decimal("1.000")` = 1, e `NUM` aceita o token. Confirmado: `parse_line("cimento 1.000 un")` → `qty=1.000`. Na folha, uma célula de texto "1.000" dá o mesmo resultado. Já `"1.000,5"` é recusado, o que mostra que o caso não foi pensado. É uma quantidade errada em silêncio: o cabeçalho mostra "(1 un)" e não há aviso.
**Fix:** tratar um ponto seguido de exatamente três dígitos, sem vírgula, como separador de milhares, ou recusar com motivo:
```python
if isinstance(v, str) and re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", s_orig):
    s = s_orig.replace(".", "").replace(",", ".")
```
Testar com "1.000" → 1000, "1.000,5" → 1000.5, "2.5" → 2.5 e "2,5" → 2.5.

### WR-04: Allmat cai inteira com `InvalidOperation` se um produto vier com `price: ""`

**File:** `src/strata/stores/allmat.py:81`
**Issue:** `from_minor(prices["price"], ...)` faz `Decimal("")` e lança `decimal.InvalidOperation`. A exceção sobe até `search_store`, que marca a Allmat inteira como `erro` por causa de um único produto. O adaptador da Bricomarché trata exatamente este caso (`_minor`: `value in (None, "")`, `bricomarche.py:24-27`), portanto a Store API devolve-o. A Allmat usa o mesmo WooCommerce e não o trata.
**Fix:** reutilizar a mesma guarda:
```python
raw = prices.get("price")
price = from_minor(raw, prices["currency_minor_unit"]) if raw not in (None, "") else Decimal(0)
if price <= 0:
    no_price += 1
    continue
```
Juntar um teste com uma linha `"price": ""` no meio da fixture de cimento.

### WR-05: Uma página de caixa bloqueada deita fora todas as ofertas da Allmat

**File:** `src/strata/stores/allmat.py:115-118`, `src/strata/stores/allmat.py:143-147`
**Issue:** `_read_box` só apanha `StoreError`. Um `StoreBlocked` (403/429/503 da Cloudflare) ou `StoreTimeout` numa das até 10 páginas de produto é relançado e a loja fica toda `bloqueada`, perdendo as ofertas da API JSON que já tinham preço válido. As páginas HTML da Allmat estão atrás da Cloudflare e são mais propensas a desafios do que a API. Uma leitura opcional (a área da caixa) derruba o resultado principal.
**Fix:** tratar o bloqueio de uma página de caixa como falha dessa oferta e deixar uma nota visível na loja:
```python
except (StoreError, StoreBlocked, StoreTimeout) as e:
    o.content, o.content_unit, o.note = None, None, f"página do produto falhou: {e}"
```
Se todas as páginas lidas derem `StoreBlocked`, acrescentar `notes.append("páginas de produto bloqueadas: área das caixas por ler")`. Assim a falha continua visível e não se perdem preços.

### WR-06: Obras 360 usa `total_products` como `raw`: se o campo faltar, os produtos lidos passam a "sem resultados"

**File:** `src/strata/stores/obras360.py:39`, `src/strata/stores/obras360.py:112`, `src/strata/stores/obras360.py:144`
**Issue:** `parse_list` faz `int(p.get("total_products") or 0)`. Se o campo vier a `None` ou deixar de existir, o ciclo pára na página 1 e `Found(raw=0, ...)` leva `search_store` a responder "sem resultados", com os produtos já na mão. Na fixture, `total_products=13` conta SKUs, mas só vêm 2 pais. `raw` (SKUs) e `hidden` (pais) estão em unidades diferentes, e a nota "mais produtos na loja não lidos" (linha 121) também compara páginas de pais com o total de SKUs.
**Fix:**
```python
return Found(offers=offers, raw=max(total, len(products)), hidden=len(products) - len(kept), notes=notes)
```
Na linha 121, decidir "há mais" pelo número de linhas da última página (`len(rows) == PER_PAGE`) em vez de `total`.

## Info

### IN-01: Texto colado "Tinta branca 15L" ou "Tubo 3m" perde a medida sem aviso

**File:** `src/strata/text.py:53-55`
**Issue:** `GLUED` lê "15L" como quantidade 15 em L, e o produto fica "Tinta branca". O mesmo acontece em "Tubo 3m" → produto "Tubo", 3 m. Segue D-11, mas não há aviso quando a quantidade colada vem sem espaço e a linha não tem outro número.
**Fix:** acrescentar `warns.append(f"'{tok}' lido como quantidade e unidade")` no ramo `GLUED`.

### IN-02: `broadened` deita fora tokens com hífen inteiros

**File:** `src/strata/words.py:32-34`
**Issue:** `broadened("OSB-12mm")` → `None`, porque o token tem um dígito e é removido inteiro. Fica sem a nova tentativa de D-14.
**Fix:** partir com `re.split(r"[\s-]+", query)` antes de filtrar.

### IN-03: Fórmulas sem valor guardado aparecem como "Qty vazia"

**File:** `src/strata/sheet.py:57`, `src/strata/sheet.py:91-92`
**Issue:** com `data_only=True`, uma célula com fórmula de uma folha gravada por uma ferramenta que não guarda o valor calculado chega como `None`, e o motivo diz "Qty vazia" quando a célula tem conteúdo.
**Fix:** se for preciso, reabrir sem `data_only` só para distinguir e dizer "fórmula sem valor calculado: abra e grave no Excel".

### IN-04: `write_template` deixa um ficheiro parcial se a gravação falhar

**File:** `src/strata/sheet.py:125-126`
**Issue:** com `open(path, "xb")`, uma exceção em `wb.save` deixa um `modelo.xlsx` truncado, e a execução seguinte diz "já existe".
**Fix:** no `except`, apagar o ficheiro que acabou de ser criado (`path.unlink(missing_ok=True)`) e relançar.

### IN-05: HTTP 503 é sempre classificado como "bloqueada"

**File:** `src/strata/fetch.py:82`
**Issue:** uma manutenção normal (503 sem `cf-mitigated`) aparece como "bloqueada", e isso pode levar a mexer no ritmo sem necessidade.
**Fix:** contar como bloqueio só o `503` com `cf-mitigated` ou com um marcador de desafio no corpo. Os outros 503 vão para `StoreError("HTTP 503")`.

### IN-06: Dois `CONTENT_UNITS` com significados diferentes

**File:** `src/strata/search.py:58`, `src/strata/money.py:23`
**Issue:** em `money` é um dicionário de unidades do título, em `search` é um tuplo de unidades válidas para o `verificar`. Facilita trocar um pelo outro.
**Fix:** renomear o de `search.py` para `VALID_CONTENT_UNITS`.

---

_Reviewed: 2026-10-23T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
