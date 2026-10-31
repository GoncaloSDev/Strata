"""Testes sem rede: bloqueio de pedidos reais e um Fetcher falso que lê tests/fixtures/."""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from curl_cffi.requests import AsyncSession

import strata.ai
from strata.fetch import StoreError, fixture_name, full_url

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    async def blocked(*args, **kwargs):
        raise RuntimeError("rede bloqueada nos testes")

    monkeypatch.setattr(AsyncSession, "request", blocked)


@pytest.fixture(autouse=True)
def no_ai(monkeypatch):
    """Nenhum teste chama a API nem o claude: quem quer IA troca strata.ai.ask por uma resposta gravada."""
    async def off(text):
        raise StoreError("IA desligada nos testes")

    monkeypatch.setattr(strata.ai, "ask", off)


class FakeFetcher:
    """Mesma interface do Fetcher (get_json, get_html, cache), sem rede.

    route(substring, alvo): ganha a primeira rota cujo substring está no URL completo.
    alvo = nome de ficheiro em tests/fixtures/ (str), corpo da resposta (bytes),
    uma Exception (é lançada) ou outro objeto (devolvido tal como está pelo get_json).
    Sem rota: tests/fixtures/<fixture_name(url)>, o mesmo nome que o --record grava.
    """

    def __init__(self):
        self.routes: list[tuple[str, object]] = []
        self.calls: list[str] = []
        self.missing: list[str] = []
        self.cache: dict = {}

    def route(self, substring: str, target) -> "FakeFetcher":
        self.routes.append((substring, target))
        return self

    def _body(self, url, params):
        full = full_url(url, params)
        self.calls.append(full)
        target = next((t for s, t in self.routes if s in full), None)
        if target is None:
            path = FIXTURES / fixture_name(full)
            if not path.exists():
                self.missing.append(full)
                raise StoreError(f"fixture em falta: {full}")
            return path.read_bytes()
        if isinstance(target, BaseException) or (isinstance(target, type) and issubclass(target, BaseException)):
            raise target
        if isinstance(target, str):
            return (FIXTURES / target).read_bytes()
        return target  # bytes ou objeto Python

    async def get_json(self, url, params=None):
        body = self._body(url, params)
        if isinstance(body, bytes):
            return json.loads(body, parse_float=Decimal)
        return body

    async def get_html(self, url, params=None, idle=False) -> str:
        body = self._body(url, params)
        return body.decode("utf-8") if isinstance(body, bytes) else body


@pytest.fixture
def fake():
    f = FakeFetcher()
    yield f
    assert not f.missing, f"fixtures em falta (gravar com --record tests/fixtures): {f.missing}"
