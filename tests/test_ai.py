"""Degrau IA sem rede: texto da página, validação das ofertas e os motores com processos/clientes falsos."""

import asyncio
import io
import json
from decimal import Decimal
from types import SimpleNamespace

import pytest

import strata.ai
import strata.search
from conftest import FakeFetcher
from strata.__main__ import main
from strata.ai import MARK, MAX_CHARS, offers_from, page_text, parse_price
from strata.fetch import StoreBlocked, StoreError
from strata.stores import obramat
from test_e2e import blocks

OSB_URL = "https://www.obramat.pt/produtos/placa-osb-3-250x125x1-8cm-25134518.html"
# Página sem dataTms: o browser falha com "sem lista de resultados" e só a IA a lê.
OSB_PAGE = ('<html><body><script>var x = "28,50 €";</script>'
            '<a href="/produtos/placa-osb-3-250x125x1-8cm-25134518.html">PLACA OSB 3 250X125X1,8CM</a>'
            ' <span>28,50 €</span></body></html>')
OSB_ROW = {"title": "PLACA OSB 3 250X125X1,8CM", "price": "28,50 €", "url": OSB_URL}
PAGE_URL = obramat.search_page("placa osb")
REAL_ASK = strata.ai.ask  # antes do no_ai do conftest


def answer(*rows):
    calls = []

    async def ask(text):
        calls.append(text)
        return list(rows)

    ask.calls = calls
    return ask


def test_ponta_a_ponta_todos_os_degraus_falham_e_a_ia_le_a_pagina(fake, monkeypatch, capsys):
    monkeypatch.setattr(strata.search, "STORES", (obramat,))
    monkeypatch.setattr("sys.stdin", io.StringIO("placa osb 3 un\n\n"))
    monkeypatch.setattr(strata.ai, "ask", answer(OSB_ROW))
    fake.route("obramat.pt", StoreBlocked("HTTP 403"))
    browser = FakeFetcher().route("obramat.pt/search", OSB_PAGE.encode("utf-8"))
    browser.cache = fake.cache

    assert main(["pesquisar"], fetch=fake, browser=browser) == 0

    osb = blocks(capsys.readouterr().out)["placa osb"]
    assert "  Obramat: ok" in osb
    assert "28,50 €  PLACA OSB 3 250X125X1,8CM" in osb
    assert "método: IA" in osb and MARK in osb
    assert "loja: OBRAMAT Lisboa - Alfragide" in osb
    assert "nota: antes da IA: API: HTTP 403; JSON-LD: HTTP 403" in osb
    assert not browser.missing


@pytest.mark.parametrize("rows", [[], [dict(OSB_ROW, price="19,99 €")]])  # nada, ou preço que não está na página
def test_ponta_a_ponta_ia_sem_ofertas_validas_loja_falha_com_o_motivo(fake, monkeypatch, capsys, rows):
    monkeypatch.setattr(strata.search, "STORES", (obramat,))
    monkeypatch.setattr("sys.stdin", io.StringIO("placa osb 3 un\n\n"))
    monkeypatch.setattr(strata.ai, "ask", answer(*rows))
    fake.route("obramat.pt", StoreBlocked("HTTP 403"))
    browser = FakeFetcher().route("obramat.pt/search", OSB_PAGE.encode("utf-8"))
    browser.cache = fake.cache

    assert main(["pesquisar"], fetch=fake, browser=browser) == 0

    osb = blocks(capsys.readouterr().out)["placa osb"]
    line = ("  Obramat: bloqueada — API: HTTP 403; JSON-LD: HTTP 403; browser: página da Obramat sem lista "
            "de resultados (layout mudou?); IA: IA não leu nenhuma oferta válida na página")
    assert any(row.startswith(line) for row in osb.splitlines())
    if not rows:
        assert line in osb.splitlines()
    else:
        assert "1 ofertas da IA rejeitadas" in osb
    assert "sem resultados" not in osb
    assert not browser.missing


def test_page_text_links_absolutos_sem_script_e_cortado():
    text = page_text(OSB_PAGE, PAGE_URL)
    assert f"PLACA OSB 3 250X125X1,8CM <{OSB_URL}>" in text
    assert "var x" not in text
    assert text.endswith("28,50 €")
    assert len(page_text("<p>" + "a " * MAX_CHARS + "</p>", PAGE_URL)) == MAX_CHARS


@pytest.mark.parametrize("s, value", [
    ("28,50 €", Decimal("28.50")), ("1 299,60 €", Decimal("1299.60")), ("1\xa0299,60 €", Decimal("1299.60")),
    ("1.299,60", Decimal("1299.60")), ("28.50", Decimal("28.50")), ("1.299", Decimal(1299)), ("1299", Decimal(1299)),
    ("abc", None), ("0,00", None), ("", None),
])
def test_parse_price(s, value):
    assert parse_price(s) == value


