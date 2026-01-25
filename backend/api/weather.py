from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.schemas import SetCitySchema, GetWeatherSchema
from database import get_db, WeatherRequest
from services.weather_service import weather_service
from services.user_service import UserService

weather_router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@weather_router.post("/set-city")
async def set_default_city(
        data: SetCitySchema,
        db: Session = Depends(get_db)
):
    return UserService.set_default_city(db, data.telegram_id, data.city, data.city_id)


@weather_router.post("/search")
async def search_city(city: str):
    return await weather_service.search_suggest(city)


@weather_router.post("/forecast")
async def get_forecast(
        data: GetWeatherSchema,
        db: Session = Depends(get_db)
):
    user = UserService.get_user(db, data.telegram_id)

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not verified"
        )
    city_id = data.city_id if data.city_id else user.city_id
    city_name = data.city_name if data.city_name else user.city

    if not city_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No city specified. Set default city or provide city_id"
        )
    forecast = await weather_service.get_forecast_by_id(city_id)
    weather_request = WeatherRequest(
        telegram_id=data.telegram_id,
        city=city_name
    )
    db.add(weather_request)
    db.commit()

    return forecast
