# Phase 1: Folha Excel e preços da Allmat, Bricomarché e Obras 360 - Research

**Researched:** 2026-10-22
**Domain:** CLI Python assíncrona: leitura/escrita `.xlsx` (openpyxl), três adaptadores de loja por API JSON (WooCommerce Store API ×2, Beevo), dinheiro em `Decimal` com IVA 23% e preço unitário
**Confidence:** HIGH nas lojas (todas as chamadas abaixo foram feitas hoje com `curl_cffi` `impersonate="chrome"` e as respostas lidas), HIGH no openpyxl/curl_cffi (testados no venv de sondagem), MEDIUM em escolhas de desenho (limites K, ritmo)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Saída no terminal
- **D-01:** Cada item aparece com uma secção por loja (Allmat, Bricomarché, depois Obras 360). Cada secção começa pelo estado da loja (ok / sem resultados / bloqueada / erro / tempo esgotado), sempre visível, também quando não há ofertas.
- **D-02:** Até 5 ofertas por loja e por item. Quando há mais, uma linha diz quantas ficaram de fora (ex.: "+14 ofertas não mostradas"). Nada desaparece em silêncio.
- **D-03:** Ordem: mais barato primeiro, pelo preço em € na unidade pedida pela linha (ex.: €/m² se a linha pede m²). As ofertas que não dá para converter para a unidade pedida (ex.: vendidas à unidade, área desconhecida) vão para o fim, com o motivo escrito.
- **D-04:** Só terminal. Esta fase não grava CSV nem JSON de resultados para o utilizador. A folha preenchida chega na Phase 4 e o Excel detalhado na Phase 5.

#### Modelo Excel
- **D-05:** Um comando grava `modelo.xlsx` na pasta atual (ex.: `uv run python -m strata modelo`). Se o ficheiro já existir, não escreve por cima: para, com uma mensagem a dizê-lo.
- **D-06:** O modelo traz os cabeçalhos (Produto, Família, Tamanho, Unidade, Qty, Referência, Notas) e 2–3 linhas de exemplo (ex.: "OSB 12 mm" / 30 / un; "cimento" / 10 / saco).
- **D-07:** No modelo, a coluna Unidade tem uma lista pendente (validação de dados) com un, m², m, kg, L, saco. Ao ler, também aceita sinónimos comuns (m2, unid, uni, lt, l, sacos), sem contar maiúsculas nem espaços. Um valor que não bate com nenhum torna a linha inválida: "unidade desconhecida: X".
- **D-08:** As colunas encontram-se pelo nome do cabeçalho, sem contar maiúsculas nem acentos. A ordem é livre e as colunas extra (ex.: Obra, Fornecedor) são ignoradas na leitura. — **Reversibility:** costly — a Phase 4 escreve na folha do utilizador a contar com este mapeamento por nome; mudar para posição fixa obriga a rever a leitura e a escrita.
- **D-09:** A folha lida é a primeira que tem Produto, Unidade e Qty nas primeiras 10 linhas, e a linha onde estão passa a ser a dos cabeçalhos. Se nenhuma folha os tiver, o erro diz quais colunas faltam. O número de linha nas mensagens é o número de linha do Excel (o que o utilizador vê à esquerda).

#### Texto colado
- **D-10:** Sem caminho de ficheiro, o comando lê do terminal: o utilizador cola as linhas e termina com uma linha vazia. Não há entrada por `.txt`.
- **D-11:** A quantidade e a unidade ficam no fim da linha ("OSB 12mm 30 un", "cimento 10 saco"). Números no meio (como o "12mm") ficam na descrição. Aceita os mesmos sinónimos de unidade de D-07.
- **D-12:** Uma linha sem unidade assume "un" e uma linha sem quantidade assume 1. Nos dois casos, a pesquisa corre na mesma e aparece um aviso (ex.: "unidade assumida: un"). Isto é só para o texto colado: na folha Excel, Unidade ou Qty em falta continuam a tornar a linha inválida (critério 1 do ROADMAP).

#### O que se pesquisa
- **D-13:** Só o Produto vai para a pesquisa da loja, tal como está escrito. Família, Tamanho e Referência são lidos e guardados no item, mas só entram na pesquisa e na classificação na Phase 3 (LIST-06). Notas não é usada.
- **D-14:** Se uma loja devolver zero resultados, a app faz uma segunda pesquisa alargada, sem medidas nem números (ex.: "OSB 12mm" → "OSB"), e marca essas ofertas como "pesquisa alargada". Se continuar a zero, o estado fica "sem resultados". É uma só tentativa extra por loja e por item (na Bricomarché custa cerca de 12 s a mais).
- **D-15:** As ofertas cujo título não contém as palavras da pesquisa são escondidas, mas contadas numa linha visível (ex.: "+12 ofertas escondidas: título sem 'osb'"). Serve para cortar resultados que só batem na descrição, como parafusos "para OSB". Na pesquisa alargada, compara com as palavras dessa pesquisa.

#### Obras 360 (acrescentada à fase pelo utilizador em 2026-10-22)
- **D-16:** A Obras 360 (`obras360.pt`, nunca `obra360.pt`) entra nesta fase (STORE-03, antes na Phase 2). Cada variante do produto é uma oferta separada: a linha pai da pesquisa (ex.: "Placa OSB 9-30MM") mostra só o preço da variante mais barata, por isso o adaptador expande as variantes pelo `product-details` antes de mostrar qualquer preço. O preço da loja vem sem IVA e é convertido para IVA 23% com a evidência da loja (`tax_percentage`). Os escalões por quantidade (`DiscountByQuantity`) são lidos e mostrados na oferta; aplicá-los ao custo total fica para a Phase 4 (PRICE-04).

### Claude's Discretion
- Verificação das lojas (STORE-07): nome do comando, produtos de teste por loja (ex.: "cimento" na Allmat, que não vende OSB) e formato do relatório. Tem de dizer, por adaptador, se ainda devolve preços válidos (preço acima de zero, IVA e unidade coerentes).
- Ritmo, timeouts, paralelismo e paginação por loja (ex.: leitura de 30 s na Bricomarché, que demora cerca de 12 s por página). Confirmar se `orderby=price` funciona com `type=variation`.
- Nomes exatos dos comandos e das opções, e o desenho da tabela no terminal (colunas, largura, cores).
- Normalização ao comparar palavras para D-15: acentos, maiúsculas, "12 mm" = "12mm", plural simples. Leitura de números com vírgula decimal ("2,5 m²").
- Allmat sem área da caixa no HTML do produto: mostrar a oferta com o preço por caixa e o €/m² como desconhecido, no fim da lista (D-03). Nunca a esconder.
- Gravar respostas das lojas como fixtures para os testes (ex.: uma opção `--record`). É ferramenta de desenvolvimento, não exportação para o utilizador.

### Deferred Ideas (OUT OF SCOPE)
Nenhuma: a discussão ficou dentro do âmbito da fase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LIST-01 | Lista colada multilinha com descrição, quantidade e unidade | §Pattern 6 (parser de linha a partir do fim), §Pitfall 8 (stdin cp1252 no Windows) |
| LIST-02 | Pesquisa em texto livre sem categoria | Os três endpoints aceitam texto livre; todos fazem AND das palavras (§Pitfall 3); D-14 alargada |
| LIST-04 | Modelo Excel de formato fixo | §Code Examples "Modelo" (openpyxl + `DataValidation`, `open(..., "xb")` para não sobrescrever) |
| LIST-05 | Ler a folha; linhas inválidas com nº de linha e motivo | §Code Examples "Folha" (cabeçalho nas 10 primeiras linhas, NFKD, linha Excel) |
| STORE-01 | Bricomarché: mais barato entre lojas físicas + nome + link | §Bricomarché (pais rápidos + variações por `parent=`; link `/{loja}/produto/{slug}/`) |
| STORE-02 | Allmat: preço por caixa convertido com a área | §Allmat (cêntimos com IVA; bloco `.allmat-loop-price-box` ancorado ao preço da API; "Produto por caixa") |
| STORE-03 | Obras 360: variantes + escalões | §Obras 360 (`product-list` + `product-details/27`, `attribute_values_prices`, `DiscountByQuantity.levels`) |
| STORE-05 | Estado por loja sempre visível | §Pattern 3 (classificação de estados com os marcadores reais de cada loja) |
| STORE-07 | Verificação das lojas | §Pattern 7 (`verificar`, um termo-canário por loja, verificações de coerência) |
| PRICE-01 | Preço com IVA 23% + origem do IVA | §Pattern 4 (política por loja + evidência; Obras 360 net×1,23 confirmado igual ao `with_tax` da loja) |
| PRICE-02 | Preço unitário normalizado | §Pattern 5 (conteúdo da embalagem: `conversion_factor` Beevo, área da caixa Allmat, kg/L no título) |
| RES-02 | Stock quando a loja indica, sem filtrar | §Stock por loja (texto Woo "N em stock"/"Esgotado", inteiro por variante na Obras 360) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Python 3.13 + uv; correr sempre `uv run python -m strata ...`. Neste Windows **nunca** `python3` (atalho da Microsoft Store); usar `python`.
- Cliente HTTP único: `curl_cffi` com `impersonate="chrome"`. Não usar `requests`/`httpx`/`urllib` para as lojas.
- Dinheiro em `Decimal`; preço vem sempre de campo estruturado (API → JSON-LD → HTML → IA). Nada de LLM a ler preços nesta fase.
- Sem base de dados, sem pandas, sem pint, sem tenacity, sem python-dotenv; nada de proxies/CAPTCHA.
- Testes com pytest sobre ficheiros gravados, sem rede (o vcrpy não interceta curl_cffi).
- Ritmo respeitador por loja e **nunca omitir falhas em silêncio**.
- `ponytail` ativo: a solução completa mais pequena, sem abstrações especulativas; atalhos com limite levam comentário `shortcut: <limite>, <quando mudar>`.
- Textos para pessoas em PT-PT (`humanizer`); respostas ao utilizador no estilo i-have-adhd.
- Trabalho só dentro de um fluxo GSD (`/gsd-execute-phase`).
- Desvio já decidido no ROADMAP: **openpyxl** (não XlsxWriter) para ler a folha e gerar o modelo.

