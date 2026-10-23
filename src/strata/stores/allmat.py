"""Allmat (allmat.pt): WooCommerce Store API, preços em cêntimos já com IVA."""

import html
import re
from decimal import Decimal

from strata.models import Found, Offer
from strata.money import content_from_title, from_minor
from strata.text import norm
from strata.words import title_matches

NAME = "Allmat"
SEARCH_URL = "https://allmat.pt/wp-json/wc/store/v1/products"
PER_PAGE = 100
MAX_PAGES = 3
VAT_EVIDENCE = "páginas de produto da Allmat: IVA incluído"
UNIT_LABEL = re.compile(r'class="wd-price-unit"[^>]*>\s*([^<]*?)\s*<')


INCOHERENT = "área da caixa incoerente com o preço por m²"


def parse_box(page: str, product_id: int, api_price: Decimal) -> tuple[Decimal | None, Decimal | None, str]:
    return None, None, ""


def parse_products(rows) -> tuple[list[Offer], int]:
    """Ofertas e quantos produtos ficaram de fora por preço <= 0."""
    offers, no_price = [], 0
    for p in rows:
        prices = p["prices"]
        price = from_minor(prices["price"], prices["currency_minor_unit"])
        if price <= 0:
            no_price += 1
            continue
        m = UNIT_LABEL.search(p.get("price_html") or "")
        label = m[1] if m else ""
        content, content_unit, note = None, None, ""
        if norm(label) == "unid":
            content, content_unit = content_from_title(html.unescape(p["name"])) or (Decimal(1), "un")
        elif norm(label) == "m2":
            note = "rótulo M2 da loja: área da caixa não lida"
        elif label:
            note = f"rótulo da loja: {label}"
        else:
            note = "sem rótulo de unidade na loja"
        stock = ((p.get("stock_availability") or {}).get("text") or "").strip()
        offers.append(Offer(
            store=NAME,
            title=html.unescape(p["name"]),
            url=p["permalink"],
            price=price,
            vat_origin="regra da loja",
            vat_evidence=VAT_EVIDENCE,
            content=content,
            content_unit=content_unit,
            stock=stock or "desconhecido",
            note=note,
        ))
    return offers, no_price


async def search(query: str, fetch) -> Found:
    rows, notes = [], []
    for page in range(1, MAX_PAGES + 1):
        data = await fetch.get_json(SEARCH_URL, {"search": query, "per_page": PER_PAGE, "page": page})
        if not isinstance(data, list):
            raise ValueError("resposta da Allmat não é uma lista de produtos")
        rows.extend(data)
        if len(data) < PER_PAGE:
            break
    else:
        notes.append(f"mais produtos na loja não lidos (limite de {PER_PAGE * MAX_PAGES})")
    raw = len(rows)
    rows = [p for p in rows if title_matches(query, html.unescape(p.get("name") or ""))]  # D-15
    offers, no_price = parse_products(rows)
    if no_price:
        notes.append(f"{no_price} produtos sem preço ignorados")
    return Found(offers=offers, raw=raw, hidden=raw - len(rows), notes=notes)
