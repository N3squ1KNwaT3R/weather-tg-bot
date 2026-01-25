from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from database import User


class UserService:
    @staticmethod
    def set_default_city(db: Session, telegram_id: int, city_name: str, city_id: str) -> dict:

        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not verified"
            )

        user.city = city_name
        user.city_id = city_id
        db.commit()

        return {
            "success": True,
            "message": f"Default city set to {city_name}"
        }

    @staticmethod
    def get_user(db: Session, telegram_id: int) -> User:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user