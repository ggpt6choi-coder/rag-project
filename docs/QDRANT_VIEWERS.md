# Qdrant 데이터 시각화 도구들

Qdrant 벡터 데이터베이스에 저장된 데이터를 시각적으로 확인하고 분석할 수 있는 다양한 도구들을 소개합니다.

## 🔍 현재 사용 가능한 도구들

### 1. **직접 HTTP API 확인** (가장 안정적)
```bash
# 컬렉션 목록 확인
curl -s http://localhost:6333/collections | jq .

# 특정 컬렉션 정보 확인
curl -s http://localhost:6333/collections/pdf_documents | jq .

# 포인트 데이터 조회
curl -s -X POST "http://localhost:6333/collections/pdf_documents/points/scroll" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "with_payload": true, "with_vectors": false}' | jq .
```

### 2. **Python 스크립트 도구들**

#### A. 간단한 데이터 확인 (`check_qdrant_data.py`)
```bash
# 전체 데이터 확인
python check_qdrant_data.py
```

**기능:**
- 📊 컬렉션 목록 표시
- 📋 컬렉션 상세 정보
- 🔍 포인트 데이터 조회
- 🏆 검색 테스트
- 📄 JSON 형태로 전체 정보 출력

#### B. 고급 뷰어 (`qdrant_viewer.py`)
```bash
# 컬렉션 목록
python qdrant_viewer.py --action collections

# 컬렉션 상세 정보
python qdrant_viewer.py --action info --collection pdf_documents

# 포인트 데이터 조회
python qdrant_viewer.py --action points --collection pdf_documents --limit 5

# 검색 테스트
python qdrant_viewer.py --action search --collection pdf_documents --query "인공지능"
```

**기능:**
- 📊 테이블 형태로 데이터 표시
- 🔍 벡터 검색 기능
- 📋 페이로드 상세 분석
- 🎯 다양한 검색 옵션

## 🌐 웹 기반 도구들

### 1. **Qdrant Web UI** (공식 - 제한적)
```bash
# Docker로 실행 (사용 가능한 경우)
docker run -d --name qdrant-web-ui -p 8080:80 qdrant/qdrant-web-ui
```

### 2. **Jupyter Notebook 기반 뷰어**
```python
# Jupyter에서 실행 가능한 코드
import requests
import pandas as pd
import matplotlib.pyplot as plt
from qdrant_client import QdrantClient

# 데이터 로드
client = QdrantClient("localhost", port=6333)
collections = client.get_collections()

# 데이터프레임으로 변환
data = []
for collection in collections.collections:
    info = client.get_collection(collection.name)
    data.append({
        'name': collection.name,
        'points_count': info.points_count,
        'vector_size': info.config.params.vectors.size,
        'distance': info.config.params.vectors.distance
    })

df = pd.DataFrame(data)
print(df)
```

### 3. **Streamlit 기반 대시보드**
```python
# streamlit_qdrant_viewer.py
import streamlit as st
import requests
import pandas as pd

def main():
    st.title("Qdrant 데이터 뷰어")
    
    # 컬렉션 목록
    response = requests.get("http://localhost:6333/collections")
    collections = response.json()["result"]["collections"]
    
    st.header("컬렉션 목록")
    for collection in collections:
        st.write(f"- {collection['name']}")
    
    # 선택된 컬렉션의 데이터 표시
    selected_collection = st.selectbox("컬렉션 선택", [c['name'] for c in collections])
    
    if selected_collection:
        # 포인트 데이터 조회
        scroll_url = f"http://localhost:6333/collections/{selected_collection}/points/scroll"
        response = requests.post(scroll_url, json={"limit": 100, "with_payload": True})
        
        if response.status_code == 200:
            points = response.json()["result"]["points"]
            st.write(f"총 {len(points)}개 포인트")
            
            # 데이터프레임으로 표시
            data = []
            for point in points:
                data.append({
                    'ID': point['id'],
                    'Text': point['payload'].get('text', '')[:100] + '...',
                    'Document ID': point['payload'].get('document_id', ''),
                    'Chunk Index': point['payload'].get('chunk_index', ''),
                    'Page Number': point['payload'].get('page_number', '')
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df)

if __name__ == "__main__":
    main()
```

