# PDF to Qdrant Vector Database - 실행 및 테스트 가이드

## 🚀 빠른 시작

이 가이드는 PDF 문서를 청킹하여 Qdrant 벡터 데이터베이스에 저장하는 시스템을 설치하고 실행하는 방법을 설명합니다.

## 📋 사전 요구사항

### 1. 시스템 요구사항

- **Python 3.9+** 설치
- **Docker** 설치 (Qdrant 실행용)
- **Git** 설치
- **최소 4GB RAM** (Ollama 모델 실행용)

### 2. 외부 서비스 설치

#### Ollama 설치

```bash
# macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# https://ollama.ai/download 에서 다운로드
```

#### Docker 설치

```bash
# macOS
brew install --cask docker

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

## 🛠️ 설치 및 설정

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd DigitalCompetition
```

### 2. 자동 설정 (권장)

```bash
# 실행 권한 부여
chmod +x setup.sh

# 자동 설정 실행
./setup.sh
```

### 3. 수동 설정

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 파일 생성
cp env.example .env

# 필요한 디렉토리 생성
mkdir -p data/uploads data/samples logs
```

### 4. 환경 변수 설정

`.env` 파일을 편집하여 설정값을 확인/수정하세요:

```env
# Qdrant 설정
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=pdf_documents

# Ollama 설정
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text

# 텍스트 청킹 설정
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# 애플리케이션 설정
APP_HOST=0.0.0.0
APP_PORT=8001
DEBUG=True
```

## 🔧 외부 서비스 실행

### 1. Ollama 모델 다운로드

```bash
# 임베딩 모델 다운로드
ollama pull nomic-embed-text

# 모델 확인
ollama list
```

### 2. Qdrant 실행

```bash
# Docker로 Qdrant 실행
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# 실행 확인
curl http://localhost:6333/collections
```

## 🚀 애플리케이션 실행

### 1. 서버 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 실행
PYTHONPATH=. python src/main.py
```

또는

```bash
# FastAPI 서버로 실행
source venv/bin/activate
PYTHONPATH=. uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### 2. 실행 확인

```bash
# 서버 상태 확인
curl http://localhost:8001/api/v1/health

# API 문서 확인 (웹 브라우저에서)
open http://localhost:8001/docs
```

## 🧪 테스트 및 사용법

### 1. 기본 테스트

```bash
# 예제 실행
source venv/bin/activate
python example.py
```

### 2. API 테스트

#### 헬스 체크

```bash
curl http://localhost:8001/api/v1/health
```

#### 검색 테스트

```bash
# 검색 요청
curl -X POST "http://localhost:8001/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "인공지능", "limit": 3}'
```

#### 문서 목록 확인

```bash
curl http://localhost:8001/api/v1/documents
```

### 3. 웹 인터페이스 사용

브라우저에서 다음 URL에 접속하세요:

- **API 문서**: http://localhost:8001/docs
- **대안 문서**: http://localhost:8001/redoc

## 📁 프로젝트 구조

```
DigitalCompetition/
├── 📄 PRD.md                    # 프로젝트 요구사항
├── 📄 README.md                 # 프로젝트 설명
├── 📄 RUNNING.md                # 이 파일
├── 📄 requirements.txt           # Python 의존성
├── 📄 setup.sh                  # 자동 설정 스크립트
├── 📄 example.py                # 사용 예제
├── 📁 src/                      # 소스 코드
│   ├── 📄 main.py               # FastAPI 애플리케이션
│   ├── 📄 config.py             # 설정 관리
│   ├── 📄 pdf_processor.py      # PDF 처리
│   ├── 📄 text_chunker.py       # 텍스트 청킹
│   ├── 📄 embedding_service.py  # Ollama 임베딩
│   ├── 📄 qdrant_manager.py     # Qdrant 관리
│   ├── 📄 search_service.py     # 검색 서비스
│   └── 📁 api/                  # API 모듈
├── 📁 tests/                    # 테스트 코드
├── 📁 data/                     # 데이터 디렉토리
└── 📁 logs/                     # 로그 파일
```

## 🔍 API 엔드포인트

| 메서드   | 엔드포인트               | 설명               |
| -------- | ------------------------ | ------------------ |
| `GET`    | `/api/v1/`               | API 정보           |
| `GET`    | `/api/v1/health`         | 서비스 상태 확인   |
| `POST`   | `/api/v1/upload-pdf`     | PDF 업로드 및 처리 |
| `POST`   | `/api/v1/search`         | 벡터 검색          |
| `GET`    | `/api/v1/documents`      | 저장된 문서 목록   |
| `GET`    | `/api/v1/collections`    | Qdrant 컬렉션 정보 |
| `DELETE` | `/api/v1/documents/{id}` | 문서 삭제          |

## 🐛 문제 해결

### 1. 포트 충돌

```bash
# 포트 사용 확인
lsof -i :8001
lsof -i :6333

