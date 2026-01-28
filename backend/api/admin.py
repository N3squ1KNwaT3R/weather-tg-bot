from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Dict, Optional
from api.websocket import log_user_activity

admin_router = APIRouter(prefix="/api/logs", tags=["logs"])


class ActivityLog(BaseModel):
    user_id: int
    username: str
    action: str
    details: Optional[Dict] = {}
    level: str = "info"


@admin_router.post("/activity")
async def log_activity(log: ActivityLog):
    """Endpoint для приема логов активности"""
    await log_user_activity(
        user_id=log.user_id,
        username=log.username,
        action=log.action,
        details=log.details,
        level=log.level
    )
    return {"status": "ok"}