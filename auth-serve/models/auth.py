import uuid

from sqlmodel import SQLModel
from pydantic import BaseModel

from .organization import OrganizationBase
from .users import UserBase


class SignupRequest(SQLModel):
    user: UserBase
    org: OrganizationBase

class SignupResponse(SQLModel):
    user_id: uuid.UUID
    org_id: uuid.UUID

class Token(BaseModel):
    access_token: str
    token_type: str