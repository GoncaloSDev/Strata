# Requirements: Strata

**Defined:** 2026-10-22
**Core Value:** Para cada produto da lista, mostrar o custo total mais baixo real (com IVA, para a quantidade pedida) entre as lojas portuguesas, com link para comprar: igual ou mais barato do que uma pesquisa feita à mão, e em minutos em vez de horas.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Lista e pesquisa

- [x] **LIST-01**: Utilizador cola uma lista multilinha em que cada linha tem descrição em texto livre, quantidade e unidade (un, m², m, kg, L, saco)
- [x] **LIST-02**: Utilizador pesquisa qualquer produto em texto livre (OSB, tijolo, mesa, mobília...) sem escolher categoria
- [ ] **LIST-03**: Uma lista de 10 itens fica resolvida nas 4 lojas fixas em menos de 5 minutos
- [x] **LIST-04**: Utilizador obtém da app um modelo Excel de formato fixo com as colunas Produto, Família, Tamanho, Unidade, Qty (obrigatórias: Produto, Unidade, Qty) e as opcionais Referência (EAN/ref. do fabricante) e Notas
- [x] **LIST-05**: Utilizador carrega uma folha Excel nesse formato e cada linha passa a ser um item da pesquisa (entrada principal da app); linhas inválidas são assinaladas com o número da linha e o motivo, sem parar as restantes
- [ ] **LIST-06**: Família, Tamanho e Referência da folha são usados como contexto na pesquisa e na classificação exato/parecido, sem categorias fixas no código

### Lojas fixas

- [x] **STORE-01**: Utilizador obtém preços na hora da Bricomarché, com o preço mais barato entre todas as lojas físicas e o nome dessa loja
- [x] **STORE-02**: Utilizador obtém preços na hora da Allmat, com o preço por caixa convertido usando a área/conteúdo da caixa
- [ ] **STORE-03**: Utilizador obtém preços na hora da Obras 360, com todas as variantes do produto expandidas e os escalões por quantidade
- [ ] **STORE-04**: Utilizador obtém preços na hora da Obramat através da pesquisa direta do site, a ritmo lento (um pedido de cada vez)
- [ ] **STORE-05**: Utilizador vê, por item, o estado de cada loja fixa (ok / sem resultados / bloqueada / erro / tempo esgotado); nenhuma loja fixa é omitida
- [ ] **STORE-06**: Quando o método principal de uma loja falha, a app tenta JSON-LD, browser automático e IA antes de marcar a falha, e mostra que método funcionou
- [ ] **STORE-07**: Utilizador corre uma verificação das lojas que diz se cada adaptador ainda devolve preços válidos

### Descoberta de lojas

- [ ] **DISC-01**: A app encontra outras lojas online portuguesas que vendem o produto e mostra as ofertas delas marcadas como "descoberta"
- [ ] **DISC-02**: Comparadores, marketplaces e lojas estrangeiras ficam fora da descoberta
- [ ] **DISC-03**: Ofertas de lojas descobertas sem prova do IVA ficam marcadas "IVA por confirmar" e nunca aparecem como a mais barata
- [ ] **DISC-04**: A app sugere passar para a lista fixa as lojas descobertas que funcionam bem, com base no registo de sucessos/falhas

### Preço

- [ ] **PRICE-01**: Todos os preços aparecem com IVA 23%; preços sem IVA são convertidos e cada linha mostra a origem do IVA (indicado pela loja / regra da loja / assumido)
- [ ] **PRICE-02**: Cada oferta mostra o preço unitário normalizado (€/un, €/m², €/m, €/kg, €/L), calculado a partir do preço e do conteúdo da embalagem
- [ ] **PRICE-03**: A quantidade pedida é convertida para a unidade vendida (m² → caixas, m → varas, un → packs); se a conversão for impossível, a linha diz porquê
- [ ] **PRICE-04**: Utilizador vê o custo total para a quantidade pedida com a combinação de embalagens e escalões mais barata (mesmo que compre a mais), com quantidade comprada vs pedida e sobras
- [ ] **PRICE-05**: Utilizador vê quanto poupa com o parecido mais barato face ao exato mais barato

### Correspondência

- [ ] **MATCH-01**: A app extrai as especificações de cada anúncio (espessura, medidas, material, unidade de venda, quantidade por embalagem), com regras primeiro e IA para o resto
- [ ] **MATCH-02**: Cada anúncio é classificado como exato / parecido / outro; um atributo desconhecido nunca dá "exato"
- [ ] **MATCH-03**: Utilizador vê os parecidos à parte dos exatos, com a diferença escrita (ex.: "2,44×1,22 m em vez de 2,5×1,25 m")
- [ ] **MATCH-04**: Utilizador exclui um resultado ("isto não é o produto") e o mais barato e o total são recalculados
- [ ] **MATCH-05**: Cada linha mostra a origem do preço e das especificações (API / JSON-LD / browser / IA)
- [ ] **MATCH-06**: A classificação é avaliada num conjunto de ~50 anúncios portugueses rotulados, comparando Claude Haiku e Jev, e o modelo escolhido fica registado

