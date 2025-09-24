from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    username: str = Field(unique=True)
    password: str
    primary_email: str = Field(unique=True)