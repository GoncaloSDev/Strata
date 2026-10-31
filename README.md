# Strata

Pega numa lista de compras de obra e procura cada produto na Allmat, na Bricomarché e na Obras 360. Mostra o preço com IVA, o preço por unidade, o stock e o estado de cada loja.

- `uv run python -m strata modelo` grava `modelo.xlsx` na pasta atual, para preencher uma linha por produto.
- `uv run python -m strata pesquisar modelo.xlsx` pesquisa a folha. Sem ficheiro, cola-se a lista no terminal (ex.: `OSB 12mm 30 un`) e termina-se com uma linha vazia.
- `uv run python -m strata verificar` corre um termo de teste por loja e diz se cada uma ainda devolve preços válidos. Sai com código 1 se alguma falhar.

## Âmbito e acesso às lojas

O Strata é para uso pessoal. Faz poucos pedidos, a ritmo humano, com um limite por loja: na Obramat vai um pedido de cada vez, com 3 a 5 s entre eles. Se uma loja mostrar um CAPTCHA, a app não o resolve nem fica à espera; a loja fica marcada como "abrir à mão". A app não usa proxies, não troca de identidade e não inicia sessão em nenhuma loja.

A Obramat é lida pela pesquisa do próprio site (`/search`), que o robots.txt dela não abre a robôs. Lê-la na mesma foi uma decisão consciente, por ser uso pessoal e com volume baixo. Os preços ficam no PC e nada é republicado.
