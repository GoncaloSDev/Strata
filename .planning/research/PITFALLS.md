# Pitfalls Research

**Domain:** Comparador de preços pessoal (materiais de obra, bricolage, mobília) em lojas online portuguesas, com recolha na hora e classificação de produtos por IA
**Researched:** 2026-10-22
**Confidence:** MEDIUM-HIGH (os pontos sobre as lojas fixas foram verificados hoje com pedidos diretos aos sites; os legais e os de custos de APIs vêm de fontes secundárias)

> Nota sobre as fases: ainda não existe roadmap. As fases abaixo usam nomes de tema, para o roadmapper mapear:
> **F-Núcleo** (modelo de dados, preço/IVA/unidades, parser de medidas, fixtures) ·
> **F-Lojas** (adaptadores das 4 lojas fixas) ·
> **F-Matching** (classificação exato/parecido, IA) ·
> **F-Embalagens** (otimizador de quantidade) ·
> **F-Descoberta** (API de pesquisa + leitor genérico) ·
> **F-Resultados** (tabela, estado das lojas, exportação)

## Factos verificados hoje (servem de base aos pitfalls)

| Loja | O que se observou (22-10-2026) | Consequência |
|------|-------------------------------|--------------|
| **Obramat** (`obramat.pt`) | `curl` simples devolve **403** com `Server: DataDome`, `X-DataDome: protected`, riskscore 0,83. `robots.txt` proíbe `/pesquisa/` e `/search?q=*`, mas publica `sitemap-product1.xml`. O site espanhol (mesma plataforma) mostra **dois preços por artigo**: "12,56 € IVA" e "10,38 € sin IVA", e blocos "Mejor precio por cantidad". | Anti-bot forte; risco de apanhar o preço sem IVA; existem preços por escalão de quantidade. |
| **Bricomarché** (`bricomarche.pt`) | WordPress + WooCommerce. A Store API pública responde (`/wp-json/wc/store/v1/products?search=osb`). O site diz "Deve escolher loja antes de pesquisar". O produto "PLACA OSB 12 MM" é `variable` com atributo **Loja** (uma variação por loja física) e `price_range` **18,49 € a 29,99 €**. O `price` de topo é o mínimo entre lojas. Os preços vêm em cêntimos (`"1849"`, `currency_minor_unit: 2`). A descrição diz "2500x125x12 mm" (erro: devia ser 1250) e o título não diz se é OSB2 ou OSB3. | O preço depende da loja escolhida (diferença de 62% no mesmo artigo). Os dados da loja têm erros de medidas. |
| **Allmat** (`allmat.pt`) | Cloudflare (`__cf_bm`, `CF-Ray`), mas a página passa com um User-Agent normal. WooCommerce + tema WoodMart. Mostra "IVA incluído", preço riscado + preço atual, "3,99€ / m²", "Ou 4,48€ 3,59€ / Caixa". A pesquisa "OSB" dá **zero resultados legítimos** ("Não foram encontrados produtos..."), enquanto "cimento" dá resultados. O HTML tem um preço **"0,00 €"** (o total do mini-carrinho) antes dos preços dos produtos. A Store API devolve `[]`. | Um seletor de preço ingénuo apanha 0,00 €, que passa a ser "o mais barato". "Sem resultados" é diferente de "falhou". |
| **"Obra360"** | `obra360.pt` tem um certificado com o nome errado (`SEC_E_WRONG_PRINCIPAL`) e devolve 503. `obra360.com` está à venda. A loja real parece ser a **Obras 360** em `obras360.pt` (Sotecnisol, lojas em Camarate, Maia, Leiria e Coimbra). Plataforma própria ("Beevo"), produtos e preços carregados por JavaScript (cartões vazios no HTML). O `robots.txt` proíbe `/restfull/` e `/external_apis/`. | Domínio a confirmar com o utilizador. A API interna provavelmente está num caminho que o `robots.txt` proíbe. |

---

## Critical Pitfalls

### Pitfall 1: Comparar preços sem IVA com preços com IVA (ou inferir o estado do IVA anúncio a anúncio)

**What goes wrong:**
A Obramat (orientada a profissionais) mostra o preço com e sem IVA lado a lado; um parser ou o LLM apanha o "sin/sem IVA" e a Obramat aparece 18,7% mais barata do que é. O erro contrário também acontece: o código soma 23% a um preço que já tinha IVA. A tabela fica ordenada errada e ninguém repara, porque os números parecem plausíveis.

**Why it happens:**
- O estado do IVA é tratado como atributo do anúncio ("o LLM que decida") em vez de uma regra da loja verificada.
- O `schema.org/Offer` raramente traz `priceSpecification.valueAddedTaxIncluded`; quando falta, o código assume um valor por omissão.
- Uma sessão com conta profissional pode mudar o modo de mostrar preços sem o código saber.

