"""Normalização de texto, unidades aceites e leitura de números escritos à portuguesa."""

import re
import unicodedata
from decimal import Decimal, InvalidOperation

from strata.models import Invalida, Item


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


NUM = re.compile(r"^\d+(?:[.,]\d+)?$")
GLUED = re.compile(r"^(\d+(?:[.,]\d+)?)([^\d\s]+)$")  # "30un", "10sacos"


def parse_line(line: str, row: int) -> tuple[Item | None, str | None]:
    """Linha colada, lida a partir do fim (D-11): "OSB 12mm 30 un" -> OSB 12mm / 30 / un."""
    toks, warns, unit, qty, qty_text = line.split(), [], None, None, None
    if toks and norm(toks[-1]) in UNITS:
        unit = UNITS[norm(toks.pop())]
    elif toks and (m := GLUED.match(toks[-1])) and norm(m[2]) in UNITS:
        toks.pop()
        qty_text, unit = m[1], UNITS[norm(m[2])]
    if qty_text is None and toks and NUM.match(toks[-1]):
        if len(toks) == 1:
            return None, "linha sem descrição"
        qty_text = toks.pop()
    if not toks:
        return None, "linha sem descrição"
    if qty_text is not None:
        qty = to_decimal(qty_text)
        if qty is None or qty <= 0:
            return None, f"quantidade não é um número positivo: {qty_text}"
    if unit is None:  # D-12: só no texto colado
        unit = "un"
        warns.append("unidade assumida: un")
    if qty is None:
        qty = Decimal(1)
        warns.append("quantidade assumida: 1")
    return Item(row=row, product=" ".join(toks), qty=qty, unit=unit, warnings=warns), None


def read_pasted(stream) -> tuple[list[Item], list[Invalida]]:
    """Linhas até à primeira linha vazia ou ao fim (D-10), numeradas a partir de 1."""
    items, invalid = [], []
    for row, line in enumerate(stream, start=1):
        if not line.strip():
            break
        item, err = parse_line(line, row)
        if err:
            invalid.append(Invalida(row, err))
        else:
            items.append(item)
    return items, invalid
