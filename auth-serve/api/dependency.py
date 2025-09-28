from typing import Annotated

from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel import Session, select

from auth.rbac import RBAC
from db.engine import get_session
from db.tables import User
from utils.seed import system_permissions


class OAuth2PasswordBearerWithScopes(OAuth2PasswordBearer):
    def __init__(self):
        scopes = {}
        for permission in system_permissions:
            description, slug = permission["description"], permission["slug"]
            scopes[slug] = description
        super().__init__(tokenUrl="user/login", scopes=scopes)


oauth2_scheme = OAuth2PasswordBearerWithScopes()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    security_scopes: SecurityScopes,
    db: Session = Depends(get_session),
) -> User:      
    rbac = RBAC(db)
    try:
        validated_token = await rbac.validate_access_token(token)
    except InvalidTokenError or ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = validated_token.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.exec(select(User).where(User.id == user_id)).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_scopes = await rbac.get_scopes(user.id)
    token_scopes = set(validated_token.get("scopes"))
    granted = user_scopes & token_scopes

    required_scopes = set(security_scopes.scopes)
    has_access = required_scopes & granted
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user
