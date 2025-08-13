from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PDFUploadRequest(BaseModel):
    """PDF 업로드 요청 모델"""
    title: Optional[str] = Field(None, description="문서 제목")
    author: Optional[str] = Field(None, description="저자")
    description: Optional[str] = Field(None, description="문서 설명")

class PDFUploadResponse(BaseModel):
    """PDF 업로드 응답 모델"""
    document_id: str = Field(..., description="문서 ID")
    status: str = Field(..., description="처리 상태")
    message: str = Field(..., description="처리 메시지")
    chunks_count: int = Field(..., description="생성된 청크 수")
    processing_time: float = Field(..., description="처리 시간 (초)")
    metadata: Dict[str, Any] = Field(..., description="문서 메타데이터")

class SearchRequest(BaseModel):
    """검색 요청 모델"""
    query: str = Field(..., description="검색 쿼리")
    limit: int = Field(10, description="반환할 결과 수")
    score_threshold: float = Field(0.0, description="점수 임계값")
    document_id: Optional[str] = Field(None, description="특정 문서 ID")
    page_number: Optional[int] = Field(None, description="특정 페이지 번호")

class SearchResult(BaseModel):
    """검색 결과 모델"""
    id: Any = Field(..., description="결과 ID")
    score: float = Field(..., description="유사도 점수")
    text: str = Field(..., description="텍스트 내용")
    document_id: str = Field(..., description="문서 ID")
    page_number: int = Field(..., description="페이지 번호")
    chunk_index: int = Field(..., description="청크 인덱스")
    metadata: Dict[str, Any] = Field(..., description="메타데이터")

class SearchResponse(BaseModel):
    """검색 응답 모델"""
    query: str = Field(..., description="검색 쿼리")
    results: List[SearchResult] = Field(..., description="검색 결과")
    total_results: int = Field(..., description="총 결과 수")
    processing_time: float = Field(..., description="처리 시간 (초)")

class DocumentInfo(BaseModel):
    """문서 정보 모델"""
    document_id: str = Field(..., description="문서 ID")
    title: str = Field(..., description="문서 제목")
    author: str = Field(..., description="저자")
    total_pages: int = Field(..., description="총 페이지 수")
    chunks_count: int = Field(..., description="청크 수")
    upload_time: datetime = Field(..., description="업로드 시간")
    file_size: int = Field(..., description="파일 크기 (바이트)")

class DocumentsResponse(BaseModel):
    """문서 목록 응답 모델"""
    documents: List[DocumentInfo] = Field(..., description="문서 목록")
    total_documents: int = Field(..., description="총 문서 수")

class CollectionInfo(BaseModel):
    """컬렉션 정보 모델"""
    name: str = Field(..., description="컬렉션 이름")
    vectors_count: int = Field(..., description="벡터 수")
    points_count: int = Field(..., description="포인트 수")
    segments_count: int = Field(..., description="세그먼트 수")
    config: Dict[str, Any] = Field(..., description="설정 정보")

class DeleteDocumentResponse(BaseModel):
    """문서 삭제 응답 모델"""
    document_id: str = Field(..., description="삭제된 문서 ID")
    status: str = Field(..., description="삭제 상태")
    message: str = Field(..., description="삭제 메시지")
    deleted_chunks: int = Field(..., description="삭제된 청크 수")

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    timestamp: datetime = Field(..., description="에러 발생 시간")

class HealthCheckResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str = Field(..., description="서비스 상태")
    qdrant_status: str = Field(..., description="Qdrant 상태")
    ollama_status: str = Field(..., description="Ollama 상태")
    timestamp: datetime = Field(..., description="체크 시간")

class QARequest(BaseModel):
    """Q&A 요청 모델"""
    question: str = Field(..., description="질문")
    max_results: int = Field(default=5, description="검색할 최대 결과 수")
    max_tokens: int = Field(default=500, description="생성할 최대 토큰 수")
    include_metadata: bool = Field(default=False, description="메타데이터 포함 여부")
    document_id: str = Field(default=None, description="검색할 문서의 document_id (선택)")

class QAResponse(BaseModel):
    """Q&A 응답 모델"""
    question: str = Field(..., description="질문")
    answer: str = Field(..., description="답변")
    sources: List[Dict[str, Any]] = Field(default=[], description="참조 소스")
    search_results: List[Dict[str, Any]] = Field(default=[], description="검색 결과")
    context_count: int = Field(default=0, description="사용된 컨텍스트 수")
    processing_time: Optional[float] = Field(None, description="처리 시간")
    stats: Optional[Dict[str, Any]] = Field(None, description="통계 정보")
    documents: Optional[List[Dict[str, Any]]] = Field(None, description="문서 정보")
    error: Optional[str] = Field(None, description="오류 메시지")
