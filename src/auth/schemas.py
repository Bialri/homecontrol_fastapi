from pydantic import EmailStr, BaseModel


class UserReadSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False


class UserAuthSchema(BaseModel):
    email: EmailStr
    password: str