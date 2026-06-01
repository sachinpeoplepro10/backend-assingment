from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    is_completed: Optional[bool] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    is_completed: bool
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = {"from_attributes": True}
