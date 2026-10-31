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


def nofetch():
    """Transporte sem pedidos: só a cache da execução, que a cadeia lê (D-08)."""
    return SimpleNamespace(cache={})


def fake_store(name, *answers):
    """Loja falsa: cada chamada devolve a resposta seguinte (Found, Exception ou corrotina)."""
    calls, ranks = [], []

    async def search(query, fetch, rank=None):
        calls.append(query)
        ranks.append(rank)
        a = answers[min(len(calls), len(answers)) - 1]
        if isinstance(a, BaseException):
            raise a
        if callable(a):
            return await a()
        return a

    return SimpleNamespace(NAME=name, search=search, calls=calls, ranks=ranks)


@pytest.mark.parametrize("query, title, expected", [
    ("cimento", "PAINEL AQUECIMENTO", False),
    ("cimento", "LIZ CIMENTO COLA CINZA", True),
    ("cimento", "Cimento-Cola", True),
    ("OSB 12mm", "PLACA OSB 12 MM", True),
    ("placas osb", "Placa OSB 9-30MM", True),
    ("OSB.", "Placa OSB", True),
    # CR-01: género, palavras de ligação e plurais em -eis/-ões/-res
    ("tinta branca", "Tinta Plástica 15L Branco Mate", True),
    ("cola de contacto", "Cola Contacto 1L", True),
    ("painéis", "Painel sandwich", True),
    ("luzes", "Luz LED", True),
    ("colheres", "Colher de pedreiro", True),
    ("portões", "Portão seccionado", True),
    ("lustres", "Lustre de cristal", True),
    ("aquecimento", "Cimento cola", False),
    ("tinta branca", "Fita Pintura Branca", False),
    ("tinta branca", "Tinta Preta", False),
    ("porta", "Portão seccionado", False),
    # CR-03: medidas coladas por "x", "Lt"/"litros" e sufixos de classe
    ("osb 18mm", "Chapa Osb 2440X590X18Mm", True),
    ("12mm", "Placa 2440x1220x12 mm", True),
    ("tinta 15L", "Tinta 15 Lt", True),
    ("tinta 15 litros", "Tinta 15L", True),
    ("OSB 12mm", "Placa OSB3 12 mm", True),
    ("osb 12mm", "Chapa Osb 2440X590X18Mm", False),
    # CR-05: plurais -ais/-is/-ens/-óis e palavras de 3 letras
    ("perfis", "Perfil alumínio", True),
    ("funis", "Funil", True),
    ("canais", "Canal", True),
    ("ferragens", "Ferragem", True),
    ("lençóis", "Lençol", True),
    ("pás", "Pá", True),
    ("lápis", "Lápis", True),
    ("jacuzzis", "Jacuzzi", True),
    ("táxis", "Táxi", True),
    ("projetor ip65", "Projetor LED IP65", True),
    ("azulejo 2,5 m²", "Azulejo 2,5 m2", True),
    ("projetor ip65", "Projetor LED IP44", False),
    # WR-12: -eis átono de têxtil e plurais nasais (-ins/-ons/-uns); -éis tónico continua -el
    ("mantas geotêxteis", "Manta Geotêxtil", True),
    ("têxteis", "Têxtil", True),
    ("coxins", "Coxim", True),
    ("jardins", "Jardim", True),
    ("pincéis", "Pincel", True),
    ("papéis", "Papel", True),
    ("listéis", "Listel", True),
    ("plafons", "Plafon LED", True),
    # WR-13: unidades por extenso
    ("tubo 3 metros", "Tubo 3m", True),
    ("cimento 25 quilos", "Cimento 25kg", True),
    # WR-07: medida com várias partes na pesquisa tem de estar seguida no título
    ("azulejo 30x30", "Azulejo 30x60", False),
    ("tubo 20x20", "Tubo Quadrado 20x40x1,5", False),
    ("azulejo 30x30", "Azulejo 30X30 cm", True),
    ("azulejo 30x30", "Azulejo 30 x 30 cm", True),
    ("tubo 20x20", "Tubo Quadrado 20x20x1,5", True),
    ("parafuso m8x40", "Parafuso Sextavado M8 — 40", True),
    ("parafuso m12x40", "Parafuso Sextavado M12 — 40", True),  # rosca de 2 dígitos não lê "2x40"
    ("parafuso 4x40", "Parafuso 4x40mm", False),  # WR-09 (fora do âmbito): "40" sem unidade não bate em "40mm"
    # WR-14: a medida não depende da ordem das partes; "×" e "60 x 120" contam como "60x120"
    ("pavimento 120x60", "Pavimento 60x120", True),
    ("azulejo 30x30", "Azulejo 30×30 cm", True),
    ("placa 1250x2500x12mm", "Placa OSB 2500x1250x12mm", True),
    ("azulejo 30 x 30", "Azulejo 30x30", True),
    ("pavimento 60 x 120", "PAVIMENTO 60X120", True),
])
def test_title_matches(query, title, expected):
    assert title_matches(query, title) is expected


