import os
import time
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger

from .models import (
    PDFUploadResponse, SearchRequest, SearchResponse, 
    DocumentsResponse, CollectionInfo, DeleteDocumentResponse,
    ErrorResponse, HealthCheckResponse, QARequest, QAResponse,
    FeedbackRequest, FeedbackResponse
)
from ..pdf_processor import PDFProcessor, get_processor
from ..text_chunker import TextChunker
from ..embedding_service import EmbeddingService
from ..qdrant_manager import QdrantManager
from ..search_service import SearchService
from ..config import config
from src.qa_service import QAService

# 라우터 생성
router = APIRouter()

@router.post("/qa/feedback", response_model=FeedbackResponse, summary="Q&A 답변 피드백/수정 요청")
async def submit_feedback(request: FeedbackRequest):
    """Q&A 답변에 대한 사용자 피드백/수정 요청을 처리합니다."""
    try:
        feedback_id = str(uuid.uuid4())
        # 실제 운영에서는 DB나 파일 등에 저장 필요. 여기서는 로그로만 기록
        logger.info(f"[피드백] ID: {feedback_id}\n질문: {request.question}\n답변: {request.answer}\n유형: {request.feedback_type}\n상세: {request.feedback_detail}\n사용자: {request.user_id}")
        return FeedbackResponse(
            status="success",
            message="피드백이 정상적으로 접수되었습니다.",
            feedback_id=feedback_id
        )
    except Exception as e:
        logger.error(f"피드백 처리 중 오류: {e}")
        return FeedbackResponse(
            status="error",
            message="피드백 처리 중 오류가 발생했습니다.",
            feedback_id=None
        )
import os
import time
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger


from .models import (
    PDFUploadResponse, SearchRequest, SearchResponse, 
    DocumentsResponse, CollectionInfo, DeleteDocumentResponse,
    ErrorResponse, HealthCheckResponse, QARequest, QAResponse
)
from ..pdf_processor import PDFProcessor, get_processor
from ..text_chunker import TextChunker
from ..embedding_service import EmbeddingService
from ..qdrant_manager import QdrantManager
from ..search_service import SearchService
from ..config import config
from src.qa_service import QAService

# 라우터 생성
router = APIRouter()

@router.post("/qa/feedback", response_model=FeedbackResponse, summary="Q&A 답변 피드백/수정 요청")
async def submit_feedback(request: FeedbackRequest):
    """Q&A 답변에 대한 사용자 피드백/수정 요청을 처리합니다."""
    try:
        feedback_id = str(uuid.uuid4())
        # 실제 운영에서는 DB나 파일 등에 저장 필요. 여기서는 로그로만 기록
        logger.info(f"[피드백] ID: {feedback_id}\n질문: {request.question}\n답변: {request.answer}\n유형: {request.feedback_type}\n상세: {request.feedback_detail}\n사용자: {request.user_id}")
        return FeedbackResponse(
            status="success",
            message="피드백이 정상적으로 접수되었습니다.",
            feedback_id=feedback_id
        )
    except Exception as e:
        logger.error(f"피드백 처리 중 오류: {e}")
        return FeedbackResponse(
            status="error",
            message="피드백 처리 중 오류가 발생했습니다.",
            feedback_id=None
        )

