from sqlmodel import Session, select

from db.tables import Organization, OrganizationBase, Role, User, UserBase, UserRole
from models.rbac import SystemRole


class Authentication:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def signup(self, org: OrganizationBase, user: UserBase):
        # Create org
        org = Organization(**org.model_dump())
        # Create user
        user = User(
            org_id=org.id,
            **user.model_dump()
        )
        self.db.add(org)
        self.db.add(user)
        self.db.commit()

        # Create default role
        await self.assign_role(user_id=user.id, role=SystemRole.owner.value)

        return user

    async def assign_role(self, user_id, role):
        stmt = select(Role).where(Role.name == role)
        role = self.db.exec(stmt).one()
        user_role = UserRole(user_id=user_id, role_id=role.id)
        self.db.add(user_role)
        self.db.commit()

    async def login(self):
        pass
