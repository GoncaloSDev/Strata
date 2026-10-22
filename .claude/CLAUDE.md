<!-- GSD:project-start source:PROJECT.md -->

## Project

**Strata**

Ferramenta pessoal, para usar no PC, que recebe uma lista de compras de obra (sobretudo uma folha Excel com produto, família, tamanho, unidade e quantidade) e procura cada produto em lojas online portuguesas para encontrar o fornecedor mais barato. Os preços são normalizados com IVA (23%) e por unidade, e o custo é calculado para a quantidade pedida (ex.: uma palete de 50 pode sair mais barata do que 30 avulsas). Serve materiais de construção, bricolage e também mobília, sem categorias fixas no código.

**Core Value:** Para cada produto da lista, mostrar o custo total mais baixo real (com IVA, para a quantidade pedida) entre as lojas portuguesas, com link para comprar: igual ou mais barato do que uma pesquisa feita à mão, e em minutos em vez de horas.

### Constraints

- **Plataforma**: PC — o utilizador prepara as compras em casa/escritório
- **Orçamento**: aceita pagar APIs de pesquisa e de IA, com preferência por opções baratas — ferramenta pessoal
- **Latência**: preços na hora; uma lista de ~10 produtos deve resolver-se em minutos — critério de sucesso
- **Fiscal**: IVA 23% (Portugal continental), preços em EUR — mercado-alvo
- **Mercado**: só lojas online que vendem em Portugal — âmbito do produto
- **Acesso às lojas**: volume baixo, respeitar o ritmo de cada site, nunca omitir falhas em silêncio — evitar bloqueios e resultados enganadores

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

