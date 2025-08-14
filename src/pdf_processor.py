import cv2
import numpy as np
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None
try:
    import easyocr
except ImportError:
    easyocr = None

# ---- 파일 포맷별 프로세서 ----
class BaseFileProcessor:
    """파일 추출 기본 클래스"""
    def extract_text(self, file_path: str) -> str:
        raise NotImplementedError

class ImageProcessor(BaseFileProcessor):
    def extract_text(self, file_path: str) -> str:
        img = cv2.imread(file_path)
        img = preprocess_image_for_ocr(img)
        # easyocr 우선 사용, 실패 시 pytesseract fallback
        text = ""
        if easyocr:
            try:
                reader = easyocr.Reader(['ko', 'en'])
                text = "\n".join([r[1] for r in reader.readtext(img)])
            except Exception as e:
                print(f"[easyocr 오류] {e}")
        if (not text or not text.strip()) and pytesseract:
            try:
                from PIL import Image
                pil_img = Image.fromarray(img)
                text = pytesseract.image_to_string(pil_img, lang='kor+eng')
            except Exception as e:
                print(f"[pytesseract 오류] {e}")
        return text

# 이미지 전처리 및 OCR 함수
def preprocess_image_for_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 샤프닝 필터 적용
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharp = cv2.filter2D(gray, -1, kernel)
    # 대비 증가
    sharp = cv2.convertScaleAbs(sharp, alpha=1.5, beta=0)
    # adaptive threshold
    proc = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10)
    proc = cv2.fastNlMeansDenoising(proc, None, 30, 7, 21)
    proc = cv2.resize(proc, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return proc

def ocr_image(img) -> str:
    if pytesseract:
        pil_img = Image.fromarray(img)
        text = pytesseract.image_to_string(pil_img, lang='kor+eng')
        if text.strip():
            return text
    if easyocr:
        reader = easyocr.Reader(['ko', 'en'])
        text = "\n".join([r[1] for r in reader.readtext(img)])
        return text
    return ""
import os
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import PyPDF2
import pdfplumber
from loguru import logger


# ---- 파일 포맷별 프로세서 ----
class BaseFileProcessor:
    """파일 추출 기본 클래스"""
    def extract_text(self, file_path: str) -> str:
        raise NotImplementedError

class WordProcessor(BaseFileProcessor):
    def extract_text(self, file_path: str) -> str:
        from docx import Document
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

class ExcelProcessor(BaseFileProcessor):
    def extract_text(self, file_path: str) -> str:
        import openpyxl
        wb = openpyxl.load_workbook(file_path)
        text_blocks = []
        for sheet in wb.worksheets:
            rows = list(sheet.iter_rows(values_only=True))
            if not rows or all([all(cell is None or str(cell).strip() == '' for cell in row) for row in rows]):
                continue  # 빈 시트 skip
            block = [f"[{sheet.title}]"]
            # 헤더 추출 (첫 행)
            header = rows[0]
            header_text = " | ".join([str(cell) if cell is not None else "" for cell in header])
            block.append(f"| {header_text} |")
            # 데이터 행
            for row in rows[1:]:
                row_text = " | ".join([str(cell) if cell is not None else "" for cell in row])
                block.append(f"| {row_text} |")
            text_blocks.append("\n".join(block))
        return "\n\n".join(text_blocks) if text_blocks else ""

class PowerPointProcessor(BaseFileProcessor):
    def extract_text(self, file_path: str) -> str:
        from pptx import Presentation
        prs = Presentation(file_path)
        text = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text.append(shape.text)
        return "\n".join(text)

def get_processor(file_path: str) -> BaseFileProcessor:
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        return PDFProcessor()
    elif ext == ".docx":
        return WordProcessor()
    elif ext == ".xlsx":
        return ExcelProcessor()
    elif ext == ".pptx":
        return PowerPointProcessor()
    elif ext in [".jpg", ".jpeg", ".png"]:
        return ImageProcessor()
    else:
        raise ValueError("지원하지 않는 파일 형식입니다.")

# ---- PDF 전용 프로세서 ----
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
            metadata = self._extract_metadata(file_path)
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
        text_content = ""
        # pdfplumber로 시도
        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
            if text.strip():
                logger.info("pdfplumber로 텍스트 추출 성공")
                return text
        except Exception as e:
            logger.warning(f"pdfplumber 텍스트 추출 실패: {e}")
        # PyPDF2로 시도
        try:
            text_content = ""
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

    def extract_text_by_pages(self, file_path: str) -> List[Dict[str, any]]:
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
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            pages.append({
                                'page_number': page_num,
                                'text': page_text,
                                'page_size': 0
                            })
        except Exception as e:
            logger.error(f"페이지별 텍스트 추출 중 오류: {e}")
            raise
        return pages

    def get_file_hash(self, file_path: str) -> str:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def validate_pdf(self, file_path: str) -> bool:
        try:
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            return True
        except Exception:
            return False
