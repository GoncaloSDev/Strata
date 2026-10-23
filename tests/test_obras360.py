"""Obras 360 (Beevo): uma oferta por variante, IVA da loja confirmado, escalões e stock (amostras reais em tests/fixtures/)."""

import asyncio
import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import Workbook

import strata.search
from strata.__main__ import main
from strata.fetch import StoreBlocked, StoreError
from strata.money import fmt_eur, fmt_unit_price, per_unit
from strata.stores import allmat, obras360
from strata.stores import bricomarche as bm

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


# --- Tarefa 2: pesquisa (widget, lista, top 20, detalhes) e registo em STORES ---

LIST_URL = f"product-list/{WIDGET}?search="
DETAIL_URL = "product-details/27?_beevo_decoded_params[0][product_id]="
PLACA_ID = "f807c893-c3eb-4630-a409-8a0a7bbc88c1"
COLA_ID = COLA["product"]["product"]["product_id"]
NO_DETAIL = {"success": False, "meta_data": {"protected": {"attribute_values_prices": []}}}


def listing(products, total):
    d = copy.deepcopy(LIST_NONE)
    d["meta_data"]["protected"]["products"] = products
    d["meta_data"]["protected"]["total_products"] = total
    return d


def parent(pid, name, price):
    p = copy.deepcopy(PLACA)
    p["product"]["product"]["product_id"] = pid
    p["product"]["name"] = name
    p["product"]["prices_with_conversion_factor"]["final_price_unformatted"] = Decimal(price)
    return p


def run(query, fetch):
    return asyncio.run(obras360.search(query, fetch))


def test_search_placa_osb_le_o_widget_uma_vez(fake):
    fake.route("/pesquisa?search=placa+osb", "obras360_pesquisa-widget.html")
    fake.route(LIST_URL + "placa+osb&items_per_page=48&page=1", "obras360_product-list_osb.json")
    fake.route(DETAIL_URL + PLACA_ID, "obras360_product-details_osb-parent.json")

    found = run("placa osb", fake)

    assert len(found.offers) == 7
    assert found.raw == 13 and found.hidden == 1  # a cola não tem "placa" no título
    assert fake.cache["obras360_widget"] == WIDGET
    assert sum("/pesquisa?" in c for c in fake.calls) == 1
    assert sum("product-details" in c for c in fake.calls) == 1  # a cola filtrada não é expandida


def test_widget_em_cache_nao_pede_a_pagina(fake):
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "placa+osb", "obras360_product-list_osb.json")
    fake.route(DETAIL_URL + PLACA_ID, "obras360_product-details_osb-parent.json")

    run("placa osb", fake)

    assert not any("/pesquisa?" in c for c in fake.calls)


def test_produto_sem_detalhe_vai_para_a_nota(fake):
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "osb", "obras360_product-list_osb.json")
    fake.route(DETAIL_URL + PLACA_ID, "obras360_product-details_osb-parent.json")
    fake.route(DETAIL_URL + COLA_ID, NO_DETAIL)

    found = run("osb", fake)

    assert len(found.offers) == 7
    assert found.hidden == 0
    assert any(n.startswith("1 produtos sem detalhe: ") and "sem variantes" in n for n in found.notes)


def test_todos_os_detalhes_falham_e_erro(fake):
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "osb", listing([COLA], 1))
    fake.route(DETAIL_URL + COLA_ID, NO_DETAIL)

    with pytest.raises(StoreError, match="sem variantes"):
        run("osb", fake)


def test_bloqueio_num_detalhe_sobe(fake):
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "osb", "obras360_product-list_osb.json")
    fake.route(DETAIL_URL + PLACA_ID, "obras360_product-details_osb-parent.json")
    fake.route(DETAIL_URL + COLA_ID, StoreBlocked("HTTP 403"))

    with pytest.raises(StoreBlocked):
        run("osb", fake)


