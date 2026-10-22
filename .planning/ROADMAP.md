# Roadmap: Strata

## Overview

O Strata começa pela folha Excel, que é a base da aplicação: a app dá um modelo de formato fixo, o utilizador preenche-o e a linha de comandos lê-o e procura cada linha na Allmat e na Bricomarché (as duas lojas que partilham a mesma API) e na Obras 360 (API própria, com as variantes expandidas), já com o dinheiro certo (IVA 23%, unidades, preço unitário). O texto colado fica como entrada secundária para pesquisas rápidas. Depois junta a loja difícil (Obramat) e a cadeia de recurso, até uma folha de 10 itens se resolver nas 4 lojas fixas em menos de 5 minutos. Com ofertas reais na mão, vem a classificação exato/parecido (com Família, Tamanho e Referência da folha como contexto), a seguir o custo total para a quantidade pedida (embalagens e escalões) com a folha original devolvida preenchida, depois a app local no browser com progresso e exportação detalhada, e por fim a descoberta de outras lojas portuguesas.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Folha Excel e preços da Allmat, Bricomarché e Obras 360** - Modelo Excel e leitura da folha na linha de comandos (texto colado como pesquisa rápida), preços na hora das duas lojas Woo e da Obras 360, com IVA 23%, preço unitário e estado por loja
- [ ] **Phase 2: Obramat e cadeia de recurso** - As 4 lojas fixas respondem para uma folha de 10 itens em menos de 5 minutos, com recurso a JSON-LD, browser e IA
- [ ] **Phase 3: Especificações e classificação exato/parecido** - Exatos primeiro, parecidos à parte com a diferença escrita, sem falsos exatos; Família, Tamanho e Referência da folha como contexto; teste Haiku vs Jev
- [ ] **Phase 4: Embalagens, custo total e folha preenchida** - Custo total mais baixo para a quantidade pedida, com embalagens e escalões, poupança do parecido, total da lista e a folha original devolvida preenchida
- [ ] **Phase 5: App no browser e exportação** - App local com a folha Excel, progresso em tempo real, tabela por item, exclusão de resultados, repetição seletiva, Excel detalhado e PDF
- [ ] **Phase 6: Descoberta de lojas** - Outras lojas online portuguesas marcadas como "descoberta", com IVA por confirmar e sugestão de as passar a fixas

## Phase Details

### Phase 1: Folha Excel e preços da Allmat, Bricomarché e Obras 360

**Goal**: O utilizador preenche o modelo Excel da app, passa o caminho do `.xlsx` à linha de comandos e recebe, para cada linha, os preços na hora da Allmat, da Bricomarché e da Obras 360, já com IVA 23% e preço unitário normalizado, com o estado de cada loja sempre visível; para uma pesquisa rápida pode colar texto em vez da folha
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: LIST-01, LIST-02, LIST-04, LIST-05, STORE-01, STORE-02, STORE-03, STORE-05, STORE-07, PRICE-01, PRICE-02, RES-02
**Success Criteria** (what must be TRUE):
  1. O utilizador obtém da app o modelo Excel (Produto, Família, Tamanho, Unidade, Qty, Referência, Notas), preenche-o e corre a linha de comandos com o caminho do `.xlsx`; cada linha válida passa a ser um item, e uma linha sem Produto, Unidade ou Qty (ou com Qty que não é um número positivo, ou Unidade desconhecida) aparece assinalada com o número da linha e o motivo, sem parar as restantes
  2. Para uma pesquisa rápida, o utilizador cola em vez disso uma lista multilinha (ex.: "OSB 12mm 30 un", "cimento 10 saco") e cada linha é lida com descrição, quantidade e unidade; nas duas entradas, qualquer produto em texto livre é pesquisado sem escolher categoria
  3. A Bricomarché devolve o preço mais barato entre todas as lojas físicas, com o nome dessa loja e o link para a página do produto nessa loja; a Allmat devolve o preço por caixa convertido com a área/conteúdo da caixa; a Obras 360 devolve todas as variantes do produto como ofertas separadas (ex.: OSB 9, 12 e 15 mm, cada uma com o seu preço), com os preços sem IVA da loja convertidos para IVA 23% e os escalões por quantidade mostrados quando existem
  4. Cada oferta mostra o preço com IVA 23%, a origem do IVA (indicado pela loja / regra da loja / assumido), o preço unitário normalizado (€/un, €/m², €/m, €/kg, €/L) e o stock quando a loja o indica, sem filtrar
  5. Cada item mostra o estado das três lojas (ok / sem resultados / bloqueada / erro / tempo esgotado), por exemplo "OSB" na Allmat aparece como "sem resultados", nunca como erro nem omitido; e a verificação das lojas diz, por adaptador, se ainda devolve preços válidos (preço acima de zero, IVA e unidade coerentes)

