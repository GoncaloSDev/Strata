"""Degrau browser: o Chrome dedicado do Claude por CDP, com a interface do Fetcher (get_json, get_html, cache)."""

import asyncio
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit

from strata.fetch import CHALLENGE, StoreBlocked, StoreError, StoreTimeout, fixture_name, full_url

CDP = "http://127.0.0.1:9222"
# shortcut: caminho fixo do .claude/claude-chrome.cmd; ler o caminho do registo se o Chrome estiver noutro sítio
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = Path.home() / ".claude-chrome"
START_S = 10
NAV_MS = 30_000


class BrowserFetcher:
    def __init__(self, base):
        self.hosts = base.hosts  # o mesmo ritmo por host do pedido simples (T-02-10)
        self.cache = base.cache  # o mesmo estado da execução (D-08)
        self.record = base.record
        self._pw = None
        self._browser = None
        self._ctx = None
        self._opened = False  # fui eu que abri o Chrome dedicado (D-06)
        self._lock = asyncio.Lock()

    async def _context(self):
        async with self._lock:
            if self._ctx is not None:
                return self._ctx
            from playwright.async_api import Error, async_playwright

            if self._pw is None:
                self._pw = await async_playwright().start()
            try:
                self._browser = await self._pw.chromium.connect_over_cdp(CDP, timeout=2000)
            except Error:
                if not Path(CHROME).exists():
                    raise StoreError(f"Chrome não encontrado em {CHROME}")
                # Os argumentos do .claude/claude-chrome.cmd, em lista e sem shell (T-02-07).
                subprocess.Popen([CHROME, f"--user-data-dir={PROFILE}", "--remote-debugging-port=9222",
                                  "--no-first-run", "--no-default-browser-check"])
                self._opened = True
                for _ in range(START_S * 2):
                    await asyncio.sleep(0.5)
                    try:
                        self._browser = await self._pw.chromium.connect_over_cdp(CDP, timeout=2000)
                        break
                    except Error:
                        pass
                else:
                    raise StoreError(f"Chrome dedicado não respondeu na porta 9222 em {START_S} s")
            self._ctx = self._browser.contexts[0]  # o contexto do perfil dedicado, com os cookies (D-05)
            return self._ctx

    async def _open(self, url: str, params, read):
        from playwright.async_api import Error
        from playwright.async_api import TimeoutError as PwTimeout

        host = urlsplit(url).hostname
        if host not in self.hosts:
            raise ValueError(f"host sem limites definidos: {host}")
        full = full_url(url, params)
        ctx = await self._context()
        async with self.hosts[host]:
            page = await ctx.new_page()  # um separador por pedido: navegações em paralelo nunca o partilham
            try:
                resp = await page.goto(full, wait_until="load", timeout=NAV_MS)
                if resp is None:
                    raise StoreError("navegação sem resposta")
                if resp.status in (403, 429, 503):
                    raise StoreBlocked(f"HTTP {resp.status} (browser)")
                if resp.status >= 400:
                    raise StoreError(f"HTTP {resp.status} (browser)")
                body = await read(page, resp)
            except PwTimeout as e:
                raise StoreTimeout(str(e)) from e
            except Error as e:
                raise StoreError(f"browser: {e}") from e
            finally:
                await page.close()
        if self.record:
            self.record.mkdir(parents=True, exist_ok=True)
            data = body.encode("utf-8") if isinstance(body, str) else body
            (self.record / fixture_name(full)).write_bytes(data)  # só o corpo, nunca cabeçalhos/cookies
        return body

    async def get_json(self, url: str, params: dict | None = None):
        async def read(page, resp):
            return await resp.body()

        body = await self._open(url, params, read)
        try:
            return json.loads(body, parse_float=Decimal)
        except ValueError as e:
            if any(m in body[:4000].decode("utf-8", "replace").lower() for m in CHALLENGE):
                raise StoreBlocked("página de desafio") from e
            raise StoreError("resposta não é JSON (layout mudou?)") from e

    async def get_html(self, url: str, params: dict | None = None) -> str:
        async def read(page, resp):
            return await page.content()

        return await self._open(url, params, read)

    async def close(self) -> None:
        """D-06: fecha o Chrome que a app abriu; o que já estava aberto só é desligado."""
        if self._pw is None:
            return
        try:
            if self._browser is not None:
                if self._opened:
                    cdp = await self._browser.new_browser_cdp_session()
                    await cdp.send("Browser.close")
                else:
                    await self._browser.close()  # só desliga; as páginas da app já fecharam
        except Exception as e:
            print(f"aviso: não consegui fechar o Chrome dedicado: {e}", file=sys.stderr)
        finally:
            await self._pw.stop()
