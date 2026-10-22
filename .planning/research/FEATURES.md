# Feature Research

**Domain:** Comparador de preços pessoal para materiais de construção, bricolage e mobília em lojas online portuguesas (lista de compras → custo total mais baixo por item, com IVA, para a quantidade pedida)
**Researched:** 2026-10-22
**Confidence:** MEDIUM (padrões dos comparadores de consumo e do Obramat confirmados em várias fontes; o comportamento exato de Obra360, Allmat e Bricomarché não foi confirmado, porque os sites devolveram 403 ou não apareceram na pesquisa)

## Contexto: o que existe e onde o Strata encaixa

| Tipo de produto | Exemplos | O que faz bem | O que não faz (e o Strata precisa) |
|---|---|---|---|
| Comparador de consumo centrado no produto | KuantoKusta, idealo, PriceSpy, Google Shopping | Uma ficha por produto com ofertas de várias lojas, ordenação por preço (idealo e PriceSpy por preço total com portes), histórico, alertas, filtros por especificação | Não aceita uma lista com quantidades. Não otimiza embalagens. Cobre mal materiais de obra: a pesquisa por OSB 15 mm no KuantoKusta não devolveu nada. Depende de feeds dos lojistas, não recolhe na hora |
| Comparador de cabaz/lista | Kabaz (KuantoKusta, 2024, já offline), trolley.co.uk | Lista → loja mais barata; dividir o cabaz; sugerir artigos semelhantes de outra marca | Só supermercado; preços pré-recolhidos; não otimiza packs |
| Ferramentas B2B de materiais | Contractor+ (comparação de materiais), Bundle, BuyMaterials, BPBP (Reino Unido) | Lista de materiais (BOM) com quantidades, escolher várias lojas, exportar a lista; pedidos de orçamento a vários fornecedores | Funcionam por pedido de orçamento (RFQ) ou com lojas dos EUA ou do Reino Unido; nada para Portugal |
| Site da própria loja | Obramat ("mejor precio por cantidad"), Leroy Merlin PT (preço/m² e preço/caixa) | Preço com e sem IVA lado a lado (Obramat ES); escalões por quantidade (unidade vs palete); preço por m² | Só a própria loja |

**Conclusão:** ninguém junta *lista com quantidades + lojas de obra portuguesas + IVA normalizado + otimização de embalagens*. É esse o espaço do Strata. Histórico, alertas, filtros por categoria e leitura de códigos de barras são o padrão dos comparadores, mas aqui são anti-features, porque o PROJECT.md os põe fora do âmbito ou porque não servem um utilizador único no PC.

## Feature Landscape

### Table Stakes (Users Expect These)

Sem isto, a ferramenta não bate a pesquisa feita à mão, que é o critério do Core Value.

