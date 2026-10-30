---
phase: "01"
slug: "folha-excel-e-pre-os-da-allmat-e-bricomarch"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-30"
---

# Phase 01 — Security

> Contrato de segurança da fase: registo de ameaças, riscos aceites e histórico de auditorias.
> Registo vindo dos `<threat_model>` dos 12 PLAN (escritos na altura do plano); nenhum SUMMARY tem `## Threat Flags`.
> Verificação ao nível ASVS 1 (grep no código), com `block_on: high`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| loja → Fetcher / adaptadores | Respostas HTTP (JSON e HTML) da Allmat, Bricomarché e Obras 360 | Preços, títulos, stock, links: não confiáveis |
| folha do utilizador → sheet.read_sheet | .xlsx escolhido pelo utilizador | Produto, unidade, quantidade: só lidos |
| stdin → text.read_pasted | Texto colado | Linhas de compra |
| texto de loja/folha → terminal | Títulos, notas e produto impressos | Texto que pode trazer sequências de controlo |
| strata → lojas | Pedidos a sites de terceiros | Ritmo e volume |
| --record → disco → repositório | Corpos de resposta gravados como fixtures | Sem cabeçalhos nem cookies |
| testes → lojas | Os testes não podem chegar às lojas | Nenhum |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-01-01 | Tampering | report.clean | medium | mitigate | `report.py:11-13` tira a categoria Unicode "C" | closed |
| T-01-02 | Tampering (preço) | allmat.parse_products, money.from_minor | high | mitigate | `allmat.py:81-82` `from_minor(price, currency_minor_unit)`, preço ≤ 0 fora; `fetch.py:95` `parse_float=Decimal` | closed |
| T-01-03 | Tampering (perda de dados) | sheet.write_template | high | mitigate | `sheet.py:125` `open(path, "xb")`; a folha do utilizador só tem `load_workbook` (`sheet.py:57`) | closed |
| T-01-04 | DoS | fetch, search_store | medium | mitigate | `__main__.py:36` `timeout=(10, 30)`; `search.py:22` `asyncio.timeout(90)` → "tempo esgotado" | closed |
| T-01-05 | DoS (contra a loja) | fetch.Host / LIMITS | medium | mitigate | `fetch.py:27` LIMITS por host, `fetch.py:41-44` semáforo + intervalo | closed |
| T-01-06 | Information Disclosure | fetch --record | low | mitigate | `fetch.py:88` grava só `r.content` | closed |
| T-01-07 | Spoofing | fetch / AsyncSession | medium | mitigate | Nenhum `verify=False` nem `http://` em `src/strata`; URLs base https fixos | closed |
| T-01-08 | DoS | sheet.read_sheet (XML) | low | accept | Ver Accepted Risks | closed |
| T-01-09 | Tampering | sheet.read_sheet | medium | mitigate | `sheet.py:85-97` validação por linha → `Invalida`; `SheetError` (`sheet.py:14-63`) | closed |
| T-01-10 | DoS | sheet.read_sheet | medium | mitigate | Linha a linha com `Invalida`; ficheiros ilegíveis → `SheetError` | closed |
| T-01-11 | Tampering (quantidade) | text.to_decimal | medium | mitigate | `text.py:29` rejeita `bool`; unidade só de `UNITS` | closed |
| T-01-12 | Tampering | text.read_pasted | low | mitigate | `__main__.py:65-66` stdin UTF-8; impressão via `report.clean` | closed |
| T-01-13 | Tampering (perda de dados) | sheet.read_sheet | high | mitigate | Uma só `.save(` (`sheet.py:126`, a do modelo) | closed |
| T-01-14 | Tampering (preço) | allmat.parse_box | high | mitigate | `allmat.py:49` só `#product-{id}`; `allmat.py:71` coerência de 2% | closed |
| T-01-15 | Repudiation | search_store, allmat.search | medium | mitigate | Contagem `hidden` e notas de limite (`allmat.py:135`) | closed |
| T-01-16 | DoS (contra a loja) | allmat.search | medium | mitigate | `MAX_PAGES = 3`, `MAX_BOX_PAGES = 10` (`allmat.py:19-21`) | closed |
| T-01-17 | Tampering (arredondamento) | money | medium | mitigate | `Decimal` em money; arredondar só em `fmt_*` (teste em test_money.py) | closed |
| T-01-18 | Spoofing (estado errado) | fetch.get_json / search_store | medium | mitigate | `StoreBlocked`/`StoreTimeout` em fetch.py; estados testados em test_search.py | closed |
| T-01-19 | Tampering (preço) | bricomarche.offer_from | high | mitigate | `bricomarche.py:49` preço > 0, sem "master"; preço do pai só ordena (`:31-34`) | closed |
| T-01-20 | Spoofing (link) | bricomarche.store_link | low | mitigate | `bricomarche.py:67-68` link `/{loja}/produto/{slug}/` | closed |
| T-01-21 | DoS (contra a loja) | bricomarche.search | medium | mitigate | `K = 10`, `MAX_PAGES = 3` (`bricomarche.py:17-19`) | closed |
| T-01-22 | Repudiation (IVA) | bricomarche.offer_from | medium | mitigate | `vat_origin` "regra da loja" na oferta; A9 confirmado na UAT (teste 3/9) | closed |
| T-01-23 | Tampering (preço) | obras360.offers_from_details | high | mitigate | `obras360.py:68-69` confronto ±0,01 € → `StoreError`; `:72` nota se taxa ≠ 23 | closed |
| T-01-24 | Tampering (preço do pai) | obras360.search | high | mitigate | Ofertas só de `product-details` (`obras360.py:133`) | closed |
| T-01-25 | Spoofing (widget) | obras360.widget_id | medium | mitigate | `obras360.py:31,37,58` `StoreError` visível | closed |
| T-01-26 | DoS (contra a loja) | obras360.search | medium | mitigate | `K = 20`, `MAX_PAGES = 3` (`obras360.py:17-19`); LIMITS 3 / 0,3 s | closed |
| T-01-27 | Tampering (terminal) | obras360 stock | low | mitigate | `obras360.py:23` remove tags; `report.clean` | closed |
| T-01-28 | Repudiation (falso verde) | search.verificar | medium | mitigate | `search.py:108` verificações por oferta, código 1 | closed |
| T-01-29 | Information Disclosure | --record | low | mitigate | Só corpos (`fetch.py:88`) | closed |
| T-01-30 | DoS (contra a loja) | search.verificar | low | mitigate | Canários um a um pelo mesmo Fetcher (`search.py:108-111`) | closed |
| T-01-31 | DoS / Information Disclosure | tests/conftest.py | low | mitigate | `conftest.py:15-20` fixture autouse bloqueia `AsyncSession.request` | closed |
| T-01-32 | Information Disclosure | tests/fixtures | low | mitigate | `grep -rliE "set-cookie\|authorization\|bearer\|csrf" tests/fixtures` vazio (2026-10-30) | closed |
| T-01-33 | DoS (contra a loja) | gravação "tinta branca" | low | mitigate | Uma corrida, sem ciclos (01-07-SUMMARY) | closed |
| T-01-34 | Repudiation (falso "ok") | search_store | medium | mitigate | Cabeçalho com contagem de escondidas; testes `tudo_escondido` | closed |
| T-01-35 | DoS (contra a loja) | pesquisa alargada | low | mitigate | No máximo uma pesquisa extra (D-14) | closed |
| T-01-36 | Tampering (outra medida) | obras360 filtro de variantes | low | accept | Ver Accepted Risks | closed |
| T-01-37 | DoS (contra a loja) | obras360.search | low | mitigate | K = 20 mantido | closed |
| T-01-38 | Repudiation | obras360 Found.hidden | medium | mitigate | Variantes cortadas somam a `hidden` (teste hidden == 6) | closed |
| T-01-39 | DoS (contra a loja) | verificar ao vivo | low | mitigate | Uma corrida, um termo de cada vez | closed |
| T-01-40 | Tampering (produto diferente) | words._stem | low | accept | Ver Accepted Risks | closed |
| T-01-41 | Repudiation ("ok" sem ofertas) | search_store detail | medium | mitigate | test_zero_ofertas_sem_escondidas_nao_diz_so_ok | closed |
| T-01-42 | DoS (contra a loja) | obras360 ordenação | low | mitigate | Só muda quem entra nos K = 20 | closed |
| T-01-47 | Repudiation (preço escondido) | bricomarche.offer_from | medium | mitigate | Nota "mais barata sem stock"; test_offer_from_prefere_a_loja_com_stock; UAT teste 9 | closed |
| T-01-48 | Tampering (stock errado) | bricomarche.has_stock | low | accept | Ver Accepted Risks | closed |
| T-01-49 | Tampering (terminal) | nota da loja | low | mitigate | Passa por `report.clean` em `_offer_lines` | closed |
| T-01-50 | Repudiation | search_store, print_item | medium | mitigate | `wide_only` contado na linha "+N ofertas escondidas" (D-02) | closed |
| T-01-51 | Tampering (produto errado) | words.title_matches | low | accept | Ver Accepted Risks | closed |
| T-01-52 | Tampering (terminal) | print_item, item.product | low | mitigate | Produto passa por `report.clean` | closed |
| T-01-53 | DoS (contra a loja) | search_store | low | mitigate | Nenhum pedido novo; `store.calls == ["OSB 12mm", "OSB"]` | closed |
| T-01-54 | DoS (contra a loja) | adaptadores (rank) | low | mitigate | K = 10, K = 20, MAX_BOX_PAGES = 10 iguais; LIMITS igual | closed |
| T-01-55 | Tampering (pesquisa alterada) | search_store | low | mitigate | A pesquisa enviada continua `b`; `store.ranks` testado | closed |
| T-01-56 | Repudiation | search_store, print_item | low | mitigate | WR-16 "1.ª pesquisa:" fixado em testes | closed |
| T-01-57 | Tampering (ordem) | words.words | low | accept | Ver Accepted Risks | closed |
| T-01-58 | DoS (CPU local) | words.words combinations | low | accept | Ver Accepted Risks | closed |
| T-01-SC | Tampering (cadeia de fornecimento) | uv add (PyPI) | high | mitigate | Checkpoint blocking-human no 01-01; `selectolax>=1.0,<1.1` (`pyproject.toml:12`); `uv.lock` no repositório | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-01-08 | Ficheiros do próprio utilizador; o openpyxl usa defusedxml se existir. Não se acrescenta dependência | plano 01-01 | 2026-10-22 |
| AR-02 | T-01-36 | Gama no nome do pai ("9-30MM"); a designação da variante fica à vista; exato/parecido na Phase 3 | plano 01-08 | 2026-10-23 |
| AR-03 | T-01-40 | Tabela de plurais junta formas a mais; título à vista; Phase 3 (MATCH-01/02) | plano 01-09 | 2026-10-23 |
| AR-04 | T-01-48 | O stock vem só da loja e aparece tal como a loja o escreve | plano 01-10 | 2026-10-24 |
| AR-05 | T-01-51 | Palavras não distinguem produto de menção; título à vista; Phase 3 | plano 01-11 | 2026-10-24 |
| AR-06 | T-01-57 | Ordem por palavras pode pôr outro produto à frente; continua sujeito ao passo do 01-11 | plano 01-12 | 2026-10-24 |
| AR-07 | T-01-58 | Custo quadrático só em títulos curtos (microssegundos) | plano 01-12 | 2026-10-24 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-30 | 55 | 55 | 0 | /gsd-secure-phase 1 (ASVS L1, grep no orquestrador; auditor dispensado pela regra de atalho) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-30
