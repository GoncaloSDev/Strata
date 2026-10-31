---
phase: 02-obramat-e-cadeia-de-recurso
reviewed: 2026-10-31T12:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - src/strata/__main__.py
  - src/strata/ai.py
  - src/strata/browser.py
  - src/strata/fetch.py
  - src/strata/jsonld.py
  - src/strata/models.py
  - src/strata/report.py
  - src/strata/search.py
  - src/strata/stores/allmat.py
  - src/strata/stores/bricomarche.py
  - src/strata/stores/obramat.py
  - src/strata/stores/obras360.py
  - pyproject.toml
findings:
  critical: 2
  warning: 7
  info: 3
  total: 12
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-10-31T12:00:00Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Revisão do diff `ded65f5..HEAD`: a cadeia de recurso (API → JSON-LD → browser → IA), o adaptador da Obramat, o Chrome dedicado por CDP e o degrau IA (`claude -p` / API).

Está bem feito:
- o dinheiro é sempre `Decimal` (`parse_float=Decimal`, `add_vat` sem arredondar, só se arredonda ao mostrar);
- o `claude -p` corre sem shell, recusa `.cmd`/`.bat`, recebe o texto pelo stdin e corre sem ferramentas;
- o CAPTCHA pára a loja até ao fim, incluindo os pedidos que já estavam em fila;
- a escalada NO_STORE fica com os preços da API quando o browser falha.

Há dois problemas que dão resultados enganadores:
1. O degrau IA transforma "a IA não leu nada" em `sem resultados`.
2. A validação das ofertas da IA (T-02-18) é fraca. Um número curto aparece quase sempre algures no texto, e o link nunca é conferido contra o texto enviado.

## Critical Issues

### CR-01: O degrau IA vazio ou todo rejeitado aparece como "sem resultados"

**File:** `src/strata/ai.py:304-307`, `src/strata/search.py:129-131`
**Issue:** `offers_from` devolve `Found(offers, raw=valid, ...)`. Quando a IA devolve `[]` (página por montar, layout mudado, desafio) ou todas as ofertas são rejeitadas, fica `raw == 0`. Depois o `search_store` mostra `status = "sem resultados"` com `detail=""`. A IA só corre quando todos os degraus anteriores falharam (por exemplo, layout mudado em API/JSON-LD/browser). Por isso o estado principal diz que a loja não tem o produto, quando na verdade nenhum método leu a loja. O motivo fica só em `nota:`, e o estado é a primeira coisa que se lê (D-01). Isto contradiz a regra que o próprio `jsonld.py:413` aplica ("falha do degrau, nunca 'sem resultados'") e a restrição "nunca omitir falhas em silêncio". O teste `tests/test_chain.py:339-351` (`test_degrau_ia_uma_so_chamada_sem_pesquisa_alargada`) fixa este comportamento errado.
**Fix:** tratar o resultado vazio da IA como falha do degrau:
```python
# ai.offers_from, no fim
if valid == 0:
    raise StoreError("; ".join(["IA não leu nenhuma oferta válida na página", *notes]))
return Found(offers, raw=valid, hidden=valid - len(offers), notes=notes)
```
Assim o `search_store` cai em `found is None` e devolve `erro` com todos os degraus em `detail`. Atualizar o teste de `test_chain.py:351` para `sr.status == "erro"`.

### CR-02: A validação das ofertas da IA não liga preço nem link ao texto enviado

**File:** `src/strata/ai.py:288-293`
**Issue:** a verificação é `price_s in text`, que só procura uma substring no texto inteiro (até 20 000 caracteres):
- um preço como `"5"`, `"12"` ou `"1"` aparece quase sempre em qualquer página (contagens, medidas, paginação) e passa;
- um preço verdadeiro de *outro* produto também passa, atribuído ao título errado;
- o URL só tem de ser https no host da loja. Um link inventado (`https://www.obramat.pt/produtos/qualquer.html`) ou a própria página de pesquisa (`url: ""` → `urljoin` dá `page_url`) passa, mesmo sem estar no texto.