## Summary

As três lojas têm dados estruturados limpos e baratos de ler; o trabalho da fase está em **escolher os campos certos** e em **não perder ofertas em silêncio**. As sondas de hoje fecharam as dúvidas que o planeamento tinha. Na Bricomarché, `orderby=price` com `type=variation` **não ordena** (verificado), mas há um caminho muito mais rápido do que os ~12 s por página: pesquisar os produtos-pai (~2 s), depois pedir as variações só dos pais escolhidos com `type=variation&parent=<ids>` (~2,5 s por página de 100). A Obras 360 responde em 0,2–2,6 s, aceita `items_per_page=48` e `page=N`, e o `product-details/27` só precisa de `product_id`. A Allmat devolve `[]` com `X-WP-Total: 0` quando não tem o produto (marcador próprio de "sem resultados").

Há três armadilhas novas que o planeamento tem de cobrir. (1) **As três lojas fazem AND de todas as palavras**: "OSB 12mm" dá zero na Bricomarché ("12mm" ≠ "12 MM") e zero na Obras 360 (o pai chama-se "9-30MM"). A pesquisa alargada D-14 vai disparar quase sempre que a linha tiver medidas, por isso é caminho principal, não exceção. (2) Na Bricomarché, o `prices.price` do pai **não é fiável** (0 em 37 de 85 pais de "cimento", e diferente de `price_range.min_amount` em 11 dos restantes). Serve só para escolher que pais expandir; o preço mostrado vem sempre das variações. (3) O link `?attribute_pa_loja=` da Store API redireciona para `/escolher-loja/`. O link que funciona é `https://www.bricomarche.pt/{loja-slug}/produto/{slug}/` (verificado: redireciona para a página do produto nessa loja).

Na Obras 360, o JSON do `product-details` escreve `prices_with_convertion_factor` (com "t"), enquanto o `product-list` escreve `prices_with_conversion_factor`. O preço sem IVA × 1,23 bate exatamente com o `final_price_with_tax_unformatted` da loja (verificado em 10 variantes). Os escalões estão em `prices.discounts[]` com `class == "DiscountByQuantity"` e `levels: [{unity, value}]` (ex.: −2,5% a partir de 90).

**Primary recommendation:** pacote pequeno e plano (`strata/` com `stores/`). Parsers puros por loja testados com as amostras gravadas. Um `Fetcher` com `curl_cffi.AsyncSession` (limites por host, `--record`) e a classificação de estados num só sítio. Bricomarché pelo caminho "pais → variações por `parent`", com expansão limitada a K pais (recomendado 10).

## Architectural Responsibility Map

Ferramenta local de um processo; os "tiers" são camadas do próprio programa.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Ler `.xlsx`, gerar `modelo.xlsx` | Entrada (ficheiro local, openpyxl) | — | Só I/O de ficheiro; devolve `Item`/`Invalida` com nº de linha Excel |
| Ler texto colado | Entrada (stdin) | — | Parser puro de linha + leitura até linha vazia |
| Pedidos HTTP, ritmo por host, `--record`, deteção de bloqueio | Transporte (`fetch.py`) | — | Um só sítio para timeouts e estados; adaptadores nunca criam clientes |
| Saber que URL pedir e como ler a resposta | Adaptador de loja (`stores/*.py`) | Transporte | Relata o que a loja diz + evidência; não decide IVA final nem ordem |
| IVA, cêntimos, preço unitário, normalização de palavras | Núcleo puro (`money.py`/`text.py`) | — | Onde vivem os erros de dinheiro; 100% testável sem rede |
| Item × loja em paralelo, D-14, D-15, D-02/D-03, prazos | Orquestração (`search.py`) | Núcleo | Regras de produto iguais para as três lojas |
| Tabela no terminal | Saída (`report.py`) | — | Só formata `ItemResult`; Phase 5 troca por UI |
| Verificação das lojas (STORE-07) | Orquestração | Adaptadores | Reutiliza os adaptadores com um termo-canário por loja |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.13.2 (instalado) | Linguagem | Decisão do projeto [VERIFIED: `python --version` → 3.13.2] |
| uv | 0.12.6 (instalado) | venv, deps, `uv run` | Decisão do projeto [VERIFIED: `uv --version`] |
| curl_cffi | 0.16.3 (2026-09-02, `requires_python >=3.10`) | HTTP (TLS do Chrome), `AsyncSession` | Decisão do projeto; testado hoje nas 3 lojas, no `ProactorEventLoop` do Windows [VERIFIED: PyPI JSON + probe] |
| openpyxl | 3.1.5 (2024-06-28, `>=3.8`) | Ler a folha; gerar o modelo com validação de dados | Nota de stack do ROADMAP (o XlsxWriter não lê) [VERIFIED: PyPI JSON + teste local] |
| selectolax | `>=1.0,<1.1` (1.0.2 saiu hoje, 2026-10-22 15:43; 1.0.1 a 2026-10-17) | Ler o bloco de preço e "Produto por caixa" na página de produto da Allmat | Decisão do projeto; `LexborHTMLParser` testado hoje [VERIFIED: PyPI JSON + probe] |
| pytest | 9.1.1 (2026-06-19, `>=3.10`) | Testes | Decisão do projeto [VERIFIED: PyPI JSON] |

Biblioteca padrão que cobre o resto: `argparse` (CLI), `asyncio` (paralelismo, `asyncio.timeout`), `decimal`, `json` (`parse_float=Decimal`), `unicodedata` (NFKD), `hashlib` (nomes de fixtures), `urllib.parse` (links Bricomarché), `re`.

### Supporting
Nenhuma. Nesta fase não entram anthropic, NiceGUI, Playwright, XlsxWriter, rich nem orjson.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| selectolax na página Allmat | `re` sobre o HTML | Menos uma dependência, mas o bloco certo tem de ser escolhido entre vários `.allmat-loop-price-box` (produtos relacionados); com seletores fica legível. Manter selectolax (já está na STACK). |
| `argparse` | click/typer | Dependência nova para 3 subcomandos. Não. |
| tabela à mão (`str.ljust`) | rich | Dependência nova; a UI chega na Phase 5. Não. |

**Installation:**
```bash
uv init --package --name strata --python 3.13 .   # na raiz do repo; cria pyproject + src/strata/
uv add curl_cffi openpyxl "selectolax>=1.0,<1.1"
uv add --dev pytest
```
`uv init --package` gera `src/strata/__init__.py`, `[project.scripts] strata = "strata:main"` e o backend `uv_build`; `uv run python -m strata` funciona com `src/strata/__main__.py` [VERIFIED: teste num diretório de rascunho]. O `uv init` também escreve `README.md`, `.gitignore` e `.python-version`; rever antes do commit.

## Package Legitimacy Audit

