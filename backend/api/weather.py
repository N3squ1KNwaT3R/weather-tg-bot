from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from models.schemas import SetCitySchema, GetWeatherSchema
from database import get_db, WeatherRequest
from services.weather_service import weather_service
from services.user_service import UserService

weather_router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@weather_router.get("/search")
async def search_city(city: str = Query(...)):
    result = await weather_service.search_suggest(city)

    return result.get("locations", [])


@weather_router.post("/set-city")
async def set_default_city(
        data: SetCitySchema,
        db: Session = Depends(get_db)
):
    return UserService.set_default_city(db, data.telegram_id, data.city, data.city_id)


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

    forecast_data = await weather_service.get_forecast_by_id(city_id)

    location = forecast_data.get("location", {})
    forecast = forecast_data.get("forecast", {})

    today = datetime.now().strftime("%Y-%m-%d")
    today_forecast = forecast.get(today, {})

    now = today_forecast.get("now", {})
    temp_range = today_forecast.get("temp", {})

    result = {
        "city": location.get("title", city_name),
        "temp": now.get("temp", 0),
        "temp_feels": now.get("temp_feels", 0),
        "temp_min": temp_range.get("min", 0),
        "temp_max": temp_range.get("max", 0),
        "condition": now.get("condition", 0),
        "description": location.get("description", ""),
        "coordinates": location.get("coordinates", {}),
    }

    weather_request = WeatherRequest(
        telegram_id=data.telegram_id,
        city=location.get("title", city_name)
    )
    db.add(weather_request)
    db.commit()

    return result


@weather_router.post("/hourly")
async def get_hourly_forecast(
        data: GetWeatherSchema,
        db: Session = Depends(get_db)
):
    """Получить почасовой прогноз"""
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
            detail="No city specified"
        )

    forecast_data = await weather_service.get_forecast_by_id(city_id)

    location = forecast_data.get("location", {})
    forecast = forecast_data.get("forecast", {})

    today = datetime.now().strftime("%Y-%m-%d")
    today_forecast = forecast.get(today, {})
    hours = today_forecast.get("hours", [])

    return {
        "city": location.get("title", city_name),
        "hours": hours
    }


from datetime import datetime, timedelta


@weather_router.post("/tomorrow")
async def get_tomorrow_forecast(
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
            detail="No city specified"
        )

    forecast_data = await weather_service.get_forecast_by_id(city_id)

    location = forecast_data.get("location", {})
    forecast = forecast_data.get("forecast", {})

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_forecast = forecast.get(tomorrow, {})

    if not tomorrow_forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No forecast for tomorrow"
        )

    temp_range = tomorrow_forecast.get("temp", {})
    condition = tomorrow_forecast.get("condition", 0)
    hours = tomorrow_forecast.get("hours", [])

    if hours:
        avg_temp = sum(h.get("temp", 0) for h in hours) // len(hours)
    else:
        avg_temp = (temp_range.get("min", 0) + temp_range.get("max", 0)) // 2

    return {
        "city": location.get("title", city_name),
        "date": tomorrow,
        "temp_avg": avg_temp,
        "temp_min": temp_range.get("min", 0),
        "temp_max": temp_range.get("max", 0),
        "condition": condition,
        "hours": hours
    }