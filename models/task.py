from pydantic import BaseModel

class Task(BaseModel):
    title: str
    description: str | None = None
    completed: bool | None = False

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None