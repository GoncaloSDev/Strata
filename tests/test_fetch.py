"""Desafios do DataDome no pedido simples e no browser, sem rede (D-05, D-07, Pitfall 2)."""

import asyncio
from types import SimpleNamespace

import pytest
from playwright.async_api import Error

import strata.fetch
from conftest import FIXTURES
from strata.browser import past_challenge
from strata.fetch import Fetcher, StoreBlocked, StoreCaptcha, challenge_kind

DD_403 = (FIXTURES / "obramat_curl-403-datadome.html").read_text(encoding="utf-8")  # 'rt':'i'
DD_CAPTCHA = DD_403.replace("'rt':'i'", "'rt':'c'")
DD_BV = DD_403.replace("'rt':'i'", "'rt':'i','t':'bv'")
NORMAL = "<html><body><ol id='guidance-product-list'></ol></body></html>"
URL = "https://www.obramat.pt/search"


class FakeSession:
    def __init__(self, status=200, body=b"[]"):
        self.r = SimpleNamespace(status_code=status, headers={}, content=body, text=body.decode("utf-8"))
        self.calls = 0

    async def get(self, url):
        self.calls += 1
        return self.r


@pytest.mark.parametrize("body, kind", [
    (DD_403, "interstitial"),
    (DD_CAPTCHA, "captcha"),
    (DD_BV, "captcha"),
    (NORMAL, None),
])
def test_challenge_kind(body, kind):
    assert challenge_kind(body) == kind


def test_verificacao_do_dispositivo_e_bloqueio_e_nao_captcha():
    with pytest.raises(StoreBlocked, match=r"HTTP 403 \(verificação DataDome\)") as e:
        asyncio.run(Fetcher(FakeSession(403, DD_403.encode())).get(URL))
    assert not isinstance(e.value, StoreCaptcha)


def test_captcha_no_pedido_simples_e_depois_nenhum_pedido(monkeypatch):
    monkeypatch.setitem(strata.fetch.LIMITS, "www.obramat.pt", (1, 0.0, 0.0))  # sem os 3–5 s da loja
    assert issubclass(StoreCaptcha, StoreBlocked)
    session = FakeSession(403, DD_CAPTCHA.encode())
    f = Fetcher(session)
    with pytest.raises(StoreCaptcha, match=r"CAPTCHA da DataDome \(HTTP 403\)"):
        asyncio.run(f.get(URL, {"q": "osb"}))
    with pytest.raises(StoreCaptcha, match="antes nesta execução"):
        asyncio.run(f.get(URL, {"q": "cimento"}))
    assert session.calls == 1


def reader(*pages):
    """Leituras sucessivas da página; uma Exception é lançada (página a recarregar)."""
    seq = list(pages)

    async def read():
        p = seq.pop(0) if len(seq) > 1 else seq[0]
        if isinstance(p, BaseException):
            raise p
        return p

    return read


def check(read, **kw):
    return asyncio.run(past_challenge(read, step=0.001, **kw))


def test_past_challenge_espera_a_verificacao_passar():
    assert check(reader(DD_403, DD_403, NORMAL)) == (NORMAL, True)


def test_past_challenge_pagina_normal():
    assert check(reader(NORMAL)) == (NORMAL, False)


def test_past_challenge_captcha_para():
    with pytest.raises(StoreCaptcha):
        check(reader(DD_403, DD_CAPTCHA))


def test_past_challenge_verificacao_que_nao_passa():
    with pytest.raises(StoreBlocked, match="não passou em 0.05 s") as e:
        check(reader(DD_403), wait_s=0.05)
    assert not isinstance(e.value, StoreCaptcha)


def test_past_challenge_pagina_a_recarregar():
    assert check(reader(DD_403, Error("Execution context was destroyed"), NORMAL)) == (NORMAL, True)
