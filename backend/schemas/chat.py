from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: Optional[str] = "新对话"


class SessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class AISettingsUpdate(BaseModel):
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    model_name: Optional[str] = None
    system_prompt: Optional[str] = None
    user_profile: Optional[str] = None
    embedding_model: Optional[str] = None


class AISettingsOut(BaseModel):
    id: int
    api_key: str
    api_base_url: Optional[str]
    model_name: Optional[str]
    system_prompt: Optional[str]
    user_profile: Optional[str]
    embedding_model: Optional[str]

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: int
    content: str


class DocumentOut(BaseModel):
    id: int
    name: str
    file_path: str
    chunks_count: int
    created_at: datetime
