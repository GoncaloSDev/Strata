"""Conteúdo da embalagem pelo título, preço na unidade pedida e formatação (PRICE-02, D-03)."""

import inspect
from decimal import Decimal

import pytest

import strata.money
from strata.models import Offer
from strata.money import content_from_title, fmt_eur, fmt_unit_price, in_unit


def offer(price="4.22", content=None, content_unit=None) -> Offer:
    return Offer(store="X", title="t", url="https://x.pt/p", price=Decimal(price),
                 vat_origin="regra da loja", vat_evidence="e",
                 content=None if content is None else Decimal(content), content_unit=content_unit)


@pytest.mark.parametrize("title, expected", [
    ("LIZ CIMENTO COLA CINZA SACO 25 KG REF 01.001", (Decimal("25"), "kg")),
    ("SACO 25KG", (Decimal("25"), "kg")),
    ("TINTA 5L", (Decimal("5"), "L")),
    ("SikaBond-52 Parquet 600ML", (Decimal("0.6"), "L")),
    ("Cola 500 g", (Decimal("0.5"), "kg")),
    ("Azulejo 1,44 m2 caixa", (Decimal("1.44"), "m²")),
    ("PLACA OSB 12 MM", None),
    ("FISCHER CIMENTO BARBACOAS", None),
])
def test_content_from_title(title, expected):
    assert content_from_title(title) == expected


@pytest.mark.parametrize("unit, expected", [
    ("saco", (Decimal("4.22"), "")),
    ("kg", (Decimal("0.1688"), "")),
    ("m²", (None, "não convertível para m²: vendido em kg")),
])
def test_in_unit_com_conteudo(unit, expected):
    assert in_unit(offer(content="25", content_unit="kg"), unit) == expected


def test_in_unit_sem_conteudo():
    assert in_unit(offer(), "m²") == (None, "não convertível para m²: conteúdo da embalagem desconhecido")


def test_formatacao():
    assert fmt_eur(Decimal("4.225")) == "4,23 €"
    assert fmt_unit_price(Decimal("0.16880"), "kg") == "0,1688 €/kg"
    assert fmt_unit_price(Decimal("10.0292"), "m²") == "10,03 €/m²"


def test_money_nunca_usa_float():
    assert "float(" not in inspect.getsource(strata.money)
    key, _ = in_unit(offer(content="25", content_unit="kg"), "kg")
    assert isinstance(key, Decimal)
    c = content_from_title("SACO 25KG")
    assert c is not None and isinstance(c[0], Decimal)
