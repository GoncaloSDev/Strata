"""Obras 360 (Beevo): uma oferta por variante, IVA da loja confirmado, escalões e stock (amostras reais em tests/fixtures/)."""

import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest

from strata.fetch import StoreError
from strata.money import fmt_eur, fmt_unit_price, per_unit
from strata.stores import obras360

FIXTURES = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"), parse_float=Decimal)


LIST_OSB = load("obras360_product-list_osb.json")
LIST_NONE = load("obras360_product-list_no-results.json")
DETAIL = load("obras360_product-details_osb-parent.json")
PLACA = LIST_OSB["meta_data"]["protected"]["products"][0]
COLA = LIST_OSB["meta_data"]["protected"]["products"][1]
WIDGET = "f1f5fb06-09e7-4519-8f44-9b3cd0093460"


def variants(d):
    return d["meta_data"]["protected"]["attribute_values_prices"]


def by_mm(offers, mm):
    return next(o for o in offers if f"1 Placa {mm} MM" in o.title)


def test_offers_from_details_uma_oferta_por_variante():
    offers = obras360.offers_from_details(DETAIL, PLACA)
    assert len(offers) == 7
    assert {o.store for o in offers} == {"Obras 360"}


def test_variante_9mm_preco_com_iva_da_loja_unidade_e_stock():
    o = by_mm(obras360.offers_from_details(DETAIL, PLACA), 9)
    assert o.price == Decimal("15.02406624")
    assert fmt_eur(o.price) == "15,02 €"
    assert o.content == Decimal("3.125") and o.content_unit == "m²"
    assert fmt_unit_price(per_unit(o), "m²") == "4,81 €/m²"
    assert o.stock == "1843 em stock"
    assert o.tiers == [(Decimal(108), Decimal("2.5"))]
    assert o.vat_origin == "indicado pela loja"
    assert o.vat_evidence == "tax_percentage=23"
    assert o.note == ""
    assert o.title.startswith("Placa OSB 9-30MM") and " — 1 Placa 9 MM" in o.title
    assert o.url == "https://www.obras360.pt/" + variants(DETAIL)["20008"]["segment"]


def test_escaloes_por_variante():
    offers = obras360.offers_from_details(DETAIL, PLACA)
    assert by_mm(offers, 12).tiers == [(Decimal(90), Decimal("2.5"))]
    assert by_mm(offers, 25).tiers == []


def test_iva_incoerente_e_erro():
    d = copy.deepcopy(DETAIL)
    v = variants(d)["19875"]
    v["prices_with_convertion_factor"]["final_price_with_tax_unformatted"] += Decimal("0.05")
    with pytest.raises(StoreError, match="IVA incoerente"):
        obras360.offers_from_details(d, PLACA)


def test_iva_diferente_de_23_nao_e_convertido():
    d = copy.deepcopy(DETAIL)
    v = variants(d)["20008"]
    v["prices"]["tax_percentage"] = 6
    item = v["prices_with_convertion_factor"]
    item["final_price_with_tax_unformatted"] = item["final_price_unformatted"] * Decimal("1.06")
    o = by_mm(obras360.offers_from_details(d, PLACA), 9)
    assert o.note == "IVA da loja 6%: não convertido para 23%"
    assert o.vat_evidence == "tax_percentage=6"
    assert o.price == item["final_price_unformatted"] * Decimal("1.06")


def test_variante_esgotada_mostra_a_previsao_sem_html():
    d = copy.deepcopy(DETAIL)
    variants(d)["20008"]["stock"] = 0
    o = by_mm(obras360.offers_from_details(d, PLACA), 9)
    assert o.stock == "esgotado (Previsão em Armazém Lisboa: 6 dias úteis)"


@pytest.mark.parametrize("bad", [
    {"success": False, "meta_data": {"protected": {"attribute_values_prices": []}}},
    {"success": True, "meta_data": {"protected": {"attribute_values_prices": []}}},
])
def test_detalhe_sem_variantes_e_erro(bad):
    with pytest.raises(StoreError, match="sem variantes"):
        obras360.offers_from_details(bad, PLACA)


def test_unidade_da_loja_sem_conversao_fica_desconhecida():
    parent = copy.deepcopy(PLACA)
    parent["product"]["visible_sell_unit"]["description"] = "ML"
    o = by_mm(obras360.offers_from_details(DETAIL, parent), 9)
    assert o.content is None
    assert "unidade da loja 'ML' sem conversão" in o.note


def test_desconto_por_quantidade_noutro_formato_vai_para_a_nota():
    d = copy.deepcopy(DETAIL)
    variants(d)["20008"]["prices"]["discounts"][0]["calc_value_mathop"] = "-"
    o = by_mm(obras360.offers_from_details(d, PLACA), 9)
    assert o.tiers == []
    assert "desconto por quantidade noutro formato (não lido)" in o.note


def test_widget_id():
    html = f'<script>var x = {{"widget_slug":"product-list","widget_instance_id":"{WIDGET}","a":1}};</script>'
    assert obras360.widget_id(html) == WIDGET


def test_widget_id_sem_bloco_e_erro():
    with pytest.raises(StoreError, match="widget"):
        obras360.widget_id("<html><body>nada</body></html>")


def test_parse_list():
    products, total = obras360.parse_list(LIST_OSB)
    assert len(products) == 2 and total == 13
    assert obras360.parse_list(LIST_NONE) == ([], 0)


def test_parse_list_success_false_e_erro():
    with pytest.raises(StoreError):
        obras360.parse_list({"success": False})
