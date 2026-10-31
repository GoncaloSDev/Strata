# Phase 2: Obramat e cadeia de recurso - Research

**Researched:** 2026-10-30
**Domain:** recolha de preços com anti-bot (DataDome), cadeia de recurso por loja (principal → JSON-LD → browser → IA), Chrome dedicado por CDP, extração estruturada com Claude
**Confidence:** HIGH na Obramat (medido ao vivo hoje); MEDIUM no degrau browser para as lojas de API e no degrau IA (desenho verificado em documentação, não corrido ponta a ponta)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

As decisões D-01 a D-16 da fase 1 (`.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-CONTEXT.md`) continuam em vigor; aqui chamam-se "fase 1 D-xx". As desta fase numeram-se de novo.

#### Preço da Obramat por loja física
- **D-01:** A oferta da Obramat é a da loja física (armazém) mais barata **com stock**, com o nome dessa loja em `Offer.location`; se nenhuma tiver stock, a mais barata com o stock dela; uma loja mais barata sem stock fica na nota "mais barata sem stock: X em Y". É a mesma regra da Bricomarché (G-01-3, `01-10`). O `contextCode=000` é o preço nacional, não o de uma loja.
- **D-02:** Entram todas as lojas Obramat do país, sem lista configurada pelo utilizador, como na Bricomarché.
- **D-03:** Se a pesquisa da fase mostrar que o preço por loja física só se obtém com muitos pedidos por produto ou só pelo browser, **o planeamento para e pergunta de novo ao utilizador**, com os números medidos (pedidos por item, segundos, sinais do DataDome). Não escolher sozinho entre o preço nacional e o preço por loja.
- **D-04:** Os escalões "Melhor preço por quantidade" da Obramat, se a pesquisa os encontrar, vão para `Offer.tiers` e aparecem na oferta, como os da Obras 360 (fase 1 D-16). Aplicá-los ao custo total é da Phase 4. O preço guardado é com IVA (`unitprice_ati`); quando a página traz os dois preços, confirmar que `com IVA / sem IVA ≈ 1,23` e tratar como erro se não bater (PITFALLS §Pitfall 1).

#### Bloqueio e browser
- **D-05:** O degrau browser usa o **Chrome dedicado do Claude** (perfil `%USERPROFILE%\.claude-chrome`, porta 9222, `.claude\claude-chrome.cmd`), **com janela visível** e os cookies guardados no perfil. Nunca headless, nunca o Chrome do utilizador.
- **D-06:** Se o Chrome dedicado não estiver a correr quando o browser é preciso, a app abre-o e, no fim da execução, fecha-o se foi ela a abri-lo. Se já estava aberto, fica aberto.
- **D-07:** Ao primeiro **CAPTCHA** na Obramat, a loja fica "abrir à mão" nesse item e em **todos os itens seguintes da execução**, com o link da pesquisa na loja (ex.: `https://www.obramat.pt/search?q=<produto>`). Não se volta a pedir nada à Obramat nessa execução; as outras 3 lojas continuam. A app nunca resolve nem espera por um CAPTCHA. O mesmo vale para um CAPTCHA noutra loja fixa.
- **D-08:** Depois de um bloqueio sem CAPTCHA (ex.: 403 do DataDome) que o browser resolve, essa loja **fica no browser até ao fim da execução**; não volta a tentar o pedido simples nos itens seguintes.

#### Preços lidos por IA (último degrau)
- **D-09:** Uma oferta lida por IA aparece com a marca "lido por IA", mas fica **sempre depois** das ofertas lidas de dados estruturados (API, JSON-LD, HTML do browser), mesmo que seja mais barata. Nunca é a primeira da loja.
- **D-10:** No máximo **1 chamada de IA por (item, loja)**, com o texto da página cortado. Sem contador em euros.
- **D-11:** A IA lê a página de pesquisa da loja e devolve **até 5 ofertas** (título, preço, link de cada, tirados da página). Passam pelo mesmo filtro de título que as outras (fase 1 D-15) e o IVA segue a regra conhecida da loja fixa.
- **D-12:** Motor da IA: se houver `ANTHROPIC_API_KEY`, usa a API (Claude Haiku 5.5, saída estruturada); se não houver, usa o **Claude Code como subprocesso** (`claude -p --model haiku --output-format json --json-schema …`), que corre com a conta Claude Pro do utilizador. Se nenhum estiver disponível, o degrau salta e o motivo fica visível (ex.: "IA não configurada"). **Nunca** reaproveitar o token OAuth da conta Pro fora do Claude Code (o que fazem agentes como o Hermes): vai contra os termos da Anthropic. — **Reversibility:** reversible — o motor está atrás de uma função; trocar ou retirar o `claude -p` é local.

#### Quando escalar a cadeia
- **D-13:** A cadeia (principal → JSON-LD → browser → IA) corre para **as 4 lojas fixas**, não só para a Obramat.
- **D-14:** Escalam: `bloqueada`, `erro` e `tempo esgotado`. `sem resultados` é uma resposta válida e **não** escala (a Allmat não vende OSB). Zero ofertas mostradas pelo filtro de título também não escala.
- **D-15:** Os degraus de um (item, loja) **partilham o prazo de 90 s** que já existe (`DEADLINE_S`); o recurso usa o que sobrar. Se o prazo acabar a meio da cadeia, o estado diz até onde chegou (ex.: "tempo esgotado depois do browser").
- **D-16:** Cada oferta mostra o método que a produziu (API / JSON-LD / browser / IA). Se todos os degraus falharem, a loja aparece falhada com o motivo de cada degrau tentado.
- **D-17:** Uma opção de desenvolvimento no comando força a falha do método principal de uma loja (ex.: `--sem-principal obramat`), para ver o recurso ao vivo, como o `--record` da fase 1. Os testes com fixtures provam o mesmo sem rede.

### Claude's Discretion
- Quantos produtos da Obramat são vistos loja física a loja física (corte K): o utilizador deixou para depois de medir tempo e bloqueios ao vivo na pesquisa da fase. Ponto de partida: o mesmo padrão K da Bricomarché.
- Ritmo da Obramat (intervalo entre pedidos, com jitter) dentro de "um pedido de cada vez"; entrada em `LIMITS` do `fetch.py`.
- Como detetar CAPTCHA vs bloqueio simples (cabeçalhos `x-datadome`, `captcha-delivery`, conteúdo da página).
- Tamanho do corte de texto para a IA e o esquema de saída estruturada.
- Nome exato da opção de D-17 e o canário da Obramat na verificação das lojas.
- Como o browser se liga ao Chrome dedicado (CDP na porta 9222 via Playwright `connect_over_cdp`, ou outro) e como corre os mesmos parsers sobre o HTML que recebe.

### Deferred Ideas (OUT OF SCOPE)
- Usar o `claude -p` (conta Pro) também na extração de especificações e na classificação exato/parecido — decidir na Phase 3, com medição de tempo e de consumo do limite.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| STORE-04 | Utilizador obtém preços na hora da Obramat através da pesquisa direta do site, a ritmo lento (um pedido de cada vez) | §Achados ao vivo (Obramat), §Padrão 3 (adaptador Obramat), §Código: `parse_search`, `parse_tiers`; amostras gravadas em `samples/` |
| STORE-06 | Quando o método principal de uma loja falha, a app tenta JSON-LD, browser automático e IA antes de marcar a falha, e mostra que método funcionou | §Padrão 1 (cadeia em `search_store`), §Padrão 2 (`BrowserFetcher` com a interface do `Fetcher`), §Padrão 4 (JSON-LD), §Padrão 5 (IA), `Offer.method` |
| LIST-03 | Uma lista de 10 itens fica resolvida nas 4 lojas fixas em menos de 5 minutos | §Orçamento de tempo (medições), corte de páginas de produto da Obramat, prazo partilhado de 90 s; verificação final ao vivo |
</phase_requirements>

