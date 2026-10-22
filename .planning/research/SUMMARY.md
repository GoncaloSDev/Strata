# Project Research Summary

**Project:** Strata
**Domain:** Comparador de preços pessoal (PC) para materiais de obra, bricolage e mobília em lojas online portuguesas: recolha na hora, normalização IVA/unidades, otimização de embalagens, classificação exato/parecido com IA
**Researched:** 2026-10-22
**Confidence:** MEDIUM-HIGH (as 4 lojas fixas foram sondadas ao vivo hoje; preços de APIs de pesquisa, Jev e notas legais vêm de fontes secundárias)

## Executive Summary

O Strata é um agregador de preços pequeno, de um utilizador, que corre localmente. Não existe nada igual em Portugal: os comparadores de consumo (KuantoKusta, idealo, Google Shopping) não aceitam listas com quantidades, não otimizam embalagens e cobrem mal materiais de obra. As ferramentas B2B (Contractor+, BuyMaterials) servem os EUA e o Reino Unido. Quem faz isto bem usa um adaptador por loja que lê dados estruturados (API interna > JSON-LD > HTML > IA), um normalizador puro e testado onde vive toda a aritmética de dinheiro, e a IA apenas em volta: interpretar o pedido, extrair atributos e classificar. A IA nunca lê preços quando há campo estruturado.

Recomendação: Python 3.13 + uv, app local em NiceGUI, curl_cffi (TLS do Chrome) como único cliente HTTP, selectolax, Playwright só como recurso e para o PDF, Claude Haiku 5.5 com saída estruturada para extração e classificação (cerca de 2 cêntimos por lista), Serper.dev para descobrir lojas e XlsxWriter. As sondas de hoje mostram que as 4 lojas fixas têm dados estruturados: Allmat e Bricomarché expõem a WooCommerce Store API pública (um adaptador genérico serve as duas), a Obras 360 (`obras360.pt`, plataforma Beevo) tem uma API JSON interna de widgets com variantes, IVA e escalões por quantidade, e a Obramat (ADEO, DataDome) embute JSON `dataTms` com preço com e sem IVA no HTML do servidor.

O risco principal não é técnico, é de correção silenciosa: um preço sem IVA a ganhar por cerca de 19%, o 0,00 € do mini-carrinho, a linha "pai" da Obras 360 com o preço da variante de 9 mm, o `price` de topo da Bricomarché (mínimo entre lojas), ou um "exato" falso porque falta um atributo. O `price` do JSON-LD tem um significado diferente em cada loja fixa. Mitigação: política de IVA declarada por loja com evidência, `Decimal`, estados explícitos por loja (`ok / no_results / blocked / error / timeout`), canários por loja, regra "atributo desconhecido nunca dá exato" e fixtures gravadas para todos os parsers.

## Key Findings

### Recommended Stack

Um processo Python assíncrono. Separar "buscar" (rede) de "interpretar" (puro, testado com fixtures) em cada adaptador. Sem base de dados no v1. Detalhe completo em STACK.md.

**Core technologies:**
- **Python 3.13 + uv:** linguagem e ambiente. Já instalados; não subir para 3.15 (as rodas binárias chegam tarde). Usar sempre `uv run`, nunca `python3`.
- **NiceGUI 3.18:** UI local no browser. Assíncrona, com progresso por loja sem escrever JS nem SSE.
- **curl_cffi 0.16.3:** único cliente HTTP. Imita o TLS do Chrome; passou o DataDome da Obramat no teste de hoje (o `curl` simples levou 403).
- **selectolax 1.0.2:** HTML e JSON-LD, rápido e sem dependências pesadas.
- **Playwright 1.64 (`channel="chrome"`):** só como recurso para páginas com JS ou bloqueio, e para gerar o PDF (`page.pdf()`).
- **anthropic 2.1 + Claude Haiku 5.5:** extração de especificações e classificação com `messages.parse` + Pydantic, por cerca de 2 cêntimos por lista. Confirmar a assinatura da API 2.x no primeiro uso.
- **Serper.dev:** descoberta (`/search` + `/shopping`, `gl=pt`). Cerca de 1 $/1k pesquisas, com 2.500 grátis. A Google Custom Search API fecha a 2027-01-01.
- **XlsxWriter + pytest:** exportação Excel; testes com fixtures em ficheiro (o vcrpy não interceta o curl_cffi).

