# Phase 1: Folha Excel e preços da Allmat e Bricomarché - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-22
**Phase:** 01-Folha Excel e preços da Allmat e Bricomarché
**Areas discussed:** Saída no terminal, Modelo Excel, Texto colado, O que se pesquisa

---

## Saída no terminal

| Option | Description | Selected |
|--------|-------------|----------|
| As 5 primeiras | Chega para ver se a loja encontrou o produto, sem encher o ecrã | ✓ |
| Todas | Nada fica escondido, mas pode dar dezenas de linhas por loja | |
| Só a mais barata | Curto, mas sem classificação pode ser um acessório | |

| Option | Description | Selected |
|--------|-------------|----------|
| Relevância da loja | A ordem da pesquisa do site; ordenar por preço fica para a Phase 3 | |
| Mais barato primeiro | Por €/unidade; antes da Phase 3 pode pôr acessórios no topo | ✓ |
| Tu decides | À escolha do Claude | |

| Option | Description | Selected |
|--------|-------------|----------|
| Só terminal | O mínimo; folha preenchida na Phase 4, Excel na Phase 5 | ✓ |
| Também um CSV | Todas as ofertas num .csv | |
| Também um JSON | Tudo em bruto, para depurar | |

| Option | Description | Selected |
|--------|-------------|----------|
| Uma secção por loja | Item → Allmat (estado + ofertas) → Bricomarché (estado + ofertas) | ✓ |
| Uma tabela por item | Lojas misturadas, com coluna Loja | |

| Option | Description | Selected |
|--------|-------------|----------|
| Unidade pedida 1.º | € na unidade da linha; as que não convertem vão para o fim, com motivo | ✓ |
| Preço da embalagem | Preço com IVA tal como a loja vende | |
| Tu decides | À escolha do Claude | |

**User's choice:** 5 ofertas por loja, mais barato primeiro na unidade pedida, só terminal, uma secção por loja.
**Notes:** O utilizador escolheu "mais barato primeiro" em vez da recomendação (relevância da loja), apesar do aviso sobre acessórios antes da Phase 3.

---

## Modelo Excel

| Option | Description | Selected |
|--------|-------------|----------|
| Comando que o grava | Grava modelo.xlsx na pasta atual, nunca por cima | ✓ |
| Ficheiro no repositório | modelo.xlsx fixo, copiado à mão | |

| Option | Description | Selected |
|--------|-------------|----------|
| 2–3 linhas de exemplo | Ex.: OSB 12 mm / 30 / un; cimento / 10 / saco | ✓ |
| Só os cabeçalhos | Folha limpa | |
| Exemplos + folha de ajuda | Segunda folha a explicar colunas e unidades | |

| Option | Description | Selected |
|--------|-------------|----------|
| Lista + sinónimos | Lista pendente no modelo; ao ler aceita m2, unid, lt, sacos... | ✓ |
| Só os valores exatos | Outro valor dá "unidade desconhecida" | |

| Option | Description | Selected |
|--------|-------------|----------|
| Pelo nome do cabeçalho | Ordem livre e colunas extra permitidas | ✓ |
| Posição fixa A–G | Colunas exatas do modelo, por esta ordem | |

| Option | Description | Selected |
|--------|-------------|----------|
| Procura os cabeçalhos | Primeira folha com Produto/Unidade/Qty nas primeiras 10 linhas | ✓ |
| Primeira folha, linha 1 | Cabeçalhos obrigatoriamente na linha 1 | |

**User's choice:** Todas as recomendações.
**Notes:** —

---

## Texto colado

| Option | Description | Selected |
|--------|-------------|----------|
| Colar no terminal | Sem ficheiro; termina com linha vazia | ✓ |
| Ficheiro .txt | Caminho de um .txt | |
| Os dois | Colar ou .txt | |

| Option | Description | Selected |
|--------|-------------|----------|
| No fim | "OSB 12mm 30 un"; o "12mm" do meio fica na descrição | ✓ |
| No início ou no fim | Aceita também "30 un OSB 12mm" | |

| Option | Description | Selected |
|--------|-------------|----------|
| Assume 1 / un e avisa | Pesquisa na mesma e mostra o valor assumido | ✓ |
| Linha inválida | Mesma regra da folha Excel | |

**User's choice:** Todas as recomendações.
**Notes:** —

---

## O que se pesquisa

| Option | Description | Selected |
|--------|-------------|----------|
| Só o Produto | Família/Tamanho/Referência entram na Phase 3 | ✓ |
| Produto + Tamanho | Mais preciso, mais risco de "sem resultados" | |

| Option | Description | Selected |
|--------|-------------|----------|
| Alarga uma vez e avisa | Tira medidas e números e tenta de novo, marcado "pesquisa alargada" | ✓ |
| Fica "sem resultados" | Um pedido por loja e por item | |

| Option | Description | Selected |
|--------|-------------|----------|
| Esconder e contar | Só fica o que tem as palavras no título, com contagem do que ficou escondido | ✓ |
| Mostrar tudo | Tal como a loja devolve | |

**User's choice:** Todas as recomendações.
**Notes:** —

---

## Claude's Discretion

- Verificação das lojas (STORE-07): comando, produtos de teste e relatório.
- Ritmo, timeouts, paralelismo e paginação por loja.
- Nomes dos comandos e opções; desenho da tabela no terminal.
- Normalização de palavras e números (acentos, "12 mm" = "12mm", vírgula decimal).
- Allmat sem área da caixa: mostrar com €/m² desconhecido, no fim.
- Gravação de fixtures para testes.

## Deferred Ideas

Nenhuma.