Seam `gsd-tools query package-legitimacy check --ecosystem pypi` executado hoje:

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| curl_cffi | PyPI | 0.16.3 de 2026-09-02 (projeto com anos) | desconhecido (PyPI não expõe) | github.com/lexiforest/curl_cffi (em `project_urls.repository`; o seam não o leu) | [SUS] (`unknown-downloads`, `no-repository`) | Flagged — planner adiciona checkpoint |
| openpyxl | PyPI | 3.1.5 de 2024-06-28 | desconhecido | foss.heptapod.net/openpyxl/openpyxl | [SUS] (`unknown-downloads`) | Flagged — planner adiciona checkpoint |
| selectolax | PyPI | **1.0.2 publicado hoje (2026-10-22 15:43)** | desconhecido | github.com/rushter/selectolax | [SUS] (`too-new`, `unknown-downloads`) | Flagged — pin `>=1.0,<1.1`; se o checkpoint preferir, fixar `==1.0.1` |
| pytest | PyPI | 9.1.1 de 2026-06-19 | desconhecido | github.com/pytest-dev/pytest | [SUS] (`unknown-downloads`) | Flagged — planner adiciona checkpoint |

**Packages removed due to [SLOP] verdict:** nenhum.
**Packages flagged as suspicious [SUS]:** os quatro. Para três deles a causa é sistémica: o PyPI não publica contagens de downloads, por isso `unknown-downloads` aparece sempre. O único sinal real é a idade do selectolax 1.0.2. Os quatro já constam do STACK.md do projeto (escolhidos e verificados no PyPI a 2026-10-22). Recomendação: **um** `checkpoint:human-verify` antes do `uv add`, a confirmar os quatro nomes e o pin do selectolax.

## Architecture Patterns

### System Architecture Diagram

```
 [.xlsx path]──► sheet.read_sheet ──┐                     ┌─► [modelo] sheet.write_template ──► modelo.xlsx (open "xb")
 [stdin colado]─► text.parse_lines ─┼─► Item[] + Invalida[]│
                                    ▼                      │
                        search.run(items) ── asyncio.gather(item × loja) ──────────────────────┐
                                    │                                                         │
          ┌─────────────────────────┼──────────────────────────────┐                          │
          ▼                         ▼                              ▼                          │
   stores.allmat              stores.bricomarche             stores.obras360                  │
   Store API search           pais: search (~2 s)            product-list (widget lido 1×/run)│
   + página (só "M2")         → top K por preço do pai       → filtro D-15 nos pais           │
                              → variações parent=ids         → product-details/27 por pai     │
          │ RawOffer[]/estado       │                              │                          │
          └──────────── fetch.Fetcher (AsyncSession chrome, limite+intervalo por host, ───────┤
                        classificação: ok/sem resultados/bloqueada/erro/tempo esgotado,       │
                        --record DIR grava cada corpo)                                         │
                                    │                                                          │
                                    ▼                                                          │
     zero resultados? ──sim──► 2.ª pesquisa alargada (D-14, 1×) ──► marca "pesquisa alargada"  │
                                    │                                                          │
                                    ▼                                                          │
         money: IVA (política+evidência) → preço unitário na unidade pedida (ou motivo)        │
         text:  filtro de título D-15 (conta escondidas)                                       │
         ordena (D-03), corta a 5 (D-02, conta o resto)                                        │
                                    ▼                                                          │
                     report.print_item: secção por loja, estado primeiro ◄─────────────────────┘
```

### Recommended Project Structure
```
pyproject.toml
src/strata/
├── __main__.py        # argparse: pesquisar [xlsx] | modelo | verificar; --record DIR (dev)
├── models.py          # dataclasses: Item, Invalida, Offer, StoreResult (estados como Literal)
├── sheet.py           # ler folha + escrever modelo (openpyxl)
├── text.py            # norm() NFKD, parse de linha colada, unidades/sinónimos, palavras D-15, query alargada D-14
├── money.py           # cêntimos→Decimal, IVA, preço unitário (puro)
├── fetch.py           # Fetcher: AsyncSession, Host(sem+intervalo), get_json/get_html, estados, --record
├── stores/
│   ├── allmat.py      # search() + parse puros
│   ├── bricomarche.py
│   └── obras360.py
├── search.py          # item × loja, D-14, D-15, ordenação/corte, verificar()
└── report.py          # tabela no terminal
tests/
├── conftest.py        # FakeFetcher (URL→ficheiro), bloqueio de rede
├── fixtures/          # gravadas com --record (ponto de partida: .planning/phases/01-.../samples/)
└── test_*.py
```
Um `woo.py` genérico **não** compensa: a Allmat e a Bricomarché partilham só o formato de cêntimos e o `X-WP-Total` (2 linhas em `money.py`/`fetch.py`). Os fluxos são diferentes (variações por loja física vs. página da caixa).

### Pattern 1: Adaptador = pedidos + parsers puros; o transporte é injetado
**What:** cada `stores/x.py` expõe `async def search(query, fetch) -> StoreResult` e funções puras `parse_*(json) -> list[Offer]`. O `fetch` é o `Fetcher` real ou um `FakeFetcher` nos testes.
**When to use:** as três lojas.
```python
# models.py — o mínimo que as Phases 2–4 vão estender
Status = Literal["ok", "sem resultados", "bloqueada", "erro", "tempo esgotado"]

@dataclass
class Offer:
    store: str; title: str; url: str
    price: Decimal                 # preço de 1 artigo vendido (placa, caixa, saco), COM IVA
    vat_origin: Literal["indicado pela loja", "regra da loja", "assumido"]
    vat_evidence: str              # ex.: "tax_percentage=23", "página: IVA incluído", "B2C (DL 138/90)"
    content: Decimal | None = None # quantidade da unidade-base num artigo (3.125 m², 25 kg, 1 un)
    content_unit: str | None = None  # "m²" | "un" | "kg" | "L" | "m"
    stock: str = "desconhecido"    # "em stock" | "esgotado" | "N em stock" | "desconhecido"
    location: str | None = None    # Bricomarché: nome da loja física
    tiers: list[tuple[Decimal, Decimal]] = field(default_factory=list)  # (a partir de N, −%)
    broadened: bool = False        # D-14
    note: str = ""                 # motivo de "não convertível", "derivada", etc.

@dataclass
class StoreResult:
    store: str; status: Status; offers: list[Offer]; detail: str = ""
    hidden: int = 0                # D-15
```

### Pattern 2: Limite por host dentro do Fetcher
**What:** um semáforo + intervalo mínimo por host, aplicados a todos os pedidos; timeout `(10, 30)` (curl_cffi soma: ligação 10 s, total 40 s) [VERIFIED: `curl_cffi/requests/utils.py` lido hoje: tuplo → `CONNECTTIMEOUT_MS` + `TIMEOUT_MS = connect+read`].

| Host | Concorrência | Intervalo | Porquê |
|------|-------------|-----------|--------|
| allmat.pt | 2 | 0,5 s | Cloudflare (`server: cloudflare`, `cf-ray`), sem desafio a este ritmo hoje |
| www.bricomarche.pt | 2 | 0,5 s | nginx, sem WAF; pedidos lentos mas não hostis |
| www.obras360.pt | 3 | 0,3 s | nginx, sem proteção; muitos `product-details` pequenos (0,2–0,3 s) |

Prazo por (item, loja): `asyncio.timeout(90)` → "tempo esgotado" [ASSUMED: 90 s cobre a Bricomarché com K=10 e a alargada; afinar com a verificação].

### Pattern 3: Estados com os marcadores reais de cada loja (STORE-05)
| Situação observada | Estado | Marcador |
|---|---|---|
| Woo 200 + `[]` + `X-WP-Total: 0` | sem resultados | Allmat "osb", Bricomarché "xyzqwkk" [VERIFIED: probe] |
| Beevo `success: true` + `total_products: 0` + `products: []` | sem resultados | "xyzqwkk", "osb 12mm" [VERIFIED: probe] |
| Beevo `success: false` (`product-list` com widget errado; `product-details` com id errado) | erro ("widget/produto mudou") | [VERIFIED: probe, resposta de 69 bytes] |
| `curl_cffi.requests.exceptions.Timeout` ou `asyncio.TimeoutError` do prazo | tempo esgotado | [VERIFIED: classe `Timeout` apanhada num teste com `timeout=(5,1)`] |
| 403/429/503, ou HTML onde se esperava JSON, com `cf-mitigated`, "Just a moment", "challenge-platform", `x-datadome`, "captcha" | bloqueada | [ASSUMED: marcadores Cloudflare/DataDome padrão; não reproduzidos hoje] |
| Outro HTTP ≥ 400, `ConnectionError`/`SSLError`, JSON inválido, `KeyError` no parser | erro (com detalhe) | — |

Regra: os adaptadores **lançam** (`StoreBlocked`, `LayoutChanged`, ...) e um único `try/except` em `search.py` converte tudo em `StoreResult`. Nunca `except: return []`.

