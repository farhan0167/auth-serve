import datetime
import uuid
from typing import Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, UniqueConstraint

from models import (
    APIKeyBase,
    OrganizationBase,
    PermissionBase,
    ProjectBase,
    RoleBase,
    UserBase,
)


class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    org_id: uuid.UUID = Field(foreign_key="organization.id")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), default=datetime.datetime.utcnow),
    )


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    org_id: uuid.UUID = Field(foreign_key="organization.id")
    is_active: bool = Field(default=True)


class Role(RoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    __table_args__ = (UniqueConstraint("name", "type", name="uq_role_name_type"),)


class Permission(PermissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class APIKey(APIKeyBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id")


class UserRole(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)

    user: "User" = Relationship()
    role: "Role" = Relationship()


class RolePermission(SQLModel, table=True):
    role_id: int = Field(foreign_key="role.id", primary_key=True)
    permission_id: int = Field(foreign_key="permission.id", primary_key=True)

    role: "Role" = Relationship()
    permission: "Permission" = Relationship()
