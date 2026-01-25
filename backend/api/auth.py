from http import HTTPStatus

from fastapi import APIRouter, status, Request

from models.schemas import RegisterSchema

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/register")
async def auth_register(request: RegisterSchema):
    email_service = request.app.state.email_service
    await email_service.send(request.email)
    return HTTPStatus(status.HTTP_200_OK)


@auth_router.post("/verify")
async def auth_verify(request: Request):
    pass
