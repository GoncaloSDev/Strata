"""Bricomarché: pais -> top 10 -> variações por loja física (amostras reais em tests/fixtures/)."""

import asyncio
import copy
import json
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook

import strata.search
from strata.__main__ import main
from strata.stores import allmat
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
    assert o.price == Decimal("19.99")  # a loja física mais barata com stock, nunca o preço do pai
    assert o.location == "Monção"
    assert o.stock == "118 em stock"
    assert o.url == "https://www.bricomarche.pt/moncao/produto/plc-osb-lisa-2-50x1-25-12mm/"
    assert o.vat_origin == "regra da loja"
    assert "B2C" in o.vat_evidence
    assert (o.content, o.content_unit) == (Decimal(1), "un")
    assert o.note == "mais barata sem stock: 18,49 € em Coina - Barreiro"  # master (19,99 €) fica de fora


def test_offer_from_sem_dica_quando_a_mais_barata_tem_stock():
    o = bm.offer_from(parent(47412), [row(1500, text="3 em stock"), row(1600, loja="x", nome="X", text="Esgotado",
                                                                         cls="out-of-stock")])
    assert o.price == Decimal("15.00") and o.location == "Coina - Barreiro"
    assert o.note == ""
    o = bm.offer_from(parent(47412), [row(1500, text="3 em stock")])
    assert o.note == ""


def test_offer_from_prefere_a_loja_com_stock():
    o = bm.offer_from(parent(47412), [row(1500, text="3 em stock"), row(1400, loja="x", nome="X", text="Esgotado",
                                                                         cls="out-of-stock")])
    assert (o.price, o.location, o.stock) == (Decimal("15.00"), "Coina - Barreiro", "3 em stock")
    assert o.url == "https://www.bricomarche.pt/coina-barreiro/produto/plc-osb-lisa-2-50x1-25-12mm/"
    assert o.note == "mais barata sem stock: 14,00 € em X"


def test_offer_from_nenhuma_loja_com_stock():
    o = bm.offer_from(parent(47412), [row(1500, text="0 em stock"), row(1400, loja="x", nome="X", text="Esgotado",
                                                                         cls="out-of-stock")])
    assert (o.price, o.location, o.stock) == (Decimal("14.00"), "X", "Esgotado")
    assert o.note == ""  # a oferta já é a mais barata


def test_offer_from_empate_prefere_a_loja_com_stock():
    # a sem stock primeiro: ganhava o empate quando a escolha ignorava o stock
    o = bm.offer_from(parent(47412), [row(1400, loja="x", nome="X", text="Esgotado", cls="out-of-stock"),
                                      row(1400, text="3 em stock")])
    assert (o.price, o.location, o.stock) == (Decimal("14.00"), "Coina - Barreiro", "3 em stock")
    assert o.note == ""  # a sem stock não é mais barata


def test_preco_do_pai_nunca_e_mostrado():
    # pai a 18,49 €, única variação válida a 25,00 €: mostra-se 25,00 €
    o = bm.offer_from(parent(47412), [row(2500), row(0, loja="y"), row(100, loja="master", nome="master")])
    assert o.price == Decimal("25.00")


def test_pai_sem_variacoes_com_preco_nao_da_oferta():
    assert bm.offer_from(parent(37387), []) is None
    assert bm.offer_from(parent(37387), [row(0), row(999, loja="master", nome="master")]) is None


# --- Tarefa 2: pesquisa (pais -> top 10 -> variações) ---

PARENTS_URL = "bricomarche.pt/wp-json/wc/store/v1/products?search="


def route_osb(fake, query="osb"):
    fake.route(PARENTS_URL + query, "bricomarche_products_search-osb.json")
    fake.route("parent=47412&", "bricomarche_variations_parent-47412.json")
    fake.route("parent=47411&", [row(1449, text="12 em stock", parent=47411)])
    fake.route("parent=37387&", [])
    fake.route("parent=37386&", [])


def test_search_osb(fake):
    route_osb(fake)
    found = asyncio.run(bm.search("osb", fake))
    assert found.raw == 4 and found.hidden == 0
    assert sorted((o.price, o.location) for o in found.offers) == [
        (Decimal("14.49"), "Coina - Barreiro"), (Decimal("19.99"), "Monção")]
    assert "2 produtos sem preço" in found.notes


