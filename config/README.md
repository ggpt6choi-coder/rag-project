# ⚙️ 설정 파일

이 디렉토리에는 프로젝트 설정과 관련된 모든 파일들이 포함되어 있습니다.

## 📋 설정 파일 목록

### 📦 의존성 관리

- **[requirements.txt](./requirements.txt)** - Python 패키지 의존성 목록

### 🔧 환경 설정

- **[setup.sh](./setup.sh)** - 프로젝트 초기 설정 스크립트

## 🚀 사용법

### 1. 프로젝트 초기 설정

```bash
# 설정 스크립트 실행
bash config/setup.sh

# 또는 수동 설정
pip install -r config/requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 편집
vi .env
```

### 3. 의존성 설치

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r config/requirements.txt
```

## 🔧 파일별 상세 설명

### requirements.txt

Python 프로젝트에 필요한 모든 패키지와 버전을 정의합니다.

**주요 패키지:**

- `fastapi` - 웹 프레임워크
- `uvicorn` - ASGI 서버
- `qdrant-client` - Qdrant 클라이언트
- `pypdf2` - PDF 처리
- `loguru` - 로깅
- `python-dotenv` - 환경 변수 관리

### setup.sh

프로젝트 초기 설정을 자동화하는 스크립트입니다.

**주요 기능:**

- 가상환경 생성
- 의존성 설치
- 환경 변수 파일 생성
- 필요한 디렉토리 생성
- 권한 설정

## 🔧 설정 옵션

### 개발 환경 설정

```bash
# 개발용 설정
cp config/env.example .env
echo "DEBUG=True" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
```

### 프로덕션 환경 설정

```bash
# 프로덕션용 설정
cp config/env.example .env
echo "DEBUG=False" >> .env
echo "LOG_LEVEL=WARNING" >> .env
echo "APP_HOST=0.0.0.0" >> .env
```

### 테스트 환경 설정

```bash
# 테스트용 설정
cp config/env.example .env
echo "TEST_MODE=True" >> .env
echo "QDRANT_COLLECTION_NAME=test_documents" >> .env
```

## 📊 환경별 설정

### 개발 환경

```bash
# 개발용 환경 변수
DEBUG=True
LOG_LEVEL=DEBUG
APP_PORT=8000
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### 프로덕션 환경

```bash
# 프로덕션용 환경 변수
DEBUG=False
LOG_LEVEL=INFO
APP_PORT=80
CHUNK_SIZE=1024
CHUNK_OVERLAP=100
```

### 테스트 환경

```bash
# 테스트용 환경 변수
TEST_MODE=True
LOG_LEVEL=DEBUG
APP_PORT=8001
QDRANT_COLLECTION_NAME=test_collection
```

## 🔍 설정 검증

### 환경 변수 확인

```bash
# 설정된 환경 변수 확인
python -c "import os; print('QDRANT_HOST:', os.getenv('QDRANT_HOST'))"
python -c "import os; print('OLLAMA_HOST:', os.getenv('OLLAMA_HOST'))"
```

### 의존성 확인

```bash
# 설치된 패키지 확인
pip list

# requirements.txt와 비교
pip freeze > current_requirements.txt
diff config/requirements.txt current_requirements.txt
```

### 연결 테스트

```bash
# Qdrant 연결 테스트
curl http://localhost:6333/collections

# Ollama 연결 테스트
curl http://localhost:11434/api/tags
```

## 🚨 문제 해결

### 일반적인 문제들

1. **의존성 설치 실패**

   ```bash
   # pip 업그레이드
   pip install --upgrade pip

   # 가상환경 재생성
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r config/requirements.txt
   ```

2. **환경 변수 문제**

   ```bash
   # .env 파일 확인
   cat .env

   # 환경 변수 로드 확인
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('QDRANT_HOST'))"
   ```

3. **권한 문제**

   ```bash
   # 파일 권한 확인
   ls -la config/

   # 실행 권한 부여
   chmod +x config/setup.sh
   ```

## 📝 설정 관리

### 버전 관리

```bash
# 설정 파일 백업
cp .env .env.backup

# 설정 변경사항 추적
git add .env.example
git commit -m "Update environment template"
```

## 🔄 자동화

### CI/CD 파이프라인

```yaml
# .github/workflows/setup.yml
name: Setup
on: [push, pull_request]
jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r config/requirements.txt
```

### Docker 설정

```dockerfile
# Dockerfile
FROM python:3.9-slim
COPY config/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/main.py"]
```

## 📚 추가 문서

자세한 설정 방법은 다음 문서를 참조하세요:

- **[README.md](../docs/README.md)** - 프로젝트 상세 설명
- **[RUNNING.md](../docs/RUNNING.md)** - 실행 가이드
- **[Q&A_UPGRADE_GUIDE.md](../docs/Q&A_UPGRADE_GUIDE.md)** - 시스템 업그레이드 가이드