**Jev (TypeSafe AI):** não serve para extração, porque só devolve choice/score/sim-não e não valores como "18 mm" ou "pack de 10". As comparações numéricas ficam no código. v1 só com Haiku. Spike de 1–2 h na fase de matching: cerca de 50 anúncios PT rotulados, Haiku vs Jev na pergunta "mesmo tipo de produto?". Adotar apenas se igualar o Haiku em português. Acesso via Vercel AI Gateway (os registos diretos estão fechados); fixar `jev-1.13.0`.

**Não usar:** requests/httpx simples para as lojas, Scrapy, Selenium, proxies residenciais ou resolvedores de CAPTCHA, pandas, uma LLM a ler preços quando há JSON, Google CSE.

### Expected Features

**Must have (table stakes, v1):**
- T1/T2: lista colada (texto + quantidade + unidade), pesquisa em texto livre, sem categorias.
- T3: recolha na hora nas 4 lojas fixas.
- T4/T5/D2: IVA normalizado para 23% com origem visível; preço unitário (€/un, €/m², €/m, €/kg); conversão entre a unidade pedida e a unidade vendida.
- T6/T7: extração de especificações; exatos primeiro, parecidos à parte com a diferença escrita.
- T8/D1: custo total para a quantidade pedida, com a melhor combinação de embalagens e escalões (o diferenciador central), excedente visível.
- T9–T15: tabela ordenada com link, estado por loja, stock mostrado sem filtrar, progresso em tempo real, exclusão manual de linhas, total da lista, exportação Excel.

**Should have (v1.x):**
- D5: cadeia completa de recurso (browser, IA).
- D6/D7: descoberta de lojas PT e sugestão de as promover a fixas.
- D3/D4/D8: poupança do parecido, etiqueta de origem e confiança, repetir só um item ou só uma loja.
- D9: exportação PDF.

**Defer (v2+) / anti-features:** portes, agrupar compras por loja, histórico e alertas, catálogo pré-recolhido, árvore de categorias, filtrar por stock, carrinho automático, IVA das ilhas, esconder lojas que falham.

### Architecture Approach

Pipeline num só sentido: UI → Orquestrador (`asyncio`, item × loja em paralelo, prazos) → Fontes (adaptadores fixos + genéricos, cadeia de recurso) → Normalizador (IVA, unidades, embalagens, escalões; puro) → Matcher (regras primeiro, LLM depois, com cache) → Otimizador de embalagens (pesquisa exata, sem solver) → Resultados/Export. Os adaptadores reportam o que o site diz, mais a evidência; nunca calculam IVA nem decidem o match. O transporte (curl_cffi ou browser) é injetado, por isso o mesmo parser corre sobre HTML renderizado.

**Major components:**
1. **Adaptadores:** `generic/woo_store_api` (Allmat, Bricomarché e qualquer loja Woo descoberta), `stores/obras360` (Beevo `product-list` + `product-details` com variantes e `DiscountByQuantity`), `stores/obramat` (`dataTms`: `unitprice_ati`/`_tf`), `generic/jsonld`, `generic/llm_page`.
2. **Fetcher:** limites por host (Obramat: 1 pedido em simultâneo, intervalo de 1,5 s + jitter; Bricomarché: timeout de leitura de 30 s, porque cada página demora cerca de 12 s), deteção de bloqueio pelo conteúdo.
3. **`core/` sem I/O:** `models` (RawOffer com `price_vat` + `vat_evidence`, `sale_unit`, `content_qty`, `tiers`, `location`, `method`, `fetched_at`), `normalize`, `match_rules`, `optimize`.
4. **LLM side-car (`infra/llm.py`):** uma interface; o Haiku hoje, o Jev atrás da mesma interface se o spike o justificar.
5. **Orquestrador + modelo de estado item × loja:** alimenta o progresso, as falhas visíveis, a repetição seletiva e a fiabilidade das lojas descobertas.

**Fluxos por loja confirmados:**
- **Bricomarché:** `type=variation` → agrupar por `parent` → mínimo por loja física, com `location`. Isto cumpre a decisão do utilizador. O link tem de apontar para o caminho da loja (`/{store-slug}/produto/...`).
- **Allmat:** o preço vem por caixa; a área da caixa só existe no HTML do produto. Ignorar a etiqueta "M2" da Store API.
- **Obras 360:** expandir as variantes antes do matching. O ID do widget deve ser lido da página `/pesquisa`, não fixado no código.

