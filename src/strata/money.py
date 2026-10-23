"""Dinheiro em Decimal: conversão de cêntimos, preço por unidade e formatação (arredonda só ao mostrar)."""

from decimal import ROUND_HALF_UP, Decimal

from strata.models import Offer


def from_minor(value, minor_unit) -> Decimal:
    """Cêntimos da Store API: ("422", 2) -> 4.22."""
    return Decimal(str(value)).scaleb(-int(minor_unit))


def per_unit(offer: Offer) -> Decimal | None:
    if offer.content is None or offer.content <= 0:
        return None
    return offer.price / offer.content


def content_from_title(title: str) -> tuple[Decimal, str] | None:
    return None


def in_unit(offer: Offer, unit: str) -> tuple[Decimal | None, str]:
    return None, ""


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
