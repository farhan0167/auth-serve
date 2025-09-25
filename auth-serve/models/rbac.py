import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class RoleType(str, Enum):
    system = "system"
    custom = "custom"

class SystemRole(str, Enum):
    owner = "owner"
    admin = "admin"
    user = "user"

class PermissionActions(str, Enum):
    read = "read"
    write = "write"
    delete = "delete"
    create = "create"


class RoleBase(SQLModel):
    name: str
    type: RoleType = Field(default=RoleType.system)

class PermissionBase(SQLModel):
    action: PermissionActions = Field(default=None)
    resource: str
    namespace: str

class APIKeyBase(SQLModel):
    name: str
    description: str
    key: str = Field(unique=True, index=True)
    active: bool
    last_used: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    
class JWTPayload(BaseModel):
    sub: str
    exp: datetime.datetime
    iat: datetime.datetime
    scopes: List[str]
    
