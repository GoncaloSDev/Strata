"""Pesquisa por loja: pesquisa alargada (D-14), filtro de título (D-15) e estados de loja (STORE-05)."""

import asyncio
import io
import json
from decimal import Decimal
from types import SimpleNamespace

import pytest
from curl_cffi.requests.exceptions import Timeout

import strata.search
from strata.fetch import Fetcher
from strata.models import Found, Item, ItemResult, Offer
from strata.report import print_item
from strata.search import search_store
from strata.stores import allmat
from strata.words import broadened, title_matches

FIXTURES = __import__("pathlib").Path(__file__).parent / "fixtures"
SEARCH = "allmat.pt/wp-json/wc/store/v1/products?search="


def offer(title="t", price="1", **kw) -> Offer:
    return Offer(store="X", title=title, url="https://x.pt/p", price=Decimal(price),
                 vat_origin="regra da loja", vat_evidence="e", **kw)


def item(product="cimento", unit="saco") -> Item:
    return Item(row=2, product=product, qty=Decimal(10), unit=unit)


def fake_store(name, *answers):
    """Loja falsa: cada chamada devolve a resposta seguinte (Found, Exception ou corrotina)."""
    calls = []

    async def search(query, fetch):
        calls.append(query)
        a = answers[min(len(calls), len(answers)) - 1]
        if isinstance(a, BaseException):
            raise a
        if callable(a):
            return await a()
        return a

    return SimpleNamespace(NAME=name, search=search, calls=calls)


@pytest.mark.parametrize("query, title, expected", [
    ("cimento", "PAINEL AQUECIMENTO", False),
    ("cimento", "LIZ CIMENTO COLA CINZA", True),
    ("cimento", "Cimento-Cola", True),
    ("OSB 12mm", "PLACA OSB 12 MM", True),
    ("placas osb", "Placa OSB 9-30MM", True),
    ("OSB.", "Placa OSB", True),
])
def test_title_matches(query, title, expected):
    assert title_matches(query, title) is expected


@pytest.mark.parametrize("query, expected", [
    ("OSB 12mm", "OSB"),
    ("placa osb 12 mm", "placa osb"),
    ("cimento 25kg", "cimento"),
    ("osb", None),
    ("12mm", None),
])
def test_broadened(query, expected):
    assert broadened(query) == expected


def test_pesquisa_alargada_quando_a_loja_da_zero():
    store = fake_store("Falsa", Found([], 0), Found([offer("PLACA OSB")], 1))
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), None))
    assert sr.status == "ok"
    assert sr.broadened_query == "OSB"
    assert [o.broadened for o in sr.offers] == [True]
    assert store.calls == ["OSB 12mm", "OSB"]


def test_pesquisa_alargada_tambem_a_zero():
    store = fake_store("Falsa", Found([], 0))
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), None))
    assert sr.status == "sem resultados"
    assert sr.detail == "também sem resultados com 'OSB'"
    assert store.calls == ["OSB 12mm", "OSB"]


def test_sem_pesquisa_alargada_quando_nada_muda():
    store = fake_store("Falsa", Found([], 0))
    sr = asyncio.run(search_store(store, item("osb", "un"), None))
    assert sr.status == "sem resultados"
    assert store.calls == ["osb"]


def test_allmat_esconde_titulos_sem_as_palavras(fake):
    rows = json.loads((FIXTURES / "allmat_products_search-cimento.json").read_bytes(), parse_float=Decimal)
    rows.append({**rows[0], "id": 99999, "name": "PAINEL AQUECIMENTO", "permalink": "https://allmat.pt/produto/painel/"})
    fake.route(SEARCH + "cimento", rows)
    sr = asyncio.run(search_store(allmat, item(), fake))
    assert sr.status == "ok"
    assert len(sr.offers) == 3
    assert sr.hidden == 1
    out = io.StringIO()
    print_item(ItemResult(item(), [sr]), out)
    assert "+1 ofertas escondidas: título sem 'cimento'" in out.getvalue()


class FakeSession:
    def __init__(self, status=200, headers=None, body=b"[]", exc=None):
        self.r = SimpleNamespace(status_code=status, headers=headers or {}, content=body,
                                 text=body.decode("utf-8"))
        self.exc = exc

    async def get(self, url):
        if self.exc:
            raise self.exc
        return self.r


@pytest.mark.parametrize("session, expected", [
    (FakeSession(403), "bloqueada — HTTP 403"),
    (FakeSession(200, {"cf-mitigated": "challenge"}), "bloqueada"),
    (FakeSession(500), "erro — StoreError: HTTP 500"),
    (FakeSession(200, body=b"<html><title>Just a moment...</title></html>"), "bloqueada — página de desafio"),
    (FakeSession(200, body=b"<html><p>outra coisa</p></html>"), "resposta não é JSON"),
    (FakeSession(exc=Timeout("demorou")), "tempo esgotado"),
])
def test_estados_da_loja_por_tipo_de_falha(session, expected):
    sr = asyncio.run(search_store(allmat, item(), Fetcher(session)))
    shown = f"{sr.status} — {sr.detail}"
    assert expected in shown
    assert sr.store == "Allmat"
    if "JSON" in expected:
        assert sr.status == "erro"


