from typing import List, Dict, Any, Optional
from loguru import logger
from .qdrant_manager import QdrantManager
from .embedding_service import EmbeddingService

class SearchService:
    """검색 서비스 클래스"""
    
    def __init__(self, qdrant_manager: QdrantManager = None, embedding_service: EmbeddingService = None):
        """
        SearchService 초기화
        
        Args:
            qdrant_manager: Qdrant 매니저 인스턴스
            embedding_service: 임베딩 서비스 인스턴스
        """
        self.qdrant_manager = qdrant_manager or QdrantManager()
        self.embedding_service = embedding_service or EmbeddingService()
        
        logger.info("검색 서비스 초기화 완료")
    
    def search(self, query: str, limit: int = 10, score_threshold: float = 0.0, 
               document_id: str = None, page_number: int = None) -> List[Dict[str, Any]]:
        """
        텍스트 검색을 수행합니다.
        
        Args:
            query: 검색 쿼리
            limit: 반환할 결과 수
            score_threshold: 점수 임계값
            document_id: 특정 문서로 제한
            page_number: 특정 페이지로 제한
            
        Returns:
            검색 결과 리스트
        """
        try:
            # 필터 조건 생성
            filter_condition = self.qdrant_manager.create_filter(
                document_id=document_id,
                page_number=page_number
            )
            
            # 텍스트 검색 수행
            results = self.qdrant_manager.search_by_text(
                query_text=query,
                embedding_service=self.embedding_service,
                limit=limit,
                score_threshold=score_threshold,
                filter_condition=filter_condition
            )
            
            # 결과 포맷팅
            formatted_results = []
            for result in results:
                formatted_result = {
                    'id': result['id'],
                    'score': result['score'],
                    'text': result['payload'].get('text', ''),
                    'document_id': result['payload'].get('document_id', ''),
                    'page_number': result['payload'].get('page_number', 0),
                    'chunk_index': result['payload'].get('chunk_index', 0),
                    'metadata': result['payload'].get('metadata', {})
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"검색 완료: '{query}' -> {len(formatted_results)}개 결과")
            return formatted_results
            
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {e}")
            return []
    
    def search_similar(self, text: str, limit: int = 10, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        유사한 텍스트를 검색합니다.
        
        Args:
            text: 유사성을 찾을 텍스트
            limit: 반환할 결과 수
            score_threshold: 점수 임계값
            
        Returns:
            유사한 텍스트 리스트
        """
        return self.search(text, limit, score_threshold)
    
    def search_by_document(self, query: str, document_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        특정 문서 내에서 검색합니다.
        
        Args:
            query: 검색 쿼리
            document_id: 문서 ID
            limit: 반환할 결과 수
            
        Returns:
            검색 결과 리스트
        """
        return self.search(query, limit, document_id=document_id)
    
    def search_by_page(self, query: str, document_id: str, page_number: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        특정 문서의 특정 페이지에서 검색합니다.
        
        Args:
            query: 검색 쿼리
            document_id: 문서 ID
            page_number: 페이지 번호
            limit: 반환할 결과 수
            
        Returns:
            검색 결과 리스트
        """
        return self.search(query, limit, document_id=document_id, page_number=page_number)
    
    def get_documents(self) -> List[str]:
        """
        저장된 모든 문서 ID를 반환합니다.
        
        Returns:
            문서 ID 리스트
        """
        return self.qdrant_manager.get_documents()
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        컬렉션 정보를 반환합니다.
        
        Returns:
            컬렉션 정보
        """
        return self.qdrant_manager.get_collection_info()
    
    def delete_document(self, document_id: str) -> bool:
        """
        특정 문서를 삭제합니다.
        
        Args:
            document_id: 삭제할 문서 ID
            
        Returns:
            삭제 성공 여부
        """
        return self.qdrant_manager.delete_document(document_id)
    
    def search_with_metadata(self, query: str, metadata_filter: Dict[str, Any], 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        메타데이터 필터와 함께 검색합니다.
        
        Args:
            query: 검색 쿼리
            metadata_filter: 메타데이터 필터
            limit: 반환할 결과 수
            
        Returns:
            검색 결과 리스트
        """
        try:
            # 기본 검색 수행
            results = self.search(query, limit)
            
            # 메타데이터 필터링
            filtered_results = []
            for result in results:
                metadata = result.get('metadata', {})
                match = True
                
                for key, value in metadata_filter.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_results.append(result)
            
            logger.info(f"메타데이터 필터링: {len(results)} -> {len(filtered_results)}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"메타데이터 검색 중 오류: {e}")
            return []
    
    def get_search_statistics(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """
        검색 통계를 반환합니다.
        
        Args:
            query: 검색 쿼리
            limit: 검색할 최대 결과 수
            
        Returns:
            검색 통계
        """
        try:
            results = self.search(query, limit)
            
            if not results:
                return {
                    'total_results': 0,
                    'avg_score': 0.0,
                    'min_score': 0.0,
                    'max_score': 0.0,
                    'document_count': 0,
                    'page_count': 0
                }
            
            scores = [result['score'] for result in results]
            document_ids = set(result['document_id'] for result in results)
            page_numbers = set(result['page_number'] for result in results)
            
            return {
                'total_results': len(results),
                'avg_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'document_count': len(document_ids),
                'page_count': len(page_numbers),
                'documents': list(document_ids),
                'pages': list(page_numbers)
            }
            
        except Exception as e:
            logger.error(f"검색 통계 계산 중 오류: {e}")
            return {}
    
    def validate_search(self, query: str) -> bool:
        """
        검색 기능의 유효성을 검사합니다.
        
        Args:
            query: 테스트 쿼리
            
        Returns:
            검색 유효성 여부
        """
        try:
            # 간단한 검색 테스트
            results = self.search(query, limit=1)
            
            # 임베딩 서비스 검증
            embedding_valid = self.embedding_service.validate_model()
            
            # Qdrant 연결 검증
            qdrant_valid = self.qdrant_manager.connect()
            
            return embedding_valid and qdrant_valid
            
        except Exception as e:
            logger.error(f"검색 유효성 검사 중 오류: {e}")
            return False
