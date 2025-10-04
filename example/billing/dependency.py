import httpx
import json
from typing import Annotated

import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

# Define scopes for your service
SCOPES = {
    "example_service.billing.read": "Read billing",
    "example_service.billing.write": "Write billing",
    "example_service.billing.delete": "Delete billing",
}

# Define the URL for the token endpoint
AUTH_URL = "http://localhost:8000/user/login"
JWKS_URL = "http://localhost:8000/.well-known/jwks.json"
USER_ME_URL = "http://localhost:8000/user/me"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=AUTH_URL,
    scopes=SCOPES
)

async def validate_access_token(token:str):
    unverified_header = jwt.get_unverified_header(token)
    # Fetch the public key
    async with httpx.AsyncClient() as client:
        public_key = await client.get(JWKS_URL)
        public_key = public_key.json()
    kid = unverified_header.get("kid")
    if not kid:
        raise jwt.InvalidTokenError("Token has no kid")
    matches = [k for k in public_key["keys"] if k["kid"] == kid]
    matching = matches[0] if matches else None
    if not matches:
        raise jwt.InvalidTokenError("Token has no matching kid")
    public_key = RSAAlgorithm.from_jwk(json.dumps(matching))
    # Verify the token
    return jwt.decode(token, public_key, algorithms=["RS256"])

async def has_access(
    token: Annotated[str, Depends(oauth2_scheme)],
    security_scopes: SecurityScopes
):
    try:
        validated_token = await validate_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token_scopes = set(validated_token.get("scopes"))
    required_scopes = set(security_scopes.scopes)

    has_access = token_scopes & required_scopes
    if not has_access:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return True
    
    
    
    