from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as api_router
from src.config.settings import get_settings

def create_application() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title="News Verifier API",
        description="API para verificação de veracidade de notícias",
        version="1.0.0",
        debug=settings.api_debug
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Rotas
    app.include_router(api_router, prefix="/api/v1")
    
    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )