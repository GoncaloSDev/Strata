"""Orquestração: cada item contra cada loja, com o estado de cada loja sempre preenchido."""

import asyncio

from strata.fetch import StoreBlocked, StoreTimeout
from strata.models import Item, ItemResult, StoreResult
from strata.money import in_unit
from strata.stores import allmat, bricomarche
from strata.words import broadened

# Módulos com NAME e async search(query, fetch) -> Found, pela ordem de D-01.
STORES = (allmat, bricomarche)
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
