# Phase 2: Obramat e cadeia de recurso - Context

**Gathered:** 2026-10-30
**Status:** Ready for planning

<domain>
## Phase Boundary

A linha de comandos da fase 1 passa a pesquisar as 4 lojas fixas: entra a Obramat (`obramat.pt`, pesquisa direta `/search?q=`, um pedido de cada vez). Quando o método principal de qualquer loja fixa falha, a app tenta JSON-LD, depois browser automático, depois IA, por esta ordem, e cada oferta mostra o método que a produziu. Uma folha de 10 itens fica resolvida nas 4 lojas em menos de 5 minutos, com o estado das 4 lojas por item, e a verificação das lojas (STORE-07) cobre as 4.

Requisitos: STORE-04, STORE-06, LIST-03.

Fora desta fase: classificação exato/parecido, especificações e Família/Tamanho/Referência (Phase 3); aplicar escalões e embalagens ao custo total (Phase 4); UI e exportação (Phase 5); descoberta de lojas (Phase 6).

</domain>

<decisions>
## Implementation Decisions

As decisões D-01 a D-16 da fase 1 (`.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-CONTEXT.md`) continuam em vigor; aqui chamam-se "fase 1 D-xx". As desta fase numeram-se de novo.

### Preço da Obramat por loja física
- **D-01:** A oferta da Obramat é a da loja física (armazém) mais barata **com stock**, com o nome dessa loja em `Offer.location`; se nenhuma tiver stock, a mais barata com o stock dela; uma loja mais barata sem stock fica na nota "mais barata sem stock: X em Y". É a mesma regra da Bricomarché (G-01-3, `01-10`). O `contextCode=000` é o preço nacional, não o de uma loja.
- **D-02:** Entram todas as lojas Obramat do país, sem lista configurada pelo utilizador, como na Bricomarché.
- **D-03:** Se a pesquisa da fase mostrar que o preço por loja física só se obtém com muitos pedidos por produto ou só pelo browser, **o planeamento para e pergunta de novo ao utilizador**, com os números medidos (pedidos por item, segundos, sinais do DataDome). Não escolher sozinho entre o preço nacional e o preço por loja.
- **D-04:** Os escalões "Melhor preço por quantidade" da Obramat, se a pesquisa os encontrar, vão para `Offer.tiers` e aparecem na oferta, como os da Obras 360 (fase 1 D-16). Aplicá-los ao custo total é da Phase 4. O preço guardado é com IVA (`unitprice_ati`); quando a página traz os dois preços, confirmar que `com IVA / sem IVA ≈ 1,23` e tratar como erro se não bater (PITFALLS §Pitfall 1).

### Bloqueio e browser
- **D-05:** O degrau browser usa o **Chrome dedicado do Claude** (perfil `%USERPROFILE%\.claude-chrome`, porta 9222, `.claude\claude-chrome.cmd`), **com janela visível** e os cookies guardados no perfil. Nunca headless, nunca o Chrome do utilizador.
- **D-06:** Se o Chrome dedicado não estiver a correr quando o browser é preciso, a app abre-o e, no fim da execução, fecha-o se foi ela a abri-lo. Se já estava aberto, fica aberto.
- **D-07:** Ao primeiro **CAPTCHA** na Obramat, a loja fica "abrir à mão" nesse item e em **todos os itens seguintes da execução**, com o link da pesquisa na loja (ex.: `https://www.obramat.pt/search?q=<produto>`). Não se volta a pedir nada à Obramat nessa execução; as outras 3 lojas continuam. A app nunca resolve nem espera por um CAPTCHA. O mesmo vale para um CAPTCHA noutra loja fixa.
- **D-08:** Depois de um bloqueio sem CAPTCHA (ex.: 403 do DataDome) que o browser resolve, essa loja **fica no browser até ao fim da execução**; não volta a tentar o pedido simples nos itens seguintes.

### Preços lidos por IA (último degrau)
- **D-09:** Uma oferta lida por IA aparece com a marca "lido por IA", mas fica **sempre depois** das ofertas lidas de dados estruturados (API, JSON-LD, HTML do browser), mesmo que seja mais barata. Nunca é a primeira da loja.
- **D-10:** No máximo **1 chamada de IA por (item, loja)**, com o texto da página cortado. Sem contador em euros.
- **D-11:** A IA lê a página de pesquisa da loja e devolve **até 5 ofertas** (título, preço, link de cada, tirados da página). Passam pelo mesmo filtro de título que as outras (fase 1 D-15) e o IVA segue a regra conhecida da loja fixa.
- **D-12:** Motor da IA: se houver `ANTHROPIC_API_KEY`, usa a API (Claude Haiku 5.5, saída estruturada); se não houver, usa o **Claude Code como subprocesso** (`claude -p --model haiku --output-format json --json-schema …`), que corre com a conta Claude Pro do utilizador. Se nenhum estiver disponível, o degrau salta e o motivo fica visível (ex.: "IA não configurada"). **Nunca** reaproveitar o token OAuth da conta Pro fora do Claude Code (o que fazem agentes como o Hermes): vai contra os termos da Anthropic. — **Reversibility:** reversible — o motor está atrás de uma função; trocar ou retirar o `claude -p` é local.