### Critical Pitfalls

1. **IVA misturado (Pitfall 1):** `vat_policy` por loja com evidência; `excl × 1,23` num único sítio, com `Decimal`. Na Obramat, verificar que ati/tf ≈ 1,23. Lojas descobertas sem prova ficam "IVA por confirmar" e nunca em 1.º lugar. O `price` do JSON-LD não é comparável entre lojas: sem IVA na Obras 360, com IVA na Obramat, por caixa na Allmat, mínimo entre lojas na Bricomarché.
2. **Número errado (Pitfalls 2 e 6):** o 0,00 € do mini-carrinho na Allmat, preços riscados ou "preço mais baixo em 30 dias", "desde X €", €/m² vs €/caixa, cêntimos da Store API. Usar fontes estruturadas, validar preço > 0 e a plausibilidade face à mediana, guardar `sale_unit` + `content_qty`, e confirmar que €/m² × m²/caixa ≈ €/caixa.
3. **Falhas silenciosas (Pitfall 4):** estados explícitos; "sem resultados" só conta com o marcador próprio da loja (a Allmat não vende OSB, e isso é informação, não erro); deteção de DataDome e Cloudflare pelo conteúdo; canário por loja (`strata check-stores`). Tem de existir desde o primeiro adaptador.
4. **Falsos exatos (Pitfall 5):** parser determinístico de medidas (m/cm/mm, vírgula, `x`/`×`); "exato" exige todos os atributos iguais, e "desconhecido" passa a parecido. O LLM cita o trecho de onde tirou cada valor. Dados contraditórios (a Bricomarché escreve "2500x125x12") ficam marcados. Conjunto de avaliação com cerca de 100 anúncios.
5. **Otimizador errado nos limites (Pitfall 7):** DP exata com escalões como função preço(qtd), mínimos e múltiplos, stock, limite de compra a mais com a alternativa sem sobras ao lado. Testes com palete ± 1 e com a fronteira de cada escalão.

## Conflitos entre os ficheiros de pesquisa (resolver no planeamento)

| # | Conflito | Posições | Recomendação |
|---|----------|----------|--------------|
| C1 | **Via de extração da Obramat** (decisão do utilizador em aberto) | ARCHITECTURE: `GET /search?q=` (SSR) + JSON `dataTms`, uma chamada por item. PITFALLS: o `robots.txt` proíbe `/search?q=*` e `/pesquisa/`; as páginas `/produtos/*.html` são permitidas e o `sitemap-product1.xml` é público. | **Perguntar ao utilizador antes da fase 2.** Opção A: `/search?q=` (simples e rápido; contraria o robots.txt; aceitável para uso pessoal de baixo volume, segundo a ARCHITECTURE). Opção B: índice local a partir do sitemap (título → URL), pesquisa local e depois a página de produto (respeita o robots.txt; obriga a descarregar e procurar no sitemap). Opção C: descobrir URLs de produto da Obramat via Serper (custo por pesquisa; depende da indexação da Google). Por omissão sugere-se B, com A como alternativa se o utilizador aceitar. |
| C2 | Tolerância do DataDome na Obramat | PITFALLS: `curl` → 403 (riskscore 0,83). STACK: `curl_cffi` → 200. ARCHITECTURE: `requests` com UA de browser → 200 em 3 pedidos. | Usar curl_cffi; a resistência ao longo de uma lista de 10 itens não foi testada. Fazer um spike no início da fase 2. Recurso: Chrome com interface e perfil dedicado (`.claude-chrome`), a ritmo humano; ao primeiro CAPTCHA, marcar "abrir à mão". |
| C3 | Obras 360: API proibida? | PITFALLS: produtos carregados por JS; a API "provavelmente" está em `/restfull/`, proibido. ARCHITECTURE: encontrou `/api/latest/dot/shop/...`, que **não** está proibido. | Seguir a ARCHITECTURE (sondado ao vivo). |
| C4 | Allmat Store API "devolve []" | PITFALLS: `[]` → usar a página de pesquisa. ARCHITECTURE: a Store API funciona (azulejo a 1374 cêntimos = 13,74 € com IVA); `[]` para "osb" porque a Allmat não vende OSB. | Store API. O `[]` é `no_results`. Confirmar com um termo que tenha resultados (canário "cimento"). |
| C5 | Bricomarché: loja preferida vs mínimo | PITFALLS recomenda uma loja configurada; ARCHITECTURE e o utilizador escolhem o mínimo entre todas. | **Decidido pelo utilizador:** mínimo entre todas as lojas físicas, com o nome da loja. Nunca usar o `price` de topo do JSON-LD/Store API; agregar as variações. |
| C6 | Infraestrutura | ARCHITECTURE: httpx, cache SQLite, `stores.toml`, openpyxl. STACK: curl_cffi, sem BD no v1, `stores.json`, XlsxWriter. | Seguir a STACK nas bibliotecas (o httpx é detetado pelo TLS). Cache de LLM e de HTTP em memória por sessão no v1; SQLite só se a cache entre sessões fizer falta (nunca para preços). |

