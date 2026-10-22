# Walking Skeleton — Strata

**Phase:** 1
**Generated:** 2026-10-22

## Capability Proven End-to-End

O utilizador grava o modelo com `uv run python -m strata modelo`, preenche-o e `uv run python -m strata pesquisar modelo.xlsx` mostra no terminal, para cada linha, a secção da Allmat com o estado da loja e as ofertas com preço com IVA, origem do IVA, stock e link (plano 01-01). Os planos 01-02 a 01-06 acrescentam fatias por cima deste esqueleto sem mudar as decisões abaixo.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Linguagem e ambiente | Python 3.13 + uv (`uv run python -m strata ...`), pacote `src/strata/` criado com `uv init --package` | Decisão do projeto (STACK.md); `python3` não funciona neste Windows |
| Ponto de entrada | `argparse` em `src/strata/__main__.py`: subcomandos `pesquisar [ficheiro.xlsx] [--record DIR]`, `modelo`, `verificar`; `main(argv=None, fetch=None) -> int` | Três subcomandos não justificam click/typer; o parâmetro `fetch` é a costura para os testes sem rede |
| Dados | Sem base de dados. Tudo em memória numa execução; a folha do utilizador só é lida (openpyxl, modo normal, `data_only=True`); o `modelo.xlsx` é criado com `open(path, "xb")` | PROJECT.md exclui histórico e base de preços; o ficheiro do utilizador nunca é alterado |
| HTTP | Um só `Fetcher` (`src/strata/fetch.py`) sobre `curl_cffi.requests.AsyncSession(impersonate="chrome", timeout=(10, 30))`, com limite e intervalo por host e a classificação de falhas (`StoreBlocked`, `StoreError`, `StoreTimeout`) | Impressão TLS do Chrome; um sítio só para ritmo, timeouts e estados |
| Contrato de loja | Cada loja é um módulo em `src/strata/stores/` com `NAME` e `async def search(query, fetch) -> Found`; o adaptador lança exceções e um único `try/except` em `search.search_store` converte-as em estado | Estados separados (ok / sem resultados / bloqueada / erro / tempo esgotado), nunca `return []` em silêncio |
| Ordem das lojas | `search.STORES` = Allmat, Bricomarché, Obras 360 (D-01) | A saída mostra sempre as três secções, pela mesma ordem |
| Dinheiro | `Decimal` em todo o lado: `json.loads(..., parse_float=Decimal)`, cêntimos da Store API com `money.from_minor`, arredondamento só ao mostrar (`ROUND_HALF_UP`) | Erros de dinheiro são o risco principal; o preço vem sempre de campo estruturado |
| Modelo de dados | `src/strata/models.py`: `Item`, `Invalida`, `Offer`, `Found`, `StoreResult`, `ItemResult` (dataclasses) | Contrato que as Phases 2–5 estendem |
| Saída | Só terminal (`src/strata/report.py`), um item de cada vez à medida que fica pronto (D-04) | A folha preenchida chega na Phase 4 e a app NiceGUI na Phase 5, por cima do mesmo núcleo |
| Testes | pytest; `tests/conftest.py` com `FakeFetcher` (rotas por substring do URL, ficheiros em `tests/fixtures/`) e bloqueio de rede autouse; `--record DIR` grava corpos de resposta para fixtures | O vcrpy não interceta curl_cffi; separar "buscar" de "interpretar" |
| Layout | `src/strata/{__main__,models,text,sheet,money,fetch,words,search,report}.py` + `src/strata/stores/{allmat,bricomarche,obras360}.py`; `tests/test_*.py` | Pacote plano; sem `woo.py` genérico (Allmat e Bricomarché só partilham os cêntimos) |

## Stack Touched in Phase 1

- [ ] Project scaffold (uv init --package, pyproject com pytest, uv.lock)
- [ ] Routing — subcomando real `pesquisar` (e `modelo`) no `python -m strata`
- [ ] Database — N/A por decisão do projeto; leitura real = folha `.xlsx` do utilizador; escrita real = `modelo.xlsx`
- [ ] UI — terminal: secção por loja com o estado primeiro (D-01)
- [ ] Deployment — corrida local documentada: `uv run python -m strata modelo` + `uv run python -m strata pesquisar modelo.xlsx` contra a Allmat real

## Out of Scope (Deferred to Later Slices)

- Obramat e cadeia de recurso JSON-LD → browser → IA (Phase 2)
- Classificação exato/parecido e uso de Família/Tamanho/Referência na pesquisa (Phase 3)
- Custo total para a quantidade pedida, escalões aplicados, folha do utilizador preenchida (Phase 4)
- App NiceGUI, exportação Excel/PDF, progresso em tempo real (Phase 5)
- Descoberta de outras lojas (Phase 6)
- Gravar resultados em CSV/JSON para o utilizador (D-04)

## Subsequent Slice Plan

- Phase 2: Obramat e cadeia de recurso — novo módulo em `stores/` + degraus de recurso no `Fetcher`
- Phase 3: classificação exato/parecido sobre as `Offer` existentes
- Phase 4: custo total por item e folha original preenchida numa cópia (mapeamento por nome de cabeçalho, D-08)
- Phase 5: UI NiceGUI por cima de `search.run` e `models`
- Phase 6: lojas descobertas como mais um tipo de adaptador
