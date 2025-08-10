#!/usr/bin/env python3
"""
Q&A 서비스 직접 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qa_service import QAService

def test_qa_direct():
    """Q&A 서비스 직접 테스트"""
    
    print("🔍 Q&A 서비스 직접 테스트")
    print("=" * 50)
    
    # Q&A 서비스 초기화
    qa_service = QAService()
    
    # LLM 연결 테스트
    print("🤖 LLM 연결 테스트...")
    if not qa_service.test_llm_connection():
        print("❌ LLM 연결 실패")
        return
    
    print("✅ LLM 연결 성공")
    
    # 테스트 질문
    test_questions = [
        "운수좋은날에 나오는 등장인물 이름들은?",
        "김첨지는 어떤 직업을 가지고 있나요?",
        "치삼은 어떤 인물인가요?"
    ]
    
    for question in test_questions:
        print(f"\n🔍 질문: {question}")
        
        try:
            result = qa_service.ask_question(question, max_results=5)
            
            print(f"💡 답변: {result.get('answer', '')}")
            print(f"📊 검색 결과: {len(result.get('search_results', []))}개")
            print(f"📋 컨텍스트: {result.get('context_count', 0)}개")
            
            if result.get('search_results'):
                print("🔍 검색된 텍스트 샘플:")
                for i, search_result in enumerate(result['search_results'][:2]):
                    text = search_result.get('text', '')[:100]
                    print(f"  {i+1}. {text}...")
            
        except Exception as e:
            print(f"❌ 오류: {e}")

if __name__ == "__main__":
    test_qa_direct()
