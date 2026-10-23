"""Saída no terminal: uma secção por loja, o estado primeiro (D-01), no máximo 5 ofertas (D-02)."""

import unicodedata

from strata.models import Invalida, ItemResult, Offer
from strata.money import fmt_eur, fmt_qty, fmt_unit_price, per_unit

MAX_SHOWN = 5


def clean(s) -> str:
    """Tira caracteres de controlo (sequências ANSI vindas das lojas ou da folha)."""
    return "".join(c for c in str(s) if unicodedata.category(c)[0] != "C")


def _offer_lines(o: Offer) -> list[str]:
    pu = per_unit(o)
    unit_price = fmt_unit_price(pu, o.content_unit) if pu is not None and o.content_unit else "preço por unidade desconhecido"
    info = [f"IVA: {o.vat_origin} ({clean(o.vat_evidence)})", unit_price, clean(o.stock)]
    if o.location:
        info.append(f"loja: {clean(o.location)}")
    info += [f"escalões: −{fmt_qty(p)}% a partir de {fmt_qty(n)}" for n, p in o.tiers]
    if o.broadened:
        info.append("pesquisa alargada")
    if o.note:
        info.append(clean(o.note))
    return [
        f"    {fmt_eur(o.price)}  {clean(o.title)}",
        "      " + " · ".join(info),
        f"      {clean(o.url)}",
    ]


def print_invalid(invalids: list[Invalida], out) -> None:
    if not invalids:
        return
    print("Linhas com erro (não pesquisadas):", file=out)
    for inv in invalids:
        print(f"  linha {inv.row}: {clean(inv.reason)}", file=out)
    print(file=out)


def print_item(result: ItemResult, out) -> None:
    it = result.item
    print(f"Linha {it.row} — {clean(it.product)} ({fmt_qty(it.qty)} {it.unit})", file=out)
    for w in it.warnings:
        print(f"  aviso: {clean(w)}", file=out)
    for sr in result.stores:
        head = f"  {sr.store}: {sr.status}"
        if sr.detail:
            head += f" — {clean(sr.detail)}"
        if sr.broadened_query:
            head += f" (pesquisa alargada: '{clean(sr.broadened_query)}')"
        print(head, file=out)
        for o in sr.offers[:MAX_SHOWN]:
            for line in _offer_lines(o):
                print(line, file=out)
        if len(sr.offers) > MAX_SHOWN:
            print(f"    +{len(sr.offers) - MAX_SHOWN} ofertas não mostradas", file=out)
        if sr.hidden > 0:
            words = clean(sr.broadened_query or it.product)
            print(f"    +{sr.hidden} ofertas escondidas: título sem '{words}'", file=out)
        if sr.wide_only > 0:
            print(f"    +{sr.wide_only} ofertas escondidas: título sem '{clean(it.product)}'", file=out)
        for n in sr.notes:
            print(f"    nota: {clean(n)}", file=out)
    print(file=out)