def test_paginas_por_total_e_so_20_detalhes_dos_mais_baratos(fake):
    products = []
    for i in range(25):
        p = copy.deepcopy(PLACA)
        p["product"]["product"]["product_id"] = f"id-{i:02d}"
        p["product"]["prices_with_conversion_factor"]["final_price_unformatted"] = Decimal(100 - i)
        products.append(p)
    fake.cache["obras360_widget"] = WIDGET
    fake.route("page=1", listing(products[:10], 120))
    fake.route("page=2", listing(products[10:20], 120))
    fake.route("page=3", listing(products[20:], 120))
    fake.route("product-details/27", "obras360_product-details_osb-parent.json")

    found = run("placa osb", fake)

    pages = [c for c in fake.calls if "product-list" in c]
    assert [c[-6:] for c in pages] == ["page=1", "page=2", "page=3"]
    details = [c.rsplit("=", 1)[1] for c in fake.calls if "product-details" in c]
    assert sorted(details) == [f"id-{i:02d}" for i in range(5, 25)]  # os 20 mais baratos
    assert "+5 produtos não expandidos (limite de 20 por pesquisa)" in found.notes
    assert found.raw == 120


def test_sem_resultados(fake):
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "xyz", "obras360_product-list_no-results.json")

    found = run("xyz", fake)

    assert found.raw == 0 and found.offers == []
    assert not any("product-details" in c for c in fake.calls)


def test_stores_tem_obras360_a_seguir_a_bricomarche():
    assert strata.search.STORES == (allmat, bm, obras360)


def test_ponta_a_ponta_tres_lojas(tmp_path, fake, monkeypatch, capsys):
    path = tmp_path / "lista.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["Produto", "Família", "Tamanho", "Unidade", "Qty", "Referência", "Notas"])
    ws.append(["placa osb", None, None, "un", 3])
    wb.save(path)
    fake.route("allmat.pt/wp-json/wc/store/v1/products?search=placa", "allmat_products_search-osb_no-results.json")
    fake.route("bricomarche.pt/wp-json/wc/store/v1/products?search=placa", [])
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "placa+osb", "obras360_product-list_osb.json")
    fake.route(DETAIL_URL + PLACA_ID, "obras360_product-details_osb-parent.json")
    monkeypatch.setattr(strata.search, "STORES", (allmat, bm, obras360))

    assert main(["pesquisar", str(path)], fetch=fake) == 0

    out = capsys.readouterr().out
    assert out.index("Allmat:") < out.index("Bricomarché:") < out.index("Obras 360: ok")
    section = out[out.index("Obras 360: ok"):]
    first = section.splitlines()[1]
    assert first.strip().startswith("15,02 €") and "1 Placa 9 MM" in first
    assert section.count("IVA: indicado pela loja (tax_percentage=23)") == 5
    assert "+2 ofertas não mostradas" in section
    assert "+1 ofertas escondidas" in section
    assert "escalões: −2,5% a partir de 108" in section


# --- 01-07: "tinta branca" sobre respostas reais gravadas com --record (CR-01) ---

TINTAS = {"Dyrustar": "obras360_product-details_tinta-dyrustar.json",
          "Dyrup Super": "obras360_product-details_tinta-dyrup-super.json",
          "Dycrilforce": "obras360_product-details_tinta-dycrilforce.json",
          "Colorite": "obras360_product-details_tinta-colorite.json"}


def test_tinta_branca_gravada_mostra_as_tintas_brancas(fake):
    import io

    from strata.models import Item, ItemResult
    from strata.report import print_item

    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "tinta+branca", "obras360_product-list_tinta-branca.json")
    for p in load("obras360_product-list_tinta-branca.json")["meta_data"]["protected"]["products"]:
        key = next((k for k in TINTAS if k in p["product"]["name"]), None)
        if key:  # os outros pais ficam sem rota: se o filtro os deixar passar, `fake` falha
            fake.route(DETAIL_URL + p["product"]["product"]["product_id"], TINTAS[key])
    it = Item(row=4, product="tinta branca", qty=Decimal(15), unit="L")

    sr = asyncio.run(strata.search.search_store(obras360, it, fake))

    assert sr.status == "ok" and sr.detail == ""
    assert sr.hidden == 4  # Primário Dyprolite, SecilTek Isovit e as duas fitas de pintura
    assert {k for k in TINTAS if any(k in o.title for o in sr.offers)} == set(TINTAS)
    assert all(o.vat_origin == "indicado pela loja" for o in sr.offers)
    out = io.StringIO()
    print_item(ItemResult(it, [sr]), out)
    text = out.getvalue()
    assert "  Obras 360: ok\n" in text
    section = text[text.index("  Obras 360: ok"):]
    assert any("Branco" in ln for ln in section.splitlines()[1:])
    assert "+4 ofertas escondidas: título sem 'tinta branca'" in text


