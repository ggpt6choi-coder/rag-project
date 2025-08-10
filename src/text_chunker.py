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
        if not text or not text.strip():
            logger.warning("빈 텍스트가 제공되었습니다")
            return []
        
        try:
            # 텍스트 분할
            chunks = self.text_splitter.split_text(text)
            
            # 청크에 메타데이터 추가
            chunk_data = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # 빈 청크 제외
                    chunk_data.append({
                        'text': chunk.strip(),
                        'chunk_index': i,
                        'chunk_size': len(chunk),
                        'start_char': text.find(chunk),
                        'end_char': text.find(chunk) + len(chunk)
                    })
            
            logger.info(f"텍스트를 {len(chunk_data)}개의 청크로 분할했습니다")
            return chunk_data
            
        except Exception as e:
            logger.error(f"텍스트 청킹 중 오류 발생: {e}")
            raise
    
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
            metadata: 메타데이터
            
        Returns:
            청크 리스트 (메타데이터 포함)
        """
        chunks = self.chunk_text(text)
        
        # 각 청크에 메타데이터 추가
        for chunk in chunks:
            chunk['metadata'] = metadata.copy()
        
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
