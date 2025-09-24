from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/signup")
async def signup():
    return

@auth_router.post("/login")
async def login():
    return

@auth_router.post("/invite")
async def logout():
    return