### Pattern 4: IVA = política da loja + evidência (PRICE-01)
| Loja | Campo lido | Origem | Evidência |
|---|---|---|---|
| Obras 360 | `prices.final_price_unformatted` (sem IVA) × (1 + `tax_percentage`/100) | **indicado pela loja** | `tax_percentage: 23` por variante e `message_tax_applied: "LANG_PRODUCT_TAX_NOT_INCLUDED"`. Verificação cruzada: o resultado tem de bater com `final_price_with_tax_unformatted` a ±0,01 € (bate em todas as variantes testadas) [VERIFIED: probe] |
| Allmat | `prices.price` em cêntimos (`currency_minor_unit: 2`) | **regra da loja** | página de produto: "IVA incluído" junto ao preço (verificado em 3 produtos) [VERIFIED: probe] |
| Bricomarché | `prices.price` da **variação** em cêntimos | **regra da loja** | B2C; DL 138/90 obriga a preço com taxas. Nenhuma página diz "IVA" (termos e FAQ lidos hoje sem menção) [VERIFIED: ausência lida nas páginas; a inferência legal é CITED em PITFALLS.md] |

`tax_percentage != 23` → oferta mostrada com aviso "IVA da loja X%: não convertido" (ilhas fora de âmbito), nunca recalculada em silêncio. "assumido" não é usado por nenhuma das três lojas nesta fase; fica no tipo para a Phase 6.

### Pattern 5: Preço unitário a partir do conteúdo do artigo (PRICE-02)
`Offer.price` é sempre o preço de **um artigo vendido**; `content`/`content_unit` dizem quanto traz. Na unidade pedida `u`:
- `u == "un"` ou `"saco"` → €/un = `price` (o artigo é a unidade) [ASSUMED: "saco" pedido = 1 artigo; confirmar com o utilizador].
- `u == content_unit` → `price / content`.
- caso contrário → "não convertível: <motivo>" e vai para o fim (D-03).

De onde vem o conteúdo:
| Loja | Artigo / conteúdo |
|---|---|
| Obras 360 | artigo = `sell_unit.description` (ex.: `"m2/Placa"`, `"Unidade"`, `"Kg"`, `"Caixa"`); unidade-base = `visible_sell_unit.description` (`"M2"`, `"UN"`, `"KG"`, `"CX"`); conteúdo = `prices.conversion_factor` (OSB: 3.125; cola epóxi "Kg": 10). Preço do artigo = `prices_with_convertion_factor.final_price_unformatted` × 1,23; preço por unidade-base = `prices.final_price_unformatted` × 1,23 [VERIFIED: probe; 15.024066 = 4.807701 × 3.125] |
| Allmat | rótulo `span.wd-price-unit` em `price_html` (`"Unid"` → 1 un; `"M2"` → ir à página). Na página, o `.allmat-loop-price-box` cujo `.allmat-loop-current-box` = preço da API dá o €/m² (`.allmat-loop-current-m2`); a área vem de "Produto por caixa: 1.37 m2" (`.elementor-button-text`), ou, se faltar, de caixa ÷ m² (nota "área derivada") [VERIFIED: probe em 3 produtos] |
| Bricomarché | só o título: regex de conteúdo kg/g/L/ml/m² (ex.: "CIMENTO COLA CINZA 20KG" → 20 kg). Medidas (2.50X1.25 → m²) ficam para a Phase 3 (MATCH-01) |

### Pattern 6: Parser da linha colada, a partir do fim (D-11/D-12)
```python
UNITS = {"un": "un", "unid": "un", "uni": "un", "m2": "m²", "m": "m", "kg": "kg",
         "l": "L", "lt": "L", "saco": "saco", "sacos": "saco"}   # chaves já passadas por norm()
NUM = re.compile(r"^\d+(?:[.,]\d+)?$")
GLUED = re.compile(r"^(\d+(?:[.,]\d+)?)([^\d\s]+)$")              # "30un", "10sacos"

def parse_line(line: str):
    toks, warns, unit, qty = line.split(), [], None, None
    if toks and norm(toks[-1]) in UNITS:
        unit = UNITS[norm(toks.pop())]
    elif toks and (m := GLUED.match(toks[-1])) and norm(m[2]) in UNITS:
        toks.pop(); qty, unit = to_decimal(m[1]), UNITS[norm(m[2])]
    if qty is None and toks and NUM.match(toks[-1]) and len(toks) > 1:
        qty = to_decimal(toks.pop())
    if not toks: return None, "linha sem descrição"
    if unit is None: unit = "un"; warns.append("unidade assumida: un")
    if qty is None: qty = Decimal(1); warns.append("quantidade assumida: 1")
    return Item(product=" ".join(toks), qty=qty, unit=unit, warnings=warns), None
```
"OSB 12mm 30 un" → ("OSB 12mm", 30, un); "OSB 12mm" → ("OSB 12mm", 1, un) + 2 avisos ("mm" não é unidade); "azulejo 30 m²" → m² (NFKD faz "²"→"2").

### Pattern 7: Verificação das lojas (STORE-07)
`uv run python -m strata verificar`: um termo-canário por loja ("cimento" na Allmat e na Bricomarché; "osb" na Obras 360) pelo mesmo `search()` do dia a dia. Falha se: estado ≠ ok; zero ofertas; algum `price <= 0`; Obras 360 com `tax_percentage != 23` ou net×1,23 ≠ `with_tax` (±0,01); Allmat com área de caixa e |€/caixa − €/m² × área| > 2%; Bricomarché sem nome de loja. Imprime uma linha por loja ("Allmat: OK, 11 ofertas, 4,22 €…") e devolve código de saída 1 se alguma falhar. Também apanha a mudança do ID do widget da Obras 360 (Anti-Pattern 5 da ARCHITECTURE).

### Anti-Patterns to Avoid
- **Preço do pai na Bricomarché como preço mostrado:** 0 em 37/85 pais de "cimento"; diferente do `price_range.min_amount` em 11 casos (ex.: `price 990`, `range 1199–1399`). Usar só para escolher o top-K; o número mostrado vem da variação.
- **Seguir o `permalink` das variações Bricomarché:** `?attribute_pa_loja=` → redireciona para `/escolher-loja/?next=...` sem cookie [VERIFIED: probe].
- **Primeiro `.allmat-loop-price-box` da página:** no produto 21574, o primeiro bloco é de um produto relacionado (14,99 €/m²); o preço principal é `5,99 € M2` noutro bloco. Escolher o bloco pelo preço da API.
- **`r.json()` do curl_cffi para dinheiro:** usa `orjson` se estiver instalado e não aceita `parse_float` [VERIFIED: `curl_cffi/requests/models.py:304-311` lido hoje]. Usar `json.loads(r.content, parse_float=Decimal)`.
- **Substring em vez de palavra no filtro D-15:** a Bricomarché devolve "PAINEL AQUECIMENTO" para "cimento". Comparar palavras normalizadas.
- **Paginação com parâmetros diferentes entre páginas:** a página 1 com `orderby=price` e a 2 sem ele deram linhas repetidas e em falta (76 linhas de um pai que tem 65). Mesmos parâmetros em todas as páginas.

## Store Specifics (sondas de 2026-10-22, `curl_cffi` `impersonate="chrome"`)

### Obras 360 (`https://www.obras360.pt`, plataforma Beevo)
1. **ID do widget** (uma vez por execução): `GET /pesquisa?search=osb` (≈700 KB, 0,4 s). Regex: `"widget_slug":"product-list","widget_instance_id":"([0-9a-f-]+)"` → hoje `f1f5fb06-09e7-4519-8f44-9b3cd0093460` [VERIFIED: probe].
2. **Lista:** `GET /api/latest/dot/shop/product-list/{widget}?search=<q>&items_per_page=48&page=<n>`. Os `_beevo_decoded_params[0][page_id]=241&...[segment]=pesquisa` **não são precisos** (mesma resposta sem eles). Por omissão vêm 12 por página; `items_per_page=48` funciona; `page=2` funciona. `has_more` vem sempre `1` e `page_count` vem `1` mesmo com 13 produtos: **paginar por `total_products` e `items_per_page`** [VERIFIED: probe].
   - Caminho: `meta_data.protected.products[]`; cada item é `{"product": {...}, "children": {...}}`.
   - `product.product.product_id` (id do pai, UUID), `product.name`, `product.seo_data.segment` (URL = `https://www.obras360.pt/{segment}`), `product.sell_unit.description`, `product.visible_sell_unit.description`, `product.prices.*` (unidade-base), `product.prices_with_conversion_factor.*` (artigo), `product.stock`, `product.availability_days_message` (HTML: "Previsão em Armazém Lisboa: <b>6 dias úteis</b>").
   - Variantes: `product.attributes._productByAttribute` = `{attribute_value_id: {product_id, parent_id, is_available}}`; designação legível em `product.attributes._selectionsAttributes["1"].values[attribute_value_id].designation` (ex.: `"1 Placa 12 MM - 2,5 M x 1,25 M - 3,125 M2 - 22,31 KG"`, chave `19875`). **Não há preços por variante na lista** (os `children.children[*]` só têm sku/stock) [VERIFIED: probe].
   - Todos os produtos têm ≥1 variante (12/12 em "osb").
