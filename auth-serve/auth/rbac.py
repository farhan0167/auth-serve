import datetime
import uuid

import jwt
from sqlmodel import Session, select

from config.settings import settings
from db.tables import Role, RolePermission, UserRole
from models.rbac import JWTPayload
from utils import SecretsManager


class RBAC:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def assign_roles(self, user_id: uuid.UUID, role: str):
        role = self.db.exec(select(Role).where(Role.name == role)).one_or_none()
        user_role = UserRole(user_id=user_id, role_id=role.id)
        self.db.add(user_role)
        self.db.commit()

    async def get_scopes(self, user_id: uuid.UUID):
        roles = self.db.exec(select(UserRole).where(UserRole.user_id == user_id)).all()

        scopes = []
        for role in roles:
            role_permissions = self.db.exec(
                select(RolePermission).where(RolePermission.role_id == role.role_id)
            ).all()
            for role_permission in role_permissions:
                permission = role_permission.permission
                scope = permission.slug
                scopes.append(scope)
        return scopes

    async def create_access_token(self, user_id: uuid.UUID):
        expire_after = datetime.timedelta(days=settings.JWT_TOKEN_EXPIRATION_TIME)
        expire = datetime.datetime.now() + expire_after
        scopes = await self.get_scopes(user_id)
        jwt_payload = JWTPayload(
            sub=str(user_id), exp=expire, iat=datetime.datetime.now(), scopes=scopes
        )
        secret = SecretsManager().get_secret()
        return jwt.encode(jwt_payload.model_dump(), secret, algorithm="HS256")

    async def validate_access_token(self, token: str):
        secret = SecretsManager().get_secret()
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.InvalidTokenError:
            return None
        except jwt.ExpiredSignatureError:
            return None