## Summary

A pesquisa ao vivo mudou três pressupostos do CONTEXT. **Primeiro: hoje o `curl_cffi` com `impersonate="chrome"` leva 403 do DataDome logo no primeiro pedido** à Obramat (pesquisa, página inicial e página de produto, 3 de 3, sem cookies). O corpo é um "interstitial" de verificação do dispositivo (`'rt':'i'`), não um CAPTCHA. No Chrome dedicado (janela visível, perfil próprio) a mesma pesquisa abriu à primeira e **21 páginas seguidas, a 4–10 s umas das outras, passaram sem nenhum CAPTCHA** (o próprio site marca a sessão como `"cdl_environment_bot","value":"Humans"`). Na prática, o degrau browser é o caminho da Obramat; o D-08 já cobre isto (depois do 1.º item fica no browser).

**Segundo: a Obramat Portugal tem um só armazém**, "OBRAMAT Lisboa - Alfragide" (código de contexto `201`). A janela "Escolha o seu Armazém" do site lista só esse, e as notícias confirmam que é a única loja aberta. O preço do `contextCode=000` (sem armazém escolhido) é **igual** ao do armazém 201 nos 8 produtos comparados. O D-01 fica trivial: a oferta é sempre de Alfragide e o preço vem da página de pesquisa, sem pedidos extra. **Mas o D-03 pede que o planeamento pare e pergunte** quando a Obramat "só se obtém pelo browser", e é o caso. Ver Open Question 1, com os números.

**Terceiro: os escalões existem, mas só aparecem na página de produto e só com o armazém escolhido.** A tabela é "Palete (N unidades)" com um preço por unidade e o total da palete: OSB 18 mm, 48 un a 27,08 €/un (1 299,60 €); tijolo 30×20×11, 270 un a 0,32 €/un (87,21 €). Nos dois casos o desconto é exatamente −5%. O stock exato ("327 em stock em OBRAMAT Lisboa - Alfragide") também só está na página de produto. O armazém escolhido fica num cookie `customer_context` do perfil dedicado, válido até 2027-11-29, que ficou gravado durante esta pesquisa.

Para a cadeia nas 4 lojas, o achado que conta é este: **nenhuma das 4 páginas de pesquisa tem JSON-LD de produto**. A Bricomarché e a Obras 360 montam a página de pesquisa com JavaScript (o HTML do servidor não tem links de produto). Só a Allmat (e a Obramat, quando o pedido passa) têm links de produto no HTML. O degrau JSON-LD só é real onde há links. Nas outras lojas falha depressa, com um motivo visível.

**Recomendação principal:** cada degrau tem a mesma assinatura que já existe, `search(query, fetch, rank=None) -> Found`. O degrau browser é **o mesmo `store.search`** a correr com um `BrowserFetcher` (mesma interface `get_json`/`get_html`/`cache` do `Fetcher`, mas cada pedido é uma navegação no Chrome dedicado por CDP). A cadeia vive em `search_store`, à volta do corpo que já existe. O estado da execução (D-07, D-08) fica em `fetch.cache`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cadeia de recurso, prazo de 90 s, estado por loja | Orquestração (`search.py`) | — | `search_store` já é "o único sítio onde uma falha vira estado" |
| Pedidos HTTP com ritmo por host | Cliente HTTP (`fetch.py`) | — | `Fetcher` + `Host` já fazem semáforo e intervalo |
| Navegação no Chrome dedicado, arranque/fecho do Chrome | Cliente browser (novo `browser.py`) | Chrome externo (CDP 9222) | Mesma interface do `Fetcher`, para os adaptadores não mudarem |
| Leitura da pesquisa e dos escalões da Obramat | Adaptador (`stores/obramat.py`) | — | Parsers puros, testados com fixtures |
| JSON-LD genérico de páginas de produto | Novo `jsonld.py` | Adaptadores (constantes de URL e regra de IVA) | Um leitor genérico; a política de IVA é por loja (Pattern 3 do ARCHITECTURE) |
| Leitura por IA (Haiku 5.5 ou `claude -p`) | Novo `ai.py` | API Anthropic / Claude Code (externo) | Um só ponto para trocar o motor (D-12 reversível) |
| Mostrar método, "lido por IA", "abrir à mão" | Saída no terminal (`report.py`) | — | A UI só chega na Phase 5 |

## Achados ao vivo (Obramat, 2026-10-30)

Todos os pedidos foram feitos um de cada vez, a 4–10 s de intervalo. Total: 3 pedidos `curl_cffi` à Obramat (e mais 2 tentativas que o classificador de permissões bloqueou antes de saírem, ver Assumption A1) e 21 navegações no Chrome dedicado.

| Medição | Valor | Fonte |
|---|---|---|
| `curl_cffi` `impersonate="chrome"`, `/search?q=osb`, `/` e página de produto | **403** nos 3; `server: DataDome`, `x-datadome: protected`, `x-datadome-riskscore` 0,55 e 0,39; corpo de 773 bytes com `var dd={'rt':'i',…,'host':'geo.captcha-delivery.com',…}` | [VERIFIED: probe ao vivo; amostra `samples/obramat_curl-403-datadome.html`] |
| Chrome dedicado, 1.ª pesquisa (perfil sem cookies da Obramat) | carregou os resultados em 3,4 s; o "interstitial" correu sozinho no browser | [VERIFIED: probe ao vivo] |
| Chrome dedicado, pesquisas seguintes | 1,7–1,8 s por página (uma de 10,3 s); 0 CAPTCHA em 21 navegações; `"cdl_environment_bot","value":"Humans"` | [VERIFIED: probe ao vivo] |
| Armazéns em Portugal | 1: "OBRAMAT Lisboa - Alfragide", Rua Quinta do Paizinho nº 13, 2790-236 Carnaxide; contexto `201` | [VERIFIED: janela "Todos os Armazéns OBRAMAT" no site; CITED: notícias, ver Sources] |
| Preço 000 vs 201 | igual nos 7 produtos da pesquisa "osb" e na página do OSB 18 mm (28,50 €) | [VERIFIED: probe ao vivo] |
| Rácio IVA (`unitprice_ati / unitprice_tf`) | 1,2297–1,2304 em todos os produtos de 3 pesquisas (18+18+7) | [VERIFIED: probe ao vivo] |
| Produtos por página de pesquisa | 18 com preço no HTML; os outros 30 da página chegam por pedidos `/lazy/…?ktx=<token opaco>` ao fazer scroll; paginação `&p=2` | [VERIFIED: probe ao vivo] |
| Escalões | só na página de produto **com armazém escolhido**; bloco `.o-priceByQuantity__tileItem` | [VERIFIED: `samples/obramat_product-osb-18_ctx201_tiers.html`, `…tijolo…`] |

### Onde estão os dados na página de pesquisa

