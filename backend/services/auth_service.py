from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from database import User, VerificationCode
from services.email_service import EmailService


class AuthService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    async def register_user(self, db: Session, telegram_id: int, email: str) -> dict:
        existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if existing_user:
            if existing_user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already registered and verified"
                )

        code = EmailService.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        if not existing_user:
            user = User(telegram_id=telegram_id, email=email)
            db.add(user)
        else:
            existing_user.email = email
        verification = VerificationCode(
            telegram_id=telegram_id,
            code=code,
            expires_at=expires_at
        )
        db.add(verification)
        db.commit()

        await self.email_service.send_verification_code(email, code)

        return {"success": True, "message": "Verification code sent to email"}

    async def verify_code(self, db: Session, telegram_id: int, code: str) -> dict:
        verification = db.query(VerificationCode).filter(
            VerificationCode.telegram_id == telegram_id,
            VerificationCode.code == code
        ).order_by(VerificationCode.created_at.desc()).first()

        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        if datetime.utcnow() > verification.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired"
            )

        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_verified = True
        db.commit()
        db.delete(verification)
        db.commit()

        return {"success": True, "message": "User verified successfully"}
