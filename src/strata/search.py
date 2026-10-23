"""Orquestração: cada item contra cada loja, com o estado de cada loja sempre preenchido."""

import asyncio
from decimal import Decimal

from strata.fetch import StoreBlocked, StoreTimeout
from strata.models import Item, ItemResult, StoreResult
from strata.money import fmt_eur, in_unit
from strata.stores import allmat, bricomarche, obras360
from strata.words import broadened, title_matches

# Módulos com NAME e async search(query, fetch, rank=None) -> Found, pela ordem de D-01.
STORES = (allmat, bricomarche, obras360)
DEADLINE_S = 90


async def search_store(store, item: Item, fetch) -> StoreResult:
    b = None
    first_hidden = 0  # ofertas que a 1.ª pesquisa escondeu, quando a alargada a substitui
    wide_only = 0
    try:
        async with asyncio.timeout(DEADLINE_S):
            found = await store.search(item.product, fetch)  # D-13: só o Produto, tal como escrito
            all_hidden = found.hidden > 0 and not found.offers
            # D-14: uma só tentativa extra; também quando D-15 esconde tudo (WR-01)
            if (found.raw == 0 or all_hidden) and (b := broadened(item.product)):
                # WR-17: o produto da linha só ordena os pais antes do corte K; a pesquisa enviada é b
                wide = await store.search(b, fetch, rank=item.product)
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
    detail = ""  # STORE-05/D-01: nunca "ok" sozinho com zero ofertas; o motivo fica nas notas
    if not found.offers:
        detail = (f"0 ofertas mostradas; {found.hidden} escondidas pelo filtro de título" if found.hidden
                  else f"0 ofertas mostradas de {found.raw} resultados da loja")
    elif first_hidden:
        detail = f"1.ª pesquisa: {first_hidden} escondidas pelo filtro de título com '{item.product}'"  # WR-16
    return StoreResult(store.NAME, "ok", [o for _, o in keyed], detail=detail, hidden=found.hidden,
                       wide_only=wide_only, notes=found.notes, broadened_query=b)


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
