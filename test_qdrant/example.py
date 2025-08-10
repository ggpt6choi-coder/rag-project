#!/usr/bin/env python3
"""
PDF to Qdrant Vector Database 사용 예제

이 스크립트는 PDF 파일을 처리하여 Qdrant 벡터 데이터베이스에 저장하고
검색하는 방법을 보여줍니다.
"""

import os
import sys
import time
from pathlib import Path
import argparse

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from src.pdf_processor import PDFProcessor
from src.text_chunker import TextChunker
from src.embedding_service import EmbeddingService
from src.qdrant_manager import QdrantManager
from src.search_service import SearchService
from src.config import config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=str, choices=['pdf', 'search', 'all'], default='all', help='실행할 단계')
    args = parser.parse_args()

    """메인 함수"""
    print("🚀 PDF to Qdrant Vector Database 예제")
    print("=" * 50)
    
    # 서비스 인스턴스 생성
    print("📋 서비스 초기화 중...")
    pdf_processor = PDFProcessor()
    text_chunker = TextChunker()
    embedding_service = EmbeddingService()
    qdrant_manager = QdrantManager()
    search_service = SearchService(qdrant_manager, embedding_service)
    
    # 서비스 연결 확인
    print("🔗 서비스 연결 확인 중...")
    
    # Qdrant 연결 확인
    if not qdrant_manager.connect():
        print("❌ Qdrant 서버에 연결할 수 없습니다.")
        print("   Docker로 Qdrant를 실행하세요:")
        print("   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")
        return
    
    print("✅ Qdrant 연결 성공")
    
    # Ollama 모델 확인
    if not embedding_service.validate_model():
        print("❌ Ollama 모델을 사용할 수 없습니다.")
        print("   Ollama를 설치하고 모델을 다운로드하세요:")
        print("   ollama pull nomic-embed-text")
        return
    
    print("✅ Ollama 모델 검증 성공")
    
    # 샘플 PDF 파일 경로
    sample_pdf = "data/uploads/운수좋은날.pdf"
    
    # 샘플 PDF가 없으면 생성
    if not os.path.exists(sample_pdf):
        print("📄 샘플 PDF 파일 생성 중...")
        create_sample_pdf(sample_pdf)
    
    if not os.path.exists(sample_pdf):
        print("❌ 샘플 PDF 파일을 생성할 수 없습니다.")
        return
    
    print(f"📄 PDF 파일 처리 중: {sample_pdf}")
    
    try:
        # 1. PDF 텍스트 추출
        if args.step in ['pdf', 'all']:
            print("1️⃣ PDF 텍스트 추출 중...")
            start_time = time.time()
            pdf_data = pdf_processor.extract_text(sample_pdf)
            extraction_time = time.time() - start_time
            
            print(f"   ✅ 텍스트 추출 완료 ({extraction_time:.2f}초)")
            print(f"   📄 텍스트 길이: {len(pdf_data['text'])} 문자")
            print(f"   📊 메타데이터: {pdf_data['metadata']}")
            
            # 2. 텍스트 청킹
            print("2️⃣ 텍스트 청킹 중...")
            start_time = time.time()
            chunks = text_chunker.chunk_text(pdf_data['text'])
            chunking_time = time.time() - start_time
            
            print(f"   ✅ 청킹 완료 ({chunking_time:.2f}초)")
            print(f"   📦 생성된 청크 수: {len(chunks)}")
            
            # 청크 통계 출력
            stats = text_chunker.get_chunk_statistics(chunks)
            print(f"   📊 청크 통계: 평균 {stats['avg_chunk_size']:.1f} 문자")
            
            # 3. 임베딩 생성
            print("3️⃣ 임베딩 생성 중...")
            start_time = time.time()
            embedded_chunks = embedding_service.embed_chunks(chunks)
            embedding_time = time.time() - start_time
            
            print(f"   ✅ 임베딩 완료 ({embedding_time:.2f}초)")
            print(f"   🧠 임베딩 차원: {embedded_chunks[0]['embedding_dimension'] if embedded_chunks else 0}")
            
            # 4. Qdrant에 저장
            print("4️⃣ Qdrant에 저장 중...")
            start_time = time.time()
            document_id = "example_document"
            success = qdrant_manager.store_vectors(embedded_chunks, document_id)
            storage_time = time.time() - start_time
            
            if success:
                print(f"   ✅ 저장 완료 ({storage_time:.2f}초)")
                print(f"   📊 저장된 벡터 수: {len(embedded_chunks)}")
            else:
                print("   ❌ 저장 실패")
                return

        # 5. 검색 테스트
        if args.step in ['search', 'all']:
            print("5️⃣ 검색 테스트 중...")
            test_queries = ["김천지", "인력거"]
            
            for query in test_queries:
                print(f"   🔍 검색: '{query}'")
                start_time = time.time()
                results = search_service.search(query, limit=3)
                search_time = time.time() - start_time
                
                print(f"      ✅ 검색 완료 ({search_time:.3f}초)")
                print(f"      📊 결과 수: {len(results)}")
                
                if results:
                    best_result = results[0]
                    print(f"      🏆 최고 점수: {best_result['score']:.3f}")
                    print(f"      📄 텍스트: {best_result['text'][:100]}...")
        
        # 6. 컬렉션 정보 출력
        print("6️⃣ 컬렉션 정보 확인 중...")
        collection_info = search_service.get_collection_info()
        if collection_info:
            print(f"   📊 상태: {collection_info['status']}")
            print(f"   🧠 벡터 수: {collection_info['vectors_count']}")
            print(f"   📦 포인트 수: {collection_info['points_count']}")
        
        print("\n🎉 모든 작업이 완료되었습니다!")
        print("\n다음 명령으로 API 서버를 실행할 수 있습니다:")
        print("python src/main.py")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def create_sample_pdf(file_path):
    """샘플 PDF 파일 생성"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # PDF 생성
        c = canvas.Canvas(file_path, pagesize=letter)
        
        # 제목
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "인공지능과 머신러닝")
        
        # 부제목
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, "샘플 문서")
        
        # 본문
        c.setFont("Helvetica", 10)
        text = """
인공지능(AI)은 컴퓨터 시스템이 인간의 지능을 모방하여 학습하고, 추론하고, 
문제를 해결할 수 있도록 하는 기술입니다. 머신러닝은 인공지능의 한 분야로, 
데이터로부터 패턴을 학습하여 예측이나 분류를 수행합니다.

딥러닝은 머신러닝의 하위 분야로, 인공 신경망을 사용하여 복잡한 패턴을 
학습합니다. 자연어 처리, 컴퓨터 비전, 음성 인식 등 다양한 분야에서 
활용되고 있습니다.

데이터 분석은 대용량 데이터에서 의미 있는 정보를 추출하는 과정입니다. 
통계적 방법과 머신러닝 알고리즘을 사용하여 데이터의 패턴을 발견하고 
의사결정에 활용합니다.
        """
        
        y_position = 680
        for line in text.strip().split('\n'):
            c.drawString(100, y_position, line.strip())
            y_position -= 15
        
        c.save()
        print(f"   ✅ 샘플 PDF 생성 완료: {file_path}")
        
    except ImportError:
        print("   ⚠️ reportlab이 설치되지 않아 샘플 PDF를 생성할 수 없습니다.")
        print("   pip install reportlab로 설치하거나 수동으로 PDF 파일을 추가하세요.")
    except Exception as e:
        print(f"   ❌ 샘플 PDF 생성 실패: {e}")

if __name__ == "__main__":
    main()