- Lista de resultados: `ol#guidance-product-list > li[data-reflm]`. O **primeiro** `li` traz um `<script type="application/json" class="dataTms">` com a lista inteira dos produtos com preço, no elemento `cdl_products_list`. [VERIFIED: amostras de pesquisa]
- Campos de cada produto (pesquisa "osb", verbatim): `"name": "PLACA OSB 3 250X125X1,8CM"`, `"sku":"25134518"`, `"url":"/produtos/placa-osb-3-250x125x1-8cm-25134518.html"`, `"offer":{… "seller_type":"1P","unitprice_ati":28.5,"unitprice_tf":23.17}`, `"commercial_animations":{"id":"151","label":"Melhor Preço quantidade"}`. [VERIFIED: `samples/obramat_search-osb_browser.html`]
- Total de resultados e tipo de página: noutro `dataTms`, `"cdl_page_type","value":"Search"`, `"cdl_search","value":{… "ise_number_result":"7" …}`, `"cdl_page_number","value":"1_1"`. Sem resultados: `"ise_number_result":"0"` e `"cdl_page_name","value":"0 result search page"`. [VERIFIED: amostras]
- Armazém da sessão: `"cdl_user_context_main_store","value":"201"` com armazém escolhido; `"no cookie here"` sem ele. [VERIFIED: amostras]
- **Armadilha 1:** todas as páginas (incluindo a de zero resultados) têm um carrossel "vistos recentemente" (`data-testid="ITEM_RECOMMENDED_ZSERPLSP_HISTORY_PRODUCTS"`) com o seu próprio `cdl_products_list`. Na amostra sem resultados ele traz a placa OSB vista antes. Ler o primeiro `cdl_products_list` da página dá resultados falsos. [VERIFIED: `samples/obramat_search-no-results_browser.html`]
- **Armadilha 2:** a pesquisa "cimento cola" tem um bloco promocional ("endcap") **dentro** do `ol#guidance-product-list`, num `li.push-highlight-digital-endcap-container` com `li[data-reflm]` e `dataTms` próprios (4 produtos). Usar o seletor de filho direto `>`. [VERIFIED: `samples/obramat_search-cimento-cola_endcap_browser.html`]

### Onde estão os escalões e o stock (página de produto, armazém 201)

- Cada opção de quantidade é um `.o-priceByQuantity__tileItem`. Rótulo: `.o-priceByQuantity__label` ("unidade" / "Palete (48 unidades)"). Quantidade: `input[value]` (`value="48"`). Preços em `.kl-hidden-accessibility`, verbatim: `'Vendido 27,08 € IVA', 'Ou Vendido 1 299,60 € IVA', 'Vendido 22,01 € sem IVA', 'Ou Vendido 1 056,59 € sem IVA'`. [VERIFIED: `samples/obramat_product-osb-18_ctx201_tiers.html`]
- Tijolo: `'Vendido 0,32 € IVA', 'Ou Vendido 87,21 € IVA'` com `value="270"`. **O preço por unidade do escalão é arredondado** (87,21 / 270 = 0,323): o desconto tem de vir do total da palete, nunca do 0,32. [VERIFIED: `samples/obramat_product-tijolo_ctx201_tiers.html`]
- Stock: `"available_deliveries":[{"price":0.0,"stock":327,"stockStatus":"ONSITE","time":"2 HOUR","type":"storeDelivery"},…]` e o texto "327 em stock em OBRAMAT Lisboa - Alfragide". Sem armazém escolhido o mesmo campo traz `"stock":1` (só um sinal) e o texto "Ver disponibilidade em Armazém". [VERIFIED: amostras de produto com e sem contexto]
- JSON-LD `Product` da página de produto: `"price" : "28.5"` (= `unitprice_ati`, com IVA), `"gtin" : "5600784046086"`, `"availability" : "http://schema.org/InStock"`. [VERIFIED: probe ao vivo]
- A página de pesquisa **não** tem JSON-LD de produto (só `Organization` e `WebSite`). [VERIFIED: probe ao vivo]

### JSON-LD nas páginas de pesquisa das outras 3 lojas (curl_cffi, 1 pedido cada)

| Loja | URL da pesquisa para pessoas | Estado | JSON-LD de produto | Links de produto no HTML |
|---|---|---|---|---|
| Allmat | `https://allmat.pt/?s=cimento&post_type=product` | 200, 5,2 s | 0 | sim: `https://allmat.pt/produto/<slug>/` (36 na amostra) |
| Bricomarché | `https://www.bricomarche.pt/?s=cimento&post_type=product` | 200, 1,1 s | 0 | não (página montada com JS) |
| Obras 360 | `https://www.obras360.pt/pesquisa?search=osb` | 200, 0,6 s | 0 | não (Beevo, montada com JS) |

[VERIFIED: probe ao vivo]

## Standard Stack

### Core (já no projeto)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| curl_cffi | 0.16.3 (instalado) | Degrau principal e JSON-LD | Já é o único cliente HTTP [VERIFIED: `uv pip list`] |
| selectolax | 1.0.2 (instalado) | Parsers da Obramat e leitor JSON-LD | Já usado na Allmat (`LexborHTMLParser`) [VERIFIED: `uv pip list`] |

### A acrescentar
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| playwright | 1.64.1 (PyPI, `requires_python >=3.10`, roda `win_amd64`) | `connect_over_cdp("http://127.0.0.1:9222")` ao Chrome dedicado | Degrau browser. Ligado por CDP não descarrega browsers (sem `playwright install`) [VERIFIED: PyPI JSON; CITED: playwright.dev/python/docs/api/class-browsertype] |
| anthropic | 2.3.0 (PyPI, `>=3.10`) | Degrau IA com `ANTHROPIC_API_KEY` | Só no degrau IA; o STACK.md diz 2.1.0, o PyPI tem 2.3.0 hoje [VERIFIED: PyPI JSON] |

`pydantic` não precisa de entrar à parte: chega como dependência do `anthropic`, e a recomendação abaixo usa um esquema JSON simples, partilhado pelos dois motores.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Playwright `connect_over_cdp` | CDP à mão sobre o WebSocket do `curl_cffi` | Zero dependências, mas obriga a gerir sessões, eventos de carga e `Network.getResponseBody` à mão. Não compensa. |
| `messages.parse(output_format=Modelo)` | `messages.create(output_config={"format": {"type":"json_schema","schema": SCHEMA}, "effort": "low"})` | Recomendado o `create`: o mesmo `SCHEMA` serve o `claude -p --json-schema`, e não há dúvida sobre misturar `output_format` com `output_config.effort` no `parse` |
| `patchright` | — | Não é preciso: o Chrome real com janela passou o DataDome sem ajuda |

**Installation:**
```bash
uv add "playwright>=1.64,<1.65" "anthropic>=2.3,<3"
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| playwright | PyPI | última versão de 2026-10-22 (pacote com anos) | desconhecido na ferramenta | o seam não leu o repo (é github.com/microsoft/playwright-python) | [SUS: too-new, unknown-downloads, no-repository] | Flagged — planner must add checkpoint |
| anthropic | PyPI | última versão de 2026-10-23 | desconhecido | github.com/anthropics/anthropic-sdk-python | [SUS: too-new, unknown-downloads] | Flagged — planner must add checkpoint |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** `playwright` [WARNING: flagged as suspicious — verify before using.], `anthropic` [WARNING: flagged as suspicious — verify before using.]. O motivo "too-new" vem da data da última versão, não da idade do pacote; os dois estão no STACK.md do projeto. Mesmo assim o protocolo pede um `checkpoint:human-verify` antes do `uv add`. PyPI não tem `postinstall`.

## Architecture Patterns

### System Architecture Diagram

```
folha / texto ──> run(items) ── um item de cada vez ──> por loja, em paralelo:
                                                          │
                     search_store(store, item, fetch) ────┤ prazo único de 90 s (D-15)
                                                          │
   fetch.cache["captcha"] tem a loja? ──sim──> estado "abrir à mão" + link (D-07), fim
                                                          │ não
   fetch.cache["browser_only"] tem a loja? ──sim──> salta para o degrau browser (D-08)
                                                          │ não
   ┌─ degrau 1 "API"     store.search(q, fetch)           (curl_cffi; corpo atual + pesquisa alargada)
   │      ok / sem resultados ─────────────────────────────────────> StoreResult (method="API")
   │      bloqueada / erro / tempo ─> anota motivo, segue
   ├─ degrau 2 "JSON-LD" jsonld.search(store)(q, fetch)    (página de pesquisa HTML → links → páginas de produto)
   │      sem links de produto ─> motivo "página montada com JavaScript", segue
   ├─ degrau 3 "browser" store.search(q, BrowserFetcher)   (mesmo adaptador; cada pedido = navegação no Chrome 9222)
   │      ok ─> fetch.cache["browser_only"].add(loja) (D-08)
   └─ degrau 4 "IA"      ai.search(store)(q, fetch)        (texto da página de pesquisa → Haiku 5.5 ou claude -p, ≤5 ofertas)
          │
   StoreCaptcha em qualquer degrau ──> fetch.cache["captcha"].add(loja); "abrir à mão" (D-07)
   todos falham ──> "bloqueada"/"erro" com o motivo de cada degrau (D-16)
   tempo esgotado a meio ──> "tempo esgotado depois do <degrau>" (D-15)
