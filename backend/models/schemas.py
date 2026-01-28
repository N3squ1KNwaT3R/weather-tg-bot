from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterSchema(BaseModel):
    telegram_id: int
    email: EmailStr

class VerifySchema(BaseModel):
    telegram_id: int
    code: str

class SetCitySchema(BaseModel):
    telegram_id: int
    city: str
    city_id: str

class GetWeatherSchema(BaseModel):
    telegram_id: int
    city_id: Optional[str] = None
    city_name: Optional[str] = None