| # | Feature | Why Expected | Complexity | Notes |
|---|---------|--------------|------------|-------|
| T1 | **Entrada da lista de compras**: várias linhas de "texto livre + quantidade + unidade" (ex.: `30 un placa OSB 15mm 2500x1250`, `45 m2 pavimento flutuante`). Colar de um texto/Excel | É o ponto de partida do fluxo inteiro; hoje o utilizador tem a lista num papel ou numa folha | LOW | Aceitar a unidade pedida (un, m², m, kg, L, saco) separada da descrição. Colar texto multilinha basta como entrada; a importação de ficheiros pode esperar |
| T2 | **Pesquisa em texto livre sem categorias** | Tem de servir tijolo, OSB e mesas. Uma árvore de categorias parte com o primeiro produto novo | MEDIUM | Os adaptadores das lojas recebem a frase de pesquisa tal como está. A estrutura vem da extração de especificações (T6), não de categorias no código |
| T3 | **Recolha na hora nas 4 lojas fixas** (Obra360, Obramat, Allmat, Bricomarché) | Sem estas lojas não há resultado em que o utilizador confie | HIGH | Um adaptador por loja. Obramat (.pt e .es) devolveu 403 a um fetch simples: há proteção anti-bot. É a feature com mais risco; ver PITFALLS/STACK |
| T4 | **Normalização do IVA (tudo com IVA 23%)** | Comparar preços com e sem IVA dá vencedores errados. O PROJECT.md chama-lhe ponto crítico | MEDIUM | O Obramat ES mostra os dois valores ("0,40 € IVA / 0,33 € sin IVA por unidad"); as lojas para profissionais podem mostrar só sem IVA. Lojas fixas: regra configurada por loja e verificada. Lojas descobertas: ler `priceSpecification.valueAddedTaxIncluded` no JSON-LD, ou texto como "s/IVA", "+IVA", "IVA incluído". Na falta destes sinais, assumir com IVA, porque a lei portuguesa (DL 138/90) obriga os preços ao consumidor a incluir impostos. Mostrar sempre a origem: "IVA: indicado pela loja / regra da loja / assumido" |
| T5 | **Preço unitário normalizado** (€/un, €/m², €/m, €/kg, €/L) | É o que o comparador do Google faz (`unit_pricing_measure`, com m² suportado) e o que a lei exige nas etiquetas. Sem ele, não se compara uma caixa de 1,44 m² com outra de 2,22 m² | MEDIUM | Precisa do conteúdo da embalagem (m²/caixa, un/palete), que vem da página ou do título (T6). Na Leroy Merlin PT, o preço/m² e o preço/caixa nem sempre batem: calcular a partir do preço da embalagem e não confiar no €/m² que a loja mostra |
| T6 | **Extração de especificações do anúncio** (espessura, medidas, material, unidade de venda, quantidade por pack/caixa/palete) | Sem isto não há preço unitário (T5), embalagens (D1) nem exatos vs parecidos (T7) | MEDIUM-HIGH | Primeiro campos estruturados (JSON-LD, API interna); depois regex para padrões óbvios (`15mm`, `2440x1220`); a IA (Jev ou um LLM barato) só para o resto. Guardar a especificação extraída ao lado do anúncio para se poder verificar |
| T7 | **Exatos primeiro, parecidos à parte, com a diferença marcada** (ex.: "2,44×1,22 m em vez de 2,5×1,25 m") | É uma decisão do PROJECT.md. Os comparadores agrupam variantes, mas aqui um OSB de 2,44×1,22 tem menos área do que um de 2,5×1,25, por isso o €/placa engana | MEDIUM-HIGH | Três classes: exato / parecido / outro (este escondido). Comparar especificação a especificação com tolerâncias. Para parecidos com outra área, mostrar também o €/m² |
| T8 | **Custo total para a quantidade pedida**, arredondado a embalagens inteiras | O Core Value é o "custo total real". Quem pede 45 m² de pavimento compra caixas inteiras | MEDIUM | O caso simples (só uma embalagem) faz parte de T8; a mistura de embalagens e os escalões são D1. Mostrar a quantidade a comprar e o excedente ("compra 32 caixas = 46,1 m², sobra 1,1 m²") |
| T9 | **Tabela por produto ordenada por custo total, com link para a página da loja** | É a saída que o PROJECT.md pede e o formato de todos os comparadores | LOW | Colunas: loja, produto (título original), classe (exato/parecido), especificação/diferença, embalagem escolhida, quantidade comprada, €/unidade normalizado, custo total com IVA, stock, link, hora da recolha |
| T10 | **Estado por loja visível** (OK / sem resultados / falhou / bloqueado / tempo esgotado) | "Nunca omitir falhas em silêncio" está nas restrições: uma loja em falta pode esconder o preço mais baixo | LOW-MEDIUM | Por item *e* por loja. "Sem resultados" é diferente de "falhou", e a interface tem de o mostrar |
| T11 | **Stock mostrado quando a loja o indica, sem filtrar** | Pedido explícito; numa obra, um produto esgotado não serve | LOW | Valores: em stock / esgotado / desconhecido / quantidade. JSON-LD `offers.availability` cobre muitos casos. "Desconhecido" é um valor normal |
| T12 | **Progresso e resultados parciais durante a pesquisa** | Uma lista de 10 itens demora minutos. Sem progresso, parece que a ferramenta encravou | LOW-MEDIUM | Mostrar por item × loja: em curso / feito / falhou. Mostrar cada resultado assim que chega |
| T13 | **Excluir um resultado à mão** ("isto não é o produto") e recalcular o mais barato | O classificador vai errar às vezes. Sem esta correção, o "mais barato" fica errado e o utilizador volta a confirmar tudo à mão | LOW | Só nessa sessão; não é aprendizagem nem histórico |
| T14 | **Exportar para Excel** | Pedido explícito; o utilizador partilha com a obra ou compra a partir da folha | LOW | Uma folha com o melhor resultado por item e o total da lista; outra com todos os resultados. Os links têm de ser clicáveis |
| T15 | **Total da lista** (soma do mais barato de cada item) e hora da recolha | Toda a ferramenta de cabaz mostra o total; a hora diz se o preço ainda vale | LOW | Escolher o exato mais barato; os parecidos só entram se o utilizador os escolher. Avisar "portes não incluídos" |

