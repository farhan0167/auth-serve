from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, Security, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.dependency import get_current_user
from db.engine import get_session
from db.tables import Permission, Role, RolePermission, User, UserRole
from models.rbac import (
    AssignRoleRequest,
    AttachPermimissionToRoleRequest,
    RoleCreateRequest,
    RoleType,
)

role_router = APIRouter(prefix="/role", tags=["role"])

READ = "auth.role.read"
WRITE = "auth.role.write"
DELETE = "auth.role.delete"
ALL = "auth.role.all"


@role_router.get("/", response_model=List[Role])
async def get_roles(
    current_user=Security(get_current_user, scopes=[READ, ALL]),
    db: Session = Depends(get_session),
):
    roles = db.exec(select(Role)).all()
    return roles


@role_router.post("/", response_model=Role)
async def create_role(
    role: RoleCreateRequest,
    current_user=Security(get_current_user, scopes=[WRITE, ALL]),
    db: Session = Depends(get_session),
):
    if role.type == RoleType.system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create system role",
        )
    role = Role.model_validate(role)
    db.add(role)
    db.commit()
    return role


@role_router.delete("/", response_model=Role)
async def delete_role(
    role_id: int,
    current_user=Security(get_current_user, scopes=[DELETE, ALL]),
    db: Session = Depends(get_session),
):
    role = db.exec(select(Role).where(Role.id == role_id)).one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} not found",
        )
    if role.type == RoleType.system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system role",
        )
    db.delete(role)
    db.commit()
    return role


@role_router.post("/assign")
async def assign_role(
    request: AssignRoleRequest,
    current_user=Security(get_current_user, scopes=[WRITE, ALL]),
    db: Session = Depends(get_session),
):
    user = db.exec(select(User).where(User.username == request.username)).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {request.username} not found",
        )

    role = db.exec(select(Role).where(Role.name == request.role_name)).one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with name {request.role_name} not found",
        )
    try:
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)
        db.commit()
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {request.username} already has role {request.role_name}",
        ) from e
    return Response(status_code=status.HTTP_201_CREATED)


@role_router.post("/revoke")
async def revoke_role():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@role_router.get("/{username}", response_model=List[Role])
async def get_user_roles(
    username: str,
    current_user=Security(get_current_user, scopes=[READ, ALL]),
    db: Session = Depends(get_session),
):
    user_id = db.exec(select(User.id).where(User.username == username)).one_or_none()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found",
        )
    user_roles = db.exec(select(UserRole).where(UserRole.user_id == user_id)).all()
    user_roles = [user_role.role for user_role in user_roles]
    return user_roles


@role_router.post("/attach-permission")
async def attach_permission(
    request: AttachPermimissionToRoleRequest,
    current_user=Security(get_current_user, scopes=[WRITE, ALL]),
    db: Session = Depends(get_session),
):
    permission = db.exec(
        select(Permission).where(Permission.slug == request.permission_slug)
    ).one_or_none()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with slug {request.permission_slug} not found",
        )

    role_permission = RolePermission(
        role_id=request.role_id, permission_id=permission.id
    )
    db.add(role_permission)
    db.commit()
    return Response(status_code=status.HTTP_201_CREATED)
