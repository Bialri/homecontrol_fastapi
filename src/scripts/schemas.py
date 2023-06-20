from pydantic import BaseModel, validator, ValidationError
import datetime


class DeviceCreateSchema(BaseModel):
    name: str
    secret: str


class DevicesResponseSchema(DeviceCreateSchema):
    class Config:
        orm_mode = True


class ActionResponseSchema(BaseModel):
    id: int
    name: str
    device_type: int

    class Config:
        orm_mode = True


class ActionCreateSchema(BaseModel):
    name: str
    device_type: int
    secret: str


class ScriptActionBaseSchema(BaseModel):
    device_id: int
    latency: datetime.timedelta
    action_id: int

    @validator('latency')
    def in_multiple_of_5(cls, value):
        if value.total_seconds() % 5:
            raise ValidationError('latency must be divisible by 5')
        return value


class ScriptActionCreateSchema(ScriptActionBaseSchema):
    script_id: int


class ScriptActionResponseSchema(ScriptActionBaseSchema):
    id: int

    class Config:
        orm_mode = True


class ScriptActionUpdateSchema(ScriptActionBaseSchema):
    device_id: int | None
    latency: datetime.timedelta | None
    action_id: int | None
    script_id: int | None


class ScriptCreateSchema(BaseModel):
    name: str
    time: datetime.time

    @validator('time')
    def in_multiple_of_5(cls, value):
        if value.second % 5:
            raise ValidationError("time must be divisible by 5")
        return value


class ScriptResponseSchema(ScriptCreateSchema):
    id: int

    class Config:
        orm_mode = True


class ScriptUpdateSchema(ScriptCreateSchema):
    name: str | None
    time: datetime.time | None
