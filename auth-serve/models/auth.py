import uuid

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

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


class JWKSToken(BaseModel):
    kty: str = Field("RSA")
    use: str = Field("sig")
    alg: str = Field("RS256")
    kid: str
    n: str
    e: str
