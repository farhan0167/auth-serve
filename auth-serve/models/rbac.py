import datetime
from enum import Enum
from typing import Literal
from sqlmodel import Field, SQLModel

class RoleType(str, Enum):
    SYSTEM = "system"
    CUSTOM = "custom"

class PermissionActions(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    CREATE = "create"
    

class RoleBase(SQLModel):
    name: str
    type: RoleType = Field(default=RoleType.SYSTEM)
    
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