# ConfereAí! — Sistema de Verificação de Notícias com IA

## Sumário
- [Visão geral](#visão-geral)
- [Arquitetura e fluxo de verificação](#arquitetura-e-fluxo-de-verificação)
- [Tecnologias e ferramentas](#tecnologias-e-ferramentas)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Configuração do ambiente](#configuração-do-ambiente)
  - [Backend (Flask)](#backend-flask)
  - [Frontend (React + Vite)](#frontend-react--vite)
- [Como executar](#como-executar)
  - [Subir a API](#subir-a-api)
  - [Rodar a interface web](#rodar-a-interface-web)
- [Uso da API](#uso-da-api)
- [Uso da interface web](#uso-da-interface-web)
- [Principais módulos do backend](#principais-módulos-do-backend)
- [Principais componentes do frontend](#principais-componentes-do-frontend)
- [Resolução de problemas e dicas](#resolução-de-problemas-e-dicas)

## Visão geral
O projeto **ConfereAí!** disponibiliza uma API Flask com recursos de NLP e busca semântica para verificar a veracidade de notícias e uma interface web em React para uso amigável. A API expõe endpoints REST, detalha o fluxo completo da checagem e fornece métricas de confiança, incluindo alerta para contradições encontradas nas fontes consultadas.

## Arquitetura e fluxo de verificação
O backend orquestra as etapas abaixo sempre que o endpoint `/api/verificar` recebe um conteúdo textual ou URL de notícia.

1. **Validação de entrada** — Garante que o corpo contenha `tipo` (`url` ou `texto`) e `conteudo`, além de respeitar limites mínimos/máximos definidos em `Config`.
2. **Extração de conteúdo** — Para URLs, baixa e interpreta a página antes de seguir; para texto puro, usa o texto enviado. A extração usa múltiplas estratégias de fallback (newspaper3k, trafilatura, AMP, readability, parser específico Globo e BeautifulSoup).
3. **Processamento NLP** — Limpa o texto, extrai entidades/palavras-chave e monta a consulta de busca usando spaCy e NLTK.
4. **Busca em fontes confiáveis** — Interroga portais configurados, com cache, diferentes estratégias e modo paralelo opcional.
5. **Filtros inteligentes** — Remove URLs com paywall, páginas genéricas ou sem correlação; replica a filtragem após o scraping.
6. **Scraping paralelo** — Extrai textos das URLs mantidas respeitando paywalls e reutilizando cache; há wrapper `scrape_noticias` que o app usa direto.
7. **Análise semântica & contradições** — Calcula similaridade via sentence-transformers, detecta padrões de desmentido, quantifica confirmações/parciais/menções e registra evidências de contradição.
8. **Cálculo de veracidade** — Converte a análise em percentual (10–95%), gera justificativa e nível de confiança, penalizando fortemente contradições.
9. **Resposta enriquecida** — Retorna resumo, fontes ranqueadas, estatísticas de NLP, detalhamento do score e metadados gerais.

## Tecnologias e ferramentas
### Backend (Python)
- Frameworks e utilitários: Flask, Flask-CORS, python-dotenv, logging com rotacionamento.
- Coleta de conteúdo: requests, newspaper3k, trafilatura, readability-lxml, BeautifulSoup, validators.
- NLP e IA: spaCy, NLTK, sentence-transformers, scikit-learn, torch, transformers, accelerate, sentencepiece.
- Busca e scraping: google-search-results (SerpAPI), googlesearch-python, multithreading com ThreadPoolExecutor, caches em disco.
- Configuração centralizada: classe `Config` com fontes confiáveis, limites, modelos e parâmetros de scoring.

### Frontend (JavaScript)
- React 18 com Vite como bundler/dev server e React Icons para ícones.
- Hooks personalizados, componentes reutilizáveis e estilização CSS modular para UX informativa.

## Estrutura de pastas
```
news-verifier/
├── app.py               # API Flask principal
├── config.py            # Parâmetros globais do sistema
├── modules/             # Núcleo de IA, busca, scraping e scoring
├── frontend/            # Aplicação React (Vite)
├── requirements.txt     # Dependências Python
└── tests/               # Scripts utilitários e diagnósticos
```

## Configuração do ambiente
### Backend (Flask)
1. Crie e ative um ambiente virtual Python 3.10+.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Garanta que o modelo spaCy pt_core_news_lg esteja disponível. Caso a instalação via `requirements.txt` falhe, execute:
   ```bash
   python -m spacy download pt_core_news_lg
   ```
4. Configure variáveis opcionais em `.env` (porta, host, chaves SerpAPI, etc.) seguindo os atributos da classe `Config`.

### Frontend (React + Vite)
1. Instale Node.js 18+.
2. Na pasta `frontend`, instale as dependências:
   ```bash
   npm install
   ```
   Os scripts `dev`, `build` e `preview` são fornecidos pelo Vite.

## Como executar
### Subir a API
1. Ative seu ambiente virtual.
2. (Opcional) Ajuste `FLASK_ENV`, `PORT` ou `HOST` conforme necessário.
3. Execute:
   ```bash
   python app.py
   ```
   A aplicação inicializa com CORS liberado, logging estruturado e informações de versão/endpoints no console.

### Rodar a interface web
1. Em outro terminal, acesse `frontend/`.
2. Execute o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```
3. Acesse o endereço indicado (por padrão `http://127.0.0.1:5173`). Certifique-se de que a API esteja disponível em `http://127.0.0.1:5000` ou ajuste `baseURL` em `frontend/src/services/api.js` caso utilize outra porta.

## Uso da API
- **Health check**: `GET /api/health` — retorna status, versão e módulos ativos.
- **Verificar notícia**: `POST /api/verificar`
  - Corpo:
    ```json
    {
      "tipo": "url" | "texto",
      "conteudo": "..."
    }
    ```
  - Erros retornam mensagens padronizadas (`codigo`, `erro`).
  - Sucesso retorna campos como `veracidade`, `nivel_confianca`, `justificativa`, `fontes_consultadas`, estatísticas de NLP e metadados (incluindo alerta de contradição).

## Uso da interface web
A aplicação React organiza a experiência em três blocos principais:
1. **Formulário de verificação** — Permite alternar entre URL e texto, valida tamanho mínimo (alinhado ao backend), mostra contagem de caracteres e botão de limpeza.
2. **Resultado** — Exibe o percentual de veracidade, justificativas, sinais adicionais, fontes consultadas com modal detalhado e nível de confiança colorido.
3. **Feedback em tempo real** — Enquanto a análise roda, um indicador animado explica cada estágio do processamento (extração, busca, análise semântica, detecção de contradições, etc.).

O hook `useNewsVerification` centraliza chamadas à API, estado de carregamento/erro e data da última requisição, reaproveitando a função `verifyNewsRequest` que constrói o payload adequado (`url`/`texto`) e normaliza a resposta antes de repassar para a UI.

## Principais módulos do backend
- **`modules/extractor.py`** — Classe `ContentExtractor` com seis estratégias de fallback para extrair texto estruturado de URLs; a função `extrair_conteudo` é usada diretamente pela API.
- **`modules/nlp_processor.py`** — Classe `NLPProcessor` carrega spaCy e stopwords, normaliza o texto, extrai entidades/palavras-chave e monta queries; `processar_texto` encapsula o uso padrão.
- **`modules/searcher.py`** — `buscar_noticias` e `buscar_noticias_paralelo` executam buscas em portais confiáveis, respeitando cache, prioridades de métodos e threads para paralelismo.
- **`modules/filters.py`** — `ContentFilter` remove URLs problemáticas e conteúdos desconexos; funções helper `filtrar_busca` e `filtrar_scraping` aplicam rapidamente os filtros dentro do fluxo do app.
- **`modules/scraper.py`** — `scrape_noticias_paralelo` lida com extração em larga escala, cuidando de paywalls, cache e agrupamento por fonte; `scrape_noticias` mantém a interface sequencial usada pelo endpoint.
- **`modules/semantic_analyzer.py`** — `analisar_semantica` gera embeddings, calcula similaridade, detecta contradições por padrões linguísticos e agrega estatísticas por fonte.
- **`modules/scorer.py`** — `VeracityScorer.calcular_veracidade` aplica pesos, penalidades e bônus para gerar o score final, justificativa e nível de confiança; penaliza severamente contradições.
- **`config.py`** — Consolida fontes confiáveis, limites de requisição/conteúdo, parâmetros de IA, mensagens padrão e ambientes (desenvolvimento, produção, teste).

## Principais componentes do frontend
- **`App.jsx`** — Monta a página com cabeçalho, formulário, painel de resultados e seção "Como utilizar" que instrui o usuário passo a passo.
- **`VerificationForm.jsx`** — Controla modo URL/texto, validações, mensagens auxiliares, botões e chama `onSubmit` com payload normalizado.
- **`VerificationResult.jsx`** — Renderiza estado inicial/erro, painel de resultados, lista de sinais, grade de fontes e modal detalhado por fonte.
- **`VeracityGauge.jsx`** — Gauge circular responsivo que colore o arco conforme o score de veracidade e indica a confiança.
- **`LoadingIndicator.jsx`** — Spinner temporal que descreve cada fase do backend e sinaliza tempos maiores que o esperado.
- **`useNewsVerification.js` + `services/api.js`** — Hook de orquestração de estado + cliente fetch com timeout e normalização de resposta, garantindo que o frontend continue funcionando mesmo em timeouts (gera mensagens orientativas).

## Resolução de problemas e dicas
- **Timeouts longos**: a chamada é abortada após 4 minutos; o hook exibe instruções para tentar novamente com textos menores.
- **Modelo spaCy ausente**: instale manualmente com `python -m spacy download pt_core_news_lg` ou utilize o pacote listado em `requirements.txt`.
- **Chave SerpAPI**: defina `SERPAPI_KEY` no `.env` para habilitar buscas reais no Google; caso contrário, use modo `mock` para testes locais.
- **CORS/Portas**: a API já habilita CORS para qualquer origem; ajuste `HOST`/`PORT` em `.env` ou atualize `baseURL` no frontend se expuser externamente.

Com estes passos você consegue reproduzir o ambiente do TCC, compreender cada módulo e operar tanto o backend quanto a interface web.