## Resposta curta

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Python | 3.13 (3.13.2 já instalado) | Linguagem de toda a app | O ecossistema de scraping mais forte (curl_cffi, Playwright, selectolax), SDK oficial Anthropic, um só processo. Já está no PC. Não subir para 3.15: algumas rodas binárias (selectolax `<3.16`, etc.) chegam tarde a versões novas. | HIGH |
| uv | 0.12.6 (instalado) | Ambiente virtual, dependências, `uv run` | Um comando cria venv + lock; dispensa pip/venv/poetry. Evita o atalho `python3` da Microsoft Store. | HIGH |
| NiceGUI | 3.18.0 | Interface: lista de compras, progresso por loja, tabelas de resultados, botões de exportação | UI em Python puro sobre FastAPI, **assíncrona por natureza**: um `async` handler lança as pesquisas e vai atualizando a tabela à medida que cada loja responde, sem escrever JS nem SSE à mão. Tem tabelas (Quasar), aceita classes Tailwind (encaixa no design system do `ui-ux-pro-max`) e, se um dia quiser janela própria, `ui.run(native=True)` usa pywebview. | MEDIUM-HIGH |
| curl_cffi | 0.16.3 | Cliente HTTP único (lojas, APIs internas, Serper, Jev) | Imita a impressão digital TLS/HTTP2 do Chrome. **Teste de hoje:** `curl` normal → `403 Server: DataDome` na obramat.pt; `curl_cffi` com `impersonate="chrome"` → `200` com JSON-LD. Tem `AsyncSession` para pedidos em paralelo. Um cliente só = um sítio para timeouts, cabeçalhos e ritmo por loja. | HIGH |
| selectolax | 1.0.2 | Parsing de HTML (CSS selectors) e recolha dos blocos `<script type="application/ld+json">` | Motor Lexbor em C, muito mais rápido que BeautifulSoup e sem dependências pesadas. O leitor JSON-LD é ~10 linhas: selecionar os `script[type="application/ld+json"]`, `json.loads`, procurar `@type: Product`/`Offer`. | HIGH |
| Playwright (Python) | 1.64.1 | Recurso para sites com JavaScript ou bloqueio; exportação PDF | Só entra quando curl_cffi falha (escada definida no PROJECT.md). Usar `channel="chrome"` (o Chrome instalado) em vez do Chromium descarregado: menos 150 MB e menos detetável. O mesmo Playwright gera o PDF com `page.pdf()` a partir do HTML dos resultados, por isso o PDF não custa dependência nova. | HIGH |
| anthropic (SDK oficial) | 2.1.0 | Chamar Claude Haiku 5.5 | `client.messages.parse(model=..., output_format=ModeloPydantic)` devolve `response.parsed_output` já validado contra o esquema. Retentativas (429/5xx) incluídas no SDK. | HIGH (SDK) / MEDIUM (forma exata da API na 2.x, confirmar no arranque) |
| Claude Haiku 5.5 (`claude-haiku-5-5`) | modelo atual | Extrair especificações do título (espessura, medidas, unidade, qtd/pack, IVA incluído?) e classificar exato/parecido/outro | $0,10 / $0,50 por milhão de tokens (entrada/saída, até 100K tokens). Faz extração com valores livres (números, unidades), coisa que o Jev não faz. Uma lista de 10 produtos × ~60 anúncios ≈ 60K tokens de entrada → **cerca de 2 cêntimos por lista**. Para latência: `effort: "low"` e, se preciso, `thinking: {type: "disabled"}` (permitido no Haiku 5.5 com effort ≤ high). | HIGH (preço e ID vêm da documentação Anthropic de 2026-10-06) |
| Serper.dev | API (sem versão) | Descobrir lojas novas: `POST https://google.serper.dev/search` e `/shopping` com `gl: "pt"`, `hl: "pt-pt"` | ~$1,00 por 1.000 pesquisas no pacote mais pequeno ($50 = 50.000 créditos), até ~$0,30/1k em volume; 2.500 pesquisas grátis sem cartão. Uma chave serve a pesquisa normal (URLs diretos de páginas de produto) e o Shopping (nome da loja + preço). Para uso pessoal (~10–40 pesquisas por lista) o crédito grátis dura meses. | MEDIUM (preço e expiração dos créditos vêm de fontes secundárias; confirmar custo do `/shopping` na conta) |
| XlsxWriter | 3.3.0 | Exportar Excel | Só precisamos de escrever (nunca ler) `.xlsx`: XlsxWriter é puro Python, sem dependências, mantido ativamente (lançamento recente), com formatos de moeda, hiperligações e larguras de coluna. | HIGH |
| pytest | 9.1.1 | Testes | Padrão de facto. Testes de parsers sobre ficheiros gravados, sem rede. | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| pydantic | 2.14.1 | Esquemas para a saída estruturada do Haiku (`Specs`, `Match`) e para os dados normalizados de anúncio | Desde o início: o SDK Anthropic usa-o em `messages.parse`. Já vem como dependência do NiceGUI/FastAPI. | HIGH |
| Jev (TypeSafe AI) via Vercel AI Gateway | modelo `typesafe-ai/jev`, fixar versão (ex.: `jev-1.13.0`) | Decisão calibrada "este anúncio é o mesmo tipo de produto?" e "exato / parecido / outro" com probabilidade | **Só depois de um spike** com ~50 anúncios portugueses rotulados à mão, comparando com o Haiku. Chamar com `curl_cffi` (POST JSON) — não precisa de SDK. Ver secção Jev abaixo. | MEDIUM (API e preço verificados na documentação Vercel; qualidade em português não verificada) |
| patchright | 1.64.1 | Playwright com correções anti-deteção (substituto direto) | Só se uma loja bloquear o Playwright normal mesmo com `channel="chrome"`. Mesma API: troca-se o import. | MEDIUM |
| rapidfuzz | 3.14.6 | Semelhança de texto rápida (ex.: cortar anúncios irrelevantes antes de os mandar à IA) | Só se o volume de anúncios por produto tornar a chamada à IA lenta ou cara. Não usar no v1. | MEDIUM |
| SerpApi (Google Shopping / Immersive Product) | API | Alternativa ao Serper com respostas mais ricas (`extracted_price`, lojas por produto via `more_stores=true`) | Se o Serper não devolver lojas portuguesas suficientes. Plano grátis: 250 pesquisas/mês; Starter $25/mês por 1.000 (= $25/1k); Developer $75 por 5.000 (= $15/1k). 15–25× mais caro que o Serper. | HIGH (preços lidos em serpapi.com/pricing hoje) |
| Brave Search API | API | Pesquisa web orgânica com índice independente do Google | Só como plano B se o Serper falhar. $5 por 1.000 pedidos com $5 de crédito mensal automático (~1.000 grátis/mês), exige cartão. **Não tem vertical de shopping com preços.** | MEDIUM |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | `uv init`, `uv add`, `uv run` | `uv run python -m strata` sempre; nunca `python3` neste Windows. |
| `playwright install` | Só se não usar o Chrome instalado | Com `channel="chrome"` não é preciso descarregar browsers. |
| Variáveis de ambiente | Chaves (`ANTHROPIC_API_KEY`, `SERPER_API_KEY`, `AI_GATEWAY_API_KEY`) | Definir com `setx` no Windows ou num `.env` lido à mão; não acrescentar python-dotenv só para isto. Nunca guardar chaves no repositório. |
| ruff | Lint + formatação | Opcional; uma ferramenta em vez de flake8+black+isort. |

## Installation

# Projeto

# Core

# Dev

# Só quando for preciso (não no v1)

