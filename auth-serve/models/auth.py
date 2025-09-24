import uuid

from sqlmodel import SQLModel

from .organization import OrganizationBase
from .users import UserBase


class SignupRequest(SQLModel):
    user: UserBase
    org: OrganizationBase

class SignupResponse(SQLModel):
    user_id: uuid.UUID
    org_id: uuid.UUID
