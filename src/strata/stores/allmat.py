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
from strata.words import title_matches

NAME = "Allmat"
SEARCH_URL = "https://allmat.pt/wp-json/wc/store/v1/products"
PER_PAGE = 100
MAX_PAGES = 3
# shortcut: limite de 10 páginas por pesquisa (as caixas mais baratas), subir se o `verificar` mostrar caixas baratas por ler
MAX_BOX_PAGES = 10
VAT_EVIDENCE = "páginas de produto da Allmat: IVA incluído"
UNIT_LABEL = re.compile(r'class="wd-price-unit"[^>]*>\s*([^<]*?)\s*<')
BOX_AREA = re.compile(r"Produto por caixa:\s*([\d.,]+)\s*m")
INCOHERENT = "área da caixa incoerente com o preço por m²"
DERIVED = "área derivada do preço por m²"
NOT_FOUND = "área da caixa não encontrada na página (rótulo M2 da loja)"
NOT_READ = f"área da caixa não lida (limite de {MAX_BOX_PAGES} páginas por pesquisa)"


def _eur(text: str) -> Decimal | None:
    """"13,74 €" -> 13.74 (a loja usa vírgula decimal e espaço nos milhares)."""
    try:
        d = Decimal(re.sub(r"[^\d,]", "", text).replace(",", "."))
    except InvalidOperation:
        return None
    return d if d.is_finite() else None


def _area(text: str) -> Decimal | None:
    try:
        return Decimal(text.replace(",", "."))
    except InvalidOperation:
        return None


def parse_box(page: str, product_id: int, api_price: Decimal) -> tuple[Decimal | None, Decimal | None, str]:
    """(m² por caixa, €/m², nota). Só dentro de #product-{id} e só o bloco com o preço da caixa igual ao da API."""
    root = LexborHTMLParser(page).css_first(f"#product-{int(product_id)}")
    if root is None:
        return None, None, NOT_FOUND
    for box in root.css(".allmat-loop-price-box"):
        cur = box.css_first(".allmat-loop-current-box")
        if cur is not None and _eur(cur.text()) == api_price:
            m2_node = box.css_first(".allmat-loop-current-m2")
            m2 = _eur(m2_node.text()) if m2_node is not None else None
            break
    else:
        return None, None, NOT_FOUND
    area = None
    for btn in root.css(".elementor-button-text"):
        if m := BOX_AREA.search(btn.text()):
            area = _area(m[1])
            break
    if area is not None and area <= 0:
        area = None
    if m2 is None or m2 <= 0:
        return (area, None, "") if area else (None, None, NOT_FOUND)
    if area is None:
        return api_price / m2, m2, DERIVED
    if abs(api_price - m2 * area) > api_price * Decimal("0.02"):
        return api_price / m2, m2, INCOHERENT
    return area, m2, ""


def parse_products(rows) -> tuple[list[Offer], int, list[tuple[int, Offer]]]:
    """Ofertas, quantos produtos ficaram de fora por preço <= 0 e as caixas "M2" (id, oferta)."""
    offers, no_price, boxes = [], 0, []
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
            note = NOT_READ  # trocada pela leitura da página, se esta caixa estiver entre as mais baratas
        elif label:
            note = f"rótulo da loja: {label}"
        else:
            note = "sem rótulo de unidade na loja"
        stock = ((p.get("stock_availability") or {}).get("text") or "").strip()
        offer = Offer(
            store=NAME,
            title=html.unescape(p["name"]),
            url=p["permalink"],
            price=price,  # sempre o da API: preço de um artigo (uma caixa nos "M2")
            vat_origin="regra da loja",
            vat_evidence=VAT_EVIDENCE,
            content=content,
            content_unit=content_unit,
            stock=stock or "desconhecido",
            note=note,
        )
        offers.append(offer)
        if norm(label) == "m2":
            boxes.append((p["id"], offer))
    return offers, no_price, boxes


async def _read_box(product_id: int, o: Offer, fetch) -> None:
    try:
        page = await fetch.get_html(o.url)
    except StoreError as e:  # StoreBlocked e StoreTimeout sobem: a loja fica bloqueada / tempo esgotado
        o.content, o.content_unit, o.note = None, None, f"página do produto falhou: {e}"
        return
    area, _, o.note = parse_box(page, product_id, o.price)
    o.content, o.content_unit = (area, "m²") if area else (None, None)


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
    offers, no_price, boxes = parse_products(rows)
    if no_price:
        notes.append(f"{no_price} produtos sem preço ignorados")
    boxes.sort(key=lambda b: b[1].price)
    # Em paralelo; o limite por host do Fetcher dá o ritmo. Esperar por todas antes de relançar a 1.ª falha.
    results = await asyncio.gather(*(_read_box(pid, o, fetch) for pid, o in boxes[:MAX_BOX_PAGES]),
                                   return_exceptions=True)
    for r in results:
        if isinstance(r, BaseException):
            raise r
    return Found(offers=offers, raw=raw, hidden=raw - len(rows), notes=notes)
