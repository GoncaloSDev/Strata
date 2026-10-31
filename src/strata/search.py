"""Orquestração: cada item contra cada loja, com o estado de cada loja sempre preenchido."""

import asyncio
from decimal import Decimal

from strata import jsonld
from strata.fetch import StoreBlocked, StoreCaptcha, StoreError, StoreTimeout
from strata.models import Found, Item, ItemResult, StoreResult
from strata.money import fmt_eur, in_unit
from strata.stores import allmat, bricomarche, obramat, obras360
from strata.words import broadened, title_matches

# Módulos com NAME e async search(query, fetch, rank=None) -> Found, pela ordem de D-01.
STORES = (allmat, bricomarche, obras360, obramat)
DEADLINE_S = 90


async def _attempt(search, fetch, item: Item) -> tuple[Found, str | None, int, int]:
    """Um degrau: 1.ª pesquisa, pesquisa alargada (D-14) e filtro da pergunta completa (G-01-5)."""
    b = None
    first_hidden = 0  # ofertas que a 1.ª pesquisa escondeu, quando a alargada a substitui
    wide_only = 0
    found = await search(item.product, fetch)  # D-13: só o Produto, tal como escrito
    all_hidden = found.hidden > 0 and not found.offers
    # D-14: uma só tentativa extra; também quando D-15 esconde tudo (WR-01)
    if (found.raw == 0 or all_hidden) and (b := broadened(item.product)):
        # WR-17: o produto da linha só ordena os pais antes do corte K; a pesquisa enviada é b
        wide = await search(b, fetch, rank=item.product)
        if found.raw > 0 and not wide.offers:  # fica a 1.ª, com a contagem e as palavras pedidas
            found.notes.append(f"também sem ofertas com '{b}'")
            b = None
        else:
            first_hidden = found.hidden if all_hidden else 0
            found = wide
            for o in found.offers:
                o.broadened = True
            # D-15 emendada (G-01-5): se alguma bate a pergunta completa, só essas; as outras ficam contadas
            full = [o for o in found.offers if title_matches(item.product, o.title)]
            if full:
                wide_only = len(found.offers) - len(full)
                found.offers = full
    return found, b, first_hidden, wide_only


def _rungs(store, fetch, browser) -> list[tuple[str, object, object]]:
    """Degraus (nome, search, transporte); a loja que o browser resolveu fica no browser (D-08)."""
    if store.NAME in fetch.cache.get("browser_only", set()):
        return [("browser", store.search, browser)]
    # D-13: principal → JSON-LD (pedido simples) → browser
    return [("API", store.search, fetch), ("JSON-LD", jsonld.rung(store), fetch), ("browser", store.search, browser)]