## 📊 데이터 분석 도구들

### 1. **벡터 시각화**
```python
# 벡터를 2D로 시각화
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def visualize_vectors(collection_name="pdf_documents"):
    # 벡터 데이터 수집
    response = requests.post(
        f"http://localhost:6333/collections/{collection_name}/points/scroll",
        json={"limit": 1000, "with_vectors": True, "with_payload": True}
    )
    
    points = response.json()["result"]["points"]
    vectors = np.array([point["vector"] for point in points])
    
    # PCA로 2D 변환
    pca = PCA(n_components=2)
    vectors_2d = pca.fit_transform(vectors)
    
    # 시각화
    plt.figure(figsize=(10, 8))
    plt.scatter(vectors_2d[:, 0], vectors_2d[:, 1], alpha=0.6)
    plt.title("Qdrant 벡터 분포 (PCA)")
    plt.xlabel("첫 번째 주성분")
    plt.ylabel("두 번째 주성분")
    plt.show()
```

### 2. **클러스터링 분석**
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def analyze_clusters(collection_name="pdf_documents", n_clusters=5):
    # 벡터 데이터 수집
    response = requests.post(
        f"http://localhost:6333/collections/{collection_name}/points/scroll",
        json={"limit": 1000, "with_vectors": True}
    )
    
    points = response.json()["result"]["points"]
    vectors = np.array([point["vector"] for point in points])
    
    # K-means 클러스터링
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(vectors)
    
    # 실루엣 점수 계산
    silhouette_avg = silhouette_score(vectors, clusters)
    
    print(f"클러스터 수: {n_clusters}")
    print(f"실루엣 점수: {silhouette_avg:.3f}")
    
    # 클러스터별 포인트 수
    for i in range(n_clusters):
        count = np.sum(clusters == i)
        print(f"클러스터 {i}: {count}개 포인트")
```

## 🛠️ 커스텀 도구 개발

### 1. **FastAPI 기반 웹 뷰어**
```python
# web_viewer.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def qdrant_viewer():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Qdrant 데이터 뷰어</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h1>Qdrant 데이터 뷰어</h1>
        <div id="collections"></div>
        <div id="data"></div>
        <script>
            // JavaScript로 데이터 로드 및 시각화
            fetch('/api/collections')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('collections').innerHTML = 
                        '<h2>컬렉션: ' + data.collections.join(', ') + '</h2>';
                });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/api/collections")
async def get_collections():
    response = requests.get("http://localhost:6333/collections")
    return response.json()
```

### 2. **CLI 도구**
```python
# cli_viewer.py
import click
import requests
from tabulate import tabulate

@click.group()
def cli():
    """Qdrant 데이터 뷰어 CLI"""
    pass

@cli.command()
def list_collections():
    """컬렉션 목록 표시"""
    response = requests.get("http://localhost:6333/collections")
    collections = response.json()["result"]["collections"]
    
    table_data = []
    for collection in collections:
        table_data.append([collection["name"]])
    
    print(tabulate(table_data, headers=["컬렉션명"], tablefmt="grid"))

@cli.command()
@click.argument("collection_name")
def show_collection(collection_name):
    """컬렉션 상세 정보 표시"""
    response = requests.get(f"http://localhost:6333/collections/{collection_name}")
    info = response.json()["result"]
    
    print(f"컬렉션: {collection_name}")
    print(f"포인트 수: {info['points_count']}")
    print(f"벡터 차원: {info['config']['params']['vectors']['size']}")

if __name__ == "__main__":
    cli()
```

## 📈 모니터링 도구들

### 1. **실시간 모니터링**
```python
# monitor.py
import time
import requests
from datetime import datetime

