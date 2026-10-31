"""Corrida completa sem rede com as quatro lojas reais de strata.search.STORES (STORE-05)."""

import io
import re

import strata.search
from strata.__main__ import main
from strata.stores import allmat, bricomarche, obramat, obras360

ALLMAT = "allmat.pt/wp-json/wc/store/v1/products?search="
BRICO = "bricomarche.pt/wp-json/wc/store/v1/products?search="
WIDGET = "f1f5fb06-09e7-4519-8f44-9b3cd0093460"
O360_LIST = f"product-list/{WIDGET}?search="
O360_DETAIL = "product-details/27?_beevo_decoded_params[0][product_id]="
PLACA_ID = "f807c893-c3eb-4630-a409-8a0a7bbc88c1"
ORDER = ("Allmat:", "Bricomarché:", "Obras 360:", "Obramat:")


def blocks(out: str) -> dict[str, str]:
    """Texto de cada item, pelo produto do cabeçalho 'Linha N — <produto> (...)'."""
    parts = re.split(r"^Linha \d+ — ", out, flags=re.M)[1:]
    return {p.split(" (", 1)[0]: p for p in parts}


def test_tres_itens_tres_lojas_pela_ordem(fake, monkeypatch, capsys):
    assert strata.search.STORES == (allmat, bricomarche, obras360, obramat)  # as lojas reais, sem monkeypatch
    monkeypatch.setattr("sys.stdin", io.StringIO("placa osb 3 un\ncimento 10 saco\nxyzqwkk 1 un\n\n"))
    fake.route(ALLMAT + "placa+osb", "allmat_products_search-osb_no-results.json")
    fake.route(ALLMAT + "cimento", "allmat_products_search-cimento.json")
    fake.route(ALLMAT + "xyzqwkk", [])
    fake.route(BRICO + "placa+osb", "bricomarche_products_search-osb.json")
    fake.route("parent=47412&", "bricomarche_variations_parent-47412.json")
    fake.route("type=variation", [])  # o outro pai "Placa Osb" sem variações com preço
    fake.route(BRICO + "cimento", [])
    fake.route(BRICO + "xyzqwkk", [])
    fake.cache["obras360_widget"] = WIDGET
    fake.route(O360_LIST + "placa+osb", "obras360_product-list_osb.json")
    fake.route(O360_DETAIL + PLACA_ID, "obras360_product-details_osb-parent.json")
    fake.route(O360_LIST, "obras360_product-list_no-results.json")  # cimento e xyzqwkk
    fake.route("obramat.pt/search?q=placa+osb", "obramat_search-osb_browser.html")
    fake.route("obramat.pt/produtos/", "obramat_product-osb-18_ctx201_tiers.html")  # as 3 primeiras placas
    fake.route("obramat.pt/search?q=", "obramat_search-no-results_browser.html")  # cimento e xyzqwkk

    assert main(["pesquisar"], fetch=fake) == 0

    by_item = blocks(capsys.readouterr().out)
    assert list(by_item) == ["placa osb", "cimento", "xyzqwkk"]
    for product, text in by_item.items():
        pos = [text.index(f"  {name}") for name in ORDER]
        assert pos == sorted(pos), product
    for name in ORDER:
        assert f"  {name} sem resultados" in by_item["xyzqwkk"], name
    osb = by_item["placa osb"]
    assert "  Allmat: sem resultados" in osb
    assert "  Bricomarché: ok" in osb and "loja: Monção" in osb
    assert "mais barata sem stock: 18,49 € em Coina - Barreiro" in osb
    assert "  Obras 360: ok" in osb and "IVA: indicado pela loja (tax_percentage=23)" in osb
    assert "  Obramat: ok" in osb and "loja: OBRAMAT Lisboa - Alfragide" in osb
    assert "+1 ofertas escondidas: título sem 'placa osb'" in osb  # a tinta para piscinas
    assert "+1 ofertas não mostradas" in osb  # 6 placas, 5 mostradas
    assert "  Allmat: ok" in by_item["cimento"] and "4,22 €" in by_item["cimento"]
    assert "  Obramat: sem resultados" in by_item["cimento"]
