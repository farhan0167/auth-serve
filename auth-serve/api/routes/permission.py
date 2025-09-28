from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlmodel import Session, select

from api.dependency import get_current_user
from db.engine import get_session
from db.tables import Permission, User
from models import PermissionCreateRequest

permission_router = APIRouter(prefix="/permission", tags=["permission"])

READ = "auth.permission.read"
WRITE = "auth.permission.write"
DELETE = "auth.permission.delete"
ALL = "auth.permission.all"


@permission_router.get("/", response_model=List[Permission])
async def get_permissions(
    service: Optional[str] = Query(default=None),
    resource: Optional[str] = Query(default=None),
    slug: Optional[str] = Query(default=None),
    current_user: User = Security(get_current_user, scopes=[READ, ALL]),
    db: Session = Depends(get_session),
):
    org_id = current_user.org_id
    stmt = select(Permission).where(Permission.org_id == org_id)
    if service:
        stmt = stmt.where(Permission.service == service)
    if resource:
        stmt = stmt.where(Permission.resource == resource)
    if slug:
        if slug.endswith("*"):
            stmt = stmt.where(Permission.slug.startswith(slug[:-1]))
        else:
            stmt = stmt.where(Permission.slug == slug)

    permissions = db.exec(stmt).all()
    return permissions


@permission_router.post("/")
async def create_permission(
    permission: PermissionCreateRequest,
    current_user: User = Security(get_current_user, scopes=[WRITE, ALL]),
    db: Session = Depends(get_session),
):
    org_id = current_user.org_id
    try:
        slug = f"{permission.service}.{permission.resource}.{permission.action.value}"
        permission = Permission(
            slug=slug,
            org_id=org_id,
            **permission.model_dump(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    db.add(permission)
    db.commit()
    return permission


@permission_router.delete("/")
async def delete_permission(
    permission_id: int,
    current_user: User = Security(get_current_user, scopes=[DELETE, ALL]),
    db: Session = Depends(get_session),
):
    org_id = current_user.org_id
    permission = db.exec(
        select(Permission).where(
            Permission.id == permission_id, Permission.org_id == org_id
        )
    ).one_or_none()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with id {permission_id} not found",
        )
    db.delete(permission)
    db.commit()
    return permission
