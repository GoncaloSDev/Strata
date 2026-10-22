# Architecture Research

**Domain:** Personal live price-comparison / scraping aggregator (PT construction, DIY, furniture stores)
**Researched:** 2026-10-22
**Confidence:** HIGH for the 4 fixed stores (endpoints were called live and the responses read on 2026-10-22). MEDIUM for the generic architecture (standard aggregator patterns, adapted to this scale). LOW/unverified items are marked inline.

> Confidence note: the `classify-confidence` seam tags `webfetch` as LOW. The store findings below did not come from third-party pages. I called each store's own endpoints (plain `requests` plus a real Chrome over CDP) and read the responses. Treat them as first-hand evidence, valid on the probe date. Sites change, so every adapter needs a canary test (see Pitfalls).

---

## Per-Store Extraction Feasibility (probed 2026-10-22)

| Store | Real URL | Platform | Best extraction method | VAT in primary data | Anti-bot / robots | Confidence |
|---|---|---|---|---|---|---|
| **Obras 360** (user's "Obra360") | `https://www.obras360.pt` (`obra360.pt` has no TLS cert configured: 503 "SSL Error") | **Beevo** (Portuguese SaaS e-commerce; `analytics.beevo.com`, `/beevo/` paths, `Beevo.apiRequest` in JS) | **Internal JSON widget API**: `GET /api/latest/dot/shop/product-list/{widgetId}?search=<q>&_beevo_decoded_params[0][page_id]=241&_beevo_decoded_params[0][segment]=pesquisa` returns JSON with `meta_data.protected.products[]` (12/page, `total_products`). Then per parent product, `GET /api/latest/dot/shop/product-details/27?_beevo_decoded_params[0][product_id]=..&[segment]=..` returns **every variant** (thickness etc.) with prices, SKU, stock and **quantity-discount tiers** (`DiscountByQuantity.levels: [{unity:42, value:2.5}]`) | API has **both**: `final_price_unformatted` (no VAT) and `final_price_with_tax_unformatted`, plus `tax_percentage: 23`. Page shows per-m² **sem IVA** as the headline. **JSON-LD `offers.price` is WITHOUT VAT** (12.21 vs 15.02 with VAT) | None observed (nginx; CloudFront only for assets; reCAPTCHA only on forms). robots.txt disallows `/restfull/`, `/external_apis/`, `/beevo/`, but **not** `/api/` or `/pesquisa` | HIGH |
| **Obramat** | `https://www.obramat.pt` | **ADEO** in-house platform (Leroy Merlin group; `media.adeo.com`, Mirakl-style seller fields `seller_type: 1P`) | **Server-rendered search HTML**: `GET /search?q=<q>`. Each result `<li data-reflm=SKU>` embeds `<script type="application/json" class="dataTms">` with `name, sku, url, offer.unitprice_ati, offer.unitprice_tf, available_deliveries[].stock`. No XHR search API (results are SSR). Product page has the same `dataTms` plus a schema.org `Product` JSON-LD with `gtin` | `unitprice_ati` = with VAT, `unitprice_tf` = without. Page shows **com IVA** headline, sem IVA secondary, and €/m². **JSON-LD price is WITH VAT** (28.5 = ati) | **DataDome** (`x-datadome: protected` header, `captcha-delivery` script) + ADEO bot JS (`bot.cdn.adeo.cloud`). Plain `requests` with a browser UA got 200 on 3 sequential requests. **robots.txt disallows `/search?q=*` and `/pesquisa/`**; product pages `/produtos/*.html` are allowed. Prices are per warehouse context (`contextCode=000` default) | HIGH (extraction), MEDIUM (how long plain HTTP survives DataDome) |
| **Allmat** | `https://allmat.pt` (`www.` redirects there; user-confirmed) | **WordPress + WooCommerce** (Woodmart theme, Elementor, Yoast) | **WooCommerce Store API** (public, no key): `GET /wp-json/wc/store/v1/products?search=<q>&per_page=100` returns `prices.price` in minor units (cents), `is_in_stock`, `stock_availability.text` ("1127 em stock"), `attributes`. Product page JSON-LD `Product/Offer` as fallback | **With VAT** (page: "13,74€ / Caixa IVA incluído"; Store API `1374` matches). **Trap:** Store API `price_html` labels the price "M2", but it is the **per-box** price. Box size ("Produto por caixa: 1.37 m2") is **only in product-page HTML**, not in the Store API | **Cloudflare** (`server: cloudflare`, `__cf_bm` cookie), no challenge at low volume. robots.txt permissive (only `add-to-cart`, `wp-admin`) | HIGH |
| **Bricomarché** | `https://www.bricomarche.pt` | **WordPress + WooCommerce**; each product is a **variable product whose variations are physical stores** (`attribute Loja`, ~65 stores) | **WooCommerce Store API, variation mode**: `GET /wp-json/wc/store/v1/products?search=<q>&type=variation&per_page=100` returns **one row per (product, store)** with `parent`, `variation: "Loja: Coina - Barreiro"`, `prices.price`, stock text. Group by `parent` and take the minimum: one query gives the cheapest store **and its name** (matches user decision). Paginate with `X-WP-TotalPages` ("osb" = 166 rows, 2 pages) | No VAT label anywhere. B2C retail; PT law requires consumer prices to include taxes, so treat as **with VAT** (inferred, not stated on the page). **Trap:** product JSON-LD `price` is the **minimum across all stores** (18.49), not the selected store's price (Beja shows 20.99) | nginx, no WAF observed. Product pages redirect to `/escolher-loja/` until a store cookie (`loja-slug`, `loja-id`) is set. robots.txt disallows `*/?prod=*` and `/?swoof=*`, but **not `/wp-json/`**. **Slow:** ~12 s per 100-variation page | HIGH (API + store-name), MEDIUM (VAT inference) |

**Price spread evidence (Bricomarché "PLACA OSB 12 MM", same SKU):** €18.49 (Coina - Barreiro) to €29.99 (Tondela) across 38 stores. "Cheapest across all stores" changes the answer a lot. The user must be able to see the store name, because he may not be able to buy from a distant store.

**Price-range evidence for pack/tier modelling:**
- Obras360 sells OSB as a parent "Placa OSB 9-30MM" with 7 thickness variants. The list API only shows the cheapest variant's price (9 mm). The adapter **must** expand variants through `product-details`, or every comparison is wrong. Quantity tiers are explicit (e.g. -2.5% at 42 units, roughly one pallet).
- Obramat flags "Melhor Preço quantidade" (quantity pricing). `is_buyable_with_quantity_discount` exists in `dataTms`, but the tier table was not located (**unverified**: needs phase research).
- Allmat sells tiles per box. The m² price has to be derived from box coverage scraped off the product page.
- Allmat does not sell OSB: Store API and HTML search both return 0 results for "osb". This is **"no results", not a failure**, and the status model must keep the two apart.

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│ PRESENTATION   local web UI (list input, live progress, results, export) │
└───────────────┬──────────────────────────────────────────▲───────────────┘
                │ ShoppingList                             │ ResultTable + StoreStatus events
┌───────────────▼──────────────────────────────────────────┴───────────────┐
│ ORCHESTRATOR  (asyncio run: per-item fan-out, deadlines, progress stream)│
└──┬──────────────┬───────────────────┬──────────────────┬─────────────────┘
   │1 ItemSpec    │2 search(spec)     │3 RawOffer[]      │4 NormalizedOffer[]
┌──▼─────────┐ ┌──▼────────────────────────────────┐ ┌───▼──────────┐ ┌─────▼──────┐
│ SPEC PARSER│ │ SOURCE LAYER                      │ │ NORMALIZER   │ │ MATCHER    │
│ (LLM,      │ │ ┌──────────────────────────────┐  │ │ VAT → c/IVA  │ │ rules +    │
│  cached)   │ │ │ Fixed adapters (registry)    │  │ │ unit / pack  │ │ LLM class. │
└────────────┘ │ │ Obras360 · Obramat · Allmat ·│  │ │ tiers        │ │ exact /    │
               │ │ Bricomarché                  │  │ └──────────────┘ │ similar /  │
               │ ├──────────────────────────────┤  │                  │ other+diff │
               │ │ Discovery: search API (PT) → │  │                  └─────┬──────┘
               │ │ generic adapters (Woo Store  │  │                        │5 Match[]
               │ │ API · JSON-LD · LLM page)    │  │                  ┌─────▼──────┐
               │ ├──────────────────────────────┤  │                  │ PACK       │
               │ │ Fallback chain per store     │  │                  │ OPTIMIZER  │
               │ │ api → jsonld → browser → llm │  │                  │ min total  │
               │ └──────────────┬───────────────┘  │                  │ cost ≥ qty │
               └────────────────┼──────────────────┘                  └─────┬──────┘
                                │                                           │6 ItemResult
┌───────────────────────────────▼──────────────────────────────────────────▼─────┐
│ INFRASTRUCTURE  Fetcher (httpx, per-host limiter, retries) · BrowserPool        │
│ (Playwright, lazy) · LLM client (classifier + extractor) · SQLite cache         │
│ (http short-TTL, LLM long-TTL) · config (stores.toml, user store prefs)         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|---|---|---|
| **UI** | Enter list (text area or table: product + qty + unit), show per-store progress live, results per item (exact first, similar apart), export | Local web page served by the same Python process. Progress over SSE/websocket. Exact framework is in STACK.md |
| **Orchestrator** | Turns a list into jobs, fans out item × store, enforces deadlines, collects `StoreStatus`, streams partial results | `asyncio.TaskGroup` + semaphores. One run object holds all state; nothing global |
| **Spec parser** | Free text ("OSB 12mm 2,5x1,25", "mesa jantar 6 pessoas") becomes `ItemSpec` (attributes, target unit, search terms per store) | LLM call with typed output, cached by normalized text. A regex fast path covers dimensions/thickness so it still works without the LLM |
| **Store adapter** (one per fixed store) | `search(spec) → RawOffer[]` with store-specific API knowledge. Optional `enrich(offer)` for variants, tiers and pack size | Plain class implementing a Protocol. Holds **no** VAT or matching logic; it reports what the site says plus evidence |
| **Generic adapters** | Reusable for discovered stores: `WooStoreApiAdapter` (works for Allmat, Bricomarché and any Woo site), `JsonLdAdapter` (any product URL), `LlmPageAdapter` (last resort) | The fixed Woo stores should be thin configs over `WooStoreApiAdapter`, not copies |
| **Discovery** | For each item: shopping/web search restricted to Portugal, then candidate product URLs on non-fixed domains, then platform sniff (Woo? JSON-LD?), then a generic adapter | Search API (Serper/SerpAPI Google Shopping `gl=pt`, or Brave; choice in STACK.md). Remember which domains work so the app can suggest "add as fixed store" |
| **Fetcher** | All HTTP: per-host concurrency and min-interval, timeouts, retries with backoff, block detection (403/429/captcha markers), response cache | `httpx.AsyncClient` (HTTP/2 off by default), one limiter per host |
| **BrowserPool** | Fallback transport for JS-only or bot-protected pages. Runs the **same parsers** on rendered HTML | Playwright Chromium, started lazily on the first fallback, 1-2 contexts max |
| **Normalizer** | `RawOffer → NormalizedOffer`: price incl. VAT 23% with evidence, sell unit, pack contents (m², units, kg), unit price, quantity tiers | Pure functions with a per-store `vat_policy` and unit parsers. Fully unit-testable with fixtures |
| **Matcher** | Classify each offer against `ItemSpec`: exact / similar (with human-readable diff, e.g. "2,44×1,22 m em vez de 2,5×1,25 m") / other | Deterministic numeric comparison first, LLM only for what rules can't decide. Cached |
| **Pack optimizer** | For each matched product family (variants + pack SKUs + quantity tiers), find the minimum total cost covering the requested quantity (buying extra is allowed) | Small exact search (bounded knapsack over ≤ ~5 pack sizes). No solver dependency |
| **Results / Export** | `ItemResult` table sorted by total cost; store failures visible; export xlsx/pdf | openpyxl / a PDF lib (STACK.md) |
| **Cache** | HTTP responses (TTL ~30 min: prices must be live), LLM outputs (long TTL, keyed by content hash + model + prompt version), discovery memory | One SQLite file. No server DB |

---

## Recommended Project Structure

```
strata/
├── app/                 # UI + HTTP routes + export (thin)
│   ├── web.py
│   └── export.py
├── core/                # Pure domain; no network, fully unit-tested
│   ├── models.py        # ItemSpec, RawOffer, NormalizedOffer, Match, ItemResult, StoreStatus
│   ├── normalize.py     # VAT + unit/pack + tiers
│   ├── match_rules.py   # deterministic spec comparison + diff text
│   └── optimize.py      # pack/tier cost minimisation
├── sources/
│   ├── base.py          # StoreAdapter Protocol, registry, fallback runner
│   ├── generic/
│   │   ├── woo_store_api.py   # reused by allmat, bricomarche, discovered Woo sites
│   │   ├── jsonld.py          # schema.org Product/Offer reader
│   │   └── llm_page.py        # last resort
│   ├── stores/
│   │   ├── obras360.py        # Beevo widget API + product-details
│   │   ├── obramat.py         # SSR search HTML dataTms parser
│   │   ├── allmat.py          # Woo config + box-size enrich from product page
│   │   └── bricomarche.py     # Woo config: type=variation, group by parent, min by store
│   └── discovery.py     # search API → candidate URLs → platform sniff
├── infra/
│   ├── fetch.py         # httpx client, per-host limiter, block detection
│   ├── browser.py       # lazy Playwright pool
│   ├── llm.py           # classifier/extractor interface (+ Jev or other impl)
│   └── cache.py         # SQLite
├── orchestrator.py      # run(list) → async stream of events/results
├── stores.toml          # enabled stores, rate limits, VAT policy, per-store prefs
└── tests/
    ├── fixtures/        # saved real responses per store (HTML/JSON)
    └── canary/          # opt-in live tests: one known query per store
```

### Structure Rationale

- **`core/` has no I/O**, so VAT, unit and optimizer logic (where money bugs live) can be tested against saved fixtures without the network.
- **`sources/stores/` holds one file per store.** Adding a store means adding one file plus a `stores.toml` entry. No core change.
- **`sources/generic/` comes first, `stores/` second.** Two of the four fixed stores are WooCommerce, so the Woo adapter covers them and every discovered Woo site.

---

## Architectural Patterns

### Pattern 1: Adapter = parser + declared capabilities; transport is injected

**What:** An adapter knows *what to request and how to parse it*. It never decides *how to fetch* (httpx or browser) or what VAT means. The fallback runner can then re-run the same parser on browser-rendered HTML.
**When to use:** Every store, fixed or discovered.
**Trade-offs:** One extra indirection. In return, the browser fallback is free for any HTML-parsing adapter, and adapters stay ~100 lines.

```python
class StoreAdapter(Protocol):
    store_id: str                      # "obramat"
    vat_policy: VatPolicy              # INCL | EXCL | PER_OFFER (offer carries both)
    methods: tuple[str, ...]           # ordered: ("api", "jsonld", "browser", "llm")

    async def search(self, spec: ItemSpec, method: str, fetch: Fetcher) -> SearchResult: ...
    async def enrich(self, offer: RawOffer, fetch: Fetcher) -> list[RawOffer]: ...  # variants/tiers/pack

@dataclass
class RawOffer:
    store_id: str; url: str; title: str
    price: Decimal; price_vat: Literal["incl", "excl", "unknown"]; vat_evidence: str  # e.g. "api:unitprice_ati"
    price_excl: Decimal | None = None          # when the site gives both, keep both
    sell_unit: str | None = None               # site's own label ("m2/Placa", "Caixa")
    pack_hint: str | None = None               # "3,125 M2", "Produto por caixa: 1.37 m2"
    tiers: list[tuple[int, Decimal]] = ()      # (min_qty, unit price or % off)
    stock_text: str | None = None
    location: str | None = None                # Bricomarché store name, Obramat warehouse
    method: str = "api"                        # which fallback step produced it

@dataclass
class SearchResult:
    status: Literal["ok", "no_results", "blocked", "error", "timeout"]
    offers: list[RawOffer]; detail: str = ""
```

`no_results` is a success: Allmat genuinely has no OSB. Only `blocked | error | timeout` move to the next fallback method.

### Pattern 2: Ordered fallback chain with visible provenance

**What:** For each (item, store), try `methods` in order until one returns `ok` or `no_results`. Record every attempt in `StoreStatus`. Each offer keeps `method`, so the UI can mark "price read by AI, check it".
**When to use:** Fixed stores. Discovered stores start at `jsonld` (or `api` if Woo is sniffed).
**Trade-offs:** Worst case is slow (browser + LLM). Bound it with a per-(item, store) deadline. When the deadline is hit, show "Obramat: timed out after browser attempt" rather than waiting.

```python
async def run_store(adapter, spec, fetch, deadline) -> tuple[SearchResult, list[Attempt]]:
    attempts = []
    for m in adapter.methods:
        try:
            r = await asyncio.wait_for(adapter.search(spec, m, fetch), timeout=deadline.remaining())
        except asyncio.TimeoutError:
            r = SearchResult("timeout", [], m)
        attempts.append(Attempt(m, r.status, r.detail))
        if r.status in ("ok", "no_results"):
            return r, attempts
    return r, attempts   # last failure; UI shows it, never silently dropped
```

### Pattern 3: VAT normalisation is policy + evidence, never a guess

**What:** Each offer carries `price_vat` from the strongest evidence available: (1) explicit API field (`final_price_with_tax_unformatted`, `unitprice_ati`), (2) page label ("IVA incluído", "sem IVA"), (3) the store's declared `vat_policy` in `stores.toml`, (4) for discovered stores with no evidence, `unknown`. `unknown` offers are shown with a warning badge and are **not** ranked as cheapest.
**When to use:** Always. This is the project's critical correctness point.
**Trade-offs:** Some discovered-store offers end up "unknown". That is better than a result that looks 23% cheaper than it is.

Probe results that justify this pattern: **JSON-LD `price` means different things per store.** It is without VAT on Obras360, with VAT on Obramat, the per-box price on Allmat, and the minimum across all stores on Bricomarché. A generic "read JSON-LD price" step is not safe without per-store policy and unit context.

### Pattern 4: LLM as a cached, typed side-car, never in the price path when data exists

**What:** The LLM sits in four places, each behind one `infra/llm.py` interface with typed outputs:

| Use | Input | Output | Cache key | TTL |
|---|---|---|---|---|
| Spec parse | list item text | `ItemSpec` (dims, thickness, unit, terms) | `sha(normalized text + prompt_v)` | long (months) |
| Title → attributes | offer title (+ variant label) | dims, thickness, pack qty/unit | `sha(title + prompt_v)` | long |
| Match classify | `ItemSpec` + offer attributes | exact / similar(diff) / other + confidence | `sha(spec + title + prompt_v)` | long |
| Page extraction (last resort) | cleaned page text | price, VAT label, unit, stock | `sha(url + content_hash)` | short (≤ 30 min: price data) |

**When to use:** Only where rules fail. Run deterministic attribute parsing first (regex for `\d+([,.]\d+)?\s*(mm|cm|m)`, `\d+x\d+`). Call the LLM for leftovers and for the exact/similar decision.
**Trade-offs:** Long-TTL caching makes repeat lists nearly free and deterministic. Bump `prompt_v` to invalidate. Jev (TypeSafe AI) or any other provider plugs in behind the same interface. Do not hard-wire a vendor until it has been evaluated (see STACK/PITFALLS).

### Pattern 5: Search fan-out with per-host politeness

**What:** A global concurrency cap plus a per-host cap and minimum interval, applied inside `Fetcher`, not in adapters.

| Host | Max concurrent | Min interval | Why |
|---|---|---|---|
| obras360.pt | 3 | 0.3 s | No protection seen; 2 calls per item (+1 per parent product) |
| obramat.pt | 1 | 1.5 s + jitter | DataDome: keep request rate low and human-like |
| allmat.pt | 2 | 0.5 s | Cloudflare bot-score cookie |
| bricomarche.pt | 2 | 0.5 s | Store API is slow (~12 s/page), not hostile |
| discovered hosts | 1 | 1 s | Unknown |

Timeouts: connect 10 s, read 30 s (Bricomarché needs > 12 s). Per (item, store) deadline ~60 s across all fallbacks. Whole-run soft budget ~5 min, with results streamed as they arrive.

---

## Data Flow

### Request Flow

```
User list (text/rows: product, qty, unit)
    ↓
Spec parser ──(LLM cache)──→ ItemSpec[]
    ↓  (per item, in parallel)
┌── Fixed adapters × 4 ────────┐   ┌── Discovery ───────────────────────┐
│ search → enrich (variants,   │   │ search API (gl=pt) → URLs on new   │
│ tiers, pack size)            │   │ domains → sniff → generic adapter  │
└──────────────┬───────────────┘   └───────────────┬────────────────────┘
               └──────────────┬────────────────────┘
                              ↓ RawOffer[] + StoreStatus[]
Normalizer (VAT → incl., unit, pack, tiers) → NormalizedOffer[]
    ↓
Matcher (rules → LLM) → exact[] / similar[] (with diff) / other (dropped from table, counted)
    ↓
Pack optimizer (per product family, qty requested) → best purchase plan + total cost
    ↓
ItemResult: rows sorted by total cost incl. VAT, link, stock text, store/location, method badge
    ↓
UI table (live) → Export xlsx/pdf
```

Data flows strictly one way, left to right. Adapters never see match results. The optimizer never calls the network. Enrichment (variant expansion) happens **before** matching, because Obras360's parent row hides the variant you actually want.

### State Management

```
Run (in-memory, one per search)
  items[i].status: pending → searching → normalizing → done
  items[i].stores[s]: StoreStatus{attempts[], final_status, n_offers}
    ↓ events (SSE) to UI
SQLite (persistent): http_cache, llm_cache, discovered_domains(score, last_ok)
```

No price history is stored (out of scope). The HTTP cache TTL is short so a re-run 10 minutes later doesn't hammer stores. Prices are still "live" for a purchase decision.

### Key Data Flows

1. **Bricomarché cheapest-store flow:** one `type=variation&search=q` call (all pages) returns rows per (parent, store). Group by parent, pick the minimum price, keep `location = "Coina - Barreiro"` and its stock text. The other stores' prices are available if the UI later wants a "nearby stores" filter. Store-gated product URLs (`/escolher-loja/?next=`) mean the "buy" link should be the per-store path (`/{store-slug}/produto/...`), or a note telling the user which store to pick.
2. **Obras360 variant flow:** product-list search, then for each candidate parent `product-details` (contains all variants + `DiscountByQuantity` tiers), then one RawOffer per variant. Without this step the 18 mm board would be compared using the 9 mm price.
3. **Allmat box flow:** Store API search (price per box, VAT incl.). For m²-sold items, fetch the product page and parse "Produto por caixa: X m2", then unit price = box price ÷ X. The Store API's "M2" label must be ignored.
4. **Obramat flow:** SSR search HTML, parse each `dataTms` JSON (`unitprice_ati`). Product page only when needed (pack/tier details). If blocked by DataDome: browser fallback on the same URL, then the same parser.
5. **Discovery flow:** search API results on non-fixed domains, then fetch the product page. If `/wp-json/wc/store/v1` responds, use the Woo adapter. Otherwise JSON-LD `Product/Offer`, otherwise LLM page extraction. Domains that succeed repeatedly get suggested as fixed stores (requirement).

---

## Scaling Considerations

Single user, single PC. "Scale" here means **list size × stores × politeness**, not users.

| Scale | Architecture Adjustments |
|---|---|
| 10 items × 4 fixed stores (target) | ~40 searches + ~30 enrich calls + Bricomarché pagination. With the caps above, expect **1.5-3 min**, bounded mainly by Bricomarché (~12 s/page) and Obramat's 1.5 s interval. Fine |
| 10 items × 4 fixed + ~5 discovered/item | +50 page fetches on unknown hosts + LLM calls. Still minutes if discovery runs in parallel with fixed stores and is capped at N URLs/item |
| 30+ items | Run-level budget becomes the limit. Stream results, let the user stop early, rely on the HTTP cache for re-runs |

### Scaling Priorities

1. **First bottleneck: Bricomarché Store API latency** (~12 s per 100 variation rows, 2+ pages per query). Fix: request pages in parallel (2 concurrent), and test whether `orderby=price&order=asc` works with `type=variation`. If it does, page 1 alone holds the cheapest stores (**unverified**).
2. **Second bottleneck: Obramat rate under DataDome.** Fix: low rate and cache. If blocked, the browser fallback reuses the real Chrome profile's cookies. Last resort: discovery-style lookup of Obramat product pages (allowed by robots) instead of `/search`.
3. **Third: LLM latency on the match step.** Fix: rules first, batch the remaining offers per item into one call, cache aggressively.

---

## Anti-Patterns

### Anti-Pattern 1: Trusting JSON-LD `price` as "the price"

**What people do:** A generic schema.org reader is used for every store, taking `offers.price` as a comparable number.
**Why it's wrong:** Proven on the probe date. On Obras360 it is **without VAT** (12.21 vs 15.02). On Allmat it is **per box**, not per m². On Bricomarché it is the **minimum across 65 stores**, not any specific store. The "cheapest" ranking would be wrong by 20-60%.
**Do this instead:** Prefer each store's structured API fields that state VAT explicitly. Treat JSON-LD as a fallback that inherits the store's `vat_policy` and unit context, and mark `price_vat="unknown"` when nothing confirms it.

### Anti-Pattern 2: Comparing the parent/list row instead of the variant

**What people do:** Take the first price shown in search results.
**Why it's wrong:** Obras360's list row "Placa OSB 9-30MM" shows the 9 mm price. Bricomarché's parent shows a price range. Woo variable products expose `price_range`.
**Do this instead:** An `enrich()` step expands variants before matching. Matching is done per variant.

### Anti-Pattern 3: One "failed" bucket

**What people do:** Treat empty results, timeouts and blocks the same way.
**Why it's wrong:** "Allmat doesn't sell OSB" is information. "Obramat blocked us" means a possibly cheaper price is missing, which the requirements say must be visible.
**Do this instead:** Use `SearchResult.status` ∈ {ok, no_results, blocked, error, timeout}, show per-store status per item, and only escalate the fallback chain on real failures.

### Anti-Pattern 4: LLM in the hot path for everything

**What people do:** Send every page to an LLM to "extract price".
**Why it's wrong:** It is slow, costs money, can hallucinate prices, and isn't needed for the 4 fixed stores (all have structured data).
**Do this instead:** LLM for spec parsing and match classification (cached). Page extraction only as the last fallback, with a visible "AI-read" badge.

### Anti-Pattern 5: Hard-coding Beevo widget IDs and Woo quirks in core

**What people do:** Paste `f1f5fb06-…` into the code and forget it.
**Why it's wrong:** The widget instance ID is page configuration. A site redesign changes it silently.
**Do this instead:** The Obras360 adapter reads the `ProductList` widget ID from the `/pesquisa?search=` page's widget config JSON (verified present there) and caches it per day. A canary test fails loudly when it moves.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---|---|---|
| Obras360 Beevo API | `GET /api/latest/dot/shop/product-list/{widgetId}` + `product-details/27` | JSON under `meta_data.protected`. Both prices given. `tax_percentage` present. Stock per variant. `availability_days_message` gives lead time |
| Obramat | `GET /search?q=` HTML, parse `script.dataTms` | Breaks if ADEO changes the datalayer. Fixture tests needed. robots disallows `/search?q=*`: user's call (personal, low volume) |
| Allmat / Bricomarché | WooCommerce Store API v1 (`/wp-json/wc/store/v1/products`) | Public, no auth. Prices in minor units (`currency_minor_unit: 2`). Standard across Woo sites, so very reusable |
| Search API (discovery) | REST, `gl=pt`, `hl=pt` | Provider choice in STACK.md. Filter out the 4 fixed domains and marketplaces as configured |
| LLM | Typed classify/extract calls | Behind `infra/llm.py`. Cache in SQLite |
| Playwright | Lazy-started Chromium | Only when a fallback needs it. Real-Chrome-over-CDP is an option for DataDome cases |

### Internal Boundaries

| Boundary | Communication | Notes |
|---|---|---|
| orchestrator ↔ adapters | direct async calls through `run_store` | Adapters get a `Fetcher`. They never construct HTTP clients |
| adapters ↔ normalizer | `RawOffer` dataclasses | Adapters pass raw evidence (labels, units), never computed VAT |
| normalizer/matcher/optimizer | pure functions on dataclasses | No I/O except matcher → `llm` (cached) |
| orchestrator ↔ UI | event stream (item/store status, result rows) | UI renders partial results as they arrive |

---

## Suggested Build Order

Dependencies drive the order. Each phase leaves a runnable tool.

1. **Walking skeleton (core models + Woo Store API adapter + VAT/unit normaliser + CLI/basic table).** Allmat and Bricomarché both run on one generic adapter, so two of the four stores come almost free. This proves the `RawOffer → NormalizedOffer` contract, the status model and the Bricomarché cheapest-store grouping early.
2. **Obras360 + Obramat adapters with variant enrichment and the fallback runner (api → jsonld → browser).** These need store-specific parsing and are where the VAT traps live. Build fixture tests from saved responses.
3. **Spec parsing + matching (rules, then LLM, with cache).** It needs real offers from phases 1-2 to tune against. This is where the exact/similar split and diff text come from.
4. **Pack/tier optimiser.** It depends on adapters exposing pack size and tiers (Obras360 `DiscountByQuantity`, Allmat box m², Obramat quantity pricing, which still needs research).
5. **Discovery + generic JSON-LD/LLM-page adapters + "suggest as fixed store".** It depends on the generic adapters and the VAT `unknown` handling being solid, because discovered stores are the riskiest data.
6. **UI polish + live progress + xlsx/pdf export.** The UI can start as a simple table in phase 1. Export is last because it just serialises `ItemResult`.

Research flags: phase 2 (Obramat tier table, DataDome tolerance over a 10-item run), phase 4 (Obramat quantity-discount data source), phase 5 (search-API coverage of PT shops).

---

## Sources

- Live probes on 2026-10-22 (plain `requests` + Chrome over CDP). Endpoints:
  - `https://www.obras360.pt/pesquisa?search=osb`, `/api/latest/dot/shop/product-list/f1f5fb06-…?search=osb`, `/api/latest/dot/shop/product-details/27?...`, product page JSON-LD, `/robots.txt`
  - `https://www.obramat.pt/search?q=osb`, `/produtos/placa-osb-3-250x125x1-8cm-25134518.html`, `/robots.txt` (response header `x-datadome: protected`)
  - `https://allmat.pt/wp-json/wc/store/v1/products?search=…`, `/produto/16083-splendor-s-decor-m25x550-8-fundo-white-cloud-p/`, `/robots.txt`
  - `https://www.bricomarche.pt/wp-json/wc/store/v1/products?search=osb&type=variation&per_page=100`, `/products/{variationId}`, `/beja/produto/madeiras/madeiras-e-derivados-a-corte/plc-osb-lisa-2-50x1-25-12mm/` (cookie `loja-slug=beja`), `/robots.txt`
  - `https://obra360.pt` returns 503 "There is no SSL certificate configured for this domain" (not the store)
- Identification of Obras 360 / Sotecnisol: [Portal da Queixa – Obras 360](https://portaldaqueixa.com/brands/obras-360o/complaints/obras-360-caixas-de-visita-142442125) (LOW, used only to find the domain, which was then confirmed live)
- WooCommerce Store API v1 (public products endpoint): standard WooCommerce core, behaviour confirmed by the live calls above

---
*Architecture research for: PT live price-comparison aggregator (construction/DIY/furniture)*
*Researched: 2026-10-22*
