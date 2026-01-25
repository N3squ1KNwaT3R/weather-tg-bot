import httpx
import os
from loguru import logger


class APIClient:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://backend:8000")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def register(self, telegram_id: int, email: str) -> dict:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/register",
                json={"telegram_id": telegram_id, "email": email}
            )
            response.raise_for_status()
            logger.info(f"User {telegram_id} registered with email {email}")
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Registration failed: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise

    async def verify(self, telegram_id: int, code: str) -> dict:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/verify",
                json={"telegram_id": telegram_id, "code": code}
            )
            response.raise_for_status()
            logger.info(f"User {telegram_id} verified successfully")
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Verification failed: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Verification error: {e}")
            raise

    async def search_city(self, city: str) -> list:
        try:
            response = await self.client.get(  # Измени на GET
                f"{self.base_url}/api/v1/weather/search",
                params={"city": city}
            )
            response.raise_for_status()
            data = response.json()

            return data if isinstance(data, list) else []

        except Exception as e:
            logger.error(f"City search error: {e}")
            return []

    async def set_default_city(self, telegram_id: int, city: str, city_id: str) -> dict:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/weather/set-city",
                json={"telegram_id": telegram_id, "city": city, "city_id": city_id}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Set city error: {e}")
            raise

    async def get_forecast(self, telegram_id: int, city_id: str = None, city_name: str = None) -> dict:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/weather/forecast",
                json={
                    "telegram_id": telegram_id,
                    "city_id": city_id,
                    "city_name": city_name
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get forecast error: {e}")
            raise

    async def get_user_info(self, telegram_id: int) -> dict:

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/auth/user/{telegram_id}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get user info error: {e}")
            raise

    async def get_hourly_forecast(self, telegram_id: int, city_id: str = None, city_name: str = None) -> dict:
        """Получить почасовой прогноз"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/weather/hourly",
                json={
                    "telegram_id": telegram_id,
                    "city_id": city_id,
                    "city_name": city_name
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get hourly forecast error: {e}")
            raise

    async def get_tomorrow_forecast(self, telegram_id: int, city_id: str = None, city_name: str = None) -> dict:
        """Получить прогноз на завтра"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/weather/tomorrow",
                json={
                    "telegram_id": telegram_id,
                    "city_id": city_id,
                    "city_name": city_name
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get tomorrow forecast error: {e}")
            raise


api_client = APIClient()
