#!/usr/bin/env python3
"""
Qdrant 데이터 직접 확인 도구
HTTP API를 사용하여 Qdrant 데이터를 확인
"""

import requests
import json

def check_qdrant_data():
    base_url = "http://localhost:6333"
    
    print("🔍 Qdrant 데이터 확인")
    print("=" * 50)
    
    # 1. 컬렉션 목록 확인
    print("📊 컬렉션 목록:")
    try:
        response = requests.get(f"{base_url}/collections")
        if response.status_code == 200:
            collections = response.json()["result"]["collections"]
            for collection in collections:
                print(f"  - {collection['name']}")
        else:
            print(f"❌ 컬렉션 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print()
    
    # 2. 특정 컬렉션 정보 확인
    collection_name = "pdf_documents"
    print(f"📋 컬렉션 정보: {collection_name}")
    try:
        response = requests.get(f"{base_url}/collections/{collection_name}")
        if response.status_code == 200:
            info = response.json()["result"]
            print(f"  - 상태: {info.get('status', 'N/A')}")
            print(f"  - 포인트 수: {info.get('points_count', 'N/A')}")
            print(f"  - 벡터 차원: {info.get('config', {}).get('params', {}).get('vectors', {}).get('size', 'N/A')}")
            print(f"  - 거리 함수: {info.get('config', {}).get('params', {}).get('vectors', {}).get('distance', 'N/A')}")
        else:
            print(f"❌ 컬렉션 정보 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print()
    
    # 3. 포인트 데이터 조회 (스크롤 방식)
    print(f"🔍 포인트 데이터 조회: {collection_name}")
    try:
        # 스크롤 API 사용
        scroll_url = f"{base_url}/collections/{collection_name}/points/scroll"
        params = {
            "limit": 10,
            "with_payload": True,
            "with_vectors": False
        }
        
        response = requests.post(scroll_url, json=params)
        if response.status_code == 200:
            result = response.json()["result"]
            points = result.get("points", [])
            print(f"  📊 조회된 포인트: {len(points)}개")
            
            for i, point in enumerate(points, 1):
                print(f"\n    🔹 포인트 {i}:")
                print(f"      ID: {point.get('id', 'N/A')}")
                
                payload = point.get('payload', {})
                if payload:
                    print("      📋 페이로드:")
                    for key, value in payload.items():
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"        {key}: {value}")
        else:
            print(f"❌ 포인트 조회 실패: {response.status_code}")
            print(f"응답: {response.text}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print()
    
    # 4. 검색 테스트
    print("🔍 검색 테스트")
    try:
        # 더미 벡터로 검색
        search_url = f"{base_url}/collections/{collection_name}/points/search"
        search_payload = {
            "vector": [0.1] * 768,  # 더미 벡터
            "limit": 5
        }
        
        response = requests.post(search_url, json=search_payload)
        if response.status_code == 200:
            results = response.json()["result"]
            print(f"  📊 검색 결과: {len(results)}개")
            
            for i, result in enumerate(results, 1):
                print(f"\n    🏆 결과 {i}:")
                print(f"      ID: {result.get('id', 'N/A')}")
                print(f"      점수: {result.get('score', 'N/A'):.4f}")
                
                payload = result.get('payload', {})
                if payload:
                    print("      📋 내용:")
                    for key, value in payload.items():
                        if key == 'text' and isinstance(value, str) and len(value) > 200:
                            value = value[:200] + "..."
                        print(f"        {key}: {value}")
        else:
            print(f"❌ 검색 실패: {response.status_code}")
            print(f"응답: {response.text}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print()
    
    # 5. 전체 컬렉션 정보 (JSON)
    print("📄 전체 컬렉션 정보 (JSON):")
    try:
        response = requests.get(f"{base_url}/collections/{collection_name}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    check_qdrant_data()
