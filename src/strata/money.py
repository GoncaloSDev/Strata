"""Dinheiro em Decimal: conversão de cêntimos, preço por unidade e formatação (arredonda só ao mostrar)."""

import re
from decimal import ROUND_HALF_UP, Decimal

from strata.models import Offer
from strata.words import plain


def from_minor(value, minor_unit) -> Decimal:
    """Cêntimos da Store API: ("422", 2) -> 4.22."""
    return Decimal(str(value)).scaleb(-int(minor_unit))


def per_unit(offer: Offer) -> Decimal | None:
    if offer.content is None or offer.content <= 0:
        return None
    return offer.price / offer.content


# Primeiro número (vírgula ou ponto) seguido de unidade de conteúdo; medidas e espessuras ficam para a Phase 3.
CONTENT = re.compile(r"(?<![\d.,])(\d+(?:[.,]\d+)?)\s*(kg|g|lt|l|ml|m2)\b")
CONTENT_UNITS = {"kg": (0, "kg"), "g": (-3, "kg"), "l": (0, "L"), "lt": (0, "L"), "ml": (-3, "L"), "m2": (0, "m²")}


def content_from_title(title: str) -> tuple[Decimal, str] | None:
    """"SACO 25 KG" -> (25, "kg"); "600ML" -> (0.6, "L"); "1,44 m2" -> (1.44, "m²")."""
    m = CONTENT.search(plain(title))
    if not m:
        return None
    exp, unit = CONTENT_UNITS[m[2]]
    return Decimal(m[1].replace(",", ".")).scaleb(exp), unit


def in_unit(offer: Offer, unit: str) -> tuple[Decimal | None, str]:
    """Preço na unidade pedida pela linha (chave de ordenação D-03), ou None e o motivo."""
    if unit in ("un", "saco"):  # A5: um artigo vendido
        return offer.price, ""
    if offer.content_unit == unit and offer.content and offer.content > 0:
        return offer.price / offer.content, ""
    if offer.content_unit is None or offer.content_unit == unit:
        return None, f"não convertível para {unit}: conteúdo da embalagem desconhecido"
    return None, f"não convertível para {unit}: vendido em {offer.content_unit}"


def _fmt(d: Decimal, places: int) -> str:
    q = Decimal(1).scaleb(-places)
    return f"{d.quantize(q, rounding=ROUND_HALF_UP):f}".replace(".", ",")


def fmt_eur(d: Decimal) -> str:
    return f"{_fmt(d, 2)} €"


def fmt_unit_price(d: Decimal, unit: str) -> str:
    return f"{_fmt(d, 4 if d < 1 else 2)} €/{unit}"


def fmt_qty(d: Decimal) -> str:
    """10 -> "10", 2.50 -> "2,5"."""
    s = f"{d.normalize():f}"
    return s.replace(".", ",")


def add_vat(net, rate) -> Decimal:
    """Preço sem IVA + taxa em %: 12.214688 a 23 -> 15.02406624 (sem arredondar)."""
    return Decimal(net) * (1 + Decimal(rate) / 100)
