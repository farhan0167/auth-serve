from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from auth.rbac import RBAC
from db.engine import engine, get_session
from db.tables import User, Permission

class OAuth2PasswordBearerWithScopes(OAuth2PasswordBearer):
    def __init__(self):
        with Session(engine) as db:
            scopes_db = db.exec(select(Permission)).all()
        scopes = {
            scope.namespace : f"{scope.action.value}:{scope.namespace}" 
            for scope in scopes_db
        }
        super().__init__(tokenUrl="user/login", scopes=scopes)

oauth2_scheme = OAuth2PasswordBearerWithScopes()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_session),
):
    rbac = RBAC(db)
    validated_token = await rbac.validate_access_token(token)
    if not validated_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = validated_token["sub"]
    user = db.exec(select(User).where(User.id == user_id)).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user