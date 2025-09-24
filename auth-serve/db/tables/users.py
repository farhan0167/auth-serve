import uuid

from sqlmodel import Field

from models.users import UserBase


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)