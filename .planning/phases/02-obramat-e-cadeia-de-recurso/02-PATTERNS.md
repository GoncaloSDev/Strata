# Phase 2: Obramat e cadeia de recurso - Pattern Map

**Mapped:** 2026-10-31
**Files analyzed:** 17 (6 novos em `src/`, 6 tocados em `src/`, 5 de testes + fixtures)
**Analogs found:** 15 / 17

Todos os caminhos abaixo são ficheiros rastreados pelo git (`git ls-files src tests`). As amostras novas estão em `.planning/phases/02-obramat-e-cadeia-de-recurso/samples/` e copiam-se para `tests/fixtures/`.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/strata/stores/obramat.py` (novo) | adaptador de loja | request-response + transform (HTML → Offer) | `src/strata/stores/allmat.py` (selectolax, página de produto) + `src/strata/stores/bricomarche.py` (corte K, loja física, nota "mais barata sem stock") | exact |
| `src/strata/browser.py` (novo) | cliente de transporte | request-response (CDP) | `src/strata/fetch.py` (`Fetcher`, `Host`, `--record`) | role-match |
| `src/strata/jsonld.py` (novo) | utility + degrau | request-response + transform | `src/strata/stores/allmat.py` `_read_box`/`parse_box` (HTML de produto com selectolax) | role-match |
| `src/strata/ai.py` (novo) | serviço externo | request-response (API / subprocesso) | nenhum (validação de fronteira copiada de `obras360.py:67-68`) | no analog |
| `src/strata/fetch.py` (tocar) | cliente HTTP | request-response | si próprio | exact |
| `src/strata/search.py` (tocar) | orquestração | event-driven por loja | si próprio (`search_store`) | exact |
| `src/strata/models.py` (tocar) | model | — | si próprio | exact |
| `src/strata/report.py` (tocar) | saída terminal | transform | si próprio (`_offer_lines`, `print_item`) | exact |
| `src/strata/__main__.py` (tocar) | CLI | request-response | si próprio (`--record`, `_with_fetch`) | exact |
| `pyproject.toml` (tocar) | config | — | `uv add` (checkpoint humano antes) | exact |
| `tests/test_obramat.py` (novo) | test | unit, fixtures | `tests/test_bricomarche.py` | exact |
| `tests/test_chain.py` (novo) | test | unit, lojas falsas | `tests/test_search.py` (`fake_store`, `monkeypatch DEADLINE_S`) | exact |
| `tests/test_jsonld.py` (novo) | test | unit, fixtures | `tests/test_allmat.py` | role-match |
| `tests/test_ai.py` (novo) | test | unit, motor trocado por monkeypatch | `tests/test_search.py` (monkeypatch em `strata.search`) | partial |
| `tests/test_fetch.py` (novo) | test | unit | `tests/test_search.py` (importa `Fetcher`, `Timeout`) | partial |
| `tests/test_e2e.py` (tocar) | test | e2e sem rede | si próprio | exact |
| `tests/fixtures/obramat_*.html` (novo) | fixture | — | `tests/fixtures/obras360_pesquisa-widget.html` (HTML gravado, nome legível + `fake.route`) | exact |

## Pattern Assignments

### `src/strata/stores/obramat.py` (adaptador, HTML → Offer)

**Analog principal:** `src/strata/stores/allmat.py`; regra de loja física e corte K: `src/strata/stores/bricomarche.py`.

**Cabeçalho, imports e constantes** (`allmat.py` linhas 1-28; `bricomarche.py` 1-21):
```python
"""Allmat (allmat.pt): WooCommerce Store API, preços em cêntimos já com IVA."""

import asyncio
import html
import re
from decimal import Decimal, InvalidOperation

from selectolax.lexbor import LexborHTMLParser

from strata.fetch import StoreError
from strata.models import Found, Offer
from strata.money import content_from_title, from_minor
from strata.text import norm
from strata.words import title_matches, words