**How to avoid:**
1. Cada adaptador declara `vat_mode` (`incl` | `excl` | `both→usar o incl`) e o seletor exato de onde o tira. Nunca fica como "auto".
2. Guardar sempre o preço tal como foi lido, o `vat_mode` e o preço normalizado. O cálculo `excl × 1,23` faz-se num único sítio, com `Decimal`.
3. Teste-canário por loja: um produto conhecido cujo preço com IVA foi visto à mão; se o normalizado divergir mais de 1%, a loja passa a "falhou: IVA incoerente".
4. Lojas descobertas: só aceitar "com IVA" com prova (texto "IVA incluído", `valueAddedTaxIncluded: true`, ou loja B2C portuguesa, a quem o DL 138/90 obriga a mostrar o preço com todas as taxas). Sem prova, marcar "IVA por confirmar" e não pôr em primeiro lugar.
5. Quando a página mostra os dois preços (Obramat), confirmar que `incl / excl ≈ 1,23` e falhar se não bater.

**Warning signs:**
Uma loja profissional ganha quase sempre; a diferença para a segunda é perto de 18–19%; o rácio entre os dois preços da Obramat não dá 1,23.

**Phase to address:** F-Núcleo (modelo e regra) + F-Lojas (declaração e canário por loja).

---

### Pitfall 2: Apanhar o número errado da página (carrinho a 0,00 €, preço riscado, "preço mais baixo em 30 dias", "desde", preço por m²)

**What goes wrong:**
Na Allmat, o primeiro `.woocommerce-Price-amount` do HTML é o total do mini-carrinho, **0,00 €**. Um seletor genérico ou um LLM a ler a página devolve 0,00 €, que ganha sempre. Outras armadilhas: preço riscado vs atual (a ordem no HTML muda entre temas); a indicação obrigatória do "preço mais baixo praticado nos 30 dias anteriores" (DL 70/2007, alterado pelo DL 109-G/2021) põe um terceiro preço nas páginas em promoção; produtos variáveis mostram "desde X €"; azulejos e pavimentos mostram "€/m²" e "€/Caixa" lado a lado.

**Why it happens:**
Extração por "primeiro preço que aparece" ou um LLM sem contexto de onde fica o produto na página.

**How to avoid:**
1. Ordem de fontes: API JSON da loja → JSON-LD `Offer` → seletor ancorado no bloco do produto → LLM. Nunca "procurar € na página toda".
2. Validação forte: preço > 0, dentro de um intervalo plausível face aos outros resultados (por exemplo, menos de 20% da mediana marca "suspeito"), moeda EUR.
3. Guardar o tipo de preço lido (`unit`, `per_m2`, `per_box`, `from`) e rejeitar `from` como preço final.
4. Números em formato português: `1.234,56 €` → `Decimal("1234.56")`; a Store API do WooCommerce dá cêntimos (`"1849"` e `currency_minor_unit: 2`). Fazer um parser com testes próprios e nunca usar `float` para dinheiro.

**Warning signs:**
Preços de 0,00 €, 0,01 € ou 1,00 €; o mesmo preço em todos os produtos de uma loja; um vencedor que é muito mais barato do que todos os outros.

**Phase to address:** F-Núcleo (parser de preço + validação) e F-Lojas (seletores ancorados com fixtures HTML guardadas).

---

### Pitfall 3: O preço depende da loja física ou do código postal escolhido

**What goes wrong:**
Na Bricomarché, a mesma placa OSB 12 mm custa entre 18,49 € e 29,99 € conforme a loja (variações WooCommerce com atributo "Loja"). O campo `price` de topo da API é o **mínimo entre todas as lojas**, por isso a ferramenta mostra 18,49 € quando a loja onde o utilizador compra cobra 29,99 €. O stock também é por loja. A Obramat (mesmo grupo da Leroy Merlin) tem quase de certeza o mesmo modelo de preço e stock por armazém.

**Why it happens:**
Testar só com o preço "por omissão" e não perceber que existe um contexto de loja no cookie, na sessão ou na variação.

**How to avoid:**
1. Configuração do utilizador: loja preferida de cada cadeia (ou código postal), guardada uma vez.
2. O adaptador resolve a variação ou o cookie dessa loja e regista no resultado "preço da loja X".
3. Se não conseguir fixar a loja, mostrar o intervalo ("18,49–29,99 € conforme a loja") e não usar o mínimo para ordenar.
4. Teste: na Bricomarché, um produto `variable` tem de devolver o preço da variação da loja configurada e não o `price` de topo.

**Warning signs:**
`price_range.min != max` na API; o preço na ferramenta difere do que o utilizador vê no browser; o stock aparece "disponível" mas a loja local não tem.

**Phase to address:** F-Lojas (primeiro adaptador, Bricomarché) e F-Núcleo (campo `store_location` no modelo de resultado).

---

### Pitfall 4: Falhas silenciosas que escondem a loja mais barata