# 서비스 인스턴스들
pdf_processor = PDFProcessor()
@router.post("/upload-file", response_model=PDFUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_id: str = Form(None),
    collection_name: str = Form(None)
):
    """
    다양한 파일(docx, xlsx, pptx, pdf 등)을 업로드하고 처리합니다. (비동기 백그라운드 처리)
    """
    start_time = time.time()
    try:
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(config.UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        name, ext = os.path.splitext(file.filename)
        if not ext:
            raise HTTPException(status_code=400, detail="파일 확장자가 없는 파일은 지원하지 않습니다.")
        # 백그라운드 작업 등록
        task_id = str(uuid.uuid4())
        def process_file_task():
            try:
                processor = get_processor(file_path)
                extracted = processor.extract_text(file_path)
                if isinstance(extracted, dict):
                    text = extracted.get('text', '')
                    if ext.lower() == '.pdf':
                        metadata = extracted.get('metadata', {})
                        metadata['title'] = file.filename
                        metadata['file_type'] = ext.lower()
                    else:
                        metadata = {
                            'title': file.filename,
                            'file_type': ext.lower(),
                        }
                else:
                    text = extracted
                    metadata = {
                        'title': file.filename,
                        'file_type': ext.lower(),
                    }
                logger.info(f"[OCR 추출 결과] 파일명: {file.filename}\n{text}")
                if not text or not isinstance(text, str) or not text.strip():
                    logger.error(f"[백그라운드] 텍스트 추출 실패: {file.filename}")
                    return
                if ext.lower() == '.xlsx':
                    sample = text[:1000]
                    logger.info(f"[엑셀 구조 요약 프롬프트] 예시:\n아래는 업로드된 엑셀의 구조 일부입니다. 시트명, 표 구조, 헤더, 데이터 등을 요약/설명해 주세요.\n---\n{sample}\n---")
                chunks = text_chunker.chunk_text(text)
                if not chunks:
                    logger.error(f"[백그라운드] 청크 생성 실패: {file.filename}")
                    return
                embedded_chunks = embedding_service.embed_chunks(chunks)
                if not embedded_chunks:
                    logger.error(f"[백그라운드] 임베딩 생성 실패: {file.filename}")
                    return
                for chunk in embedded_chunks:
                    chunk['metadata'] = metadata
                doc_id = document_id if document_id else str(uuid.uuid4())
                qdrant_mgr = QdrantManager(collection_name=collection_name) if collection_name else QdrantManager()
                success = qdrant_mgr.store_vectors(embedded_chunks, doc_id)
                if not success:
                    logger.error(f"[백그라운드] 벡터 저장 실패: {file.filename}")
                logger.info(f"[백그라운드] 파일 처리 완료: {file.filename}")
            except Exception as e:
                logger.error(f"[백그라운드] 파일 처리 중 오류: {e}")
        background_tasks.add_task(process_file_task)
        processing_time = time.time() - start_time
        return PDFUploadResponse(
            document_id=task_id,
            status="processing",
            message="파일 업로드 완료, 백그라운드에서 처리 중입니다.",
            chunks_count=0,
            processing_time=processing_time,
            metadata={"filename": file.filename, "file_type": ext.lower()}
        )
    except Exception as e:
        logger.error(f"파일 업로드 중 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
text_chunker = TextChunker()
embedding_service = EmbeddingService()
qdrant_manager = QdrantManager()
search_service = SearchService(qdrant_manager, embedding_service)

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    # title, author, description 제거
    collection_name: str = Form(None)
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
        metadata['title'] = file.filename
            
        # 각 청크에 메타데이터 추가
        for chunk in embedded_chunks:
            chunk['metadata'] = metadata
        
        # Qdrant에 저장
        document_id = str(uuid.uuid4())
        qdrant_mgr = QdrantManager(collection_name=collection_name) if collection_name else QdrantManager()
        success = qdrant_mgr.store_vectors(embedded_chunks, document_id)

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
        documents = []
        # 각 document_id별 대표 메타데이터 추출
        from datetime import datetime
        for doc_id in document_ids:
            # Qdrant에서 해당 document_id의 첫 번째 벡터(포인트) 메타데이터 조회
            meta = qdrant_manager.get_document_metadata(doc_id)
            extraction_time = meta.get('extraction_time', None) if meta else None
            # extraction_time이 없거나 빈 문자열이면 현재 시간으로 대체
            if not extraction_time:
                upload_time = datetime.now()
            else:
                try:
                    upload_time = datetime.fromisoformat(extraction_time)
                except Exception:
                    upload_time = datetime.now()
            documents.append({
                'document_id': doc_id,
                'title': meta.get('title', f"Document {doc_id}") if meta else f"Document {doc_id}",
                'author': meta.get('author', "Unknown") if meta else "Unknown",
                'description': meta.get('description', "") if meta else "",
                'file_type': meta.get('file_type', "") if meta else "",
                'total_pages': meta.get('total_pages', 0) if meta else 0,
                'chunks_count': meta.get('chunks_count', 0) if meta else 0,
                'upload_time': upload_time,
                'file_size': meta.get('file_size', 0) if meta else 0
            })
        return DocumentsResponse(
            documents=documents,
            total_documents=len(documents)
        )
    except Exception as e:
        logger.error(f"문서 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections")
async def get_collection_info():
    """
    Qdrant 컬렉션 정보를 반환합니다.
    """
    try:
        infos = search_service.qdrant_manager.get_all_collections_info()
        if not infos:
            raise HTTPException(status_code=404, detail="컬렉션 정보를 찾을 수 없습니다")
        return infos
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
                collection_name=request.collection_name,
                max_results=request.max_results,
                max_tokens=request.max_tokens,
                document_id=request.document_id
            )
        else:
            result = qa_service.ask_question(
                question=request.question,
                collection_name=request.collection_name,
                max_results=request.max_results,
                max_tokens=request.max_tokens,
                document_id=request.document_id
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