def test_prazo_esgotado(monkeypatch):
    async def slow():
        await asyncio.sleep(1)
        return Found([], 0)

    monkeypatch.setattr(strata.search, "DEADLINE_S", 0.05)
    sr = asyncio.run(search_store(fake_store("Lenta", slow), item(), None))
    assert sr.status == "tempo esgotado"


def test_allmat_conteudo_pelo_titulo(fake):
    fake.route(SEARCH + "cimento", "allmat_products_search-cimento.json")
    found = asyncio.run(allmat.search("cimento", fake))
    by_title = {o.title: o for o in found.offers}
    liz = by_title["LIZ CIMENTO COLA CINZA SACO 25 KG REF 01.001"]
    assert (liz.content, liz.content_unit) == (Decimal("25"), "kg")
    fischer = by_title["FISCHER CIMENTO BARBACOAS"]
    assert (fischer.content, fischer.content_unit) == (Decimal("1"), "un")


def test_ordem_estavel_pelo_preco_na_unidade_pedida():
    offers = [
        offer("a", "5", content=Decimal(1), content_unit="kg"),   # 5 €/kg
        offer("b", "6", content=Decimal(2), content_unit="kg"),   # 3 €/kg
        offer("c", "1"),                                          # não convertível
        offer("d", "9", content=Decimal(3), content_unit="kg"),   # 3 €/kg
    ]
    store = fake_store("Falsa", Found(offers, 4))
    sr = asyncio.run(search_store(store, item("cola", "kg"), None))
    assert [o.title for o in sr.offers] == ["b", "d", "a", "c"]
    assert sr.offers[-1].note == "não convertível para kg: conteúdo da embalagem desconhecido"
    assert sr.offers[0].note == ""


def test_allmat_cimento_saco_mais_barato_primeiro(fake):
    fake.route(SEARCH + "cimento", "allmat_products_search-cimento.json")
    sr = asyncio.run(search_store(allmat, item("cimento", "saco"), fake))
    assert [o.price for o in sr.offers] == [Decimal("4.22"), Decimal("4.72"), Decimal("6.60")]


def test_tres_lojas_pela_ordem_de_stores(monkeypatch):
    stores = (
        fake_store("Primeira", Found([offer("CIMENTO COLA")], 1)),
        fake_store("Segunda", ValueError("campo em falta")),
        fake_store("Terceira", Found([], 0)),
    )
    monkeypatch.setattr(strata.search, "STORES", stores)

    async def go():
        return [r async for r in strata.search.run([item()], None)]

    (result,) = asyncio.run(go())
    out = io.StringIO()
    print_item(result, out)
    text = out.getvalue()
    heads = ["Primeira: ok", "Segunda: erro — ValueError: campo em falta", "Terceira: sem resultados"]
    for h in heads:
        assert h in text, h
    assert text.index(heads[0]) < text.index(heads[1]) < text.index(heads[2])


# --- 01-06: verificar (STORE-07) ---

from strata.__main__ import main  # noqa: E402
from strata.fetch import StoreBlocked  # noqa: E402
from strata.stores import bricomarche, obras360  # noqa: E402

BRICO = "bricomarche.pt/wp-json/wc/store/v1/products?search="
SPLENDOR = "allmat.pt/produto/splendor/"
BOX_PAGE = (FIXTURES / "allmat_product-page_39233_box.html").read_text(encoding="utf-8")
WIDGET = "f1f5fb06-09e7-4519-8f44-9b3cd0093460"
O360_LIST = f"product-list/{WIDGET}?search="
O360_DETAIL = "product-details/27?_beevo_decoded_params[0][product_id]="
PLACA_ID = "f807c893-c3eb-4630-a409-8a0a7bbc88c1"
NO_DETAIL = {"success": False, "meta_data": {"protected": {"attribute_values_prices": []}}}


def load(name):
    return json.loads((FIXTURES / name).read_bytes(), parse_float=Decimal)


def m2_row(cents="1374"):
    return {
        "id": 39233, "name": "SPLENDOR PAVIMENTO", "permalink": "https://allmat.pt/produto/splendor/",
        "prices": {"price": cents, "currency_minor_unit": 2},
        "price_html": '<span class="amount">13,74 €</span>\t<span class="wd-price-unit">M2</span>',
        "stock_availability": {"text": "12 em stock"},
    }


def brico_variation(variation="Loja: Coina - Barreiro"):
    return {
        "id": 2, "parent": 1, "variation": variation,
        "permalink": "https://www.bricomarche.pt/produto/cimento-cola/?attribute_pa_loja=coina-barreiro",
        "prices": {"price": "500", "currency_minor_unit": 2},
        "stock_availability": {"text": "12 em stock", "class": "in-stock"},
    }


