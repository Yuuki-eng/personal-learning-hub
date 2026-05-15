from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class PlanCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Optional[str] = "medium"
    deadline: Optional[date] = None


class PlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[date] = None
    progress: Optional[int] = None


class PlanOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    deadline: Optional[date]
    progress: int
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
