#!/usr/bin/env python3
"""
간단한 Q&A 테스트
"""

import requests
import json

def test_qa_api():
    """Q&A API 테스트"""
    
    # 1. Q&A 서비스 테스트
    print("🔍 Q&A 서비스 테스트...")
    response = requests.get("http://localhost:8001/api/v1/qa/test")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 상태: {result.get('status')}")
        print(f"🤖 모델: {result.get('llm_model')}")
    else:
        print(f"❌ 테스트 실패: {response.status_code}")
        return
    
    # 2. 사용 가능한 모델 확인
    print("\n📋 사용 가능한 모델...")
    response = requests.get("http://localhost:8001/api/v1/qa/models")
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"✅ 모델 수: {len(models)}")
        for model in models[:5]:  # 처음 5개만 표시
            print(f"  - {model}")
    else:
        print(f"❌ 모델 조회 실패: {response.status_code}")
    
    # 3. Q&A 질문 테스트
    print("\n💬 Q&A 질문 테스트...")
    
    test_questions = [
        "운수좋은날에 나오는 등장인물 이름들은?",
        "김첨지는 어떤 직업을 가지고 있나요?",
        "치삼은 어떤 인물인가요?"
    ]
    
    for question in test_questions:
        print(f"\n🔍 질문: {question}")
        
        payload = {
            "question": question,
            "max_results": 5,
            "max_tokens": 300,
            "include_metadata": True
        }
        
        response = requests.post(
            "http://localhost:8001/api/v1/qa",
            json=payload,
            timeout=120  # 2분 타임아웃
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"💡 답변: {result.get('answer', '')}")
            print(f"📊 검색 결과: {len(result.get('search_results', []))}개")
            processing_time = result.get('processing_time')
            if processing_time is not None:
                print(f"⏱️ 처리 시간: {processing_time:.2f}초")
            else:
                print("⏱️ 처리 시간: 알 수 없음")
        else:
            print(f"❌ 질문 처리 실패: {response.status_code}")
            print(f"오류: {response.text}")

if __name__ == "__main__":
    test_qa_api()