### Quando escalar a cadeia
- **D-13:** A cadeia (principal → JSON-LD → browser → IA) corre para **as 4 lojas fixas**, não só para a Obramat.
- **D-14:** Escalam: `bloqueada`, `erro` e `tempo esgotado`. `sem resultados` é uma resposta válida e **não** escala (a Allmat não vende OSB). Zero ofertas mostradas pelo filtro de título também não escala.
- **D-15:** Os degraus de um (item, loja) **partilham o prazo de 90 s** que já existe (`DEADLINE_S`); o recurso usa o que sobrar. Se o prazo acabar a meio da cadeia, o estado diz até onde chegou (ex.: "tempo esgotado depois do browser").
- **D-16:** Cada oferta mostra o método que a produziu (API / JSON-LD / browser / IA). Se todos os degraus falharem, a loja aparece falhada com o motivo de cada degrau tentado.
- **D-17:** Uma opção de desenvolvimento no comando força a falha do método principal de uma loja (ex.: `--sem-principal obramat`), para ver o recurso ao vivo, como o `--record` da fase 1. Os testes com fixtures provam o mesmo sem rede.

### Claude's Discretion
- Quantos produtos da Obramat são vistos loja física a loja física (corte K): o utilizador deixou para depois de medir tempo e bloqueios ao vivo na pesquisa da fase. Ponto de partida: o mesmo padrão K da Bricomarché.
- Ritmo da Obramat (intervalo entre pedidos, com jitter) dentro de "um pedido de cada vez"; entrada em `LIMITS` do `fetch.py`.
- Como detetar CAPTCHA vs bloqueio simples (cabeçalhos `x-datadome`, `captcha-delivery`, conteúdo da página).
- Tamanho do corte de texto para a IA e o esquema de saída estruturada.
- Nome exato da opção de D-17 e o canário da Obramat na verificação das lojas.
- Como o browser se liga ao Chrome dedicado (CDP na porta 9222 via Playwright `connect_over_cdp`, ou outro) e como corre os mesmos parsers sobre o HTML que recebe.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Âmbito e requisitos
- `.planning/ROADMAP.md` §Phase 2 — objetivo, os 3 critérios de sucesso e o research flag (tolerância do DataDome numa lista de 10 itens, tabela de escalões, se `contextCode=000` dá o preço certo)
- `.planning/REQUIREMENTS.md` — STORE-04, STORE-06, LIST-03; Out of Scope (sem proxies, resolvedores de CAPTCHA nem sessões autenticadas; ao primeiro CAPTCHA a loja fica "abrir à mão")
- `.planning/PROJECT.md` §Key Decisions — Obramat pela pesquisa direta `/search?q=` apesar do robots.txt; Bricomarché com a loja mais barata com stock (G-01-3)
- `.planning/STATE.md` §Blockers/Concerns — nota curta de âmbito legal antes de começar; DataDome numa lista de 10 itens por testar; Bricomarché ~12 s por página pesa nos 5 minutos

### Fase 1 (decisões e padrões em vigor)
- `.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-CONTEXT.md` — D-01 a D-16 (saída no terminal, filtro de título D-15 com a emenda G-01-5, Obras 360 D-16)
- `.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-10-SUMMARY.md` — regra da loja física mais barata com stock (G-01-3), a copiar para a Obramat (D-01)
- `.planning/phases/01-folha-excel-e-pre-os-da-allmat-e-bricomarch/01-UAT.md` — casos reais da UAT (cola "para OSB", stock por loja)

