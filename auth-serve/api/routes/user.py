from fastapi import APIRouter, Depends
from sqlmodel import Session

from db.engine import get_session

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.post("/signup")
async def signup(db: Session = Depends(get_session)):
    return

@user_router.post("/login")
async def login(db: Session = Depends(get_session)):
    return

@user_router.post("/invite")
async def invite(db: Session = Depends(get_session)):
    return