**What goes wrong:**
Uma loja deixa de aparecer na tabela e o utilizador conclui que "não tem" ou "é mais cara". Causas reais: o DataDome devolve 403 ou uma página de desafio com HTTP 200; o Cloudflare devolve "Just a moment..." com 200/503; o site muda o HTML e o seletor devolve lista vazia; o certificado falha (caso `obra360.pt`). Ao mesmo tempo, há zeros legítimos: a Allmat não tem resultados para "OSB" mas tem para "cimento".

**Why it happens:**
`try/except` que devolve `[]`; não distinguir "pesquisa correu e não encontrou" de "não consegui pesquisar".

**How to avoid:**
1. Estado explícito por loja e por produto: `ok_com_resultados` | `ok_sem_resultados` | `bloqueada` | `erro` | `timeout`, com motivo legível. A tabela mostra sempre todas as lojas fixas, incluindo as que falharam.
2. Detetar desafios anti-bot pelo conteúdo, não só pelo código HTTP (cabeçalhos `Server: DataDome`/`x-datadome`, `cf-ray` + título "Just a moment", HTML sem marcadores do produto).
3. "Sem resultados" só conta se a página de resultados tiver o marcador próprio da loja (ex.: "Não foram encontrados produtos"). Uma lista vazia sem esse marcador é `erro: layout mudou`.
4. Pesquisa-canário por loja (um termo que sabidamente dá resultados), corrida no arranque ou à mão (`strata check-stores`), para apanhar adaptadores partidos antes de uma lista real.
5. Seguir a cadeia de recurso do PROJECT.md (API → JSON-LD → browser → IA), mas registar qual via deu o preço e quais falharam.

**Warning signs:**
Uma loja fixa com 0 resultados em vários produtos seguidos; tempos de resposta de 50 ms (página de bloqueio) em vez de 1–3 s; HTML muito mais pequeno do que o normal.

**Phase to address:** F-Lojas (estados + deteção de desafio + canário) e F-Resultados (mostrar o estado). Tem de existir desde o primeiro adaptador, não no fim.

---

### Pitfall 5: Correspondências "exatas" falsas (medidas, OSB2 vs OSB3, espessura) e especificações inventadas pelo LLM

**What goes wrong:**
- Formatos de medida: "2,5×1,25 m", "2500x1250 mm", "250x125 cm", "250x125x1,2cm" (Obramat ES), "2-50x1-25-12mm" (slug Bricomarché).
- Dados da loja errados: a Bricomarché escreve "2500x125x12 mm" na descrição (125 em vez de 1250) e o título "PLACA OSB 12 MM" nem diz se é OSB2 ou OSB3.
- O LLM, perante "placa OSB 12 mm", completa "OSB3" porque é o mais comum, e o resultado passa a "exato".
- 2,44×1,22 m (formato imperial 8×4 ft) aparece como "exato" de 2,50×1,25 m porque "é quase igual", mas a área é 4,8% menor e o preço por m² muda.
- Espessura: 11 mm vs 12 mm, 18 mm vs 19 mm; tolerâncias diferentes por material.

**Why it happens:**
Deixar o LLM fazer o parse **e** a decisão; tratar "atributo ausente" como "atributo igual".

**How to avoid:**
1. Parser determinístico de medidas (regex + conversão para mm, vírgula e ponto decimais, `x`/`×`/`X`/`*`, ordem C×L×E) com uma bateria de testes feita a partir de títulos reais das 4 lojas. O LLM só extrai o que o regex não apanha e tem de citar o trecho do título de onde tirou cada valor.
2. Três estados por atributo: `igual` | `diferente` | `desconhecido`. **"Exato" exige `igual` em todos os atributos pedidos.** Qualquer `desconhecido` → "parecido (confirmar: classe OSB não indicada)".
3. Verificação cruzada: se título, slug e descrição discordam (caso Bricomarché), marcar "medidas contraditórias" e não classificar como exato.
4. Comparar em preço por m² ou por unidade funcional quando as medidas diferem, e mostrar a diferença ("2,44×1,22 m, −4,8% área").
5. Conjunto de avaliação: cerca de 100 anúncios reais rotulados à mão (OSB, contraplacado, tijolo, cimento, uma mesa), para medir falsos exatos antes de confiar em qualquer modelo.

**Warning signs:**
Taxa de "exato" muito alta (>70%) em pesquisas genéricas; o LLM devolve atributos que não aparecem no texto; medidas convertidas com um fator 10 errado.

**Phase to address:** F-Núcleo (parser de medidas + testes) antes de F-Matching. F-Matching define a regra "desconhecido ≠ igual" e o conjunto de avaliação.

---

### Pitfall 6: Erros de unidade e de embalagem (m² vs placa vs caixa vs palete vs pack de N)

