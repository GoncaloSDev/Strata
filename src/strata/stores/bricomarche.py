"""Bricomarché (bricomarche.pt): WooCommerce Store API, um preço por loja física (variações)."""

import asyncio
import html
import re
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

from strata.models import Found, Offer
from strata.money import content_from_title, fmt_eur, from_minor
from strata.words import title_matches

NAME = "Bricomarché"
BASE = "https://www.bricomarche.pt"
SEARCH_URL = BASE + "/wp-json/wc/store/v1/products"
PER_PAGE = 100
MAX_PAGES = 3
# shortcut: só os 10 pais mais baratos pelo preço do pai (A2) pedem variações; subir se o `verificar` mostrar baratos de fora
K = 10
VAT_EVIDENCE = "loja B2C: preço final com IVA (DL 138/90); o site não mostra o IVA"
STOCK_N = re.compile(r"^(\d+) em stock")


def _minor(value, prices: dict) -> Decimal | None:
    if value in (None, ""):
        return None
    return from_minor(value, prices["currency_minor_unit"])


def parent_key(p) -> Decimal | None:
    """Só para escolher que pais expandir: o menor > 0 entre o price e o price_range.min_amount."""
    prices = p["prices"]
    vals = [_minor(prices.get("price"), prices), _minor((prices.get("price_range") or {}).get("min_amount"), prices)]
    vals = [v for v in vals if v is not None and v > 0]
    return min(vals) if vals else None


def _loja(row) -> str:
    return (parse_qs(urlsplit(row.get("permalink") or "").query).get("attribute_pa_loja") or [""])[0]


def _price(row) -> Decimal:
    prices = row["prices"]
    return _minor(prices.get("price"), prices) or Decimal(0)


def _valid(rows) -> list:
    # shortcut: a variação "master" não é uma loja física (989 em stock na amostra); rever se a Bricomarché explicar o que é
    return [r for r in rows if _price(r) > 0 and _loja(r) and _loja(r) != "master"]


def cheapest(rows):
    """A variação de loja física com o menor preço > 0 (empates: a primeira da loja), ou None."""
    return min(_valid(rows), key=_price, default=None)


def has_stock(row) -> bool:
    sa = row.get("stock_availability") or {}
    text, cls = (sa.get("text") or "").strip(), sa.get("class") or ""
    if "out-of-stock" in cls:
        return False
    if m := STOCK_N.match(text):
        return int(m[1]) > 0  # a amostra tem "0 em stock" com a classe in-stock
    return "in-stock" in cls


def store_link(row) -> tuple[str, str]:
    """Página do produto nessa loja; nunca o permalink com ?attribute_pa_loja= (vai para /escolher-loja/)."""
    slug = urlsplit(row["permalink"]).path.rstrip("/").split("/")[-1]
    return f"{BASE}/{_loja(row)}/produto/{slug}/", (row.get("variation") or "").removeprefix("Loja: ").strip()


def offer_from(parent, rows) -> Offer | None:
    best = cheapest(rows)
    if best is None:
        return None
    title = html.unescape(parent["name"])
    url, location = store_link(best)
    note = ""
    if not has_stock(best):
        with_stock = cheapest([r for r in rows if has_stock(r)])
        if with_stock is not None:
            note = f"com stock: {fmt_eur(_price(with_stock))} em {store_link(with_stock)[1]}"
    content, content_unit = content_from_title(title) or (Decimal(1), "un")
    stock = ((best.get("stock_availability") or {}).get("text") or "").strip()
    return Offer(
        store=NAME,
        title=title,
        url=url,
        price=_price(best),  # sempre o de uma variação por loja física, nunca o do pai
        vat_origin="regra da loja",
        vat_evidence=VAT_EVIDENCE,
        content=content,
        content_unit=content_unit,
        stock=stock or "desconhecido",
        location=location,
        note=note,
    )


async def _pages(fetch, params: dict) -> tuple[list, bool]:
    """Todas as páginas até uma com menos de PER_PAGE linhas; True se parou no limite de MAX_PAGES."""
    rows = []
    for page in range(1, MAX_PAGES + 1):
        data = await fetch.get_json(SEARCH_URL, {**params, "per_page": PER_PAGE, "page": page})
        if not isinstance(data, list):
            raise ValueError("resposta da Bricomarché não é uma lista de produtos")
        rows.extend(data)
        if len(data) < PER_PAGE:
            return rows, False
    return rows, True


async def _variations(parent_id: int, fetch) -> tuple[list, bool]:
    # Nunca search + type=variation (~10 s por página); a API não ordena variações por preço, lê-se tudo.
    return await _pages(fetch, {"type": "variation", "parent": parent_id})


async def search(query: str, fetch) -> Found:
    parents, truncated = await _pages(fetch, {"search": query})
    notes = [f"mais produtos na loja não lidos (limite de {PER_PAGE * MAX_PAGES})"] if truncated else []
    raw = len(parents)
    parents = [p for p in parents if title_matches(query, html.unescape(p.get("name") or ""))]  # D-15
    keyed = [(k, p) for p in parents if (k := parent_key(p)) is not None]
    no_price = len(parents) - len(keyed)
    keyed.sort(key=lambda t: t[0])  # o preço do pai só escolhe quem expandir; nunca é mostrado
    chosen = [p for _, p in keyed[:K]]
    # Em paralelo; o limite por host do Fetcher dá o ritmo. Esperar por todas antes de relançar a 1.ª falha.
    results = await asyncio.gather(*(_variations(p["id"], fetch) for p in chosen), return_exceptions=True)
    offers = []
    for p, r in zip(chosen, results):
        if isinstance(r, BaseException):
            raise r
        rows, cut = r
        if cut:
            notes.append(f"variações de '{html.unescape(p['name'])}' além de {PER_PAGE * MAX_PAGES} não lidas")
        if (o := offer_from(p, rows)) is None:
            no_price += 1
        else:
            offers.append(o)
    if no_price:
        notes.append(f"{no_price} produtos sem preço")
    if len(keyed) > K:
        notes.append(f"+{len(keyed) - K} produtos não expandidos (limite de {K} por pesquisa)")
    return Found(offers=offers, raw=raw, hidden=raw - len(parents), notes=notes)
