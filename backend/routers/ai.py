import os
import json
import uuid
from datetime import datetime
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
from database import get_db
from models.chat import ChatSession, ChatMessage, AISettings
from models.blog import Blog
from models.plan import Plan
from schemas.chat import (
    SessionCreate, SessionOut,
    MessageCreate, MessageOut,
    AISettingsUpdate, AISettingsOut,
    ChatRequest, DocumentOut,
)
from services.ai_service import rag_service
from config import DOCUMENTS_DIR

router = APIRouter(prefix="/api/ai", tags=["ai"])


async def _get_settings(db: AsyncSession) -> AISettings:
    result = await db.execute(select(AISettings).where(AISettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = AISettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("/settings", response_model=AISettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)):
    return await _get_settings(db)


@router.put("/settings", response_model=AISettingsOut)
async def update_settings(data: AISettingsUpdate, db: AsyncSession = Depends(get_db)):
    settings = await _get_settings(db)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    await db.commit()
    await db.refresh(settings)
    return settings


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).order_by(desc(ChatSession.updated_at)))
    return result.scalars().all()


@router.post("/sessions", response_model=SessionOut, status_code=201)
async def create_session(data: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = ChatSession(title=data.title or "新对话")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
async def list_messages(session_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return result.scalars().all()


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.execute(
        ChatMessage.__table__.delete().where(ChatMessage.session_id == session_id)
    )
    await db.delete(session)
    await db.commit()
    return {"message": "deleted"}


async def _build_context(db: AsyncSession, user_message: str, settings: AISettings) -> str:
    rag_results = []
    if settings.api_key and settings.api_base_url:
        try:
            rag_results = await rag_service.search(
                user_message,
                settings.api_key,
                settings.api_base_url,
                top_k=3,
                embedding_model=settings.embedding_model or "text-embedding-3-small",
            )
        except Exception:
            pass

    blogs_count = (await db.execute(select(func.count(Blog.id)))).scalar()
    plans_count = (await db.execute(select(func.count(Plan.id)))).scalar()
    completed_count = (await db.execute(
        select(func.count(Plan.id)).where(Plan.status == "completed")
    )).scalar()

    usage = f"博客文章: {blogs_count}篇, 学习计划: {plans_count}个, 已完成: {completed_count}个"

    context_parts = []
    if settings.user_profile:
        context_parts.append(f"用户个人情况:\n{settings.user_profile}")
    context_parts.append(f"网站使用概况: {usage}")
    if rag_results:
        context_parts.append(f"相关文档资料:\n" + "\n---\n".join(rag_results))

    return "\n\n".join(context_parts)


@router.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    settings = await _get_settings(db)
    if not settings.api_key:
        raise HTTPException(status_code=400, detail="请先在设置中配置API Key")

    session_result = await db.execute(select(ChatSession).where(ChatSession.id == request.session_id))
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_msg = ChatMessage(
        session_id=request.session_id,
        role="user",
        content=request.content,
    )
    db.add(user_msg)

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == request.session_id)
        .order_by(ChatMessage.created_at)
    )
    history = result.scalars().all()

    if session.title == "新对话" and request.content:
        session.title = request.content[:30] + ("..." if len(request.content) > 30 else "")
    session.updated_at = datetime.utcnow()
    await db.commit()

    context = await _build_context(db, request.content, settings)

    system_prompt = settings.system_prompt or "你是一个个人学习助手，帮助用户解答学习问题。"
    system_content = f"{system_prompt}\n\n{context}"

    messages = [{"role": "system", "content": system_content}]
    for msg in history[-20:]:
        messages.append({"role": msg.role, "content": msg.content})

    client = AsyncOpenAI(
        api_key=settings.api_key,
        base_url=settings.api_base_url,
        timeout=120.0,
    )

    async def generate() -> AsyncGenerator[str, None]:
        full_response = ""
        try:
            stream = await client.chat.completions.create(
                model=settings.model_name or "deepseek-chat",
                messages=messages,
                stream=True,
                max_tokens=2000,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield f"data: {json.dumps({'content': text}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

        try:
            from database import async_session as _session_factory
            async with _session_factory() as save_db:
                ai_msg = ChatMessage(
                    session_id=request.session_id,
                    role="assistant",
                    content=full_response,
                )
                save_db.add(ai_msg)
                await save_db.commit()
        except Exception:
            pass

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/documents", status_code=201)
async def upload_document(file: UploadFile = FastAPIFile(...), db: AsyncSession = Depends(get_db)):
    settings = await _get_settings(db)
    if not settings.api_key or not settings.api_base_url:
        raise HTTPException(status_code=400, detail="请先在设置中配置API Key和API Base URL")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail="仅支持 PDF、TXT、MD 格式")

    save_path = DOCUMENTS_DIR / file.filename
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    try:
        chunks = await rag_service.add_document(
            str(save_path),
            file.filename,
            settings.api_key,
            settings.api_base_url,
            settings.embedding_model or "text-embedding-3-small",
        )
    except Exception as e:
        if save_path.exists():
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"文档索引失败: {str(e)}")

    return {"name": file.filename, "chunks_count": chunks}


@router.get("/documents")
async def list_documents():
    docs = rag_service.get_documents_info()
    return docs


@router.delete("/documents/{doc_name}")
async def delete_document(doc_name: str):
    removed = await rag_service.remove_by_source(doc_name)
    doc_path = DOCUMENTS_DIR / doc_name
    if doc_path.exists():
        os.remove(doc_path)
    return {"removed_chunks": removed}


@router.get("/usage-stats")
async def get_usage_stats(db: AsyncSession = Depends(get_db)):
    blogs_count = (await db.execute(select(func.count(Blog.id)))).scalar()
    plans_total = (await db.execute(select(func.count(Plan.id)))).scalar()
    plans_completed = (await db.execute(
        select(func.count(Plan.id)).where(Plan.status == "completed")
    )).scalar()
    plans_in_progress = (await db.execute(
        select(func.count(Plan.id)).where(Plan.status == "in_progress")
    )).scalar()
    sessions_count = (await db.execute(select(func.count(ChatSession.id)))).scalar()
    messages_count = (await db.execute(select(func.count(ChatMessage.id)))).scalar()
    docs = rag_service.get_documents_info()

    return {
        "blogs": blogs_count,
        "plans_total": plans_total,
        "plans_completed": plans_completed,
        "plans_in_progress": plans_in_progress,
        "chat_sessions": sessions_count,
        "chat_messages": messages_count,
        "rag_documents": len(docs),
        "rag_chunks": sum(d["chunks_count"] for d in docs),
    }


@router.get("/learning-graph")
async def get_learning_graph(db: AsyncSession = Depends(get_db)):
    categories_result = await db.execute(
        select(Blog.category, func.count(Blog.id)).group_by(Blog.category)
    )
    categories = {row[0]: row[1] for row in categories_result.all() if row[0]}

    plans_result = await db.execute(
        select(Plan.title, Plan.status, Plan.progress, Plan.priority)
        .order_by(desc(Plan.created_at))
        .limit(20)
    )
    plans = [
        {"title": r[0], "status": r[1], "progress": r[2], "priority": r[3]}
        for r in plans_result.all()
    ]

    return {
        "categories": categories,
        "recent_plans": plans,
    }
