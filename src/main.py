import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn

from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

from src.config import config
from src.api.routes import router

# 로깅 설정
logger.add(
    config.LOG_FILE,
    level=config.LOG_LEVEL,
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# FastAPI 앱 생성
app = FastAPI(
    title="Document to Qdrant Vector Database API",
    description="문서를 청킹하여 Qdrant 벡터 데이터베이스에 저장하는 API",
    version="1.0.0",
    docs_url=None,  # Swagger UI 기본 비활성화
    redoc_url=None
)

# static/swagger 폴더를 /static 경로로 서빙
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../static")), name="static")

# 오프라인 Swagger UI 커스텀 엔드포인트
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
        swagger_favicon_url="/static/swagger/favicon-32x32.png"
    )


# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우터 등록
app.include_router(router, prefix="/api/v1", tags=["api"])

# favicon.ico 요청 무시 (204 No Content)
from fastapi.responses import Response
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error(f"전역 예외 발생: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": "2024-01-01T00:00:00"
        }
    )

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("애플리케이션 시작")
    
    # 필요한 디렉토리 생성
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    logger.info(f"업로드 디렉토리: {config.UPLOAD_DIR}")
    logger.info(f"로그 파일: {config.LOG_FILE}")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("애플리케이션 종료")

def main():
    """메인 함수"""
    logger.info("PDF to Qdrant Vector Database 서버 시작")
    
    uvicorn.run(
        "src.main:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
