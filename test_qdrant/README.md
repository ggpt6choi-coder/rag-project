# 📝 예제 코드

이 디렉토리에는 프로젝트 사용법을 보여주는 예제 코드들이 포함되어 있습니다.

## 📋 예제 목록

### 🔧 기본 사용 예제

- **[example.py](./example.py)** - 프로젝트의 기본 사용법 예제

## 🚀 사용법

### 기본 예제 실행

```bash
# 기본 예제 실행
python test_qdrant/example.py

# 특정 기능만 테스트
python test_qdrant/example.py --pdf-only
python test_qdrant/example.py --search-only
```

## 🔧 예제별 상세 설명

### example.py

- 프로젝트의 모든 주요 기능을 보여주는 종합 예제
- PDF 처리부터 Q&A까지 전체 워크플로우 시연
- 실제 사용 시나리오 기반 예제

**주요 기능:**

- PDF 파일 업로드 및 처리
- 텍스트 청킹 및 임베딩 생성
- 벡터 데이터베이스 저장
- 검색 및 Q&A 기능 사용

## 📊 예제 시나리오

### 1. PDF 처리 예제

```python
# PDF 파일 처리
pdf_path = "data/uploads/sample.pdf"
text = processor.extract_text(pdf_path)
chunks = chunker.chunk_text(text)
embeddings = embedding_service.embed_chunks(chunks)
qdrant_manager.store_vectors(embeddings, metadata)
```

### 2. 검색 예제

```python
# 벡터 검색
search_service = SearchService()
results = search_service.search("검색어", limit=10)
for result in results:
    print(f"유사도: {result.score}, 내용: {result.content}")
```

## 🔍 예제 실행 옵션

### 기본 실행

```bash
# 전체 예제 실행
python test_qdrant/example.py
```

### 단계별 실행

```bash
# PDF 처리만
python test_qdrant/example.py --step pdf

# 검색만
python test_qdrant/example.py --step search
```

### 디버그 모드

```bash
# 상세 로그와 함께 실행
python test_qdrant/example.py --debug

# 단계별 진행 상황 표시
python test_qdrant/example.py --verbose
```

## 📝 예제 출력

### 성공적인 실행

```
✅ PDF 처리 완료
- 파일: sample.pdf
- 추출된 텍스트: 1,234 단어
- 생성된 청크: 15개
- 임베딩 생성: 완료
- 벡터 저장: 완료

✅ 검색 테스트 완료
- 검색어: "인공지능"
- 결과 수: 5개
- 최고 유사도: 0.92
```

### 오류 처리

```
❌ PDF 처리 실패
- 오류: 파일을 찾을 수 없습니다
- 해결: data/uploads/sample.pdf 파일을 확인하세요

❌ 검색 실패
- 오류: Qdrant 서버에 연결할 수 없습니다
- 해결: Qdrant 서버를 시작하세요
```

## 🔧 설정

### 환경 설정

```bash
# 환경 변수 설정
export OLLAMA_HOST=http://localhost:11434
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# 예제 실행
python test_qdrant/example.py
```

### 샘플 데이터 준비

```bash
# 샘플 PDF 파일 준비
mkdir -p data/samples
# PDF 파일을 data/samples/ 디렉토리에 복사
```

## 🚨 문제 해결

### 일반적인 문제들

1. **샘플 파일이 없는 경우**

   ```bash
   # 샘플 PDF 파일 생성 (테스트용)
   echo "This is a sample PDF content for testing." > data/samples/sample.txt
   ```

2. **서비스 연결 실패**

   ```bash
   # Ollama 서버 시작
   ollama serve

   # Qdrant 서버 시작
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. **모델이 없는 경우**
   ```bash
   # 필요한 모델 다운로드
   ollama pull nomic-embed-text
   ollama pull llama2
   ```

## 📊 성능 테스트

### 처리 시간 측정

```bash
# 처리 시간 측정
python test_qdrant/example.py --measure-time
```

### 메모리 사용량 측정

```bash
# 메모리 사용량 측정
python test_qdrant/example.py --measure-memory
```

## 📚 추가 문서

자세한 사용법은 다음 문서를 참조하세요:

- **[README.md](../docs/README.md)** - 프로젝트 상세 설명
- **[RUNNING.md](../docs/RUNNING.md)** - 실행 가이드
