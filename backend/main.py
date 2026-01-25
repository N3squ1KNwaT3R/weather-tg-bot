from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from core.smtp_client import create_smtp
from services.email_service import EmailService
from core.config import settings

from api.auth import auth_router
from api.weather import weather_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(weather_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    smtp = await create_smtp()
    app.state.email_service = EmailService(smtp, settings.MAIL_FROM)
