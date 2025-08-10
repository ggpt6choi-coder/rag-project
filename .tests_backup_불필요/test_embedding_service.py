import pytest
from unittest.mock import Mock, patch
from src.embedding_service import EmbeddingService

class TestEmbeddingService:
    """임베딩 서비스 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.service = EmbeddingService()
    
    def test_init(self):
        """초기화 테스트"""
        assert self.service.model_name is not None
        assert self.service.base_url is not None
        assert self.service.embedding_url is not None
    
    @patch('src.embedding_service.requests.post')
    def test_embed_text_success(self, mock_post):
        """성공적인 텍스트 임베딩 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            'embedding': [0.1, 0.2, 0.3, 0.4, 0.5] * 300  # 1500 차원
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.service.embed_text("Test text for embedding")
        
        assert len(result) == 1500
        assert all(isinstance(x, float) for x in result)
        assert all(0 <= x <= 1 for x in result)  # 임베딩 값은 보통 0-1 범위
    
    @patch('src.embedding_service.requests.post')
    def test_embed_text_empty(self, mock_post):
        """빈 텍스트 임베딩 테스트"""
        result = self.service.embed_text("")
        assert result == []
        
        result = self.service.embed_text("   ")
        assert result == []
    
    @patch('src.embedding_service.requests.post')
    def test_embed_text_request_error(self, mock_post):
        """요청 오류 테스트"""
        mock_post.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            self.service.embed_text("Test text")
    
    @patch('src.embedding_service.requests.post')
    def test_embed_chunks(self, mock_post):
        """청크 임베딩 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            'embedding': [0.1, 0.2, 0.3, 0.4, 0.5] * 300
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        chunks = [
            {'text': 'First chunk text', 'chunk_index': 0},
            {'text': 'Second chunk text', 'chunk_index': 1},
            {'text': 'Third chunk text', 'chunk_index': 2}
        ]
        
        result = self.service.embed_chunks(chunks)
        
        assert len(result) == 3
        for chunk in result:
            assert 'embedding' in chunk
            assert 'embedding_dimension' in chunk
            assert len(chunk['embedding']) == 1500
            assert chunk['embedding_dimension'] == 1500
    
    @patch('src.embedding_service.requests.post')
    def test_embed_chunks_empty(self, mock_post):
        """빈 청크 리스트 테스트"""
        result = self.service.embed_chunks([])
        assert result == []
    
    @patch('src.embedding_service.requests.post')
    def test_embed_batch(self, mock_post):
        """배치 임베딩 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            'embedding': [0.1, 0.2, 0.3, 0.4, 0.5] * 300
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        texts = ["Text 1", "Text 2", "Text 3", "Text 4", "Text 5"]
        
        result = self.service.embed_batch(texts, batch_size=2)
        
        assert len(result) == 5
        for embedding in result:
            assert len(embedding) == 1500
    
    @patch('src.embedding_service.requests.post')
    def test_get_embedding_dimension(self, mock_post):
        """임베딩 차원 확인 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            'embedding': [0.1, 0.2, 0.3, 0.4, 0.5] * 300
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        dimension = self.service.get_embedding_dimension()
        assert dimension == 1500
    
    @patch('src.embedding_service.requests.post')
    def test_validate_model_success(self, mock_post):
        """모델 검증 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            'embedding': [0.1, 0.2, 0.3, 0.4, 0.5] * 300
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.service.validate_model()
        assert result == True
    
    @patch('src.embedding_service.requests.post')
    def test_validate_model_failure(self, mock_post):
        """모델 검증 실패 테스트"""
        # Mock 응답 설정 (빈 임베딩)
        mock_response = Mock()
        mock_response.json.return_value = {
            'embedding': []
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.service.validate_model()
        assert result == False
    
    @patch('src.embedding_service.requests.get')
    def test_get_model_info_success(self, mock_get):
        """모델 정보 조회 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            'models': [
                {
                    'name': 'nomic-embed-text',
                    'size': 123456789,
                    'modified_at': '2024-01-01T00:00:00Z',
                    'digest': 'sha256:abc123'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        info = self.service.get_model_info()
        
        assert info['name'] == 'nomic-embed-text'
        assert info['size'] == 123456789
    
    @patch('src.embedding_service.requests.get')
    def test_get_model_info_not_found(self, mock_get):
        """모델 정보 조회 실패 테스트"""
        # Mock 응답 설정 (모델 없음)
        mock_response = Mock()
        mock_response.json.return_value = {
            'models': []
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        info = self.service.get_model_info()
        
        assert info['name'] == self.service.model_name
        assert info['status'] == 'not_found'
    
    def test_calculate_similarity_success(self):
        """유사도 계산 성공 테스트"""
        embedding1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        embedding2 = [0.2, 0.3, 0.4, 0.5, 0.6]
        
        similarity = self.service.calculate_similarity(embedding1, embedding2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.9  # 유사한 벡터이므로 높은 유사도
    
    def test_calculate_similarity_empty(self):
        """빈 임베딩 유사도 계산 테스트"""
        similarity = self.service.calculate_similarity([], [])
        assert similarity == 0.0
        
        similarity = self.service.calculate_similarity([0.1, 0.2], [])
        assert similarity == 0.0
    
    def test_calculate_similarity_different_dimensions(self):
        """다른 차원 임베딩 유사도 계산 테스트"""
        embedding1 = [0.1, 0.2, 0.3]
        embedding2 = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        similarity = self.service.calculate_similarity(embedding1, embedding2)
        assert similarity == 0.0
    
    def test_calculate_similarity_zero_vectors(self):
        """영벡터 유사도 계산 테스트"""
        embedding1 = [0.0, 0.0, 0.0]
        embedding2 = [0.1, 0.2, 0.3]
        
        similarity = self.service.calculate_similarity(embedding1, embedding2)
        assert similarity == 0.0
