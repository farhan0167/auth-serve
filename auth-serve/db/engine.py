from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import Session, SQLModel, create_engine

import db.tables
from config.settings import settings
from utils.seed import role_permission, system_permissions, system_roles

DATABASE_URL = (
    f"postgresql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

    def insert_into_db(
        table: SQLModel, rows: list[dict], index_elements: list[str], session: Session
    ):
        stmt = pg_insert(table).values(rows)
        stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)
        session.exec(stmt)

    # Seed system roles, permissions, and role_permissions
    with Session(engine) as session:
        insert_into_db(db.tables.Role, system_roles, ["id"], session)
        insert_into_db(db.tables.Permission, system_permissions, ["id"], session)
        insert_into_db(
            db.tables.RolePermission,
            role_permission,
            ["role_id", "permission_id"],
            session,
        )
        session.commit()


def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
