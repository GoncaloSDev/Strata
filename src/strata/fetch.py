"""Único cliente HTTP: ritmo por loja, classificação das falhas e gravação de fixtures (--record)."""

import asyncio
import hashlib
import json
import random
import re
import time
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from curl_cffi.requests.exceptions import RequestException, Timeout


class StoreBlocked(Exception):
    pass


class StoreCaptcha(StoreBlocked):
    """CAPTCHA: a loja fica 'abrir à mão' até ao fim da execução (D-07); a app nunca o resolve nem espera."""


class StoreError(Exception):
    pass


class StoreTimeout(Exception):
    pass


# host -> (pedidos em simultâneo, intervalo mínimo entre pedidos em s[, acaso a somar ao intervalo em s])
LIMITS = {
    "allmat.pt": (2, 0.5),
    "www.bricomarche.pt": (2, 0.5),
    "www.obras360.pt": (3, 0.3),
    "www.obramat.pt": (1, 3.0, 2.0),  # STORE-04: um pedido de cada vez, 3 a 5 s entre inícios (testado a 4–10 s)
}
CHALLENGE = ("just a moment", "challenge-platform", "captcha", "datadome")
DD = re.compile(r"var dd=\{([^}]*)\}")


def challenge_kind(body: str) -> str | None:
    """'captcha' (D-07: parar), 'interstitial' (verificação do dispositivo: escala para o browser) ou None."""
    m = DD.search(body)
    if not m:
        return None
    # A2: 'rt':'c' = CAPTCHA, 't':'bv' = bloqueio; 'rt':'i' = verificação do dispositivo (fontes de terceiros)
    return "captcha" if ("'rt':'c'" in m[1] or "'t':'bv'" in m[1]) else "interstitial"


def full_url(url: str, params: dict | None = None) -> str:
    return f"{url}?{urlencode(params, safe=',[]')}" if params else url


def fixture_name(full: str) -> str:
    """O mesmo nome no --record e no FakeFetcher dos testes."""
    return f"{urlsplit(full).hostname}_{hashlib.sha1(full.encode()).hexdigest()[:12]}"


class Host:
    """Semáforo + intervalo mínimo entre o início de dois pedidos ao mesmo host."""

    def __init__(self, n: int, gap: float, jitter: float = 0.0):
        self.sem = asyncio.Semaphore(n)
        self.gap = gap
        self.jitter = jitter
        self.next = 0.0
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        await self.sem.acquire()
        try:
            async with self.lock:
                await asyncio.sleep(max(0.0, self.next - time.monotonic()))
                self.next = time.monotonic() + self.gap + random.uniform(0, self.jitter)
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
        captcha = self.cache.setdefault("captcha_hosts", set())
        async with self.hosts[host]:
            if host in captcha:  # D-07: pedidos já em fila quando o CAPTCHA chegou nunca saem
                raise StoreCaptcha("CAPTCHA antes nesta execução")
            try:
                r = await self.s.get(full)
            except Timeout as e:
                raise StoreTimeout(str(e)) from e
            except RequestException as e:
                raise StoreError(f"ligação: {e}") from e
        if r.status_code in (403, 429, 503) or r.headers.get("cf-mitigated"):
            kind = challenge_kind(r.text[:4000])
            if kind == "captcha":
                captcha.add(host)
                raise StoreCaptcha(f"CAPTCHA da DataDome (HTTP {r.status_code})")
            if kind == "interstitial":
                raise StoreBlocked(f"HTTP {r.status_code} (verificação DataDome)")
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