```

### Estrutura (ficheiros novos e tocados)
```
src/strata/
├── fetch.py          # + LIMITS da Obramat, + StoreCaptcha, + deteção do 'rt':'c' no corpo do 403
├── browser.py        # NOVO: BrowserFetcher (get_json/get_html/cache) + abrir/fechar o Chrome (D-06)
├── jsonld.py         # NOVO: leitor genérico de Product JSON-LD + degrau JSON-LD
├── ai.py             # NOVO: degrau IA, um esquema, dois motores (API / claude -p)
├── search.py         # cadeia em search_store; STORES e CANARIES com a Obramat
├── models.py         # Offer.method; Status + "abrir à mão"; StoreResult.link
├── report.py         # método por oferta, "lido por IA", "abrir à mão" com link
├── __main__.py       # --sem-principal LOJA em pesquisar e verificar (D-17)
└── stores/obramat.py # NOVO: parse_search, parse_tiers, search
tests/
├── fixtures/obramat_*.html   # a partir de .planning/phases/02-…/samples/
├── test_obramat.py           # NOVO
├── test_chain.py             # NOVO: ordem dos degraus, D-07, D-08, D-14, D-15, D-16
└── test_jsonld.py / test_ai.py
```

### Pattern 1: a cadeia em `search_store`, sem mexer nos adaptadores
**What:** uma lista de degraus `(nome, search_fn, fetch)` em que `search_fn` tem a assinatura que todos os adaptadores já têm. O corpo atual de `search_store` (pesquisa alargada, filtro D-15) passa a correr por degrau, com o `search_fn` e o `fetch` desse degrau. As exceções `StoreBlocked`/`StoreError`/`StoreTimeout`/genéricas dão o motivo do degrau e passam ao seguinte. `Found` com `raw == 0` é resposta válida e pára a cadeia (D-14).
**When to use:** as 4 lojas fixas (D-13).
**Example:**
```python
# Esboço; nomes novos são sugestões. O que existe: search_store, DEADLINE_S, StoreBlocked/StoreError/StoreTimeout.
RUNGS = ("API", "JSON-LD", "browser", "IA")

async def search_store(store, item, fetch, browser=None) -> StoreResult:
    done = fetch.cache.setdefault("captcha", set())
    if store.NAME in done:                                   # D-07: nem um pedido
        return StoreResult(store.NAME, "abrir à mão", [], detail="CAPTCHA antes nesta execução",
                           link=store.search_page(item.product))
    tried, stage, blocked = [], None, False
    try:
        async with asyncio.timeout(DEADLINE_S):                # D-15: um prazo para todos os degraus
            for stage, fn, f in rungs(store, fetch, browser):  # salta API e JSON-LD se a loja estiver em browser_only (D-08)
                try:
                    found, b, extra = await _one(fn, f, item)  # o corpo atual: 1.ª pesquisa + alargada
                except StoreCaptcha:
                    done.add(store.NAME)
                    return StoreResult(store.NAME, "abrir à mão", [], link=store.search_page(item.product))
                except Exception as e:  # StoreBlocked, StoreError, StoreTimeout e o resto: motivo e degrau seguinte
                    blocked = blocked or isinstance(e, StoreBlocked)
                    tried.append(f"{stage}: {e or type(e).__name__}")
                    continue
                for o in found.offers:
                    o.method = stage
                if stage == "browser":
                    fetch.cache.setdefault("browser_only", set()).add(store.NAME)  # D-08
                return _result(store, item, found, b, extra, tried)  # o resto de hoje (ordenação, detail)
    except TimeoutError:
        return StoreResult(store.NAME, "tempo esgotado", [], detail=f"mais de {DEADLINE_S} s, durante {stage}; " + "; ".join(tried))
    return StoreResult(store.NAME, "bloqueada" if blocked else "erro",
                       [], detail="; ".join(tried))  # D-16: motivo de cada degrau
```

### Pattern 2: `BrowserFetcher` com a interface do `Fetcher`
**What:** `get_html(url, params)` e `get_json(url, params)` fazem `page.goto(full_url(url, params))` num separador do Chrome dedicado e devolvem o corpo da resposta da navegação. O mesmo `store.search` corre sem mudanças, incluindo as APIs JSON (Allmat, Bricomarché, Obras 360), porque o Chrome também navega para URLs JSON. Usa a classe `Host` que já existe para o ritmo.
**When to use:** degrau 3 de todas as lojas.
**Notas de implementação:**
- Ligação: `async_playwright().start()` → `pw.chromium.connect_over_cdp("http://127.0.0.1:9222")` → `browser.contexts[0]` é o contexto do perfil, com os cookies (D-05). [CITED: playwright.dev/python/docs/api/class-browsertype: "The default browser context is accessible via browser.contexts."]
- Um separador por host, criado na primeira vez e reutilizado; o `Host(1, gap)` serializa as navegações desse host.
- Desafio DataDome na navegação: se o HTML tiver `captcha-delivery` com `'rt':'i'`, esperar pela recarga (`page.wait_for_load_state`) até ~10 s e ler `page.content()` de novo. Se tiver `'rt':'c'` ou `'t':'bv'` → `StoreCaptcha` (D-07). Nunca clicar no desafio.
- `get_json`: `json.loads(body, parse_float=Decimal)`, como o `Fetcher` (nunca `r.json()`).
- `--record` também no browser: gravar o corpo com o mesmo `fixture_name(full)`.
- Arranque (D-06): se `http://127.0.0.1:9222/json/version` não responder, `subprocess.Popen` com os argumentos do `.claude/claude-chrome.cmd`, esperar até ~10 s pela porta e marcar "fui eu que abri". No fim da execução: se foi a app que abriu, `Browser.close` por CDP (`await browser.new_browser_cdp_session()` → `send("Browser.close")`). O `Browser.close` fechou mesmo o Chrome dedicado nesta pesquisa. [VERIFIED: probe ao vivo]. Se foi o utilizador que abriu, só `browser.close()` do Playwright, que desliga sem fechar [CITED: playwright.dev/python/docs/api/class-browser: "clears all created contexts belonging to this browser and disconnects from the browser server"].

Argumentos do Chrome, verbatim do `.claude/claude-chrome.cmd`:
`"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="%USERPROFILE%\.claude-chrome" --remote-debugging-port=9222 --no-first-run --no-default-browser-check` [VERIFIED: `.claude/claude-chrome.cmd:3`]

