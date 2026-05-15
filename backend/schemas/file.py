from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FolderCreate(BaseModel):
    name: str
    folder_id: Optional[int] = None


class FileRename(BaseModel):
    name: str


class FileOut(BaseModel):
    id: int
    name: str
    original_name: Optional[str]
    file_path: Optional[str]
    file_size: int
    mime_type: Optional[str]
    folder_id: Optional[int]
    is_folder: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StorageInfo(BaseModel):
    total_files: int
    total_folders: int
    total_size: int
