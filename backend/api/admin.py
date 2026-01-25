from fastapi import APIRouter, status

admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@admin_router.get("/stats/users")
async def users_list():
    pass

@admin_router.get("/admin/stats/popular-city")
async def popular_city():
    pass