def monitor_qdrant():
    while True:
        try:
            response = requests.get("http://localhost:6333/collections")
            collections = response.json()["result"]["collections"]
            
            print(f"[{datetime.now()}] Qdrant 상태:")
            for collection in collections:
                info_response = requests.get(f"http://localhost:6333/collections/{collection['name']}")
                info = info_response.json()["result"]
                print(f"  {collection['name']}: {info['points_count']} 포인트")
            
            time.sleep(30)  # 30초마다 체크
        except Exception as e:
            print(f"모니터링 오류: {e}")
            time.sleep(60)
```

### 2. **성능 분석**
```python
# performance_analyzer.py
import time
import requests
import statistics

def analyze_search_performance(collection_name="pdf_documents", queries=10):
    times = []
    
    for i in range(queries):
        start_time = time.time()
        
        # 검색 요청
        response = requests.post(
            f"http://localhost:6333/collections/{collection_name}/points/search",
            json={"vector": [0.1] * 768, "limit": 5}
        )
        
        end_time = time.time()
        times.append(end_time - start_time)
    
    print(f"평균 검색 시간: {statistics.mean(times):.3f}초")
    print(f"최소 검색 시간: {min(times):.3f}초")
    print(f"최대 검색 시간: {max(times):.3f}초")
```

## 🎯 추천 사용법

### 1. **일반적인 데이터 확인**
```bash
# 가장 간단하고 안정적인 방법
python check_qdrant_data.py
```

### 2. **상세 분석**
```bash
# 고급 기능 사용
python qdrant_viewer.py --action collections
python qdrant_viewer.py --action info --collection pdf_documents
python qdrant_viewer.py --action points --collection pdf_documents --limit 10
```

### 3. **웹 기반 확인**
```bash
# Streamlit 대시보드 (추가 설치 필요)
pip install streamlit
streamlit run streamlit_qdrant_viewer.py
```

### 4. **CLI 도구**
```bash
# CLI 도구 사용
python cli_viewer.py list-collections
python cli_viewer.py show-collection pdf_documents
```

## 🔧 설치 및 설정

### 필요한 패키지
```bash
pip install requests tabulate pandas matplotlib scikit-learn streamlit click
```

### 환경 설정
```bash
# Qdrant 서버 확인
curl http://localhost:6333/collections

# 포트 확인
lsof -i :6333
```

## 📝 사용 팁

1. **데이터 백업**: 중요한 데이터는 정기적으로 백업
2. **성능 모니터링**: 대용량 데이터의 경우 성능 지표 확인
3. **메모리 사용량**: 벡터 데이터는 메모리를 많이 사용하므로 주의
4. **인덱싱 상태**: `indexed_vectors_count` 확인으로 인덱싱 상태 체크

## 🚀 고급 기능

### 1. **벡터 유사도 분석**
```python
def analyze_similarity(collection_name="pdf_documents"):
    # 모든 벡터 간 유사도 계산
    response = requests.post(
        f"http://localhost:6333/collections/{collection_name}/points/scroll",
        json={"limit": 100, "with_vectors": True}
    )
    
    points = response.json()["result"]["points"]
    vectors = np.array([point["vector"] for point in points])
    
    # 코사인 유사도 계산
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(vectors)
    
    print(f"평균 유사도: {np.mean(similarity_matrix):.3f}")
    print(f"최대 유사도: {np.max(similarity_matrix):.3f}")
    print(f"최소 유사도: {np.min(similarity_matrix):.3f}")
```

### 2. **데이터 품질 분석**
```python
def analyze_data_quality(collection_name="pdf_documents"):
    response = requests.post(
        f"http://localhost:6333/collections/{collection_name}/points/scroll",
        json={"limit": 1000, "with_payload": True}
    )
    
    points = response.json()["result"]["points"]
    
    # 텍스트 길이 분석
    text_lengths = [len(point["payload"].get("text", "")) for point in points]
    
    print(f"평균 텍스트 길이: {statistics.mean(text_lengths):.1f}")
    print(f"최소 텍스트 길이: {min(text_lengths)}")
    print(f"최대 텍스트 길이: {max(text_lengths)}")
```

이러한 도구들을 활용하여 Qdrant에 저장된 벡터 데이터를 효과적으로 확인하고 분석할 수 있습니다! 🎉
