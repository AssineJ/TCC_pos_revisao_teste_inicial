from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ContentType(str, Enum):
    URL = "url"
    TEXT = "text"

class ValidationRequest(BaseModel):
    content: str
    content_type: ContentType
    
    class Config:
        schema_extra = {
            "example": {
                "content": "https://exemplo.com/noticia",
                "content_type": "url"
            }
        }

class SourceMatch(BaseModel):
    source: str
    similarity: float
    url: Optional[HttpUrl]
    title: Optional[str]

class ValidationResponse(BaseModel):
    veracity_score: float = Field(..., ge=0, le=100)
    confidence_level: float = Field(..., ge=0, le=1)
    justification: str
    source_matches: List[SourceMatch]
    processing_time: float
    cache_hit: bool = False

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]]