### Pattern 3: adaptador Obramat
**What:** `search(query, fetch, rank=None) -> Found`, igual aos outros.
1. `html = await fetch.get_html(BASE + "/search", {"q": query})`.
2. `parse_search(html)`: confirmar que é a página de pesquisa (`cdl_page_type` = `Search`); se não for, `StoreError("página da Obramat sem lista de resultados")` (deteção pelo conteúdo, PITFALLS §4). Zero resultados (`ise_number_result` = `"0"`) → `Found([], raw=0)`. Senão, os produtos do `cdl_products_list` dentro de `ol#guidance-product-list > li[data-reflm] > script.dataTms`.
3. IVA: `unitprice_ati` é o preço; erro se `abs(add_vat(unitprice_tf, 23) - unitprice_ati) > Decimal("0.02")` (D-04). Com os dois preços arredondados ao cêntimo, o desvio honesto chega a ~0,011 €; o 0,01 da Obras 360 daria falsos erros (o rácio do tijolo, 0,34/0,28, é 1,214).
4. Filtro de título D-15 e ordenação como nas outras lojas; `raw` = produtos lidos; nota "mais N produtos na loja não lidos (só a 1.ª página: 18)" quando `ise_number_result` > lidos.
5. `location = "OBRAMAT Lisboa - Alfragide"` (único armazém; comentário `shortcut:`). D-01 cumpre-se sem pedidos extra.
6. Escalões e stock exato (D-04): página de produto, só para as K primeiras ofertas depois do filtro, uma de cada vez. `parse_tiers(html)` devolve `[(N, desconto_%)]` com `desconto = (1 - total_palete / (N × preço_unidade)) × 100`, a partir de `Ou Vendido <total> € IVA`. Se `cdl_user_context_main_store` não for `"201"` (cookie do armazém perdido), nota visível "escalões e stock por ler: escolha o armazém no Chrome dedicado".
7. URL da oferta: `BASE + p["url"]`; link "abrir à mão": `BASE + "/search?q=" + quote_plus(query)`.

### Pattern 4: degrau JSON-LD genérico
**What:** `jsonld.search(store)` devolve uma função com a assinatura dos adaptadores. Lê `store.search_page(query)` com o `Fetcher`, tira os links de produto com `store.PRODUCT_LINK` (regex por loja), lê as primeiras 5 páginas de produto e tira os `Product`/`Offer` de `script[type="application/ld+json"]`. Lojas sem `PRODUCT_LINK` (Bricomarché, Obras 360) ou sem links na página falham com motivo visível. O IVA segue a regra da loja (ARCHITECTURE Pattern 3: com IVA na Obramat e na Allmat, sem IVA na Obras 360, mínimo entre lojas na Bricomarché).
**When to use:** degrau 2. Na prática só a Allmat tira proveito; na Obramat o pedido leva o mesmo 403 do degrau 1.

### Pattern 5: degrau IA com um esquema e dois motores
**What:** um `SCHEMA` JSON (objeto `offers` = lista de `{title, price, url}`, `additionalProperties: false`, sem `maxItems`, que a saída estruturada não aceita; o corte a 5 faz-se no código). Texto de entrada: o texto da página de pesquisa da loja (o do browser, se o degrau 3 chegou a carregar a página; senão o HTML do `curl_cffi` passado a texto com o selectolax), cortado a ~20 000 caracteres.
- Com `ANTHROPIC_API_KEY`: `AsyncAnthropic().messages.create(model="claude-haiku-5-5", max_tokens=2048, output_config={"format": {"type": "json_schema", "schema": SCHEMA}, "effort": "low"}, messages=[…])`, depois `json.loads` do bloco de texto. [CITED: skill claude-api, `python/claude-api/tool-use.md` §Raw Schema; Haiku 5.5 `$0.10 / $0.50` por MTok, effort por omissão `medium`]
- Sem chave: `asyncio.create_subprocess_exec(shutil.which("claude"), "-p", "--model", "haiku", "--output-format", "json", "--json-schema", json.dumps(SCHEMA), "--tools", "", "--no-session-persistence", "--system-prompt", PROMPT, stdin=PIPE, stdout=PIPE)`, texto da página no stdin, e ler `structured_output` do JSON. Se faltar `structured_output`, ou `is_error` vier `true`, o degrau falha com o `result` como motivo. [CITED: code.claude.com/docs/en/headless: "the structured output in the `structured_output` field … If a run ends without valid structured output … the response has no `structured_output` field"]
- **Nunca `--bare`:** em modo bare o Claude Code "never reads OAuth credentials", por isso a conta Pro deixa de funcionar. [CITED: code.claude.com/docs/en/headless]
- Validação de cada oferta lida (fronteira de confiança): preço convertido para `Decimal` > 0, e **a string do preço tem de aparecer no texto enviado** (trava preços inventados); URL absoluto no host da loja, ou relativo resolvido contra `BASE`; título passa no filtro D-15. `vat_origin="regra da loja"`, `method="IA"`, `note="lido por IA"`.

### Anti-Patterns to Avoid
- **Um "degrau browser" com parsers próprios por loja:** duplica os 4 adaptadores. O `BrowserFetcher` com a mesma interface reutiliza-os.
- **Ler o primeiro `cdl_products_list` da página:** apanha o carrossel "vistos recentemente" e mostra produtos numa pesquisa sem resultados.
- **Tirar o escalão do preço por unidade mostrado (0,32 €):** está arredondado; usar o total da palete.
- **Tratar o 403 do DataDome como CAPTCHA:** o `'rt':'i'` é a verificação do dispositivo, que o Chrome real passa sozinho. Só `'rt':'c'` (ou `'t':'bv'`) é a paragem do D-07.
- **Estado da execução em variáveis globais do módulo:** os testes correm várias execuções no mesmo processo. Usar `fetch.cache`, que já é por execução.
- **Escalar quando a loja diz "sem resultados":** proibido pelo D-14.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Controlar o Chrome | Cliente CDP próprio (WebSocket, sessões, eventos de carga) | Playwright `connect_over_cdp` | Corpo da resposta, espera pela carga e separadores já resolvidos |
| Passar o DataDome | Cabeçalhos/impressões TLS diferentes, resolver o desafio | Chrome dedicado com janela, ritmo humano | Contornar uma medida técnica é o ato de maior risco legal (PITFALLS §13); o browser real já passa |
| JSON da IA | Regex sobre texto livre | Saída estruturada (`output_config.format`, `--json-schema`) | Formato garantido |
| Ritmo por host no browser | Novo limitador | A classe `Host` do `fetch.py` | Já testada |

**Key insight:** quase tudo o que esta fase precisa já existe; o trabalho novo está em pôr os mesmos adaptadores a correr por outro transporte (browser) e em ler a Obramat.

## Runtime State Inventory

Não é uma fase de renomeação. O que conta é estado fora do repositório de que a fase passa a depender:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | Perfil `%USERPROFILE%\.claude-chrome`: cookies da Obramat gravados nesta pesquisa. `customer_context` (armazém 201, expira 2027-11-29), `OptanonConsent` (cookies recusados, 2027-10-30), `datadome` (2027-10-30) | Nenhuma no código. Se o utilizador limpar o perfil, os escalões e o stock exato deixam de aparecer: o adaptador deteta `cdl_user_context_main_store` ≠ `"201"` e escreve a nota |
| Live service config | Nenhum | — |
| OS-registered state | Nenhum (o Chrome é lançado à mão ou pela app) | — |
| Secrets/env vars | `ANTHROPIC_API_KEY` não está definida nesta máquina; o `claude -p` lançado a partir desta sessão deu "Failed to authenticate: OAuth session expired and could not be refreshed" | O degrau IA tem de mostrar este motivo; o utilizador confirma o `claude -p` no terminal dele (Open Question 3) |
| Build artifacts | `.venv` sem `playwright` nem `anthropic` | `uv add` (com checkpoint) |

## Common Pitfalls

### Pitfall 1: pressupor que o `curl_cffi` passa na Obramat
**What goes wrong:** o STACK.md (22-10) registou 200 na página inicial; hoje são 403 em tudo.
**How to avoid:** o degrau principal da Obramat fica, mas o plano conta com o browser como caminho real; D-08 evita repetir o 403 nos itens seguintes.
**Warning signs:** `x-datadome-riskscore` no cabeçalho; corpo de ~773 bytes com `captcha-delivery`.