### Differentiators (Competitive Advantage)

Alinhados com o Core Value. Nenhum comparador de consumo os tem.

| # | Feature | Value Proposition | Complexity | Notes |
|---|---------|-------------------|------------|-------|
| D1 | **Otimização da combinação de embalagens** (avulso / pack / caixa / palete / escalões de preço por quantidade), mesmo comprando a mais | É o diferenciador central. O Obramat aplica "mejor precio por cantidad" (ex.: tijolo a 0,40 €/un, ou 0,38 €/un numa palete de 480). Às vezes 50 numa palete custam menos do que 30 avulsas | MEDIUM | Um problema pequeno de cobertura com custo mínimo (soma das quantidades ≥ pedido), resolvido por programação dinâmica sobre poucas embalagens e quantidades modestas, ou por enumeração. Precisa de teste com casos conhecidos, porque é dinheiro. Mostrar a escolha ("1 palete de 50 = 112 €, em vez de 30 avulsas = 126 €") e o excedente. Avisar que a palete pode ser cobrada à parte: a tabela da Preceram indica "paletes debitadas separadamente" |
| D2 | **Conversão entre a unidade pedida e a unidade vendida** (pede m², a loja vende caixas; pede metros, a loja vende varas de 2,4 m; pede unidades, a loja vende packs de 10) | Sem isto, D1 só funciona quando o pedido vem na unidade da loja | MEDIUM | Depende de T6 trazer o conteúdo da embalagem. Se a conversão for impossível (falta a área da caixa), dizê-lo na linha, sem adivinhar |
| D3 | **Poupança do parecido mais barato** ("parecido 2,44×1,22: −18 € no total, −0,9 €/m²") | Torna útil a separação exato/parecido: não se perdem alternativas mais baratas | LOW | Construído sobre T7 e T5 |
| D4 | **Origem e confiança de cada preço** (API interna / JSON-LD / browser / IA; IVA indicado ou assumido; especificação extraída por regex ou IA) | O utilizador confia mais no resultado e vê onde convém confirmar antes de comprar | LOW | Uma etiqueta pequena na linha; tudo o que veio da IA ou de um pressuposto fica assinalado |
| D5 | **Cadeia de alternativas por loja** (API → JSON-LD → Playwright → IA) antes de desistir | Decisão do PROJECT.md; reduz as linhas "falhou" | HIGH | Cada degrau é um adaptador; o estado (T10) diz qual degrau funcionou ou porque falharam todos |
| D6 | **Descoberta automática de outras lojas PT** (pesquisa de shopping filtrada para Portugal + leitor genérico de JSON-LD) | Cobre o país sem escrever um adaptador por loja | HIGH | Os resultados das lojas descobertas passam pela mesma deteção de IVA e classificação, com a etiqueta "descoberta". Filtrar marketplaces e lojas estrangeiras com envio para PT |
| D7 | **Sugerir passar para a lista fixa as lojas descobertas que funcionam bem** | A lista de lojas melhora com o uso | LOW (depois de D6) | Precisa de um registo mínimo por loja (sucessos/falhas, nº de resultados exatos). É contagem de fiabilidade, não histórico de preços |
| D8 | **Repetir só um item ou só uma loja** | Quando uma loja falha, não é preciso repetir a lista inteira (minutos) | LOW-MEDIUM | Reaproveita o estado de T10 |
| D9 | **Exportar para PDF** | Pedido explícito; serve para imprimir ou enviar | LOW-MEDIUM | Fazer depois do Excel; a mesma tabela renderizada. Fica em P2 porque o Excel cobre a necessidade principal |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Portes / custo entregue na obra** | idealo e PriceSpy ordenam por preço com portes | Fora de âmbito no PROJECT.md. Portes de obra dependem do código postal, do peso e de limiares (ex.: Obra360 sem portes acima de 750 €, segundo um fórum); é quase um projeto à parte | Aviso fixo "portes não incluídos" na tabela e na exportação |
| **Agrupar compras por loja / minimizar nº de lojas** | O Kabaz fazia "dividir o cabaz"; parece poupar tempo | Fora de âmbito; sem portes nem descontos por volume entre itens, a otimização não tem dados reais | Permitir ordenar ou filtrar a tabela final por loja, se for preciso; não otimizar |
| **Histórico de preços e alertas** | É o padrão no KuantoKusta, idealo e PriceSpy | Fora de âmbito; obriga a guardar dados e a correr em segundo plano | Nada. A exportação Excel é o registo, se o utilizador o quiser |
| **Base de dados/catálogo pré-recolhido** | Seria mais rápido | Contraria "preços na hora"; um catálogo desatualizado mostra o preço errado | Cache só dentro da sessão (por exemplo, a mesma pesquisa repetida em minutos) |
| **Árvore de categorias e filtros por especificação** (estilo Geizhals/idealo) | Os comparadores têm-nos | Partem com tudo o que é novo (mobília, tijolo); manutenção contínua | Texto livre + extração de especificações (T6) + exato/parecido (T7) |
| **Filtrar por stock** | Parece óbvio | Fora de âmbito: o stock online é pouco fiável e esconder linhas esconde preços | Mostrar o stock (T11) e deixar o utilizador decidir |
| **Escolher automaticamente "o" produto e esconder o resto** | Interface mais limpa | Com o classificador a errar, o utilizador não vê o erro | Mostrar sempre a tabela completa, com o melhor em destaque, e exclusão manual (T13) |
| **Pôr no carrinho / comprar automaticamente** | Parece o próximo passo natural | Risco nos termos de uso e de compras erradas com dinheiro real; tráfego de bot em sessões autenticadas | Link para a página do produto |
| **Contas, multiutilizador, versão telemóvel, leitura de códigos de barras** | Funcionalidades habituais nas apps dos comparadores | Fora de âmbito (ferramenta pessoal no PC) | Nada |
| **Pedidos de orçamento a fornecedores sem site** (como BuyMaterials ou Bundle) | Seriam os preços mais baixos de madeireiras locais | Fora de âmbito; não há preço publicado para automatizar | Nada; o utilizador junta esses orçamentos à mão ao Excel |
| **IVA da Madeira e dos Açores e outras taxas de IVA** | Completude | Fora de âmbito; só continente | Uma constante, 23%. Se o anúncio trouxer outra taxa explícita, assinalar a linha em vez de converter |
| **Ocultar lojas que falham** | Interface limpa | Contraria "nunca omitir falhas"; uma loja escondida pode ter o preço mais baixo | T10: estado visível sempre |

