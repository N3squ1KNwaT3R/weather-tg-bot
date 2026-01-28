from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.schemas import RegisterSchema, VerifySchema
from database import get_db
from services.auth_service import AuthService
from database import get_db, User
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


@auth_router.get("/user/{telegram_id}")
async def get_user_info(
        telegram_id: int,
        db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "telegram_id": user.telegram_id,
        "email": user.email,
        "city": user.city,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }