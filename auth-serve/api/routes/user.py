from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from api.dependency import get_current_user
from auth.authentication import Authentication
from auth.caching import RBACCache
from db.engine import get_session
from db.tables import Role, User, UserRole
from models import (
    NewUserInvite,
    RoleMeResponse,
    SignupRequest,
    SignupResponse,
    Token,
    UserBase,
)
from utils import Hasher

user_router = APIRouter(prefix="/user", tags=["user"])

READ = "auth.user.read"
WRITE = "auth.user.write"
DELETE = "auth.user.delete"
ALL = "auth.user.all"


@user_router.post("/signup", response_model=SignupResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_session)):
    auth = Authentication(db)
    user = await auth.signup(request.org, request.user)
    return SignupResponse(user_id=user.id, org_id=user.org_id)


@user_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_session),
):
    username, password = form_data.username, form_data.password
    requested_scopes = form_data.scopes
    auth = Authentication(db)
    user = await auth.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await auth.rbac.create_access_token(
        user_id=user.id, org_id=user.org_id, requested_scopes=requested_scopes
    )
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requested scopes not granted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=access_token, token_type="bearer")


@user_router.post("/invite", response_model=User)
async def invite(
    request: NewUserInvite,
    current_user: User = Security(get_current_user, scopes=[WRITE, ALL]),
    db: Session = Depends(get_session),
):
    org_id = current_user.org_id
    user_data = UserBase(
        username=request.username,
        password=Hasher().get_password_hash(request.password),
        primary_email=request.primary_email,
    )
    role_name = request.role
    if role_name == "owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot invite owner or create owner role",
        )
    # Query role table
    role = db.exec(
        select(Role).where(Role.name == role_name, Role.org_id == org_id)
    ).one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with name {role_name} not found",
        )
    try:
        user = User(
            org_id=org_id,
            **user_data.model_dump(),
        )
        db.add(user)
        db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user",
        ) from e

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(user_role)
    db.commit()

    return user


@user_router.get("/me", response_model=User, name="Get current user")
async def get_me(
    current_user: User = Security(get_current_user, scopes=[READ, ALL]),
):
    return current_user


@user_router.get("/me/roles", name="Get current user roles")
async def get_me_roles(
    current_user: User = Security(get_current_user, scopes=[READ, ALL]),
    db: Session = Depends(get_session),
):
    cache = RBACCache(db)
    roles = await cache.get_user_roles(current_user.org_id, current_user.id)
    if roles:
        response = []
        for role in roles:
            r = RoleMeResponse(name=role, permissions=[])
            r.permissions = await cache.get_role_permissions(current_user.org_id, role)
            response.append(r)
        return response
    roles = db.exec(select(UserRole).where(UserRole.user_id == current_user.id)).all()
    response = []
    for role in roles:
        r = RoleMeResponse(name=role.role.name, permissions=[])
        permissions = role.role.role_permissions
        for permission in permissions:
            r.permissions.append(permission.permission.slug)
        response.append(r)

    return response