## Implications for Roadmap

Ordem guiada pelas dependências: modelo e normalização antes dos adaptadores, ofertas reais antes do matching, matching antes das embalagens. Cada fase deixa uma ferramenta que corre.

### Phase 1: Núcleo + Woo (Allmat, Bricomarché) + CLI
**Rationale:** o modelo de unidades e IVA custa caro se for corrigido tarde (Recovery HIGH). Duas lojas fixas saem de um único adaptador genérico.
**Delivers:** `core/models` (RawOffer com evidência de IVA, `sale_unit`, `content_qty`, `tiers`, `location`, `fetched_at`), parser de preço PT e de cêntimos com `Decimal`, parser de medidas com testes, Fetcher curl_cffi com limites por host e deteção de bloqueio, `WooStoreApiAdapter` (Bricomarché `type=variation` → mínimo + nome da loja; Allmat com a área da caixa lida da página), estados por loja, CLI `uv run python -m strata "OSB 12mm" 30` com `--record` para fixtures, canário.
**Addresses:** T2, T3 (parcial), T4, T5, T10, T11.
**Avoids:** Pitfalls 1, 2, 3, 4, 6.

### Phase 2: Obras 360 + Obramat + cadeia de recurso
**Rationale:** é onde estão as armadilhas específicas (variantes, IVA, DataDome). Precisa da decisão C1.
**Delivers:** adaptador Beevo (ID do widget lido de `/pesquisa`, expansão de variantes, `DiscountByQuantity`), adaptador Obramat pela via escolhida, executor da cadeia api → jsonld → browser com tentativas registadas, `JsonLdAdapter` genérico (herda a política da loja), canários das 4 lojas.
**Uses:** curl_cffi, Playwright `channel="chrome"` (perfil dedicado) como recurso.
**Avoids:** Pitfalls 4, 8, 13, e as Anti-Patterns 1, 2 e 5.

### Phase 3: Especificações + matching (Haiku; spike Jev)
**Rationale:** precisa de ofertas reais das fases 1–2 para afinar.
**Delivers:** interpretação do pedido (ItemSpec), regex primeiro e Haiku para o resto (com citação do trecho), regra de três estados por atributo, exato/parecido/outro com o texto da diferença, pré-filtro + top-N, orçamento de chamadas e contador, conjunto de avaliação rotulado, spike Haiku vs Jev.
**Addresses:** T1 (interpretação), T6, T7, D3.
**Avoids:** Pitfalls 5, 11, 12.

### Phase 4: Embalagens e custo total
**Rationale:** depende das unidades da fase 1 e dos escalões das fases 1–2.
**Delivers:** conversão entre a unidade pedida e a vendida, DP exata com escalões, mínimos e múltiplos, stock e limite de compra a mais; "comprado vs pedido" e sobras em €.
**Addresses:** T8, D1, D2.
**Avoids:** Pitfall 7.

### Phase 5: UI NiceGUI + progresso + Excel (fecha o v1)
**Rationale:** a UI só serializa ItemResult e o estado. A CLI cobre o desenvolvimento até aqui. Correr o `ui-ux-pro-max` (design system com `--persist`) antes do primeiro ecrã.
**Delivers:** lista colada, progresso item × loja em tempo real, tabela com exatos primeiro e parecidos à parte, estado de todas as lojas fixas sempre visível, exclusão manual, total da lista, aviso "portes não incluídos", Excel com data/hora e lojas que falharam, repetir item/loja.
**Addresses:** T1, T9, T12–T15, D4, D8.

