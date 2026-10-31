"""Obramat sem rede: parsers sobre as páginas gravadas e a pesquisa com o FakeFetcher."""

import asyncio
import time
from decimal import Decimal

from pathlib import Path

import pytest

from strata.fetch import LIMITS, Host, StoreError
from strata.stores import obramat

FIXTURES = Path(__file__).parent / "fixtures"

SEARCH = "obramat.pt/search?q="
OSB18 = "obramat_product-osb-18_ctx201_tiers.html"


def load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def product(ati, tf, sku="1"):
    return {"name": "PLACA OSB 3 250X125X1,8CM", "sku": sku, "url": "/produtos/x-1.html",
            "offer": {"unitprice_ati": Decimal(str(ati)), "unitprice_tf": Decimal(str(tf))}}


def run(query, fake, rank=None):
    return asyncio.run(obramat.search(query, fake, rank))


def test_parse_search_osb():
    products, total = obramat.parse_search(load("obramat_search-osb_browser.html"))
    assert (len(products), total) == (7, 7)


def test_sem_resultados_ignora_o_carrossel_vistos_recentemente():
    page = load("obramat_search-no-results_browser.html")
    assert "ITEM_RECOMMENDED_ZSERPLSP_HISTORY_PRODUCTS" in page  # a armadilha está mesmo na página
    assert obramat.parse_search(page) == ([], 0)


def test_cimento_cola_sem_o_bloco_promocional():
    products, total = obramat.parse_search(load("obramat_search-cimento-cola_endcap_browser.html"))
    assert len(products) == 18 and total == 18


def test_pagina_que_nao_e_de_pesquisa_da_erro():
    page = load("obramat_search-osb_browser.html").replace('"cdl_page_type","value":"Search"',
                                                          '"cdl_page_type","value":"Home"')
    with pytest.raises(StoreError, match="sem lista de resultados"):
        obramat.parse_search(page)


def test_total_sem_lista_da_erro_e_nunca_sem_resultados():
    page = load("obramat_search-no-results_browser.html").replace('"ise_number_result":"0"',
                                                                  '"ise_number_result":"5"')
    with pytest.raises(StoreError, match="diz 5 resultados"):
        obramat.parse_search(page)


def test_offer_from_iva_conferido_e_na_fronteira():
    o = obramat.offer_from(product(28.5, 23.17))
    assert o.price == Decimal("28.5") and o.location == obramat.LOCATION and o.vat_origin == "indicado pela loja"
    assert o.url == "https://www.obramat.pt/produtos/x-1.html"
    assert obramat.offer_from(product(0.34, 0.28)).price == Decimal("0.34")  # desvio 0,0044 €, rácio 1,214
    with pytest.raises(StoreError, match="IVA incoerente"):
        obramat.offer_from(product(28.5, 20))
    assert obramat.offer_from(product(0, 0)) is None


def test_product_info():
    assert obramat.product_info(load(OSB18)) == (Decimal("28.5"), 327, "201")
    assert obramat.product_info(load("obramat_product-tijolo_ctx201_tiers.html")) == (Decimal("0.34"), 1439, "201")


def test_parse_tiers_do_total_da_palete():
    assert obramat.parse_tiers(load(OSB18), Decimal("28.50")) == ([(48, 5)], [])
    # 87,21 € / 270 = 0,323: o "Vendido 0,32 €" arredondado daria 5,9%
    assert obramat.parse_tiers(load("obramat_product-tijolo_ctx201_tiers.html"), Decimal("0.34")) == ([(270, 5)], [])


def test_parse_tiers_incoerente_com_o_preco_fica_em_nota():
    tiers, notes = obramat.parse_tiers(load(OSB18), Decimal("6.90"))
    assert tiers == [] and notes == ["escalão de 48 incoerente com o preço (não lido)"]


def test_parse_tiers_com_iva_do_escalao_incoerente():
    page = load(OSB18).replace("1&nbsp;056,59", "900,00")  # o total sem IVA da palete
    assert obramat.parse_tiers(page, Decimal("28.50")) == ([], ["escalão de 48 com IVA incoerente (não lido)"])


def test_search_so_le_3_paginas_de_produto(fake):
    fake.route(SEARCH, "obramat_search-osb_browser.html").route("/produtos/", OSB18)

    found = run("osb", fake)

    assert sum("/produtos/" in c for c in fake.calls) == 3
    assert found.raw == 7 and found.hidden == 1 and len(found.offers) == 6  # a tinta para piscinas
    assert [o.price for o in found.offers[:3]] == [Decimal("6.9"), Decimal("14.5"), Decimal("14.9")]
    for o in found.offers[:3]:
        assert o.note == "página do produto com outro preço (28,50 €)" and o.tiers == []
        assert o.stock == "desconhecido"
    assert "escalões e stock exato só nas 3 primeiras ofertas (+3 com o preço da pesquisa)" in found.notes


def test_search_le_escaloes_e_stock_da_oferta_certa(fake):
    fake.route(SEARCH, "obramat_search-osb_browser.html").route("/produtos/", OSB18)

    found = run("osb 1,8cm", fake)

    [o] = found.offers
    assert o.tiers == [(48, 5)] and o.stock == f"327 em stock em {obramat.LOCATION}" and o.note == ""
    assert found.notes == []


def test_read_product_osb_18():
    class F:
        async def get_html(self, url, params=None):
            return load(OSB18)

    o = obramat.offer_from(product(28.5, 23.17))
    assert asyncio.run(obramat._read_product(o, F())) is False
    assert o.tiers == [(48, 5)] and o.stock == "327 em stock em OBRAMAT Lisboa - Alfragide"


def test_sem_armazem_na_sessao_da_nota_e_nao_le_escaloes(fake):
    page = load(OSB18).replace('"cdl_user_context_main_store","value":"201"',
                               '"cdl_user_context_main_store","value":"no cookie here"')
    fake.route(SEARCH, "obramat_search-osb_browser.html").route("/produtos/", page.encode("utf-8"))

    found = run("osb 1,8cm", fake)

    assert obramat.NO_STORE in found.notes
    assert found.offers[0].tiers == [] and found.offers[0].stock == "desconhecido"


def test_pagina_de_produto_que_falha_fica_em_nota(fake):
    fake.route(SEARCH, "obramat_search-osb_browser.html").route("/produtos/", StoreError("HTTP 404"))

    found = run("osb 1,8cm", fake)

    assert found.offers[0].note == "página do produto falhou: HTTP 404"


def test_todos_com_iva_incoerente_da_erro(fake):
    page = load("obramat_search-osb_browser.html").replace('"unitprice_tf":23.17', '"unitprice_tf":20')
    fake.route(SEARCH, page.encode("utf-8"))
    with pytest.raises(StoreError, match="IVA incoerente"):
        run("osb 1,8cm", fake)


def test_sem_resultados_nao_le_produtos(fake):
    fake.route(SEARCH, "obramat_search-no-results_browser.html")
    found = run("xyzqwkk", fake)
    assert found.raw == 0 and found.offers == [] and len(fake.calls) == 1


def test_ritmo_da_obramat():
    assert LIMITS["www.obramat.pt"] == (1, 3.0, 2.0)

    async def two_starts():
        h, starts = Host(1, 0.05, 0.0), []
        for _ in range(2):
            async with h:
                starts.append(time.monotonic())
        return starts

    a, b = asyncio.run(two_starts())
    assert b - a >= 0.05
