"""Regras da cadeia de recurso API → JSON-LD → browser, sem rede (D-08, D-13, D-14, D-15, D-16, D-17, D-19)."""

import asyncio
import io
from decimal import Decimal
from types import SimpleNamespace

import pytest

import strata.fetch
import strata.search
from conftest import FIXTURES, FakeFetcher
from strata.__main__ import main
from strata.fetch import Fetcher, StoreBlocked, StoreCaptcha, StoreError, StoreTimeout
from strata.jsonld import JS_PAGE
from strata.models import Found, Item, Offer
from strata.search import search_store
from strata.stores import allmat, bricomarche, obramat, obras360
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

    return SimpleNamespace(NAME=name, search=search, calls=calls, fetches=fetches,
                           search_page=lambda q: f"https://x.pt/?s={q}")


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
    assert f"antes do browser: API: HTTP 403; JSON-LD: {JS_PAGE}" in sr.notes
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
    assert sr.detail == f"API: HTTP 403; JSON-LD: {JS_PAGE}; browser: x"
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
    assert sr.detail.endswith(f"; JSON-LD: {JS_PAGE}; browser: x")


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
    assert f"antes do browser: API: desativado com --sem-principal; JSON-LD: {JS_PAGE}" in sr.notes


def test_sem_principal_na_linha_de_comandos(fake, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("placa osb 3 un\n\n"))
    route_api_stores(fake)
    fake.route("obramat.pt", StoreBlocked("HTTP 403"))  # senão o JSON-LD respondia pelo pedido simples
    browser = FakeFetcher()
    browser.cache = fake.cache
    route_obramat(browser)

    assert main(["pesquisar", "--sem-principal", "obramat"], fetch=fake, browser=browser) == 0

    osb = blocks(capsys.readouterr().out)["placa osb"]
    # o API desligado não pede nada; o JSON-LD pede a mesma página de pesquisa e leva o 403
    assert [c for c in fake.calls if "obramat" in c] == ["https://www.obramat.pt/search?q=placa+osb"]
    assert "  Obramat: ok" in osb and "método: browser" in osb
    assert "nota: antes do browser: API: desativado com --sem-principal; JSON-LD: HTTP 403" in osb
    assert "  Allmat: sem resultados" in osb and "  Bricomarché: ok" in osb  # as outras lojas ficam na API
    assert not browser.missing


def test_ordem_api_json_ld_browser():
    api, browser = transports()
    sr = go(fake_store("Falsa", StoreBlocked("HTTP 403"), StoreTimeout("demorou")), api, browser)
    assert sr.status == "bloqueada"
    assert sr.detail.index("API: ") < sr.detail.index("JSON-LD: ") < sr.detail.index("browser: ")


def test_allmat_sem_principal_responde_pelo_json_ld(fake):
    fake.cache["sem_principal"] = {"Allmat"}
    fake.route("allmat.pt/?s=cimento", "allmat_search-page_cimento.html")
    fake.route("liz-cimento-cola-branco", "allmat_product-page_liz-branco_jsonld.html")
    fake.route("allmat.pt/produto/", b"<html></html>")
    sr = asyncio.run(search_store(allmat, Item(row=2, product="cimento", qty=Decimal(1), unit="saco"), fake))
    assert sr.status == "ok"
    assert [o.method for o in sr.offers] == ["JSON-LD"]
    assert "antes do JSON-LD: API: desativado com --sem-principal" in sr.notes
    assert not [c for c in fake.calls if "wp-json" in c]


def test_obramat_bloqueada_no_api_e_no_json_ld_vai_ao_browser(fake):
    dd = StoreBlocked("HTTP 403 (verificação DataDome)")
    fake.route("obramat.pt", dd)
    browser = FakeFetcher()
    browser.cache = fake.cache
    route_obramat(browser)
    sr = asyncio.run(search_store(obramat, item("placa osb"), fake, browser))
    assert sr.status == "ok"
    assert {o.method for o in sr.offers} == {"browser"}
    assert ("antes do browser: API: HTTP 403 (verificação DataDome); JSON-LD: HTTP 403 (verificação DataDome)"
            in sr.notes)


def test_bricomarche_sem_principal_salta_o_json_ld_sem_pedidos(fake):
    fake.cache["sem_principal"] = {"Bricomarché"}
    browser = FakeFetcher()
    browser.cache = fake.cache
    route_api_stores(browser)
    sr = asyncio.run(search_store(bricomarche, item("placa osb"), fake, browser))
    assert sr.status == "ok"
    assert {o.method for o in sr.offers} == {"browser"}
    assert f"antes do browser: API: desativado com --sem-principal; JSON-LD: {JS_PAGE}" in sr.notes
    assert fake.calls == []


