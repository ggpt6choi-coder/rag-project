#!/usr/bin/env python3
"""
간단한 Qdrant 데이터 확인 도구
"""

import requests
import json
from qdrant_client import QdrantClient

def main():
    # Qdrant 클라이언트 연결
    client = QdrantClient("localhost", port=6333)
    
    print("🔍 Qdrant 데이터 확인")
    print("=" * 50)
    
    # 컬렉션 목록
    collections = client.get_collections()
    print(f"📊 컬렉션 수: {len(collections.collections)}")
    
    for collection in collections.collections:
        print(f"\n📋 컬렉션: {collection.name}")
        
        # 컬렉션 정보
        info = client.get_collection(collection.name)
        print(f"  - 상태: {info.status}")
        print(f"  - 포인트 수: {info.points_count}")
        print(f"  - 벡터 차원: {info.config.params.vectors.size}")
        print(f"  - 거리 함수: {info.config.params.vectors.distance}")
        
        # 포인트 데이터 조회
        try:
            points = client.scroll(
                collection_name=collection.name,
                limit=5,
                with_payload=True,
                with_vectors=False
            )
            
            print(f"  - 조회된 포인트: {len(points[0])}")
            
            for i, point in enumerate(points[0], 1):
                print(f"\n    🔹 포인트 {i}:")
                print(f"      ID: {point.id}")
                
                if point.payload:
                    print("      📋 페이로드:")
                    for key, value in point.payload.items():
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"        {key}: {value}")
        
        except Exception as e:
            print(f"    ❌ 포인트 조회 실패: {e}")
    
    # 검색 테스트
    print("\n🔍 검색 테스트")
    print("=" * 50)
    
    try:
        # 간단한 검색 (모든 포인트)
        search_result = client.search(
            collection_name="pdf_documents",
            query_vector=[0.1] * 768,  # 더미 벡터
            limit=3
        )
        
        print(f"📊 검색 결과: {len(search_result)}개")
        
        for i, result in enumerate(search_result, 1):
            print(f"\n🏆 결과 {i}:")
            print(f"  ID: {result.id}")
            print(f"  점수: {result.score:.4f}")
            
            if result.payload:
                print("  📋 내용:")
                for key, value in result.payload.items():
                    if key == 'text' and isinstance(value, str) and len(value) > 200:
                        value = value[:200] + "..."
                    print(f"    {key}: {value}")
    
    except Exception as e:
        print(f"❌ 검색 실패: {e}")

if __name__ == "__main__":
    main()
