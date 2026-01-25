from fastapi import APIRouter, status

from models.schemas import WeatherSchema
from services.weather_service import weather_service

weather_router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@weather_router.post("/city")
async def find_city(request: WeatherSchema):
    return await weather_service.search_suggest(request.city)


@weather_router.post("/forecast")
async def get_forecast(request: WeatherSchema):
    return await weather_service.get_forecast_by_id(request.city)