def test_variacoes_pedidas_por_pai(fake):
    route_osb(fake)
    asyncio.run(bm.search("osb", fake))
    var_calls = [c for c in fake.calls if "type=variation" in c]
    assert len(var_calls) == 4
    for pid in (47412, 47411, 37387, 37386):
        assert any(f"parent={pid}&" in c for c in var_calls), pid
    assert not any("search=" in c for c in var_calls)  # nunca search + type=variation (~10 s por página)


def test_so_os_10_pais_mais_baratos_sao_expandidos(fake):
    parents = [
        {"id": 100 + i, "name": f"Placa OSB modelo {i}",
         "prices": {"price": str(1000 + i * 100), "price_range": None, "currency_minor_unit": 2}}
        for i in range(12)
    ]
    fake.route(PARENTS_URL + "osb", parents)
    fake.route("type=variation", [row(5000)])
    found = asyncio.run(bm.search("osb", fake))
    var_calls = [c for c in fake.calls if "type=variation" in c]
    assert len(var_calls) == 10
    assert not any("parent=110&" in c or "parent=111&" in c for c in var_calls)  # os 2 mais caros
    assert len(found.offers) == 10
    assert "+2 produtos não expandidos (limite de 10 por pesquisa)" in found.notes


def test_pais_sem_as_palavras_ficam_escondidos(fake):
    fake.route(PARENTS_URL + "cimento", [
        {"id": 1, "name": "Cimento cola", "prices": {"price": "500", "price_range": None, "currency_minor_unit": 2}},
        {"id": 2, "name": "Painel aquecimento", "prices": {"price": "100", "price_range": None,
                                                           "currency_minor_unit": 2}},
    ])
    fake.route("parent=1&", [row(500, parent=1)])
    found = asyncio.run(bm.search("cimento", fake))
    assert found.raw == 2 and found.hidden == 1 and len(found.offers) == 1
    assert not any("parent=2&" in c for c in fake.calls)


def test_medidas_coladas_por_x_batem_no_filtro(fake):
    # CR-03: "osb 18mm" tem de bater em "Chapa Osb 2440X590X18Mm" (pai 37387)
    route_osb(fake, "osb+18mm")
    found = asyncio.run(bm.search("osb 18mm", fake))
    assert found.raw == 4 and found.hidden == 3
    var_calls = [c for c in fake.calls if "type=variation" in c]
    assert len(var_calls) == 1 and "parent=37387&" in var_calls[0]
    assert "1 produtos sem preço" in found.notes


def test_ponta_a_ponta_allmat_e_bricomarche(tmp_path, fake, monkeypatch, capsys):
    path = tmp_path / "lista.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["Produto", "Família", "Tamanho", "Unidade", "Qty", "Referência", "Notas"])
    ws.append(["OSB 12mm", None, None, "un", 3])
    wb.save(path)
    fake.route("allmat.pt/wp-json/wc/store/v1/products?search=OSB", "allmat_products_search-osb_no-results.json")
    fake.route(PARENTS_URL + "OSB+12mm", [])  # mais específica primeiro
    route_osb(fake, "OSB&")
    monkeypatch.setattr(strata.search, "STORES", (allmat, bm))

    assert main(["pesquisar", str(path)], fetch=fake) == 0

    out = capsys.readouterr().out
    assert "Allmat: sem resultados" in out
    assert "Bricomarché: ok (pesquisa alargada: 'OSB')" in out
    assert out.index("Allmat: sem resultados") < out.index("Bricomarché: ok")
    # D-15 emendada (G-01-5): só a placa de 12 mm; a de 9 mm (14,49 € em Coina) fica contada
    assert "19,99 €  PLACA OSB 12 MM" in out
    assert "loja: Monção" in out
    assert "https://www.bricomarche.pt/moncao/produto/" in out
    assert "+1 ofertas escondidas: título sem 'OSB 12mm'" in out
    assert "14,49 €" not in out


def test_stores_tem_bricomarche_a_seguir_a_allmat():
    assert strata.search.STORES[:2] == (allmat, bm)
