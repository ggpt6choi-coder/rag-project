#!/bin/bash

# PDF to Qdrant Vector Database Project Setup Script

echo "🚀 PDF to Qdrant Vector Database 프로젝트 설정을 시작합니다..."

# Python 버전 확인
echo "📋 Python 버전 확인 중..."
python3 --version

# 가상환경 생성
echo "🔧 가상환경 생성 중..."
python3 -m venv venv

# 가상환경 활성화
echo "✅ 가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "⬆️ pip 업그레이드 중..."
pip install --upgrade pip

# 의존성 설치
echo "📦 의존성 패키지 설치 중..."
pip install -r requirements.txt

# 환경 변수 파일 생성
echo "⚙️ 환경 변수 파일 생성 중..."
if [ ! -f .env ]; then
    echo "✅ .env 파일이 생성되었습니다. 필요에 따라 설정을 수정하세요."
else
    echo "ℹ️ .env 파일이 이미 존재합니다."
fi

# 필요한 디렉토리 생성
echo "📁 필요한 디렉토리 생성 중..."
mkdir -p data/uploads data/samples logs

echo "🎉 설정이 완료되었습니다!"
echo ""
echo "다음 단계:"
echo "1. 가상환경 활성화: source venv/bin/activate"
echo "2. Ollama 설치 및 모델 다운로드"
echo "3. Qdrant 서버 실행"
echo "4. 애플리케이션 실행: python src/main.py"
echo ""
echo "자세한 내용은 README.md를 참조하세요."
