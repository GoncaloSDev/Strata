"""Obras 360 (obras360.pt, plataforma Beevo): lista de produtos-pai, depois uma oferta por variante do detalhe."""

import asyncio
import html
import re
from decimal import Decimal

from strata.fetch import StoreError, full_url
from strata.models import Found, Offer
from strata.money import add_vat, fmt_qty
from strata.words import broadened, title_matches, words

NAME = "Obras 360"
BASE = "https://www.obras360.pt"  # domínio com "s" (Pitfall 14)
VAT_PT = Decimal(23)
PER_PAGE = 48
MAX_PAGES = 3
# shortcut: só os 20 pais mais baratos por artigo (A3) pedem o detalhe; subir se o `verificar` mostrar baratos de fora
K = 20
# shortcut: 27 é o ID numérico do widget de detalhe (A4), lido à mão; o `verificar` (01-06) apanha uma mudança
DETAILS_PATH = "/api/latest/dot/shop/product-details/27"
WIDGET = re.compile(r'"widget_slug":"product-list","widget_instance_id":"([0-9a-f-]+)"')
TAG = re.compile(r"<[^>]+>")
# visible_sell_unit.description -> unidade-base; "ML" fica de fora (metro linear ou mililitro?)
UNIT_MAP = {"M2": "m²", "UN": "un", "KG": "kg", "L": "L", "LT": "L", "M": "m"}


def widget_id(page: str) -> str:
    m = WIDGET.search(page)
    if not m:
        raise StoreError("ID do widget da pesquisa não encontrado (página mudou?)")
    return m[1]


def parse_list(d) -> tuple[list, int]:
    if not d.get("success"):
        raise StoreError("product-list com success falso (widget mudou?)")
    p = d["meta_data"]["protected"]
    return p.get("products") or [], int(p.get("total_products") or 0)


def _stock(n, parent) -> str:
    if int(n or 0) > 0:
        return f"{int(n)} em stock"
    msg = " ".join(html.unescape(TAG.sub("", parent.get("availability_days_message") or "")).split())
    return f"esgotado ({msg})" if msg else "esgotado"


def _designation(sel: dict, value_id: str) -> str | None:
    return next((a["values"][value_id]["designation"] for a in sel.values()
                 if value_id in (a.get("values") or {})), None)


def offers_from_details(d, parent) -> list[Offer]:
    """Uma oferta por variante, com o preço do artigo sem IVA × (1 + taxa da loja), confirmado pela loja."""
    avp = ((d.get("meta_data") or {}).get("protected") or {}).get("attribute_values_prices")
    if not d.get("success") or not isinstance(avp, dict) or not avp:  # vazio vem [] (PHP)
        raise StoreError("product-details sem variantes (produto ou widget mudou?)")
    prod = parent["product"]
    name = " ".join(prod["name"].split())
    sel = (prod.get("attributes") or {}).get("_selectionsAttributes") or {}
    sell = (prod.get("visible_sell_unit") or {}).get("description") or ""
    offers = []
    for value_id, v in avp.items():
        base, item = v["prices"], v["prices_with_convertion_factor"]  # sic: "convertion" no detalhe
        rate = Decimal(base["tax_percentage"])
        price = add_vat(item["final_price_unformatted"], rate)
        if abs(price - Decimal(item["final_price_with_tax_unformatted"])) > Decimal("0.01"):
            raise StoreError(f"IVA incoerente na variante {v.get('sku')}")
        notes = []
        if rate != VAT_PT:
            notes.append(f"IVA da loja {fmt_qty(rate)}%: não convertido para 23%")
        unit = UNIT_MAP.get(sell.strip().upper())
        if unit is None:
            notes.append(f"unidade da loja '{sell}' sem conversão")
        tiers = []
        for disc in base.get("discounts") or []:
            if disc.get("class") != "DiscountByQuantity":
                continue
            if disc.get("calc_value_mathop") != "-%":
                notes.append("desconto por quantidade noutro formato (não lido)")
                continue
            tiers += [(Decimal(lv["unity"]), Decimal(lv["value"])) for lv in disc.get("levels") or []]
        offers.append(Offer(
            store=NAME,
            title=f"{name} — {_designation(sel, value_id) or 'ref. ' + str(v.get('sku'))}",
            url=f"{BASE}/{v['segment']}",
            price=price,
            vat_origin="indicado pela loja",
            vat_evidence=f"tax_percentage={fmt_qty(rate)}",
            content=Decimal(base["conversion_factor"]) if unit else None,
            content_unit=unit,
            stock=_stock(v.get("stock"), prod),
            tiers=tiers,
            note="; ".join(notes),
        ))
    return offers


