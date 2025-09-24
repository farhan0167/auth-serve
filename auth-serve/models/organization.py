from enum import Enum
from typing import Dict, Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB

class OrgType(str, Enum):
    ENTERPRISE = "enterprise"
    TEAMS = "teams"

class OrganizationBase(SQLModel):
    name: str
    domain: str
    type: OrgType = Field(default=OrgType.TEAMS)
    mfa_enabled: bool = Field(default=False)
    
    
class ProjectBase(SQLModel):
    name: str
    description: str
    meta: Dict[str, Any] = Field(sa_type=JSONB)
    
    class Config:
        arbitrary_types_allowed = True