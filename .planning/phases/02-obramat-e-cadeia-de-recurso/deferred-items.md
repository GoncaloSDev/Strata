# Itens adiados (fase 02)

- **Percentagem do escalão da Obramat sem arredondar** (visto na corrida ao vivo do 02-06): `src/strata/report.py:24` mostra `escalões: −5,0021285653469561515538527% a partir de 324` e `−4,9993174993174993174993175% a partir de 36`. A percentagem vem de dividir o total da palete pelo preço da unidade (ambos arredondados pela loja); `fmt_qty` mostra todas as casas. Só afeta a apresentação; o custo com escalões é da Phase 4. Fora do âmbito do 02-06.
