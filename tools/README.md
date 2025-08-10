# 🛠️ 유틸리티 도구

이 디렉토리에는 프로젝트 개발 및 운영에 필요한 유틸리티 도구들이 포함되어 있습니다.

## 📋 도구 목록

### 🔍 Qdrant 데이터 확인 도구

- **[check_qdrant_data.py](./check_qdrant_data.py)** - Qdrant 데이터베이스 상태 및 데이터 확인

### 🖥️ Qdrant 뷰어 도구

- **[qdrant_viewer.py](./qdrant_viewer.py)** - 전체 기능을 갖춘 Qdrant 뷰어
- **[simple_qdrant_viewer.py](./simple_qdrant_viewer.py)** - 간단한 Qdrant 뷰어

## 🚀 사용법

### Qdrant 데이터 확인

```bash
# Qdrant 연결 상태 및 컬렉션 정보 확인
python tools/check_qdrant_data.py

# 특정 컬렉션의 데이터 확인
python tools/check_qdrant_data.py --collection pdf_documents
```

### Qdrant 뷰어 실행

```bash
# 전체 기능 뷰어 실행
python tools/qdrant_viewer.py

# 간단한 뷰어 실행
python tools/simple_qdrant_viewer.py
```

## 🔧 도구별 상세 설명

### check_qdrant_data.py

- Qdrant 서버 연결 상태 확인
- 컬렉션 목록 및 정보 조회
- 벡터 데이터 개수 및 통계 확인
- 메타데이터 샘플 조회

### qdrant_viewer.py

- 웹 기반 Qdrant 뷰어
- 컬렉션 관리 기능
- 벡터 검색 및 시각화
- 데이터 내보내기 기능

### simple_qdrant_viewer.py

- 콘솔 기반 간단한 뷰어
- 기본적인 데이터 조회 기능
- 빠른 상태 확인용

## 📊 모니터링 기능

### 데이터베이스 상태 모니터링

```bash
# 실시간 상태 확인
watch -n 5 python tools/check_qdrant_data.py
```

### 성능 모니터링

```bash
# 벡터 검색 성능 테스트
python tools/qdrant_viewer.py --performance-test
```

## 🔍 디버깅 도구

### 연결 문제 해결

```bash
# Qdrant 연결 테스트
python tools/check_qdrant_data.py --test-connection

# 상세 로그와 함께 실행
python tools/check_qdrant_data.py --verbose
```

### 데이터 무결성 검사

```bash
# 데이터 무결성 확인
python tools/check_qdrant_data.py --integrity-check
```

## 📝 로그 및 출력

모든 도구는 다음 형식으로 로그를 출력합니다:

- **INFO**: 일반 정보
- **WARNING**: 경고 메시지
- **ERROR**: 오류 메시지
- **DEBUG**: 디버그 정보 (--verbose 옵션 사용 시)

## 🔧 설정

도구들은 다음 환경 변수를 사용합니다:

- `QDRANT_HOST`: Qdrant 서버 호스트 (기본값: localhost)
- `QDRANT_PORT`: Qdrant 서버 포트 (기본값: 6333)
- `QDRANT_COLLECTION_NAME`: 기본 컬렉션 이름 (기본값: pdf_documents)

## 🚨 문제 해결

### 일반적인 문제들

1. **연결 실패**

   ```bash
   # Qdrant 서버 상태 확인
   curl http://localhost:6333/collections
   ```

2. **권한 문제**

   ```bash
   # 파일 권한 확인
   ls -la tools/
   ```

3. **의존성 문제**
   ```bash
   # 필요한 패키지 설치
   pip install qdrant-client requests
   ```

## 📚 추가 문서

자세한 사용법은 다음 문서를 참조하세요:

- **[QDRANT_VIEWERS.md](../docs/QDRANT_VIEWERS.md)** - 상세한 뷰어 사용법
- **[RUNNING.md](../docs/RUNNING.md)** - 전체 시스템 실행 가이드
