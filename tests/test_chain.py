"""Regras da cadeia de recurso API → browser, sem rede (D-08, D-14, D-15, D-16, D-17)."""

import asyncio
import io
from decimal import Decimal
from types import SimpleNamespace

import pytest

import strata.search
from conftest import FakeFetcher
from strata.__main__ import main
from strata.fetch import StoreBlocked, StoreError, StoreTimeout
from strata.models import Found, Item, Offer
from strata.search import search_store
from test_e2e import blocks, route_api_stores, route_obramat


def offer(title="PLACA OSB", price="10") -> Offer:
    return Offer(store="Falsa", title=title, url="https://x.pt/p", price=Decimal(price),
                 vat_origin="regra da loja", vat_evidence="e")


def item(product="osb") -> Item:  # "osb" não tem pesquisa alargada: uma chamada por degrau
    return Item(row=2, product=product, qty=Decimal(1), unit="un")


def fake_store(name, *answers):
    """Loja falsa: cada chamada devolve a resposta seguinte e regista o transporte recebido."""
    calls, fetches = [], []

    async def search(query, fetch, rank=None):
        calls.append(query)
        fetches.append(fetch)
        a = answers[min(len(calls), len(answers)) - 1]
        if isinstance(a, BaseException):
            raise a
        if callable(a):
            return await a()
        return a

    return SimpleNamespace(NAME=name, search=search, calls=calls, fetches=fetches)


def transports():
    """API e browser falsos com a mesma cache, como o Fetcher e o BrowserFetcher."""
    cache = {}  # "kind" distingue os dois: SimpleNamespace compara por atributos
    return SimpleNamespace(kind="API", cache=cache), SimpleNamespace(kind="browser", cache=cache)


def go(store, fetch, browser, product="osb"):
    return asyncio.run(search_store(store, item(product), fetch, browser))


def test_sem_resultados_nao_escala():
    api, browser = transports()
    store = fake_store("Falsa", Found([], 0))
    sr = go(store, api, browser)
    assert sr.status == "sem resultados"
    assert store.fetches == [api]
    assert "browser_only" not in api.cache


def test_tudo_escondido_pelo_filtro_nao_escala():
    api, browser = transports()
    store = fake_store("Falsa", Found([], 5, hidden=5))
    sr = go(store, api, browser, "tinta branca")
    assert sr.status == "ok"
    assert sr.detail == "0 ofertas mostradas; 5 escondidas pelo filtro de título"
    assert browser not in store.fetches


def test_bloqueada_na_api_vai_ao_browser():
    api, browser = transports()
    store = fake_store("Falsa", StoreBlocked("HTTP 403"), Found([offer()], 1))
    sr = go(store, api, browser)
    assert sr.status == "ok"
    assert store.fetches == [api, browser]
    assert [o.method for o in sr.offers] == ["browser"]
    assert "antes do browser: API: HTTP 403" in sr.notes
    assert "Falsa" in api.cache["browser_only"]


def test_resposta_da_api_marca_metodo_api():
    api, browser = transports()
    sr = go(fake_store("Falsa", Found([offer()], 1)), api, browser)
    assert [o.method for o in sr.offers] == ["API"]
    assert sr.notes == []


def test_loja_no_browser_salta_a_api_no_item_seguinte():
    api, browser = transports()
    api.cache["browser_only"] = {"Falsa"}
    store = fake_store("Falsa", Found([offer()], 1))
    sr = go(store, api, browser)
    assert store.fetches == [browser]
    assert sr.status == "ok" and sr.notes == []


def test_todos_falham_bloqueada_com_o_motivo_de_cada_degrau():
    api, browser = transports()
    sr = go(fake_store("Falsa", StoreBlocked("HTTP 403"), StoreError("x")), api, browser)
    assert sr.status == "bloqueada"
    assert sr.detail.index("API: HTTP 403") < sr.detail.index("browser: StoreError: x")
    assert "browser_only" not in api.cache


@pytest.mark.parametrize("first, status", [
    (StoreTimeout("demorou"), "tempo esgotado"),
    (ValueError("campo em falta"), "erro"),
])
def test_todos_falham_estado_pela_prioridade(first, status):
    api, browser = transports()
    sr = go(fake_store("Falsa", first, StoreError("x")), api, browser)
    assert sr.status == status
    assert sr.detail.startswith("API: ")
    assert "browser: StoreError: x" in sr.detail


def test_prazo_partilhado_acaba_no_browser(monkeypatch):
    async def slow():
        await asyncio.sleep(1)
        return Found([offer()], 1)

    monkeypatch.setattr(strata.search, "DEADLINE_S", 0.05)
    api, browser = transports()
    sr = go(fake_store("Falsa", StoreBlocked("HTTP 403"), slow), api, browser)
    assert sr.status == "tempo esgotado"
    assert sr.detail.startswith("mais de 0.05 s durante browser; antes: API: HTTP 403")


def test_sem_browser_diz_porque():
    api, _ = transports()
    sr = go(fake_store("Falsa", StoreBlocked("HTTP 403")), api, None)
    assert sr.status == "bloqueada"
    assert "browser: sem browser nesta execução" in sr.detail


def test_sem_principal_salta_a_api():
    api, browser = transports()
    api.cache["sem_principal"] = {"Falsa"}
    store = fake_store("Falsa", Found([offer()], 1))
    sr = go(store, api, browser)
    assert store.fetches == [browser]
    assert [o.method for o in sr.offers] == ["browser"]
    assert "antes do browser: API: desativado com --sem-principal" in sr.notes


def test_sem_principal_na_linha_de_comandos(fake, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("placa osb 3 un\n\n"))
    route_api_stores(fake)
    route_obramat(fake)  # o pedido simples responderia bem
    browser = FakeFetcher()
    browser.cache = fake.cache
    route_obramat(browser)

    assert main(["pesquisar", "--sem-principal", "obramat"], fetch=fake, browser=browser) == 0

    osb = blocks(capsys.readouterr().out)["placa osb"]
    assert not [c for c in fake.calls if "obramat" in c]
    assert "  Obramat: ok" in osb and "método: browser" in osb
    assert "nota: antes do browser: API: desativado com --sem-principal" in osb
    assert "  Allmat: sem resultados" in osb and "  Bricomarché: ok" in osb  # as outras lojas ficam na API
    assert not browser.missing


@pytest.mark.parametrize("cmd", ["pesquisar", "verificar"])
def test_sem_principal_loja_desconhecida(cmd):
    with pytest.raises(SystemExit) as e:
        main([cmd, "--sem-principal", "xpto"])
    assert e.value.code == 2