### Pitfall 2: CAPTCHA confundido com bloqueio simples (ou o contrário)
**What goes wrong:** parar a Obramat com um `'rt':'i'` perde a loja sem motivo; continuar com um `'rt':'c'` viola o D-07.
**How to avoid:** ler o objeto `dd` do corpo; `'rt':'c'` ou `'t':'bv'` → `StoreCaptcha`; `'rt':'i'` → `StoreBlocked` (escala). O `Fetcher.get` lança hoje `StoreBlocked` antes de ler o corpo (`fetch.py:82-83`); o teste ao `dd` tem de vir antes dessa linha.
**Warning signs:** iframe `geo.captcha-delivery.com` visível na janela do Chrome.

### Pitfall 3: listas falsas na página de pesquisa
Ver Armadilhas 1 e 2 acima. Teste com a amostra sem resultados: tem de dar `raw == 0`.

### Pitfall 4: IVA verificado com tolerância apertada
Preços pequenos arredondados dão rácios como 1,214. Comparar em euros, `abs(add_vat(tf, 23) - ati) <= 0.02`, nunca o rácio.

### Pitfall 5: escalões em percentagem com casas a mais
`(1 - 1299.60 / (48 × 28.50)) × 100` dá exatamente 5 nas duas amostras, mas outros produtos podem dar dízimas. O `report.py` mostra `fmt_qty(p)` sem arredondar. Arredondar para 2 casas só na saída e guardar o `Decimal`.

### Pitfall 6: orçamento de 5 minutos
**What goes wrong:** cada página de produto da Obramat é uma navegação (~1,5–2 s + intervalo). Com K grande, a Obramat passa a ser o gargalo do item.
**How to avoid:** K pequeno para escalões (sugestão: 3); a pesquisa sozinha já dá preço, título, link e armazém.
**Warning signs:** item a demorar mais do que a Bricomarché (~9 s por item na fase 1: folha de 3 linhas em 26 s).

### Pitfall 7: `claude -p` com hooks e plugins do utilizador
**What goes wrong:** sem `--bare`, o `claude -p` carrega os hooks e plugins de `~/.claude` (aqui há um hook do ponytail que injeta texto) e o `CLAUDE.md` da pasta onde corre.
**How to avoid:** correr com `cwd` numa pasta temporária vazia, `--tools ""` e `--system-prompt` próprio. O `--setting-sources ""` talvez corte os plugins do utilizador (A6); confirmar na primeira execução.

### Pitfall 8: prompt injection a partir da página da loja
O texto da página é dado não confiável. Com `--tools ""` o `claude -p` não tem ferramentas; na API não há ferramentas. A validação das ofertas (preço presente no texto, URL no host da loja) trava o resto.

## Code Examples

### Obramat: produtos da pesquisa (só a lista principal)
```python
# Seletores e chaves verificados nas amostras de samples/ (2026-10-30).
import json
from decimal import Decimal
from selectolax.lexbor import LexborHTMLParser

def _tms(node) -> dict:
    return {e["name"]: e["value"] for e in json.loads(node.text(), parse_float=Decimal)}

def parse_search(page: str) -> tuple[list[dict], int]:
    """(produtos com preço da lista principal, total de resultados da loja)."""
    root = LexborHTMLParser(page)
    meta = {}
    for s in root.css("script.dataTms"):
        if '"cdl_page_type"' in s.text():
            meta.update(_tms(s))
    if meta.get("cdl_page_type") != "Search":
        raise StoreError("página da Obramat sem lista de resultados (layout mudou?)")
    total = int(meta["cdl_search"]["ise_number_result"])
    products = []
    # Só filhos diretos: o carrossel "vistos recentemente" e o bloco promocional têm listas próprias.
    for s in root.css("ol#guidance-product-list > li[data-reflm] > script.dataTms"):
        products += _tms(s).get("cdl_products_list", [])
    return products, total
```

### Obramat: escalões da página de produto
```python
import re
EUR = re.compile(r"Ou Vendido ([\d\s\u00a0.]+,\d{2}) € IVA")

def parse_tiers(page: str, unit_price: Decimal) -> list[tuple[Decimal, Decimal]]:
    """[(a partir de N, -%)] a partir do total da palete; o preço por unidade mostrado vem arredondado."""
    out = []
    for tile in LexborHTMLParser(page).css(".o-priceByQuantity__tileItem"):
        inp = tile.css_first("input")
        n = Decimal(inp.attributes.get("value") or "1") if inp is not None else Decimal(1)
        if n <= 1:
            continue
        m = next((EUR.search(" ".join(x.text().split())) for x in tile.css(".kl-hidden-accessibility")
                  if EUR.search(" ".join(x.text().split()))), None)
        if m is None:
            continue
        total = Decimal(re.sub(r"[\s\u00a0.]", "", m[1]).replace(",", "."))
        out.append((n, (1 - total / (n * unit_price)) * 100))
    return out
# OSB 18 mm: [(48, 5)]  (1 299,60 € / 48 / 28,50 €); tijolo: [(270, 5)]  (87,21 € / 270 / 0,34 €)
```

### Deteção do tipo de desafio DataDome
```python
DD = re.compile(r"var dd=\{([^}]*)\}")

def challenge_kind(body: str) -> str | None:
    """'captcha' (D-07: parar), 'interstitial' (escala para o browser) ou None."""
    m = DD.search(body)
    if not m:
        return None
    return "captcha" if ("'rt':'c'" in m[1] or "'t':'bv'" in m[1]) else "interstitial"
# Amostra de hoje: var dd={'rt':'i',…} -> "interstitial"
```

### `claude -p` com saída estruturada
```python
proc = await asyncio.create_subprocess_exec(
    shutil.which("claude"), "-p", "--model", "haiku", "--output-format", "json",
    "--json-schema", json.dumps(SCHEMA), "--tools", "", "--no-session-persistence",
    "--system-prompt", PROMPT, cwd=tmpdir,
    stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
out, _ = await proc.communicate(page_text.encode("utf-8"))
data = json.loads(out)
if data.get("is_error") or "structured_output" not in data:
    raise StoreError(f"IA (claude -p): {data.get('result') or 'sem saída estruturada'}")
offers = data["structured_output"]["offers"][:5]
```

## Orçamento de tempo (LIST-03)

| Peça | Medido | Fonte |
|---|---|---|
| Bricomarché | ~9 s por item (folha de 3 linhas: 26 s; `verificar`: 50 s) | 01-06 SUMMARY via STATE.md |
| Obramat, 1.º item | 3 pedidos curl a 403 (<0,2 s cada) + arranque do Chrome (~2 s) + 1.ª página (3,4–10 s) | probe ao vivo |
| Obramat, itens seguintes | 1 página de pesquisa (1,7–1,8 s) + K páginas de produto (~1,5 s cada) + intervalo de 3 s + jitter | probe ao vivo |