## Feature Dependencies

```
T1 Entrada da lista
    └──alimenta──> T2 Pesquisa texto livre
                       └──requires──> T3 Adaptadores lojas fixas ──enhanced by──> D5 Cadeia de alternativas
                                          └──requires──> T10 Estado por loja
T3 / D6 (anúncios em bruto)
    └──requires──> T6 Extração de especificações
                       ├──requires──> T4 Normalização IVA (sinais do anúncio/loja)
                       ├──requires──> T5 Preço unitário ──requires──> D2 Conversão unidade pedida↔vendida
                       └──requires──> T7 Exato vs parecido ──enhanced by──> D3 Poupança do parecido
T4 + T5 + D2
    └──requires──> T8 Custo total (embalagem única) ──enhanced by──> D1 Otimização de embalagens
T8/D1 + T7 + T11 Stock
    └──requires──> T9 Tabela ordenada ──requires──> T15 Total da lista
                       ├──enhanced by──> T13 Exclusão manual (recalcula T15)
                       └──requires──> T14 Export Excel ──then──> D9 Export PDF
D6 Descoberta ──requires──> leitor genérico JSON-LD (degrau de D5) + T4 + T7
D7 Sugestão de promover ──requires──> D6 + registo de fiabilidade por loja (sai de T10)
T12 Progresso ──requires──> T10 (o mesmo modelo de estado item × loja)
```

