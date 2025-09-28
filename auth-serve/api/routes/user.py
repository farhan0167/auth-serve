from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from api.dependency import get_current_user
from auth.authentication import Authentication
from db.engine import get_session
from db.tables import User, Role, UserRole
from models import SignupRequest, SignupResponse, Token, NewUserInvite, UserBase
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
        user_id=user.id, requested_scopes=requested_scopes
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
    current_user = Security(get_current_user, scopes=[WRITE, ALL]),
    db: Session = Depends(get_session),
):
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
    role = db.exec(select(Role).where(Role.name == role_name)).one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with name {role_name} not found",
        )
    try:
        user = User(
            org_id=current_user.org_id,
            **user_data.model_dump(),
        )
        db.add(user)
        db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user",
        )

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(user_role)
    db.commit()
    
    return user
