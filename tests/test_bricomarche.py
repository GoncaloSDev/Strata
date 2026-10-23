"""Bricomarché: pais -> top 10 -> variações por loja física (amostras reais em tests/fixtures/)."""

import copy
import json
from decimal import Decimal
from pathlib import Path

from strata.stores import bricomarche as bm

FIXTURES = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"), parse_float=Decimal)


PARENTS = load("bricomarche_products_search-osb.json")
ROWS = load("bricomarche_variations_parent-47412.json")


def parent(pid):
    return next(p for p in PARENTS if p["id"] == pid)


def row(cents, loja="coina-barreiro", nome="Coina - Barreiro", text="12 em stock", cls="in-stock", parent=47412):
    return {
        "id": 1,
        "parent": parent,
        "variation": f"Loja: {nome}",
        "permalink": f"https://www.bricomarche.pt/produto/plc-osb-lisa-2-50x1-25-12mm/?attribute_pa_loja={loja}",
        "prices": {"price": str(cents), "currency_minor_unit": 2},
        "stock_availability": {"text": text, "class": cls},
    }


def test_parent_key():
    assert bm.parent_key(parent(47412)) == Decimal("18.49")
    assert bm.parent_key(parent(37387)) == Decimal("19.99")  # price "0": vale o price_range
    sem = copy.deepcopy(parent(37387))
    sem["prices"]["price_range"] = None
    assert bm.parent_key(sem) is None


def test_cheapest_e_a_loja_fisica_mais_barata():
    best = bm.cheapest(ROWS)
    assert best["prices"]["price"] == "1849"
    assert best["variation"] == "Loja: Coina - Barreiro"


def test_cheapest_ignora_master_e_precos_a_zero():
    rows = ROWS + [row(1000, loja="master", nome="master"), row(0, loja="loja-zero"), row(-5, loja="loja-neg")]
    assert bm.cheapest(rows)["variation"] == "Loja: Coina - Barreiro"
    assert bm.cheapest([row(0), row(1000, loja="master", nome="master")]) is None


def test_has_stock():
    assert bm.has_stock(row(1, text="0 em stock", cls="in-stock")) is False
    assert bm.has_stock(row(1, text="Esgotado", cls="out-of-stock")) is False
    assert bm.has_stock(row(1, text="118 em stock", cls="in-stock")) is True


def test_store_link():
    coina = next(r for r in ROWS if r["variation"] == "Loja: Coina - Barreiro")
    assert bm.store_link(coina) == (
        "https://www.bricomarche.pt/coina-barreiro/produto/plc-osb-lisa-2-50x1-25-12mm/",
        "Coina - Barreiro",
    )


def test_offer_from_amostra_47412():
    o = bm.offer_from(parent(47412), ROWS)
    assert o.store == "Bricomarché"
    assert o.title == "PLACA OSB 12 MM"
    assert o.price == Decimal("18.49")  # da variação de Coina, nunca o do pai
    assert o.location == "Coina - Barreiro"
    assert o.stock == "0 em stock"
    assert o.url == "https://www.bricomarche.pt/coina-barreiro/produto/plc-osb-lisa-2-50x1-25-12mm/"
    assert o.vat_origin == "regra da loja"
    assert "B2C" in o.vat_evidence
    assert (o.content, o.content_unit) == (Decimal(1), "un")
    assert o.note == "com stock: 19,99 € em Monção"  # master (19,99 €, 989 em stock) fica de fora


def test_offer_from_sem_dica_quando_a_mais_barata_tem_stock():
    o = bm.offer_from(parent(47412), [row(1500, text="3 em stock"), row(1400, loja="x", nome="X", text="Esgotado",
                                                                         cls="out-of-stock")])
    assert o.price == Decimal("14.00") and o.location == "X"
    assert o.note == "com stock: 15,00 € em Coina - Barreiro"
    o = bm.offer_from(parent(47412), [row(1500, text="3 em stock")])
    assert o.note == ""


def test_preco_do_pai_nunca_e_mostrado():
    # pai a 18,49 €, única variação válida a 25,00 €: mostra-se 25,00 €
    o = bm.offer_from(parent(47412), [row(2500), row(0, loja="y"), row(100, loja="master", nome="master")])
    assert o.price == Decimal("25.00")


def test_pai_sem_variacoes_com_preco_nao_da_oferta():
    assert bm.offer_from(parent(37387), []) is None
    assert bm.offer_from(parent(37387), [row(0), row(999, loja="master", nome="master")]) is None
