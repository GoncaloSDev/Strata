"""Único cliente HTTP: ritmo por loja, classificação das falhas e gravação de fixtures (--record)."""

import asyncio
import hashlib
import json
import time
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from curl_cffi.requests.exceptions import RequestException, Timeout


class StoreBlocked(Exception):
    pass


class StoreError(Exception):
    pass


class StoreTimeout(Exception):
    pass


# host -> (pedidos em simultâneo, intervalo mínimo entre pedidos em s)
LIMITS = {"allmat.pt": (2, 0.5), "www.bricomarche.pt": (2, 0.5), "www.obras360.pt": (3, 0.3)}
CHALLENGE = ("just a moment", "challenge-platform", "captcha", "datadome")


def full_url(url: str, params: dict | None = None) -> str:
    return f"{url}?{urlencode(params, safe=',[]')}" if params else url


def fixture_name(full: str) -> str:
    """O mesmo nome no --record e no FakeFetcher dos testes."""
    return f"{urlsplit(full).hostname}_{hashlib.sha1(full.encode()).hexdigest()[:12]}"


class Host:
    """Semáforo + intervalo mínimo entre o início de dois pedidos ao mesmo host."""

    def __init__(self, n: int, gap: float):
        self.sem = asyncio.Semaphore(n)
        self.gap = gap
        self.next = 0.0
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        await self.sem.acquire()
        try:
            async with self.lock:
                await asyncio.sleep(max(0.0, self.next - time.monotonic()))
                self.next = time.monotonic() + self.gap
        except BaseException:
            self.sem.release()  # cancelado à espera: não perder a vaga
            raise

    async def __aexit__(self, *exc):
        self.sem.release()


class Fetcher:
    def __init__(self, session, record: Path | None = None):
        self.s = session
        self.record = record
        self.hosts = {h: Host(*v) for h, v in LIMITS.items()}
        self.cache: dict = {}  # valores válidos durante uma execução (ex.: ID do widget da Obras 360)

    async def get(self, url: str, params: dict | None = None):
        host = urlsplit(url).hostname
        if host not in self.hosts:
            raise ValueError(f"host sem limites definidos: {host}")
        full = full_url(url, params)
        async with self.hosts[host]:
            try:
                r = await self.s.get(full)
            except Timeout as e:
                raise StoreTimeout(str(e)) from e
            except RequestException as e:
                raise StoreError(f"ligação: {e}") from e
        if r.status_code in (403, 429, 503) or r.headers.get("cf-mitigated"):
            raise StoreBlocked(f"HTTP {r.status_code}")
        if r.status_code >= 400:
            raise StoreError(f"HTTP {r.status_code}")
        if self.record:
            self.record.mkdir(parents=True, exist_ok=True)
            (self.record / fixture_name(full)).write_bytes(r.content)  # só o corpo, nunca cabeçalhos/cookies
        return r

    async def get_json(self, url: str, params: dict | None = None):
        r = await self.get(url, params)
        try:
            # nunca r.json(): pode usar orjson e perde o Decimal
            return json.loads(r.content, parse_float=Decimal)
        except ValueError as e:
            if any(m in r.text[:4000].lower() for m in CHALLENGE):
                raise StoreBlocked("página de desafio") from e
            raise StoreError("resposta não é JSON (layout mudou?)") from e

    async def get_html(self, url: str, params: dict | None = None) -> str:
        # Sem procurar marcadores: as páginas normais têm reCAPTCHA nos formulários.
        return (await self.get(url, params)).text
