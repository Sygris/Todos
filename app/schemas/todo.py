from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str


class TodoRead(BaseModel):
    id: int
    title: str
    completed: bool


class TodoUpdate(BaseModel):
    title: str | None
    completed: bool | None
