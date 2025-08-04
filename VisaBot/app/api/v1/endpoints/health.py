"""
Health check endpoints
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from app.services.redis_service import redis_client

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "visabot"}


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "service": "visabot",
        "dependencies": {}
    }
    
    # Check Redis connection
    try:
        await redis_client.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["dependencies"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status 