### Phase 6: Descoberta de lojas + PDF
**Rationale:** as lojas descobertas são os dados mais arriscados (IVA, fraude, marketplaces). Só depois de o núcleo dar resultados certos nas lojas fixas.
**Delivers:** Serper `gl=pt` → URLs em domínios novos → deteção de plataforma (Woo / JSON-LD / LLM page, este com corte de tamanho) → mesma normalização e matching, filtro de domínios (comparadores, marketplaces, estrangeiros), "IVA por confirmar", limite de cerca de 5 lojas por item, registo de fiabilidade e sugestão de promover; PDF via `page.pdf()`.
**Addresses:** D5 (degrau IA), D6, D7, D9.
**Avoids:** Pitfalls 9, 10, 11, e a injeção de instruções a partir de HTML desconhecido.

### Phase Ordering Rationale

- `core/` primeiro, porque todos os cálculos de dinheiro dependem dele e é testável sem rede.
- Woo antes de Beevo/ADEO: maior retorno (duas lojas) com menor risco.
- Matching depois de haver ofertas reais; embalagens depois de existirem escalões e unidades.
- Descoberta por último entre as funcionalidades: reutiliza os adaptadores genéricos e a política "IVA unknown".

### Research Flags

Precisam de `/gsd-plan-phase --research-phase`:
- **Phase 2:** decisão C1 da Obramat, onde está a tabela de escalões ("Melhor Preço quantidade" não foi encontrada), tolerância do DataDome ao longo de 10 itens, e se `contextCode=000` dá o preço certo.
- **Phase 4:** fonte de dados dos escalões da Obramat; regras de mínimos e múltiplos por loja.
- **Phase 6:** cobertura real do Serper `/shopping` em lojas PT de obra e custo do `/shopping`.

Padrões conhecidos (dispensam pesquisa): Phase 1 (Store API sondada), Phase 3 (o spike faz parte da fase), Phase 5 (NiceGUI + XlsxWriter).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Versões verificadas no PyPI hoje; curl_cffi testado contra o DataDome. Preços do Serper e do Jev vêm de fontes secundárias; a API 2.x do SDK anthropic está por confirmar. |
| Features | MEDIUM | Padrões dos comparadores confirmados em várias fontes; o valor do D1 (escalões) só está confirmado na Obras 360 e na Obramat ES. |
| Architecture | HIGH (lojas) / MEDIUM (genérico) | Endpoints das 4 lojas chamados ao vivo hoje; os sites mudam, daí os canários. |
| Pitfalls | MEDIUM-HIGH | Factos das lojas verificados em primeira mão; a parte legal é MEDIUM e não constitui aconselhamento jurídico. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Obramat:** via de pesquisa (C1, decisão do utilizador), dados dos escalões, preço por armazém (`contextCode`).
- **Bricomarché:** saber se `orderby=price` funciona com `type=variation` (evitaria paginar, porque cada página demora cerca de 12 s); o IVA é inferido pela lei (B2C), não está declarado na página. Verificar à mão com um produto.
- **Haiku em português e o Jev:** qualidade medida apenas com o conjunto de avaliação da fase 3.
- **Serper:** cobertura de lojas PT de materiais; custo do endpoint `/shopping`.
- **Âmbito legal:** escrever uma nota curta (uso pessoal, ritmo humano, sem CAPTCHA, proxies nem sessões iniciadas) antes da fase 2.

## Sources

### Primary (HIGH confidence)
- Sondas ao vivo a 2026-10-22: `obras360.pt` (API Beevo, `robots.txt`), `obramat.pt` (`/search?q=`, produto, `robots.txt`, cabeçalhos DataDome), `allmat.pt` e `bricomarche.pt` (`/wp-json/wc/store/v1/products`, `robots.txt`), `obra360.pt` (503 SSL).
- PyPI JSON API (versões e `requires_python`); documentação Claude API (Haiku 5.5, `messages.parse`); documentação Vercel AI Gateway (Jev: endpoints, preço, só texto); SerpApi pricing.

### Secondary (MEDIUM confidence)
- InfoQ e flaviocopes sobre o Jev (latência, limitações, registos fechados); Obramat ES ("mejor precio por cantidad", com e sem IVA); DL 138/90, DL 70/2007 / DL 109-G/2021; preços do Serper e do Brave.

### Tertiary (LOW confidence)
- Fórum da Casa (portes da Obras 360), tabela Preceram (paletes cobradas à parte), resumos legais não verificados, comparativos de preços de APIs SERP.

---
*Research completed: 2026-10-22*
*Ready for roadmap: yes*
