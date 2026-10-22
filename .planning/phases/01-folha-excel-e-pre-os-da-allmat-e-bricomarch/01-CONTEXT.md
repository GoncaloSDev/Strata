# Phase 1: Folha Excel e preços da Allmat e Bricomarché - Context

**Gathered:** 2026-10-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Linha de comandos que lê a folha Excel do modelo da app (ou texto colado no terminal, para pesquisas rápidas) e devolve, para cada linha, os preços na hora da Allmat e da Bricomarché: preço com IVA 23% e origem do IVA, preço unitário normalizado, stock quando a loja o indica e o estado de cada loja. Inclui o comando que gera o modelo Excel e a verificação das lojas (STORE-07).

Fora desta fase: Obras 360 e Obramat (Phase 2), classificação exato/parecido e uso de Família/Tamanho/Referência (Phase 3), custo total para a quantidade e folha preenchida (Phase 4), UI e exportação (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Saída no terminal
- **D-01:** Cada item aparece com uma secção por loja (Allmat, depois Bricomarché). Cada secção começa pelo estado da loja (ok / sem resultados / bloqueada / erro / tempo esgotado), sempre visível, também quando não há ofertas.
- **D-02:** Até 5 ofertas por loja e por item. Quando há mais, uma linha diz quantas ficaram de fora (ex.: "+14 ofertas não mostradas"). Nada desaparece em silêncio.
- **D-03:** Ordem: mais barato primeiro, pelo preço em € na unidade pedida pela linha (ex.: €/m² se a linha pede m²). As ofertas que não dá para converter para a unidade pedida (ex.: vendidas à unidade, área desconhecida) vão para o fim, com o motivo escrito.
- **D-04:** Só terminal. Esta fase não grava CSV nem JSON de resultados para o utilizador. A folha preenchida chega na Phase 4 e o Excel detalhado na Phase 5.

### Modelo Excel
- **D-05:** Um comando grava `modelo.xlsx` na pasta atual (ex.: `uv run python -m strata modelo`). Se o ficheiro já existir, não escreve por cima: para, com uma mensagem a dizê-lo.
- **D-06:** O modelo traz os cabeçalhos (Produto, Família, Tamanho, Unidade, Qty, Referência, Notas) e 2–3 linhas de exemplo (ex.: "OSB 12 mm" / 30 / un; "cimento" / 10 / saco).
- **D-07:** No modelo, a coluna Unidade tem uma lista pendente (validação de dados) com un, m², m, kg, L, saco. Ao ler, também aceita sinónimos comuns (m2, unid, uni, lt, l, sacos), sem contar maiúsculas nem espaços. Um valor que não bate com nenhum torna a linha inválida: "unidade desconhecida: X".
- **D-08:** As colunas encontram-se pelo nome do cabeçalho, sem contar maiúsculas nem acentos. A ordem é livre e as colunas extra (ex.: Obra, Fornecedor) são ignoradas na leitura. — **Reversibility:** costly — a Phase 4 escreve na folha do utilizador a contar com este mapeamento por nome; mudar para posição fixa obriga a rever a leitura e a escrita.
- **D-09:** A folha lida é a primeira que tem Produto, Unidade e Qty nas primeiras 10 linhas, e a linha onde estão passa a ser a dos cabeçalhos. Se nenhuma folha os tiver, o erro diz quais colunas faltam. O número de linha nas mensagens é o número de linha do Excel (o que o utilizador vê à esquerda).

### Texto colado
- **D-10:** Sem caminho de ficheiro, o comando lê do terminal: o utilizador cola as linhas e termina com uma linha vazia. Não há entrada por `.txt`.
- **D-11:** A quantidade e a unidade ficam no fim da linha ("OSB 12mm 30 un", "cimento 10 saco"). Números no meio (como o "12mm") ficam na descrição. Aceita os mesmos sinónimos de unidade de D-07.
- **D-12:** Uma linha sem unidade assume "un" e uma linha sem quantidade assume 1. Nos dois casos, a pesquisa corre na mesma e aparece um aviso (ex.: "unidade assumida: un"). Isto é só para o texto colado: na folha Excel, Unidade ou Qty em falta continuam a tornar a linha inválida (critério 1 do ROADMAP).

### O que se pesquisa
- **D-13:** Só o Produto vai para a pesquisa da loja, tal como está escrito. Família, Tamanho e Referência são lidos e guardados no item, mas só entram na pesquisa e na classificação na Phase 3 (LIST-06). Notas não é usada.
- **D-14:** Se uma loja devolver zero resultados, a app faz uma segunda pesquisa alargada, sem medidas nem números (ex.: "OSB 12mm" → "OSB"), e marca essas ofertas como "pesquisa alargada". Se continuar a zero, o estado fica "sem resultados". É uma só tentativa extra por loja e por item (na Bricomarché custa cerca de 12 s a mais).
- **D-15:** As ofertas cujo título não contém as palavras da pesquisa são escondidas, mas contadas numa linha visível (ex.: "+12 ofertas escondidas: título sem 'osb'"). Serve para cortar resultados que só batem na descrição, como parafusos "para OSB". Na pesquisa alargada, compara com as palavras dessa pesquisa.

### Claude's Discretion
- Verificação das lojas (STORE-07): nome do comando, produtos de teste por loja (ex.: "cimento" na Allmat, que não vende OSB) e formato do relatório. Tem de dizer, por adaptador, se ainda devolve preços válidos (preço acima de zero, IVA e unidade coerentes).
- Ritmo, timeouts, paralelismo e paginação por loja (ex.: leitura de 30 s na Bricomarché, que demora cerca de 12 s por página). Confirmar se `orderby=price` funciona com `type=variation`.
- Nomes exatos dos comandos e das opções, e o desenho da tabela no terminal (colunas, largura, cores).
- Normalização ao comparar palavras para D-15: acentos, maiúsculas, "12 mm" = "12mm", plural simples. Leitura de números com vírgula decimal ("2,5 m²").
- Allmat sem área da caixa no HTML do produto: mostrar a oferta com o preço por caixa e o €/m² como desconhecido, no fim da lista (D-03). Nunca a esconder.
- Gravar respostas das lojas como fixtures para os testes (ex.: uma opção `--record`). É ferramenta de desenvolvimento, não exportação para o utilizador.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Âmbito e requisitos
- `.planning/ROADMAP.md` §Phase 1 — objetivo, os 5 critérios de sucesso e a nota de stack (openpyxl para ler a folha e gerar o modelo)
- `.planning/REQUIREMENTS.md` — LIST-01, LIST-02, LIST-04, LIST-05, STORE-01, STORE-02, STORE-05, STORE-07, PRICE-01, PRICE-02, RES-02
- `.planning/PROJECT.md` §Key Decisions — Bricomarché com o mínimo entre lojas físicas, Excel de formato fixo, folha preenchida sempre em cópia
- `.planning/STATE.md` §Decisions e §Blockers/Concerns — decisões de revisão (openpyxl) e a lentidão da Bricomarché

### Lojas (Allmat e Bricomarché, WooCommerce Store API)
- `.planning/research/ARCHITECTURE.md` §Per-Store Extraction Feasibility — endpoints sondados ao vivo; Bricomarché `type=variation` agrupado por `parent` com o mínimo por loja física e o link no caminho da loja; Allmat com o preço por caixa e a área da caixa só no HTML do produto
- `.planning/research/ARCHITECTURE.md` §Pattern 1, §Pattern 3, §Pattern 5 — adaptador separado do transporte, IVA como política + evidência, limites por host
- `.planning/research/ARCHITECTURE.md` §Anti-Pattern 1–3 — não confiar no `price` de topo, comparar a variante e não a linha pai, estados separados em vez de um só "falhou"
- `.planning/research/ARCHITECTURE.md` §Recommended Project Structure — organização sugerida (`core/` sem I/O, adaptadores, fetcher)
- `.planning/research/SUMMARY.md` §Phase 1 e conflitos C4–C6 — o que a fase entrega; `[]` da Allmat = sem resultados; bibliotecas da STACK em vez das da ARCHITECTURE

### Armadilhas a evitar
- `.planning/research/PITFALLS.md` §Pitfall 1 (IVA), §Pitfall 2 (número errado: 0,00 € do mini-carrinho, cêntimos da Store API), §Pitfall 3 (preço por loja física), §Pitfall 4 (falhas silenciosas, "sem resultados" só com o marcador da loja), §Pitfall 6 (unidades e embalagens)

### Stack e ambiente
- `.planning/research/STACK.md` — Python 3.13 + uv, curl_cffi com `impersonate="chrome"`, selectolax, pytest com fixtures em ficheiro, `Decimal` para dinheiro. Exceção: openpyxl substitui o XlsxWriter para ler a folha e gerar o modelo (ROADMAP, nota de stack da Phase 1)
- `CLAUDE.md` — correr sempre `uv run python -m strata`; neste Windows usar `python`, nunca `python3`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Nenhum: o repositório ainda só tem documentos de planeamento. Esta fase cria o pacote `strata`.

### Established Patterns
- Ainda não há. Os padrões a seguir vêm de `.planning/research/ARCHITECTURE.md` (pipeline num só sentido, adaptadores que só reportam o que a loja diz mais a evidência, aritmética de dinheiro num `core/` puro e testado).

### Integration Points
- Ponto de entrada: `uv run python -m strata`, com subcomandos para pesquisar (ficheiro `.xlsx` ou texto colado), gerar o modelo e verificar as lojas. As Phases 2–4 acrescentam lojas e cálculo a este mesmo ponto de entrada; a Phase 5 põe a UI por cima do mesmo núcleo.

</code_context>

<specifics>
## Specific Ideas

- "OSB" na Allmat tem de aparecer como "sem resultados" (a Allmat não vende OSB), nunca como erro nem omitido. Exemplo do ROADMAP.
- Linhas de exemplo do texto colado: "OSB 12mm 30 un", "cimento 10 saco".
- O utilizador prefere ver primeiro o mais barato, mesmo antes de haver classificação. O filtro de título (D-15) e a contagem do que fica escondido (D-02, D-15) existem para que isso não se transforme numa lista de acessórios.

</specifics>

<deferred>
## Deferred Ideas

Nenhuma: a discussão ficou dentro do âmbito da fase.

</deferred>

---

*Phase: 01-folha-excel-e-pre-os-da-allmat-e-bricomarch*
*Context gathered: 2026-10-22*
