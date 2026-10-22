# Strata

## What This Is

Ferramenta pessoal, para usar no PC, que recebe uma lista de compras de obra (produto + quantidade) e procura cada produto em lojas online portuguesas para encontrar o fornecedor mais barato. Os preços são normalizados com IVA (23%) e por unidade, e o custo é calculado para a quantidade pedida (ex.: uma palete de 50 pode sair mais barata do que 30 avulsas). Serve materiais de construção, bricolage e também mobília, sem categorias fixas no código.

## Core Value

Para cada produto da lista, mostrar o custo total mais baixo real (com IVA, para a quantidade pedida) entre as lojas portuguesas, com link para comprar: igual ou mais barato do que uma pesquisa feita à mão, e em minutos em vez de horas.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Introduzir uma lista de compras com vários produtos, cada um com a sua quantidade
- [ ] Pesquisa em texto livre para qualquer produto (OSB, tijolo, mesa, mobília...), sem categorias fixas no código
- [ ] Obter preços das lojas fixas: Obras 360, Obramat, Allmat, Bricomarché
- [ ] Descobrir automaticamente outras lojas online portuguesas que vendem o produto
- [ ] Recolher preços na hora da pesquisa (não de uma base de dados pré-recolhida)
- [ ] Normalizar todos os preços para "com IVA 23%", detetando se cada loja mostra o preço com ou sem IVA
- [ ] Calcular preço por unidade normalizado (unidade, m², pack, palete)
- [ ] Escolher a combinação de embalagens (avulso, pack, palete) com menor custo total para a quantidade pedida, mesmo que implique comprar a mais
- [ ] Mostrar primeiro os produtos exatos e, à parte, os parecidos, marcados com a diferença (ex.: 2,44×1,22 m em vez de 2,5×1,25 m)
- [ ] Mostrar o stock quando o site o indica (sem filtrar)
- [ ] Tabela por produto ordenada por custo total, com link para a página da loja
- [ ] Exportar a lista com os resultados para Excel/PDF
- [ ] Quando uma loja falha ou bloqueia, tentar outra via (browser automático, IA) antes de desistir; se mesmo assim falhar, marcar a falha de forma visível
- [ ] Sugerir passar para a lista fixa as lojas descobertas que funcionam bem

### Out of Scope

- Portes de entrega / custo entregue na obra — v1 compara só o preço do produto; pode vir depois
- Agrupar compras por loja (minimizar nº de lojas) — só se se verificar que comprar vários produtos num fornecedor dá descontos
- Lojas sem site (madeireiras locais, pedidos de orçamento) — sem preços publicados, não dá para automatizar
- Histórico de pesquisas e evolução de preços — não pedido para v1
- Base de dados de preços pré-recolhidos — o utilizador quer preços na hora
- Contas, multiutilizador, app pública — ferramenta pessoal
- Versão para telemóvel — uso no PC
- IVA da Madeira (22%) e dos Açores (16%) — só continente, 23%
- Filtrar por stock — só mostrar

## Context

- **Utilizador:** compra materiais para obras. Hoje compara preços abrindo vários sites à mão.
- **Lojas fixas iniciais:** Obras 360 (`obras360.pt`, confirmado pelo utilizador; não `obra360.pt`), Obramat (`obramat.pt`), Allmat (`allmat.pt`, confirmado pelo utilizador), Bricomarché (`bricomarche.pt`).
- **Bricomarché tem preço por loja física** (a mesma placa varia entre lojas). Decisão do utilizador: usar o mais barato entre todas as lojas Bricomarché e mostrar qual é a loja.
- **IVA:** algumas lojas (sobretudo as orientadas a profissionais) mostram preços sem IVA e outras com IVA. Comparar sem normalizar dá resultados errados, por isso este é um ponto crítico.
- **Extração de preços nas lojas fixas (abordagem discutida, por ordem de preferência):**
  1. API interna de pesquisa que o próprio site usa (Algolia, Doofinder, Magento, VTEX...) → JSON com nome, preço, stock
  2. Dados estruturados `schema.org/Product` (JSON-LD) na página do produto
  3. Browser automático (Playwright) para sites com JavaScript ou que bloqueiam pedidos simples
  4. IA a ler o texto da página, como último recurso
- **Descoberta de lojas novas:** API de pesquisa com resultados de shopping, filtrada para Portugal (ex.: Google Shopping via SerpAPI/Serper, Brave Search), seguida do leitor genérico JSON-LD na página do produto.
- **IA:** extrair especificações do título do anúncio (espessura, medidas, unidade, quantidade por pack) e classificar cada anúncio como exato / parecido / outro. O utilizador sugeriu o **Jev** da TypeSafe AI (lançado a 15 set 2026; devolve decisões tipadas com probabilidade calibrada, 70–500 ms segundo o fabricante). É um candidato a validar na pesquisa.
- **Riscos conhecidos:** proteção anti-bot (ex.: Cloudflare) em algumas lojas; sites que mudam e partem adaptadores sem aviso; termos de uso. Uso pessoal com poucos pedidos e ritmo respeitador por loja.

## Constraints

- **Plataforma**: PC — o utilizador prepara as compras em casa/escritório
- **Orçamento**: aceita pagar APIs de pesquisa e de IA, com preferência por opções baratas — ferramenta pessoal
- **Latência**: preços na hora; uma lista de ~10 produtos deve resolver-se em minutos — critério de sucesso
- **Fiscal**: IVA 23% (Portugal continental), preços em EUR — mercado-alvo
- **Mercado**: só lojas online que vendem em Portugal — âmbito do produto
- **Acesso às lojas**: volume baixo, respeitar o ritmo de cada site, nunca omitir falhas em silêncio — evitar bloqueios e resultados enganadores

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Ferramenta pessoal, não produto público | Uso próprio nas obras do utilizador | — Pending |
| Preços na hora em vez de base de dados | O preço tem de estar atualizado no momento da compra | — Pending |
| Lista fixa de 4 lojas + descoberta automática | Lojas de confiança garantidas + cobertura nacional | — Pending |
| Normalizar tudo para preço com IVA 23% | As lojas misturam preços com e sem IVA | — Pending |
| Exatos e parecidos separados | Não perder alternativas mais baratas com medidas próximas, sem as confundir com o pedido | — Pending |
| Otimizar a embalagem pela quantidade pedida | Uma palete pode sair mais barata do que unidades avulsas | — Pending |
| Em falha, tentar outra via antes de desistir | Uma loja em falta pode esconder o preço mais baixo | — Pending |
| Jev (TypeSafe AI) como candidato para classificar anúncios | Sugestão do utilizador; barato e feito para decisões tipadas | — Pending |
| Sem categorias fixas no código | Tem de encontrar tijolos, OSB e também mobília | — Pending |
| Bricomarché: preço mais barato entre todas as lojas físicas, com o nome da loja | O preço varia por loja; o utilizador quer o mínimo | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-22 after initialization*