**What goes wrong:**
- Allmat: "3,99€ / m²" e "3,59€ / Caixa" na mesma página; comparar o preço por caixa de uma loja com o preço por m² de outra.
- Tijolo vendido "por palete de 300" num site e "à unidade" noutro; o título diz "pack 10" mas o preço é por unidade (ou o contrário).
- O pedido é "30 m² de pavimento" mas a loja vende caixas de 1,44 m², o que obriga a arredondar para cima.
- Uma placa de 3,125 m² (2500×1250) comparada por placa com uma de 2,977 m² (2440×1220).

**Why it happens:**
Normalizar para uma única "unidade" sem guardar a unidade de venda real e o conteúdo da embalagem.

**How to avoid:**
1. O modelo de oferta guarda `sale_unit` (unidade, caixa, palete, pack, m², ml, kg, saco) + `content_qty` + `content_unit` (ex.: caixa = 1,44 m²; palete = 300 un).
2. Coerência: se a página mostrar €/m² e €/caixa, confirmar `per_box ≈ per_m2 × m²_por_caixa` (±2%); se não bater, marcar "unidade incoerente".
3. A quantidade pedida tem unidade (30 un, 30 m², 5 paletes). Se a unidade pedida não se converter para a unidade de venda (m² → caixa sem área por caixa), pedir confirmação em vez de adivinhar.
4. Nunca deixar o LLM fazer a conta; o LLM só extrai `content_qty`, e a aritmética é código.

**Warning signs:**
Preços por unidade que diferem 10× ou 100× entre lojas; "pack" no título com preço igual ao avulso.

**Phase to address:** F-Núcleo (modelo de unidades) e F-Embalagens.

---

### Pitfall 7: O otimizador de embalagens dá respostas erradas nos casos-limite

**What goes wrong:**
- Preços por escalão (Obramat "melhor preço por quantidade": o preço unitário baixa a partir de N unidades) não modelados, perdendo exatamente o caso "comprar mais sai mais barato".
- A palete só existe na loja física, ou tem stock 0, mas entra na solução.
- Mínimos de encomenda e múltiplos obrigatórios (sacos só em múltiplos de 2, "venda à caixa") ignorados.
- Comprar a mais sem limite: sugerir 2 paletes (600 tijolos) para um pedido de 310 porque sai 0,50 € mais barato.
- Misturar tamanhos de embalagem da mesma loja (1 palete + 10 avulsos) não considerado, ou considerado entre lojas diferentes quando isso implica duas compras.

**Why it happens:**
Implementação gulosa ("a embalagem de menor preço unitário primeiro") em vez de procura exata; testes só com o caso feliz.

**How to avoid:**
1. Para cada loja e produto, procura exata sobre combinações de embalagens (o número de embalagens é pequeno, e uma DP sobre a quantidade até `pedido + maior embalagem` chega). Escalões como função preço(qtd).
2. Restrições explícitas: mínimo, múltiplo, stock conhecido, "só em loja".
3. Mostrar sempre "comprado vs pedido" (ex.: "300 + 10 = 310 un; sobram 0") e o excesso em € quando houver sobras.
4. Limite de compra a mais configurável (ex.: no máximo +20% ou +1 embalagem grande), com a alternativa sem sobras ao lado.
5. Tabela de testes: pedido = 0, pedido = 1, pedido = palete exata, palete − 1, palete + 1, escalão na fronteira, stock < pedido.

**Warning signs:**
O resultado muda pouco com a quantidade pedida; nunca aparece uma palete como ótima; sobras grandes sem aviso.

**Phase to address:** F-Embalagens (depende do modelo de unidades da F-Núcleo).

---

### Pitfall 8: Anti-bot (DataDome na Obramat, Cloudflare na Allmat) e a corrida às armas

**What goes wrong:**
A Obramat bloqueia `curl` à primeira (403, DataDome). O Playwright headless costuma ser detetado pelo DataDome também. A tentação é acrescentar plugins "stealth", proxies residenciais e resolvedores de CAPTCHA: custo, manutenção semanal, risco legal (contornar uma medida técnica) e, mesmo assim, bloqueios intermitentes. Pedidos a mais também podem marcar o IP de casa do utilizador e bloquear o próprio browser dele na Obramat.

**Why it happens:**
Tratar o bloqueio como bug a resolver em vez de restrição a gerir.

**How to avoid:**
1. Sondar cada loja fixa **antes** de planear o adaptador (spike de 30 min por loja): cabeçalhos, API interna, JSON-LD, comportamento do headless.
2. Para lojas com DataDome: usar um browser **com interface e perfil persistente** (o Chrome dedicado do Claude, `%USERPROFILE%\.claude-chrome`, porta 9222, já existe neste PC) a ritmo humano (1 pedido de cada vez, vários segundos entre pedidos), reaproveitando cookies válidos. Sem proxies nem resolvedores de CAPTCHA.
3. Se aparecer um CAPTCHA: marcar "bloqueada: abrir no browser" com o link de pesquisa pronto, em vez de insistir.
4. Limites de ritmo por loja no código (concorrência 1, intervalo mínimo), não por convenção.