# uv add patchright rapidfuzz

## Jev (TypeSafe AI): avaliação

| Ponto | Facto | Fonte / confiança |
|-------|-------|-------------------|
| O que é | Modelo "System One": recebe um `state` (texto/JSON) e perguntas tipadas; devolve **choice** (1–255 opções, com probabilidade por opção e `confidence`), **score** (2–10 níveis) ou **noul/predicate** (probabilidade de "sim"). Não gera texto (`max output tokens: 0`). | Vercel docs — HIGH |
| Preço | $0,042 por milhão de tokens de entrada; saída grátis. Sem plano grátis. | Página do modelo na Vercel + várias fontes — HIGH |
| Contexto | 32K tokens (estado + pergunta mais longa); 64K por pedido. Só texto (imagens → 400). | Vercel / Zuplo — HIGH |
| Latência | Fabricante: 70–500 ms; utilizadores: mediana ~76 ms. | InfoQ — MEDIUM (dados do fabricante) |
| Acesso | A TypeSafe **parou novos registos diretos no fim de setembro de 2026**. Pela Vercel AI Gateway funciona sem lista de espera. | flaviocopes.com, OpenTweet — MEDIUM |
| Chamada em Python | `POST https://ai-gateway.vercel.sh/typesafe/v1/systemone` com `Authorization: Bearer $AI_GATEWAY_API_KEY` e corpo `{"model": "typesafe-ai/jev", "state": ..., "questions": {...}}`. Alternativa neutra: `POST https://ai-gateway.vercel.sh/v1/decisions` (formato OpenAI Decisions). SDK oficial Python `typesafe-sdk` 0.7.5 existe, mas não é preciso. | Vercel docs — HIGH |
| Fallback | O gateway pode reenviar automaticamente para outro modelo quando `confidence` fica abaixo de um limiar (`providerOptions.gateway.models[...].when.confidenceBelow`). | Vercel docs — HIGH |
| Limitações declaradas | A própria TypeSafe documenta que contar, aritmética e comparar datas não são fiáveis, e que a precisão cai com estado grande e ruidoso: "manter a matemática no código". Pode devolver um valor válido mas errado. Suporte a português **não documentado**. | InfoQ (página "jaggedness" jev-1.13) — MEDIUM |

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| NiceGUI | FastAPI + Jinja2 + htmx (SSE) | Se quiser controlo total do HTML/CSS. Custa mais código: rotas, templates e canal SSE para o progresso. |
| NiceGUI | Streamlit 1.66 | Protótipo de uma tarde. Modelo de "re-executar o script inteiro" luta contra tarefas longas assíncronas com progresso por loja, e arrasta pandas/pyarrow (~150 MB). |
| NiceGUI (browser local) | App desktop (Tauri/Electron/pywebview) | Nunca para v1: o browser em `localhost` já é a janela. Se quiser ícone e janela própria, `ui.run(native=True)` do NiceGUI chega. |
| App web local | Só CLI | A CLI fica útil como arnês interno (`uv run python -m strata "OSB 12mm" 30`) para gravar fixtures e depurar, mas rever tabelas com links e exatos/parecidos pede ecrã. |
| Python | TypeScript/Node (Crawlee, AI SDK com `experimental_decide`) | Se o Jev passasse a ser central: o AI SDK tem `decide()` nativo. Mas curl_cffi (TLS do Chrome) não tem equivalente tão maduro em Node, e o Python já está instalado. |
| curl_cffi | httpx 0.28.1 | httpx tem a melhor ecologia de testes (respx), mas é detetado por DataDome/Cloudflare pela impressão TLS. Não vale ter dois clientes. |
| selectolax + `json.loads` | extruct 0.18.0 | Se precisar de microdata/RDFa além de JSON-LD em muitas lojas. extruct puxa lxml, rdflib, w3lib e o último lançamento é de nov. 2024. Para JSON-LD chega o código próprio. |
| Serper.dev | SerpApi | Quando precisar da lista de lojas por produto do Google Shopping (`more_stores=true`) ou de campos já normalizados. 15–25× mais caro. |
| Claude Haiku 5.5 | Claude Haiku 4.5 | Nunca: 10× mais caro ($1/$5) e mais antigo. |
| Claude Haiku 5.5 | Jev | Ver secção Jev: só para a pergunta "mesmo tipo de produto", depois de um spike. |
| Playwright `page.pdf()` | WeasyPrint 70.0 / ReportLab 5.1 | WeasyPrint exige GTK/Pango no Windows (instalação penosa). ReportLab obriga a desenhar o PDF à mão. O Playwright já está instalado e imprime o mesmo HTML dos resultados. Alternativa a zero código: CSS `@media print` e "Imprimir → Guardar como PDF" no browser. |
| XlsxWriter | openpyxl 3.1.5 | Se um dia for preciso **ler** ou editar um `.xlsx` (ex.: importar a lista de compras de um Excel). Último lançamento em 2024. |
| Fixtures em ficheiro | vcrpy 8.3 / pytest-recording 0.14 | vcrpy grava cassetes de httpx/requests, mas não intercepta curl_cffi. Separar "buscar" de "interpretar" torna a gravação HTTP desnecessária. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Google Custom Search JSON API | Fechada a novos clientes (novos projetos levam 403) e **desligada para todos a 1 de janeiro de 2027**. A substituta da Google (Vertex AI Search) só cobre até 50 domínios. | Serper.dev (ou SerpApi) |
| `requests` / `httpx` / `urllib` simples para as lojas | Impressão TLS de Python → 403 imediato em DataDome (Obramat confirmada hoje) e Cloudflare Bot Management. | curl_cffi com `impersonate="chrome"` |
| Scrapy | Framework de crawling em massa (Twisted, pipelines, spiders). Aqui são poucas dezenas de pedidos por pesquisa, iniciados pela UI. | `asyncio` + `curl_cffi.AsyncSession` |
| Selenium / undetected-chromedriver | Mais lento e frágil que o Playwright; o undetected-chromedriver vive atrás das versões do Chrome. | Playwright (→ patchright se preciso) |
| Scrapling 0.5, Camoufox | Frameworks/browsers anti-deteção completos: muito peso para 4 lojas fixas a ritmo baixo. | curl_cffi → Playwright → patchright, por esta ordem |
| Serviços de proxies residenciais / "unblocker APIs" (Bright Data, ScraperAPI, Zyte) | Pagos, desnecessários para uso pessoal a partir de um IP doméstico, e mascaram bloqueios que o PROJECT.md quer ver assinalados. | Ritmo respeitador por loja + falha visível |
| LLM para ler preços quando há JSON/JSON-LD | Mais lento, mais caro e pode inventar um número. Preço é dinheiro: vem de campo estruturado sempre que existir. | API interna da loja → JSON-LD → HTML → IA (último recurso, marcado como tal) |
| Base de dados (SQLite, Postgres) no v1 | O PROJECT.md exclui histórico e base de preços. Lojas fixas e lojas sugeridas cabem num ficheiro JSON. | `stores.json` + objetos em memória |
| pandas | Só para escrever uma folha e uma tabela; 30+ MB por nada. | listas de dicts + XlsxWriter |
| pint / bibliotecas de unidades | As unidades do domínio são poucas (mm, cm, m, m², un, pack, palete). | Função de normalização própria com testes |
| tenacity | A "retentativa" útil aqui é a escada de recurso (HTTP → browser → IA), não repetir o mesmo pedido. O SDK Anthropic já tem retentativas. | Escada explícita por loja |

