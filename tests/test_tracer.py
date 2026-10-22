"""Ponta a ponta sem rede do esqueleto: folha .xlsx -> Allmat (fixtures) -> terminal."""

import asyncio
import io
from decimal import Decimal

import pytest
from curl_cffi.requests import AsyncSession
from openpyxl import Workbook

import strata.search
from strata.__main__ import main
from strata.fetch import Fetcher
from strata.models import Item, ItemResult, Offer, StoreResult
from strata.report import print_item
from strata.stores import allmat

HEADERS = ["Produto", "Família", "Tamanho", "Unidade", "Qty", "Referência", "Notas"]
SEARCH = "allmat.pt/wp-json/wc/store/v1/products?search="


def test_folha_allmat_terminal(tmp_path, fake, monkeypatch, capsys):
    path = tmp_path / "lista.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(HEADERS)
    ws.append(["cimento", None, None, "saco", 10])
    ws.append(["osb", None, None, "un", 30])
    ws.append(["tijolo", None, None, "caixa", 5])
    wb.save(path)
    fake.route(SEARCH + "cimento", "allmat_products_search-cimento.json")
    fake.route(SEARCH + "osb", "allmat_products_search-osb_no-results.json")
    monkeypatch.setattr(strata.search, "STORES", (allmat,))

    assert main(["pesquisar", str(path)], fetch=fake) == 0

    out = capsys.readouterr().out
    for text in (
        "linha 4: unidade desconhecida: caixa",
        "Linha 2 — cimento (10 saco)",
        "Allmat: ok",
        "4,22 €",
        "IVA: regra da loja",
        "186 em stock",
        "Linha 3 — osb (30 un)",
        "Allmat: sem resultados",
    ):
        assert text in out, text
    assert out.index("Linha 2") < out.index("Linha 3")


def test_corte_a_5_ofertas():
    offer = Offer(
        store="Allmat", title="t", url="https://allmat.pt/x", price=Decimal("1"),
        vat_origin="regra da loja", vat_evidence="e",
    )
    item = Item(row=2, product="cimento", qty=Decimal(10), unit="saco")
    out = io.StringIO()
    print_item(ItemResult(item, [StoreResult("Allmat", "ok", [offer] * 7)]), out)
    text = out.getvalue()
    assert text.count("https://allmat.pt/x") == 5
    assert "+2 ofertas não mostradas" in text


def test_rede_bloqueada():
    async def go():
        async with AsyncSession() as s:
            await Fetcher(s).get_json("https://allmat.pt/wp-json/wc/store/v1/products", {"search": "osb"})

    with pytest.raises(RuntimeError, match="rede bloqueada nos testes"):
        asyncio.run(go())