3. **Detalhe:** `GET /api/latest/dot/shop/product-details/27?_beevo_decoded_params[0][product_id]=<id do pai>` (0,2–0,3 s; o `segment` é dispensável). `meta_data.protected.attribute_values_prices` = `{attribute_value_id: {sku, stock, segment, prices, prices_with_convertion_factor, min_purchase_quantity, purchase_quantity, ...}}`; as chaves são as mesmas do `_productByAttribute` (verificado em OSB, tijolo e cola) [VERIFIED: probe].
   - Escalões: `prices.discounts[i]` com `class == "DiscountByQuantity"`, `calc_value_mathop == "-%"`, `levels == [{"unity": 90, "value": 2.5}]` (OSB 12 mm: −2,5% a partir de 90). Algumas variantes não têm (`discounts: []`).
   - Id inválido → `success: false` e `attribute_values_prices: []` (lista vazia; com dados é dict — peculiaridade PHP).
   - `product-details` **27** é um ID numérico do widget, não UUID; é constante com comentário `shortcut:` e a verificação STORE-07 apanha uma mudança [ASSUMED: estável; não há forma barata de o ler sem ir a uma página de produto de 700 KB].
4. **Pesquisa:** AND de palavras sobre o nome. "osb" → 13; "osb 12mm", "OSB 12 mm" e "osb 12" → 0; "placa osb" → 7 [VERIFIED: probe]. Ou seja, a D-14 alargada é o caminho normal para linhas com medidas.
5. **Volume:** "cimento" = 119 produtos (3 páginas de 48). Expandir todos custaria ~119 × 0,3 s. Recomendação: aplicar D-15 aos nomes **antes** de expandir e expandir no máximo 20 pais por item; os restantes contam como "+N produtos não expandidos" [ASSUMED: 20 equilibra tempo (~6 s) e cobertura].
6. Amostras: `samples/obras360_product-list_osb.json` (2 produtos), `samples/obras360_product-details_osb-parent.json`, `samples/obras360_product-list_no-results.json`.

### Bricomarché (`https://www.bricomarche.pt`, WooCommerce)
1. **Pais:** `GET /wp-json/wc/store/v1/products?search=<q>&per_page=100` → 2,1–4,3 s; tudo `type: variable` ("osb": 4 pais; "cimento": 85) [VERIFIED: probe].
   - Pré-ordenação: `price_range.min_amount` se existir, senão `price`; pais com `price == "0"` e `price_range: null` e `variations: []` (ex.: "Planta Artificial Cimento Branco") → sem preço, contados, não expandidos.
2. **Variações dos K pais escolhidos:** `GET /wp-json/wc/store/v1/products?type=variation&parent=<id1>,<id2>,...&per_page=100&page=<n>` → ~2–2,8 s por página; 65 variações por pai (≈ uma por loja física) [VERIFIED: probe: `parent=47412,47411` → `X-WP-Total: 130`; `parent[]=a&parent[]=b` devolveu só um pai, **não usar**].
   - Comparação com `search=osb&type=variation`: ~10–11 s por página **com qualquer `per_page`** (25 → 10,4 s, 7 páginas) e 166 linhas. O caminho por `parent` dá o mesmo mínimo (1449 e 1849 cêntimos, Coina - Barreiro) em ~5 s no total.
   - `orderby=price&order=asc` com `type=variation`: **não ordena** (primeiras: 1872, 2299, 1589, 2099...) [VERIFIED: probe]. Paginar sempre todas as páginas dos pais escolhidos.
   - K recomendado: 10 pais (2× D-02, para absorver a incoerência do preço do pai) ≈ 7 páginas ≈ 9 s com concorrência 2 [ASSUMED].
3. **Campos da variação:** `prices.price` ("1849", cêntimos, `currency_minor_unit: 2`), `variation` ("Loja: Coina - Barreiro"), `parent`, `stock_availability.text` ("66 em stock" | "Esgotado") e `.class` ("in-stock" | "out-of-stock"), `permalink` (".../produto/plc-osb-lisa-2-50x1-25-12mm/?attribute_pa_loja=coina-barreiro"), `add_to_cart.maximum` (= stock). Ignorar `price <= 0`.
4. **Link:** `https://www.bricomarche.pt/{attribute_pa_loja}/produto/{último segmento do path do permalink}/` → 200, redireciona para `/coina-barreiro/produto/madeiras/madeiras-e-derivados-a-corte/plc-osb-lisa-2-50x1-25-12mm/` [VERIFIED: probe]. O preço na página é desenhado por JS (no HTML só aparece no `_egoiaq ... 18.49`).
5. **Mais barata vs. com stock:** a variação mais barata pode estar "Esgotado". RES-02 diz "sem filtrar": mostrar a mais barata com o stock dessa loja (ver Open Questions).
6. Amostras: `samples/bricomarche_products_search-osb.json`, `samples/bricomarche_variations_parent-47412.json` (65 linhas, campos essenciais).

### Allmat (`https://allmat.pt`, WooCommerce + Woodmart + WholesaleX)
1. **Pesquisa:** `GET /wp-json/wc/store/v1/products?search=<q>&per_page=100` → 2,0–3,2 s, `server: cloudflare`, JSON. "osb" → `[]` + `X-WP-Total: 0` (sem resultados legítimo); "cimento" → 11; "pavimento" → 24 [VERIFIED: probe]. **0 produtos `variable` em 3704** (só `simple`).
2. `prices.price` em cêntimos com IVA ("422" = 4,22 €); `stock_availability.text` ("186 em stock"); rótulo `span.wd-price-unit` dentro de `price_html` ("Unid" ou "M2").
3. **Rótulo "M2" não é fiável:** no Splendor (`id 39233`), a API dá 1374 com "M2", mas a página diz "9,99 € / m² Ou 13,74 € / Caixa" e "Produto por caixa: 1.37 m2". Ou seja, 1374 é o preço **da caixa**. No Nest 30x60 não existe o texto "Produto por caixa" (só 15,99/m² e 20,15/caixa). No azulejo 15x15 (21574), o bloco principal é `.allmat-loop-price-default` "5,99 € M2" sem caixa [VERIFIED: probe].
4. **Regra recomendada:** "Unid" → artigo = 1 un, sem página. "M2" → `GET` do `permalink` e procurar, dentro de `#product-{id}`, o `.allmat-loop-price-box` cujo `.allmat-loop-current-box` = preço da API:
   - Encontrado → €/m² = `.allmat-loop-current-m2`; área = "Produto por caixa: X m2" se existir, senão caixa ÷ m² (nota "área derivada"). Com área declarada, verificar |caixa − m²×área| ≤ 2% (Splendor: 9,99×1,37 = 13,69 vs 13,74 → 0,4%).
   - Não encontrado → €/m² desconhecido, motivo "área da caixa não encontrada na página (rótulo M2 da loja)", fim da lista (decisão de discrição do CONTEXT).
5. Amostras: `samples/allmat_products_search-cimento.json`, `samples/allmat_products_search-osb_no-results.json`, `samples/allmat_product-page_39233_box.html` (só `#product-39233`, sem scripts).

### Stock por loja (RES-02)
| Loja | Fonte | Texto mostrado |
|---|---|---|
| Allmat | `stock_availability.text` | tal como vem ("186 em stock"); vazio → "desconhecido" |
| Bricomarché | `stock_availability.text` da variação escolhida | "66 em stock" / "Esgotado" |
| Obras 360 | `attribute_values_prices[*].stock` (inteiro) | >0 → "N em stock"; 0 → "esgotado" + `availability_days_message` sem HTML ("Previsão em Armazém Lisboa: 6 dias úteis") |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TLS/HTTP2 parecido com o Chrome | cabeçalhos "à Chrome" com outro cliente | `curl_cffi` `impersonate="chrome"` | A impressão TLS é o que o Cloudflare/DataDome vê |
| Ler/gravar `.xlsx` e listas pendentes | XML à mão | openpyxl `load_workbook`, `DataValidation` | Formato zip+XML complexo |
| Tirar acentos e "²" | tabelas de substituição | `unicodedata.normalize("NFKD")` + remover `combining` | Já trata "m²"→"m2", "Família"→"familia" [VERIFIED: teste local] |
| Decimais exatos a partir do JSON | `float` → `Decimal` | `json.loads(..., parse_float=Decimal)` | A loja já traz ruído de float (`0.5762550000000001`) |
| Não sobrescrever o modelo | `exists()` + `save()` (corrida) | `with open(p, "xb") as f: wb.save(f)` | `FileExistsError` atómico [VERIFIED: teste local] |
| Concorrência com prazos | threads | `asyncio.gather` + `asyncio.timeout` | Funciona no `ProactorEventLoop` do Windows com curl_cffi [VERIFIED: probe] |