## Stack Patterns by Variant

- `curl_cffi` direto ao endpoint JSON; zero parsing de HTML.
- Porque: dados estruturados, rápidos, estáveis. Teste de hoje: `https://www.bricomarche.pt/wp-json/wc/store/v1/products?search=osb` devolve JSON com nome, SKU, permalink e descrição ("PLACA OSB 12 MM", "2500x125x12 mm"). allmat.pt também é WooCommerce (atrás de Cloudflare, que deixou passar).
- `curl_cffi` com `impersonate="chrome"` + JSON-LD da página de produto.
- Porque: passou o DataDome da obramat.pt hoje (200 com JSON-LD na página inicial). A URL de pesquisa ainda está por descobrir (`/pesquisa?q=` deu 404).
- Playwright com `channel="chrome"`, contexto persistente (cookies guardados entre sessões), intercetar as respostas XHR/JSON da pesquisa em vez de ler o DOM.
- Porque: o JSON por trás da página é mais estável que o HTML renderizado.
- Serper `/search` (e `/shopping`) com `gl=pt` → URL da página de produto → leitor genérico de JSON-LD → se não houver, IA sobre o texto da página, marcado como "lido por IA".

## Testing Approach

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Python 3.13 | nicegui 3.18 (`<4,>=3.10`), curl_cffi 0.16 (`>=3.10`), playwright 1.64 (`>=3.10`), anthropic 2.1 (`>=3.10`), selectolax 1.0.2 (`<3.16,>=3.9`) | Tudo verificado no PyPI hoje. rapidfuzz 3.14 pede `>=3.11`; pint pediria `>=3.12`. |
| playwright 1.64.1 | patchright 1.64.1 | Versões alinhadas; patchright é substituto direto. |
| anthropic 2.1.0 | `claude-haiku-5-5` | A documentação de saída estruturada (`messages.parse(..., output_format=Model)`) foi escrita para a série 1.x; o 2.0 saiu depois. Confirmar a assinatura no primeiro uso. |
| selectolax 1.0.x | — | Primeira série 1.0 (antes 0.3/0.4): usar `LexborHTMLParser`; se exemplos antigos usarem `HTMLParser` (Modest), confirmar que ainda existe. |
| Jev | Vercel AI Gateway | Fixar a versão do modelo (`jev-1.13.0`), não usar `jev-latest`/`jev-preview`. Formato de resposta ainda descrito como "não estável" por alguns gateways. |

