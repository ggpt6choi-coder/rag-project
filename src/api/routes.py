import os
import time
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from .models import (
    PDFUploadResponse, SearchRequest, SearchResponse, 
    DocumentsResponse, CollectionInfo, DeleteDocumentResponse,
    ErrorResponse, HealthCheckResponse, QARequest, QAResponse
)
from ..pdf_processor import PDFProcessor
from ..text_chunker import TextChunker
from ..embedding_service import EmbeddingService
from ..qdrant_manager import QdrantManager
from ..search_service import SearchService
from ..config import config
from src.qa_service import QAService

# 라우터 생성
router = APIRouter()

# 서비스 인스턴스들
pdf_processor = PDFProcessor()
text_chunker = TextChunker()
embedding_service = EmbeddingService()
qdrant_manager = QdrantManager()
search_service = SearchService(qdrant_manager, embedding_service)

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(None),
    author: str = Form(None),
    description: str = Form(None)
):
    """
    PDF 파일을 업로드하고 처리합니다.
    """
    start_time = time.time()
    
    try:
        # 파일 유효성 검사
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다")
        
        # 업로드 디렉토리 생성
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        
        # 파일 저장
        file_path = os.path.join(config.UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # PDF 처리
        pdf_data = pdf_processor.extract_text(file_path)
        
        # 텍스트 청킹
        chunks = text_chunker.chunk_text(pdf_data['text'])
        
        # 임베딩 생성
        embedded_chunks = embedding_service.embed_chunks(chunks)
        
        # 메타데이터 구성
        metadata = pdf_data['metadata'].copy()
        if title:
            metadata['title'] = title
        if author:
            metadata['author'] = author
        if description:
            metadata['description'] = description
        
        # 각 청크에 메타데이터 추가
        for chunk in embedded_chunks:
            chunk['metadata'] = metadata
        
        # Qdrant에 저장
        document_id = str(uuid.uuid4())
        success = qdrant_manager.store_vectors(embedded_chunks, document_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="벡터 저장에 실패했습니다")
        
        processing_time = time.time() - start_time
        
        return PDFUploadResponse(
            document_id=document_id,
            status="success",
            message="PDF 처리 완료",
            chunks_count=len(embedded_chunks),
            processing_time=processing_time,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"PDF 업로드 중 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    문서를 검색합니다.
    """
    start_time = time.time()
    
    try:
        results = search_service.search(
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold,
            document_id=request.document_id,
            page_number=request.page_number
        )
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"검색 중 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=DocumentsResponse)
async def get_documents():
    """
    저장된 문서 목록을 반환합니다.
    """
    try:
        document_ids = search_service.get_documents()
        
        # 실제로는 각 문서의 상세 정보를 조회해야 함
        documents = []
        for doc_id in document_ids:
            # 간단한 정보만 반환 (실제로는 더 상세한 정보 필요)
            documents.append({
                'document_id': doc_id,
                'title': f"Document {doc_id}",
                'author': "Unknown",
                'total_pages': 0,
                'chunks_count': 0,
                'upload_time': "2024-01-01T00:00:00",
                'file_size': 0
            })
        
        return DocumentsResponse(
            documents=documents,
            total_documents=len(documents)
        )
        
    except Exception as e:
        logger.error(f"문서 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections", response_model=CollectionInfo)
async def get_collection_info():
    """
    Qdrant 컬렉션 정보를 반환합니다.
    """
    try:
        info = search_service.get_collection_info()
        
        if not info:
            raise HTTPException(status_code=404, detail="컬렉션 정보를 찾을 수 없습니다")
        
        return CollectionInfo(**info)
        
    except Exception as e:
        logger.error(f"컬렉션 정보 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(document_id: str):
    """
    특정 문서를 삭제합니다.
    """
    try:
        success = search_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
        
        return DeleteDocumentResponse(
            document_id=document_id,
            status="success",
            message="문서 삭제 완료",
            deleted_chunks=0  # 실제로는 삭제된 청크 수를 계산해야 함
        )
        
    except Exception as e:
        logger.error(f"문서 삭제 중 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    서비스 상태를 확인합니다.
    """
    try:
        # Qdrant 연결 확인
        qdrant_status = "healthy" if qdrant_manager.connect() else "unhealthy"
        
        # Ollama 연결 확인
        ollama_status = "healthy" if embedding_service.validate_model() else "unhealthy"
        
        # 전체 상태 결정
        overall_status = "healthy" if qdrant_status == "healthy" and ollama_status == "healthy" else "unhealthy"
        
        return HealthCheckResponse(
            status=overall_status,
            qdrant_status=qdrant_status,
            ollama_status=ollama_status,
            timestamp=time.time()
        )
        
    except Exception as e:
        logger.error(f"헬스 체크 중 오류: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            qdrant_status="unknown",
            ollama_status="unknown",
            timestamp=time.time()
        )

@router.post("/qa", response_model=QAResponse, summary="Q&A 질문")
async def ask_question(request: QARequest):
    """Q&A 질문 처리"""
    try:
        start_time = time.time()
        
        qa_service = QAService()
        
        if request.include_metadata:
            result = qa_service.ask_with_metadata(
                question=request.question,
                max_results=request.max_results
            )
        else:
            result = qa_service.ask_question(
                question=request.question,
                max_results=request.max_results,
                max_tokens=request.max_tokens
            )
        
        processing_time = time.time() - start_time
        result["processing_time"] = processing_time
        
        return QAResponse(**result)
        
    except Exception as e:
        logger.error(f"Q&A 처리 중 오류: {e}")
        return QAResponse(
            question=request.question,
            answer="죄송합니다. 질문을 처리하는 중 오류가 발생했습니다.",
            error=str(e)
        )

@router.get("/qa/models", summary="사용 가능한 LLM 모델 목록")
async def get_available_models():
    """사용 가능한 LLM 모델 목록 조회"""
    try:
        qa_service = QAService()
        models = qa_service.get_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"모델 목록 조회 중 오류: {e}")
        return {"models": [], "error": str(e)}

@router.get("/qa/test", summary="Q&A 서비스 테스트")
async def test_qa_service():
    """Q&A 서비스 연결 테스트"""
    try:
        qa_service = QAService()
        is_connected = qa_service.test_llm_connection()
        return {
            "status": "connected" if is_connected else "disconnected",
            "llm_model": qa_service.llm_model,
            "ollama_host": qa_service.ollama_host
        }
    except Exception as e:
        logger.error(f"Q&A 서비스 테스트 중 오류: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/")
async def root():
    """
    루트 엔드포인트
    """
    return {
        "message": "PDF to Qdrant Vector Database API",
        "version": "1.0.0",
        "endpoints": [
            "POST /upload-pdf",
            "POST /search",
            "GET /documents",
            "GET /collections",
            "DELETE /documents/{document_id}",
            "GET /health"
        ]
    }