**Warning signs:**
`X-DataDome-riskscore` alto, cookie `datadome` a mudar a cada pedido, CAPTCHA no browser normal do utilizador depois de usar a ferramenta.

**Phase to address:** Spike antes de F-Lojas (decide a via por loja); F-Lojas implementa o limitador de ritmo.

---

### Pitfall 9: Preços desatualizados ou em cache apresentados como "na hora"

**What goes wrong:**
Os resultados de Google Shopping (SerpAPI/Serper) trazem preços do feed do comerciante, que podem ter horas ou dias. O JSON-LD de páginas servidas por CDN pode estar desatualizado. Uma cache interna "para poupar pedidos" torna-se invisível. O utilizador vai comprar e o preço é outro.

**How to avoid:**
1. Cada preço leva `fetched_at` e `source` (`store_api`, `jsonld`, `browser`, `llm`, `search_api`).
2. Preços vindos da API de pesquisa servem só para **descobrir** lojas e URLs; o preço mostrado vem sempre de um pedido à página da loja. Se esse pedido falhar, mostrar "preço do Google, não confirmado" separado.
3. Se existir cache, TTL curto (minutos, dentro da mesma sessão) e indicada na tabela.

**Warning signs:**
O preço na tabela difere do preço na página aberta pelo link; o mesmo preço em pesquisas de dias diferentes.

**Phase to address:** F-Núcleo (campos no modelo) e F-Descoberta.

---

### Pitfall 10: Ruído na descoberta de lojas (marketplaces, comparadores, lojas estrangeiras, IVA espanhol)

**What goes wrong:**
A API de shopping devolve Amazon.es, vendedores de marketplace (Worten Marketplace, por exemplo), comparadores como o KuantoKusta, páginas de categoria em vez de produto, artigos esgotados ou descontinuados, e lojas espanholas que enviam para Portugal. Estas mostram o preço com **IVA espanhol de 21%**, por isso "com IVA" não quer dizer 23%, e muitas vezes cobram portes elevados para material pesado.

**How to avoid:**
1. Filtro de domínio: `.pt` ou lista de domínios conhecidos que vendem para Portugal; lista negra de comparadores e agregadores; marketplaces numa secção à parte, com o vendedor identificado.
2. Exigir uma página de produto com `schema.org/Product`+`Offer` e `priceCurrency: EUR`; páginas de categoria ou listagem são rejeitadas.
3. Loja não portuguesa → IVA "por confirmar" (Pitfall 1) e nunca em primeiro lugar sem confirmação.
4. Mostrar o stock quando existir (requisito), mas assinalar `OutOfStock`/`Discontinued` para não ganhar a ordenação de forma enganosa.
5. Limitar o número de lojas descobertas visitadas por produto (ex.: 5) para controlar tempo e custo.

**Warning signs:**
Domínios repetidos de agregadores no topo; preços muito abaixo do mercado vindos de sites desconhecidos (também um sinal de loja fraudulenta).

**Phase to address:** F-Descoberta.

---

### Pitfall 11: Custos de IA e de APIs de pesquisa a disparar

**What goes wrong:**
A conta cresce como `produtos × lojas × anúncios × chamadas`. Uma lista de 10 produtos × (4 fixas + 5 descobertas) × 20 anúncios = 1 800 classificações. O recurso "IA lê a página" envia HTML inteiro (a página de pesquisa da Allmat tem cerca de 470 KB, ou seja, mais de 100 mil tokens) por loja e por produto. Ciclos de "tentar outra via" sem limite multiplicam tudo isto quando uma loja está bloqueada.

**How to avoid:**
1. Pré-filtro determinístico (palavras-chave + medidas extraídas por regex) antes do LLM; só os N melhores candidatos (ex.: 8) por loja vão para classificação.
2. Nunca enviar HTML bruto: extrair texto do bloco de produto ou JSON-LD e cortar a um máximo fixo de caracteres.
3. Orçamento por pesquisa no código (máx. de chamadas LLM e de pesquisas de API por lista), com contador visível no fim ("12 pesquisas API, 140 classificações, ≈0,04 €").
4. Cache de classificação por `(pedido normalizado, título do anúncio)` dentro da sessão.
5. Máximo de uma tentativa de recurso por via e por loja.

**Warning signs:**
Uma lista demora mais de 5 minutos; a fatura da API num dia de testes passa o orçamento do mês; chamadas LLM com prompts acima de 10 mil tokens.

**Phase to address:** F-Matching (pré-filtro, orçamento) e F-Descoberta (limite de lojas e pesquisas).

---

### Pitfall 12: Ficar preso a um modelo novo sem validação (Jev, TypeSafe AI)