def route_canaries(fake, *, allmat_cimento="allmat_products_search-cimento.json", box_page=BOX_PAGE,
                   pavimento=None, brico_variations=None, o360_detail="obras360_product-details_osb-parent.json"):
    fake.route(SEARCH + "cimento", allmat_cimento)
    fake.route(SEARCH + "pavimento", pavimento or [m2_row()])
    fake.route(SPLENDOR, box_page.encode("utf-8"))
    fake.route(BRICO + "cimento", [{"id": 1, "name": "Cimento cola",
                                    "prices": {"price": "500", "price_range": None, "currency_minor_unit": 2}}])
    fake.route("parent=1&", brico_variations or [brico_variation()])
    fake.cache["obras360_widget"] = WIDGET
    fake.route(O360_LIST + "osb", "obras360_product-list_osb.json")
    fake.route(O360_DETAIL + PLACA_ID, o360_detail)
    fake.route(O360_DETAIL, NO_DETAIL)  # a cola SikaBond: vai para a nota, não falha o verificar


def only(monkeypatch, store, term):
    monkeypatch.setattr(strata.search, "CANARIES", ((store, term),))


def check(fake):
    return asyncio.run(strata.search.verificar(fake))


def test_verificar_quatro_lojas_ok(fake):
    route_canaries(fake)
    rows = check(fake)
    assert [label for label, _, _ in rows] == [
        "Allmat (cimento)", "Allmat (pavimento)", "Bricomarché (cimento)", "Obras 360 (osb)"]
    assert all(ok for _, ok, _ in rows), rows


def test_verificar_comando_imprime_ok_e_sai_com_0(fake, capsys):
    route_canaries(fake)
    assert main(["verificar"], fetch=fake) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len([ln for ln in lines if ": OK — " in ln]) == 4
    assert "Allmat (cimento): OK — 3 ofertas, mais barata 4,22 €" in lines
    assert "Obras 360 (osb): OK — 7 ofertas, mais barata 15,02 €" in lines


def test_verificar_preco_zero_fica_na_nota(fake, monkeypatch):
    rows = load("allmat_products_search-cimento.json")
    rows[0]["prices"]["price"] = "0"
    route_canaries(fake, allmat_cimento=rows)
    only(monkeypatch, allmat, "cimento")
    ((_, ok, msg),) = check(fake)
    assert ok, msg
    assert msg.startswith("2 ofertas")


def test_verificar_todos_a_zero_sem_ofertas(fake, monkeypatch):
    rows = load("allmat_products_search-cimento.json")
    for r in rows:
        r["prices"]["price"] = "0"
    route_canaries(fake, allmat_cimento=rows)
    only(monkeypatch, allmat, "cimento")
    assert check(fake) == [("Allmat (cimento)", False, "sem ofertas")]


def test_verificar_obras360_iva_da_loja_nao_e_23(fake, monkeypatch, capsys):
    detail = load("obras360_product-details_osb-parent.json")
    for v in detail["meta_data"]["protected"]["attribute_values_prices"].values():
        v["prices"]["tax_percentage"] = 6
        item_prices = v["prices_with_convertion_factor"]
        item_prices["final_price_with_tax_unformatted"] = Decimal(item_prices["final_price_unformatted"]) * Decimal("1.06")
    route_canaries(fake, o360_detail=detail)
    only(monkeypatch, obras360, "osb")
    assert main(["verificar"], fetch=fake) == 1
    assert "Obras 360 (osb): FALHOU — IVA da loja não é 23%" in capsys.readouterr().out.splitlines()


def test_verificar_bricomarche_sem_nome_de_loja(fake, monkeypatch):
    route_canaries(fake, brico_variations=[brico_variation(variation="")])
    only(monkeypatch, bricomarche, "cimento")
    assert check(fake) == [("Bricomarché (cimento)", False, "sem nome de loja")]


def test_verificar_allmat_caixa_incoerente(fake, monkeypatch):
    route_canaries(fake, box_page=BOX_PAGE.replace(">9,99<", ">5,00<"))
    only(monkeypatch, allmat, "pavimento")
    assert check(fake) == [("Allmat (pavimento)", False, "caixa incoerente em SPLENDOR PAVIMENTO")]


def test_verificar_allmat_nenhuma_area_de_caixa_lida(fake, monkeypatch):
    route_canaries(fake, pavimento=[m2_row(cents="999")])  # preço da API sem bloco na página
    only(monkeypatch, allmat, "pavimento")
    assert check(fake) == [("Allmat (pavimento)", False, "nenhuma área de caixa lida")]


@pytest.mark.parametrize("answer, expected", [
    (StoreBlocked("HTTP 403"), "estado bloqueada: HTTP 403"),
    ({"não": "é lista"}, "estado erro: ValueError: resposta da Allmat não é uma lista de produtos"),
])
def test_verificar_loja_bloqueada_ou_em_erro(fake, monkeypatch, answer, expected):
    route_canaries(fake, allmat_cimento=answer)
    only(monkeypatch, allmat, "cimento")
    assert check(fake) == [("Allmat (cimento)", False, expected)]
