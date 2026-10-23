"""Bricomarché (bricomarche.pt): WooCommerce Store API, um preço por loja física (variações)."""

import html
import re
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

from strata.models import Found, Offer
from strata.money import content_from_title, fmt_eur, from_minor

NAME = "Bricomarché"
BASE = "https://www.bricomarche.pt"
SEARCH_URL = BASE + "/wp-json/wc/store/v1/products"
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


async def search(query: str, fetch) -> Found:
    return Found(offers=[], raw=0)
