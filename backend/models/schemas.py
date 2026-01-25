from pydantic import BaseModel, EmailStr


class RegisterSchema(BaseModel):
    email: EmailStr

class WeatherSchema(BaseModel):
    city: str