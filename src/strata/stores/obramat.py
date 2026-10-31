"""Obramat (obramat.pt, plataforma ADEO): pesquisa direta /search?q=, preços do dataTms, um só armazém."""

import asyncio
import html
import json
import re
from decimal import Decimal
from urllib.parse import urljoin

from selectolax.lexbor import LexborHTMLParser

from strata.fetch import StoreError
from strata.models import Found, Offer
from strata.money import add_vat, content_from_title, fmt_eur, fmt_qty
from strata.words import title_matches, words

NAME = "Obramat"
BASE = "https://www.obramat.pt"
SEARCH_URL = BASE + "/search"
# shortcut: Portugal tem um só armazém (contexto 201, D-18/A8); rever se a janela "Escolha o seu Armazém" do site mostrar outro
LOCATION = "OBRAMAT Lisboa - Alfragide"
VAT_EVIDENCE = "unitprice_ati (com IVA) conferido com unitprice_tf + 23%"
VAT_TOLERANCE = Decimal("0.02")  # em euros, nunca o rácio: preços pequenos arredondados dão 1,214 (Pitfall 4)
# shortcut: escalões e stock exato só nas 3 primeiras ofertas (D-18, uma navegação cada); subir se a lista de 10 itens sobrar tempo nos 5 min
K = 3
CONTEXT = "201"  # armazém de Alfragide na sessão; sem ele a página não mostra escalões nem stock exato
NO_STORE = "escalões e stock por ler: escolha o armazém OBRAMAT Lisboa - Alfragide no Chrome dedicado"
# Total da palete; o "$" deixa de fora "… € IVA por m²". O preço por unidade do escalão vem arredondado.
TIER_TOTAL = re.compile(r"Ou Vendido ([\d .]+,\d{2}) € IVA$")
TIER_NET = re.compile(r"Ou Vendido ([\d .]+,\d{2}) € sem IVA$")


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


def _total(m) -> Decimal:
    return Decimal(m[1].replace(" ", "").replace(",", "."))


def product_info(page: str) -> tuple[Decimal | None, int | None, str | None]:
    """(preço com IVA, stock no armazém, contexto do armazém da sessão) da página de produto; o que faltar é None."""
    ati = stock = ctx = None
    found = False
    for s in LexborHTMLParser(page).css("script.dataTms"):
        d = _tms(s)
        if not found and d.get("cdl_products"):
            found = True
            offer = d["cdl_products"][0].get("offer") or {}
            if offer.get("unitprice_ati") is not None:
                ati = Decimal(str(offer["unitprice_ati"]))
            stock = next((int(x["stock"]) for x in offer.get("available_deliveries") or []
                          if x.get("type") == "storeDelivery" and x.get("stock") is not None), None)
        if ctx is None and "cdl_user_context_main_store" in d:
            ctx = str(d["cdl_user_context_main_store"])
    return ati, stock, ctx


def parse_tiers(page: str, unit_price: Decimal) -> tuple[list[tuple[Decimal, Decimal]], list[str]]:
    """[(a partir de N, -%)] a partir do total da palete com IVA, e notas dos escalões que não se leram."""
    tiers, notes = [], []
    for tile in LexborHTMLParser(page).css(".o-priceByQuantity__tileItem"):
        inp = tile.css_first("input")
        n = Decimal(inp.attributes.get("value") or "1") if inp is not None else Decimal(1)
        if n <= 1:
            continue
        texts = [" ".join(x.text().split()) for x in tile.css(".kl-hidden-accessibility")]  # split() desfaz o espaço fino
        total = next((m for t in texts if (m := TIER_TOTAL.search(t))), None)
        net = next((m for t in texts if (m := TIER_NET.search(t))), None)
        if total is None:
            notes.append(f"escalão de {fmt_qty(n)} sem total lido")
            continue
        total = _total(total)
        if net is not None and abs(add_vat(_total(net), 23) - total) > VAT_TOLERANCE:
            notes.append(f"escalão de {fmt_qty(n)} com IVA incoerente (não lido)")
            continue
        pct = (1 - total / (n * unit_price)) * 100  # sem arredondar (Pitfall 5): o report mostra fmt_qty
        if not 0 < pct < 100:
            notes.append(f"escalão de {fmt_qty(n)} incoerente com o preço (não lido)")
            continue
        tiers.append((n, pct))
    return tiers, notes


async def _read_product(o: Offer, fetch) -> bool:
    """Escalões e stock exato da página de produto; True quando a sessão não tem o armazém escolhido."""
    try:
        page = await fetch.get_html(o.url)
    except StoreError as e:  # StoreBlocked e StoreTimeout sobem: a loja fica bloqueada / tempo esgotado
        o.note = f"página do produto falhou: {e}"
        return False
    ati, stock, ctx = product_info(page)
    if ctx != CONTEXT:
        return True
    if ati is not None and ati != o.price:  # nunca trocar o preço da oferta pelo de outra página
        o.note = f"página do produto com outro preço ({fmt_eur(ati)})"
        return False
    o.tiers, notes = parse_tiers(page, o.price)
    if stock is not None and stock > 0:
        o.stock = f"{stock} em stock em {LOCATION}"
    elif stock == 0:
        o.stock = f"esgotado em {LOCATION}"
    o.note = "; ".join(notes)
    return False


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
    need = words(rank or query)  # na alargada, o produto da linha conta primeiro (WR-17)
    offers.sort(key=lambda o: (-len(need & words(o.title)), o.price))
    # Com LIMITS a 1 na Obramat, o Fetcher serializa sozinho. Esperar por todas antes de relançar a 1.ª falha.
    results = await asyncio.gather(*(_read_product(o, fetch) for o in offers[:K]), return_exceptions=True)
    for r in results:
        if isinstance(r, BaseException):
            raise r
    if any(results):
        notes.append(NO_STORE)
    if len(offers) > K:
        notes.append(f"escalões e stock exato só nas {K} primeiras ofertas (+{len(offers) - K} com o preço da pesquisa)")
    if total > len(products):
        notes.append(f"mais {total - len(products)} produtos na loja não lidos (só a 1.ª página: {len(products)})")
    return Found(offers, raw=len(products), hidden=len(products) - len(kept), notes=notes)
