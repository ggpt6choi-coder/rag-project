from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    Filter, FieldCondition, MatchValue, Range
)
from loguru import logger
from .config import config

class QdrantManager:
    """Qdrant 벡터 데이터베이스 관리 클래스"""
    
    def __init__(self, host: str = None, port: int = None, collection_name: str = None):
        """
        QdrantManager 초기화
        
        Args:
            host: Qdrant 호스트
            port: Qdrant 포트
            collection_name: 컬렉션 이름
        """
        self.host = host or config.QDRANT_HOST
        self.port = port or config.QDRANT_PORT
        self.collection_name = collection_name or config.QDRANT_COLLECTION_NAME
        self.client = None
        
        logger.info(f"Qdrant 매니저 초기화: {self.host}:{self.port}")
    
    def connect(self) -> bool:
        """
        Qdrant 서버에 연결합니다.
        
        Returns:
            연결 성공 여부
        """
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            
            # 연결 테스트
            collections = self.client.get_collections()
            logger.info(f"Qdrant 연결 성공: {len(collections.collections)}개 컬렉션")
            return True
            
        except Exception as e:
            logger.error(f"Qdrant 연결 실패: {e}")
            return False
    
    def create_collection(self, vector_size: int = None, distance: Distance = Distance.COSINE) -> bool:
        """
        컬렉션을 생성합니다.
        
        Args:
            vector_size: 벡터 크기
            distance: 거리 측정 방식
            
        Returns:
            생성 성공 여부
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            # 컬렉션이 이미 존재하는지 확인
            collections = self.client.get_collections()
            existing_collections = [col.name for col in collections.collections]
            
            if self.collection_name in existing_collections:
                logger.info(f"컬렉션 '{self.collection_name}'이 이미 존재합니다")
                return True
            
            # 벡터 크기 결정 (기본값 또는 임베딩 서비스에서 확인)
            if vector_size is None:
                # 임베딩 서비스를 통해 차원 확인
                try:
                    from src.embedding_service import EmbeddingService
                    embedding_service = EmbeddingService()
                    vector_size = embedding_service.get_embedding_dimension()
                except:
                    vector_size = 768  # 기본값
            
            # 새 컬렉션 생성
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            
            logger.info(f"컬렉션 '{self.collection_name}' 생성 완료")
            return True
            
        except Exception as e:
            logger.error(f"컬렉션 생성 실패: {e}")
            return False
    
    def store_vectors(self, embedded_chunks: List[Dict[str, Any]], 
                     document_id: str = None) -> bool:
        """
        임베딩된 청크들을 Qdrant에 저장합니다.
        
        Args:
            embedded_chunks: 임베딩된 청크 리스트
            document_id: 문서 ID
            
        Returns:
            저장 성공 여부
        """
        if not embedded_chunks:
            logger.warning("저장할 청크가 없습니다")
            return False
        
        if not self.client:
            if not self.connect():
                return False
        
        try:
            # 컬렉션 생성 확인
            if not self.create_collection():
                return False
            
            # 포인트 생성
            points = []
            for i, chunk in enumerate(embedded_chunks):
                embedding = chunk.get('embedding', [])
                if not embedding:
                    logger.warning(f"청크 {i}에 임베딩이 없습니다")
                    continue
                
                # 페이로드 구성
                payload = {
                    'text': chunk.get('text', ''),
                    'document_id': document_id or f"doc_{i}",
                    'chunk_index': chunk.get('chunk_index', i),
                    'page_number': chunk.get('page_number', 0),
                    'chunk_size': chunk.get('chunk_size', 0),
                    'embedding_dimension': chunk.get('embedding_dimension', len(embedding))
                }
                
                # 메타데이터 추가
                if 'metadata' in chunk:
                    payload['metadata'] = chunk['metadata']
                
                point = PointStruct(
                    id=i,  # 정수 ID 사용
                    vector=embedding,
                    payload=payload
                )
                points.append(point)
            
            # 벡터 저장
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"{len(points)}개의 벡터를 저장했습니다")
            return True
            
        except Exception as e:
            logger.error(f"벡터 저장 실패: {e}")
            return False
    
    def search_vectors(self, query_vector: List[float], limit: int = 10, 
                      score_threshold: float = 0.0, filter_condition: Filter = None) -> List[Dict[str, Any]]:
        """
        벡터 검색을 수행합니다.
        
        Args:
            query_vector: 검색할 쿼리 벡터
            limit: 반환할 결과 수
            score_threshold: 점수 임계값
            filter_condition: 필터 조건
            
        Returns:
            검색 결과 리스트
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_condition
            )
            
            results = []
            for result in search_result:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            logger.info(f"검색 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"벡터 검색 실패: {e}")
            return []
    
    def search_by_text(self, query_text: str, embedding_service, limit: int = 10, 
                       score_threshold: float = 0.0, filter_condition: Filter = None) -> List[Dict[str, Any]]:
        """
        텍스트로 검색을 수행합니다.
        
        Args:
            query_text: 검색할 텍스트
            embedding_service: 임베딩 서비스 인스턴스
            limit: 반환할 결과 수
            score_threshold: 점수 임계값
            filter_condition: 필터 조건
            
        Returns:
            검색 결과 리스트
        """
        try:
            # 텍스트를 벡터로 임베딩
            query_vector = embedding_service.embed_text(query_text)
            
            if not query_vector:
                logger.error("쿼리 텍스트 임베딩 실패")
                return []
            
            # 벡터 검색 수행
            return self.search_vectors(
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                filter_condition=filter_condition
            )
            
        except Exception as e:
            logger.error(f"텍스트 검색 실패: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        컬렉션 정보를 반환합니다.
        
        Returns:
            컬렉션 정보
        """
        if not self.client:
            if not self.connect():
                return {}
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            print('DEBUG collection_info:', collection_info)
            print('DEBUG collection_info.__dict__:', getattr(collection_info, '__dict__', str(collection_info)))
            
            return {
                'status': collection_info.status.value if hasattr(collection_info.status, 'value') else str(collection_info.status),
                'optimizer_status': collection_info.optimizer_status.value if hasattr(collection_info.optimizer_status, 'value') else str(collection_info.optimizer_status),
                'vectors_count': collection_info.vectors_count,
                'indexed_vectors_count': collection_info.indexed_vectors_count,
                'points_count': collection_info.points_count,
                'segments_count': collection_info.segments_count,
                'config': collection_info.config.dict(exclude_none=True, exclude_unset=True),
                'payload_schema': collection_info.payload_schema
            }
            
        except Exception as e:
            logger.error(f"컬렉션 정보 조회 실패: {e}")
            return {}
    
    def delete_document(self, document_id: str) -> bool:
        """
        특정 문서의 모든 벡터를 삭제합니다.
        
        Args:
            document_id: 삭제할 문서 ID
            
        Returns:
            삭제 성공 여부
        """
        if not self.client:
            if not self.connect():
                return False
        
        try:
            # 문서 ID로 필터링하여 삭제
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=filter_condition
            )
            
            logger.info(f"문서 '{document_id}' 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"문서 삭제 실패: {e}")
            return False
    
    def get_documents(self) -> List[str]:
        """
        저장된 모든 문서 ID를 반환합니다.
        
        Returns:
            문서 ID 리스트
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            # 모든 포인트 조회
            points = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000  # 충분히 큰 값
            )[0]
            
            # 고유한 문서 ID 추출
            document_ids = set()
            for point in points:
                payload = point.payload
                if 'document_id' in payload:
                    document_ids.add(payload['document_id'])
            
            return list(document_ids)
            
        except Exception as e:
            logger.error(f"문서 목록 조회 실패: {e}")
            return []
    
    def create_filter(self, document_id: str = None, page_number: int = None, 
                     chunk_size_range: Tuple[int, int] = None) -> Filter:
        """
        검색 필터를 생성합니다.
        
        Args:
            document_id: 문서 ID
            page_number: 페이지 번호
            chunk_size_range: 청크 크기 범위 (min, max)
            
        Returns:
            필터 객체
        """
        conditions = []
        
        if document_id:
            conditions.append(
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            )
        
        if page_number is not None:
            conditions.append(
                FieldCondition(
                    key="page_number",
                    match=MatchValue(value=page_number)
                )
            )
        
        if chunk_size_range:
            min_size, max_size = chunk_size_range
            conditions.append(
                FieldCondition(
                    key="chunk_size",
                    range=Range(gte=min_size, lte=max_size)
                )
            )
        
        if conditions:
            return Filter(must=conditions)
        else:
            return None