**Key insight:** quase todo o código desta fase é escolher campos e mapear estados. O valor está nos parsers puros testados com respostas reais. Infraestrutura genérica não traz nada aqui.

## Common Pitfalls

### Pitfall 1: Bricomarché lenta por usar `search` + `type=variation`
**What goes wrong:** ~10–11 s por página, qualquer que seja o `per_page`; "cimento" teria ~36 páginas.
**How to avoid:** pais (~2 s) → top-K → `type=variation&parent=<csv>` (~2,5 s/página).
**Warning signs:** um item demora mais de 30 s só na Bricomarché.

### Pitfall 2: Preço do pai Bricomarché tratado como verdade
**What goes wrong:** 0 € ou um mínimo antigo; ordenação errada.
**How to avoid:** pré-ordenar com `min(price>0, price_range.min_amount)`, mostrar só preços de variações e verificar `price > 0`.

### Pitfall 3: Todas as palavras têm de bater (AND) nas três lojas
**What goes wrong:** "OSB 12mm" → zero na Bricomarché e na Obras 360; "cimento 25kg" → zero na Allmat.
**How to avoid:** a D-14 alargada tira os tokens com dígitos **e** os tokens de unidade soltos que sobrem ("placa osb 12 mm" → "placa osb", não "placa osb mm"); se a alargada ficar vazia (ex.: "12mm"), não pesquisar e dar "sem resultados" com o motivo.
**Warning signs:** "pesquisa alargada" em quase todas as linhas com medidas (é esperado; mostrar sem ruído).

### Pitfall 4: Chave com erro ortográfico na Obras 360
**What goes wrong:** `KeyError` em `prices_with_conversion_factor` no `product-details`.
**How to avoid:** detalhe = `prices_with_convertion_factor`; lista = `prices_with_conversion_factor` [VERIFIED: probe]. Testar com as amostras.

### Pitfall 5: `attribute_values_prices` é `[]` quando vazio e `{}`-com-dados quando cheio
**How to avoid:** `if not d["success"] or not avp: raise LayoutChanged(...)` antes de `.items()`.

### Pitfall 6: Bloco de preço errado na página Allmat
**What goes wrong:** o 1.º `.allmat-loop-price-box` pode ser de um produto relacionado; o mini-carrinho tem um "0,00 €".
**How to avoid:** procurar dentro de `#product-{id}` e escolher o bloco cujo preço da caixa é igual ao da API.

### Pitfall 7: Linha Excel errada nas mensagens
**What goes wrong:** em modo `read_only`, `iter_rows()` começa em `ws.min_row` (pode não ser 1) e as células vazias (`EmptyCell`) não têm `.row`.
**How to avoid:** modo normal (`load_workbook(p, data_only=True)`; as folhas são pequenas) e `enumerate(ws.iter_rows(min_row=1, values_only=True), start=1)` [VERIFIED: teste local da leitura; ASSUMED: comportamento de `min_row` em read_only, não reproduzido].

### Pitfall 8: Acentos e "²" partidos no Windows
**What goes wrong:** com stdin em pipe, a codificação é `cp1252` [VERIFIED: probe: `sys.stdin.encoding == "cp1252"` em pipe]; "m²" em UTF-8 chega como dois caracteres.
**How to avoid:** no arranque, `sys.stdin.reconfigure(encoding="utf-8")` e `sys.stdout.reconfigure(encoding="utf-8")` [VERIFIED: com reconfigure, "²" chega como `0xb2`]. Na consola interativa já é UTF-8 [ASSUMED: comportamento da consola Windows].

### Pitfall 9: Arredondar cedo demais
**What goes wrong:** tijolo a 0,3478 € sem IVA → 0,43 € com IVA; arredondar o unitário a cêntimos perde ordem entre ofertas próximas.
**How to avoid:** guardar `Decimal` completo, arredondar só ao mostrar (`ROUND_HALF_UP`, 2 casas no preço; 3–4 casas no €/unidade abaixo de 1 €).

### Pitfall 10: Excel com fórmulas, `.xls` ou ficheiro corrompido
**How to avoid:** `data_only=True` (fórmulas → último valor guardado pelo Excel; `None` se nunca calculado → "Qty vazia"). Apanhar `openpyxl.utils.exceptions.InvalidFileException` (`.xls`) e `zipfile.BadZipFile` → mensagem clara. `bool` é `int` em Python: rejeitar Qty `True/False`.

## Code Examples

### Fetcher: limite por host, estados e `--record`
```python
# fetch.py — fonte: API curl_cffi 0.16.3 (AsyncSession, timeout tuplo) lida hoje
import asyncio, hashlib, json, time
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from curl_cffi.requests import AsyncSession
from curl_cffi.requests.exceptions import RequestException, Timeout

class StoreBlocked(Exception): ...
class StoreError(Exception): ...
class StoreTimeout(Exception): ...

LIMITS = {"allmat.pt": (2, 0.5), "www.bricomarche.pt": (2, 0.5), "www.obras360.pt": (3, 0.3)}
CHALLENGE = ("just a moment", "challenge-platform", "captcha", "datadome")

def fixture_name(url: str) -> str:   # o mesmo nome no --record e no FakeFetcher
    return f"{urlsplit(url).hostname}_{hashlib.sha1(url.encode()).hexdigest()[:12]}"

class Host:
    def __init__(self, n, gap): self.sem, self.gap, self.next, self.lock = asyncio.Semaphore(n), gap, 0.0, asyncio.Lock()
    async def __aenter__(self):
        await self.sem.acquire()
        async with self.lock:
            await asyncio.sleep(max(0, self.next - time.monotonic()))
            self.next = time.monotonic() + self.gap
    async def __aexit__(self, *exc): self.sem.release()

class Fetcher:
    def __init__(self, session: AsyncSession, record: Path | None = None):
        self.s, self.record = session, record
        self.hosts = {h: Host(*v) for h, v in LIMITS.items()}

    async def get(self, url, params=None):
        full = f"{url}?{urlencode(params)}" if params else url
        async with self.hosts[urlsplit(url).hostname]:
            try:
                r = await self.s.get(full)
            except Timeout as e: raise StoreTimeout(str(e)) from e
            except RequestException as e: raise StoreError(f"ligação: {e}") from e
        if r.status_code in (403, 429, 503) or r.headers.get("cf-mitigated"):
            raise StoreBlocked(f"HTTP {r.status_code}")
        if r.status_code >= 400: raise StoreError(f"HTTP {r.status_code}")
        if self.record:
            (self.record / fixture_name(full)).write_bytes(r.content)
        return r

    async def get_json(self, url, params=None):
        r = await self.get(url, params)
        try: return json.loads(r.content, parse_float=Decimal), r.headers
        except ValueError as e:
            # só aqui o texto da página conta: era JSON e veio HTML
            if any(m in r.text[:4000].lower() for m in CHALLENGE): raise StoreBlocked("página de desafio") from e
            raise StoreError("resposta não é JSON (layout mudou?)") from e
```
Uso: `async with AsyncSession(impersonate="chrome", timeout=(10, 30)) as s: fetch = Fetcher(s, record_dir)`.
Atenção: **não** procurar "captcha" no corpo de páginas HTML normais. A página `/pesquisa` da Obras 360 e as páginas de produto da Allmat contêm a palavra (reCAPTCHA dos formulários) [VERIFIED: grep nas páginas gravadas hoje], e seriam marcadas "bloqueada" por engano.

### Bricomarché: mais barata por pai, com loja e link
```python
from urllib.parse import parse_qs, urlsplit
BASE = "https://www.bricomarche.pt"

def cheapest_per_parent(rows):
    best = {}
    for r in rows:
        cents = int(r["prices"]["price"])
        if cents > 0 and (r["parent"] not in best or cents < int(best[r["parent"]]["prices"]["price"])):
            best[r["parent"]] = r
    return best

def store_link(row):
    u = urlsplit(row["permalink"])
    loja = parse_qs(u.query)["attribute_pa_loja"][0]
    slug = u.path.rstrip("/").split("/")[-1]
    return f"{BASE}/{loja}/produto/{slug}/", row["variation"].removeprefix("Loja: ")
```

