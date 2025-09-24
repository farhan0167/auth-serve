from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth.authentication import Authentication
from db.engine import get_session
from models import SignupRequest, SignupResponse

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.post("/signup", response_model=SignupResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_session)):
    auth = Authentication(db)
    user = await auth.signup(request.org, request.user)
    return SignupResponse(user_id=user.id, org_id=user.org_id)

@user_router.post("/login")
async def login(db: Session = Depends(get_session)):
    return

@user_router.post("/invite")
async def invite(db: Session = Depends(get_session)):
    return