@pytest.mark.parametrize("cmd", ["pesquisar", "verificar"])
def test_sem_principal_loja_desconhecida(cmd):
    with pytest.raises(SystemExit) as e:
        main([cmd, "--sem-principal", "xpto"])
    assert e.value.code == 2


DD_403 = (FIXTURES / "obramat_curl-403-datadome.html").read_bytes()  # corpo real, 'rt':'i'
DD_CAPTCHA = DD_403.replace(b"'rt':'i'", b"'rt':'c'")


class RouteSession:
    """Sessão curl_cffi falsa: (substring do URL, estado, corpo); regista cada URL pedido."""

    def __init__(self, *routes):
        self.routes = routes
        self.urls: list[str] = []

    async def get(self, url):
        self.urls.append(url)
        status, body = next((st, b) for sub, st, b in self.routes if sub in url)
        return SimpleNamespace(status_code=status, headers={}, content=body, text=body.decode("utf-8"))


def no_wait(monkeypatch):
    """Sem os 3–5 s da Obramat nem os 0,5 s da Allmat: os Host leem LIMITS ao criar o Fetcher."""
    monkeypatch.setitem(strata.fetch.LIMITS, "www.obramat.pt", (1, 0.0, 0.0))
    monkeypatch.setitem(strata.fetch.LIMITS, "allmat.pt", (2, 0.0))


def test_captcha_obramat_abrir_a_mao_e_lista_continua(monkeypatch, capsys):
    no_wait(monkeypatch)
    monkeypatch.setattr(strata.search, "STORES", (allmat, obramat))
    session = RouteSession(
        ("obramat.pt", 403, DD_CAPTCHA),
        ("search=cimento", 200, (FIXTURES / "allmat_products_search-cimento.json").read_bytes()),
        ("allmat.pt", 200, b"[]"),
    )
    fetcher = Fetcher(session)
    browser = FakeFetcher()  # sem rotas: um pedido ao browser falharia o teste
    browser.cache = fetcher.cache
    monkeypatch.setattr("sys.stdin", io.StringIO("cimento cola 1 un\nplaca osb 2 un\n\n"))

    assert main(["pesquisar"], fetch=fetcher, browser=browser) == 0

    out = blocks(capsys.readouterr().out)
    first, second = out["cimento cola"], out["placa osb"]
    assert "  Obramat: abrir à mão — CAPTCHA em API: CAPTCHA da DataDome (HTTP 403)\n" in first
    assert "    abrir à mão: https://www.obramat.pt/search?q=cimento+cola\n" in first
    assert ("  Obramat: abrir à mão — CAPTCHA antes nesta execução: nenhum pedido a esta loja\n"
            "    abrir à mão: https://www.obramat.pt/search?q=placa+osb\n") in second
    assert "  Allmat: " in first and "  Allmat: " in second  # a outra loja continua (STORE-05)
    assert len([u for u in session.urls if "obramat" in u]) == 1
    assert browser.calls == []


def test_verificacao_do_dispositivo_nao_e_captcha(monkeypatch):
    no_wait(monkeypatch)
    fetcher = Fetcher(RouteSession(("obramat.pt", 403, DD_403)))
    sr = asyncio.run(search_store(obramat, item("placa osb"), fetcher, None))
    assert sr.status == "bloqueada"
    assert "API: HTTP 403 (verificação DataDome)" in sr.detail
    assert sr.link is None and not fetcher.cache["captcha"]


@pytest.mark.parametrize("store, link", [
    (allmat, "https://allmat.pt/?s=placa+osb&post_type=product"),
    (bricomarche, "https://www.bricomarche.pt/?s=placa+osb&post_type=product"),
    (obras360, "https://www.obras360.pt/pesquisa?search=placa+osb"),
    (obramat, "https://www.obramat.pt/search?q=placa+osb"),
])
def test_search_page_das_4_lojas(store, link):
    assert store.search_page("placa osb") == link


def test_captcha_no_browser_da_allmat(fake):
    fake.route("allmat.pt", StoreBlocked("HTTP 403"))
    browser = FakeFetcher().route("allmat.pt", StoreCaptcha("CAPTCHA da DataDome no browser"))
    browser.cache = fake.cache
    sr = asyncio.run(search_store(allmat, item("placa osb"), fake, browser))
    assert sr.status == "abrir à mão"
    assert sr.detail == "CAPTCHA em browser: CAPTCHA da DataDome no browser; antes: API: HTTP 403; JSON-LD: HTTP 403"
    assert sr.link == "https://allmat.pt/?s=placa+osb&post_type=product"
    assert "Allmat" in fake.cache["captcha"]