### Obras 360: uma oferta por variante
```python
VAT_PT = Decimal("23")

def offers_from_details(d, parent):            # parent = item de product-list
    avp = d["meta_data"]["protected"]["attribute_values_prices"]
    if not d.get("success") or not avp:
        raise StoreError("product-details sem variantes (produto/widget mudou?)")
    sel = parent["product"]["attributes"]["_selectionsAttributes"]
    for value_id, v in avp.items():
        base, item = v["prices"], v["prices_with_convertion_factor"]      # sic: "convertion"
        rate = Decimal(base["tax_percentage"])
        price = item["final_price_unformatted"] * (1 + rate / 100)
        if abs(price - item["final_price_with_tax_unformatted"]) > Decimal("0.01"):
            raise StoreError(f"IVA incoerente na variante {v['sku']}")
        designation = next((a["values"][value_id]["designation"] for a in sel.values() if value_id in a["values"]), "")
        tiers = [(Decimal(l["unity"]), Decimal(l["value"]))
                 for disc in base["discounts"] if disc.get("class") == "DiscountByQuantity"
                 for l in disc["levels"]]
        yield dict(title=f'{parent["product"]["name"]} — {designation}',
                   url=f'https://www.obras360.pt/{v["segment"]}',
                   price=price, vat_rate=rate, content=base["conversion_factor"],
                   base_unit=parent["product"]["visible_sell_unit"]["description"],
                   stock=v["stock"], tiers=tiers)
```
Os escalões mostram-se como "−2,5% a partir de 90". Em que unidade conta o `unity` (placas ou m²) fica para a Phase 4 [ASSUMED: placas/artigos; 90 placas de 12 mm é plausível para uma palete].

### Folha: cabeçalho por nome nas 10 primeiras linhas
```python
import unicodedata
from openpyxl import load_workbook

def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).casefold().replace(" ", "")

REQUIRED = ("produto", "unidade", "qty")
OPTIONAL = ("familia", "tamanho", "referencia", "notas")

def find_table(path):
    wb = load_workbook(path, data_only=True)        # modo normal: folhas pequenas, linhas certas
    best_missing = set(REQUIRED)
    for ws in wb.worksheets:
        for r, row in enumerate(ws.iter_rows(min_row=1, max_row=10, values_only=True), start=1):
            cols = {norm(v): i for i, v in enumerate(row) if v not in (None, "")}
            missing = set(REQUIRED) - cols.keys()
            if not missing:
                return ws, r, cols
            if len(missing) < len(best_missing): best_missing = missing
    raise SheetError(f"nenhuma folha tem os cabeçalhos: faltam {', '.join(sorted(best_missing))}")
```
Linhas de dados: `enumerate(ws.iter_rows(min_row=r + 1, values_only=True), start=r + 1)`; linha toda vazia → ignorar; Produto vazio → "Produto vazio"; Qty: número (não `bool`) ou texto com vírgula → `Decimal`, > 0, senão "Qty não é um número positivo: X"; Unidade via `UNITS[norm(v)]`, senão "unidade desconhecida: X".

### Modelo (D-05/D-06/D-07)
```python
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

def write_template(path):
    wb = Workbook(); ws = wb.active; ws.title = "Lista"
    ws.append(["Produto", "Família", "Tamanho", "Unidade", "Qty", "Referência", "Notas"])
    ws.append(["OSB 12 mm", "Madeira", "2500x1250x12 mm", "un", 30, None, None])
    ws.append(["cimento", None, None, "saco", 10, None, None])
    dv = DataValidation(type="list", formula1='"un,m²,m,kg,L,saco"', allow_blank=True,
                        showErrorMessage=True, errorTitle="Unidade", error="Escolha da lista: un, m², m, kg, L, saco")
    ws.add_data_validation(dv); dv.add("D2:D1000")
    with open(path, "xb") as f:      # FileExistsError → "modelo.xlsx já existe; não foi alterado"
        wb.save(f)
```
O openpyxl grava e volta a ler `sqref D2:D1000` com `formula1 '"un,m²,m,kg,L,saco"'` [VERIFIED: teste local]. Que o Excel mostre o "²" na lista pendente não foi verificado (não há Excel nesta máquina) [ASSUMED].

### Palavras para D-15 e query alargada D-14
```python
def words(s):            # "12 mm" = "12mm"; plural simples
    s = re.sub(r"(\d)\s+(mm|cm|m|kg|l)\b", r"\1\2", norm_keep_spaces(s))
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in re.findall(r"[a-z0-9,.]+", s)}

def title_matches(query, title): return words(query) <= words(title)

UNIT_TOKENS = {"mm", "cm", "m", "m2", "kg", "g", "l", "lt", "ml", "un", "x"}
def broadened(query):    # "OSB 12mm" → "OSB"; "placa osb 12 mm" → "placa osb"
    keep = [t for t in query.split() if not any(c.isdigit() for c in t) and norm(t) not in UNIT_TOKENS]
    return " ".join(keep) if keep and keep != query.split() else None
```
(`norm_keep_spaces` = `norm` sem tirar os espaços.)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Store API `per_page=0` para "tudo" | `per_page` 1–100 obrigatório; paginar | WooCommerce 10.6 | Usar sempre `per_page=100` + `page` [CITED: developer.woocommerce.com/2026/02/23/restricting-per_page-…] |
| `XlsxWriter` para Excel (STACK.md) | openpyxl para ler e gerar o modelo | Revisão do ROADMAP, 2026-10-22 | Não instalar XlsxWriter nesta fase |
| `selectolax.parser.HTMLParser` (Modest) | `selectolax.lexbor.LexborHTMLParser` | série 1.0 | Usar Lexbor [VERIFIED: import e `css_first` testados hoje] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Prazo de 90 s por (item, loja) chega | Pattern 2 | Lojas marcadas "tempo esgotado" sem razão; afinar com `verificar` |
| A2 | K = 10 pais na Bricomarché apanha o mais barato real | Bricomarché §2 | Um pai com preço de topo desatualizado fica de fora; é visível na contagem "+N" |
| A3 | Expandir no máximo 20 pais na Obras 360 por item | Obras 360 §5 | Variantes baratas de pais não expandidos ficam de fora (contadas) |
| A4 | `product-details/27` é estável | Obras 360 §3 | `verificar` falha; corrigir a constante |
| A5 | Pedido em "saco" = 1 artigo vendido | Pattern 5 | €/saco errado se a loja vender paletes de sacos como artigo |
| A6 | `unity` dos escalões Obras 360 conta artigos (placas) | Code Examples | Só afeta a Phase 4; nesta fase só se mostra o texto |
| A7 | Marcadores de bloqueio Cloudflare/DataDome (`cf-mitigated`, "Just a moment", ...) | Pattern 3 | Um bloqueio aparece como "erro" em vez de "bloqueada" (continua visível) |
| A8 | A consola interativa do Windows já lê UTF-8; o Excel mostra "m²" na lista pendente | Pitfall 8, Modelo | Texto com "²" estragado; testar à mão no fim da fase |
| A9 | Bricomarché inclui IVA (regra B2C, sem rótulo no site) | Pattern 4 | Preços 23% abaixo do real; confirmar à mão um produto numa loja física ou no talão |

## Open Questions

1. **Bricomarché: mais barata absoluta ou mais barata com stock?**
   - O que se sabe: a variação mais barata pode estar "Esgotado"; RES-02 proíbe filtrar.
   - Recomendação: mostrar a mais barata com o stock dela; se estiver esgotada e houver outra loja com stock, acrescentar na mesma oferta "com stock: 19,99 € em Faro". São mais 3 linhas de código; o planner decide se entra.
2. **D-15 deixa tudo escondido: estado "ok" ou "sem resultados"?**
   - Recomendação: o estado reflete a resposta da loja ("ok"), e a linha "+N ofertas escondidas" explica o resto. A D-14 só dispara com zero cru da loja (texto literal da decisão).
3. **Allmat com rótulo "M2" e sem caixa na página (ex.: azulejo 21574 a 5,99 € "M2")**
   - Recomendação: seguir a discrição do CONTEXT (preço por artigo, €/m² desconhecido, fim da lista).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | tudo | ✓ | 3.13.2 | — |
| uv | ambiente, `uv run` | ✓ | 0.12.6 | — |
| Rede para allmat.pt / bricomarche.pt / obras360.pt | adaptadores, `verificar`, `--record` | ✓ (200 nas três hoje) | — | Testes correm sem rede (fixtures) |
| Excel | ver a lista pendente do modelo | ✗ (não verificado nesta máquina) | — | Validar com openpyxl ao reler; teste manual pelo utilizador |
| curl_cffi, openpyxl, selectolax, pytest | código e testes | ✗ no projeto (ainda não há `pyproject.toml`) | — | `uv add` na tarefa 1 |

**Missing dependencies with no fallback:** nenhuma.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 |
| Config file | nenhum — Wave 0 acrescenta `[tool.pytest.ini_options] testpaths = ["tests"]` ao `pyproject.toml` |
| Quick run command | `uv run pytest -q -x` |
| Full suite command | `uv run pytest -q` + `uv run python -m strata verificar` (rede, canário) |

