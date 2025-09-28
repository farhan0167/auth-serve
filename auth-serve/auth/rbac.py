import datetime
import uuid
from typing import Dict, List

import jwt
from sqlmodel import Session, select

from config.settings import settings
from db.tables import Permission, Role, RolePermission, UserRole
from models.rbac import JWTPayload
from utils import SecretsManager
from utils.seed import (
    ROLE_PERMISSION_MAP,
    get_system_permissions,
    get_system_roles,
)


class RBAC:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_scopes(self, user_id: uuid.UUID) -> set[str]:
        roles = self.db.exec(select(UserRole).where(UserRole.user_id == user_id)).all()

        scopes = set()
        for role in roles:
            role_permissions = self.db.exec(
                select(RolePermission).where(RolePermission.role_id == role.role_id)
            ).all()
            for role_permission in role_permissions:
                permission = role_permission.permission
                scope = permission.slug
                scopes.add(scope)
        return scopes

    async def create_access_token(
        self, user_id: uuid.UUID, requested_scopes: List[str]
    ):
        expire_after = datetime.timedelta(seconds=settings.JWT_TOKEN_EXPIRATION_TIME)
        expire = datetime.datetime.now(tz=datetime.timezone.utc) + expire_after
        scopes = await self.get_scopes(user_id)
        # Grant requested scopes only
        scopes = set(requested_scopes) & scopes
        if not scopes:
            return None
        jwt_payload = JWTPayload(
            sub=str(user_id), exp=expire, iat=datetime.datetime.now(), scopes=scopes
        )
        secret = SecretsManager().get_secret()
        return jwt.encode(jwt_payload.model_dump(), secret, algorithm="HS256")

    async def validate_access_token(self, token: str) -> Dict:
        secret = SecretsManager().get_secret()
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload

    async def seed_org_acl(self, org_id: uuid.UUID) -> dict:
        # Roles
        role_rows = [Role(**r) for r in get_system_roles(org_id)]
        self.db.add_all(role_rows)
        self.db.flush()
        role_id_by_name = {r.name: r.id for r in role_rows}

        # Permissions
        perm_rows = [Permission(**p) for p in get_system_permissions(org_id)]
        self.db.add_all(perm_rows)
        self.db.flush()
        perm_id_by_slug = {p.slug: p.id for p in perm_rows}

        # Role-Permission links
        rp_links = []
        for role_name, slugs in ROLE_PERMISSION_MAP.items():
            role_id = role_id_by_name[role_name]
            for slug in slugs:
                rp_links.append(
                    RolePermission(role_id=role_id, permission_id=perm_id_by_slug[slug])
                )
        self.db.add_all(rp_links)
        self.db.flush()

        return {"roles": role_id_by_name, "permissions": perm_id_by_slug}
