    
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
            import uuid
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
                # 메타데이터(문서명, 시트명, 행번호 등) 보장
                if 'metadata' in chunk and isinstance(chunk['metadata'], dict):
                    for k, v in chunk['metadata'].items():
                        payload[k] = v
                # Qdrant가 허용하는 UUID로 point id 생성
                point_id = str(uuid.uuid4())
                point = PointStruct(
                    id=point_id,
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
    
    def get_all_collections_info(self) -> list:
        """
        Qdrant에 존재하는 모든 컬렉션의 정보를 반환합니다.
        """
        if not self.client:
            if not self.connect():
                return []
        try:
            collections = self.client.get_collections()
            infos = []
            for col in collections.collections:
                try:
                    col_info = self.client.get_collection(col.name)
                    # config 파싱 오류 우회
                    try:
                        config = col_info.config.asdict()
                    except Exception:
                        try:
                            config = dict(col_info.config)
                        except Exception:
                            config = getattr(col_info.config, '__dict__', str(col_info.config))
                    infos.append({
                        'collection_name': col.name,
                        'status': col_info.status.value if hasattr(col_info.status, 'value') else str(col_info.status),
                        'optimizer_status': col_info.optimizer_status.value if hasattr(col_info.optimizer_status, 'value') else str(col_info.optimizer_status),
                        'vectors_count': col_info.vectors_count,
                        'indexed_vectors_count': col_info.indexed_vectors_count,
                        'points_count': col_info.points_count,
                        'segments_count': col_info.segments_count,
                        'config': config,
                        'payload_schema': col_info.payload_schema
                    })
                except Exception as e:
                    logger.error(f"컬렉션 {col.name} 정보 조회 실패: {e}")
            return infos
        except Exception as e:
            logger.error(f"전체 컬렉션 정보 조회 실패: {e}")
            return []
        
    
    def delete_document(self, document_id: str) -> bool:
        """
        특정 문서의 모든 벡터를 삭제합니다.
        (qdrant-client 구버전 호환: filter로 id 조회 후 id 리스트로 삭제)
        Args:
            document_id: 삭제할 문서 ID
        Returns:
            삭제 성공 여부
        """
        if not self.client:
            if not self.connect():
                return False

        try:
            # 1. 해당 document_id의 point id들을 모두 조회
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                filter=filter_condition,
                limit=10000
            )
            point_ids = [point.id for point in points]
            if not point_ids:
                logger.info(f"삭제할 포인트 없음: document_id={document_id}")
                return True
            # 2. id 리스트로 삭제
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_ids
            )
            logger.info(f"문서 '{document_id}' 삭제 완료 (포인트 {len(point_ids)}개)")
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
            # 컬렉션이 없을 때는 에러 로그 대신 info로 남기고 빈 리스트 반환
            if 'Not found: Collection' in str(e) or '404' in str(e):
                logger.info(f"컬렉션 없음: {self.collection_name} (문서 없음)")
            else:
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

    def get_document_metadata(self, document_id: str) -> dict:
        """
        해당 document_id의 첫 번째 벡터(포인트)에서 메타데이터를 추출
        """
        if not self.client:
            if not self.connect():
                return {}
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            filter_obj = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=1,
                filter=filter_obj
            )
            if points:
                return points[0].payload.get("metadata", points[0].payload)
            return {}
        except Exception as e:
            # filter 인자 관련 에러는 info로만 남기고 빈 dict 반환
            if "Unknown arguments: ['filter']" in str(e):
                logger.info(f"qdrant-client 버전 미지원: filter 인자 사용 불가 (document_id={document_id})")
            else:
                logger.error(f"문서 메타데이터 조회 실패: {e}")
            return {}