NAME = "Allmat"
SEARCH_URL = "https://allmat.pt/wp-json/wc/store/v1/products"
# shortcut: limite de 10 páginas por pesquisa (...), subir se o `verificar` mostrar caixas baratas por ler
MAX_BOX_PAGES = 10
VAT_EVIDENCE = "páginas de produto da Allmat: IVA incluído"
```
Copiar: docstring de uma linha, `NAME`, `BASE` (como `bricomarche.py:11`), `K = 3` com comentário `shortcut:` (como `bricomarche.py:15-16`), `VAT_EVIDENCE`, `LOCATION = "OBRAMAT Lisboa - Alfragide"` com `shortcut:` (um só armazém, A8). Acrescentar `search_page(query)` (link "abrir à mão", `BASE + "/search?q=" + quote_plus(query)`). Usar `from strata.money import add_vat, content_from_title, fmt_eur`.

**Parser de euros em texto PT** (`allmat.py` 31-37) — reutilizar a ideia para `Ou Vendido 1 299,60 € IVA`:
```python
def _eur(text: str) -> Decimal | None:
    try:
        d = Decimal(re.sub(r"[^\d,]", "", text).replace(",", "."))
    except InvalidOperation:
        return None
    return d if d.is_finite() else None
```

**Parser puro com selectolax e escopo restrito** (`allmat.py` 47-59) — o mesmo cuidado de "só dentro do bloco certo" que o `ol#guidance-product-list > li[data-reflm] > script.dataTms` exige (Armadilhas 1 e 2 da RESEARCH):
```python
root = LexborHTMLParser(page).css_first(f"#product-{int(product_id)}")
if root is None:
    return None, None, NOT_FOUND
for box in root.css(".allmat-loop-price-box"):
```
Código de `parse_search`/`parse_tiers`/`challenge_kind` está pronto em RESEARCH §Code Examples (linhas 349-410).

**Conferência do IVA** (`obras360.py` 67-68) — copiar com tolerância 0,02 (D-04, Pitfall 4):
```python
price = add_vat(item["final_price_unformatted"], rate)
if abs(price - Decimal(item["final_price_with_tax_unformatted"])) > Decimal("0.01"):
```

**Construção da Offer + nota da mais barata sem stock** (`bricomarche.py` 73-98):
```python
note = ""
if _price(low) < _price(best):  # RES-02: a mais barata sem stock nunca some
    note = f"mais barata sem stock: {fmt_eur(_price(low))} em {store_link(low)[1]}"
content, content_unit = content_from_title(title) or (Decimal(1), "un")
return Offer(store=NAME, title=title, url=url, price=..., vat_origin="regra da loja",
             vat_evidence=VAT_EVIDENCE, content=content, content_unit=content_unit,
             stock=stock or "desconhecido", location=location, note=note)
```
Com um só armazém, a regra D-01 reduz-se a `location=LOCATION`; a nota fica sem uso.

**Páginas de produto só para as K primeiras, falha de página não mata a loja** (`allmat.py` 115-122 e 143-148):
```python
async def _read_box(product_id: int, o: Offer, fetch) -> None:
    try:
        page = await fetch.get_html(o.url)
    except StoreError as e:  # StoreBlocked e StoreTimeout sobem: a loja fica bloqueada / tempo esgotado
        o.content, o.content_unit, o.note = None, None, f"página do produto falhou: {e}"
        return
...
results = await asyncio.gather(*(_read_box(pid, o, fetch) for pid, o in boxes[:MAX_BOX_PAGES]),
                               return_exceptions=True)
for r in results:
    if isinstance(r, BaseException):
        raise r
```
Na Obramat, `LIMITS` = 1 em simultâneo, por isso o `gather` serializa sozinho. Se faltar o armazém 201, nota visível (RESEARCH Pattern 3 passo 6).

**Função `search` e notas** (`allmat.py` 125-149; `bricomarche.py` 232-261): `raw = len(produtos)`, filtro `title_matches(query, ...)` (D-15), `hidden=raw - len(filtrados)`, notas em lista (`"+N produtos não expandidos (limite de K por pesquisa)"`, `bricomarche.py:259-260`), `rank` para ordenar antes do corte K (`bricomarche.py:241-243`).

---

### `src/strata/browser.py` (BrowserFetcher, CDP)

**Analog:** `src/strata/fetch.py`.

