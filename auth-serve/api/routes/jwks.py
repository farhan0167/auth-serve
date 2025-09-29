# auth_serve/routers/jwks.py
from fastapi import APIRouter

from auth.keystore import KeyStore

jkws_router = APIRouter(tags=["jwks"])


@jkws_router.get("/.well-known/jwks.json")
async def get_jwks():
    return KeyStore().jwks()
