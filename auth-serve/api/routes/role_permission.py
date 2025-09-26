from fastapi import APIRouter

role_router = APIRouter(prefix="/role", tags=["role"])


@role_router.get("/")
async def get_roles():
    return


@role_router.post("/")
async def create_role():
    return


@role_router.delete("/")
async def delete_role():
    return


@role_router.post("/assign")
async def assign_role():
    return


@role_router.post("/revoke")
async def revoke_role():
    return


@role_router.get("/{user_id}")
async def get_user_roles(user_id):
    return


permission_router = APIRouter(prefix="/permission", tags=["permission"])


@permission_router.post("/")
async def create_permission():
    return
