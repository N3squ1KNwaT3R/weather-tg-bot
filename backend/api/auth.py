from fastapi import APIRouter, status

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/auth/register")
async def auth_register():
    pass

@auth_router.post("/auth_verify")
async def auth_verify():
    pass

