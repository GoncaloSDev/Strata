# API Coverage — Obramat, páginas de pesquisa das lojas, Chrome por CDP, API Anthropic e Claude Code (Phase 2)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Superfície = o que cada serviço expõe e serve para obter preços na hora pela cadeia principal → JSON-LD → browser → IA. Carrinho, conta e checkout ficam fora do produto (REQUIREMENTS, Out of Scope).

## Obramat — site (www.obramat.pt)

| capability | decision | reason |
|---|---|---|
| obramat:search-page-ssr | INTEGRATE | |
| obramat:search-datatms-product-list | INTEGRATE | |
| obramat:search-total-and-page-type | INTEGRATE | |
| obramat:vat-ati-and-tf | INTEGRATE | |
| obramat:product-page-quantity-tiers | INTEGRATE | |
| obramat:product-page-store-stock | INTEGRATE | |
| obramat:product-page-jsonld | INTEGRATE | |
| obramat:warehouse-context-detection | INTEGRATE | |
| obramat:search-pagination | OPT-OUT | not needed yet: só a 1.ª página (18 produtos com preço), com nota visível do que fica por ler |
| obramat:lazy-loaded-products | OPT-OUT | not needed yet: pedidos /lazy/…?ktx= com token opaco; a nota conta os produtos não lidos |
| obramat:warehouse-selection | OPT-OUT | not needed: um só armazém em Portugal, escolhido à mão no Chrome dedicado (D-18) |
| obramat:home-delivery-options | OPT-OUT | explicitly out of scope: portes são v2 (COST-01) |
| obramat:cart-and-checkout | OPT-OUT | explicitly out of scope: a app só dá o link, nunca compra |
| obramat:product-reviews | OPT-OUT | not needed: não entra no preço nem na escolha |

## Páginas de pesquisa para pessoas (Allmat, Bricomarché, Obras 360)

| capability | decision | reason |
|---|---|---|
| allmat:search-page-product-links | INTEGRATE | |
| allmat:product-page-jsonld | INTEGRATE | |
| all-stores:search-page-link-for-manual-use | INTEGRATE | |
| all-stores:search-page-text-for-ai | INTEGRATE | |
| bricomarche:search-page-product-links | OPT-OUT | not needed: página montada com JavaScript, sem links no HTML do servidor (D-19) |
| obras360:search-page-product-links | OPT-OUT | not needed: página montada com JavaScript (D-19); o JSON-LD dela é sem IVA |

## Chrome dedicado por CDP (Playwright connect_over_cdp)

| capability | decision | reason |
|---|---|---|
| cdp:connect-over-cdp | INTEGRATE | |
| cdp:default-context-with-profile-cookies | INTEGRATE | |
| cdp:new-page-goto-content-body | INTEGRATE | |
| cdp:wait-for-network-idle | INTEGRATE | |
| cdp:browser-close | INTEGRATE | |
| cdp:start-dedicated-chrome | INTEGRATE | |
| cdp:launch-playwright-browser | OPT-OUT | explicitly out of scope: só o Chrome dedicado do Claude (D-05) |
| cdp:headless-mode | OPT-OUT | explicitly out of scope: janela visível (D-05) |
| cdp:page-input-click-fill | OPT-OUT | explicitly out of scope: nunca interagir com desafios nem CAPTCHA (D-07) |
| cdp:network-interception | OPT-OUT | not needed: a Obramat é HTML do servidor e as APIs JSON leem-se pela navegação |
| cdp:screenshots-and-pdf | OPT-OUT | not needed yet: o PDF é da Phase 5 |
| cdp:anti-detection-patches | OPT-OUT | not needed: o Chrome real com janela passou o DataDome sem ajuda |

## API Anthropic (SDK anthropic)

| capability | decision | reason |
|---|---|---|
| anthropic:messages-create | INTEGRATE | |
| anthropic:structured-output-json-schema | INTEGRATE | |
| anthropic:effort | INTEGRATE | |
| anthropic:sdk-retries | INTEGRATE | |
| anthropic:streaming | OPT-OUT | not needed: resposta curta (até 5 ofertas) |
| anthropic:tool-use | OPT-OUT | explicitly out of scope: sem ferramentas, contra prompt injection (T-02-17) |
| anthropic:prompt-caching | OPT-OUT | not needed: uma chamada por (item, loja), com textos diferentes |
| anthropic:message-batches | OPT-OUT | not needed: preços na hora |
| anthropic:vision-and-files | OPT-OUT | not needed: só texto da página |
| anthropic:messages-parse-pydantic | OPT-OUT | not needed: um só SCHEMA partilhado com o claude -p |
| anthropic:token-counting | OPT-OUT | not needed: corte por caracteres (D-10) |

## Claude Code CLI (claude -p, conta Pro do utilizador)

| capability | decision | reason |
|---|---|---|
| claude:print-mode | INTEGRATE | |
| claude:output-format-json | INTEGRATE | |
| claude:json-schema-structured-output | INTEGRATE | |
| claude:model-selection | INTEGRATE | |
| claude:tools-disabled | INTEGRATE | |
| claude:system-prompt | INTEGRATE | |
| claude:no-session-persistence | INTEGRATE | |
| claude:minimal-bare-mode | OPT-OUT | explicitly out of scope: não lê o login da conta Pro (D-12) |
| claude:setting-sources | OPT-OUT | not needed yet: A6 por confirmar; pode cortar a autenticação |
| claude:sessions-and-resume | OPT-OUT | not needed: cada chamada é independente |
| claude:mcp-and-plugins | OPT-OUT | not needed: sem ferramentas no degrau IA |
| claude:oauth-token-outside-cli | OPT-OUT | explicitly out of scope: contra os termos da Anthropic (D-12) |
| claude:specs-and-classification | OPT-OUT | explicitly out of scope: ideia adiada para a Phase 3 (CONTEXT Deferred) |
