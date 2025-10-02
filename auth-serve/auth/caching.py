import uuid

from sqlmodel import Session

from db.tables import User
from utils.redis_client import RedisClient


def k_user(user_id: uuid.UUID):
    return f"user:{user_id}"


def k_user_roles(org_id: uuid.UUID, user_id: uuid.UUID):
    return f"user_roles:{org_id}:{user_id}"


def k_role_perm(org_id: uuid.UUID, role: str):
    return f"role_perm:{org_id}:{role}"


class RBACCache:
    def __init__(self, db: Session) -> None:
        self.redis_client = RedisClient()
        self.db = db

    def pipeline(self):
        """Return a redis pipeline object"""
        return self.redis_client.pipeline()

    async def get_user(self, user_id: uuid.UUID):
        key = k_user(user_id)
        return await self.redis_client.get_dict(key)

    async def set_user(self, user_id: uuid.UUID, user: User):
        key = k_user(user_id)
        await self.redis_client.set_dict(key, user.model_dump())

    async def get_user_roles(self, org_id: uuid.UUID, user_id: uuid.UUID):
        user_roles_key = k_user_roles(org_id, user_id)
        return await self.redis_client.smembers(user_roles_key)

    async def get_role_permissions(self, org_id: uuid.UUID, role: str):
        role_perm_key = k_role_perm(org_id, role)
        return await self.redis_client.smembers(role_perm_key)

    async def get_scopes(self, org_id: uuid.UUID, user_id: uuid.UUID) -> set[str]:
        user_roles = await self.get_user_roles(org_id, user_id)
        if not user_roles:
            return None
        scopes = set()
        for role in user_roles:
            permissions = await self.get_role_permissions(org_id, role)
            if not permissions:
                continue
            scopes.update(permissions)
        return scopes if scopes else None