@pytest.mark.parametrize("query, expected", [
    ("OSB 12mm", "OSB"),
    ("placa osb 12 mm", "placa osb"),
    ("cimento 25kg", "cimento"),
    ("osb", None),
    ("12mm", None),
    ("tinta 15 litros", "tinta"),  # IN-08
    ("tubo 3 metros", "tubo"),  # WR-13
    ("cimento 25 quilos", "cimento"),
    ("tinta 15 l.", "tinta"),
    ("parafuso 10 unidades", "parafuso"),
    ("metro articulado 2m", "metro articulado"),  # unidade só a seguir a um número
    # WR-15: o "x" (ou "×") solto nunca fica na alargada
    ("tela 1 m x 25 m", "tela"),
    ("osb 12 mm x 2500 x 1250", "osb"),
    ("tela 1 m × 25 m", "tela"),
    ("tela 1m x 25m", "tela"),
    ("tela 1 x 25 m", "tela"),
])
def test_broadened(query, expected):
    assert broadened(query) == expected


def test_pesquisa_alargada_quando_a_loja_da_zero():
    store = fake_store("Falsa", Found([], 0), Found([offer("PLACA OSB")], 1))
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), nofetch()))
    assert sr.status == "ok"
    assert sr.broadened_query == "OSB"
    assert [o.broadened for o in sr.offers] == [True]
    assert store.calls == ["OSB 12mm", "OSB"]
    assert store.ranks == [None, "OSB 12mm"]  # WR-17: a pesquisa enviada fica "OSB"; o produto só ordena


def test_pesquisa_alargada_tambem_a_zero():
    store = fake_store("Falsa", Found([], 0))
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), nofetch()))
    assert sr.status == "sem resultados"
    assert sr.detail == "também sem resultados com 'OSB'"
    assert store.calls == ["OSB 12mm", "OSB"]


def test_sem_pesquisa_alargada_quando_nada_muda():
    store = fake_store("Falsa", Found([], 0))
    sr = asyncio.run(search_store(store, item("osb", "un"), nofetch()))
    assert sr.status == "sem resultados"
    assert store.calls == ["osb"]


def heading(sr, product):
    out = io.StringIO()
    print_item(ItemResult(item(product, "un"), [sr]), out)
    return out.getvalue().splitlines()[1]


def report(sr, product):
    out = io.StringIO()
    print_item(ItemResult(item(product, "un"), [sr]), out)
    return out.getvalue()


def test_tudo_escondido_diz_quantas_no_cabecalho():
    store = fake_store("Falsa", Found([], 8, hidden=8))
    sr = asyncio.run(search_store(store, item("tinta branca", "L"), nofetch()))
    assert (sr.status, sr.offers) == ("ok", [])
    assert sr.detail == "0 ofertas mostradas; 8 escondidas pelo filtro de título"
    assert store.calls == ["tinta branca"]  # sem números: broadened dá None
    assert heading(sr, "tinta branca") == "  Falsa: ok — 0 ofertas mostradas; 8 escondidas pelo filtro de título"


def test_tudo_escondido_com_medidas_tenta_a_alargada():
    store = fake_store("Falsa", Found([], 5, hidden=5), Found([offer("PLACA OSB 9 MM")], 1))
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), nofetch()))
    assert store.calls == ["OSB 12mm", "OSB"]
    assert sr.broadened_query == "OSB"
    assert [o.broadened for o in sr.offers] == [True]
    assert sr.detail == "1.ª pesquisa: 5 escondidas pelo filtro de título com 'OSB 12mm'"
    assert heading(sr, "OSB 12mm") == ("  Falsa: ok — 1.ª pesquisa: 5 escondidas pelo filtro de título com 'OSB 12mm'"
                                       " (pesquisa alargada: 'OSB')")


@pytest.mark.parametrize("second", [Found([], 3, hidden=3), Found([], 0)])
def test_tudo_escondido_alargada_sem_ofertas_fica_a_primeira(second):
    store = fake_store("Falsa", Found([], 5, hidden=5), second)
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), nofetch()))
    assert store.calls == ["OSB 12mm", "OSB"]
    assert (sr.status, sr.broadened_query, sr.hidden) == ("ok", None, 5)
    assert sr.detail == "0 ofertas mostradas; 5 escondidas pelo filtro de título"
    assert "também sem ofertas com 'OSB'" in sr.notes



# --- G-01-5: na pesquisa alargada, só as que batem a pergunta completa (D-15 emendada) ---