### Resultados

- [ ] **RES-01**: Utilizador vê, por item, uma tabela ordenada por custo total com loja, título, classe, embalagem, quantidade comprada, €/unidade, custo total com IVA, link e hora da recolha
- [ ] **RES-02**: Utilizador vê o stock quando a loja o indica (em stock / esgotado / quantidade / desconhecido), sem filtrar
- [ ] **RES-03**: Utilizador vê o total da lista (soma do exato mais barato de cada item) com o aviso "portes não incluídos"
- [ ] **RES-04**: Utilizador vê o progresso por item × loja em tempo real, com os resultados a aparecer à medida que chegam
- [ ] **RES-05**: Utilizador repete só um item ou só uma loja sem refazer a lista toda
- [ ] **RES-06**: Utilizador exporta para Excel: folha com o melhor por item e o total, folha com todos os resultados, links clicáveis, data/hora e lojas que falharam
- [ ] **RES-07**: Utilizador exporta os resultados para PDF
- [ ] **RES-08**: Utilizador recebe a sua folha Excel original preenchida com colunas novas (melhor custo total, loja, link, classe exato/parecido, preço unitário), mantendo as colunas e a ordem das linhas originais

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Custos extra

- **COST-01**: Utilizador vê o custo entregue na obra (produto + portes por código postal)
- **COST-02**: Utilizador vê a melhor combinação comprando em menos lojas, se houver descontos por compra conjunta

### Conveniência

- **CONV-01**: Utilizador guarda listas de entrada para reutilizar

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Lojas sem site (madeireiras, pedidos de orçamento) | Sem preços publicados, não dá para automatizar |
| Histórico de preços e alertas | Não pedido; obriga a guardar dados e a correr em segundo plano |
| Base de dados de preços pré-recolhidos | O utilizador quer preços na hora; um catálogo desatualizado mostra o preço errado |
| Árvore de categorias e filtros por especificação | Parte com produtos novos (mobília, tijolo); texto livre + especificações cobre o caso |
| Filtrar por stock | Esconder linhas esconde preços; o stock é só mostrado |
| Esconder lojas que falham | Uma loja escondida pode ter o preço mais baixo |
| Pôr no carrinho / comprar automaticamente | Risco de compras erradas e de violar termos de uso; basta o link |
| Contas, multiutilizador, telemóvel, códigos de barras | Ferramenta pessoal no PC |
| IVA da Madeira e dos Açores | Só continente (23%); outras taxas explícitas são assinaladas, não convertidas |
| Proxies, resolvedores de CAPTCHA, sessões autenticadas nas lojas | Uso pessoal a ritmo humano; ao primeiro CAPTCHA a loja fica marcada "abrir à mão" |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| LIST-01 | Phase 1 | Complete |
| LIST-02 | Phase 1 | Complete |
| LIST-03 | Phase 2 | Pending |
| LIST-04 | Phase 1 | Complete |
| LIST-05 | Phase 1 | Complete |
| LIST-06 | Phase 3 | Pending |
| STORE-01 | Phase 1 | Complete |
| STORE-02 | Phase 1 | Complete |
| STORE-03 | Phase 1 | Pending |
| STORE-04 | Phase 2 | Pending |
| STORE-05 | Phase 1 | Pending |
| STORE-06 | Phase 2 | Pending |
| STORE-07 | Phase 1 | Pending |
| DISC-01 | Phase 6 | Pending |
| DISC-02 | Phase 6 | Pending |
| DISC-03 | Phase 6 | Pending |
| DISC-04 | Phase 6 | Pending |
| PRICE-01 | Phase 1 | Pending |
| PRICE-02 | Phase 1 | Pending |
| PRICE-03 | Phase 4 | Pending |
| PRICE-04 | Phase 4 | Pending |
| PRICE-05 | Phase 4 | Pending |
| MATCH-01 | Phase 3 | Pending |
| MATCH-02 | Phase 3 | Pending |
| MATCH-03 | Phase 3 | Pending |
| MATCH-04 | Phase 5 | Pending |
| MATCH-05 | Phase 3 | Pending |
| MATCH-06 | Phase 3 | Pending |
| RES-01 | Phase 5 | Pending |
| RES-02 | Phase 1 | Pending |
| RES-03 | Phase 4 | Pending |
| RES-04 | Phase 5 | Pending |
| RES-05 | Phase 5 | Pending |
| RES-06 | Phase 5 | Pending |
| RES-07 | Phase 5 | Pending |
| RES-08 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 36 total
- Mapped to phases: 36
- Unmapped: 0 ✓

---
*Requirements defined: 2026-10-22*
*Last updated: 2026-10-22 after roadmap revision (folha Excel como entrada principal)*
