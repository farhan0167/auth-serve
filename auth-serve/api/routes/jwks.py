# auth_serve/routers/jwks.py
from fastapi import APIRouter

from auth.keystore import KeyStore

jwks_router = APIRouter(tags=["jwks"])


@jwks_router.get("/.well-known/jwks.json")
async def get_jwks():
    return KeyStore().jwks()