### Obramat
- `.planning/research/ARCHITECTURE.md` §Per-Store Extraction Feasibility (linha Obramat) — `/search?q=` SSR, `<li data-reflm>` com `script.dataTms` (`unitprice_ati`, `unitprice_tf`, `available_deliveries[].stock`), JSON-LD na página de produto com IVA, `contextCode=000`, DataDome
- `.planning/research/ARCHITECTURE.md` §Pattern 2 (cadeia de recurso com proveniência visível), §Pattern 5 (limites por host), Anti-Pattern 3 (estados separados), §Scaling (gargalo Obramat), linhas 270 e 288
- `.planning/research/PITFALLS.md` §Pitfall 1 (IVA, rácio 1,23), §Pitfall 3 (preço por loja física), §Pitfall 4 (falhas silenciosas, deteção de desafio pelo conteúdo), §Pitfall 8 (anti-bot, Chrome dedicado a ritmo humano, parar ao primeiro CAPTCHA), §Pitfall 11 (custo da IA, uma tentativa por via), §Pitfall 13 (robots.txt, DL 122/2000, Lei 109/2009)
- `.planning/research/FEATURES.md` T3, D1 — escalões "melhor preço por quantidade" da Obramat ES

### Stack e ambiente
- `.planning/research/STACK.md` — curl_cffi `impersonate="chrome"`, Playwright com `channel="chrome"` (→ patchright se preciso), SDK `anthropic` com `messages.parse`, Claude Haiku 5.5
- `CLAUDE.md` (raiz) — Chrome dedicado: perfil `%USERPROFILE%\.claude-chrome`, porta 9222, `.claude\claude-chrome.cmd`; `uv run python -m strata`; `python`, nunca `python3`
- `.claude/claude-chrome.cmd` — como o Chrome dedicado é lançado (D-06)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/strata/fetch.py` — `Fetcher` (único cliente HTTP, `LIMITS` por host, `--record`), exceções `StoreBlocked` / `StoreError` / `StoreTimeout`, marcadores `CHALLENGE` (já inclui "datadome" e "captcha"). A Obramat precisa de uma entrada em `LIMITS` com 1 pedido em simultâneo.
- `src/strata/search.py` — `search_store` (prazo `DEADLINE_S = 90`, pesquisa alargada D-14, o único sítio onde uma falha vira estado), `STORES`, `run` (um item de cada vez, lojas em paralelo), `CANARIES` + `_problem` + `verificar` (STORE-07). A cadeia de recurso encaixa em `search_store`, à volta de `store.search`.
- `src/strata/models.py` — `Offer` (já tem `location`, `tiers`, `note`, `vat_origin`/`vat_evidence`; falta o método que produziu a oferta), `StoreResult` com `Status`.
- `src/strata/stores/bricomarche.py` — padrão da loja física mais barata com stock (`cheapest`, `has_stock`, `parent_key`) a reproduzir na Obramat.
- `src/strata/words.py` — `title_matches` e `broadened` (filtro D-15), a aplicar também às ofertas lidas por IA.
- `src/strata/money.py` — `in_unit`, `fmt_eur`, `Decimal` para dinheiro.

### Established Patterns
- Cada loja é um módulo com `NAME` e `async search(query, fetch, rank=None) -> Found`; parsers puros testados com fixtures gravadas (`tests/conftest.py`, `FakeFetcher`).
- Nenhuma falha some em silêncio: estado + `detail` por loja, contagens do que fica escondido.
- Comentários `shortcut:` para limites conhecidos.

### Integration Points
- `search.STORES` ganha `obramat`; `CANARIES` ganha um termo da Obramat.
- `__main__.py` ganha a opção de D-17 nos subcomandos `pesquisar` e `verificar`.
- `report.py` mostra o método por oferta, a marca "lido por IA" e o estado "abrir à mão" com link.
- Estado da execução partilhado entre itens (D-07 e D-08: Obramat parada ou presa ao browser até ao fim) — hoje o `Fetcher.cache` já guarda valores válidos durante uma execução.

</code_context>

<specifics>
## Specific Ideas

- O utilizador perguntou se o degrau IA podia usar a conta Claude Pro em vez da API paga. Resposta acordada: sim, através do Claude Code (`claude -p`, versão 2.1.308 instalada, com `--json-schema`), nunca com o token OAuth noutra ferramenta (D-12). A mesma escolha para a classificação da Phase 3 fica por decidir lá: pesa mais no limite de 5 h do Pro e no tempo.
- "Abrir à mão" leva sempre o link pronto da pesquisa na loja, para o utilizador continuar sem escrever nada.
- Uma janela do Chrome a aparecer durante a pesquisa é aceitável (D-05).

</specifics>

<deferred>
## Deferred Ideas

- Usar o `claude -p` (conta Pro) também na extração de especificações e na classificação exato/parecido — decidir na Phase 3, com medição de tempo e de consumo do limite.

</deferred>

---

*Phase: 02-obramat-e-cadeia-de-recurso*
*Context gathered: 2026-10-30*
