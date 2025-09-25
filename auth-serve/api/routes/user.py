from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from auth.authentication import Authentication
from db.engine import get_session
from models import SignupRequest, SignupResponse, Token

user_router = APIRouter(prefix="/user", tags=["user"])

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
    auth = Authentication(db)
    user = await auth.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await auth.rbac.create_access_token(user_id=user.id)
    return Token(access_token=access_token, token_type="bearer")

@user_router.post("/invite")
async def invite(db: Session = Depends(get_session)):
    return
