"""
Q&A 서비스 - RAG (Retrieval-Augmented Generation)
검색된 관련 문서를 바탕으로 LLM이 답변을 생성하는 서비스
"""

import requests
import json
from typing import List, Dict, Any, Optional
from loguru import logger
from src.config import config
from src.search_service import SearchService
from src.embedding_service import EmbeddingService


class QAService:
    def __init__(self):
        """Q&A 서비스 초기화"""
        self.ollama_host = config.OLLAMA_HOST
        self.llm_model = "gemma3:latest"  # Gemma3 모델 사용
        self.search_service = SearchService()
        self.embedding_service = EmbeddingService()
        
        logger.info(f"Q&A 서비스 초기화: {self.llm_model}")
    
    def generate_answer(self, query: str, context: List[str], max_tokens: int = 500) -> str:
        """LLM을 사용하여 답변 생성"""
        try:
            # 프롬프트 구성
            prompt = self._build_prompt(query, context)
            
            # Ollama API 호출
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": max_tokens
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                logger.info(f"답변 생성 완료: {len(answer)}자")
                return answer
            else:
                logger.error(f"LLM API 오류: {response.status_code}")
                return "죄송합니다. 답변을 생성하는 중 오류가 발생했습니다."
                
        except Exception as e:
            logger.error(f"답변 생성 중 오류: {e}")
            return "죄송합니다. 답변을 생성하는 중 오류가 발생했습니다."
    
    def _build_prompt(self, query: str, context: List[str]) -> str:
        """RAG 프롬프트 구성 - 최적화된 버전"""
        context_text = "\n\n".join(context)
        
        prompt = f"""다음은 문서에서 검색된 관련 내용입니다:

{context_text}

위의 내용을 바탕으로 다음 질문에 간결하고 정확하게 답변해주세요.
답변은 한국어로 작성하고, 문서에 있는 정보만을 사용하세요.

질문: {query}

답변:"""
        
        return prompt
    
    def ask_question(self, question: str, collection_name: str = "pdf_documents", 
                    max_results: int = 5, max_tokens: int = 500) -> Dict[str, Any]:
        """질문에 대한 답변 생성"""
        try:
            logger.info(f"질문 처리 시작: {question}")
            
            # 1. 관련 문서 검색
            search_results = self.search_service.search(
                query=question,
                limit=max_results
            )
            
            logger.info(f"검색 결과: {len(search_results)}개")
            
            if not search_results:
                logger.warning(f"검색 결과 없음: {question}")
                return {
                    "question": question,
                    "answer": "죄송합니다. 관련된 정보를 찾을 수 없습니다.",
                    "sources": [],
                    "search_results": []
                }
            
            # 2. 검색된 텍스트 추출
            context_texts = []
            sources = []
            
            for result in search_results:
                text = result.get("text", "")
                if text:
                    context_texts.append(text)
                    sources.append({
                        "id": result.get("id"),
                        "score": result.get("score"),
                        "document_id": result.get("document_id"),
                        "chunk_index": result.get("chunk_index")
                    })
            
            # 3. LLM을 사용한 답변 생성
            answer = self.generate_answer(question, context_texts, max_tokens)
            
            return {
                "question": question,
                "answer": answer,
                "sources": sources,
                "search_results": search_results,
                "context_count": len(context_texts)
            }
            
        except Exception as e:
            logger.error(f"질문 처리 중 오류: {e}")
            return {
                "question": question,
                "answer": "죄송합니다. 질문을 처리하는 중 오류가 발생했습니다.",
                "sources": [],
                "search_results": [],
                "error": str(e)
            }
    
    def ask_with_metadata(self, question: str, collection_name: str = "pdf_documents") -> Dict[str, Any]:
        """메타데이터를 포함한 상세한 질문 처리"""
        try:
            # 기본 질문 처리
            result = self.ask_question(question, collection_name)
            
            # 추가 메타데이터 분석
            if result.get("search_results"):
                # 문서 정보 수집
                documents = {}
                for search_result in result["search_results"]:
                    doc_id = search_result.get("document_id")
                    if doc_id not in documents:
                        documents[doc_id] = {
                            "document_id": doc_id,
                            "metadata": search_result.get("metadata", {}),
                            "chunks_count": 0
                        }
                    documents[doc_id]["chunks_count"] += 1
                
                result["documents"] = list(documents.values())
                
                # 통계 정보
                result["stats"] = {
                    "total_results": len(result["search_results"]),
                    "unique_documents": len(documents),
                    "avg_score": sum(r.get("score", 0) for r in result["search_results"]) / len(result["search_results"]) if result["search_results"] else 0
                }
            
            return result
            
        except Exception as e:
            logger.error(f"메타데이터 포함 질문 처리 중 오류: {e}")
            return {
                "question": question,
                "answer": "죄송합니다. 질문을 처리하는 중 오류가 발생했습니다.",
                "error": str(e)
            }
    
    def test_llm_connection(self) -> bool:
        """LLM 연결 테스트"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": "안녕하세요. 간단한 테스트입니다.",
                    "stream": False,
                    "options": {
                        "max_tokens": 10
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                logger.info("LLM 연결 테스트 성공")
                return True
            else:
                logger.error(f"LLM 연결 테스트 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"LLM 연결 테스트 중 오류: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """사용 가능한 모델 목록 조회"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                return []
        except Exception as e:
            logger.error(f"모델 목록 조회 중 오류: {e}")
            return []


# 테스트 함수
def test_qa_service():
    """Q&A 서비스 테스트"""
    qa_service = QAService()
    
    # LLM 연결 테스트
    if not qa_service.test_llm_connection():
        print("❌ LLM 연결 실패")
        return
    
    print("✅ LLM 연결 성공")
    
    # 테스트 질문들
    test_questions = [
        "운수좋은날에 나오는 등장인물 이름들은?",
        "김첨지는 어떤 직업을 가지고 있나요?",
        "치삼은 어떤 인물인가요?",
        "개똥이는 누구인가요?",
        "이 소설의 배경은 어디인가요?"
    ]
    
    for question in test_questions:
        print(f"\n🔍 질문: {question}")
        result = qa_service.ask_question(question)
        print(f"💡 답변: {result['answer']}")
        print(f"📊 검색 결과 수: {len(result['search_results'])}")


if __name__ == "__main__":
    test_qa_service()