# --- 01-08: a medida está na variante, não no nome do pai (CR-02) ---

def test_osb_12mm_so_a_variante_de_12mm(fake):
    import io

    from strata.models import Item, ItemResult
    from strata.report import print_item

    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "OSB+12+mm", "obras360_product-list_osb.json")
    fake.route(DETAIL_URL + PLACA_ID, "obras360_product-details_osb-parent.json")
    fake.route(DETAIL_URL + COLA_ID, NO_DETAIL)  # a cola SikaBond também tem "OSB" no nome
    it = Item(row=3, product="OSB 12 mm", qty=Decimal(30), unit="un")

    sr = asyncio.run(strata.search.search_store(obras360, it, fake))

    assert sr.status == "ok"
    assert len(sr.offers) == 1
    o = sr.offers[0]
    assert " — 1 Placa 12 MM" in o.title
    assert fmt_eur(o.price) == "19,37 €"
    assert sr.hidden == 6  # as outras 6 espessuras da placa
    assert sr.broadened_query is None and not o.broadened
    out = io.StringIO()
    print_item(ItemResult(it, [sr]), out)
    text = out.getvalue()
    assert "19,37 €" in text
    assert "+6 ofertas escondidas: título sem 'OSB 12 mm'" in text
    assert "nota: 1 produtos sem detalhe" in text
    assert "1 Placa 9 MM" not in text


# --- 01-09: plurais -is/-il no filtro de título (CR-05) ---

def test_perfis_mostra_o_pai_perfil(fake):
    import io

    from strata.models import Item, ItemResult
    from strata.report import print_item

    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "perfis", listing([parent("id-perfil", "Perfil Montante 48mm Gesso Cartonado", 3),
                                             parent("id-calha", "Calha Gesso Cartonado", 2)], 2))
    fake.route(DETAIL_URL + "id-perfil", "obras360_product-details_osb-parent.json")  # a calha fica sem rota
    it = Item(row=5, product="perfis", qty=Decimal(10), unit="un")

    sr = asyncio.run(strata.search.search_store(obras360, it, fake))

    assert sr.status == "ok" and sr.detail == ""
    assert sr.offers and all(o.title.startswith("Perfil Montante 48mm") for o in sr.offers)
    assert sr.hidden == 1  # a calha
    assert not any("id-calha" in c for c in fake.calls)
    out = io.StringIO()
    print_item(ItemResult(it, [sr]), out)
    text = out.getvalue()
    assert "  Obras 360: ok\n" in text
    assert "Perfil Montante 48mm" in text
    assert "+1 ofertas escondidas: título sem 'perfis'" in text


# --- 01-09: o pai que bate na pesquisa completa passa à frente do corte K=20 (CR-04) ---

def test_pai_com_a_pesquisa_completa_passa_a_frente_do_corte(fake):
    baratos = [parent(f"id-{i:02d}", "Parafuso Zincado Cabeça Chata", i + 1) for i in range(25)]
    m8 = parent("id-m8", "Parafuso Sextavado M8", 99)  # o mais caro
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "parafuso+m8", listing(baratos + [m8], 26))
    fake.route("product-details/27", "obras360_product-details_osb-parent.json")

    found = run("parafuso m8", fake)

    details = [c.rsplit("=", 1)[1] for c in fake.calls if "product-details" in c]
    assert "id-m8" in details and len(details) == 20
    assert found.offers and all(o.title.startswith("Parafuso Sextavado M8") for o in found.offers)
    assert "+6 produtos não expandidos (limite de 20 por pesquisa)" in found.notes