Isto é a fronteira de confiança que a fase declara (T-02-18), e o que entra aqui é dinheiro mostrado ao utilizador.
**Fix:** exigir que o link esteja no texto como `<URL>` e que o preço venha logo a seguir a esse link, e recusar números sem casas decimais:
```python
anchor = f"<{url}>"
pos = text.find(anchor)
window = text[pos:pos + 400] if pos >= 0 else ""
price = parse_price(price_s) if ("," in price_s or "." in price_s) else None
if pos < 0 or price is None or price_s not in window or parts.scheme != "https" or parts.hostname != host:
    rejected += 1
    continue
```
Afinar o tamanho da janela (e se o preço vem antes ou depois do link) com `tests/fixtures/obramat_search-osb_browser.html`. Juntar um teste com um preço de outro produto e outro com um link que não está no texto.

## Warnings

### WR-01: A IA não sabe a unidade do preço: um preço por m² passa a ser preço de um artigo

**File:** `src/strata/ai.py:297-303`, `src/strata/stores/obras360.py:16-17`
**Issue:** o próprio comentário da Obras 360 diz que a página mostra o preço sem IVA "às vezes por m²". `offers_from` soma 23% e guarda esse número como `Offer.price` ("preço de UM artigo", `models.py:235`). O mesmo acontece com as caixas M2 da Allmat. Depois `content_from_title` pode dar `content` em m² e `in_unit` volta a dividir. O resultado é um preço por unidade errado (dividido duas vezes) ou um "artigo" que na verdade é 1 m².
**Fix:** pedir à IA o texto completo do preço (com `€/m²`, `/un`) e rejeitar, ou marcar como `content_unit` explícito, os preços com sufixo de unidade. Na Obras 360, enquanto não houver isto, não usar o degrau IA: `PAGE_PRICES_WITHOUT_VAT` → levantar `StoreError("página com preço sem IVA e por vezes por m²")`.

### WR-02: Depois de um bloqueio, o JSON-LD repete o mesmo pedido bloqueado

**File:** `src/strata/search.py:54`, `src/strata/search.py:89-92`
**Issue:** quando a API dá `StoreBlocked` (403 DataDome/Cloudflare), a cadeia passa para o JSON-LD com o **mesmo** transporte e o mesmo host. Na Obramat, `search_page(query)` é exatamente o URL que acabou de dar 403. O teste `test_chain.py:334` confirma o padrão `API: HTTP 403; JSON-LD: HTTP 403`. Cada 403 repetido aumenta a hipótese de a DataDome subir para CAPTCHA, o que vai contra "respeitar o ritmo de cada site".
**Fix:** depois de `StoreBlocked` num degrau com `fetch`, saltar os degraus seguintes com o mesmo transporte:
```python
blocked_transport = None
...
if f is blocked_transport:
    tried.append(f"{stage}: saltado (bloqueado antes no pedido simples)")
    kinds.add("bloqueada")
    continue
...
except StoreBlocked as e:
    blocked_transport = f
```

### WR-03: Uma falha a arrancar o Chrome não fica guardada e o Chrome lançado pode ficar aberto

**File:** `src/strata/browser.py:59-86`, `src/strata/browser.py:156-170`
**Issue:**
1. Se o Chrome não abre a porta 9222 (porta ocupada, perfil já aberto sem depuração), `_ctx` fica `None`. Cada chamada seguinte (cada loja, cada item) volta a fazer `Popen` e espera mais 10 s, em série por causa do `_lock`. Com 4 lojas em paralelo, a 4.ª espera cerca de 48 s do prazo de 90 s, em todos os itens.
2. Se o `Popen` correu mas a ligação falhou, `_opened = True` e `_browser = None`. Então `close()` não envia `Browser.close` e o Chrome lançado pela app fica aberto (contra D-06).

**Fix:** guardar o erro (`self._failed = StoreError(...)`; no início de `_context`, `if self._failed: raise self._failed`). Guardar também o `Popen` e, em `close()`, se `_opened and self._browser is None`, chamar `proc.terminate()`.

### WR-04: Ao cancelar o `claude -p`, o processo é morto sem esperar e a pasta temporária pode rebentar

**File:** `src/strata/ai.py:349-361`
**Issue:** no cancelamento pelo prazo da loja, `proc.kill()` é chamado sem `await proc.wait()`, e o bloco `with tempfile.TemporaryDirectory()` fecha logo a seguir. No Windows não se apaga a pasta de trabalho de um processo que ainda está a terminar (`WinError 32`). O `PermissionError` do `__exit__` substitui o `CancelledError`, o `except Exception` de `search.py:101` apanha-o como "IA: PermissionError", e o `asyncio.timeout` deixa de converter o cancelamento em `TimeoutError`. O resultado é o estado errado ("erro" em vez de "tempo esgotado") e um processo por recolher.
**Fix:**
```python
with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as empty:
    ...
    except BaseException:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        await asyncio.shield(proc.wait())
        raise
```