### Dependency Notes

- **T6 é a base do cálculo:** T4, T5, T7, T8 e D1 dependem da especificação extraída. Tem de ficar sólida cedo, com testes sobre títulos reais das 4 lojas.
- **T8 antes de D1:** primeiro o custo com uma embalagem e arredondamento; depois a combinação. A tabela não muda entre os dois, só o motor de cálculo.
- **T10 e T12 partilham o modelo de estado item × loja:** desenhado uma vez, serve progresso, falhas, repetição seletiva (D8) e fiabilidade (D7).
- **D6 reaproveita o degrau JSON-LD de D5:** fazer o leitor genérico como alternativa das lojas fixas paga também a descoberta.
- **T4 e D6 juntos são onde o IVA mais engana:** nas lojas fixas a regra é configurada e verificada à mão; nas descobertas é detetada. Uma loja descoberta com IVA mal assumido ganha falsamente a comparação (aparece cerca de 19% mais barata). Mitigação: etiqueta D4 e, nas descobertas, só aceitar "sem IVA" quando o anúncio o diz.
- **T13 conflitua com cache entre sessões:** as exclusões ficam só na sessão; não guardar nada entre sessões evita histórico disfarçado.

## MVP Definition

### Launch With (v1)

Fecha o ciclo "lista → custo total real → link" e prova o Core Value contra a pesquisa à mão.

- [ ] T1 Entrada da lista (colar texto) — ponto de partida
- [ ] T2 + T3 Pesquisa em texto livre nas 4 lojas fixas — sem elas não há comparação
- [ ] T6 Extração de especificações (estruturado + regex + IA) — base do cálculo
- [ ] T4 Normalização do IVA com origem visível — o erro mais caro se falhar
- [ ] T5 + D2 Preço unitário e conversão de unidades — comparar embalagens diferentes
- [ ] T8 + D1 Custo total com otimização de embalagens — o diferenciador do Core Value
- [ ] T7 Exatos vs parecidos com a diferença — decisão do PROJECT.md
- [ ] T9, T11, T15 Tabela ordenada, stock, total da lista
- [ ] T10 + T12 Estado por loja e progresso — "nunca omitir falhas"
- [ ] T13 Exclusão manual — corrige erros do classificador
- [ ] T14 Export Excel

### Add After Validation (v1.x)

