"""Obramat (obramat.pt, plataforma ADEO): pesquisa direta /search?q=, preços do dataTms, um só armazém."""

import html
import json
from decimal import Decimal
from urllib.parse import urljoin

from selectolax.lexbor import LexborHTMLParser

from strata.fetch import StoreError
from strata.models import Found, Offer
from strata.money import add_vat, content_from_title
from strata.words import title_matches

NAME = "Obramat"
BASE = "https://www.obramat.pt"
SEARCH_URL = BASE + "/search"
# shortcut: Portugal tem um só armazém (contexto 201, D-18/A8); rever se a janela "Escolha o seu Armazém" do site mostrar outro
LOCATION = "OBRAMAT Lisboa - Alfragide"
VAT_EVIDENCE = "unitprice_ati (com IVA) conferido com unitprice_tf + 23%"
VAT_TOLERANCE = Decimal("0.02")  # em euros, nunca o rácio: preços pequenos arredondados dão 1,214 (Pitfall 4)


def _tms(node) -> dict:
    return {e["name"]: e["value"] for e in json.loads(node.text(), parse_float=Decimal)}


def parse_search(page: str) -> tuple[list[dict], int]:
    """(produtos com preço da lista principal, total de resultados da loja)."""
    root = LexborHTMLParser(page)
    meta = {}
    for s in root.css("script.dataTms"):
        if '"cdl_page_type"' in s.text():
            meta.update(_tms(s))
    if meta.get("cdl_page_type") != "Search":
        raise StoreError("página da Obramat sem lista de resultados (layout mudou?)")
    total = int(meta["cdl_search"]["ise_number_result"])
    products = []
    # Só filhos diretos: o carrossel "vistos recentemente" e o bloco promocional têm listas próprias.
    for s in root.css("ol#guidance-product-list > li[data-reflm] > script.dataTms"):
        products += _tms(s).get("cdl_products_list", [])
    if total > 0 and not products:
        raise StoreError(f"a Obramat diz {total} resultados mas a página não tem a lista (layout mudou?)")
    return products, total


def _title(p: dict) -> str:
    return " ".join(html.unescape(p["name"]).split())


def offer_from(p: dict) -> Offer | None:
    """Oferta a preço com IVA (unitprice_ati), conferido com o sem IVA; None sem preço."""
    ati = Decimal(str(p["offer"]["unitprice_ati"]))
    tf = Decimal(str(p["offer"]["unitprice_tf"]))
    if ati <= 0:
        return None
    if abs(add_vat(tf, 23) - ati) > VAT_TOLERANCE:
        raise StoreError(f"IVA incoerente no produto {p['sku']}")
    title = _title(p)
    content, content_unit = content_from_title(title) or (Decimal(1), "un")
    # D-01/D-02: com um só armazém, a loja física mais barata com stock é sempre Alfragide
    return Offer(store=NAME, title=title, url=urljoin(BASE, p["url"]), price=ati, vat_origin="indicado pela loja",
                 vat_evidence=VAT_EVIDENCE, content=content, content_unit=content_unit, stock="desconhecido",
                 location=LOCATION)


async def search(query: str, fetch, rank: str | None = None) -> Found:
    page = await fetch.get_html(SEARCH_URL, {"q": query})
    products, total = parse_search(page)
    if total == 0:
        return Found([], raw=0)
    kept = [p for p in products if title_matches(query, _title(p))]  # D-15
    offers, failed, no_price = [], [], 0
    for p in kept:
        try:
            o = offer_from(p)
        except StoreError as e:
            failed.append(e)
            continue
        if o is None:
            no_price += 1
        else:
            offers.append(o)
    if failed and len(failed) == len(kept):
        raise failed[0]
    notes = []
    if failed:
        notes.append(f"{len(failed)} produtos com erro: {failed[0]}")
    if no_price:
        notes.append(f"{no_price} produtos sem preço ignorados")
    if total > len(products):
        notes.append(f"mais {total - len(products)} produtos na loja não lidos (só a 1.ª página: {len(products)})")
    return Found(offers, raw=len(products), hidden=len(products) - len(kept), notes=notes)