**What goes wrong:**
O Jev foi lançado a 15-09-2026 em **acesso antecipado**. As latências (70–500 ms) e os preços (0,042 USD por milhão de tokens de entrada, saída grátis) são do fabricante, sem benchmarks independentes. Riscos: API muda ou deixa de existir, lista de espera, preços alterados depois do acesso antecipado, calibração que não se aplica a títulos de obra em português.

**How to avoid:**
1. Classificador atrás de uma interface pequena (`classify(pedido, anúncio) -> {exato|parecido|outro, diferenças, confiança}`), com uma implementação base num LLM generalista barato.
2. Comparar os dois no conjunto de avaliação do Pitfall 5 (falsos exatos, latência, custo) antes de escolher.
3. Não confiar na "probabilidade calibrada" como limiar sem a medir no próprio conjunto.

**Warning signs:**
Erros 4xx/429 de acesso antecipado; respostas confiantes em casos onde falta o atributo.

**Phase to address:** F-Matching (spike de avaliação no início da fase).

---

### Pitfall 13: Robots.txt, termos de uso e enquadramento legal tratados como irrelevantes "porque é pessoal"

**What goes wrong:**
- A Obramat proíbe no `robots.txt` exatamente as páginas de pesquisa (`/pesquisa/`, `/search?q=*`). A Obras 360 proíbe `/restfull/` e `/external_apis/`, onde provavelmente está a API interna de pesquisa.
- Em Portugal, as bases de dados têm direito *sui generis* contra a extração substancial (DL 122/2000, alterado pela Lei 92/2019). O DL 47/2023 criou exceções de prospeção de texto e dados com opt-out legível por máquina (o `robots.txt` conta). A Lei 109/2009 (cibercrime) pune o acesso ilegítimo, e contornar ativamente uma proteção técnica (DataDome) é o ato mais arriscado.
- Iniciar sessão numa conta profissional para ver preços implica aceitar termos de cliente que normalmente proíbem a automação.

**How to avoid:**
1. Âmbito legal da ferramenta, num documento curto: uso pessoal, só os produtos pesquisados (extração não substancial), ritmo humano, sem contornar CAPTCHAs, sem revender nem publicar dados.
2. Preferir páginas de produto (permitidas) às de pesquisa (proibidas) onde o `robots.txt` o indicar. Na Obramat, o `sitemap-product1.xml` público permite encontrar URLs de produto sem usar `/pesquisa/`.
3. Não usar contas com sessão iniciada na automação na v1.
4. RGPD: os dados de produto não são pessoais. O que conta aqui é o perfil do browser automático (cookies, sessões) e as chaves de API, que ficam locais e fora do repositório.

**Warning signs:**
O adaptador precisa de proxies, de rotação de impressões digitais ou de resolver CAPTCHAs para funcionar.

**Phase to address:** Spike antes de F-Lojas (decisão de via por loja, à luz do `robots.txt`). Nota legal: confiança MEDIUM, sem jurisprudência portuguesa específica sobre scraping. Não é aconselhamento jurídico.

---

### Pitfall 14: Loja fixa com o domínio errado ("Obra360" vs "Obras 360")

**What goes wrong:**
O PROJECT.md diz "Obra360". `obra360.pt` responde com um certificado inválido e 503, e `obra360.com` está à venda. A loja de materiais com esse nome parece ser a **Obras 360** (`obras360.pt`). Um adaptador feito contra o domínio errado falha sempre, e se a falha for silenciosa (Pitfall 4) a loja desaparece sem ninguém notar.

**How to avoid:** Confirmar com o utilizador o URL exato de cada loja fixa antes de escrever adaptadores; guardar os URLs base em configuração.

