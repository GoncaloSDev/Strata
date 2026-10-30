# Phase 2: Obramat e cadeia de recurso - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-30
**Phase:** 02-obramat-e-cadeia-de-recurso
**Areas discussed:** Preço da Obramat por loja, Bloqueio e browser, Preços lidos por IA, Quando escalar a cadeia

---

## Preço da Obramat por loja

| Option | Description | Selected |
|--------|-------------|----------|
| Mais barato entre lojas | Como na Bricomarché: loja física mais barata com stock e o nome dela | ✓ |
| Uma loja fixa minha | Só o preço e stock da Obramat escolhida | |
| Preço nacional (000) | Preço por omissão do site, sem loja | |

| Option | Description | Selected |
|--------|-------------|----------|
| Só os 5 mais baratos | Os 5 mais baratos no nacional vistos loja a loja | |
| Só o mais barato | Apenas o n.º 1 visto loja a loja | |
| Tu decides | Fixar depois de medir ao vivo | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| Todas, como na Bricomarché | Mesma regra das outras lojas com várias lojas físicas | ✓ |
| Só uma lista minha | Lojas Obramat escolhidas num ficheiro de configuração | |

| Option | Description | Selected |
|--------|-------------|----------|
| Nacional com nota | Preço 000 com nota "pode variar por loja" | |
| Por loja, custe o que custar | Mesmo que rebente os 5 minutos | |
| Perguntar-me de novo | Planeamento para e pergunta com números medidos | ✓ |

**User's choice:** loja física mais barata, todas as lojas; corte K e o caso "preço por loja caro" ficam para depois de medir (o segundo volta ao utilizador).

---

## Bloqueio e browser

| Option | Description | Selected |
|--------|-------------|----------|
| Chrome dedicado, janela visível | Perfil .claude-chrome, porta 9222, cookies guardados | ✓ |
| Chrome dedicado, minimizado | O mesmo, janela minimizada | |
| Headless | Sem janela | |

| Option | Description | Selected |
|--------|-------------|----------|
| Obramat parada no resto da lista | "Abrir à mão" com link em todos os itens seguintes | ✓ |
| Parada só nesse item | Próximo item volta a tentar | |
| Pausa para eu resolver | A app espera que o utilizador resolva o CAPTCHA | |

| Option | Description | Selected |
|--------|-------------|----------|
| Fica no browser até ao fim | Depois do 1.º bloqueio, browser no resto da lista | ✓ |
| Volta a tentar o simples | Cada item começa pelo pedido simples | |

| Option | Description | Selected |
|--------|-------------|----------|
| Sim, abre e fecha no fim | A app lança o Chrome dedicado e fecha-o se foi ela a abrir | ✓ |
| Sim, e deixa-o aberto | Abre e deixa aberto | |
| Não, só avisa | Degrau browser falha com aviso | |

---

## Preços lidos por IA

| Option | Description | Selected |
|--------|-------------|----------|
| Aparece, mas nunca como o 1.º | Marca "lido por IA", depois das ofertas estruturadas | ✓ |
| Compete igual, com marca | Ordenada pelo preço como as outras | |
| Só se o preço aparecer no texto | Descartada se o número não existir no texto | |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 página por loja e item | Máximo 1 chamada por (item, loja), texto cortado | ✓ |
| Teto em euros por lista | Ex.: 0,50 € por execução | |
| Sem teto | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Até 5, com link de cada | Mesmo número do terminal; passam pelo filtro D-15 | ✓ |
| Só a primeira | Uma oferta por loja e item | |

Pergunta sobre a falta de `ANTHROPIC_API_KEY` (opções: "Salta, com motivo visível" / "Recusa arrancar"). O utilizador respondeu com outra pergunta: se em vez da API se podia usar o limite da conta Claude Pro, como fazem agentes como o Hermes. Explicado: o caminho permitido é chamar o Claude Code (`claude -p`) como subprocesso; reaproveitar o token OAuth noutra ferramenta vai contra os termos. Nova pergunta:

| Option | Description | Selected |
|--------|-------------|----------|
| API se houver chave, senão claude -p | API mais rápida; sem chave usa a conta Pro; sem nenhum, salta com motivo | ✓ |
| Só claude -p | Nunca a API paga | |
| Só API | Plano original | |

---

## Quando escalar a cadeia

| Option | Description | Selected |
|--------|-------------|----------|
| As 4 lojas fixas | Qualquer loja cujo principal falhe tenta os outros degraus | ✓ |
| Só a Obramat | As outras 3 ficam como na fase 1 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Bloqueada, erro e tempo esgotado | "Sem resultados" não escala | ✓ |
| Só bloqueada e erro | Tempo esgotado não escala | |
| Também 0 ofertas mostradas | Escala quando o filtro esconde tudo | |

| Option | Description | Selected |
|--------|-------------|----------|
| 90 s para a cadeia inteira | Degraus partilham o prazo atual | ✓ |
| Prazo próprio por degrau | Ex.: 30 s browser, 30 s IA | |
| Tu decides | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Opção de comando também | Ex.: --sem-principal obramat, além dos testes | ✓ |
| Só nos testes | | |

---

## Claude's Discretion

- Corte K da Obramat (quantos produtos vistos loja física a loja física), depois de medir.
- Ritmo da Obramat, deteção de CAPTCHA vs bloqueio, corte de texto para a IA, nome da opção de recurso forçado, canário da Obramat, ligação ao Chrome dedicado.

## Deferred Ideas

- Usar o `claude -p` (conta Pro) na extração e classificação da Phase 3 — decidir lá, com medição.
