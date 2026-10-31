# Strata

Pega numa lista de compras de obra e procura cada produto na Allmat, na Bricomarché, na Obras 360 e na Obramat. Mostra o preço com IVA, o preço por unidade, o stock e o estado de cada loja.

- `uv run python -m strata modelo` grava `modelo.xlsx` na pasta atual, para preencher uma linha por produto.
- `uv run python -m strata pesquisar modelo.xlsx` pesquisa a folha. Sem ficheiro, cola-se a lista no terminal (ex.: `OSB 12mm 30 un`) e termina-se com uma linha vazia.
- `uv run python -m strata verificar` corre um termo de teste por loja e diz se cada uma ainda devolve preços válidos. Sai com código 1 se alguma falhar.
- `--sem-principal LOJA` (em `pesquisar` e `verificar`) é uma opção de desenvolvimento: desliga o método principal da loja (ex.: `--sem-principal obramat`) para ver o recurso a funcionar.

Uma folha de 10 itens nas 4 lojas demorou 3 min 43 s numa corrida real (outubro de 2026).

## Como cada loja é lida

Cada oferta diz de onde veio o preço: `API`, `JSON-LD`, `browser` ou `IA`. A app começa pelo método principal da loja. Se falhar, tenta o JSON-LD das páginas de produto, depois o Chrome dedicado do Claude e, por fim, a IA.

O Chrome dedicado é um perfil só da app (`%USERPROFILE%\.claude-chrome`, porta 9222), nunca o Chrome de quem usa o PC. Durante a pesquisa aparece uma janela dele. Se não estiver aberto, a app abre-o e fecha-o no fim; para o abrir à mão, corre-se `.claude\claude-chrome.cmd`.

A Obramat vai hoje pelo Chrome dedicado. Os escalões de preço e o stock exato só aparecem com o armazém "OBRAMAT Lisboa - Alfragide" escolhido nesse Chrome; sem ele, a loja diz que o armazém está por escolher e mostra só o preço da pesquisa.

"Abrir à mão" com um link quer dizer que a loja pediu um CAPTCHA. Até ao fim dessa execução, a app não lhe faz mais pedidos; o link abre a mesma pesquisa no browser.

Uma oferta "lido por IA" fica sempre no fim da loja, mesmo que seja mais barata, e o preço deve ser confirmado na página. A IA usa a API da Anthropic quando `ANTHROPIC_API_KEY` está definida. Sem a chave, usa o `claude` (Claude Code) com a conta de quem usa o PC. Sem nenhum dos dois, a loja mostra "IA não configurada".

## Âmbito e acesso às lojas

O Strata é para uso pessoal. Faz poucos pedidos, a ritmo humano, com um limite por loja: na Obramat vai um pedido de cada vez, com 3 a 5 s entre eles. Se uma loja mostrar um CAPTCHA, a app não o resolve nem fica à espera; a loja fica marcada como "abrir à mão". A app não usa proxies, não troca de identidade e não inicia sessão em nenhuma loja.

A Obramat é lida pela pesquisa do próprio site (`/search`), que o robots.txt dela não abre a robôs. Lê-la na mesma foi uma decisão consciente, por ser uso pessoal e com volume baixo. Os preços ficam no PC e nada é republicado.
