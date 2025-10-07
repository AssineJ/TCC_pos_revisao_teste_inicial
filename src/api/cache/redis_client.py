import redis
import json
from functools import wraps
from src.config.settings import get_settings

class RedisCache:
    def __init__(self):
        self.settings = get_settings()
        self.redis_client = redis.Redis.from_url(
            self.settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    
    def cache_result(self, key: str, ttl: int = None):
        """Decorator para cache de resultados de funções"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{key}:{str(args)}:{str(kwargs)}"
                
                # Tentar obter do cache
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # Executar função e cachear resultado
                result = func(*args, **kwargs)
                self.redis_client.setex(
                    cache_key,
                    ttl or self.settings.redis_cache_ttl,
                    json.dumps(result, default=str)
                )
                return result
            return wrapper
        return decorator
    
    def clear_cache_pattern(self, pattern: str):
        """Limpar cache baseado em padrão"""
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)