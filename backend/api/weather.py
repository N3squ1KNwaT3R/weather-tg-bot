from fastapi import APIRouter, status

weather_router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@weather_router.get("/city")
async def city_weather():
    pass
