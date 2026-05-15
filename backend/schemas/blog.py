from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    content: str = ""
    summary: Optional[str] = ""
    category: Optional[str] = "未分类"
    tags: Optional[str] = ""
    is_published: Optional[bool] = True


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_published: Optional[bool] = None


class BlogOut(BaseModel):
    id: int
    title: str
    content: str
    summary: Optional[str]
    category: Optional[str]
    tags: Optional[str]
    is_published: bool
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogListOut(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    category: Optional[str]
    tags: Optional[str]
    is_published: bool
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
