"""Normalização de texto, unidades aceites e leitura de números escritos à portuguesa."""

import unicodedata
from decimal import Decimal, InvalidOperation


def norm(s) -> str:
    """Sem acentos, minúsculas e sem espaços: "Família" -> "familia", "m²" -> "m2"."""
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).casefold().replace(" ", "")


# Chaves já passadas por norm(); valor = unidade canónica (D-07).
UNITS = {
    "un": "un", "unid": "un", "uni": "un", "unidade": "un", "unidades": "un",
    "m2": "m²",
    "m": "m",
    "kg": "kg",
    "l": "L", "lt": "L", "litro": "L", "litros": "L",
    "saco": "saco", "sacos": "saco",
}


def to_decimal(v) -> Decimal | None:
    """int, float, Decimal ou texto com vírgula ou ponto ("2,5"); None se não for número."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float, Decimal)):
        s = str(v)
    else:
        s = str(v).strip().replace(" ", "").replace(",", ".")
    if not s:
        return None
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None
    return d if d.is_finite() else None  # "nan", "inf" não são quantidades
