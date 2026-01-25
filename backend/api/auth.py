from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.schemas import RegisterSchema, VerifySchema
from database import get_db
from services.auth_service import AuthService

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_auth_service() -> AuthService:
    from main import auth_service
    return auth_service

@auth_router.post("/register")
async def auth_register(
    data: RegisterSchema,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register_user(db, data.telegram_id, data.email)

@auth_router.post("/verify")
async def auth_verify(
    data: VerifySchema,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.verify_code(db, data.telegram_id, data.code)