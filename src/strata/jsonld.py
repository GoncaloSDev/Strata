"""Degrau JSON-LD: página de pesquisa → links de produto da loja → Product/Offer do ld+json de cada página."""

# Só lojas cujo JSON-LD traz o preço com IVA definem product_links (o da Obras 360 é sem IVA, ARCHITECTURE Pattern 3).

import asyncio
import html
import json
from decimal import Decimal, InvalidOperation

from selectolax.lexbor import LexborHTMLParser

from strata.fetch import StoreError
from strata.models import Found, Offer
from strata.money import content_from_title
from strata.words import title_matches

# shortcut: só 5 páginas de produto por (item, loja); subir se o verificar mostrar baratos de fora
MAX_PAGES = 5
JS_PAGE = "página montada com JavaScript, sem links de produto"  # D-19


def _walk(x, out: list[dict]) -> None:
    if isinstance(x, list):
        for y in x:
            _walk(y, out)
    elif isinstance(x, dict):
        t = x.get("@type")
        if t == "Product" or (isinstance(t, list) and "Product" in t):
            out.append(x)
        else:
            _walk(x.get("@graph"), out)


def products(page: str) -> list[dict]:
    """Nós Product de todos os script application/ld+json (topo, listas e @graph); JSON inválido salta."""
    out: list[dict] = []
    for s in LexborHTMLParser(page).css('script[type="application/ld+json"]'):
        try:
            data = json.loads(s.text(), parse_float=Decimal, strict=False)
        except ValueError:
            continue
        _walk(data, out)
    return out


def _first(x):
    return (x[0] if x else None) if isinstance(x, list) else x


def offer_of(node: dict) -> tuple[Decimal | None, str]:
    """(preço em EUR > 0 ou None, stock) do primeiro Offer do Product."""
    offer = _first(node.get("offers"))
    if not isinstance(offer, dict):
        return None, "desconhecido"
    spec = _first(offer.get("priceSpecification"))
    spec = spec if isinstance(spec, dict) else {}
    value = offer.get("price")
    if value is None:
        value = spec.get("price")
    availability = str(offer.get("availability") or "")
    stock = ("em stock" if availability.endswith("InStock")
             else "esgotado" if availability.endswith("OutOfStock") else "desconhecido")
    if (offer.get("priceCurrency") or spec.get("priceCurrency")) != "EUR" or value is None or isinstance(value, bool):
        return None, stock
    try:
        price = Decimal(str(value))
    except InvalidOperation:
        return None, stock
    return (price if price.is_finite() and price > 0 else None), stock


def rung(store):
    """async search(query, fetch, rank=None) -> Found, com a assinatura dos adaptadores."""

    async def search(query: str, fetch, rank: str | None = None) -> Found:
        links_of = getattr(store, "product_links", None)
        if links_of is None:
            raise StoreError(JS_PAGE)
        links = links_of(await fetch.get_html(store.search_page(query)))
        if not links:  # pode ser layout mudado, não "sem resultados": escala (D-14)
            raise StoreError("página de pesquisa sem links de produto")
        read = links[:MAX_PAGES]
        # O limite por host do Fetcher dá o ritmo. Esperar por todas antes de relançar a 1.ª falha.
        pages = await asyncio.gather(*(fetch.get_html(u) for u in read), return_exceptions=True)
        offers, failed, raw = [], [], 0
        for link, page in zip(read, pages):
            if isinstance(page, StoreError):  # StoreBlocked, StoreCaptcha e StoreTimeout sobem
                failed.append(page)
                continue
            if isinstance(page, BaseException):
                raise page
            for node in products(page):
                price, stock = offer_of(node)
                if price is None:
                    continue
                raw += 1
                title = " ".join(html.unescape(str(node.get("name") or "")).split())
                if not title_matches(query, title):  # D-15 da fase 1
                    continue
                content, content_unit = content_from_title(title) or (None, None)
                offers.append(Offer(store=store.NAME, title=title, url=str(node.get("url") or link), price=price,
                                    vat_origin="regra da loja", vat_evidence=f"{store.VAT_EVIDENCE} (JSON-LD)",
                                    content=content, content_unit=content_unit, stock=stock,
                                    location=getattr(store, "LOCATION", None)))
        notes = []
        if failed:
            notes.append(f"{len(failed)} páginas falharam: {failed[0]}")
        if raw == 0:  # links sem Product com preço: falha do degrau, nunca "sem resultados"
            raise StoreError("; ".join([f"nenhum Product com preço nas {len(read)} páginas de produto", *notes]))
        if len(links) > MAX_PAGES:
            notes.append(f"+{len(links) - MAX_PAGES} produtos não lidos (limite de {MAX_PAGES} páginas)")
        return Found(offers, raw=raw, hidden=raw - len(offers), notes=notes)

    return search
