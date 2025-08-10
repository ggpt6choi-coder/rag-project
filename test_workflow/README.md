# 📜 실행 스크립트

이 디렉토리에는 프로젝트 테스트 및 실행에 필요한 스크립트들이 포함되어 있습니다.

## 📋 스크립트 목록

### 🧪 테스트 스크립트

- **[test_qa_direct.py](./test_qa_direct.py)** - Q&A 시스템 직접 테스트
- **[test_qa_simple.py](./test_qa_simple.py)** - 간단한 Q&A 테스트

## 🚀 사용법

### Q&A 시스템 테스트

```bash
# Q&A 직접 테스트 (상세한 로그 포함)
python test_workflow/test_qa_direct.py

# 간단한 Q&A 테스트 (기본 기능만)
python test_workflow/test_qa_simple.py
```

### 테스트 환경 설정

```bash
# 환경 변수 설정
export OLLAMA_HOST=http://localhost:11434
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# 테스트 실행
python test_workflow/test_qa_direct.py
```

## 🔧 스크립트별 상세 설명

### test_qa_direct.py

- Q&A 시스템의 전체 기능 테스트
- 상세한 로그 및 디버깅 정보 출력
- 다양한 질문 유형 테스트
- 성능 측정 및 결과 분석

**주요 기능:**

- 벡터 검색 테스트
- RAG 기반 답변 생성 테스트
- 응답 시간 측정
- 결과 품질 평가

### test_qa_simple.py

- 기본적인 Q&A 기능 테스트
- 빠른 기능 확인용
- 최소한의 로그 출력

**주요 기능:**

- 간단한 질의응답 테스트
- 기본 검색 기능 확인
- 연결 상태 확인

## 📊 테스트 시나리오

### 기본 테스트

```bash
# 기본 Q&A 테스트
python test_workflow/test_qa_simple.py

# 상세 테스트
python test_workflow/test_qa_direct.py
```

### 특정 기능 테스트

```bash
# 검색 기능만 테스트
python test_workflow/test_qa_direct.py --search-only

# Q&A 기능만 테스트
python test_workflow/test_qa_direct.py --qa-only
```

### 성능 테스트

```bash
# 성능 측정 테스트
python test_workflow/test_qa_direct.py --performance

# 부하 테스트
python test_workflow/test_qa_direct.py --load-test
```

## 🔍 디버깅 기능

### 상세 로그 출력

```bash
# 디버그 모드로 실행
python test_workflow/test_qa_direct.py --debug

# 상세 로그와 함께 실행
python test_workflow/test_qa_direct.py --verbose
```

### 문제 진단

```bash
# 연결 상태 확인
python test_workflow/test_qa_direct.py --check-connection

# 시스템 상태 확인
python test_workflow/test_qa_direct.py --system-check
```

## 📝 출력 형식

### 테스트 결과

```
✅ Q&A 테스트 성공
- 질문: "PDF에서 어떤 내용이 있나요?"
- 답변: "PDF 문서에는 다음과 같은 내용이 포함되어 있습니다..."
- 응답 시간: 1.2초
- 유사도 점수: 0.85
```

### 오류 메시지

```
❌ Q&A 테스트 실패
- 오류: Ollama 서버에 연결할 수 없습니다
- 해결 방법: Ollama 서버를 시작하세요
```

## 🔧 설정 옵션

### 명령행 옵션

```bash
# 도움말 보기
python test_workflow/test_qa_direct.py --help

# 특정 질문으로 테스트
python test_workflow/test_qa_direct.py --question "PDF 내용은 무엇인가요?"

# 반복 테스트
python test_workflow/test_qa_direct.py --repeat 5
```

### 환경 변수

```bash
# Ollama 설정
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama2

# Qdrant 설정
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# 로깅 설정
export LOG_LEVEL=DEBUG
```

## 🚨 문제 해결

### 일반적인 문제들

1. **Ollama 연결 실패**

   ```bash
   # Ollama 서버 상태 확인
   curl http://localhost:11434/api/tags

   # Ollama 서버 시작
   ollama serve
   ```

2. **Qdrant 연결 실패**

   ```bash
   # Qdrant 서버 상태 확인
   curl http://localhost:6333/collections

   # Docker로 Qdrant 시작
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. **모델이 없는 경우**
   ```bash
   # 필요한 모델 다운로드
   ollama pull llama2
   ollama pull nomic-embed-text
   ```

## 📊 성능 모니터링

### 응답 시간 측정

```bash
# 응답 시간 테스트
python test_workflow/test_qa_direct.py --measure-response-time
```

### 처리량 측정

```bash
# 처리량 테스트
python test_workflow/test_qa_direct.py --throughput-test
```

## 🔄 자동화

### CI/CD 파이프라인용

```bash
# 자동 테스트 (비대화형)
python test_workflow/test_qa_direct.py --non-interactive

# 결과를 JSON으로 출력
python test_workflow/test_qa_direct.py --output-json
```

### 스케줄링

```bash
# cron 작업으로 등록
# 매시간 테스트 실행
0 * * * * cd /path/to/project && python test_workflow/test_qa_direct.py --non-interactive
```

## 📚 추가 문서

자세한 사용법은 다음 문서를 참조하세요:

- **[Q&A_UPGRADE_GUIDE.md](../docs/Q&A_UPGRADE_GUIDE.md)** - Q&A 시스템 상세 가이드
- **[RUNNING.md](../docs/RUNNING.md)** - 전체 시스템 실행 가이드
