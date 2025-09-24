from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert

from config.settings import settings
import db.tables
from models.rbac import SystemRole, PermissionActions

DATABASE_URL = (
    f"postgresql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
    # Create system roles if not exist
    system_roles = [
        {"id": 1, "name": SystemRole.owner.value},
        {"id": 2, "name": SystemRole.admin.value},
        {"id": 3, "name": SystemRole.user.value},
    ]
    # Create system permissions
    system_permissions = [
        {"id": 1, "action": PermissionActions.read.value, "resource": "user", "namespace": "get_users;get_user"},
        {"id": 2, "action": PermissionActions.write.value, "resource": "user", "namespace": "update_user*"},
        {"id": 3, "action": PermissionActions.delete.value, "resource": "user", "namespace": "delete_user"},
        {"id": 4, "action": PermissionActions.create.value, "resource": "user", "namespace": "create_user"},
    ]
    
    # Create system role permissions assignments
    role_permission = [
        {"role_id": 1, "permission_id": 1},
        {"role_id": 1, "permission_id": 2},
        {"role_id": 1, "permission_id": 3},
        {"role_id": 1, "permission_id": 4},
        {"role_id": 2, "permission_id": 1},
        {"role_id": 2, "permission_id": 2},
        {"role_id": 2, "permission_id": 3},
        {"role_id": 2, "permission_id": 4},
        {"role_id": 3, "permission_id": 1},
    ]
    
    def insert_into_db(table: SQLModel, rows: list[dict], index_elements: list[str], session: Session):
        stmt = pg_insert(table).values(rows)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=index_elements
        )
        session.exec(stmt)

    with Session(engine) as session:
        insert_into_db(db.tables.Role, system_roles, ["id"], session)
        insert_into_db(db.tables.Permission, system_permissions, ["id"], session)
        insert_into_db(db.tables.RolePermission, role_permission, ["role_id", "permission_id"], session)
        
        session.commit()
        
    
def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session