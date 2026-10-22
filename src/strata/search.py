"""Orquestração: cada item contra cada loja, com o estado de cada loja sempre preenchido."""

import asyncio

from strata.fetch import StoreBlocked, StoreTimeout
from strata.models import Item, ItemResult, StoreResult
from strata.stores import allmat

# Módulos com NAME e async search(query, fetch) -> Found, pela ordem de D-01.
STORES = (allmat,)
DEADLINE_S = 90


async def search_store(store, item: Item, fetch) -> StoreResult:
    try:
        async with asyncio.timeout(DEADLINE_S):
            found = await store.search(item.product, fetch)  # D-13: só o Produto, tal como escrito
    except TimeoutError:
        return StoreResult(store.NAME, "tempo esgotado", [], detail=f"mais de {DEADLINE_S} s")
    except StoreTimeout as e:
        return StoreResult(store.NAME, "tempo esgotado", [], detail=str(e))
    except StoreBlocked as e:
        return StoreResult(store.NAME, "bloqueada", [], detail=str(e))
    except Exception as e:  # o único sítio onde uma falha de loja vira estado; nunca some em silêncio
        return StoreResult(store.NAME, "erro", [], detail=f"{type(e).__name__}: {e}")
    status = "sem resultados" if found.raw == 0 else "ok"
    return StoreResult(store.NAME, status, found.offers, hidden=found.hidden, notes=found.notes)


async def run(items: list[Item], fetch):
    """Um item de cada vez, pela ordem da lista; as lojas desse item em paralelo."""
    for item in items:
        stores = await asyncio.gather(*(search_store(s, item, fetch) for s in STORES))
        yield ItemResult(item, list(stores))
