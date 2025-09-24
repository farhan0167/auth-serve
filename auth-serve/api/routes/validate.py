from fastapi import APIRouter

validate_router = APIRouter(prefix="/validate", tags=["validate"])


@validate_router.post("/token")
async def validate_token():
    return


@validate_router.post("/key")
async def validate_key():
    return