async def search_store(store, item: Item, fetch, browser=None) -> StoreResult:
    captcha = fetch.cache.setdefault("captcha", set())
    if store.NAME in captcha:  # D-07: depois de um CAPTCHA, nenhum pedido a esta loja até ao fim
        return StoreResult(store.NAME, "abrir à mão", [], detail="CAPTCHA antes nesta execução: nenhum pedido a esta loja",
                           link=store.search_page(item.product))
    tried: list[str] = []  # "degrau: motivo", pela ordem (D-16)
    kinds: set[str] = set()
    stage = None
    found = None
    try:
        async with asyncio.timeout(DEADLINE_S):  # D-15: um prazo para todos os degraus
            for stage, search, f in _rungs(store, fetch, browser):
                if f is None:
                    tried.append(f"{stage}: sem browser nesta execução")
                    kinds.add("erro")
                    continue
                if stage == "API" and store.NAME in fetch.cache.get("sem_principal", ()):  # D-17
                    tried.append("API: desativado com --sem-principal")
                    kinds.add("erro")
                    continue
                try:
                    found, b, first_hidden, wide_only = await _attempt(search, f, item)
                except StoreCaptcha as e:  # D-07: acaba a cadeia desta loja; nenhum degrau seguinte corre
                    captcha.add(store.NAME)
                    detail = f"CAPTCHA em {stage}: {e}"
                    if tried:
                        detail += f"; antes: {'; '.join(tried)}"
                    return StoreResult(store.NAME, "abrir à mão", [], detail=detail, link=store.search_page(item.product))
                except StoreBlocked as e:
                    tried.append(f"{stage}: {e}")
                    kinds.add("bloqueada")
                    continue
                except StoreTimeout as e:
                    tried.append(f"{stage}: {e}")
                    kinds.add("tempo esgotado")
                    continue
                except StoreError as e:  # mensagem já legível, sem o nome da classe
                    tried.append(f"{stage}: {e}")
                    kinds.add("erro")
                    continue
                except Exception as e:  # o único sítio onde uma falha de loja vira motivo; nunca some em silêncio
                    tried.append(f"{stage}: {type(e).__name__}: {e}")
                    kinds.add("erro")
                    continue
                for o in found.offers:
                    o.method = o.method or stage
                if stage == "browser":
                    fetch.cache.setdefault("browser_only", set()).add(store.NAME)  # D-08
                if tried:
                    found.notes.append(f"antes do {stage}: {'; '.join(tried)}")
                break
    except TimeoutError:
        detail = f"mais de {DEADLINE_S} s durante {stage}"
        if tried:
            detail += f"; antes: {'; '.join(tried)}"
        return StoreResult(store.NAME, "tempo esgotado", [], detail=detail)
    if found is None:  # nenhum degrau respondeu (D-16)
        status = next(k for k in ("bloqueada", "tempo esgotado", "erro") if k in kinds)
        return StoreResult(store.NAME, status, [], detail="; ".join(tried))
    if found.raw == 0:
        detail = f"também sem resultados com '{b}'" if b else ""
        return StoreResult(store.NAME, "sem resultados", [], detail=detail, notes=found.notes)
    keyed = []
    for o in found.offers:  # D-03: mais barato primeiro na unidade pedida; não convertíveis no fim
        key, reason = in_unit(o, item.unit)
        if reason:
            o.note = f"{o.note}; {reason}" if o.note else reason
        keyed.append((key, o))
    keyed.sort(key=lambda t: (t[0] is None, t[0] or 0))  # estável: empates pela ordem da loja
    detail = ""  # STORE-05/D-01: nunca "ok" sozinho com zero ofertas; o motivo fica nas notas
    if not found.offers:
        detail = (f"0 ofertas mostradas; {found.hidden} escondidas pelo filtro de título" if found.hidden
                  else f"0 ofertas mostradas de {found.raw} resultados da loja")
    elif first_hidden:
        detail = f"1.ª pesquisa: {first_hidden} escondidas pelo filtro de título com '{item.product}'"  # WR-16
    return StoreResult(store.NAME, "ok", [o for _, o in keyed], detail=detail, hidden=found.hidden,
                       wide_only=wide_only, notes=found.notes, broadened_query=b)


async def run(items: list[Item], fetch, browser=None):
    """Um item de cada vez, pela ordem da lista; as lojas desse item em paralelo."""
    for item in items:
        stores = await asyncio.gather(*(search_store(s, item, fetch, browser) for s in STORES))
        yield ItemResult(item, list(stores))


# Um termo de teste por loja (STORE-07); "pavimento" exercita as caixas M2 da Allmat.
CANARIES = ((allmat, "cimento"), (allmat, "pavimento"), (bricomarche, "cimento"), (obras360, "osb"))
VAT_ORIGINS = ("indicado pela loja", "regra da loja", "assumido")
CONTENT_UNITS = (None, "un", "m²", "m", "kg", "L")


def _problem(store, term: str, sr: StoreResult) -> str:
    """Primeiro motivo para não confiar no adaptador, ou "" se todas as ofertas devolvidas são válidas."""
    if sr.status != "ok":
        return f"estado {sr.status}: {sr.detail}"
    if not sr.offers:
        return "sem ofertas"
    for o in sr.offers:
        if o.price <= 0:
            return f"preço ≤ 0 em {o.title}"
        if o.vat_origin not in VAT_ORIGINS:
            return "origem do IVA inválida"
        if (o.content is not None and o.content <= 0) or o.content_unit not in CONTENT_UNITS:
            return f"unidade incoerente em {o.title}"
    if store is obras360 and any(o.vat_evidence != "tax_percentage=23" for o in sr.offers):
        return "IVA da loja não é 23%"
    if store is bricomarche and any(not o.location for o in sr.offers):
        return "sem nome de loja"
    if store is allmat:
        if bad := next((o for o in sr.offers if allmat.INCOHERENT in o.note), None):
            return f"caixa incoerente em {bad.title}"
        if term == "pavimento" and not any(o.content_unit == "m²" for o in sr.offers):
            return "nenhuma área de caixa lida"
    return ""


async def verificar(fetch, browser=None) -> list[tuple[str, bool, str]]:
    """(rótulo, ok, mensagem) por canário, um de cada vez, pelo mesmo search_store do dia a dia."""
    rows = []
    for store, term in CANARIES:
        sr = await search_store(store, Item(row=0, product=term, qty=Decimal(1), unit="un"), fetch, browser)
        problem = _problem(store, term, sr)
        msg = problem or f"{len(sr.offers)} ofertas, mais barata {fmt_eur(sr.offers[0].price)}"
        rows.append((f"{store.NAME} ({term})", not problem, msg))
    return rows