# 다른 포트로 실행
APP_PORT=8002 python src/main.py
```

### 2. Ollama 연결 오류

```bash
# Ollama 서비스 상태 확인
ollama list

# 모델 재다운로드
ollama pull nomic-embed-text
```

### 3. Qdrant 연결 오류

```bash
# Docker 컨테이너 상태 확인
docker ps

# Qdrant 재시작
docker restart qdrant
```

### 4. 가상환경 문제

```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. 의존성 충돌

```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 삭제 후 재설치
pip cache purge
pip install -r requirements.txt
```

## 📊 성능 모니터링

### 1. 로그 확인

```bash
# 실시간 로그 확인
tail -f logs/app.log

# 특정 로그 레벨 확인
grep "ERROR" logs/app.log
```

### 2. 시스템 리소스 확인

```bash
# 메모리 사용량
top -p $(pgrep -f "python.*main.py")

# 디스크 사용량
du -sh data/ logs/
```

### 3. API 성능 테스트

```bash
# 응답 시간 테스트
time curl -X POST "http://localhost:8001/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 1}'
```

## 🔧 고급 설정

### 1. 환경별 설정

```bash
# 개발 환경
cp env.example .env.development

# 프로덕션 환경
cp env.example .env.production
```

### 2. 로깅 설정

```env
# .env 파일에 추가
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log
LOG_ROTATION=10 MB
LOG_RETENTION=7 days
```

### 3. 성능 최적화

```env
# .env 파일에 추가
CHUNK_SIZE=1024
CHUNK_OVERLAP=100
BATCH_SIZE=10
```

## 🧪 테스트 실행

### 1. 단위 테스트

```bash
# 모든 테스트 실행
python -m pytest tests/

# 특정 테스트 실행
python -m pytest tests/test_pdf_processor.py

# 커버리지 확인
python -m pytest --cov=src tests/
```

### 2. 통합 테스트

```bash
# 전체 워크플로우 테스트
python example.py
```

## 📈 모니터링 및 로깅

### 1. 로그 레벨

- `DEBUG`: 상세한 디버깅 정보
- `INFO`: 일반적인 정보
- `WARNING`: 경고 메시지
- `ERROR`: 오류 메시지

### 2. 주요 로그 위치

- **애플리케이션 로그**: `logs/app.log`
- **FastAPI 로그**: 콘솔 출력
- **Qdrant 로그**: Docker 컨테이너 로그

### 3. 로그 확인 명령어

```bash
# 실시간 로그
tail -f logs/app.log

# 오류만 확인
grep "ERROR" logs/app.log

# 특정 시간대 로그
grep "2025-08-09" logs/app.log
```

## 🚀 배포 고려사항

### 1. 프로덕션 환경

```bash
# 환경 변수 설정
export APP_ENV=production
export DEBUG=False
export LOG_LEVEL=INFO

# 서버 실행
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 2. Docker 배포

```dockerfile
# Dockerfile 예시
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["python", "src/main.py"]
```

### 3. 보안 설정

```env
# .env 파일에 추가
API_KEY=your-secret-key
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT=100/minute
```

## 📞 지원 및 문의

### 1. 일반적인 문제

- **포트 충돌**: 다른 포트 사용
- **메모리 부족**: Ollama 모델 크기 확인
- **네트워크 오류**: 방화벽 설정 확인

### 2. 로그 분석

```bash
# 오류 패턴 확인
grep -i "error\|exception" logs/app.log

# 성능 분석
grep "processing_time" logs/app.log
```

### 3. 디버깅 모드

```bash
# 디버그 모드로 실행
DEBUG=True python src/main.py

# 상세 로그 확인
LOG_LEVEL=DEBUG python src/main.py
```

## ✅ 체크리스트

- [ ] Python 3.9+ 설치
- [ ] Docker 설치 및 실행
- [ ] Ollama 설치 및 모델 다운로드
- [ ] 가상환경 생성 및 활성화
- [ ] 의존성 패키지 설치
- [ ] 환경 변수 설정
- [ ] Qdrant 서버 실행
- [ ] 애플리케이션 서버 실행
- [ ] API 테스트 성공
- [ ] 검색 기능 테스트 성공

## 🎉 완료!

모든 단계를 완료하면 PDF 문서를 벡터화하여 검색 가능한 형태로 저장하는 시스템이 준비됩니다!

**다음 단계:**

1. 실제 PDF 파일 업로드 테스트
2. 다양한 검색어로 검색 테스트
3. 성능 최적화 및 모니터링
4. 프로덕션 환경 배포
