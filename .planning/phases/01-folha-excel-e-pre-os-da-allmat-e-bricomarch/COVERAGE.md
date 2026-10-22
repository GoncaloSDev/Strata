# API Coverage — Allmat, Bricomarché e Obras 360 (Phase 1)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Superfície = o que cada loja expõe e que serve para obter preços na hora; carrinho, conta e checkout ficam fora do produto (REQUIREMENTS, Out of Scope: "Pôr no carrinho / comprar automaticamente").

## Allmat — WooCommerce Store API + páginas de produto (allmat.pt)

| capability | decision | reason |
|---|---|---|
| allmat:products-search | INTEGRATE | |
| allmat:products-pagination | INTEGRATE | |
| allmat:price-cents-and-vat-rule | INTEGRATE | |
| allmat:stock-availability-text | INTEGRATE | |
| allmat:price-unit-label | INTEGRATE | |
| allmat:product-page-box-area | INTEGRATE | |
| allmat:product-variations | OPT-OUT | not needed: 0 produtos variable em 3704 (sondado); só há simple |
| allmat:orderby-price | OPT-OUT | not needed: a ordem faz-se cá dentro pelo preço na unidade pedida (D-03) |
| allmat:category-and-attribute-filters | OPT-OUT | explicitly out of scope: sem categorias fixas (LIST-02, D-13) |
| allmat:cart-and-checkout | OPT-OUT | explicitly out of scope: a app só dá o link, nunca compra |
| allmat:product-reviews | OPT-OUT | not needed: não entra no preço nem na escolha |

## Bricomarché — WooCommerce Store API (www.bricomarche.pt)

| capability | decision | reason |
|---|---|---|
| bricomarche:parent-products-search | INTEGRATE | |
| bricomarche:parent-products-pagination | INTEGRATE | |
| bricomarche:variations-by-parent | INTEGRATE | |
| bricomarche:variations-pagination | INTEGRATE | |
| bricomarche:per-store-price-and-name | INTEGRATE | |
| bricomarche:per-store-stock-text | INTEGRATE | |
| bricomarche:per-store-product-link | INTEGRATE | |
| bricomarche:search-with-type-variation | OPT-OUT | not needed: cerca de 10 s por página; o caminho pais → variações por parent dá o mesmo mínimo em 5 s |
| bricomarche:orderby-price | OPT-OUT | not needed: não ordena com type=variation (sondado); lêem-se todas as páginas |
| bricomarche:store-selection-cookie | OPT-OUT | not needed: o link /{loja}/produto/{slug}/ abre a loja certa sem cookie |
| bricomarche:cart-and-checkout | OPT-OUT | explicitly out of scope: a app só dá o link, nunca compra |
| bricomarche:category-filters | OPT-OUT | explicitly out of scope: sem categorias fixas (LIST-02, D-13) |

## Obras 360 — Beevo shop API (www.obras360.pt)

| capability | decision | reason |
|---|---|---|
| obras360:search-widget-id | INTEGRATE | |
| obras360:product-list-search | INTEGRATE | |
| obras360:product-list-pagination | INTEGRATE | |
| obras360:product-details-variants | INTEGRATE | |
| obras360:net-price-and-tax-percentage | INTEGRATE | |
| obras360:conversion-factor-and-sell-units | INTEGRATE | |
| obras360:variant-stock-and-availability-message | INTEGRATE | |
| obras360:discount-by-quantity-tiers | INTEGRATE | |
| obras360:apply-tiers-to-total-cost | OPT-OUT | not needed yet: aplicar escalões ao custo total é a Phase 4 (PRICE-04); aqui só se mostram |
| obras360:min-and-multiple-purchase-quantity | OPT-OUT | not needed yet: mínimos e múltiplos de compra entram no custo total da Phase 4 |
| obras360:other-discount-classes | OPT-OUT | not needed: só DiscountByQuantity foi visto nas sondas; outro formato aparece numa nota visível |
| obras360:category-and-filter-params | OPT-OUT | explicitly out of scope: sem categorias fixas (LIST-02, D-13) |
| obras360:product-media | OPT-OUT | not needed: a saída é texto no terminal |
| obras360:cart-and-checkout | OPT-OUT | explicitly out of scope: a app só dá o link, nunca compra |