def test_alargada_mostra_so_as_que_batem_a_pergunta_completa():
    wide = Found([offer("COLA PARA OSB", "8"), offer("PLACA OSB 12 MM X", "25"), offer("PLACA OSB 9 MM", "15"),
                  offer("PLACA OSB3 12mm", "19")], 4, hidden=3)
    store = fake_store("Falsa", Found([], 0), wide)
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), nofetch()))
    assert [o.title for o in sr.offers] == ["PLACA OSB3 12mm", "PLACA OSB 12 MM X"]  # mais baratas primeiro
    assert all(o.broadened for o in sr.offers)
    assert (sr.status, sr.broadened_query, sr.hidden, sr.wide_only) == ("ok", "OSB", 3, 2)
    text = report(sr, "OSB 12mm")
    assert "  Falsa: ok (pesquisa alargada: 'OSB')\n" in text
    assert "    +3 ofertas escondidas: título sem 'OSB'\n" in text
    assert "    +2 ofertas escondidas: título sem 'OSB 12mm'\n" in text


@pytest.mark.parametrize("title", ["PLACA OSB 12 MM", "PLACA OSB 9 MM"])  # todas batem / nenhuma bate
def test_alargada_sem_mistura_fica_como_antes(title):
    store = fake_store("Falsa", Found([], 0), Found([offer(title)], 1))
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), nofetch()))
    assert [o.title for o in sr.offers] == [title]
    assert sr.offers[0].broadened
    assert (sr.broadened_query, sr.hidden, sr.wide_only) == ("OSB", 0, 0)
    assert "ofertas escondidas" not in report(sr, "OSB 12mm")


def test_tudo_escondido_alargada_com_ofertas_que_batem():
    store = fake_store("Falsa", Found([], 5, hidden=5),
                       Found([offer("PLACA OSB 9 MM", "15"), offer("PLACA OSB 12 MM", "19")], 2))
    sr = asyncio.run(search_store(store, item("OSB 12mm", "un"), nofetch()))
    assert store.calls == ["OSB 12mm", "OSB"]  # D-14: uma só tentativa extra, nenhum pedido novo
    assert [o.title for o in sr.offers] == ["PLACA OSB 12 MM"]
    assert sr.wide_only == 1
    assert sr.detail == "1.ª pesquisa: 5 escondidas pelo filtro de título com 'OSB 12mm'"  # WR-16
    text = report(sr, "OSB 12mm")
    assert ("  Falsa: ok — 1.ª pesquisa: 5 escondidas pelo filtro de título com 'OSB 12mm'"
            " (pesquisa alargada: 'OSB')\n") in text
    assert "    +1 ofertas escondidas: título sem 'OSB 12mm'\n" in text

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
    (FakeSession(403), "bloqueada — API: HTTP 403"),
    (FakeSession(200, {"cf-mitigated": "challenge"}), "bloqueada"),
    (FakeSession(500), "erro — API: HTTP 500"),
    (FakeSession(200, body=b"<html><title>Just a moment...</title></html>"), "bloqueada — API: página de desafio"),
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
    sr = asyncio.run(search_store(fake_store("Lenta", slow), item(), nofetch()))
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
    sr = asyncio.run(search_store(store, item("cola", "kg"), nofetch()))
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
        return [r async for r in strata.search.run([item()], nofetch())]

    (result,) = asyncio.run(go())
    out = io.StringIO()
    print_item(result, out)
    text = out.getvalue()
    heads = ["Primeira: ok", "Segunda: erro — API: ValueError: campo em falta", "Terceira: sem resultados"]
    for h in heads:
        assert h in text, h
    assert text.index(heads[0]) < text.index(heads[1]) < text.index(heads[2])


# --- 01-06: verificar (STORE-07) ---

from strata.__main__ import main  # noqa: E402
from strata.fetch import StoreBlocked  # noqa: E402
from strata.stores import bricomarche, obramat, obras360  # noqa: E402

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
                   pavimento=None, brico_variations=None, o360_detail="obras360_product-details_osb-parent.json",
                   obramat_product="obramat_product-osb-18_ctx201_tiers.html"):
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
    fake.route("obramat.pt/search?q=osb", "obramat_search-osb_browser.html")
    fake.route("obramat.pt/produtos/", obramat_product)


def only(monkeypatch, store, term):
    monkeypatch.setattr(strata.search, "CANARIES", ((store, term),))


def check(fake):
    return asyncio.run(strata.search.verificar(fake))


def test_verificar_quatro_lojas_ok(fake):
    route_canaries(fake)
    rows = check(fake)
    assert [label for label, _, _ in rows] == [
        "Allmat (cimento)", "Allmat (pavimento)", "Bricomarché (cimento)", "Obras 360 (osb)", "Obramat (osb)"]
    assert all(ok for _, ok, _ in rows), rows