Com K = 3 e intervalo de 3–5 s: ~15–20 s por item na Obramat, em paralelo com as outras lojas. Estimativa para 10 itens: 2,5–3,5 min. Cabe nos 5 min, sem folga larga; a prova é uma corrida ao vivo de 10 linhas (verificação manual da fase).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `<li data-reflm>` com `dataTms` por produto (ARCHITECTURE, 22-10) | Lista inteira num só `dataTms` no 1.º `li`; carrosséis com listas próprias | visto hoje | Parser tem de usar o seletor de filho direto |
| `curl_cffi` passava na página inicial da Obramat (STACK, 22-10) | 403 em tudo | visto hoje | Browser é o caminho real (D-08) |
| `output_format` em `messages.create` | `output_config: {format: …}` | skill claude-api (cache 2026-10-06) | Usar `output_config` |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | O 403 do `curl_cffi` vale para outras impressões TLS (não testado: o classificador de permissões bloqueou a tentativa com `safari260`/`firefox147`/`chrome150` como contorno de anti-bot) | Achados ao vivo | Nenhum para o plano: a política do projeto é não contornar; o degrau principal fica como está |
| A2 | `'rt':'c'` = CAPTCHA, `'rt':'i'` = verificação do dispositivo, `'t':'bv'` = bloqueio (fontes de terceiros, não documentação da DataDome) | Pitfall 2, Code Examples | Um CAPTCHA tratado como bloqueio simples: o browser mostrá-lo-ia e o `BrowserFetcher` tem de o apanhar também |
| A3 | O preço 000 = 201 em todos os produtos (8 comparados) | Summary | Uma diferença de preço por armazém ficaria por mostrar; com um só armazém e o browser já no contexto 201, o preço lido no browser é o do armazém de qualquer forma |
| A4 | `response.body()` do `page.goto` devolve o JSON cru das APIs da Allmat/Bricomarché/Obras 360 no Chrome | Pattern 2 | Degrau browser falha nessas lojas; alternativa: `page.inner_text("pre")` |
| A5 | Ritmo de 3 s + jitter aguenta 10 itens sem CAPTCHA (testado: 21 navegações a 4–10 s) | Orçamento de tempo | CAPTCHA a meio da lista → "abrir à mão" (comportamento correto, mas perde a Obramat) |
| A6 | `--setting-sources ""` evita os plugins/hooks do utilizador no `claude -p` sem estragar a autenticação | Pitfall 7 | Prompt com texto extra do hook; mais tokens |
| A7 | `messages.create` com `output_config` que junta `format` e `effort` é aceite pelo `anthropic` 2.3.0 | Pattern 5 | Erro 400 no primeiro uso; tirar o `effort` |
| A8 | Só existe um armazém em Portugal hoje; um segundo aparecerá na janela do site | Pattern 3 | `location` fixo errado; o comentário `shortcut:` e o `verificar` devem apanhar |

## Open Questions (RESOLVED)

1. **D-03: a Obramat hoje só se lê pelo browser. Avançar assim?** RESOLVED: sim, D-18 (browser via D-08, escalões e stock só nas 3 primeiras ofertas, K = 3); planos 02-01 e 02-02.
   - Números medidos: curl 3/3 a 403 (riskscore 0,39–0,55, interstitial `'rt':'i'`); browser 21/21 sem CAPTCHA, 1,7–1,8 s por página (1.ª 3,4–10 s); por item: 1 página de pesquisa para preço, título, link e armazém, mais 1 página por produto para escalões e stock exato.
   - O que já não é dúvida: só há um armazém e o preço nacional = preço de Alfragide, por isso não há escolha entre "preço nacional" e "preço por loja".
   - Recommendation: o planeamento pergunta ao utilizador antes de fechar os planos (como manda o D-03), propondo: browser como caminho real da Obramat via D-08; escalões e stock exato só para as 3 primeiras ofertas (K = 3).
2. **Degrau JSON-LD sem fonte de links na Bricomarché e na Obras 360** RESOLVED: D-19 (falha logo com motivo visível e segue para o browser); plano 02-04.
   - What we know: as páginas de pesquisa dessas lojas são montadas com JavaScript; sem a API não há URLs de produto.
   - Recommendation: o degrau corre e falha com "página de pesquisa sem links de produto (montada com JavaScript)". Confirmar com o utilizador que isto cumpre o D-13/D-16.
3. **`claude -p` não autenticado nesta sessão** RESOLVED: verificação humana no terminal do utilizador no plano 02-05; o degrau mostra o motivo quando falha.
   - What we know: lançado a partir desta sessão deu "OAuth session expired and could not be refreshed". Pode ser só deste ambiente de agente.
   - Recommendation: o plano inclui um passo manual em que o utilizador corre `echo teste | claude -p --model haiku --output-format json` no terminal dele; o degrau mostra sempre o motivo quando falha.
4. **Status novo "abrir à mão"** RESOLVED: `Status` e `StoreResult.link` nos planos 02-01 e 02-03.
   - Recommendation: acrescentar `"abrir à mão"` ao `Status` (SC1 usa o nome) e `StoreResult.link`. O `_problem` do `verificar` trata-o como falha.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python + uv | tudo | ✓ | 3.13 / uv 0.12.6 | — |
| curl_cffi, selectolax | degraus 1 e 2, parsers | ✓ | 0.16.3 / 1.0.2 | — |
| Google Chrome | degrau browser (D-05) | ✓ | 156.0.8078.76 | Sem Chrome: degrau falha com motivo |
| Perfil `.claude-chrome` + porta 9222 | degrau browser | ✓ (arranca com `.claude\claude-chrome.cmd`) | — | A app arranca-o (D-06) |
| playwright (Python) | degrau browser | ✗ | — | `uv add` (Wave 0) |
| anthropic (Python) | degrau IA com chave | ✗ | — | `uv add`; sem chave usa `claude -p` |
| `ANTHROPIC_API_KEY` | degrau IA (API) | ✗ | — | `claude -p` |
| Claude Code CLI | degrau IA (sem chave) | ✓ instalado, ✗ autenticado nesta sessão | 2.1.308 | Motivo visível; Open Question 3 |

