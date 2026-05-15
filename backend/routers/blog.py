from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.blog import Blog
from schemas.blog import BlogCreate, BlogUpdate, BlogOut, BlogListOut

router = APIRouter(prefix="/api/blogs", tags=["blogs"])


@router.get("", response_model=list[BlogListOut])
async def list_blogs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Blog).order_by(desc(Blog.updated_at))
    if category:
        query = query.where(Blog.category == category)
    if tag:
        query = query.where(Blog.tags.contains(tag))
    if keyword:
        query = query.where(
            (Blog.title.contains(keyword)) | (Blog.content.contains(keyword))
        )
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Blog.category, func.count(Blog.id))
        .group_by(Blog.category)
        .order_by(desc(func.count(Blog.id)))
    )
    return [{"name": row[0], "count": row[1]} for row in result.all()]


@router.get("/tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blog.tags).where(Blog.tags != ""))
    all_tags = []
    for row in result.scalars().all():
        all_tags.extend([t.strip() for t in row.split(",") if t.strip()])
    tag_counts = {}
    for t in all_tags:
        tag_counts[t] = tag_counts.get(t, 0) + 1
    return [{"name": k, "count": v} for k, v in sorted(tag_counts.items(), key=lambda x: -x[1])]


@router.get("/{blog_id}", response_model=BlogOut)
async def get_blog(blog_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blog).where(Blog.id == blog_id))
    blog = result.scalar_one_or_none()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog.view_count += 1
    await db.commit()
    return blog


@router.post("", response_model=BlogOut, status_code=201)
async def create_blog(data: BlogCreate, db: AsyncSession = Depends(get_db)):
    blog = Blog(**data.model_dump())
    db.add(blog)
    await db.commit()
    await db.refresh(blog)
    return blog


@router.put("/{blog_id}", response_model=BlogOut)
async def update_blog(blog_id: int, data: BlogUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blog).where(Blog.id == blog_id))
    blog = result.scalar_one_or_none()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(blog, key, value)
    blog.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(blog)
    return blog


@router.delete("/{blog_id}")
async def delete_blog(blog_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blog).where(Blog.id == blog_id))
    blog = result.scalar_one_or_none()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    await db.delete(blog)
    await db.commit()
    return {"message": "deleted"}
