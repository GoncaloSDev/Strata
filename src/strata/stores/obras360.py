"""Obras 360 (obras360.pt, plataforma Beevo): lista de produtos-pai, depois uma oferta por variante do detalhe."""

import html
import re
from decimal import Decimal

from strata.fetch import StoreError
from strata.models import Found, Offer
from strata.money import add_vat, fmt_qty

NAME = "Obras 360"
BASE = "https://www.obras360.pt"  # domínio com "s" (Pitfall 14)
VAT_PT = Decimal(23)
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