**Missing dependencies with no fallback:** nenhuma que bloqueie a fase.
**Missing dependencies with fallback:** playwright e anthropic (instalar); autenticação do `claude -p` (confirmar à mão).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (222 testes passam em 1,6 s hoje) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options] testpaths = ["tests"]` |
| Quick run command | `uv run pytest -q -x` |
| Full suite command | `uv run pytest -q` |

Padrão em vigor: sem rede (`no_network` autouse bloqueia `AsyncSession.request`), `FakeFetcher` com rotas e fixtures, lojas falsas por `monkeypatch`, `asyncio.run` nos testes. O `BrowserFetcher` tem a mesma interface, por isso os testes da cadeia usam dois `FakeFetcher` (um "curl", um "browser"). O motor da IA fica atrás de uma função que os testes trocam por `monkeypatch`.

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| STORE-04 | Lista principal da pesquisa, sem carrossel nem bloco promocional | unit | `uv run pytest tests/test_obramat.py -q` | ❌ Wave 0 |
| STORE-04 | Zero resultados → `raw == 0` (a amostra tem carrossel com 1 produto) | unit | idem | ❌ Wave 0 |
| STORE-04 | IVA: erro se `add_vat(tf) - ati` > 0,02 | unit | idem | ❌ Wave 0 |
| STORE-04 | Escalões OSB `(48, 5)` e tijolo `(270, 5)`; nota sem armazém 201 | unit | idem | ❌ Wave 0 |
| STORE-04 | `'rt':'c'` → "abrir à mão" com link; itens seguintes sem pedidos à Obramat | unit | `uv run pytest tests/test_chain.py -q` | ❌ Wave 0 |
| STORE-04 | `LIMITS` da Obramat com 1 em simultâneo | unit | `uv run pytest tests/test_fetch.py -q` | ❌ Wave 0 |
| STORE-06 | Ordem API → JSON-LD → browser → IA; `method` em cada oferta | unit | `uv run pytest tests/test_chain.py -q` | ❌ Wave 0 |
| STORE-06 | `sem resultados` não escala (D-14) | unit | idem | ❌ Wave 0 |
| STORE-06 | D-08: depois do browser, item seguinte não toca no fetch principal | unit | idem | ❌ Wave 0 |
| STORE-06 | Todos falham → motivo de cada degrau; prazo a meio → "durante <degrau>" | unit | idem | ❌ Wave 0 |
| STORE-06 | `--sem-principal obramat` força o recurso | unit | `uv run pytest tests/test_e2e.py -q` | ✅ (acrescentar caso) |
| STORE-06 | IA: ≤5 ofertas, preço tem de estar no texto, URL no host, "lido por IA" | unit | `uv run pytest tests/test_ai.py -q` | ❌ Wave 0 |
| STORE-06 | JSON-LD: Product/Offer de uma página de produto da Allmat; Bricomarché sem links → motivo | unit | `uv run pytest tests/test_jsonld.py -q` | ❌ Wave 0 |
| STORE-07 | `verificar` cobre as 4 lojas (canário Obramat "osb", exige `location`) | unit | `uv run pytest tests/test_search.py -q` | ✅ (acrescentar) |
| LIST-03 | Folha de 10 itens em < 5 min, estado das 4 lojas por item | manual (ao vivo) | `uv run python -m strata pesquisar <folha de 10>` com tempo medido | manual-only: precisa de rede e do Chrome |

### Sampling Rate
- **Per task commit:** `uv run pytest -q -x`
- **Per wave merge:** `uv run pytest -q`
- **Phase gate:** suite verde + `uv run python -m strata verificar` com as 4 lojas OK + corrida ao vivo de 10 itens cronometrada, antes do `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/fixtures/obramat_*.html`: copiar de `.planning/phases/02-obramat-e-cadeia-de-recurso/samples/` (nomes pelo `fixture_name` ou rotas no `FakeFetcher`)
- [ ] `tests/test_obramat.py`, `tests/test_chain.py`, `tests/test_ai.py`, `tests/test_jsonld.py`
- [ ] Uma página de produto da Allmat com JSON-LD intacto (a fixture atual foi cortada e não tem `ld+json`)
- [ ] `uv add playwright anthropic` (com checkpoint humano)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | não (sem contas nas lojas, REQUIREMENTS Out of Scope) | — |
| V3 Session Management | parcial: cookies do perfil dedicado | Perfil próprio; nunca o Chrome do utilizador (D-05); `--record` grava só corpos, nunca cabeçalhos/cookies (padrão do `fetch.py:88`) |
| V4 Access Control | não | — |
| V5 Input Validation | sim | Saída da IA validada (preço no texto, URL no host da loja, `Decimal` > 0); `report.clean` em tudo o que vem das lojas; JSON com `parse_float=Decimal` |
| V6 Cryptography | não | — |
| V12/V14 (configuração, segredos) | sim | `ANTHROPIC_API_KEY` só do ambiente; nunca reutilizar o token OAuth do Claude Code fora do `claude` (D-12); subprocesso sem `shell=True`, texto pelo stdin |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection no texto da página da loja | Tampering | Sem ferramentas (`--tools ""`; API sem tools); saída estruturada; validação de preço/URL |
| Preço inventado pela IA | Tampering | Preço tem de aparecer no texto; ofertas IA sempre depois das estruturadas (D-09) |
| Injeção de comandos no subprocesso | Elevation | `create_subprocess_exec` com lista de argumentos; produto nunca entra na linha de comando |
| Contornar medida técnica (DataDome) | Repudiation/legal | Sem impressões falsas, sem resolvedores, parar ao CAPTCHA (D-07); nota legal pendente do STATE.md (Blockers) como tarefa curta da fase |
| Sequências ANSI vindas das lojas | Tampering | `report.clean` |

## Project Constraints (from CLAUDE.md)

- Python 3.13 com `uv`; correr com `uv run python -m strata`; neste Windows usar `python`, nunca `python3`.
- Um só cliente HTTP: `curl_cffi` com `impersonate="chrome"`; parsing com selectolax.
- Browser: Playwright com o Chrome instalado; o Chrome do Claude (perfil `%USERPROFILE%\.claude-chrome`, porta 9222, `.claude\claude-chrome.cmd`), nunca o Chrome do utilizador.
- IA só como último recurso, marcada; preço vem de campo estruturado sempre que exista.
- Sem proxies, resolvedores de CAPTCHA, sessões autenticadas nas lojas; volume baixo; nunca omitir falhas em silêncio.
- Sem `tenacity`, `pandas`, base de dados, `python-dotenv`; chaves só em variáveis de ambiente.
- Ponytail: mudança mínima completa; reutilizar o que existe; comentários `shortcut:` para limites conhecidos; lógica nova com teste.
- Respostas e prosa em PT-PT; prosa para pessoas passa pelo `humanizer`.
- Trabalho dentro de um comando GSD.

## Sources

### Primary (HIGH confidence)
- Probes ao vivo de 2026-10-30 (curl_cffi 0.16.3 e Chrome 156 dedicado por CDP) a `www.obramat.pt` (`/search?q=osb`, `cimento cola`, `zzqxv`, `tinta`, `cimento 25kg`, `tijolo`, `gesso cartonado`, `parafuso`, `tubo pvc 110`, `areia`; produtos 25134518 e 25074549), `allmat.pt`, `www.bricomarche.pt`, `www.obras360.pt`. Amostras em `.planning/phases/02-obramat-e-cadeia-de-recurso/samples/`.
- Código lido nesta sessão: `src/strata/fetch.py`, `search.py`, `models.py`, `report.py`, `__main__.py`, `stores/*.py`, `tests/conftest.py`, `.claude/claude-chrome.cmd`, `pyproject.toml`.
- PyPI JSON: playwright 1.64.1, anthropic 2.3.0, pydantic 2.14.2.
- Skill `claude-api` (cache 2026-10-06): `claude-haiku-5-5`, preços, `output_config.format`, limites do JSON Schema.
- [Claude Code headless](https://code.claude.com/docs/en/headless): `--json-schema`, `structured_output`, `--bare` sem OAuth.

### Secondary (MEDIUM confidence)
- [Playwright BrowserType](https://playwright.dev/python/docs/api/class-browsertype) e [Browser](https://playwright.dev/python/docs/api/class-browser): `connect_over_cdp`, `contexts`, `close()`.
- Obramat em Portugal (uma loja, Alfragide): [echoboomer.pt](https://echoboomer.pt/?p=247125), [Executive Digest](https://executivedigest.sapo.pt/dona-do-leroy-merlin-abre-primeiro-armazem-de-nova-marca-de-materiais-de-construcao-em-portugal-e-cria-150-postos-de-trabalho/), [Alimarket](https://www.alimarket.es/construccion/noticia/405529/obramat-estrena-su-primer-almacen-en-portugal), [Forbes Portugal](https://www.forbespt.com/?p=158876).

### Tertiary (LOW confidence)
- Significado de `rt`/`t` no objeto `dd` da DataDome: [zendriver-datadome detect.js](https://docs.rs/crate/zendriver-datadome/latest/source/src/detect.js), [captchaforge datadome.rs](https://docs.rs/crate/captchaforge/latest/source/src/solver/vendors/datadome.rs), [Apify DataDome Unblocker](https://apify.com/xhrdev/datadome-unblocker). Usados só para classificar o desafio, nunca para o contornar.

## Metadata

**Confidence breakdown:**
- Obramat (endpoint, campos, escalões, armazém, IVA): HIGH, medido ao vivo e gravado em amostras
- Tolerância do DataDome numa lista de 10: MEDIUM, 21 navegações sem CAPTCHA, mas numa só sessão
- Degrau browser para as APIs JSON: MEDIUM, desenho por documentação (A4)
- Degrau IA: MEDIUM, API por documentação; `claude -p` com formato documentado mas não autenticado aqui
- Orçamento de 5 min: MEDIUM, estimativa a partir de medições parciais

**Research date:** 2026-10-30
**Valid until:** 2026-11-13 (DataDome e o HTML da Obramat mudam sem aviso; 14 dias)
