from typing import Annotated

from fastapi import BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlmodel import Session, select

from auth.caching import RBACCache
from auth.rbac import RBAC
from db.engine import get_session
from db.tables import User
from utils.seed import get_system_permissions


class OAuth2PasswordBearerWithScopes(OAuth2PasswordBearer):
    def __init__(self):
        scopes = {}
        system_permissions = get_system_permissions()
        for permission in system_permissions:
            description, slug = permission["description"], permission["slug"]
            scopes[slug] = description
        super().__init__(tokenUrl="user/login", scopes=scopes)


oauth2_scheme = OAuth2PasswordBearerWithScopes()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    security_scopes: SecurityScopes,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
) -> User:
    rbac = RBAC(db)
    cache = RBACCache(db)
    try:
        validated_token = await rbac.validate_access_token(token)
    except (ExpiredSignatureError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user_id = validated_token.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Query cache
    user = await cache.get_user(user_id=user_id)
    if user:
        user = User(**user)
    else:
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

    user_scopes = await rbac.get_scopes(user.id, user.org_id)
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
    background_tasks.add_task(cache.set_user, user_id=user.id, user=user)

    return user
