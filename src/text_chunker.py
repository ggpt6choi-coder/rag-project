from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger
from .config import config

class TextChunker:
    """텍스트 청킹 클래스"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        TextChunker 초기화
        
        Args:
            chunk_size: 청크 크기 (토큰 수)
            chunk_overlap: 청크 오버랩 (토큰 수)
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
        
        # RecursiveCharacterTextSplitter 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        텍스트를 청크로 분할합니다.
        
        Args:
            text: 분할할 텍스트
            
        Returns:
            청크 리스트 (각 청크는 텍스트와 메타데이터 포함)
        """
        if not text or not isinstance(text, str):
            return []
        # 표/리스트/문단 등 구조별로 우선 분리
        blocks = []
        cur = []
        for line in text.splitlines():
            if line.strip().startswith("|") and line.strip().endswith("|"):
                if cur:
                    blocks.append("\n".join(cur))
                    cur = []
                blocks.append(line)
            elif line.strip() == "":
                if cur:
                    blocks.append("\n".join(cur))
                    cur = []
            else:
                cur.append(line)
        if cur:
            blocks.append("\n".join(cur))
        # 각 블록을 chunk_size 기준으로 분할, 너무 짧은 블록은 인접 블록과 합침
        min_chunk = max(100, 500 // 5)
        merged = []
        buf = ""
        for block in blocks:
            if len(block) < min_chunk:
                buf += ("\n" if buf else "") + block
                if len(buf) >= min_chunk:
                    merged.append(buf)
                    buf = ""
            else:
                if buf:
                    merged.append(buf)
                    buf = ""
                merged.append(block)
        if buf:
            merged.append(buf)
        # 최종 청크 분할
        chunks = []
        for block in merged:
            for i in range(0, len(block), 500 - 50):
                chunk = block[i:i+500]
                if chunk.strip():
                    chunks.append({
                        'text': chunk,
                        'chunk_size': len(chunk)
                    })
        return chunks
    
    def chunk_text_by_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        페이지별 텍스트를 청크로 분할합니다.
        
        Args:
            pages: 페이지별 텍스트 리스트
            
        Returns:
            청크 리스트 (페이지 정보 포함)
        """
        all_chunks = []
        
        for page in pages:
            page_text = page.get('text', '')
            page_number = page.get('page_number', 0)
            
            if page_text.strip():
                # 페이지별로 청킹
                page_chunks = self.chunk_text(page_text)
                
                # 페이지 정보 추가
                for chunk in page_chunks:
                    chunk['page_number'] = page_number
                    chunk['page_size'] = page.get('page_size', 0)
                
                all_chunks.extend(page_chunks)
        
        logger.info(f"총 {len(all_chunks)}개의 청크를 생성했습니다")
        return all_chunks
    
    def chunk_text_with_metadata(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        메타데이터와 함께 텍스트를 청킹합니다.
        Args:
            text: 분할할 텍스트
            metadata: 메타데이터 (문서명, 시트명, 행/열, 업로드 일시 등 포함)
        Returns:
            청크 리스트 (메타데이터 포함)
        """
        chunks = self.chunk_text(text)
        # 메타데이터 확장: 기본 필드 외에도 시트명, 행/열, 업로드 일시 등 유연하게 포함
        base_metadata = metadata.copy() if metadata else {}
        # 예시: 문서명, 시트명, 행, 열, 업로드 일시 등 기본 필드 보장
        base_metadata.setdefault('document_name', metadata.get('document_name') if metadata else None)
        base_metadata.setdefault('sheet_name', metadata.get('sheet_name') if metadata else None)
        base_metadata.setdefault('row', metadata.get('row') if metadata else None)
        base_metadata.setdefault('column', metadata.get('column') if metadata else None)
        base_metadata.setdefault('uploaded_at', metadata.get('uploaded_at') if metadata else None)
        # 각 청크에 메타데이터 추가 (필요시 블록별 추가 정보도 병합)
        for chunk in chunks:
            chunk['metadata'] = base_metadata.copy()
        return chunks
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        청크 통계를 계산합니다.
        
        Args:
            chunks: 청크 리스트
            
        Returns:
            통계 정보
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'avg_chunk_size': 0,
                'min_chunk_size': 0,
                'max_chunk_size': 0,
                'total_text_length': 0
            }
        
        chunk_sizes = [chunk.get('chunk_size', 0) for chunk in chunks]
        total_text_length = sum(chunk_sizes)
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': total_text_length / len(chunks),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes),
            'total_text_length': total_text_length
        }
    
    def filter_chunks_by_size(self, chunks: List[Dict[str, Any]], 
                             min_size: int = 10, max_size: int = None) -> List[Dict[str, Any]]:
        """
        크기 기준으로 청크를 필터링합니다.
        
        Args:
            chunks: 청크 리스트
            min_size: 최소 크기
            max_size: 최대 크기 (None이면 제한 없음)
            
        Returns:
            필터링된 청크 리스트
        """
        filtered_chunks = []
        
        for chunk in chunks:
            chunk_size = chunk.get('chunk_size', 0)
            
            if chunk_size >= min_size:
                if max_size is None or chunk_size <= max_size:
                    filtered_chunks.append(chunk)
        
        logger.info(f"청크 필터링: {len(chunks)} -> {len(filtered_chunks)}")
        return filtered_chunks
    
    def merge_small_chunks(self, chunks: List[Dict[str, Any]], 
                          min_size: int = 50) -> List[Dict[str, Any]]:
        """
        작은 청크들을 병합합니다.
        
        Args:
            chunks: 청크 리스트
            min_size: 최소 크기
            
        Returns:
            병합된 청크 리스트
        """
        if not chunks:
            return []
        
        merged_chunks = []
        current_chunk = None
        
        for chunk in chunks:
            if current_chunk is None:
                current_chunk = chunk.copy()
            else:
                # 현재 청크가 최소 크기보다 작으면 병합
                if current_chunk.get('chunk_size', 0) < min_size:
                    current_chunk['text'] += ' ' + chunk['text']
                    current_chunk['chunk_size'] = len(current_chunk['text'])
                    current_chunk['end_char'] = chunk.get('end_char', 0)
                else:
                    # 현재 청크가 충분히 크면 저장하고 새 청크 시작
                    merged_chunks.append(current_chunk)
                    current_chunk = chunk.copy()
        
        # 마지막 청크 추가
        if current_chunk:
            merged_chunks.append(current_chunk)
        
        logger.info(f"청크 병합: {len(chunks)} -> {len(merged_chunks)}")
        return merged_chunks
