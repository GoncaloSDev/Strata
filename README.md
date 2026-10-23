# Strata

Pega numa lista de compras de obra e procura cada produto na Allmat, na Bricomarché e na Obras 360. Mostra o preço com IVA, o preço por unidade, o stock e o estado de cada loja.

- `uv run python -m strata modelo` grava `modelo.xlsx` na pasta atual, para preencher uma linha por produto.
- `uv run python -m strata pesquisar modelo.xlsx` pesquisa a folha. Sem ficheiro, cola-se a lista no terminal (ex.: `OSB 12mm 30 un`) e termina-se com uma linha vazia.
- `uv run python -m strata verificar` corre um termo de teste por loja e diz se cada uma ainda devolve preços válidos. Sai com código 1 se alguma falhar.