**Plans:** 6 plans

Plans:
**Wave 1**
- [ ] 01-01-PLAN.md — Esqueleto: modelo Excel → pesquisar folha → Allmat no terminal, provado ao vivo (checkpoint de pacotes + tracer)

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 01-02-PLAN.md — Testes sem rede do esqueleto (FakeFetcher, modelo), folha validada linha a linha e texto colado no terminal

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 01-03-PLAN.md — Pesquisa alargada, filtro de título, ordem por unidade pedida, caixas da Allmat e estados de loja

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 01-04-PLAN.md — Bricomarché: mais barato entre lojas físicas, com loja, link e stock

**Wave 5** *(blocked on Wave 4 completion)*
- [ ] 01-05-PLAN.md — Obras 360: uma oferta por variante, IVA da loja, escalões e stock

**Wave 6** *(blocked on Wave 5 completion)*
- [ ] 01-06-PLAN.md — Comando verificar e corrida completa das três lojas

**Stack note**: ler a folha do utilizador obriga a usar openpyxl (o XlsxWriter, escolhido no STACK.md, só escreve ficheiros novos e não lê `.xlsx`); gerar o modelo com o mesmo openpyxl evita uma segunda biblioteca Excel

### Phase 2: Obramat e cadeia de recurso

**Goal**: As 4 lojas fixas respondem na hora para uma lista inteira em menos de 5 minutos, e uma loja que falha pelo método principal é tentada por outras vias antes de ser marcada como falhada
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: STORE-04, STORE-06, LIST-03
**Success Criteria** (what must be TRUE):
  1. A Obramat devolve preços através da pesquisa direta do site, um pedido de cada vez; ao primeiro CAPTCHA a loja fica marcada "abrir à mão", com o link, e o resto da lista continua
  2. Quando o método principal de uma loja falha (ex.: desativado à força num teste), a app tenta JSON-LD, browser automático e IA, por esta ordem, e cada oferta mostra o método que funcionou; se todos falharem, a loja aparece como falhada com o motivo
  3. Uma folha Excel de 10 itens fica resolvida nas 4 lojas fixas em menos de 5 minutos, cada item mostra o estado das 4 lojas e a verificação das lojas cobre as 4

**Plans**: TBD
**Research flag**: yes — tolerância do DataDome da Obramat ao longo de uma lista de 10 itens; onde está a tabela de escalões da Obramat; se `contextCode=000` dá o preço certo

### Phase 3: Especificações e classificação exato/parecido

**Goal**: Para cada item, o utilizador vê primeiro os anúncios que são exatamente o produto pedido e, à parte, os parecidos com a diferença escrita, sem falsos exatos, usando a Família, o Tamanho e a Referência da folha como contexto
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: MATCH-01, MATCH-02, MATCH-03, MATCH-05, MATCH-06, LIST-06
**Success Criteria** (what must be TRUE):
  1. Cada anúncio mostra as especificações extraídas (espessura, medidas, material, unidade de venda, quantidade por embalagem) e cada linha mostra a origem do preço e das especificações (API / JSON-LD / browser / IA)
  2. Cada anúncio fica classificado como exato / parecido / outro; um anúncio a que falte um atributo pedido (ex.: espessura desconhecida) nunca aparece como exato; os parecidos aparecem à parte dos exatos, com a diferença escrita (ex.: "2,44×1,22 m em vez de 2,5×1,25 m")
  3. A Família, o Tamanho e a Referência da folha entram na pesquisa e na classificação: o Tamanho (ex.: "2500×1250×12 mm") decide se as medidas de um anúncio batem, e a Referência (EAN/ref. do fabricante), quando preenchida, é pesquisada nas lojas e comparada com a do anúncio; nada disto depende de categorias fixas no código
  4. Existe um conjunto de cerca de 50 anúncios portugueses rotulados; a classificação é medida com Claude Haiku e com Jev, e o modelo escolhido fica registado com os resultados
  5. Com a classificação ativa, a lista de 10 itens continua resolvida nas 4 lojas fixas em menos de 5 minutos

**Plans**: TBD

### Phase 4: Embalagens, custo total e folha preenchida

