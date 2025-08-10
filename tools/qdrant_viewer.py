#!/usr/bin/env python3
"""
Qdrant 데이터 시각화 도구
Qdrant에 저장된 벡터 데이터를 확인하고 분석할 수 있는 스크립트
"""

import json
import requests
from typing import Dict, List, Any
from tabulate import tabulate
import argparse
import sys

class QdrantViewer:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.base_url = f"http://{host}:{port}"
        
    def get_collections(self) -> List[Dict]:
        """컬렉션 목록 조회"""
        try:
            response = requests.get(f"{self.base_url}/collections")
            response.raise_for_status()
            return response.json()["result"]["collections"]
        except Exception as e:
            print(f"❌ 컬렉션 조회 실패: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict:
        """컬렉션 상세 정보 조회"""
        try:
            response = requests.get(f"{self.base_url}/collections/{collection_name}")
            response.raise_for_status()
            return response.json()["result"]
        except Exception as e:
            print(f"❌ 컬렉션 정보 조회 실패: {e}")
            return {}
    
    def get_points(self, collection_name: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """포인트 데이터 조회"""
        try:
            url = f"{self.base_url}/collections/{collection_name}/points"
            params = {"limit": limit, "offset": offset}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()["result"]["points"]
        except Exception as e:
            print(f"❌ 포인트 조회 실패: {e}")
            return []
    
    def search_points(self, collection_name: str, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """벡터 검색"""
        try:
            url = f"{self.base_url}/collections/{collection_name}/points/search"
            payload = {
                "vector": query_vector,
                "limit": limit
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()["result"]
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []
    
    def display_collections(self):
        """컬렉션 목록 표시"""
        print("📊 Qdrant 컬렉션 목록")
        print("=" * 50)
        
        collections = self.get_collections()
        if not collections:
            print("❌ 컬렉션이 없습니다.")
            return
        
        table_data = []
        for collection in collections:
            info = self.get_collection_info(collection["name"])
            table_data.append([
                collection["name"],
                info.get("vectors_count", "N/A"),
                info.get("config", {}).get("params", {}).get("vectors", {}).get("size", "N/A"),
                info.get("config", {}).get("params", {}).get("vectors", {}).get("distance", "N/A")
            ])
        
        headers = ["컬렉션명", "벡터 수", "차원", "거리 함수"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def display_collection_details(self, collection_name: str):
        """컬렉션 상세 정보 표시"""
        print(f"📋 컬렉션 상세 정보: {collection_name}")
        print("=" * 50)
        
        info = self.get_collection_info(collection_name)
        if not info:
            print("❌ 컬렉션을 찾을 수 없습니다.")
            return
        
        print(f"📊 벡터 수: {info.get('vectors_count', 'N/A')}")
        print(f"📏 차원: {info.get('config', {}).get('params', {}).get('vectors', {}).get('size', 'N/A')}")
        print(f"📐 거리 함수: {info.get('config', {}).get('params', {}).get('vectors', {}).get('distance', 'N/A')}")
        print(f"🔧 최적화 상태: {info.get('optimizer_status', 'N/A')}")
        
        # 페이로드 스키마 표시
        payload_schema = info.get('config', {}).get('params', {}).get('on_disk_payload', {})
        if payload_schema and isinstance(payload_schema, dict):
            print("\n📋 페이로드 스키마:")
            for field, schema in payload_schema.items():
                print(f"  - {field}: {schema.get('type', 'unknown')}")
        elif payload_schema:
            print(f"\n📋 페이로드 설정: {payload_schema}")
    
    def display_points(self, collection_name: str, limit: int = 10, offset: int = 0):
        """포인트 데이터 표시"""
        print(f"🔍 포인트 데이터: {collection_name}")
        print("=" * 50)
        
        points = self.get_points(collection_name, limit, offset)
        if not points:
            print("❌ 포인트가 없습니다.")
            return
        
        print(f"📊 총 {len(points)}개 포인트 (limit={limit}, offset={offset})")
        print()
        
        for i, point in enumerate(points, 1):
            print(f"🔹 포인트 {i}:")
            print(f"  ID: {point.get('id', 'N/A')}")
            print(f"  벡터 차원: {len(point.get('vector', []))}")
            
            # 페이로드 정보 표시
            payload = point.get('payload', {})
            if payload:
                print("  📋 페이로드:")
                for key, value in payload.items():
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"    {key}: {value}")
            print()
    
    def display_search_results(self, collection_name: str, query_text: str, embedding_service):
        """검색 결과 표시"""
        print(f"🔍 검색 결과: '{query_text}'")
        print("=" * 50)
        
        # 쿼리 텍스트를 벡터로 변환
        try:
            query_vector = embedding_service.embed_text(query_text)
        except Exception as e:
            print(f"❌ 임베딩 생성 실패: {e}")
            return
        
        results = self.search_points(collection_name, query_vector, limit=5)
        if not results:
            print("❌ 검색 결과가 없습니다.")
            return
        
        print(f"📊 {len(results)}개 결과 발견")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"🏆 결과 {i} (점수: {result.get('score', 'N/A'):.4f}):")
            print(f"  ID: {result.get('id', 'N/A')}")
            
            payload = result.get('payload', {})
            if payload:
                print("  📋 내용:")
                for key, value in payload.items():
                    if key == 'text' and isinstance(value, str) and len(value) > 200:
                        value = value[:200] + "..."
                    print(f"    {key}: {value}")
            print()

def main():
    parser = argparse.ArgumentParser(description="Qdrant 데이터 시각화 도구")
    parser.add_argument("--host", default="localhost", help="Qdrant 호스트")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant 포트")
    parser.add_argument("--collection", help="특정 컬렉션 이름")
    parser.add_argument("--action", choices=["collections", "info", "points", "search"], 
                       default="collections", help="실행할 액션")
    parser.add_argument("--limit", type=int, default=10, help="조회할 포인트 수")
    parser.add_argument("--offset", type=int, default=0, help="오프셋")
    parser.add_argument("--query", help="검색 쿼리 (search 액션용)")
    
    args = parser.parse_args()
    
    viewer = QdrantViewer(args.host, args.port)
    
    if args.action == "collections":
        viewer.display_collections()
    
    elif args.action == "info":
        if not args.collection:
            print("❌ --collection 옵션이 필요합니다.")
            sys.exit(1)
        viewer.display_collection_details(args.collection)
    
    elif args.action == "points":
        if not args.collection:
            print("❌ --collection 옵션이 필요합니다.")
            sys.exit(1)
        viewer.display_points(args.collection, args.limit, args.offset)
    
    elif args.action == "search":
        if not args.collection:
            print("❌ --collection 옵션이 필요합니다.")
            sys.exit(1)
        if not args.query:
            print("❌ --query 옵션이 필요합니다.")
            sys.exit(1)
        
        # 임베딩 서비스 임포트
        try:
            from src.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            viewer.display_search_results(args.collection, args.query, embedding_service)
        except ImportError:
            print("❌ 임베딩 서비스를 임포트할 수 없습니다. src.embedding_service를 확인하세요.")
            sys.exit(1)

if __name__ == "__main__":
    main()