def test_verificar_comando_imprime_ok_e_sai_com_0(fake, capsys):
    route_canaries(fake)
    assert main(["verificar"], fetch=fake) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len([ln for ln in lines if ": OK — " in ln]) == 5
    assert "Allmat (cimento): OK — 3 ofertas, mais barata 4,22 € (método: API)" in lines
    assert "Obras 360 (osb): OK — 7 ofertas, mais barata 15,02 € (método: API)" in lines


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


def test_zero_ofertas_sem_escondidas_nao_diz_so_ok(fake):
    rows = load("allmat_products_search-cimento.json")
    for r in rows:
        r["prices"]["price"] = "0"
    fake.route(SEARCH + "cimento", rows)
    sr = asyncio.run(search_store(allmat, item(), fake))
    assert sr.status == "ok" and sr.offers == [] and sr.hidden == 0
    assert sr.detail == "0 ofertas mostradas de 3 resultados da loja"
    assert "3 produtos sem preço ignorados" in sr.notes
    assert heading(sr, "cimento") == "  Allmat: ok — 0 ofertas mostradas de 3 resultados da loja"


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


def test_verificar_obramat_sem_armazem(fake, monkeypatch):
    page = (FIXTURES / "obramat_product-osb-18_ctx201_tiers.html").read_text(encoding="utf-8").replace(
        '"cdl_user_context_main_store","value":"201"', '"cdl_user_context_main_store","value":"no cookie here"')
    route_canaries(fake, obramat_product=page.encode("utf-8"))
    only(monkeypatch, obramat, "osb")
    assert check(fake) == [("Obramat (osb)", False, "armazém por escolher no Chrome dedicado (escalões e stock por ler)")]


def test_verificar_ofertas_lidas_por_ia_falham(fake, monkeypatch):
    store = fake_store("Loja X", Found([offer(method="IA")], raw=1))
    only(monkeypatch, store, "osb")
    assert check(fake) == [("Loja X (osb)", False, "preços lidos por IA: os degraus estruturados falharam")]


@pytest.mark.parametrize("answer, expected", [
    (StoreBlocked("HTTP 403"), "estado bloqueada: API: HTTP 403"),
    ({"não": "é lista"}, "estado erro: API: ValueError: resposta da Allmat não é uma lista de produtos"),
])
def test_verificar_loja_bloqueada_ou_em_erro(fake, monkeypatch, answer, expected):
    fake.route("allmat.pt/?s=", b"<html></html>")  # o degrau JSON-LD também falha: sem links de produto
    route_canaries(fake, allmat_cimento=answer)
    only(monkeypatch, allmat, "cimento")
    ((label, ok, msg),) = check(fake)
    assert (label, ok) == ("Allmat (cimento)", False)
    assert msg.startswith(expected), msg


# --- WR-17: na alargada, o produto da linha escolhe os pais antes do corte K ---

def test_alargada_expande_o_pai_com_o_produto_da_linha(fake):
    def brico_parent(pid, name, cents):
        return {"id": pid, "name": name, "prices": {"price": cents, "price_range": None, "currency_minor_unit": 2}}

    baratos = [brico_parent(100 + i, f"Pavimento Betão Cinza modelo {i}", str(20 + i)) for i in range(12)]
    placa = brico_parent(200, "PAVIMENTO CERÂMICO SIENA HEKLA 60X120 1.44M2", "3455")  # o mais caro dos 13
    fake.route(BRICO + "pavimento+60x120", [])  # a loja não junta as duas palavras: dispara D-14
    fake.route(BRICO + "pavimento&", baratos + [placa])
    fake.route("parent=200&", [{**brico_variation(), "parent": 200,
                                "prices": {"price": "3455", "currency_minor_unit": 2}}])
    fake.route("type=variation", [{**brico_variation(), "prices": {"price": "50", "currency_minor_unit": 2}}])
    sr = asyncio.run(search_store(bricomarche, item("pavimento 60x120", "m²"), fake))
    variations = [c for c in fake.calls if "type=variation" in c]
    assert len(variations) == 10  # o corte K=10 não cresce
    assert len([c for c in variations if "parent=200&" in c]) == 1
    assert [(o.title, o.price) for o in sr.offers] == [("PAVIMENTO CERÂMICO SIENA HEKLA 60X120 1.44M2", Decimal("34.55"))]
    assert (sr.status, sr.broadened_query, sr.wide_only) == ("ok", "pavimento", 9)
    text = report(sr, "pavimento 60x120")
    assert "  Bricomarché: ok (pesquisa alargada: 'pavimento')\n" in text
    assert "    34,55 €  PAVIMENTO CERÂMICO SIENA HEKLA 60X120 1.44M2\n" in text
    assert "    +9 ofertas escondidas: título sem 'pavimento 60x120'\n" in text
    assert "    nota: +3 produtos não expandidos (limite de 10 por pesquisa)\n" in text
    assert "0,50 €" not in text
