from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import text
from ..core.database import SessionLocal, engine
from ..deps import get_current_user
from .. import models
from ..state import maintenance_enabled

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
        "maintenance": maintenance_enabled,
    }


@router.post("/maintenance")
async def toggle_maintenance(
    enabled: bool = False,
    current_user: models.User = Depends(get_current_user),
):
    """Toggle maintenance mode — admin only."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    global maintenance_enabled
    maintenance_enabled = enabled
    return {
        "status": "maintenance mode updated",
        "maintenance": maintenance_enabled,
    }


@router.get("/maintenance-status")
async def get_maintenance_status():
    """Public endpoint to check maintenance mode."""
    return {"maintenance": maintenance_enabled}
