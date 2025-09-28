import datetime
import uuid
from typing import List, Optional

from sqlmodel import (
    Column,
    DateTime,
    Field,
    ForeignKey,
    Relationship,
    SQLModel,
    UniqueConstraint,
)

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

    user_roles: List["UserRole"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


class Role(RoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: uuid.UUID = Field(foreign_key="organization.id")
    __table_args__ = (
        UniqueConstraint("name", "type", "org_id", name="uq_role_name_type_org"),
    )

    # backref to join tables
    user_roles: List["UserRole"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )
    role_permissions: List["RolePermission"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


class Permission(PermissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: uuid.UUID = Field(foreign_key="organization.id")
    __table_args__ = (
        UniqueConstraint("slug", "org_id", name="uq_permission_slug_org"),
    )

    role_permissions: List["RolePermission"] = Relationship(
        back_populates="permission",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


class APIKey(APIKeyBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id")


class UserRole(SQLModel, table=True):
    user_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    )
    role_id: int = Field(
        sa_column=Column(ForeignKey("role.id", ondelete="CASCADE"), primary_key=True)
    )

    user: "User" = Relationship(
        back_populates="user_roles",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    role: "Role" = Relationship(
        back_populates="user_roles",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class RolePermission(SQLModel, table=True):
    role_id: int = Field(
        sa_column=Column(ForeignKey("role.id", ondelete="CASCADE"), primary_key=True)
    )
    permission_id: int = Field(
        sa_column=Column(
            ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True
        )
    )

    role: "Role" = Relationship(
        back_populates="role_permissions",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    permission: "Permission" = Relationship(
        back_populates="role_permissions",
        sa_relationship_kwargs={"passive_deletes": True},
    )