def _list_price(p) -> Decimal | None:
    v = ((p.get("product") or {}).get("prices_with_conversion_factor") or {}).get("final_price_unformatted")
    return None if v is None else Decimal(v)


async def search(query: str, fetch, rank: str | None = None) -> Found:
    widget = fetch.cache.get("obras360_widget")
    if widget is None:  # uma vez por execução: a página tem ~700 KB
        widget = widget_id(await fetch.get_html(BASE + "/pesquisa", {"search": query}))
        fetch.cache["obras360_widget"] = widget
    # has_more e page_count da loja não servem: pagina-se por total_products
    products, total, page = [], 0, 0
    while page < MAX_PAGES and (page == 0 or page * PER_PAGE < total):
        page += 1
        rows, total = parse_list(await fetch.get_json(
            f"{BASE}/api/latest/dot/shop/product-list/{widget}",
            {"search": query, "items_per_page": PER_PAGE, "page": page}))
        products += rows
        if not rows:
            break
    notes = []
    if page * PER_PAGE < total and products:
        notes.append(f"mais produtos na loja não lidos (limite de {PER_PAGE * MAX_PAGES})")
    # D-15 em dois níveis: a medida só existe na designação da variante, por isso o pai escolhe-se sem medidas
    loose = broadened(query) or query
    kept = [p for p in products if title_matches(loose, p["product"]["name"])]
    # Nenhum preço da lista é mostrado (só traz a variante mais barata); só escolhe quem expandir.
    # Primeiro os pais com mais palavras da pesquisa ("M8" em "parafuso m8x40", onde o "40" só está na
    # variante): a solta só serve para não perder os pais cuja medida está na variante (CR-04, CR-06).
    need = words(rank or query)  # na alargada, o produto da linha (WR-17)
    kept.sort(key=lambda p: (-len(need & words(p["product"]["name"])), _list_price(p) is None,
                             _list_price(p) or 0))
    chosen = kept[:K]
    results = await asyncio.gather(*(fetch.get_json(BASE + DETAILS_PATH, {
        "_beevo_decoded_params[0][product_id]": p["product"]["product"]["product_id"]}) for p in chosen),
        return_exceptions=True)
    offers, failed = [], []
    for p, r in zip(chosen, results):
        try:
            if isinstance(r, BaseException):
                raise r
            offers += offers_from_details(r, p)
        except StoreError as e:  # StoreBlocked/StoreTimeout e o resto sobem: a loja fica bloqueada ou erro
            failed.append(e)
    if failed and len(failed) == len(chosen):
        raise failed[0]
    if failed:
        notes.append(f"{len(failed)} produtos sem detalhe: {failed[0]}")
    if len(kept) > K:
        notes.append(f"+{len(kept) - K} produtos não expandidos (limite de {K} por pesquisa)")
    # shortcut: uma gama no nome do pai ("9-30MM") faz "30mm" bater em todas as variantes; o exato/parecido da Phase 3 separa
    shown = [o for o in offers if title_matches(query, o.title)]  # o.title = pai + " — " + designação
    hidden = len(products) - len(kept) + len(offers) - len(shown)  # variantes cortadas também contam (D-02)
    return Found(offers=shown, raw=total, hidden=hidden, notes=notes)


def search_page(query: str) -> str:
    """Página de pesquisa para pessoas, para continuar à mão (D-07)."""
    return full_url(BASE + "/pesquisa", {"search": query})
