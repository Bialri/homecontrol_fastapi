from pydantic import BaseModel
import datetime

class DevicesResponseSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class DeviceCreateSchema(BaseModel):
    name: str
    secret: str


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


class ScriptActionResponseSchema(BaseModel):
    id: int
    device_id: int
    latency: datetime.timedelta
    action_id: int

    class Config:
        orm_mode = True


class ScriptActionCreateSchema(BaseModel):
    device_id: int
    latency: datetime.timedelta
    action_id: int
    script_id: int

class ScriptActionUpdateSchema(BaseModel):
    device_id: int | None
    latency: datetime.timedelta | None
    action_id: int | None
    script_id: int | None

class ScriptResponseSchema(BaseModel):
    id: int
    name: str
    time: datetime.time

    class Config:
        orm_mode = True


class ScriptCreateSchema(BaseModel):
    name: str
    time: datetime.time


class ScriptUpdateSchema(BaseModel):
    name: str | None
    time: datetime.time | None