### WR-05: Um produto mal formado da Obramat derruba o degrau API inteiro

**File:** `src/strata/stores/obramat.py:75-80`, `src/strata/stores/obramat.py:116`
**Issue:** `offer_from` só está protegido por `except StoreError` (`obramat.py:173`), mas:
- `p["offer"]["unitprice_ati"]` ausente dá `KeyError`;
- `unitprice_ati: null` dá `Decimal("None")` → `InvalidOperation`;
- `p["sku"]` ausente na mensagem de IVA dá `KeyError`.

Qualquer um destes erros salta o tratamento por produto e faz falhar a pesquisa toda, quando o código já prevê "produtos sem preço ignorados". O mesmo em `parse_tiers`: `Decimal(inp.attributes.get("value"))` com um valor não numérico dá `InvalidOperation` fora do `except StoreError` de `_read_product`, e a loja inteira falha por causa de um escalão.
**Fix:** em `offer_from`, `offer = p.get("offer") or {}`, devolver `None` quando `unitprice_ati`/`unitprice_tf` são `None`, e converter `(KeyError, InvalidOperation)` em `StoreError(f"produto mal formado: {p.get('sku')}")`. Em `parse_tiers`, apanhar `InvalidOperation` e juntar uma nota ("escalão com quantidade ilegível").

### WR-06: O link de compra do JSON-LD não é validado

**File:** `src/strata/jsonld.py:406`
**Issue:** `url=str(node.get("url") or link)` usa o `url` do ld+json sem verificar nada. Pode ser relativo (fica um link partido no terminal) ou de outro domínio (CDN, marketplace). O `link` ao lado já foi validado pelo `PRODUCT_LINK` da loja.
**Fix:** usar sempre `link`, a página de onde o Product foi lido: `url=link`.

### WR-07: `parse_price` multiplica por 10 os preços com uma casa decimal e ponto

**File:** `src/strata/ai.py:251`, `src/strata/ai.py:265-276`
**Issue:** `DOT_DECIMAL` só aceita 2 casas, por isso `"12.5"` → tira o ponto → `125`. `"1e3"` também é aceite (`Decimal("1e3") = 1000`). Confirmado: `parse_price("12.5") == 125`, `parse_price("1e3") == Decimal("1E+3")`.
**Fix:** só aceitar `^\d{1,3}(?:[.\s]\d{3})*(?:,\d{1,2})?$|^\d+(?:[.,]\d{1,2})?$` e devolver `None` em tudo o resto. Juntar `"12.5"` e `"1e3"` aos testes de `parse_price`.

## Info

### IN-01: Percentagem dos escalões guardada e mostrada sem limite de casas

**File:** `src/strata/stores/obramat.py:129`, `src/strata/report.py:153`
**Issue:** `pct = (1 - total / (n * unit_price)) * 100` não arredonda, e `fmt_qty` só normaliza. Com totais que não dão um número redondo, o terminal mostra algo como `−4,761904761904761904761904762%`. As fixtures dão exatamente 5% e não apanham isto.
**Fix:** guardar o total do escalão (exato), em vez da percentagem derivada, ou mostrar com `_fmt(p, 2)` no report.

### IN-02: Cliente `AsyncAnthropic` criado por chamada e nunca fechado

**File:** `src/strata/ai.py:324`
**Issue:** cada chamada abre um cliente httpx novo que nunca é fechado. A forma `output_config={"format": ..., "effort": "low"}` com `anthropic>=2.3` não tem nenhum teste contra o SDK real.
**Fix:** `async with anthropic.AsyncAnthropic() as client:`. Confirmar a assinatura uma vez com uma chamada real.

### IN-03: `past_challenge` atribui à DataDome qualquer erro de leitura

**File:** `src/strata/browser.py:35-44`
**Issue:** qualquer `playwright Error` ao ler a página conta como "interstitial". Ao fim de 10 s dá `StoreBlocked("verificação DataDome não passou")`, também na Allmat (Cloudflare) ou noutra falha sem relação com a DataDome. O motivo mostrado fica enganador.
**Fix:** guardar o último `Error` e, se nunca houve um `var dd=` visto, levantar `StoreError(f"browser: {last_error}")`.

---

_Reviewed: 2026-10-31T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
