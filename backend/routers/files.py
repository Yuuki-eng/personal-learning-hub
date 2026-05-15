import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.file import FileItem
from schemas.file import FolderCreate, FileRename, FileOut, StorageInfo
from config import UPLOAD_DIR

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("", response_model=list[FileOut])
async def list_files(folder_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(FileItem)
    if folder_id is not None:
        query = query.where(FileItem.folder_id == folder_id)
    else:
        query = query.where(FileItem.folder_id.is_(None))
    query = query.order_by(FileItem.is_folder.desc(), FileItem.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/upload", response_model=FileOut, status_code=201)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    folder_id: int = Form(None),
    db: AsyncSession = Depends(get_db),
):
    date_dir = datetime.utcnow().strftime("%Y%m")
    save_dir = UPLOAD_DIR / date_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = save_dir / unique_name

    total_size = 0
    with open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            total_size += len(chunk)
            f.write(chunk)

    item = FileItem(
        name=file.filename,
        original_name=file.filename,
        file_path=str(file_path),
        file_size=total_size,
        mime_type=file.content_type,
        folder_id=folder_id,
        is_folder=False,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.post("/folder", response_model=FileOut, status_code=201)
async def create_folder(data: FolderCreate, db: AsyncSession = Depends(get_db)):
    folder = FileItem(
        name=data.name,
        is_folder=True,
        folder_id=data.folder_id,
    )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


@router.get("/storage", response_model=StorageInfo)
async def get_storage(db: AsyncSession = Depends(get_db)):
    files_result = await db.execute(
        select(func.count(FileItem.id)).where(FileItem.is_folder == False)
    )
    folders_result = await db.execute(
        select(func.count(FileItem.id)).where(FileItem.is_folder == True)
    )
    size_result = await db.execute(
        select(func.coalesce(func.sum(FileItem.file_size), 0)).where(FileItem.is_folder == False)
    )
    return StorageInfo(
        total_files=files_result.scalar(),
        total_folders=folders_result.scalar(),
        total_size=size_result.scalar(),
    )


@router.get("/{file_id}/download")
async def download_file(file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileItem).where(FileItem.id == file_id))
    item = result.scalar_one_or_none()
    if not item or item.is_folder:
        raise HTTPException(status_code=404, detail="File not found")
    if not os.path.exists(item.file_path):
        raise HTTPException(status_code=404, detail="File missing from disk")
    return FileResponse(
        item.file_path,
        filename=item.original_name or item.name,
        media_type=item.mime_type or "application/octet-stream",
    )


@router.get("/{file_id}/stream")
async def stream_file(file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileItem).where(FileItem.id == file_id))
    item = result.scalar_one_or_none()
    if not item or item.is_folder:
        raise HTTPException(status_code=404, detail="File not found")
    if not os.path.exists(item.file_path):
        raise HTTPException(status_code=404, detail="File missing from disk")
    return FileResponse(
        item.file_path,
        media_type=item.mime_type or "application/octet-stream",
    )


@router.put("/{file_id}", response_model=FileOut)
async def rename_file(file_id: int, data: FileRename, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileItem).where(FileItem.id == file_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="File not found")
    item.name = data.name
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{file_id}")
async def delete_file(file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileItem).where(FileItem.id == file_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="File not found")
    if not item.is_folder and item.file_path and os.path.exists(item.file_path):
        os.remove(item.file_path)
    if item.is_folder:
        children = await db.execute(select(FileItem).where(FileItem.folder_id == file_id))
        for child in children.scalars().all():
            await delete_file(child.id, db)
    await db.delete(item)
    await db.commit()
    return {"message": "deleted"}
