import pytest
from src.text_chunker import TextChunker

class TestTextChunker:
    """텍스트 청커 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    
    def test_init(self):
        """초기화 테스트"""
        assert self.chunker.chunk_size == 100
        assert self.chunker.chunk_overlap == 20
        assert self.chunker.text_splitter is not None
    
    def test_chunk_text_empty(self):
        """빈 텍스트 청킹 테스트"""
        chunks = self.chunker.chunk_text("")
        assert chunks == []
        
        chunks = self.chunker.chunk_text("   ")
        assert chunks == []
    
    def test_chunk_text_simple(self):
        """간단한 텍스트 청킹 테스트"""
        text = "This is a simple test text for chunking. It should be split into multiple chunks."
        chunks = self.chunker.chunk_text(text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'text' in chunk
            assert 'chunk_index' in chunk
            assert 'chunk_size' in chunk
            assert 'start_char' in chunk
            assert 'end_char' in chunk
            assert chunk['text'].strip() != ""
    
    def test_chunk_text_long(self):
        """긴 텍스트 청킹 테스트"""
        # 긴 텍스트 생성
        long_text = "This is a very long text. " * 50
        chunks = self.chunker.chunk_text(long_text)
        
        assert len(chunks) > 1  # 여러 청크로 분할되어야 함
        
        # 모든 청크가 적절한 크기를 가지는지 확인
        for chunk in chunks:
            assert len(chunk['text']) <= self.chunker.chunk_size + 50  # 약간의 여유
    
    def test_chunk_text_by_pages(self):
        """페이지별 텍스트 청킹 테스트"""
        pages = [
            {'text': 'Page 1 content', 'page_number': 1, 'page_size': 100},
            {'text': 'Page 2 content', 'page_number': 2, 'page_size': 200}
        ]
        
        chunks = self.chunker.chunk_text_by_pages(pages)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'page_number' in chunk
            assert 'page_size' in chunk
            assert chunk['page_number'] in [1, 2]
    
    def test_chunk_text_with_metadata(self):
        """메타데이터와 함께 텍스트 청킹 테스트"""
        text = "Test text for chunking with metadata."
        metadata = {'title': 'Test Document', 'author': 'Test Author'}
        
        chunks = self.chunker.chunk_text_with_metadata(text, metadata)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'metadata' in chunk
            assert chunk['metadata']['title'] == 'Test Document'
            assert chunk['metadata']['author'] == 'Test Author'
    
    def test_get_chunk_statistics(self):
        """청크 통계 계산 테스트"""
        chunks = [
            {'chunk_size': 50, 'text': 'Chunk 1'},
            {'chunk_size': 75, 'text': 'Chunk 2'},
            {'chunk_size': 100, 'text': 'Chunk 3'}
        ]
        
        stats = self.chunker.get_chunk_statistics(chunks)
        
        assert stats['total_chunks'] == 3
        assert stats['avg_chunk_size'] == 75.0
        assert stats['min_chunk_size'] == 50
        assert stats['max_chunk_size'] == 100
        assert stats['total_text_length'] == 225
    
    def test_get_chunk_statistics_empty(self):
        """빈 청크 통계 계산 테스트"""
        stats = self.chunker.get_chunk_statistics([])
        
        assert stats['total_chunks'] == 0
        assert stats['avg_chunk_size'] == 0
        assert stats['min_chunk_size'] == 0
        assert stats['max_chunk_size'] == 0
        assert stats['total_text_length'] == 0
    
    def test_filter_chunks_by_size(self):
        """크기별 청크 필터링 테스트"""
        chunks = [
            {'chunk_size': 30, 'text': 'Small chunk'},
            {'chunk_size': 60, 'text': 'Medium chunk'},
            {'chunk_size': 90, 'text': 'Large chunk'}
        ]
        
        # 최소 크기 필터링
        filtered = self.chunker.filter_chunks_by_size(chunks, min_size=50)
        assert len(filtered) == 2
        assert all(chunk['chunk_size'] >= 50 for chunk in filtered)
        
        # 최대 크기 필터링
        filtered = self.chunker.filter_chunks_by_size(chunks, max_size=70)
        assert len(filtered) == 2
        assert all(chunk['chunk_size'] <= 70 for chunk in filtered)
        
        # 범위 필터링
        filtered = self.chunker.filter_chunks_by_size(chunks, min_size=40, max_size=80)
        assert len(filtered) == 1
        assert filtered[0]['chunk_size'] == 60
    
    def test_merge_small_chunks(self):
        """작은 청크 병합 테스트"""
        chunks = [
            {'chunk_size': 30, 'text': 'Small chunk 1', 'end_char': 30},
            {'chunk_size': 25, 'text': 'Small chunk 2', 'end_char': 55},
            {'chunk_size': 80, 'text': 'Large chunk', 'end_char': 135},
            {'chunk_size': 20, 'text': 'Small chunk 3', 'end_char': 155}
        ]
        
        merged = self.chunker.merge_small_chunks(chunks, min_size=50)
        
        # 작은 청크들이 병합되어야 함
        assert len(merged) < len(chunks)
        
        # 병합된 청크의 크기가 최소 크기보다 커야 함
        for chunk in merged:
            if chunk['chunk_size'] < 50:
                # 마지막 청크는 예외적으로 작을 수 있음
                assert chunk == merged[-1]
    
    def test_custom_chunk_size(self):
        """사용자 정의 청크 크기 테스트"""
        custom_chunker = TextChunker(chunk_size=200, chunk_overlap=30)
        
        text = "This is a test text. " * 20
        chunks = custom_chunker.chunk_text(text)
        
        # 청크 크기가 설정값과 비슷해야 함
        for chunk in chunks:
            assert len(chunk['text']) <= custom_chunker.chunk_size + 50