Continuam nos requisitos ativos; entram quando o núcleo estiver validado com as 4 lojas.

- [ ] D5 Cadeia de alternativas completa (Playwright, IA) — quando uma loja fixa falhar de forma recorrente com o método principal
- [ ] D6 Descoberta automática de lojas — quando o núcleo der resultados certos nas lojas fixas; senão as lojas descobertas trazem mais ruído do que preço
- [ ] D7 Sugestão de promover lojas — quando D6 tiver algumas semanas de uso
- [ ] D9 Export PDF — quando o Excel estiver estável
- [ ] D3, D4, D8 — pequenos, encaixam em qualquer fase depois de T7/T10

### Future Consideration (v2+)

- [ ] Portes / custo entregue — se a diferença de portes mudar o vencedor com frequência
- [ ] Agrupar por loja — só se se confirmarem descontos por compra conjunta
- [ ] Guardar listas de entrada para reutilizar — hoje basta colar o texto outra vez

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| T1 Entrada da lista | HIGH | LOW | P1 |
| T2/T3 Pesquisa nas 4 lojas fixas | HIGH | HIGH | P1 |
| T6 Extração de especificações | HIGH | MEDIUM-HIGH | P1 |
| T4 Normalização IVA | HIGH | MEDIUM | P1 |
| T5/D2 Preço unitário + conversão | HIGH | MEDIUM | P1 |
| T8/D1 Custo total + embalagens | HIGH | MEDIUM | P1 |
| T7 Exato vs parecido | HIGH | MEDIUM-HIGH | P1 |
| T9/T15 Tabela + total | HIGH | LOW | P1 |
| T10/T12 Estado + progresso | HIGH | LOW-MEDIUM | P1 |
| T11 Stock | MEDIUM | LOW | P1 |
| T13 Exclusão manual | MEDIUM | LOW | P1 |
| T14 Export Excel | MEDIUM | LOW | P1 |
| D4 Origem/confiança do preço | MEDIUM | LOW | P2 |
| D3 Poupança do parecido | MEDIUM | LOW | P2 |
| D5 Cadeia de alternativas | HIGH | HIGH | P2 |
| D6 Descoberta de lojas | MEDIUM-HIGH | HIGH | P2 |
| D8 Repetir item/loja | MEDIUM | LOW-MEDIUM | P2 |
| D9 Export PDF | LOW-MEDIUM | LOW-MEDIUM | P2 |
| D7 Sugerir promover loja | LOW-MEDIUM | LOW | P3 |

## Competitor Feature Analysis

| Feature | KuantoKusta / idealo / PriceSpy / Google Shopping | Kabaz (offline) / Contractor+ / BuyMaterials | Our Approach |
|---------|------------------------------|-----------------------------|--------------|
| Entrada | Pesquisa de um produto de cada vez | Lista/BOM com quantidades | Lista colada com quantidade e unidade por linha |
| Cobertura | Feeds dos lojistas; fraca em materiais de obra PT | Supermercados (Kabaz); lojas dos EUA ou do Reino Unido | 4 lojas fixas PT + descoberta, recolha na hora |
| IVA | Assumem preço ao consumidor com IVA | Ferramentas B2B trabalham sem IVA | Normalizar tudo para com IVA 23%, mostrando a origem |
| Preço unitário | Google: `unit_pricing_measure` (inclui m²) | Por unidade da BOM | €/un, €/m², €/m, €/kg calculados a partir da embalagem |
| Quantidade/embalagens | Nenhum otimiza | Contractor+ ajusta quantidades; não otimiza packs | Combinação de embalagens e escalões com custo mínimo, excedente visível |
| Variantes/semelhantes | Agrupam variantes; o Kabaz sugeria marcas semelhantes | — | Exatos primeiro; parecidos à parte com a diferença e o €/m² |
| Portes | idealo/PriceSpy ordenam com portes | Incluem entrega nos orçamentos | Fora de âmbito; aviso "portes não incluídos" |
| Histórico/alertas | Sim | — | Não (anti-feature) |
| Falhas de recolha | Invisíveis (feeds) | — | Estado por loja visível, alternativas antes de desistir |
| Export | Não | Contractor+ exporta a lista | Excel (v1), PDF (v1.x) |

