import os
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    
    # Qdrant 설정
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "pdf_documents")
    
    # Ollama 설정
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "nomic-embed-text")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # 텍스트 청킹 설정
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # 애플리케이션 설정
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # 파일 업로드 설정
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")
    MAX_FILE_SIZE: str = os.getenv("MAX_FILE_SIZE", "100MB")
    
    @classmethod
    def get_qdrant_url(cls) -> str:
        """Qdrant URL 반환"""
        return f"http://{cls.QDRANT_HOST}:{cls.QDRANT_PORT}"
    
    @classmethod
    def get_ollama_url(cls) -> str:
        """Ollama URL 반환"""
        return cls.OLLAMA_HOST

# 전역 설정 인스턴스
config = Config()
