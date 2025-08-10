import os
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import PyPDF2
import pdfplumber
from loguru import logger

class PDFProcessor:
    """PDF 파일 처리 클래스"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def extract_text(self, file_path: str) -> Dict[str, any]:
        """
        PDF 파일에서 텍스트를 추출합니다.
        
        Args:
            file_path: PDF 파일 경로
            
        Returns:
            텍스트와 메타데이터를 포함한 딕셔너리
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"지원하지 않는 파일 형식입니다: {file_path}")
        
        try:
            # 파일 메타데이터 추출
            metadata = self._extract_metadata(file_path)
            
            # 텍스트 추출 (PyPDF2와 pdfplumber 모두 시도)
            text_content = self._extract_text_content(file_path)
            
            return {
                'text': text_content,
                'metadata': metadata,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'extraction_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PDF 텍스트 추출 중 오류 발생: {e}")
            raise
    
    def _extract_metadata(self, file_path: str) -> Dict[str, any]:
        """PDF 파일의 메타데이터를 추출합니다."""
        metadata = {
            'title': '',
            'author': '',
            'subject': '',
            'creator': '',
            'producer': '',
            'creation_date': '',
            'modification_date': '',
            'total_pages': 0
        }
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # PDF 정보 추출
                if pdf_reader.metadata:
                    info = pdf_reader.metadata
                    metadata.update({
                        'title': info.get('/Title', ''),
                        'author': info.get('/Author', ''),
                        'subject': info.get('/Subject', ''),
                        'creator': info.get('/Creator', ''),
                        'producer': info.get('/Producer', ''),
                        'creation_date': str(info.get('/CreationDate', '')),
                        'modification_date': str(info.get('/ModDate', ''))
                    })
                
                metadata['total_pages'] = len(pdf_reader.pages)
                
        except Exception as e:
            logger.warning(f"메타데이터 추출 중 오류: {e}")
        
        return metadata
    
    def _extract_text_content(self, file_path: str) -> str:
        """PDF 파일에서 텍스트 내용을 추출합니다."""
        text_content = ""
        
        # 먼저 pdfplumber로 시도
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            if text_content.strip():
                logger.info("pdfplumber로 텍스트 추출 성공")
                return text_content
                
        except Exception as e:
            logger.warning(f"pdfplumber 텍스트 추출 실패: {e}")
        
        # pdfplumber 실패 시 PyPDF2로 시도
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            if text_content.strip():
                logger.info("PyPDF2로 텍스트 추출 성공")
                return text_content
                
        except Exception as e:
            logger.error(f"PyPDF2 텍스트 추출 실패: {e}")
            raise Exception("텍스트 추출에 실패했습니다")
        
        if not text_content.strip():
            raise Exception("PDF에서 텍스트를 추출할 수 없습니다")
        
        return text_content
    
    def extract_text_by_pages(self, file_path: str) -> List[Dict[str, any]]:
        """
        PDF 파일을 페이지별로 텍스트를 추출합니다.
        
        Args:
            file_path: PDF 파일 경로
            
        Returns:
            페이지별 텍스트와 메타데이터 리스트
        """
        pages = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        pages.append({
                            'page_number': page_num,
                            'text': page_text,
                            'page_size': page.width * page.height if page.width and page.height else 0
                        })
            
            if not pages:
                # pdfplumber 실패 시 PyPDF2로 시도
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            pages.append({
                                'page_number': page_num,
                                'text': page_text,
                                'page_size': 0  # PyPDF2에서는 페이지 크기 정보를 직접 제공하지 않음
                            })
            
        except Exception as e:
            logger.error(f"페이지별 텍스트 추출 중 오류: {e}")
            raise
        
        return pages
    
    def get_file_hash(self, file_path: str) -> str:
        """파일의 SHA-256 해시를 계산합니다."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def validate_pdf(self, file_path: str) -> bool:
        """PDF 파일의 유효성을 검사합니다."""
        try:
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            return True
        except Exception:
            return False
