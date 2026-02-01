from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str | None = None


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    nickname: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