def found_for(*rows, text=None):
    return offers_from(list(rows), text or page_text(OSB_PAGE, PAGE_URL), obramat, "placa osb", PAGE_URL)


def test_offers_from_aceita_link_relativo_e_marca_ia():
    found = found_for(dict(OSB_ROW, url="/produtos/placa-osb-3-250x125x1-8cm-25134518.html"))
    [o] = found.offers
    assert (o.url, o.price, o.method, o.note, o.vat_origin) == (OSB_URL, Decimal("28.50"), "IA", MARK, "regra da loja")
    assert MARK in o.vat_evidence and o.location == obramat.LOCATION
    assert found.raw == 1 and found.notes == []


@pytest.mark.parametrize("bad", [
    {"price": "19,99 €"},  # preço que não está na página
    {"url": "https://loja-falsa.pt/produtos/placa.html"},  # outro host
    {"url": "http://www.obramat.pt/produtos/placa.html"},  # sem https
    {"price": "0,00 €"},
])
def test_offers_from_rejeita_e_conta(bad):
    text = page_text(OSB_PAGE, PAGE_URL) + " 0,00 €"
    found = found_for(dict(OSB_ROW, **bad), OSB_ROW, text=text)
    assert len(found.offers) == 1
    assert found.notes == ["1 ofertas da IA rejeitadas (preço fora da página ou link fora da loja)"]


def test_offers_from_titulo_que_nao_bate_fica_escondido():
    found = offers_from([dict(OSB_ROW, title="TINTA BRANCA")], "TINTA BRANCA 28,50 €", obramat, "placa osb", PAGE_URL)
    assert found.offers == [] and (found.raw, found.hidden) == (1, 1)


class FakeProc:
    def __init__(self, out: bytes, err: bytes = b""):
        self.out, self.err, self.stdin = out, err, None
        self.killed = False

    async def communicate(self, data):
        self.stdin = data
        return self.out, self.err

    def kill(self):
        self.killed = True


def fake_exec(monkeypatch, out: dict | bytes):
    seen = {}

    async def create(*args, **kwargs):
        seen["args"], seen["kwargs"] = args, kwargs
        seen["proc"] = FakeProc(out if isinstance(out, bytes) else json.dumps(out).encode("utf-8"))
        return seen["proc"]

    monkeypatch.setattr(strata.ai.asyncio, "create_subprocess_exec", create)
    return seen


def test_ask_claude_sem_shell_sem_ferramentas_texto_pelo_stdin(monkeypatch):
    seen = fake_exec(monkeypatch, {"is_error": False, "result": "", "structured_output": {"offers": [OSB_ROW]}})
    text = "texto da página com 28,50 € e ação"
    assert asyncio.run(strata.ai._ask_claude("C:/x/claude.exe", text)) == [OSB_ROW]
    args = seen["args"]
    assert args[0] == "C:/x/claude.exe" and args[1] == "-p"
    assert "--json-schema" in args and json.loads(args[args.index("--json-schema") + 1]) == strata.ai.SCHEMA
    assert args[args.index("--tools") + 1] == ""
    assert "--no-session-persistence" in args and "--bare" not in args
    assert not any(text in a for a in args)
    assert seen["proc"].stdin == text.encode("utf-8")
    assert "shell" not in seen["kwargs"] and seen["kwargs"]["cwd"]


@pytest.mark.parametrize("out, reason", [
    ({"is_error": True, "result": "OAuth session expired"}, "IA (claude -p): OAuth session expired"),
    ({"is_error": False, "result": "texto livre"}, "IA (claude -p): texto livre"),
    ({"is_error": False}, "IA (claude -p): sem saída estruturada"),
    (b"isto nao e json", "IA (claude -p): saída não é JSON"),
])
def test_ask_claude_falha_com_o_motivo(monkeypatch, out, reason):
    fake_exec(monkeypatch, out)
    with pytest.raises(StoreError, match=reason.replace("(", r"\(").replace(")", r"\)")):
        asyncio.run(strata.ai._ask_claude("claude.exe", "x"))


def test_ask_claude_cancelado_mata_o_processo(monkeypatch):
    seen = fake_exec(monkeypatch, b"{}")

    async def never(self, data):
        await asyncio.sleep(10)

    monkeypatch.setattr(FakeProc, "communicate", never)
    with pytest.raises(TimeoutError):  # o prazo da loja cancela o degrau
        asyncio.run(asyncio.wait_for(strata.ai._ask_claude("claude.exe", "x"), 0.01))
    assert seen["proc"].killed


def test_ask_claude_recusa_cmd_sem_lancar_processo(monkeypatch):
    seen = fake_exec(monkeypatch, b"{}")
    with pytest.raises(StoreError, match=r"\.cmd/\.bat"):
        asyncio.run(strata.ai._ask_claude(r"C:\npm\claude.CMD", "x"))
    assert seen == {}