## Sources

Confiança da maioria: LOW por fonte (classificador: `websearch` → LOW). Passa a MEDIUM onde duas fontes independentes concordam (marcado com *).

- KuantoKusta: alertas, listas de desejos, app com códigos de barras; Kabaz lançado em jan. 2024 e já offline — [pplware](https://pplware.sapo.pt/smartphones-tablets/nova-app-do-kuantokusta-agora-compara-precos-em-tempo-real), [Observador](https://observador.pt/2024/01/29/kuantokusta-lanca-plataforma-kabaz-para-comparar-precos-nos-supermercados/), [4gnews](https://4gnews.pt/nova-app-portuguesa-chega-com-funcionalidade-inovadora-que-te-poupa-dinheiro-no-supermercado/) *
- PriceSpy (alertas, histórico, custo com portes, listas) — [PriceSpy NZ](https://pricespy.co.nz/get-started-with-pricespys-features--ecYSSp9RIAACMAXh6i)
- idealo (ordenação por preço total, filtros, histórico) — [Finanztip](https://www.finanztip.de/preisvergleich/), [monsterdealz](https://www.monsterdealz.de/magazin/idealo-test)
- Google Merchant Center: preço unitário com m² — [unit_pricing_measure](https://support.google.com/merchants/answer/6324455), [unit_pricing_base_measure](https://support.google.com/merchants/answer/6324490) (documentação oficial; HIGH para este ponto)
- Obramat: "mejor precio por cantidad" (unidade vs palete; tijolo a 0,40 €/un, ou 0,38 €/un na palete de 480) e preços com/sem IVA — [Obramat ES novedades](https://www.obramat.es/sobre-obramat/novedades/mejor-precio-por-cantidad/), [Obramat ES ladrillos](https://www.obramat.es/materiales-de-construccion/elementos-de-construccion/ladrillos/) *. Não confirmado para obramat.pt (403 a fetch simples)
- Leroy Merlin PT: preço/m² e preço/caixa nem sempre coincidem — [pavimentos laminados](https://www.leroymerlin.pt/produtos/pavimentos-e-revestimentos/pavimentos-laminados/tipos-de-uso-de-pavimentos-laminados/pavimentos-laminados-fortes/)
- Obra360 = loja online da Sotecnisol; portes grátis acima de 750 €; diferenças grandes no OSB 15 mm — [Fórum da Casa](https://forumdacasa.com/discussion/86765/compra-de-materiais/) (relato de utilizador, LOW)
- Paletes cobradas à parte (Preceram, 2012) — [tabela Preceram](https://rdpc.uevora.pt/bitstream/10174/16074/63/2-Tijolos%20Preceram.pdf) (antiga, LOW)
- Ferramentas B2B: [Contractor+](https://contractorplus.app/resources/material-price-comparison), [Bundle (Capterra)](https://www.capterra.co.uk/software/1244680/Bundle), [BuyMaterials](https://www.buymaterials.com/trade), [BPBP](https://www.construction.co.uk/c/728662/best-price-building-products)
- Lei portuguesa: preço ao consumidor com todos os impostos e preço por unidade de medida — DL 138/90, alterado pelo DL 162/99 — [vLex](https://vlex.pt/vid/decreto-lei-33166099), [DRE DL 162/99](https://diariodarepublica.pt/dr/detalhe/decreto-lei/162-1999-321723) (redação em vigor não confirmada)

---
*Feature research for: comparador pessoal de preços de materiais de obra/mobília em lojas online PT*
*Researched: 2026-10-22*
