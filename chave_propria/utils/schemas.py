from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    status: str
    msg: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInvite(BaseModel):
    email: EmailStr


class Invites(BaseModel):
    id: int
    email: str
    status: str