def test_ask_sem_motor_diz_porque(monkeypatch):
    monkeypatch.setattr(strata.ai, "ask", REAL_ASK)  # aqui testa-se o ask verdadeiro
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(strata.ai.shutil, "which", lambda name: None)
    with pytest.raises(StoreError, match="IA não configurada"):
        asyncio.run(strata.ai.ask("x"))


def test_degrau_ia_pede_a_pagina_com_idle_e_le_a_resposta(monkeypatch):
    seen = []

    async def get_html(url, params=None, idle=False):
        seen.append((url, idle))
        return OSB_PAGE

    ask = answer(OSB_ROW)
    monkeypatch.setattr(strata.ai, "ask", ask)
    found = asyncio.run(strata.ai.rung(obramat)("placa osb", SimpleNamespace(get_html=get_html)))
    assert seen == [(PAGE_URL, True)]
    assert [o.title for o in found.offers] == [OSB_ROW["title"]]
    assert ask.calls == [page_text(OSB_PAGE, PAGE_URL)]


# --- motor da API (ANTHROPIC_API_KEY) e regras D-09/D-10/D-11 ---


def test_ask_com_chave_usa_a_api_e_nao_o_claude(monkeypatch):
    monkeypatch.setattr(strata.ai, "ask", REAL_ASK)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "chave-de-teste")
    used = []

    async def api(text):
        used.append("api")
        return [OSB_ROW]

    async def claude(path, text):
        used.append("claude")
        return []

    monkeypatch.setattr(strata.ai, "_ask_api", api)
    monkeypatch.setattr(strata.ai, "_ask_claude", claude)
    monkeypatch.setattr(strata.ai.shutil, "which", lambda name: "C:/x/claude.exe")
    assert asyncio.run(strata.ai.ask("x")) == [OSB_ROW]
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    asyncio.run(strata.ai.ask("x"))
    assert used == ["api", "claude"]


class FakeMessages:
    def __init__(self, result):
        self.result, self.kwargs = result, None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


def fake_client(monkeypatch, result):
    import anthropic

    messages = FakeMessages(result)
    monkeypatch.setattr(anthropic, "AsyncAnthropic", lambda **kw: SimpleNamespace(messages=messages))
    return messages


def reply(text, stop_reason="end_turn"):
    return SimpleNamespace(stop_reason=stop_reason, content=[
        SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)])


def test_ask_api_saida_estruturada_com_o_esquema(monkeypatch):
    messages = fake_client(monkeypatch, reply(json.dumps({"offers": [OSB_ROW]})))
    assert asyncio.run(strata.ai._ask_api("texto da página")) == [OSB_ROW]
    kw = messages.kwargs
    assert kw["model"] == "claude-haiku-5-5" and kw["system"] == strata.ai.PROMPT
    assert kw["messages"] == [{"role": "user", "content": "texto da página"}]
    assert kw["output_config"]["format"] == {"type": "json_schema", "schema": strata.ai.SCHEMA}
    assert "tools" not in kw


def test_ask_api_erro_da_api_vira_motivo(monkeypatch):
    import anthropic
    import httpx2

    fake_client(monkeypatch, anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com")))
    with pytest.raises(StoreError, match=r"^IA \(API\): "):
        asyncio.run(strata.ai._ask_api("x"))


@pytest.mark.parametrize("result, reason", [
    (reply("não é json"), "resposta sem JSON"),
    (reply("", stop_reason="refusal"), "recusou"),
    (reply('{"offers": [', stop_reason="max_tokens"), "resposta cortada"),
])
def test_ask_api_resposta_inutil_vira_motivo(monkeypatch, result, reason):
    fake_client(monkeypatch, result)
    with pytest.raises(StoreError, match=reason):
        asyncio.run(strata.ai._ask_api("x"))


def test_offers_from_no_maximo_5():
    rows = [dict(OSB_ROW, title=f"PLACA OSB {n}", price=f"{n},00 €") for n in range(1, 8)]
    text = " ".join(f"PLACA OSB {n} {n},00 €" for n in range(1, 8))
    found = offers_from(rows, text, obramat, "placa osb", PAGE_URL)
    assert [o.title for o in found.offers] == [f"PLACA OSB {n}" for n in range(1, 6)]


def test_offers_from_obras360_soma_o_iva_da_pagina():
    from strata.money import add_vat
    from strata.stores import obras360

    page = obras360.search_page("placa osb")
    row = {"title": "PLACA OSB 3 12MM", "price": "12,21 €", "url": "https://www.obras360.pt/placa-osb-3-12mm"}
    [o] = offers_from([row], "PLACA OSB 3 12MM 12,21 € s/IVA", obras360, "placa osb", page).offers
    assert o.price == add_vat(Decimal("12.21"), 23)
    assert "+23%" in o.vat_evidence and MARK in o.vat_evidence