# --- quick 261023-lee: o pai com mais palavras da pesquisa passa à frente do corte K=20 (CR-06) ---

def test_pai_com_mais_palavras_da_pesquisa_passa_a_frente_do_corte(fake):
    baratos = [parent(f"id-{i:02d}", "Parafuso Zincado Cabeça Chata", i + 1) for i in range(25)]
    m8 = parent("id-m8", "Parafuso Sextavado M8", 99)  # o mais caro; o "40" só está na variante
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "parafuso+m8x40", listing(baratos + [m8], 26))
    fake.route("product-details/27", "obras360_product-details_osb-parent.json")

    found = run("parafuso m8x40", fake)

    details = [c.rsplit("=", 1)[1] for c in fake.calls if "product-details" in c]
    assert "id-m8" in details and len(details) == 20
    assert "+6 produtos não expandidos (limite de 20 por pesquisa)" in found.notes


# --- G-01-5: na pesquisa alargada, só as ofertas que batem a pergunta completa (D-15 emendada) ---

def test_osb_12mm_alargada_mostra_so_a_placa_de_12mm(fake):
    import io

    from strata.models import Item, ItemResult
    from strata.report import print_item

    cola = copy.deepcopy(DETAIL)  # detalhe sintético da cola SikaBond: uma variante a 8,36 € com IVA
    k, v = next(iter(variants(cola).items()))
    for p in (v["prices"], v["prices_with_convertion_factor"]):
        p.update(final_price_unformatted="6.7967", final_price_with_tax_unformatted="8.359941",
                 conversion_factor="1", discounts=[])
    v["segment"], v["sku"] = "cola-sikabond-52", "0070120005"
    cola["meta_data"]["protected"]["attribute_values_prices"] = {k: v}
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "OSB+12+mm", "obras360_product-list_no-results.json")  # dispara D-14
    fake.route(LIST_URL + "OSB&", "obras360_product-list_osb.json")
    fake.route(DETAIL_URL + PLACA_ID, "obras360_product-details_osb-parent.json")
    fake.route(DETAIL_URL + COLA_ID, cola)
    it = Item(row=2, product="OSB 12 mm", qty=Decimal(30), unit="un")

    sr = asyncio.run(strata.search.search_store(obras360, it, fake))

    assert (sr.status, sr.broadened_query, sr.hidden) == ("ok", "OSB", 0)
    assert len(sr.offers) == 1
    o = sr.offers[0]
    assert " — 1 Placa 12 MM" in o.title
    assert fmt_eur(o.price) == "19,37 €"
    assert o.broadened
    assert sr.wide_only == 7  # a cola e as outras 6 espessuras
    out = io.StringIO()
    print_item(ItemResult(it, [sr]), out)
    text = out.getvalue()
    assert "  Obras 360: ok (pesquisa alargada: 'OSB')\n" in text
    assert "+7 ofertas escondidas: título sem 'OSB 12 mm'" in text
    assert "SikaBond" not in text
    assert "1 Placa 9 MM" not in text


# --- WR-17: na alargada, o produto da linha (rank) escolhe os pais antes do corte K=20 ---

def test_rank_poe_o_pai_do_produto_da_linha_a_frente_do_corte(fake):
    baratos = [parent(f"id-{i:02d}", "Pavê Bloco Pavimento Betão Cinza", i + 1) for i in range(25)]
    placa = parent("id-60x120", "Pavimento Cerâmico Retificado 60x120", 99)  # o mais caro
    fake.cache["obras360_widget"] = WIDGET
    fake.route(LIST_URL + "pavimento&", listing(baratos + [placa], 26))
    fake.route("product-details/27", "obras360_product-details_osb-parent.json")

    found = asyncio.run(obras360.search("pavimento", fake, rank="pavimento 60x120"))

    details = [c.rsplit("=", 1)[1] for c in fake.calls if "product-details" in c]
    assert "id-60x120" in details and len(details) == 20  # o corte K=20 não cresce
    assert all("search=pavimento&" in c for c in fake.calls if "product-list" in c)  # a pesquisa enviada não muda
    assert "+6 produtos não expandidos (limite de 20 por pesquisa)" in found.notes
