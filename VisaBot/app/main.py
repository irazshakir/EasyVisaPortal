"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api.routes import api_router
from app.core.events import create_start_app_handler, create_stop_app_handler


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="VisaBot - FastAPI + FSM + OpenAI LLM Bot",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=False,  # Disable credentials for VisaBot API
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add event handlers
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))

    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 