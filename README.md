# PDF to Qdrant Vector Database Project

PDF 문서를 청킹하여 Qdrant 벡터 데이터베이스에 저장하고 검색할 수 있는 시스템입니다.

## 📁 프로젝트 구조

```
DigitalCompetition/
├── 📄 README.md                    # 프로젝트 개요 (현재 파일)
├── 📁 docs/                        # 📚 프로젝트 문서
│   ├── README.md                   # 문서 목록 및 가이드
│   ├── PRD.md                      # Product Requirements Document
│   ├── PROJECT_SUMMARY.md          # 프로젝트 요약
│   ├── Q&A_UPGRADE_GUIDE.md       # Q&A 시스템 가이드
│   ├── QDRANT_VIEWERS.md          # Qdrant 뷰어 도구 가이드
│   └── RUNNING.md                  # 실행 가이드
│
├── 📁 config/                      # ⚙️ 설정 파일
│   ├── README.md                   # 설정 파일 가이드
│   ├── requirements.txt            # Python 의존성
│   └── setup.sh                    # 프로젝트 설정 스크립트
│
├── 📁 src/                         # 🏗️ 소스 코드
│   ├── main.py                     # FastAPI 애플리케이션
│   ├── config.py                   # 설정 관리
│   ├── pdf_processor.py            # PDF 처리
│   ├── text_chunker.py             # 텍스트 청킹
│   ├── embedding_service.py        # 임베딩 생성
│   ├── qdrant_manager.py           # Qdrant 관리
│   ├── search_service.py           # 검색 서비스
│   ├── qa_service.py               # Q&A 서비스
│   └── api/                        # API 레이어
│       ├── models.py               # Pydantic 모델
│       └── routes.py               # API 라우트
│
├── 📁 tools/                       # 🛠️ 유틸리티 도구
│   ├── README.md                   # 도구 사용 가이드
│   ├── check_qdrant_data.py       # Qdrant 데이터 확인
│   ├── qdrant_viewer.py           # Qdrant 뷰어
│   └── simple_qdrant_viewer.py    # 간단한 Qdrant 뷰어
│
├── 📁 scripts/                     # 📜 실행 스크립트
│   ├── README.md                   # 스크립트 사용 가이드
│   ├── test_qa_direct.py          # Q&A 직접 테스트
│   └── test_qa_simple.py          # 간단한 Q&A 테스트
│
├── 📁 test_workflow/                   # Qdrant/LLM 워크플로우 및 실무 테스트 스크립트
│   ├── README.md                   # 예제 사용 가이드
│   └── example.py                  # 기본 사용 예제
│
├── 📁 tests/                       # 🧪 단위 테스트
│   ├── test_pdf_processor.py
│   ├── test_text_chunker.py
│   └── test_embedding_service.py
│
├── 📁 data/                        # 📊 데이터 디렉토리
│   ├── uploads/                    # 업로드된 파일
│   └── samples/                    # 샘플 파일
│
├── 📁 logs/                        # 📝 로그 파일
├── 📁 venv/                        # 가상환경
└── .gitignore                      # Git 무시 파일
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 활성화
source venv/bin/activate

# 의존성 설치 (새로운 경로)
pip install -r config/requirements.txt
```

### 2. 서비스 실행

```bash
# Ollama 실행 (임베딩 모델)
ollama pull nomic-embed-text

# Qdrant 실행 (Docker)
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# 애플리케이션 실행
python src/main.py
```

### 3. API 접근

- API 문서: http://localhost:8000/docs
- 서버 상태: http://localhost:8000/api/v1/health

## 📚 상세 문서

- **[📚 문서 가이드](docs/README.md)** - 모든 문서 목록 및 사용법
- **[🚀 실행 가이드](docs/RUNNING.md)** - 상세한 실행 방법
- **[🤖 Q&A 가이드](docs/Q&A_UPGRADE_GUIDE.md)** - Q&A 시스템 사용법
- **[🛠️ Qdrant 뷰어](docs/QDRANT_VIEWERS.md)** - Qdrant 도구 사용법

## 🛠️ 개발 도구

### 테스트

```bash
# 단위 테스트
python -m pytest tests/

# 통합 테스트 (새로운 경로)
python scripts/test_qa_direct.py
```

### 도구

```bash
# Qdrant 데이터 확인 (새로운 경로)
python tools/check_qdrant_data.py

# Qdrant 뷰어 (새로운 경로)
python tools/qdrant_viewer.py
```

### 예제

```bash
# 기본 사용 예제 (새로운 경로)
python test_workflow/example.py
```

## 📊 모니터링

- **로그**: `logs/app.log`
- **API 문서**: http://localhost:8000/docs
- **Qdrant 관리**: http://localhost:6333/dashboard

## 🔧 설정

주요 설정은 `.env` 파일에서 관리됩니다:

- Qdrant 연결 설정
- Ollama 모델 설정
- 텍스트 청킹 설정
- 애플리케이션 설정

자세한 설정 방법은 [설정 가이드](config/README.md)를 참조하세요.

## 🎯 주요 기능

### 📄 PDF 처리

- PDF 텍스트 추출 및 청킹
- 메타데이터 추출
- 벡터 임베딩 생성

### 🔍 검색 및 Q&A

- 벡터 기반 의미 검색
- RAG 기반 질의응답
- 컨텍스트 기반 답변 생성

### 🛠️ 개발 도구

- Qdrant 데이터 확인 도구
- Q&A 시스템 테스트 스크립트
- 예제 코드 및 사용법

## 📝 실행 시 주의사항

### ✅ **정상 작동 확인**

파일 위치 변경 후에도 모든 기능이 정상 작동합니다:

1. **의존성 설치**: `pip install -r config/requirements.txt`
2. **가상환경 활성화**: `source venv/bin/activate`
3. **스크립트 실행**: `python scripts/test_qa_direct.py`
4. **도구 실행**: `python tools/check_qdrant_data.py`

### 🔧 **경로 수정 완료**

- 스크립트들의 Python 경로 수정 완료
- 모든 import 경로 정상 작동
- 설정 파일 경로 업데이트 완료

### 📚 **문서 업데이트**

- 각 디렉토리별 README.md 생성
- 새로운 경로 반영
- 사용법 가이드 업데이트

## 🚨 문제 해결

### 의존성 문제

```bash
# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

### 경로 문제

```bash
# Python 경로 확인
python -c "import sys; print(sys.path)"

# 모듈 import 테스트
python -c "from src.config import config; print('OK')"
```

### 실행 문제

```bash
# 로그 확인
tail -f logs/app.log

# 서비스 상태 확인
curl http://localhost:8000/api/v1/health
```

## 📈 프로젝트 개선사항

### ✅ **완료된 개선사항**

- [x] 파일 기능별 분류
- [x] 각 디렉토리별 README 생성
- [x] 경로 수정 및 테스트 완료
- [x] 문서 업데이트
- [x] 실행 스크립트 경로 수정

### 🎯 **사용자 경험 개선**

- **새로운 개발자**: 루트 README → docs/README.md → 실행
- **기존 개발자**: tools/, scripts/ 디렉토리 활용
- **운영자**: config/ 디렉토리로 설정 관리

이제 프로젝트가 훨씬 체계적이고 사용하기 쉬운 구조로 정리되었습니다! 🎉

실제 사용 예제 코드는 sample_workflow/ 디렉터리로 이동되었습니다.
기존 examples/ 디렉토리의 모든 예제 실행 명령어를 test_qdrant/로 변경
# rag-project
