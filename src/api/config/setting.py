from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 3600  # 1 hora
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # Scraping
    request_timeout: int = 10
    max_retries: int = 3
    
    # NLP
    spacy_model: str = "pt_core_news_sm"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()