**Goal**: Para cada item, o utilizador vê o custo total real para a quantidade pedida, com a combinação de embalagens e escalões mais barata, e o total da lista inteira, e recebe a sua folha Excel de volta com o melhor resultado de cada linha
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: PRICE-03, PRICE-04, PRICE-05, RES-03, RES-08
**Success Criteria** (what must be TRUE):
  1. A quantidade pedida é convertida para a unidade vendida (ex.: 30 m² → 21 caixas de 1,44 m²; 50 m → 17 varas de 3 m); quando a conversão é impossível, a linha diz porquê em vez de mostrar um custo
  2. Cada oferta mostra o custo total com IVA para a quantidade pedida, com a combinação mais barata de avulso, packs, paletes e escalões (mesmo que compre a mais), a quantidade comprada vs pedida e as sobras
  3. Pedidos nos limites (uma unidade abaixo ou acima de uma palete, a fronteira de um escalão) dão o custo mais baixo correto; quando a palete sai mais barata do que as unidades avulsas, é ela a escolhida
  4. Cada item mostra quanto se poupa com o parecido mais barato face ao exato mais barato, e a lista mostra o total (soma do exato mais barato de cada item) com o aviso "portes não incluídos"
  5. O utilizador recebe a sua folha Excel com colunas novas (melhor custo total, loja, link, classe exato/parecido, preço unitário), com as colunas e a ordem das linhas originais intactas; as linhas inválidas ficam com o motivo em vez de um preço, e o ficheiro original nunca é sobrescrito (o resultado é uma cópia ao lado)

**Plans**: TBD
**Research flag**: yes — fonte dos escalões da Obramat; regras de mínimos e múltiplos de compra por loja
**Stack note**: escrever na folha do próprio utilizador obriga a usar openpyxl (o XlsxWriter não abre ficheiros existentes); o openpyxl perde imagens e gráficos ao gravar, por isso o resultado vai sempre para uma cópia

### Phase 5: App no browser e exportação

**Goal**: O utilizador faz tudo numa app local no browser: carrega a folha Excel (ou cola texto), acompanha a pesquisa em tempo real, ajusta os resultados e exporta para Excel e PDF
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: RES-01, RES-04, RES-05, RES-06, RES-07, MATCH-04
**Success Criteria** (what must be TRUE):
  1. O utilizador descarrega o modelo na app, carrega a folha preenchida (ou cola texto para uma pesquisa rápida) e vê o progresso item × loja em tempo real, com os resultados a aparecer à medida que chegam
  2. Cada item tem uma tabela ordenada por custo total com loja, título, classe, embalagem, quantidade comprada, €/unidade, custo total com IVA, link e hora da recolha; exatos primeiro, parecidos à parte e o estado de todas as lojas fixas visível
  3. O utilizador exclui um resultado ("isto não é o produto") e o mais barato do item e o total da lista são recalculados
  4. O utilizador repete só um item ou só uma loja sem refazer a lista toda
  5. O utilizador descarrega a sua folha preenchida e exporta para Excel detalhado (folha com o melhor por item e o total, folha com todos os resultados, links clicáveis, data/hora e lojas que falharam) e para PDF

**Plans**: TBD
**UI hint**: yes
**Stack note**: a exportação detalhada (RES-06) pode usar o openpyxl que já entra nas Phases 1 e 4, em vez de juntar o XlsxWriter só para isto

### Phase 6: Descoberta de lojas

**Goal**: Além das 4 lojas fixas, a app encontra outras lojas online portuguesas que vendem o produto, mostra as ofertas delas sem estragar a comparação e sugere as que merecem passar a fixas
**Mode:** mvp
**Depends on**: Phase 5
**Requirements**: DISC-01, DISC-02, DISC-03, DISC-04
**Success Criteria** (what must be TRUE):
  1. Para cada item aparecem ofertas de outras lojas online portuguesas, marcadas como "descoberta", com a mesma normalização e classificação das lojas fixas
  2. Comparadores (ex.: KuantoKusta), marketplaces e lojas estrangeiras nunca aparecem como lojas descobertas
  3. Uma oferta de loja descoberta sem prova do IVA aparece marcada "IVA por confirmar" e nunca fica como a mais barata do item
  4. A app sugere passar para a lista fixa as lojas descobertas que funcionam bem e mostra o registo de sucessos/falhas que justifica a sugestão
  5. A descoberta não atrasa as lojas fixas: a lista de 10 itens continua resolvida nas 4 lojas fixas em menos de 5 minutos

**Plans**: TBD
**UI hint**: yes
**Research flag**: yes — cobertura real do Serper `/shopping` em lojas portuguesas de materiais de obra; custo do endpoint `/shopping`

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Folha Excel e preços da Allmat, Bricomarché e Obras 360 | 0/6 | Planned | - |
| 2. Obramat e cadeia de recurso | 0/TBD | Not started | - |
| 3. Especificações e classificação exato/parecido | 0/TBD | Not started | - |
| 4. Embalagens, custo total e folha preenchida | 0/TBD | Not started | - |
| 5. App no browser e exportação | 0/TBD | Not started | - |
| 6. Descoberta de lojas | 0/TBD | Not started | - |
