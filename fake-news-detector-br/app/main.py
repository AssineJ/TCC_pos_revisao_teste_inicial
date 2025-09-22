from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from textwrap import shorten
import uvicorn
from newspaper import Article
from newspaper.article import ArticleException
from .news_collector import run_collector
from .fake_news_detector import check_news
from .database import init_db, get_db_connection
import os

app = FastAPI(title="Fake News Detector BR", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewsRequest(BaseModel):
    title: str
    content: str


class NewsResponse(BaseModel):
    verdict: str
    probability: float
    message: str


class UrlRequest(BaseModel):
    url: HttpUrl


class UrlNewsResponse(NewsResponse):
    extracted_title: str | None = None
    content_preview: str | None = None
    url: HttpUrl


VERDICT_MESSAGES = {
    "VERDADEIRO": "Esta notícia parece ser confiável.",
    "INDETERMINADO": "Não é possível determinar a veracidade com certeza. Consulte fontes adicionais.",
    "PROVAVELMENTE FALSO": "Cuidado! Esta notícia pode conter informações falsas.",
}


def build_news_response(verdict: str, probability: float, message_override: str | None = None) -> NewsResponse:
    message = message_override or VERDICT_MESSAGES.get(verdict, "Verifique com fontes confiáveis.")
    return NewsResponse(verdict=verdict, probability=probability, message=message)


def extract_article_from_url(url: str) -> tuple[str, str]:
    article = Article(url)

    try:
        article.download()
        article.parse()
    except ArticleException as exc:
        raise HTTPException(status_code=400, detail="Não foi possível acessar a URL informada.") from exc

    content = (article.text or "").strip()
    if not content:
        raise HTTPException(status_code=422, detail="Não foi possível extrair conteúdo da página informada.")

    title = (article.title or "").strip() or "Título não encontrado"
    return title, content

@app.on_event("startup")
async def startup_event():
    init_db()
    print("Banco de dados inicializado")

@app.get("/")
async def root():
    return {"message": "Fake News Detector API - Brasil"}

@app.post("/check-news", response_model=NewsResponse)
async def check_news_endpoint(request: NewsRequest):
    try:
        verdict, probability = check_news(request.title, request.content)
        return build_news_response(verdict, probability)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect-news")
async def collect_news():
    try:
        count = run_collector()
        return {"message": f"Coleta concluída. {count} notícias coletadas."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent-news")
async def get_recent_news(limit: int = 10):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, source_name, source_url, publish_date 
            FROM news_articles 
            ORDER BY collected_date DESC 
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        cursor.close()
        conn.close()
        
        return {"news": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-news-url", response_model=UrlNewsResponse)
async def check_news_from_url(request: UrlRequest):
    title, content = extract_article_from_url(str(request.url))

    try:
        verdict, probability = check_news(title, content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    base_response = build_news_response(verdict, probability)
    preview = shorten(" ".join(content.split()), width=320, placeholder="…")

    return UrlNewsResponse(
        verdict=base_response.verdict,
        probability=base_response.probability,
        message=base_response.message,
        extracted_title=title,
        content_preview=preview,
        url=request.url,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
