"""Degrau JSON-LD sem rede: leitor de ld+json, links de produto e o degrau por loja (STORE-06, D-19)."""

import asyncio
from decimal import Decimal

import pytest

from conftest import FIXTURES
from strata import jsonld
from strata.fetch import StoreError
from strata.stores import allmat, bricomarche, obramat, obras360

SEARCH_PAGE = "allmat_search-page_cimento.html"
LIZ_PAGE = "allmat_product-page_liz-branco_jsonld.html"
LIZ = "https://allmat.pt/produto/liz-cimento-cola-branco-saco-25kg-ref-01-002/"


def read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def page(*blocks: str) -> str:
    return "".join(f'<script type="application/ld+json">{b}</script>' for b in blocks)


def product(offers: str) -> str:
    return f'{{"@type": "Product", "name": "X", "offers": {offers}}}'


def test_products_da_pagina_da_liz():
    nodes = jsonld.products(read(LIZ_PAGE))
    assert [n["name"] for n in nodes] == ["LIZ CIMENTO COLA BRANCO SACO 25KG REF 01.002"]


def test_offer_of_da_liz():
    (node,) = jsonld.products(read(LIZ_PAGE))
    assert jsonld.offer_of(node) == (Decimal("4.72"), "em stock")


def test_moeda_que_nao_e_eur_nao_tem_preco():
    (node,) = jsonld.products(page(product('{"@type": "Offer", "price": "4.72", "priceCurrency": "USD"}')))
    assert jsonld.offer_of(node)[0] is None


@pytest.mark.parametrize("spec", [
    '{"price": 12.5, "priceCurrency": "EUR"}',
    '[{"price": "12.50", "priceCurrency": "EUR"}]',
])
def test_preco_em_price_specification(spec):
    offer = f'[{{"@type": "Offer", "priceSpecification": {spec}, "availability": "https://schema.org/OutOfStock"}}]'
    (node,) = jsonld.products(page(product(offer)))
    assert jsonld.offer_of(node) == (Decimal("12.5"), "esgotado")


@pytest.mark.parametrize("price", ['"0"', '"-1"', '"NaN"', '"abc"', "null"])
def test_preco_invalido_ou_nao_positivo_fica_none(price):
    (node,) = jsonld.products(page(product(f'{{"price": {price}, "priceCurrency": "EUR"}}')))
    assert jsonld.offer_of(node)[0] is None


def test_json_invalido_e_ignorado_e_graph_e_lista_sao_lidos():
    graph = '{"@graph": [{"@type": "WebPage"}, {"@type": ["Product", "Thing"], "name": "A"}]}'
    nodes = jsonld.products(page("{ nao é json", graph, f"[{product('{}')}]"))
    assert [n["name"] for n in nodes] == ["A", "X"]


def test_links_de_produto_da_allmat():
    links = allmat.product_links(read(SEARCH_PAGE))
    assert len(links) == 12 == len(set(links))
    assert links[0] == LIZ
    assert all(u.startswith("https://allmat.pt/produto/") and u.endswith("/") for u in links)


def test_degrau_da_allmat(fake):
    fake.route("?s=cimento", SEARCH_PAGE).route(LIZ, LIZ_PAGE).route("allmat.pt/produto/", b"<html></html>")
    found = asyncio.run(jsonld.rung(allmat)("cimento", fake))
    (o,) = found.offers
    assert (o.title, o.price, o.url) == ("LIZ CIMENTO COLA BRANCO SACO 25KG REF 01.002", Decimal("4.72"), LIZ)
    assert o.vat_origin == "regra da loja" and o.vat_evidence.endswith("(JSON-LD)")
    assert (o.content, o.content_unit, o.stock, o.location) == (Decimal(25), "kg", "em stock", None)
    assert len(fake.calls) == 1 + jsonld.MAX_PAGES
    assert fake.calls[0] == "https://allmat.pt/?s=cimento&post_type=product"
    assert (found.raw, found.hidden) == (1, 0)
    assert "+7 produtos não lidos (limite de 5 páginas)" in found.notes


def test_titulo_que_nao_bate_fica_escondido(fake):
    fake.route("?s=", SEARCH_PAGE).route(LIZ, LIZ_PAGE).route("allmat.pt/produto/", b"<html></html>")
    found = asyncio.run(jsonld.rung(allmat)("tijolo", fake))
    assert (found.offers, found.raw, found.hidden) == ([], 1, 1)


def test_paginas_sem_product_com_preco_escalam(fake):
    fake.route("?s=", SEARCH_PAGE).route(LIZ, StoreError("HTTP 404")).route("allmat.pt/produto/", b"<html></html>")
    with pytest.raises(StoreError, match="nenhum Product com preço.*1 páginas falharam: HTTP 404"):
        asyncio.run(jsonld.rung(allmat)("cimento", fake))


def test_pagina_de_pesquisa_sem_links_escala(fake):
    fake.route("?s=", b"<html><body>Nada</body></html>")
    with pytest.raises(StoreError, match="página de pesquisa sem links de produto"):
        asyncio.run(jsonld.rung(allmat)("cimento", fake))


@pytest.mark.parametrize("store", [bricomarche, obras360])
def test_loja_montada_com_javascript_falha_sem_pedidos(fake, store):
    with pytest.raises(StoreError, match="página montada com JavaScript, sem links de produto"):
        asyncio.run(jsonld.rung(store)("cimento", fake))
    assert fake.calls == []


# --- Obramat: só a lista principal, nunca o carrossel "vistos recentemente" ---

OSB_18 = "https://www.obramat.pt/produtos/placa-osb-3-250x125x1-8cm-25134518.html"


def test_links_de_produto_da_obramat_so_da_lista_principal():
    links = obramat.product_links(read("obramat_search-osb_browser.html"))
    assert len(links) == 7 == len(set(links))
    assert links[1] == OSB_18
    assert all(u.startswith("https://www.obramat.pt/produtos/") and u.endswith(".html") for u in links)
    assert obramat.product_links(read("obramat_search-no-results_browser.html")) == []


def test_products_da_pagina_osb_da_obramat():
    (node,) = jsonld.products(read("obramat_product-osb-18_ctx201_tiers.html"))
    assert node["name"] == "PLACA OSB 3 250X125X1,8CM"
    assert jsonld.offer_of(node) == (Decimal("28.5"), "em stock")


def test_degrau_da_obramat(fake):
    fake.route("obramat.pt/search?q=osb", "obramat_search-osb_browser.html")
    fake.route("obramat.pt/produtos/", "obramat_product-osb-18_ctx201_tiers.html")
    found = asyncio.run(jsonld.rung(obramat)("osb", fake))
    assert len(found.offers) == jsonld.MAX_PAGES
    assert all(o.location == "OBRAMAT Lisboa - Alfragide" and o.vat_evidence.endswith("(JSON-LD)")
               and o.price == Decimal("28.5") and o.url == OSB_18 for o in found.offers)
    assert "+2 produtos não lidos (limite de 5 páginas)" in found.notes
