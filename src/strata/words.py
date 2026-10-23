"""Palavras para comparar títulos (D-15) e a pesquisa alargada (D-14)."""

import re
import unicodedata

from strata.text import norm

JOIN = re.compile(r"(\d)\s+(mm|cm|m|m2|kg|g|l|ml)\b")  # "12 mm" -> "12mm"
TOKEN = re.compile(r"[a-z0-9]+(?:[.,][0-9]+)*")  # hífen e ponto final separam palavras
UNIT_TOKENS = {"mm", "cm", "m", "m2", "kg", "g", "l", "lt", "ml", "un", "x"}


def plain(s) -> str:
    """Como text.norm, mas mantém os espaços: "Placa 1,44 m²" -> "placa 1,44 m2"."""
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


STOP = {"de", "da", "do", "das", "dos", "para", "com", "em", "e", "a", "o"}  # palavras de ligação


def _stem(w: str) -> str:
    """Género e plural: branca/branco -> "branc", painéis -> "painel", portões -> "porta", colheres -> "colher"."""
    if len(w) <= 3 or any(c.isdigit() for c in w):
        return w
    if w.endswith("oes"):
        w = w[:-3] + "ao"
    elif w.endswith("eis"):
        w = w[:-3] + "el"
    elif w.endswith("s"):
        w = w[:-1]
    return w[:-1] if len(w) > 3 and w[-1] in "aoe" else w


def words(s) -> set[str]:
    """Sem acentos, minúsculas, "12 mm" = "12mm", sem palavras de ligação, género e plural via _stem."""
    s = JOIN.sub(r"\1\2", plain(s))
    return {_stem(w) for w in TOKEN.findall(s) if w not in STOP}


def title_matches(query: str, title: str) -> bool:
    """Palavras inteiras, nunca substring: "aquecimento" não contém a palavra "cimento"."""
    return words(query) <= words(title)


def broadened(query: str) -> str | None:
    """Sem números nem unidades soltas: "placa osb 12 mm" -> "placa osb"; None se nada sobra ou nada muda."""
    toks = query.split()
    keep = [t for t in toks if not any(c.isdigit() for c in t) and norm(t) not in UNIT_TOKENS]
    return " ".join(keep) if keep and keep != toks else None
