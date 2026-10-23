"""Contrato de dados da fase: o que a folha, as lojas e o terminal trocam entre si."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

Status = Literal["ok", "sem resultados", "bloqueada", "erro", "tempo esgotado"]
VatOrigin = Literal["indicado pela loja", "regra da loja", "assumido"]


@dataclass
class Item:
    row: int  # número de linha do Excel (ou da linha colada)
    product: str
    qty: Decimal
    unit: str
    family: str | None = None
    size: str | None = None
    reference: str | None = None
    notes: str | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class Invalida:
    row: int
    reason: str


@dataclass
class Offer:
    store: str
    title: str
    url: str
    price: Decimal  # preço de UM artigo vendido (placa, caixa, saco), com IVA
    vat_origin: VatOrigin
    vat_evidence: str
    content: Decimal | None = None  # quanto da unidade-base traz um artigo (3.125 m², 25 kg, 1 un)
    content_unit: str | None = None
    stock: str = "desconhecido"
    location: str | None = None  # loja física, quando a loja tem várias
    tiers: list[tuple[Decimal, Decimal]] = field(default_factory=list)  # (a partir de N, -%)
    broadened: bool = False
    note: str = ""


@dataclass
class Found:
    offers: list[Offer]
    raw: int  # produtos que a loja devolveu antes do filtro de título; 0 = "sem resultados"
    hidden: int = 0
    notes: list[str] = field(default_factory=list)


@dataclass
class StoreResult:
    store: str
    status: Status
    offers: list[Offer]  # todas, já pela ordem final; o corte a 5 é do report
    detail: str = ""
    hidden: int = 0
    wide_only: int = 0  # ofertas da pesquisa alargada escondidas por não baterem a pergunta completa
    notes: list[str] = field(default_factory=list)
    broadened_query: str | None = None


@dataclass
class ItemResult:
    item: Item
    stores: list[StoreResult]