## Sources

- PyPI JSON API (`pypi.org/pypi/<pkg>/json`), consultado 2026-10-22 — versões e `requires_python` de todas as bibliotecas da tabela — HIGH
- Teste direto com curl e curl_cffi a obramat.pt, allmat.pt, bricomarche.pt, obras360.pt (2026-10-22) — DataDome na Obramat, WooCommerce + Cloudflare na Allmat, WooCommerce Store API aberta no Bricomarché — HIGH. Nota: o domínio da "Obra360" parece ser **obras360.pt** (Sotecnisol, S.A.); `obra360.pt` não tem loja. Plataforma da obras360.pt por identificar.
- Documentação Claude API (skill `claude-api`, cache 2026-10-06) — `claude-haiku-5-5`, $0,10/$0,50 por MTok, `messages.parse` com `output_format` — HIGH
- [Vercel AI Gateway — OpenAI-Compatible Decisions API](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions) — endpoint `/v1/decisions`, tipos de pergunta, `typesafe-ai/jev` só texto — HIGH
- [Vercel AI Gateway — TypeSafe API](https://vercel.com/docs/ai-gateway/sdks-and-apis/typesafe) — `/typesafe/v1/systemone`, exemplo Python com HTTP simples, decision fallbacks — HIGH
- [Vercel AI Gateway — modelo Jev](https://vercel.com/ai-gateway/models/jev) — $0,042/1M entrada, 32K contexto, 0 tokens de saída — HIGH
- [InfoQ — TypeSafe AI Jev released](https://infoq.com/news/2026/10/typesafe-ai-jev-released) — lançamento 2026-09-15, latência, limitações ("jaggedness"), críticas — MEDIUM
- [How to use Jev with Python (flaviocopes)](https://flaviocopes.com/jev-python/) — `typesafe-sdk`, limites 80 req/s, pausa de registos diretos — MEDIUM
- [Zuplo — Using Jev](https://zuplo.com/docs/ai-gateway/jev.md) — formato HTTP bruto, só texto — MEDIUM
- [Vercel — Anthropic Messages API](https://vercel.com/docs/ai-gateway/sdks-and-apis/anthropic-messages-api) — Claude pelo gateway com `base_url` — MEDIUM
- [SerpApi Pricing](https://serpapi.com/pricing) — planos lidos hoje (Free 250/mês, Starter $25/1.000, Developer $75/5.000) — HIGH
- [SerpApi Google Shopping release notes](https://serpapi.com/google-shopping-api/release-notes) — remoção dos URLs de produto (nov. 2025), links para Immersive Product — MEDIUM
- [Serper pricing explained (apiserpent)](https://apiserpent.com/blog/serper-pricing-credits-explained), [coldiq](https://coldiq.com/blog/serper-pricing), [serper.dev](https://serper.dev/) — $50/50k a $3.750/12,5M, 2.500 grátis, créditos expiram em 6 meses (fontes discordam) — MEDIUM
- [Brave — alternativas antes do fim da API Google](https://brave.com/learn/google-api-shutdown/), [Brave API dashboard pricing](https://api-dashboard.search.brave.com/documentation/pricing), [implicator.ai](https://www.implicator.ai/brave-drops-free-search-api-tier-puts-all-developers-on-metered-billing/) — $5/1k + $5 de crédito mensal — MEDIUM
- [Bright Data — Google Search API](https://brightdata.com/blog/web-data/google-search-api), [dev.to — CSE morre em 2027](https://dev.to/booyaka101/google-kills-the-custom-search-json-api-on-2027-01-01-here-is-a-self-hosted-drop-in-3nk0), [Wikimedia Phabricator T425144](https://phabricator.wikimedia.org/T425144) — Custom Search JSON API fechada a novos clientes, fim a 2027-01-01 — HIGH (várias fontes concordam)

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-fast` for a trivial task inline, with no subagents and no PLAN.md
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
