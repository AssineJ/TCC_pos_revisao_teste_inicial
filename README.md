# TCC-2025
Repositório ao  TCC - ANÁLISE E DESENVOLVIMENTO DE SISTEMAS PARA COMBATE E DETECÇÃO DE FAKE NEWS NA INTERNET

Este é um projeto de detecção de notícias falsas (fake news) que utiliza aprendizado de máquina para classificar textos como verdadeiros ou falsos.

## Estrutura do projeto

O projeto é composto por três principais arquivos:

1. **app.py**: Interface gráfica do detector de fake news
2. **validar_noticias.py**: Script para validar notícias em lote
3. **feedback.py**: Sistema para coletar feedback quando o modelo erra

## Requisitos

>[!IMPORTANT]
>- Python 3.6+ instalado 
>- RAM: 4GB (8GB recomendado)
>- Armazenamento: 2GB livres
>- SO: Windows 10+, macOS 10.14+, Ubuntu 18.04+
>- Conexão: Internet para coleta de dados

##  Instalação

Para instalar todas as dependências necessárias:

```
pip install -r requirements.txt
```
O arquivo requirements.txt contém:
```
gradio>=4.0.0
pandas>=1.5.0
scikit-learn>=1.3.0
joblib>=1.3.0
numpy>=1.21.0
requests>=2.28.0
python-dotenv>=0.19.0
```

## Arquitetura do sistema

```
├── data_collection.py     # Coleta automatizada via NewsAPI
├── preprocess_train.py    # Pré-processamento e preparação
├── train_model.py         # Treinamento do modelo
├── app.py                # Interface web Gradio
├── validar_noticias.py   # Validação em lote
├── feedback.py           # Sistema de feedback
└── Tcc_teste4.py         # Pipeline completo
```

##  Componentes

### Front-end Streamlit (verificação por URL)

O arquivo `fake-news-detector-br/streamlit_app.py` disponibiliza uma interface web em
Streamlit capaz de consumir a API FastAPI e validar automaticamente notícias a partir
de uma URL.

1. **Inicialize a API**
   ```bash
   uvicorn fake-news-detector-br.app.main:app --reload
   ```

2. **(Opcional) Defina a variável `API_URL`** caso o backend esteja publicado fora
   de `http://localhost:8000`:
   ```bash
   # Linux/macOS
   export API_URL="https://sua-api"

   # Windows PowerShell
   $env:API_URL="https://sua-api"
   ```

3. **Execute o Streamlit**
   ```bash
   streamlit run fake-news-detector-br/streamlit_app.py
   ```

4. **Como testar a interface**
   - Cole a URL completa de uma notícia (começando com `http://` ou `https://`) e
     clique em “Verificar URL”. A aplicação solicitará o endpoint `/check-news-url`,
     exibirá o título extraído, um resumo e o veredito com a probabilidade estimada.
   - Utilize a aba “Verificação manual” para validar textos inseridos manualmente
     através do endpoint `/check-news` sempre que precisar inspecionar conteúdos que
     não estejam disponíveis publicamente.
   - Clique em “Atualizar lista” para chamar `/recent-news` e confirmar se as últimas
     matérias coletadas pelo backend aparecem com fonte, data e link originais.

### Interface Web (app.py)

Este arquivo implementa uma interface web usando Gradio que permite aos usuários inserir textos de notícias e obter classificações em tempo real.

```
import gradio as gr
import joblib

model = joblib.load('fake_news_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

def predict(text):
    text_clean = re.sub(r'[^\w\s]', '', text.lower())
    X = vectorizer.transform([text_clean])
    return model.predict(X)[0]

interface = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(lines=3, placeholder="Cole a notícia aqui..."),
    outputs="label",
    title="Detector de Fake News"
)

interface.launch()
```

### Front-end moderno (React + Vite)

Além da interface em Gradio, o repositório conta com uma aplicação web moderna em React localizada na pasta `frontend/`. Ela consome diretamente a API FastAPI (`/check-news-url`, `/check-news`, `/recent-news` e `/collect-news`) e oferece:

- Formulário para envio da URL completa da notícia a ser analisada;
- Exibição do veredito com barra de probabilidade, resumo da matéria e orientações de checagem;
- Painel com as últimas notícias coletadas e botão para disparar a coleta automática.

Para executar o front-end:

```
cd frontend
npm install
npm run dev
```

Ao abrir a interface, cole o link da matéria (com `http://` ou `https://`) no campo principal. O front-end solicita a checagem via endpoint `/check-news-url`, que faz o scraping do texto, executa o classificador e retorna o veredito acompanhado de um resumo da notícia.

Por padrão a aplicação utiliza `http://localhost:8000` como URL da API. Para apontar para outra instância basta definir a variável `VITE_API_URL` antes de iniciar o servidor de desenvolvimento ou durante o build:

```
# Linux/macOS
export VITE_API_URL="https://sua-api"
npm run dev

# Windows PowerShell
$env:VITE_API_URL="https://sua-api"
npm run dev
```

Para gerar a versão de produção utilize `npm run build` e sirva o conteúdo de `frontend/dist` com o servidor de sua preferência.

### Validação de Notícias (validar_noticias.py)

Este script permite validar várias notícias em lote, útil para testar o desempenho do modelo com novos dados.

```
import joblib
import re
import pandas as pd

# Pré-processa e classifica notícias de teste
for noticia in noticias_teste:
    noticia_limpa = clean_text(noticia)
    noticia_vetorizada = vectorizer.transform([noticia_limpa])
    predicao = model.predict(noticia_vetorizada)[0]
    print(f"Notícia: '{noticia[:50]}...' → Classificação: {predicao}")
```

### Sistema de Feedback (feedback.py)

Este componente permite coletar dados quando o modelo faz previsões incorretas, armazenando-os para futuros retreinamentos do modelo.

```
def add_feedback(text, true_label):
    # Adiciona casos mal classificados a um CSV
    try:
        df = pd.read_csv(feedback_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['text', 'label'])
    
    new_data = pd.DataFrame([[text, true_label]], columns=['text', 'label'])
    df = pd.concat([df, new_data])
    df.to_csv(feedback_file, index=False)
```

## Arquivos de Modelo

O projeto utiliza dois arquivos pré-treinados (que devem estar no diretório do projeto):

- fake_news_model.pkl: O modelo de classificação treinado
- tfidf_vectorizer.pkl: O vetorizador TF-IDF para transformar texto em vetores

## Como Usar

### Clone e Instale

```
git clone <repository-url>
cd fake-news-detector
pip install -r requirements.txt
```

### Configure a API(Opiciona)

```
# Crie arquivo .env
echo "NEWSAPI_KEY=sua_chave_aqui" > .env
```

### Prepare os Dados

```
# Com datasets existentes
python Tcc_teste4.py

# Com coleta nova
python data_collection.py
python preprocess_train.py
python train_model.py
```

### Interface Web

1 .Execute python **app.py** 

2. Acesse a interface web (normalmente em http://localhost:7860) 

3. Cole o texto da notícia a ser analisada

4. O sistema retornará a classificação (FAKE ou REAL)

### Validação em Lote

1. Edite o arquivo **validar_noticias.py** para incluir suas notícias de teste
2. Execute python **validar_noticias.py**
3. Verifique os resultados no console

### Feedback para Melhorias

1. Quando identificar classificações incorretas, use a função **add_feedback**
2. Exemplo: add_feedback **("Texto da notícia mal classificada", "FAKE")**
3. Os dados são salvos em **feedback_data.csv** para futuros retreinamentos