`tests/conftest.py`: `FakeFetcher` com a mesma interface `get/get_json`, que lê `tests/fixtures/<fixture_name(url)>` e falha com o URL em falta (mostra o nome a gravar). Um fixture `autouse` substitui `curl_cffi.requests.AsyncSession.request` por uma função que lança erro, para garantir zero rede nos testes. Fixtures gravadas com `uv run python -m strata pesquisar --record tests/fixtures` (o texto colado é "osb", "cimento", "xyzqwkk"); as amostras em `.planning/phases/01-.../samples/` servem para os testes de parser antes de haver gravação.

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LIST-01 | "OSB 12mm 30 un", "cimento 10 saco", "OSB 12mm" (avisos), "30un", "m²"; leitura até linha vazia | unit | `uv run pytest tests/test_text.py -q` | ❌ Wave 0 |
| LIST-02 | Produto vai tal como escrito; D-14 `broadened()`; D-15 `title_matches()` (aquecimento ≠ cimento) | unit | `uv run pytest tests/test_text.py -q` | ❌ Wave 0 |
| LIST-04 | `modelo` cria o ficheiro com cabeçalhos D-06 e `DataValidation` em D2:D1000; 2.ª vez não sobrescreve | unit (tmp_path) | `uv run pytest tests/test_sheet.py -k modelo -q` | ❌ Wave 0 |
| LIST-05 | Cabeçalho na linha 3, ordem trocada, acentos/maiúsculas, coluna extra; inválidas com linha Excel e motivo; folha sem colunas → erro com as que faltam | unit (xlsx gerado no teste) | `uv run pytest tests/test_sheet.py -q` | ❌ Wave 0 |
| STORE-01 | Variações → mais barata por pai, nome da loja, link `/{loja}/produto/{slug}/`; ignora `price 0` | unit (amostra 47412: mínimo 1849, Coina - Barreiro) | `uv run pytest tests/test_bricomarche.py -q` | ❌ Wave 0 |
| STORE-02 | Cêntimos → € com IVA; "Unid" → €/un; página Splendor → 9,99 €/m², 1.37 m²; `[]` → sem resultados | unit | `uv run pytest tests/test_allmat.py -q` | ❌ Wave 0 |
| STORE-03 | OSB → 7 ofertas (9–30 mm), escalão 12 mm "−2,5% a partir de 90", `total_products 0` → sem resultados, `success false` → erro | unit | `uv run pytest tests/test_obras360.py -q` | ❌ Wave 0 |
| STORE-05 | FakeFetcher a lançar `StoreTimeout`/`StoreBlocked`/JSON inválido → estados certos; as três lojas presentes em cada item | unit | `uv run pytest tests/test_search.py -q` | ❌ Wave 0 |
| STORE-07 | `verificar` sobre fixtures → OK; com fixture adulterada (preço 0, IVA 6%) → FALHOU e código 1 | unit + manual live | `uv run pytest tests/test_search.py -k verificar -q`; `uv run python -m strata verificar` | ❌ Wave 0 |
| PRICE-01 | `excl × 1,23` com `Decimal`; origem por loja; `tax_percentage != 23` → aviso | unit | `uv run pytest tests/test_money.py -q` | ❌ Wave 0 |
| PRICE-02 | Beevo `conversion_factor` (15,02 €/placa ↔ 4,81 €/m²), caixa Allmat, "20KG" → €/kg; não convertível → fim com motivo | unit | `uv run pytest tests/test_money.py -q` | ❌ Wave 0 |
| RES-02 | Texto de stock por loja (Woo texto; Beevo inteiro → "N em stock"/"esgotado") | unit | `uv run pytest tests/test_obras360.py tests/test_bricomarche.py -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest -q -x`
- **Per wave merge:** `uv run pytest -q`
- **Phase gate:** suite completa verde + `uv run python -m strata verificar` com as três lojas OK + uma corrida manual com `modelo.xlsx` preenchido.

### Wave 0 Gaps
- [ ] `pyproject.toml` (uv init --package) + deps + `[tool.pytest.ini_options]`
- [ ] `tests/conftest.py` — FakeFetcher + bloqueio de rede
- [ ] `tests/fixtures/` — copiar/gravar a partir de `samples/` e de `--record`
- [ ] `tests/test_text.py`, `test_sheet.py`, `test_money.py`, `test_allmat.py`, `test_bricomarche.py`, `test_obras360.py`, `test_search.py`

## Security Domain

`security_enforcement: true`, ASVS nível 1.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Sem contas nem chaves nesta fase |
| V3 Session Management | no | Só cookies de sessão do curl_cffi em memória |
| V4 Access Control | no | Ferramenta local de um utilizador |
| V5 Input Validation | yes | Folha e texto: validação por linha (Qty > 0, unidade da lista, Produto não vazio); respostas das lojas: validação de forma (`KeyError` → "erro"), `price > 0`, coerência do IVA |
| V6 Cryptography | no | Só TLS do curl_cffi com `verify=True` (por omissão; nunca desligar) |
| V12 Files | yes | `open(path, "xb")` no modelo; o ficheiro do utilizador só é lido |
| V14 Configuration | yes | Sem segredos; `.gitignore` sem `.env` nesta fase; não registar cabeçalhos/cookies no `--record` (só o corpo) |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Sequências de escape ANSI em títulos de loja impressos no terminal | Tampering | Remover caracteres de controlo (`unicodedata.category(c)[0] == "C"`) antes de imprimir |
| XML malicioso num `.xlsx` (billion laughs) | DoS | Risco baixo (ficheiros do próprio utilizador); o openpyxl usa defusedxml se estiver instalado (`openpyxl/xml/__init__.py:29-42`). Não acrescentar dependência; anotar |
| Resposta enorme ou lenta de uma loja | DoS | Timeout `(10, 30)` + prazo por (item, loja) |
| Preço falso/0,00 € tratado como o mais barato | Tampering (integridade dos dados) | `price > 0`, verificação cruzada do IVA, bloco Allmat ancorado ao preço da API |
| Gravar fixtures com cookies/tokens | Information disclosure | `--record` grava só `r.content` |

## Sources

### Primary (HIGH confidence)
- Sondas ao vivo de hoje (curl_cffi 0.16.3, `impersonate="chrome"`), corpos guardados no rascunho e amostras em `.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/samples/`:
  - `www.obras360.pt/pesquisa?search=osb`, `/api/latest/dot/shop/product-list/f1f5fb06-…` (osb, cimento, tijolo, placa osb, osb 12mm, xyzqwkk; `page`, `items_per_page`), `/api/latest/dot/shop/product-details/27` (pai, filho, id inválido), página de variante
  - `www.bricomarche.pt/wp-json/wc/store/v1/products` (pais osb/cimento; `type=variation` com e sem `orderby=price`; `parent=` em csv, simples e `parent[]`), links `?attribute_pa_loja=` e `/{loja}/produto/{slug}/`, termos e FAQ
  - `allmat.pt/wp-json/wc/store/v1/products` (osb, cimento, azulejo, splendor, pavimento, tinta, parafuso, `type=variable`), páginas de produto 39233, 31800, 21574
- PyPI JSON API (versões, datas, `requires_python`, `project_urls`) de curl_cffi, openpyxl, selectolax, pytest
- Código-fonte instalado: `curl_cffi/requests/models.py:304-311` (`json()` com orjson), `curl_cffi/requests/utils.py:804-825` (timeout), `curl_cffi/requests/session.py:973-1069` (`AsyncSession`, `max_clients`), `openpyxl/xml/__init__.py:29-42` (defusedxml)
- Testes locais: openpyxl `DataValidation` + releitura, `open("xb")`, NFKD, stdin em pipe, `AsyncSession` no `ProactorEventLoop`, `uv init --package`
- `.planning/research/ARCHITECTURE.md`, `PITFALLS.md`, `SUMMARY.md`, `STACK.md` (CLAUDE.md), `01-CONTEXT.md`, `ROADMAP.md`, `REQUIREMENTS.md`

### Secondary (MEDIUM confidence)
- [WooCommerce 10.6: per_page restrito a 1–100 na Store API](https://developer.woocommerce.com/2026/02/23/restricting-per_page-for-product-and-productreview-store-api-requests-in-woocommerce-10-6/)

### Tertiary (LOW confidence)
- Nenhuma usada como base de decisão.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH (versões no PyPI hoje; tudo instalado e exercitado num venv de rascunho)
- Lojas / campos / estados: HIGH (cada campo citado foi lido numa resposta real hoje); limites K/20/90 s: MEDIUM (escolhas de desenho)
- Pitfalls: HIGH nos observados (AND de palavras, preço do pai, chave "convertion", link, bloco Allmat, cp1252); MEDIUM nos marcadores de bloqueio

**Research date:** 2026-10-22
**Valid until:** 2026-11-05 (14 dias: as lojas mudam sem aviso; o `verificar` deteta antes)
