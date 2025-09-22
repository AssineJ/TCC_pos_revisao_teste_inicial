from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn
from .news_collector import run_collector, NewsCollector
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


class NewsURLRequest(BaseModel):
    url: HttpUrl


class NewsResponse(BaseModel):
    verdict: str
    probability: float
    message: str
    resolved_title: Optional[str] = None
    resolved_excerpt: Optional[str] = None
    source_url: Optional[str] = None


VERDICT_MESSAGES = {
    "VERDADEIRO": "Esta notícia parece ser confiável.",
    "INDETERMINADO": "Não é possível determinar a veracidade com certeza. Consulte fontes adicionais.",
    "PROVAVELMENTE FALSO": "Cuidado! Esta notícia pode conter informações falsas.",
}


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

        return NewsResponse(
            verdict=verdict,
            probability=probability,
            message=VERDICT_MESSAGES.get(verdict, "Verifique com fontes confiáveis."),
            resolved_title=request.title,
            resolved_excerpt=request.content[:280],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-news-url", response_model=NewsResponse)
async def check_news_from_url(request: NewsURLRequest):
    try:
        collector = NewsCollector()
        article = collector.scrape_article_content(str(request.url))

        if not article or not article.get("text"):
            raise HTTPException(
                status_code=400,
                detail="Não foi possível extrair conteúdo da notícia fornecida. Verifique o link e tente novamente.",
            )

        title = article.get("title") or str(request.url)
        content = article.get("text") or ""
        normalized_excerpt = " ".join(content.split())
        verdict, probability = check_news(title, content)

        return NewsResponse(
            verdict=verdict,
            probability=probability,
            message=VERDICT_MESSAGES.get(verdict, "Verifique com fontes confiáveis."),
            resolved_title=title,
            resolved_excerpt=normalized_excerpt[:280] if normalized_excerpt else None,
            source_url=str(request.url),
        )
    except HTTPException:
        raise
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
        cursor.execute(
            """
            SELECT id, title, source_name, source_url, publish_date
            FROM news_articles
            ORDER BY collected_date DESC
            LIMIT ?
        """,
            (limit,),
        )

        results = []
        for row in cursor.fetchall():
            results.append(dict(row))

        cursor.close()
        conn.close()

        return {"news": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
