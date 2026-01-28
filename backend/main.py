from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from core.smtp_client import create_smtp
from services.email_service import EmailService
from services.auth_service import AuthService
from core.config import settings
from database import init_db

from api.auth import auth_router
from api.weather import weather_router
from api.websocket import websocket_router

app = FastAPI()

auth_service = None


@app.on_event("startup")
async def startup():
    global auth_service

    init_db()

    smtp = await create_smtp()
    email_service = EmailService(smtp, settings.MAIL_FROM)
    auth_service = AuthService(email_service)

    app.state.email_service = email_service
    app.state.auth_service = auth_service


@app.on_event("shutdown")
async def shutdown():
    if hasattr(app.state, 'email_service'):
        await app.state.email_service.smtp.quit()


app.include_router(auth_router)
app.include_router(weather_router)
app.include_router(websocket_router)  # Добавляем WebSocket роутер

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Weather Bot API"}