Copiar a interface exata (`fetch.py` 63-103): `__init__` com `self.hosts = {h: Host(*v) for h, v in LIMITS.items()}` e `self.cache`, `get_json`, `get_html`. Pontos obrigatórios:
```python
async with self.hosts[host]:          # ritmo por host (fetch.py:75); reutilizar Host, não um novo limitador
...
if self.record:
    self.record.mkdir(parents=True, exist_ok=True)
    (self.record / fixture_name(full)).write_bytes(r.content)  # só o corpo, nunca cabeçalhos/cookies
...
return json.loads(r.content, parse_float=Decimal)   # nunca r.json()
```
`full_url`/`fixture_name` importam-se de `strata.fetch`. `cache` deve ser o **mesmo dict** do `Fetcher` (estado D-07/D-08 por execução). Arranque/fecho do Chrome (D-06) e deteção `'rt':'c'` → `StoreCaptcha`: RESEARCH Pattern 2 (linhas 248-260). Sem analog para a parte Playwright.

---

### `src/strata/fetch.py` (tocar)

- `LIMITS` (linha 27): acrescentar `"www.obramat.pt": (1, <gap>)`.
- Nova `class StoreCaptcha(Exception)` ao lado das outras (linhas 14-23). Decidir na planificação se herda de `StoreBlocked` — se herdar, os `except StoreBlocked` atuais apanham-na; a cadeia tem de a testar primeiro.
- O teste ao `var dd={...}` vem **antes** da linha 82 (Pitfall 2):
```python
if r.status_code in (403, 429, 503) or r.headers.get("cf-mitigated"):
    raise StoreBlocked(f"HTTP {r.status_code}")
```

---

### `src/strata/search.py` (tocar: cadeia em `search_store`)

**Analog:** o próprio `search_store` (linhas 17-67). O corpo das linhas 22-41 (1.ª pesquisa + alargada + filtro D-15) passa a correr por degrau; o tratamento de exceções (42-49) passa a acumular motivos em vez de devolver; a ordenação e o `detail` (50-67) ficam como estão. Esboço completo em RESEARCH Pattern 1 (linhas 216-246).

Exceções atuais a manter como motivos:
```python
except TimeoutError:
    return StoreResult(store.NAME, "tempo esgotado", [], detail=f"mais de {DEADLINE_S} s")
except StoreTimeout as e: ...
except StoreBlocked as e: ...
except Exception as e:  # o único sítio onde uma falha de loja vira estado; nunca some em silêncio
    return StoreResult(store.NAME, "erro", [], detail=f"{type(e).__name__}: {e}")
```
`raw == 0` → `"sem resultados"` sem escalar (linha 50, D-14).

Integrações: `STORES` (linha 13) ganha `obramat`; `CANARIES` (linha 78) ganha `(obramat, "osb")`; `_problem` (83-105) ganha um ramo como o da Bricomarché:
```python
if store is bricomarche and any(not o.location for o in sr.offers):
    return "sem nome de loja"
```
`run` (70-74) passa o browser a `search_store`.

---

### `src/strata/models.py` (tocar)

- `Status` (linha 7): acrescentar `"abrir à mão"`.
- `Offer` (linhas 31-44): `method: str = ""` com comentário curto, no fim, como `broadened`/`note`.
- `StoreResult` (55-64): `link: str | None = None`.

---

### `src/strata/report.py` (tocar)

Seguir `_offer_lines` (linhas 16-31): mais um `info.append(...)` para o método (e "lido por IA" via `o.note`, que já é impresso). Em `print_item` (43-67), depois do `head`, imprimir `sr.link` passado por `clean()`:
```python
if o.location:
    info.append(f"loja: {clean(o.location)}")
```
Tudo o que vem das lojas ou da IA passa por `clean()`.

---

### `src/strata/__main__.py` (tocar: `--sem-principal LOJA`, D-17)

Copiar o padrão do `--record` (linhas 19-22 e 26) nos dois subcomandos:
```python
ps.add_argument(
    "--record", metavar="DIR", type=Path,
    help="(desenvolvimento) grava o corpo de cada resposta das lojas em DIR, para fixtures de teste",
)
```
`_with_fetch` (30-37) é onde a sessão abre e fecha; é o sítio para criar e fechar o `BrowserFetcher` (D-06: fechar o Chrome só se foi a app a abri-lo), mantendo o atalho `if fetch is not None: return await work(fetch)` para os testes.

---

### `src/strata/jsonld.py` (degrau JSON-LD)

**Analog parcial:** `allmat.py` `_read_box` (página de produto via `fetch.get_html`, falha local vira nota) e `LexborHTMLParser`. Ler `script[type="application/ld+json"]` com `json.loads(..., parse_float=Decimal)` (como `fetch.py:95`). Lojas sem `PRODUCT_LINK` levantam `StoreError` com o motivo de D-19. Devolve `Found` com a assinatura dos adaptadores.

