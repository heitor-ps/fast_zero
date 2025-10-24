from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    """Default message bearer"""

    message: str


class Disgrasa(BaseModel):
    """Silly stuff"""

    disgrasa: str


class UserSchema(BaseModel):
    """Internal UserSchema"""

    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
