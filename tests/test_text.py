"""Texto colado no terminal (LIST-01, D-10..D-12)."""

import io
from decimal import Decimal

import pytest

import strata.search
from strata.__main__ import main
from strata.stores import allmat
from strata.text import parse_line, read_pasted

SEARCH = "allmat.pt/wp-json/wc/store/v1/products?search="
BOTH = ["unidade assumida: un", "quantidade assumida: 1"]


@pytest.mark.parametrize("line, product, qty, unit, warnings", [
    ("OSB 12mm 30 un", "OSB 12mm", Decimal(30), "un", []),
    ("cimento 10 saco", "cimento", Decimal(10), "saco", []),
    ("OSB 12mm", "OSB 12mm", Decimal(1), "un", BOTH),
    ("OSB 12 mm", "OSB 12 mm", Decimal(1), "un", BOTH),
    ("tijolo 30un", "tijolo", Decimal(30), "un", []),
    ("areia 3 sacos", "areia", Decimal(3), "saco", []),
    ("azulejo 2,5 m²", "azulejo", Decimal("2.5"), "m²", []),
    ("placa 2.5 m2", "placa", Decimal("2.5"), "m²", []),
    ("cimento 10", "cimento", Decimal(10), "un", ["unidade assumida: un"]),
    ("cimento 25 kg 10 saco", "cimento 25 kg", Decimal(10), "saco", []),
])
def test_parse_line(line, product, qty, unit, warnings):
    item, err = parse_line(line, 7)
    assert err is None
    assert (item.row, item.product, item.qty, item.unit, item.warnings) == (7, product, qty, unit, warnings)


@pytest.mark.parametrize("line, reason", [
    ("30 un", "linha sem descrição"),
    ("cimento 0 saco", "quantidade não é um número positivo: 0"),
])
def test_parse_line_erros(line, reason):
    assert parse_line(line, 1) == (None, reason)


def test_read_pasted_para_na_linha_vazia():
    items, invalid = read_pasted(io.StringIO("osb 30 un\ncimento 10 saco\n\nignorada 1 un\n"))
    assert [(i.row, i.product) for i in items] == [(1, "osb"), (2, "cimento")]
    assert invalid == []


def test_read_pasted_linha_invalida_com_numero():
    items, invalid = read_pasted(io.StringIO("osb 30 un\n30 un\n"))
    assert [i.product for i in items] == ["osb"]
    assert [(i.row, i.reason) for i in invalid] == [(2, "linha sem descrição")]


def test_pesquisar_sem_ficheiro_le_o_terminal(fake, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("cimento 10 saco\nosb 30 un\n\n"))
    monkeypatch.setattr(strata.search, "STORES", (allmat,))
    fake.route(SEARCH + "cimento", "allmat_products_search-cimento.json")
    fake.route(SEARCH + "osb", "allmat_products_search-osb_no-results.json")

    assert main(["pesquisar"], fetch=fake) == 0

    out = capsys.readouterr().out
    for text in ("Linha 1 — cimento (10 saco)", "Allmat: ok", "Linha 2 — osb (30 un)", "Allmat: sem resultados"):
        assert text in out, text


def test_pesquisar_sem_linhas(fake, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("\n"))
    assert main(["pesquisar"], fetch=fake) == 2
    assert "Nenhuma linha colada." in capsys.readouterr().err
    assert fake.calls == []
