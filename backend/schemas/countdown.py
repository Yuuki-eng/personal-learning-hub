from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CountdownCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    target_datetime: datetime
    color: Optional[str] = "#e8927c"


class CountdownUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_datetime: Optional[datetime] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class CountdownOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    target_datetime: datetime
    color: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
