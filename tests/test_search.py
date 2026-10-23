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
