from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.plan import Plan
from schemas.plan import PlanCreate, PlanUpdate, PlanOut

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("", response_model=list[PlanOut])
async def list_plans(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Plan).order_by(desc(Plan.created_at))
    if status:
        query = query.where(Plan.status == status)
    if priority:
        query = query.where(Plan.priority == priority)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=PlanOut, status_code=201)
async def create_plan(data: PlanCreate, db: AsyncSession = Depends(get_db)):
    plan = Plan(**data.model_dump())
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.put("/{plan_id}", response_model=PlanOut)
async def update_plan(plan_id: int, data: PlanUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)
    if update_data.get("status") == "completed" and not plan.completed_at:
        plan.completed_at = datetime.utcnow()
        plan.progress = 100
    await db.commit()
    await db.refresh(plan)
    return plan


@router.delete("/{plan_id}")
async def delete_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    await db.delete(plan)
    await db.commit()
    return {"message": "deleted"}


@router.put("/{plan_id}/status", response_model=PlanOut)
async def update_status(plan_id: int, status: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan.status = status
    if status == "completed":
        plan.completed_at = datetime.utcnow()
        plan.progress = 100
    await db.commit()
    await db.refresh(plan)
    return plan
