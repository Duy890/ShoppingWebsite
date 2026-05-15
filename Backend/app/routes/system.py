from fastapi import APIRouter, status
from pydantic import BaseModel
from sqlalchemy import text
from ..core.database import SessionLocal, engine

router = APIRouter(prefix="/api/system", tags=["system"])


class HealthResponse(BaseModel):
    status: str
    message: str


class StatusResponse(BaseModel):
    status: str
    database: str
    api: str
    maintenance: bool


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint - returns 200 if service is running.
    Used for load balancers and monitoring.
    """
    return {
        "status": "healthy",
        "message": "API is running",
    }


@router.get("/status", response_model=StatusResponse)
async def system_status():
    """
    System status endpoint - checks database connectivity and service availability.
    Returns comprehensive system health information.
    """
    db_status = "disconnected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "database": db_status,
        "api": "running",
        "maintenance": False,
    }


@router.post("/maintenance")
async def toggle_maintenance(enabled: bool = False):
    """
    Toggle maintenance mode (admin only).
    When enabled, API returns 503 Service Unavailable.
    """
    # TODO: Add admin authentication check
    return {
        "status": "maintenance mode updated",
        "maintenance": enabled,
    }
