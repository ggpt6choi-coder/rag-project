import requests
import json
from typing import List, Dict, Any, Optional
from loguru import logger
from .config import config

class EmbeddingService:
    """Ollama를 사용한 임베딩 서비스 클래스"""
    
    def __init__(self, model_name: str = None, base_url: str = None):
        """
        EmbeddingService 초기화
        
        Args:
            model_name: 사용할 임베딩 모델명
            base_url: Ollama 서버 URL
        """
        self.model_name = model_name or config.OLLAMA_EMBEDDING_MODEL
        self.base_url = base_url or config.get_ollama_url()
        self.embedding_url = f"{self.base_url}/api/embeddings"
        
        logger.info(f"임베딩 서비스 초기화: {self.model_name} at {self.base_url}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트를 벡터로 임베딩합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        if not text or not text.strip():
            logger.warning("빈 텍스트가 제공되었습니다")
            return []
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": text.strip()
            }
            
            response = requests.post(self.embedding_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            embedding = result.get('embedding', [])
            
            logger.debug(f"텍스트 임베딩 완료: {len(embedding)} 차원")
            return embedding
            
        except requests.exceptions.RequestException as e:
            logger.error(f"임베딩 요청 중 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"임베딩 처리 중 오류: {e}")
            raise
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        청크 리스트를 벡터로 임베딩합니다.
        
        Args:
            chunks: 청크 리스트
            
        Returns:
            임베딩이 추가된 청크 리스트
        """
        if not chunks:
            logger.warning("빈 청크 리스트가 제공되었습니다")
            return []
        
        embedded_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                text = chunk.get('text', '')
                if text.strip():
                    embedding = self.embed_text(text)
                    
                    # 임베딩 결과를 청크에 추가
                    embedded_chunk = chunk.copy()
                    embedded_chunk['embedding'] = embedding
                    embedded_chunk['embedding_dimension'] = len(embedding)
                    
                    embedded_chunks.append(embedded_chunk)
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"임베딩 진행률: {i + 1}/{len(chunks)}")
                        
            except Exception as e:
                logger.error(f"청크 {i} 임베딩 중 오류: {e}")
                # 오류가 발생한 청크는 건너뛰고 계속 진행
                continue
        
        logger.info(f"총 {len(embedded_chunks)}개의 청크 임베딩 완료")
        return embedded_chunks
    
    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        텍스트 배치를 벡터로 임베딩합니다.
        
        Args:
            texts: 임베딩할 텍스트 리스트
            batch_size: 배치 크기
            
        Returns:
            임베딩 벡터 리스트
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            for text in batch:
                try:
                    embedding = self.embed_text(text)
                    batch_embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"배치 임베딩 중 오류: {e}")
                    # 오류 시 빈 벡터 추가
                    batch_embeddings.append([])
            
            embeddings.extend(batch_embeddings)
            
            logger.info(f"배치 임베딩 진행률: {min(i + batch_size, len(texts))}/{len(texts)}")
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        현재 모델의 임베딩 차원을 반환합니다.
        
        Returns:
            임베딩 차원
        """
        try:
            # 테스트 텍스트로 임베딩 차원 확인
            test_text = "This is a test text for dimension check."
            embedding = self.embed_text(test_text)
            return len(embedding)
        except Exception as e:
            logger.error(f"임베딩 차원 확인 중 오류: {e}")
            # 기본값 반환
            return 1536
    
    def validate_model(self) -> bool:
        """
        현재 모델의 유효성을 검사합니다.
        
        Returns:
            모델 유효성 여부
        """
        try:
            # 간단한 텍스트로 테스트
            test_text = "Hello, world!"
            embedding = self.embed_text(test_text)
            
            if embedding and len(embedding) > 0:
                logger.info(f"모델 검증 성공: {self.model_name}")
                return True
            else:
                logger.error("모델 검증 실패: 빈 임베딩 반환")
                return False
                
        except Exception as e:
            logger.error(f"모델 검증 중 오류: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        현재 모델 정보를 반환합니다.
        
        Returns:
            모델 정보 딕셔너리
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            
            for model in models:
                if model.get('name') == self.model_name:
                    return {
                        'name': model.get('name'),
                        'size': model.get('size'),
                        'modified_at': model.get('modified_at'),
                        'digest': model.get('digest')
                    }
            
            return {'name': self.model_name, 'status': 'not_found'}
            
        except Exception as e:
            logger.error(f"모델 정보 조회 중 오류: {e}")
            return {'name': self.model_name, 'status': 'error'}
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        두 임베딩 벡터 간의 코사인 유사도를 계산합니다.
        
        Args:
            embedding1: 첫 번째 임베딩 벡터
            embedding2: 두 번째 임베딩 벡터
            
        Returns:
            코사인 유사도 (0-1)
        """
        if not embedding1 or not embedding2:
            return 0.0
        
        if len(embedding1) != len(embedding2):
            logger.warning("임베딩 차원이 다릅니다")
            return 0.0
        
        try:
            import numpy as np
            
            # numpy 배열로 변환
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # 코사인 유사도 계산
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except ImportError:
            logger.error("numpy가 설치되지 않았습니다")
            return 0.0
        except Exception as e:
            logger.error(f"유사도 계산 중 오류: {e}")
            return 0.0
