import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.pdf_processor import PDFProcessor

class TestPDFProcessor:
    """PDF 프로세서 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.processor = PDFProcessor()
    
    def test_init(self):
        """초기화 테스트"""
        assert self.processor.supported_extensions == ['.pdf']
    
    def test_extract_text_file_not_found(self):
        """존재하지 않는 파일 처리 테스트"""
        with pytest.raises(FileNotFoundError):
            self.processor.extract_text("nonexistent.pdf")
    
    def test_extract_text_unsupported_format(self):
        """지원하지 않는 형식 처리 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            f.flush()
            
            with pytest.raises(ValueError):
                self.processor.extract_text(f.name)
            
            os.unlink(f.name)
    
    @patch('src.pdf_processor.pdfplumber.open')
    @patch('src.pdf_processor.PyPDF2.PdfReader')
    def test_extract_text_success(self, mock_pypdf2, mock_pdfplumber):
        """성공적인 텍스트 추출 테스트"""
        # Mock 설정
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf
        
        # 임시 PDF 파일 생성
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"%PDF-1.4\n%Test PDF content")
            f.flush()
            
            try:
                result = self.processor.extract_text(f.name)
                
                assert 'text' in result
                assert 'metadata' in result
                assert 'file_path' in result
                assert 'file_size' in result
                assert 'extraction_time' in result
                
            finally:
                os.unlink(f.name)
    
    def test_get_file_hash(self):
        """파일 해시 계산 테스트"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            
            try:
                hash_value = self.processor.get_file_hash(f.name)
                assert len(hash_value) == 64  # SHA-256 해시 길이
                assert isinstance(hash_value, str)
                
            finally:
                os.unlink(f.name)
    
    def test_validate_pdf_valid(self):
        """유효한 PDF 검증 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"%PDF-1.4\n%Test PDF content")
            f.flush()
            
            try:
                assert self.processor.validate_pdf(f.name) == True
                
            finally:
                os.unlink(f.name)
    
    def test_validate_pdf_invalid(self):
        """유효하지 않은 PDF 검증 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"Not a PDF file")
            f.flush()
            
            try:
                assert self.processor.validate_pdf(f.name) == False
                
            finally:
                os.unlink(f.name)
    
    @patch('src.pdf_processor.pdfplumber.open')
    def test_extract_text_by_pages(self, mock_pdfplumber):
        """페이지별 텍스트 추출 테스트"""
        # Mock 설정
        mock_pdf = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page1.width = 100
        mock_page1.height = 100
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_page2.width = 200
        mock_page2.height = 200
        
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"%PDF-1.4\n%Test PDF content")
            f.flush()
            
            try:
                pages = self.processor.extract_text_by_pages(f.name)
                
                assert len(pages) == 2
                assert pages[0]['page_number'] == 1
                assert pages[0]['text'] == "Page 1 content"
                assert pages[1]['page_number'] == 2
                assert pages[1]['text'] == "Page 2 content"
                
            finally:
                os.unlink(f.name)