**Phase to address:** Antes de F-Lojas (pergunta de 1 minuto ao utilizador).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| LLM a ler a página inteira para todas as lojas | Um adaptador "universal" num dia | Custo por pesquisa alto, preços errados (0,00 €, sem IVA), sem testes reproduzíveis | Só como último recurso, com corte de tamanho e validação |
| `float` para preços | Menos código | Arredondamentos errados nos totais e no × 1,23 | Nunca |
| `except: return []` no adaptador | A pesquisa "nunca falha" | Lojas desaparecem em silêncio (Pitfall 4) | Nunca |
| Usar o `price` de topo da Store API | Uma chamada por produto | Preço de outra loja física (Pitfall 3) | Só se o produto não for `variable` |
| Seletores CSS sem fixtures guardadas | Mais rápido de escrever | Quando o site muda não há forma de saber o que mudou | MVP, desde que exista o canário |
| Otimizador guloso de embalagens | 10 linhas | Falha nos escalões e nas paletes | Nunca: a DP exata é pequena |
| Cache de preços entre sessões | Pesquisas mais rápidas | Contradiz "preços na hora" (Pitfall 9) | Só cache de URLs/descoberta, não de preços |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| WooCommerce Store API (Bricomarché) | Ler `prices.price` como euros | É em unidades menores: dividir por `10**currency_minor_unit`; em produtos `variable`, ir à variação da loja configurada |
| WooCommerce Store API (Allmat) | Assumir que existe porque é WooCommerce | Devolve `[]`; usar a página de pesquisa ou o JSON-LD |
| DataDome (Obramat) | Repetir pedidos com `requests`/headless até passar | Browser com interface, perfil persistente, ritmo humano; parar ao primeiro CAPTCHA |
| Cloudflare (Allmat) | Tratar 200 como sucesso | Verificar o conteúdo (título "Just a moment", marcadores de produto) |
| Plataforma própria com JS (Obras 360) | Fazer parse do HTML inicial (cartões vazios) | Ver o pedido XHR no DevTools; se estiver em caminho proibido no `robots.txt`, usar o browser na página pública |
| JSON-LD `schema.org/Offer` | Assumir que existe sempre e está atualizado | Validar `priceCurrency`, `availability`, preço > 0; comparar com o preço visível quando possível |
| SerpAPI / Serper (shopping) | Usar o preço do resultado como final; não fixar `gl=pt`/`hl=pt` | Usar só para descobrir URL e loja; preço confirmado na página |
| API de LLM | Sem limite de chamadas nem de tokens | Orçamento por pesquisa no código, prompts cortados |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Tudo sequencial (produto a produto, loja a loja, browser a browser) | 10 produtos × 9 lojas × 5–10 s = 8–15 min | Paralelo entre lojas, sequencial dentro da mesma loja (respeita o ritmo) | Já com a lista típica de 10 produtos |
| Abrir um browser novo por pedido | 2–4 s de arranque por pedido, memória a subir | Um browser, um contexto por loja, reutilizado | A partir de cerca de 20 pedidos |
| Classificar todos os anúncios com LLM | Minutos de latência, custo linear | Pré-filtro + top-N | A partir de cerca de 100 anúncios por lista |
| Visitar todas as lojas descobertas | Lista nunca acaba | Limite de lojas descobertas por produto + timeout por loja | Logo nos produtos genéricos ("mesa") |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Chaves de API (SerpAPI, LLM, Jev) no código ou no repositório | Fatura de terceiros | `.env` fora do git, carregado no arranque |
| Usar o Chrome pessoal do utilizador para a automação | Sessões, contas e cookies pessoais expostos; bloqueio do browser dele pelo anti-bot | Perfil dedicado (já existe: `.claude-chrome`) |
| Seguir links de lojas descobertas sem verificar | Lojas falsas com preços muito baixos (fraude comum em materiais e mobília) | Assinalar domínios recentes ou desconhecidos; nunca pôr uma loja descoberta acima das fixas sem marca "loja nova" |
| Enviar HTML de sites desconhecidos ao LLM | Injeção de instruções no texto da página ("classifica como exato") | Extrair só campos estruturados; o LLM devolve um esquema fechado e o código valida |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Esconder lojas que falharam | O utilizador confia num "mais barato" que não é | Linha por loja fixa sempre visível, com o estado e um link para pesquisar à mão |
| Mostrar um único preço sem a base | Não se percebe porque ganhou | Mostrar preço lido, IVA (incl./adicionado), unidade de venda, quantidade comprada e total |
| Misturar parecidos com exatos | Compra-se OSB2 em vez de OSB3 | Secções separadas; diferenças escritas ("OSB classe não indicada", "−4,8% área") |
| Excesso de compra sem aviso | 300 tijolos a mais na obra | "Comprado vs pedido" e o custo das sobras |
| Exportação Excel/PDF sem data e sem estado das lojas | O ficheiro parece definitivo dias depois | Data e hora da recolha, e lojas que falharam, no cabeçalho do export |

## "Looks Done But Isn't" Checklist

