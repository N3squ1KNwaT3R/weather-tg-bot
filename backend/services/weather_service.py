import httpx

class WeatherService:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.base_url = "https://sinoptik.pl/api/"
        self.headers = {
            'Host': 'sinoptik.pl',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
        }

    async def search_suggest(self, city: str) -> dict:
        json_data = {
            'query': city,
            'lang': 'pol',
            'limit': 3,
        }

        locations = await self.client.post(
            f"{self.base_url}search/suggest",
            json=json_data,
            headers=self.headers
        )
        return locations.json()

    async def get_forecast_by_id(self, id: str) -> dict:
        json_data = {
            'lang': 'pol',
            'location_id': id,
            'forecast_days': 1,
        }
        forecast = await self.client.post(
            f"{self.base_url}weather/location/forecast/by_id",
            json=json_data,
            headers=self.headers
        )
        return forecast.json()


weather_service = WeatherService()
