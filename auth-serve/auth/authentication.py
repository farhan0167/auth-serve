from sqlmodel import Session, select

from db.tables import Organization, OrganizationBase, User, UserBase
from models.rbac import SystemRole
from utils import Hasher

from .rbac import RBAC


class Authentication:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.hasher = Hasher()
        self.rbac = RBAC(db)

    async def signup(self, org: OrganizationBase, user: UserBase):
        # Create org
        org = Organization(**org.model_dump())
        # Create user
        user = User(
            org_id=org.id,
            username=user.username,
            password=self.hasher.get_password_hash(user.password),
            primary_email=user.primary_email,
        )
        self.db.add(org)
        self.db.add(user)
        self.db.commit()

        # Create default role
        await self.rbac.assign_roles(user_id=user.id, role=SystemRole.owner.value)

        return user

    async def authenticate_user(self, username: str, password: str):
        user = self.db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            return None
        if not self.hasher.verify_password(password, user.password):
            return None
        return user