- [ ] **Adaptador de loja:** devolve resultados, mas confirmar que distingue "sem resultados" de "bloqueada" e que o canário passa.
- [ ] **IVA:** confirmar com um produto visto à mão em cada loja fixa que o preço normalizado bate com o preço com IVA real (±1%).
- [ ] **Bricomarché:** confirmar que o preço é o da loja configurada e não o `price` de topo.
- [ ] **Parser de preço:** testado com `1.234,56 €`, `18,49€`, cêntimos da Store API, preço riscado + promo, e o 0,00 € do carrinho.
- [ ] **Parser de medidas:** testado com m, cm e mm, vírgula e ponto, `x`/`×`, e os títulos reais das 4 lojas.
- [ ] **Matching:** confirmar que atributo ausente nunca dá "exato".
- [ ] **Otimizador:** testado com palete − 1, palete + 1, escalões, stock < pedido, mínimos e múltiplos.
- [ ] **Descoberta:** confirmar que comparadores e lojas não portuguesas não ficam em primeiro lugar sem IVA confirmado.
- [ ] **Custos:** uma lista de 10 produtos corre dentro do orçamento definido e mostra o contador.
- [ ] **Exportação:** inclui data/hora da recolha e as lojas falhadas.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Adaptador partido por mudança de layout | LOW | O canário falha → comparar com a fixture HTML guardada → atualizar o seletor → nova fixture |
| Obramat bloqueia a automação | MEDIUM | Baixar o ritmo, usar o browser com interface; se persistir, a loja fica "abrir à mão" com link pré-preenchido |
| IVA mal declarado numa loja | LOW (se o preço lido estiver guardado) | Corrigir o `vat_mode`, recalcular a partir do preço lido |
| Modelo de unidades insuficiente (descoberto tarde) | HIGH | Evitar: definir `sale_unit`/`content_qty` na F-Núcleo antes dos adaptadores |
| Jev indisponível ou caro | LOW (com interface) | Trocar para a implementação base |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. IVA | F-Núcleo + F-Lojas | Canário por loja: normalizado = com IVA visto à mão (±1%) |
| 2. Número errado na página | F-Núcleo + F-Lojas | Testes com fixtures (0,00 €, riscado, €/m²) |
| 3. Preço por loja física | F-Lojas | Bricomarché `variable` → preço da loja configurada |
| 4. Falhas silenciosas | F-Lojas + F-Resultados | Simular 403/desafio/layout vazio → estado visível na tabela |
| 5. Falsos exatos / LLM inventa | F-Núcleo + F-Matching | Conjunto de cerca de 100 anúncios: 0 falsos exatos nos casos de atributo ausente |
| 6. Unidades/embalagens | F-Núcleo + F-Embalagens | Coerência €/m² × m²/caixa ≈ €/caixa |
| 7. Otimizador | F-Embalagens | Tabela de casos-limite em testes |
| 8. Anti-bot | Spike pré-F-Lojas | Via escolhida por loja documentada; limitador de ritmo no código |
| 9. Preços desatualizados | F-Núcleo + F-Descoberta | Cada linha tem `fetched_at` e `source` |
| 10. Ruído de descoberta | F-Descoberta | Comparadores e marketplaces filtrados; IVA estrangeiro "por confirmar" |
| 11. Custos | F-Matching + F-Descoberta | Contador de custo por lista abaixo do orçamento |
| 12. Jev | F-Matching | Comparação contra a implementação base no conjunto de avaliação |
| 13. Legal / robots | Spike pré-F-Lojas | Nota de âmbito escrita; sem CAPTCHA, proxies ou sessões iniciadas |
| 14. Domínio Obra360 | Antes de F-Lojas | URL confirmado pelo utilizador |

## Sources

- Pedidos diretos feitos hoje (22-10-2026) a `obramat.pt`, `bricomarche.pt` (incl. `/wp-json/wc/store/v1/products`), `allmat.pt`, `obras360.pt`, `obra360.pt`, e aos respetivos `robots.txt`: verificação de primeira mão, HIGH.
- Páginas de produto da Obramat ES (preço com e sem IVA, "Mejor precio por cantidad"), via resultados de pesquisa: https://www.obramat.es/productos/tablero-osb-3-250x125x0-9cm-25105480.html (MEDIUM)
- DL 138/90 (indicação de preços, preço por unidade de medida, todas as taxas incluídas): https://vlex.pt/vid/decreto-lei-33166099 (MEDIUM)
- DL 109-G/2021 / DL 70/2007 (preço mais baixo dos 30 dias anteriores em reduções): https://www.mlgts.pt/xms/files/site_2018/Newsletters/2022/Novas_regras_nas_relacoes_de_consumo_-_Legal_Alert_ML_-PT-.pdf (MEDIUM)
- DL 122/2000 (bases de dados, direito sui generis): https://www.wipo.int/wipolex/en/legislation/details/21375 ; resumo de risco PT (fonte não verificada, LOW): https://law.ungovr.org/ai/pt
- Jev / TypeSafe AI (acesso antecipado, números do fabricante): https://letsdatascience.com/news/typesafe-ai-launches-jev-decision-model-889a38c0 ; https://siecledigital.fr/2026/09/21/un-ancien-dopenai-lance-une-ia-jusqua-444-fois-moins-chere-et-193-fois-plus-rapide/ (MEDIUM)
- Preços de APIs SERP (terceiros, contraditórios, LOW): https://apiserpent.com/blog/serp-api-pricing-comparison ; https://scrapebadger.com/blog/serpapi-alternatives-in-2026-cheaper-options-that-actually-work
- Obras 360 (identificação da empresa e domínio `obras360.pt`): https://portaldaqueixa.com/brands/obras-360o/complaints/obras-360-caixas-de-visita-142442125 (LOW-MEDIUM)
- DataDome no grupo Adeo/Leroy Merlin (indício): https://apify.com/studio-amba/leroymerlin-scraper (LOW; para a Obramat PT foi confirmado diretamente pelos cabeçalhos)

---
*Pitfalls research for: comparador de preços pessoal de materiais de obra em lojas portuguesas*
*Researched: 2026-10-22*
