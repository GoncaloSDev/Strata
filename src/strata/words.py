"""Palavras para comparar títulos (D-15) e a pesquisa alargada (D-14)."""

import re
import unicodedata
from itertools import combinations

from strata.text import norm

DIMS = re.compile(r"(?<=\d)x(?=\d)")  # "2440x590x18mm" -> "2440 590 18mm"
# Medida com várias partes, só números ("30x30", "30 x 30", "2440x590x18"); não lê "m8x40" (rosca e comprimento)
SIZE = re.compile(r"(?<![a-z\d.,])\d+(?:[.,]\d+)?(?:\s*x\s*\d+(?:[.,]\d+)?)+")
UNIT_WORDS = {"lt": "l", "lts": "l", "litro": "l", "litros": "l", "metro": "m", "metros": "m",
              "quilo": "kg", "quilos": "kg", "quilograma": "kg", "quilogramas": "kg", "grama": "g", "gramas": "g"}
SPELLED = re.compile(r"(\d)\s*(" + "|".join(UNIT_WORDS) + r")\b")  # "3 metros" -> "3m", "25 quilos" -> "25kg"
CLASS = re.compile(r"([a-z]{2,})(\d)\b")  # "osb3" -> "osb 3"; sem \b à esquerda: "2,5mm2" = "2,5 mm2"; "m2" não parte
JOIN = re.compile(r"(\d)\s+(mm|cm|m|m2|kg|g|l|ml)\b")  # "12 mm" -> "12mm"
TOKEN = re.compile(r"[a-z0-9]+(?:[.,][0-9]+)*")  # hífen e ponto final separam palavras
UNIT_TOKENS = {"mm", "cm", "m", "m2", "kg", "g", "l", "ml", "un", "unidade", "unidades", "x", *UNIT_WORDS}


def plain(s) -> str:
    """Como text.norm, mas mantém os espaços: "Placa 1,44 m²" -> "placa 1,44 m2"."""
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


STOP = {"de", "da", "do", "das", "dos", "para", "com", "em", "e", "a", "o", "x"}  # ligação; o "x" solto de "60 x 120"
# Ganha o primeiro sufixo que bate. O par -il -> -i não é plural: põe "perfil" igual a "perfis" (e "táxis" igual a "táxi").
# O -eis átono (geotêxteis -> geotêxtil) só se trata em "-xteis": depois de plain() não se distingue de painéis/listéis.
PLURAL = (("xteis", "xti"), ("oes", "ao"), ("aes", "ao"), ("eis", "el"), ("ais", "al"), ("ois", "ol"), ("uis", "ul"),
          ("is", "i"), ("il", "i"), ("s", ""))


def _stem(w: str) -> str:
    """Género e plural: branca/branco -> "branc", painéis -> "painel", portões -> "porta", colheres -> "colher",
    perfis/perfil -> "perfi", ferragens/ferragem -> "ferragen", jardins/jardim -> "jardin"."""
    if len(w) <= 2 or any(c.isdigit() for c in w):
        return w
    for suf, rep in PLURAL:
        if w.endswith(suf) and len(w) > len(suf):
            w = w[: -len(suf)] + rep
            break
    if w.endswith("m"):  # -m e -n finais são o mesmo som: jardim/jardins, coxim/coxins, plafon/plafons
        w = w[:-1] + "n"
    return w[:-1] if len(w) > 3 and w[-1] in "aoe" else w


def words(s) -> set[str]:
    """Sem acentos, minúsculas, medidas LxCxE partidas e também inteiras (cada troço seguido e cada par, com as
    partes ordenadas: "20x20x1,5" dá "20x20", "1,5x20" e "1,5x20x20"; "120x60" = "60x120"; "×" = "x"),
    "15 Lt" = "15l", "3 metros" = "3m", "OSB3" = "osb 3", "12 mm" = "12mm", sem palavras de ligação nem "x"
    solto, género e plural via _stem."""
    s = plain(s).replace("×", "x")  # o sinal de multiplicação não se decompõe em plain()
    parts = ["".join(m.split()).split("x") for m in SIZE.findall(s)]
    # Cada troço seguido e cada par, com as partes ordenadas: 60x120 = 120x60, 2500x1250x12 = 1250x2500x12
    sizes = {"x".join(sorted(p[i:j])) for p in parts for i in range(len(p)) for j in range(i + 2, len(p) + 1)}
    sizes |= {"x".join(sorted(c)) for p in parts for c in combinations(p, 2)}
    s = SPELLED.sub(lambda m: m[1] + UNIT_WORDS[m[2]], DIMS.sub(" ", s))
    s = JOIN.sub(r"\1\2", CLASS.sub(r"\1 \2", s))
    return sizes | {_stem(w) for w in TOKEN.findall(s) if w not in STOP}


def title_matches(query: str, title: str) -> bool:
    """Palavras inteiras, nunca substring: "aquecimento" não contém a palavra "cimento"."""
    return words(query) <= words(title)


def _digit(t: str) -> bool:
    return any(c.isdigit() for c in t)


def broadened(query: str) -> str | None:
    """Sem números, sem "x" (ou "×") solto e sem unidades a seguir a um número: "placa osb 12 mm" -> "placa osb",
    "tela 1 m x 25 m" -> "tela", mas "metro articulado 2m" -> "metro articulado"; None se nada sobra ou nada muda."""
    toks = query.split()
    keep = [t for prev, t in zip([""] + toks, toks)
            if not _digit(t) and norm(t) not in ("x", "×")
            and not (_digit(prev) and norm(t).rstrip(".") in UNIT_TOKENS)]
    return " ".join(keep) if keep and keep != toks else None
