# Q&A 시스템 업그레이드 가이드

## 🚀 M1 Mac 추천 LLM 모델들

### 1. **Phi-3.5 3.8B** (가장 추천)

```bash
# 다운로드
ollama pull phi3.5:3.8b

# 특징
- 3.8B 파라미터 (매우 가벼움)
- 빠른 응답 속도
- 메모리 사용량: ~2GB
- 한국어 성능 양호
```

### 2. **Llama 3.1 8B** (고성능)

```bash
# 다운로드
ollama pull llama3.1:8b

# 특징
- 8B 파라미터
- 높은 품질의 답변
- 메모리 사용량: ~4GB
- 한국어 성능 우수
```

### 3. **Qwen2.5 7B** (한국어 특화)

```bash
# 다운로드
ollama pull qwen2.5:7b

# 특징
- 7B 파라미터
- 한국어 성능 매우 우수
- 메모리 사용량: ~3.5GB
```

### 4. **SOLAR 10.7B** (최고 품질)

```bash
# 다운로드
ollama pull solar:10.7b

# 특징
- 10.7B 파라미터
- 한국어 성능 최고
- 메모리 사용량: ~5GB
```

## 🔧 Q&A 시스템 구성 요소

### 1. **RAG (Retrieval-Augmented Generation)**

- **검색 (Retrieval)**: 관련 문서 청크 검색
- **생성 (Generation)**: LLM을 사용한 답변 생성
- **결합**: 검색된 정보를 바탕으로 정확한 답변

### 2. **구현된 기능들**

#### A. Q&A 서비스 (`src/qa_service.py`)

```python
# 주요 기능
- ask_question(): 질문에 대한 답변 생성
- ask_with_metadata(): 메타데이터 포함 상세 분석
- generate_answer(): LLM을 사용한 답변 생성
- test_llm_connection(): LLM 연결 테스트
```

#### B. API 엔드포인트

```python
# 새로운 엔드포인트들
POST /api/v1/qa          # Q&A 질문 처리
GET  /api/v1/qa/models   # 사용 가능한 모델 목록
GET  /api/v1/qa/test     # Q&A 서비스 테스트
```

#### C. Pydantic 모델

```python
# 요청/응답 모델
QARequest: 질문 요청 모델
QAResponse: 답변 응답 모델
```

## 📊 현재 시스템 상태

### ✅ **작동하는 부분**

- ✅ **검색 기능**: 관련 문서 청크 검색
- ✅ **LLM 연결**: Phi-3.5 모델 연결
- ✅ **API 엔드포인트**: Q&A API 구현
- ✅ **벡터 데이터베이스**: Qdrant 연동

### ⚠️ **개선 필요한 부분**

- ⚠️ **응답 시간**: LLM 응답이 느림 (타임아웃)
- ⚠️ **모델 선택**: 더 적합한 모델 필요
- ⚠️ **프롬프트 최적화**: 더 나은 프롬프트 필요

## 🎯 사용 방법

### 1. **API 사용**

```bash
# Q&A 질문
curl -X POST "http://localhost:8001/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "운수좋은날에 나오는 등장인물 이름들은?",
    "max_results": 5,
    "max_tokens": 300,
    "include_metadata": true
  }'
```

### 2. **Python 직접 사용**

```python
from src.qa_service import QAService

qa_service = QAService()
result = qa_service.ask_question("김첨지는 어떤 직업을 가지고 있나요?")
print(result['answer'])
```

### 3. **웹 인터페이스**

```
http://localhost:8001/docs  # API 문서
```

## 🔧 성능 최적화 방안

### 1. **모델 최적화**

```python
# 더 가벼운 모델 사용
self.llm_model = "phi3.5:3.8b"  # 현재 사용 중
# 또는
self.llm_model = "gemma3:latest"  # 대안
```

### 2. **프롬프트 최적화**

```python
def _build_prompt(self, query: str, context: List[str]) -> str:
    context_text = "\n\n".join(context)

    prompt = f"""다음은 문서에서 검색된 관련 내용입니다:

{context_text}

위의 내용을 바탕으로 다음 질문에 간결하고 정확하게 답변해주세요:

질문: {query}

답변:"""

    return prompt
```

### 3. **타임아웃 설정**

```python
# 더 긴 타임아웃 설정
timeout=120  # 2분
```

### 4. **캐싱 구현**

```python
# 검색 결과 캐싱
@lru_cache(maxsize=100)
def cached_search(self, query: str, limit: int):
    return self.search_service.search(query, limit)
```

## 📈 성능 모니터링

### 1. **응답 시간 측정**

```python
import time

start_time = time.time()
result = qa_service.ask_question(question)
processing_time = time.time() - start_time
print(f"처리 시간: {processing_time:.2f}초")
```

### 2. **검색 품질 평가**

```python
# 검색 결과 점수 확인
for result in search_results:
    score = result.get('score', 0)
    print(f"검색 점수: {score:.4f}")
```

### 3. **LLM 응답 품질**

```python
# 답변 길이 및 품질 확인
answer = result.get('answer', '')
print(f"답변 길이: {len(answer)}자")
print(f"답변 품질: {'좋음' if len(answer) > 50 else '부족'}")
```

## 🚀 다음 단계

### 1. **즉시 개선 가능**

- [ ] 더 가벼운 모델 테스트 (gemma3)
- [ ] 프롬프트 최적화
- [ ] 타임아웃 설정 조정
- [ ] 에러 핸들링 개선

### 2. **고급 기능**

- [ ] 스트리밍 응답
- [ ] 대화 히스토리
- [ ] 멀티 문서 지원
- [ ] 답변 품질 평가

### 3. **사용자 인터페이스**

- [ ] 웹 채팅 인터페이스
- [ ] 모바일 앱
- [ ] Slack/Discord 봇

## 📝 테스트 결과

### 현재 테스트 결과

```
🔍 질문: 운수좋은날에 나오는 등장인물 이름들은?
📊 검색 결과: 5개 ✅
📋 컨텍스트: 5개 ✅
💡 답변: 타임아웃 ⚠️

🔍 질문: 김첨지는 어떤 직업을 가지고 있나요?
📊 검색 결과: 5개 ✅
📋 컨텍스트: 5개 ✅
💡 답변: 타임아웃 ⚠️
```

### 개선 방향

1. **모델 변경**: Phi-3.5 → Gemma3
2. **타임아웃 증가**: 60초 → 120초
3. **프롬프트 단순화**: 더 간단한 프롬프트 사용
4. **배치 처리**: 여러 질문을 한 번에 처리

이제 Q&A 시스템의 기본 구조가 완성되었습니다! 🎉
