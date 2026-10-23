"""Orquestração: cada item contra cada loja, com o estado de cada loja sempre preenchido."""

import asyncio
from decimal import Decimal

from strata.fetch import StoreBlocked, StoreTimeout
from strata.models import Item, ItemResult, StoreResult
from strata.money import fmt_eur, in_unit
from strata.stores import allmat, bricomarche, obras360
from strata.words import broadened

# Módulos com NAME e async search(query, fetch) -> Found, pela ordem de D-01.
STORES = (allmat, bricomarche, obras360)
DEADLINE_S = 90


async def search_store(store, item: Item, fetch) -> StoreResult:
    b = None
    try:
        async with asyncio.timeout(DEADLINE_S):
            found = await store.search(item.product, fetch)  # D-13: só o Produto, tal como escrito
            if found.raw == 0 and (b := broadened(item.product)):  # D-14: uma só tentativa extra
                found = await store.search(b, fetch)
                for o in found.offers:
                    o.broadened = True
    except TimeoutError:
        return StoreResult(store.NAME, "tempo esgotado", [], detail=f"mais de {DEADLINE_S} s")
    except StoreTimeout as e:
        return StoreResult(store.NAME, "tempo esgotado", [], detail=str(e))
    except StoreBlocked as e:
        return StoreResult(store.NAME, "bloqueada", [], detail=str(e))
    except Exception as e:  # o único sítio onde uma falha de loja vira estado; nunca some em silêncio
        return StoreResult(store.NAME, "erro", [], detail=f"{type(e).__name__}: {e}")
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
    return StoreResult(store.NAME, "ok", [o for _, o in keyed], hidden=found.hidden, notes=found.notes,
                       broadened_query=b)


async def run(items: list[Item], fetch):
    """Um item de cada vez, pela ordem da lista; as lojas desse item em paralelo."""
    for item in items:
        stores = await asyncio.gather(*(search_store(s, item, fetch) for s in STORES))
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


async def verificar(fetch) -> list[tuple[str, bool, str]]:
    """(rótulo, ok, mensagem) por canário, um de cada vez, pelo mesmo search_store do dia a dia."""
    rows = []
    for store, term in CANARIES:
        sr = await search_store(store, Item(row=0, product=term, qty=Decimal(1), unit="un"), fetch)
        problem = _problem(store, term, sr)
        msg = problem or f"{len(sr.offers)} ofertas, mais barata {fmt_eur(sr.offers[0].price)}"
        rows.append((f"{store.NAME} ({term})", not problem, msg))
    return rows