---

### `tests/test_obramat.py`

**Analog:** `tests/test_bricomarche.py` (linhas 1-60):
```python
FIXTURES = Path(__file__).parent / "fixtures"

def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"), parse_float=Decimal)
```
Para HTML: `(FIXTURES / "obramat_search-osb_browser.html").read_text(encoding="utf-8")`. Testar parsers puros (`parse_search`, `parse_tiers`, `challenge_kind`) e depois `search` com `fake.route(...)` (padrão de `test_e2e.py` 28-39). Casos obrigatórios: RESEARCH §Phase Requirements → Test Map (linhas 503-508).

### `tests/test_chain.py`

**Analog:** `tests/test_search.py` — `fake_store` (linhas 33-47) dá lojas falsas que devolvem `Found` ou levantam exceções em sequência; `monkeypatch.setattr(strata.search, "DEADLINE_S", 0.05)` (linha 298) para o prazo a meio; `monkeypatch.setattr(strata.search, "STORES", stores)` (linha 339). Dois `FakeFetcher` (um "curl", um "browser") partilhando `cache`. Para D-07/D-08 verificar `fake.calls` vazio no 2.º item.

### `tests/test_e2e.py` (tocar)

A linha 26 fixa `STORES == (allmat, bricomarche, obras360)` e a 16 `ORDER`; ambas mudam com a Obramat. Acrescentar rotas `fake.route("obramat.pt/search?q=...", "obramat_...html")` e um caso com `--sem-principal obramat`.

### `tests/test_ai.py`, `tests/test_fetch.py`

Seguir `monkeypatch.setattr` do `test_search.py`: trocar a função do motor da IA; nunca chamar `claude` nem a API. `test_fetch.py`: `Fetcher(session_falsa)` com um objeto `SimpleNamespace(status_code=403, headers={}, content=..., text=...)` para o 403 com `'rt':'c'` vs `'rt':'i'`.

## Shared Patterns

### Falhas nunca em silêncio
**Source:** `src/strata/search.py` linhas 42-49 e 60-63; `allmat.py` 118-120.
**Apply to:** `search.py`, `obramat.py`, `jsonld.py`, `ai.py`, `browser.py`. Exceções `StoreBlocked`/`StoreError`/`StoreTimeout` sobem dos adaptadores; só `search_store` as converte em estado. Falhas parciais (uma página de produto) viram `o.note`.

### Dinheiro em `Decimal`
**Source:** `fetch.py:94-95` (`parse_float=Decimal`), `money.py` (`add_vat`, `fmt_eur`, `fmt_qty`).
**Apply to:** Obramat, JSON-LD, IA (preço da IA convertido para `Decimal` > 0 e presente no texto enviado).

### Ritmo por host
**Source:** `fetch.py` 26-27 (`LIMITS`) e 40-60 (`Host`).
**Apply to:** `Fetcher` e `BrowserFetcher`; host sem entrada em `LIMITS` → `ValueError` (`fetch.py:72-73`).

### Limites conhecidos marcados
**Source:** `bricomarche.py:15` e `:44`, `allmat.py:20`.
**Apply to:** K = 3 da Obramat, armazém único, corte de texto da IA. Formato: `# shortcut: <limite>, <quando subir>`.

### Saída limpa
**Source:** `report.py:11-13` (`clean`).
**Apply to:** método, link "abrir à mão", títulos e notas vindos da IA.

### Testes sem rede
**Source:** `tests/conftest.py` 15-20 (`no_network` autouse), 23-73 (`FakeFetcher`, `fake` com asserção de fixtures em falta).
**Apply to:** todos os testes novos. O `FakeFetcher` já serve como `BrowserFetcher` falso (mesma interface).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `src/strata/ai.py` | serviço externo | request-response (SDK `anthropic` / `claude -p` em subprocesso) | Nenhuma chamada a IA nem subprocesso no código; usar RESEARCH Pattern 5 e §Code Examples (linhas 276-281, 412-424) |
| parte Playwright de `src/strata/browser.py` | transporte | CDP | Sem Playwright no projeto; RESEARCH Pattern 2 (linhas 248-260) |

## Metadata

**Analog search scope:** `src/strata/`, `src/strata/stores/`, `tests/`
**Files scanned:** 13 módulos + 4 ficheiros de teste
**Pattern extraction date:** 2026-10-31
