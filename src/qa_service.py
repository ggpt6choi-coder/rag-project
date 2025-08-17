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
from src.qdrant_manager import QdrantManager


class QAService:
    def __init__(self):
        """Q&A 서비스 초기화"""
        self.ollama_host = config.OLLAMA_HOST
        self.llm_model = "gemma3:latest"  # Gemma3 모델 사용
        self.search_service = SearchService()
        self.embedding_service = EmbeddingService()
        
        logger.info(f"Q&A 서비스 초기화: {self.llm_model}")
    
    def generate_answer(self, query: str, context: List[str], max_tokens: int = 500, history: list = None) -> str:
        """LLM을 사용하여 답변 생성 (이전 대화 history 반영)"""
        try:
            # 프롬프트 구성
            prompt = self._build_prompt(query, context, history)
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
    
    def _build_prompt(self, query: str, context: List[str], history: list = None) -> str:
        """RAG 프롬프트 구성 - 상황별 최적화 버전 (표/리스트/근거/출처 등)"""
        import re
        filtered_context = []
        context_types = []
        # 표/리스트/일반 텍스트 구분 및 필터링
        for block in context:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                context_types.append("text")
                filtered_context.append(block)
                continue
            if lines[0].startswith("|") and lines[0].endswith("|"):
                context_types.append("table")
                filtered_context.append(block)
            elif all(l.startswith("-") or l[0].isdigit() for l in lines):
                context_types.append("list")
                filtered_context.append(block)
            else:
                context_types.append("text")
                filtered_context.append(block)
        # 예시: '진학수 40명 이상' 패턴 감지 및 표 필터링
        m = re.search(r"([가-힣A-Za-z0-9_]+)\s*([0-9]+)명\s*이상", query)
        if m:
            col_name = m.group(1)
            min_val = int(m.group(2))
            new_context = []
            for block, ctype in zip(filtered_context, context_types):
                if ctype != "table":
                    new_context.append(block)
                    continue
                lines = [l.strip() for l in block.splitlines() if l.strip()]
                header = [h.strip() for h in lines[0].strip("|").split("|")]
                try:
                    col_idx = header.index(col_name)
                except ValueError:
                    new_context.append(block)
                    continue
                filtered_rows = [lines[0]]
                for row in lines[1:]:
                    cells = [c.strip() for c in row.strip("|").split("|")]
                    try:
                        if int(cells[col_idx]) >= min_val:
                            filtered_rows.append(row)
                    except:
                        continue
                if len(filtered_rows) > 1:
                    new_context.append("\n".join(filtered_rows))
            filtered_context = new_context
        # 상황별 프롬프트 분기 (자연스러운 상담원 스타일 강조)
        context_text = "\n\n".join(filtered_context)
        style_guide = (
            "- 답변은 표/리스트/데이터 복사 느낌이 아니라, 실제 상담원이 안내하는 것처럼 자연스럽고 친근하게 작성해 주세요.\n"
            "- 필요시 예시, 추가 설명도 포함해 주세요.\n"
            "- 표가 포함된 경우 마크다운 표 형식으로, 리스트는 번호 또는 기호로, 일반 텍스트는 자연스럽게 요약해 주세요.\n"
            "- 답변에는 반드시 관련 근거(출처, 문서명, 시트명, 행/열, 페이지 등)를 명확히 표기하세요."
        )
        # history(이전 대화)가 있으면 프롬프트 상단에 추가
        history_text = ""
        if history and isinstance(history, list) and len(history) > 0:
            history_lines = []
            for turn in history:
                q = turn.get("question") or turn.get("content") or turn.get("user") or ""
                a = turn.get("answer") or turn.get("response") or turn.get("assistant") or ""
                if q:
                    history_lines.append(f"이전 질문: {q}")
                if a:
                    history_lines.append(f"이전 답변: {a}")
            if history_lines:
                history_text = "\n".join(history_lines) + "\n"
        prompt = f"""{history_text}아래 참고 내용을 바탕으로 사용자의 질문에 대해 자연스럽고 친근하게 답변해 주세요.\n{style_guide}\n\n[참고 내용]\n{context_text}\n\n[질문]\n{query}\n[답변]"""
        return prompt
    
    def ask_question(self, question: str, collection_name: str = "pdf_documents", 
                    max_results: int = 5, max_tokens: int = 500, document_id: str = None, history=None) -> Dict[str, Any]:
        """질문에 대한 답변 생성 (출처/근거 정보 포함)"""
        import re
        try:
            logger.info(f"질문 처리 시작: {question}")
            # 1. 관련 문서 검색
            search_service = self.search_service
            if collection_name:
                search_service = SearchService(QdrantManager(collection_name=collection_name), self.embedding_service)
            search_results = search_service.search(
                query=question,
                limit=max_results * 3,  # 충분히 넉넉히 받아서 필터링
                document_id=document_id
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

            # 1-1. 쿼리에서 '필드명:값' 패턴 추출 (예: TR명: AB0087R, 담당자: 이민호)
            field_match = re.findall(r"([\w가-힣]+)\s*[:：]\s*([\w가-힣0-9]+)", question)
            field_filters = {k.strip(): v.strip() for k, v in field_match} if field_match else {}

            # 1-1b. 쿼리에서 고유값(영문+숫자+영문, 숫자 등) 패턴도 추출 (예: AB0087R)
            value_patterns = re.findall(r"[A-Z]{2}\d{4,5}[A-Z]", question)  # 예: AB0087R
            value_patterns += re.findall(r"\d{5,}", question)  # 5자리 이상 숫자도 포함
            # 중복 제거
            value_patterns = list(set(value_patterns))

            # 1-2. 동적 필드 매칭 (컬럼명 하드코딩 없이)
            filtered_results = search_results
            # 1) 필드명:값 패턴이 있으면 해당 필드 우선
            if field_filters:
                def is_exact_match(res):
                    meta = res.get("metadata", {})
                    for k, v in field_filters.items():
                        if k in meta and str(meta[k]).strip() == v:
                            continue
                        elif k in res and str(res[k]).strip() == v:
                            continue
                        else:
                            return False
                    return True
                exact_matches = [r for r in search_results if is_exact_match(r)]
                if exact_matches:
                    filtered_results = exact_matches
                else:
                    filtered_results = search_results
            # 2) 필드명:값 패턴이 없고, 고유값 패턴이 있으면 모든 필드에 대해 동적 매칭
            elif value_patterns:
                def has_value_any_field(res):
                    meta = res.get("metadata", {})
                    for v in value_patterns:
                        # 메타데이터의 모든 필드에 대해 값이 정확히 일치하는지 검사
                        if any(str(val).strip() == v for val in meta.values()):
                            return True
                        # payload에도 혹시 있을 수 있음
                        if any(str(val).strip() == v for val in res.values()):
                            return True
                    return False
                exact_matches = [r for r in search_results if has_value_any_field(r)]
                if exact_matches:
                    filtered_results = exact_matches
                else:
                    filtered_results = search_results
            # 2. 검색된 텍스트 추출 및 출처 메타데이터 수집 (정확 매칭 결과만 context로 사용)
            context_texts = []
            sources = []
            for result in filtered_results[:max_results]:
                text = result.get("text", "")
                if text:
                    context_texts.append(text)
                    meta_dict = {}
                    for k in ["document_id", "title", "sheet", "row", "page_number", "chunk_index"]:
                        if "metadata" in result and k in result["metadata"]:
                            meta_dict[k] = result["metadata"][k]
                        elif k in result:
                            meta_dict[k] = result[k]
                    # 동적 필드도 근거에 추가
                    if "metadata" in result:
                        for fk in field_filters.keys():
                            if fk in result["metadata"]:
                                meta_dict[fk] = result["metadata"][fk]
                    if meta_dict:
                        sources.append(meta_dict)
            # 3. 정확 매칭 결과가 없으면 답변 자체를 정보 없음으로 제한
            if not context_texts:
                return {
                    "question": question,
                    "answer": "죄송합니다. 해당 정보를 찾을 수 없습니다.",
                    "sources": [],
                    "search_results": [],
                    "context_count": 0
                }
            # 4. LLM을 사용한 답변 생성
            answer = self.generate_answer(question, context_texts, max_tokens, history)
            # 5. 답변에 출처 추가 (자연어 근거)
            if sources:
                readable_sources = []
                for i, src in enumerate(sources):
                    # 해당 청크의 텍스트 일부 추출
                    chunk_text = filtered_results[i].get("text", "")
                    chunk_preview = chunk_text.strip().replace("\n", " ")[:80] + ("..." if len(chunk_text) > 80 else "")
                    doc_name = src.get("title") or src.get("document_id", "문서")
                    page = src.get("page_number")
                    sheet = src.get("sheet")
                    # 자연어 근거 문장 생성
                    meta_parts = []
                    if doc_name:
                        meta_parts.append(f"문서: {doc_name}")
                    if sheet:
                        meta_parts.append(f"시트: {sheet}")
                    if page is not None:
                        meta_parts.append(f"페이지: {page}")
                    # 동적 필드 근거 추가
                    for fk in field_filters.keys():
                        if fk in src:
                            meta_parts.append(f"{fk}: {src[fk]}")
                    readable = f"- \"{chunk_preview}\" ({', '.join(meta_parts)})"
                    readable_sources.append(readable)
                answer += f"\n\n📄 관련 출처:\n" + "\n".join(readable_sources)
            return {
                "question": question,
                "answer": answer,
                "sources": sources,
                "search_results": filtered_results[:max_results],
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
    
    def ask_with_metadata(self, question: str, collection_name: str = "pdf_documents", max_results: int = 5, max_tokens: int = 500, document_id: str = None) -> Dict[str, Any]:
        """메타데이터를 포함한 상세한 질문 처리"""
        try:
            # 기본 질문 처리
            result = self.ask_question(question, collection_name, max_results=max_results, max_tokens=max_tokens, document_id=document_id)
            
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
