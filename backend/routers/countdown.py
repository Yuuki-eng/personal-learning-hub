from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.countdown import Countdown
from schemas.countdown import CountdownCreate, CountdownUpdate, CountdownOut

router = APIRouter(prefix="/api/countdowns", tags=["countdowns"])


@router.get("", response_model=list[CountdownOut])
async def list_countdowns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Countdown).order_by(desc(Countdown.target_datetime)))
    return result.scalars().all()


@router.post("", response_model=CountdownOut, status_code=201)
async def create_countdown(data: CountdownCreate, db: AsyncSession = Depends(get_db)):
    cd = Countdown(**data.model_dump())
    db.add(cd)
    await db.commit()
    await db.refresh(cd)
    return cd


@router.put("/{cd_id}", response_model=CountdownOut)
async def update_countdown(cd_id: int, data: CountdownUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Countdown).where(Countdown.id == cd_id))
    cd = result.scalar_one_or_none()
    if not cd:
        raise HTTPException(status_code=404, detail="Countdown not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cd, key, value)
    await db.commit()
    await db.refresh(cd)
    return cd


@router.delete("/{cd_id}")
async def delete_countdown(cd_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Countdown).where(Countdown.id == cd_id))
    cd = result.scalar_one_or_none()
    if not cd:
        raise HTTPException(status_code=404, detail="Countdown not found")
    await db.delete(cd)
    await db.commit()
    return {"message": "deleted"}
