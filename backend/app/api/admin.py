from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.models import User, Case, Payment, Report, AnalysisResult

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_cases = (await db.execute(select(func.count(Case.id)))).scalar()
    completed = (await db.execute(select(func.count(Case.id)).where(Case.status == "completed"))).scalar()
    pending_pay = (await db.execute(select(func.count(Payment.id)).where(Payment.status == "pending"))).scalar()
    total_revenue = (await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == "confirmed")
    )).scalar() or 0

    # Risk distribution
    for band in ["GREEN", "YELLOW", "RED", "BLACK"]:
        pass
    risk_dist = {}
    for band in ["GREEN", "YELLOW", "RED", "BLACK"]:
        count = (await db.execute(
            select(func.count(Case.id)).where(Case.overall_risk_band == band)
        )).scalar()
        risk_dist[band] = count

    return {
        "total_users": total_users,
        "total_cases": total_cases,
        "completed_cases": completed,
        "pending_payments": pending_pay,
        "total_revenue_bdt": float(total_revenue),
        "risk_distribution": risk_dist,
    }

@router.get("/users")
async def list_users(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(User).order_by(User.created_at.desc()).offset(skip).limit(limit))
    users = result.scalars().all()
    return [
        {"id": u.id, "email": u.email, "full_name": u.full_name, "phone": u.phone,
         "role": u.role, "is_active": u.is_active, "created_at": u.created_at.isoformat() if u.created_at else None}
        for u in users
    ]

@router.patch("/users/{user_id}/toggle")
async def toggle_user(user_id: str, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    await db.execute(update(User).where(User.id == user_id).values(is_active=not user.is_active))
    await db.commit()
    return {"is_active": not user.is_active}

@router.get("/cases")
async def admin_cases(skip: int = 0, limit: int = 50, status: Optional[str] = None, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    q = select(Case).order_by(Case.created_at.desc()).offset(skip).limit(limit)
    if status:
        q = q.where(Case.status == status)
    result = await db.execute(q)
    cases = result.scalars().all()
    return [
        {"id": c.id, "case_ref": c.case_ref, "title": c.title, "user_id": c.user_id,
         "status": c.status, "plan": c.plan, "overall_risk_band": c.overall_risk_band,
         "overall_risk_score": c.overall_risk_score, "district": c.district,
         "created_at": c.created_at.isoformat() if c.created_at else None}
        for c in cases
    ]

@router.post("/cases/{case_id}/rerun")
async def rerun_analysis(case_id: str, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    """Admin can force re-run analysis"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(404, "Case not found")
    from app.workers.tasks import run_analysis_task
    run_analysis_task.delay(case_id)
    await db.execute(update(Case).where(Case.id == case_id).values(status="processing"))
    await db.commit()
    return {"message": "Analysis re-queued"}

@router.get("/payments")
async def admin_payments(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(Payment).order_by(Payment.created_at.desc()).offset(skip).limit(limit))
    payments = result.scalars().all()
    return [
        {"id": p.id, "case_id": p.case_id, "user_id": p.user_id, "amount": p.amount,
         "method": p.method, "status": p.status, "payment_number": p.payment_number,
         "transaction_id": p.transaction_id, "confirmed_by": p.confirmed_by,
         "created_at": p.created_at.isoformat() if p.created_at else None}
        for p in payments
    ]
