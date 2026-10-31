---
phase: 02-obramat-e-cadeia-de-recurso
review: 02-REVIEW.md
total: 12
open: 9
fixed: 3
---

# Disposição do code review da fase 02

Uma linha por achado do 02-REVIEW.md. Todos começam `open`; mudam para `fixed`, `deferred` ou `wontfix` quando alguém decidir.

| ID | Severidade | Achado | Disposição |
|----|-----------|--------|------------|
| CR-01 | critical | Degrau IA vazio ou todo rejeitado aparece como "sem resultados" | fixed (02-07, 7e1c401) |
| CR-02 | critical | Validação das ofertas da IA não liga preço nem link ao texto enviado | fixed (02-07, c4e728c) |
| WR-01 | warning | A IA não sabe a unidade do preço (por m² vira preço de artigo) | open |
| WR-02 | warning | Depois de um bloqueio, o JSON-LD repete o mesmo pedido bloqueado | open |
| WR-03 | warning | Falha a arrancar o Chrome não fica guardada; Chrome lançado pode ficar aberto | open |
| WR-04 | warning | Cancelar o `claude -p` mata o processo sem esperar | open |
| WR-05 | warning | Um produto mal formado da Obramat derruba o degrau API inteiro | open |
| WR-06 | warning | Link de compra do JSON-LD não é validado | open |
| WR-07 | warning | `parse_price` multiplica por 10 preços com uma casa decimal e ponto | fixed (02-07, c4e728c) |
| IN-01 | info | Percentagem dos escalões sem limite de casas | open |
| IN-02 | info | Cliente `AsyncAnthropic` nunca fechado | open |
| IN-03 | info | `past_challenge` atribui à DataDome qualquer erro de leitura | open |
