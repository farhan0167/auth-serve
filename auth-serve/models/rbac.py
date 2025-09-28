import datetime
from enum import Enum
from typing import List, Optional

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
    all = "all"


class RoleBase(SQLModel):
    name: str
    type: RoleType = Field(default=RoleType.system)


class PermissionBase(SQLModel):
    action: PermissionActions = Field(default=None)
    service: str
    resource: str
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None


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

class AssignRoleRequest(BaseModel):
    role_name: str
    username: str
    
class RoleCreateRequest(RoleBase):
    type: RoleType = Field(default=RoleType.custom)
    
class AttachPermimissionToRoleRequest(BaseModel):
    role_id: int
    permission_slug: str
    
class PermissionCreateRequest(BaseModel):
    service: str = Field(default="auth")
    resource: str
    action: PermissionActions = Field(default=PermissionActions.read)
    description: Optional[str] = None
    