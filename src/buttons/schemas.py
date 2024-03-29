from pydantic import BaseModel


class ButtonSchema(BaseModel):
    name: str
    status: bool

    class Config:
        orm_mode = True


class ButtonResponseSchema(BaseModel):
    id: int
    name: str
    status: bool

    class Config:
        orm_mode = True


class ButtonUpdateSchema(BaseModel):
    name: str | None
    status: bool | None


class ButtonWithTokenSchema(ButtonResponseSchema):
    token: str