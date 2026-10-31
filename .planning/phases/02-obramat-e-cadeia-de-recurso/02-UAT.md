---
status: testing
phase: 02-obramat-e-cadeia-de-recurso
source: [02-VERIFICATION.md]
started: 2026-10-31T14:50:00Z
updated: 2026-10-31T14:50:00Z
---

## Current Test

number: 1
name: Folha de 10 itens e verificar, com cronómetro
expected: |
  Folha: menos de 300 s, 10 cabeçalhos "Linha N", 4 linhas de estado por item.
  verificar: rc=0 e 5 linhas OK, a da Obramat com "método: browser".
awaiting: user response

## Tests

### 1. Folha de 10 itens e verificar, com cronómetro
`Measure-Command { uv run python -m strata pesquisar <folha-10-itens>.xlsx }` e `uv run python -m strata verificar`
expected: Folha em menos de 300 s, 10 cabeçalhos "Linha N", 4 linhas de estado por item. verificar com rc=0 e 5 linhas OK, a da Obramat com "método: browser". Prova do LIST-03.
result: [pending]

### 2. WINDOWS.md #2: 403 real da Obramat
Decidir se o caminho "API: HTTP 403 → browser" fica aceite pelo teste `test_obramat_bloqueada_vai_ao_browser_e_fica_la` e pela corrida com `--sem-principal obramat`, ou se espera por um 403 real.
expected: Decisão registada: `gsd-tools windows waive 2 "<motivo>"` ou manter aberto.
result: [pending]

### 3. Regra NO_STORE → browser (02-06)
Uma resposta da Obramat com a nota NO_STORE vinda de um degrau sem browser salta para o browser. Não está no D-14.
expected: Aceitar (fica como emenda ao D-14/D-18 no CONTEXT) ou pedir outra regra.
result: [pending]

### 4. Degrau IA ao vivo pelo `claude -p`
`printf "placa osb 1 un\n\n" | uv run python -m strata pesquisar --sem-principal obramat` com o browser a falhar de propósito (ex.: porta 9222 ocupada).
expected: A Obramat aparece com ofertas "método: IA" e "lido por IA" no fim, ou falhada com o motivo de cada degrau a acabar em "IA: …"; nunca "sem resultados".
result: [pending]

### 5. Título da oferta IA não validado
Na página gravada "osb", o link e o preço da "TINTA PARA PISCINAS … 4L AZUL" (33,60 €) com o título "PLACA OSB 3 250X125X1,8CM" são aceites como oferta de OSB.
expected: Decisão registada: aceitar o risco (a oferta sai "lido por IA" e no fim da loja) ou abrir um gap pequeno (exigir o título no texto logo antes de `<URL>` e juntar um teste).
result: [pending]

### 6. Rever as 5 proibições judgment
Lista na secção "Proibições" do 02-VERIFICATION.md. Veredito do verificador: cumpridas, não autoritativo.
expected: Confirmar ou apontar a que falha.
result: [pending]

## Summary

total: 6
passed: 0
issues: 0
pending: 6
skipped: 0
blocked: 0

## Gaps
