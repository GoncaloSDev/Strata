"""Allmat: caixas de pavimento com a área lida na página do produto (STORE-02) e as amostras da pesquisa."""

import asyncio
from decimal import Decimal
from pathlib import Path

from strata.fetch import StoreError
from strata.models import Item
from strata.money import fmt_unit_price, per_unit
from strata.search import search_store
from strata.stores import allmat

PAGE = (Path(__file__).parent / "fixtures" / "allmat_product-page_39233_box.html").read_text(encoding="utf-8")
SEARCH = "allmat.pt/wp-json/wc/store/v1/products?search="
SPLENDOR = "allmat.pt/produto/splendor/"
NOT_FOUND = "área da caixa não encontrada na página (rótulo M2 da loja)"
LIMIT = "área da caixa não lida (limite de 10 páginas por pesquisa)"


def m2_row(pid=39233, cents="1374", name="SPLENDOR PAVIMENTO", slug="splendor"):
    return {
        "id": pid,
        "name": name,
        "permalink": f"https://allmat.pt/produto/{slug}/",
        "prices": {"price": cents, "currency_minor_unit": 2},
        "price_html": '<span class="amount">13,74 €</span>\t<span class="wd-price-unit">M2</span>',
        "stock_availability": {"text": "12 em stock"},
    }


def run_search(fake, rows, query="pavimento"):
    fake.route(SEARCH + query, rows)
    return asyncio.run(allmat.search(query, fake))


def test_caixa_com_area_declarada(fake):
    fake.route(SPLENDOR, "allmat_product-page_39233_box.html")
    (o,) = run_search(fake, [m2_row()]).offers
    assert o.price == Decimal("13.74")
    assert (o.content, o.content_unit) == (Decimal("1.37"), "m²")
    assert fmt_unit_price(per_unit(o), o.content_unit) == "10,03 €/m²"
    assert o.note == ""


def test_bloco_escolhido_pelo_preco_da_api():
    area, m2, note = allmat.parse_box(PAGE, 39233, Decimal("13.74"))
    assert (area, m2, note) == (Decimal("1.37"), Decimal("9.99"), "")
    # 25,74 € é o 2.º bloco (produto relacionado): nunca o primeiro bloco por defeito
    area, m2, _ = allmat.parse_box(PAGE, 39233, Decimal("25.74"))
    assert m2 == Decimal("13.99")


def test_preco_da_api_sem_bloco_na_pagina(fake):
    fake.route(SPLENDOR, "allmat_product-page_39233_box.html")
    (o,) = run_search(fake, [m2_row(cents="999")]).offers
    assert o.content is None
    assert o.note == NOT_FOUND


def test_pagina_sem_area_declarada(fake):
    fake.route(SPLENDOR, PAGE.replace("Produto por caixa: 1.37 m", "Ver ficha técnica").encode("utf-8"))
    (o,) = run_search(fake, [m2_row()]).offers
    assert o.content == Decimal("13.74") / Decimal("9.99")
    assert o.content_unit == "m²"
    assert o.note == "área derivada do preço por m²"


def test_area_incoerente_com_o_preco_por_m2(fake):
    fake.route(SPLENDOR, PAGE.replace(">9,99<", ">5,00<").encode("utf-8"))
    (o,) = run_search(fake, [m2_row()]).offers
    assert allmat.INCOHERENT in o.note
    assert o.content == Decimal("13.74") / Decimal("5.00")


def test_pagina_do_produto_falha(fake):
    fake.route(SPLENDOR, StoreError("HTTP 500"))
    fake.route(SEARCH + "pavimento", [m2_row()])
    sr = asyncio.run(search_store(allmat, Item(row=2, product="pavimento", qty=Decimal(30), unit="m²"), fake))
    assert sr.status == "ok"
    (o,) = sr.offers
    assert o.content is None
    assert o.note.startswith("página do produto falhou: HTTP 500")


def test_limite_de_10_paginas_pelas_mais_baratas(fake):
    # 12 caixas por ordem de preço decrescente: 12,00 € ... 1,00 €
    rows = [m2_row(pid=i, cents=str(i * 100), name=f"PAVIMENTO {i}", slug=f"p{i}") for i in range(12, 0, -1)]
    fake.route("allmat.pt/produto/", PAGE.encode("utf-8"))
    found = run_search(fake, rows)
    pages = [c for c in fake.calls if "/produto/" in c]
    assert len(pages) == 10
    assert sorted(pages) == sorted(f"https://allmat.pt/produto/p{i}/" for i in range(1, 11))
    unread = [o for o in found.offers if o.note == LIMIT]
    assert sorted(o.price for o in unread) == [Decimal("11"), Decimal("12")]


def test_amostras_cimento_e_osb(fake):
    fake.route(SEARCH + "cimento", "allmat_products_search-cimento.json")
    fake.route(SEARCH + "osb", "allmat_products_search-osb_no-results.json")
    found = asyncio.run(allmat.search("cimento", fake))
    assert [o.price for o in found.offers] == [Decimal("4.22"), Decimal("4.72"), Decimal("6.60")]
    assert found.offers[0].stock == "186 em stock"
    assert {o.vat_origin for o in found.offers} == {"regra da loja"}
    assert asyncio.run(allmat.search("osb", fake)).raw == 0
