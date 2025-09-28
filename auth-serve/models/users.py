from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(unique=True)
    password: str
    primary_email: str = Field(unique=True)


class NewUserInvite(UserBase):
    role: str
