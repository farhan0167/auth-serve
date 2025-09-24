import os
from sqlmodel import Session, SQLModel, create_engine

from config.settings import settings
import db.tables

DATABASE_URL = (
    f"postgresql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session