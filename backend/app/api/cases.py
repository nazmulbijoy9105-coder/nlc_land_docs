from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Case, AnalysisResult, Report

router = APIRouter(prefix="/cases", tags=["Cases"])

def gen_ref():
    from datetime import date
    seq = str(uuid.uuid4().int)[:4]
    return f"NLC-LAND-{date.today().year}-{seq}"

class CaseIn(BaseModel):
    title: str
    property_type: str = "land"
    property_address: Optional[str] = None
    district: Optional[str] = None
    upazila: Optional[str] = None
    plan: str = "basic"
    notes: Optional[str] = None

@router.post("/")
async def create_case(body: CaseIn, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    case = Case(
        id=str(uuid.uuid4()),
        user_id=user.id,
        case_ref=gen_ref(),
        title=body.title,
        property_type=body.property_type,
        property_address=body.property_address,
        district=body.district,
        upazila=body.upazila,
        plan=body.plan,
        notes=body.notes,
        status="pending_payment",
    )
    db.add(case)
    await db.commit()
    return {"id": case.id, "case_ref": case.case_ref, "status": case.status}

@router.get("/")
async def list_cases(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(Case).where(Case.user_id == user.id).order_by(Case.created_at.desc())
    )
    cases = result.scalars().all()
    return [
        {
            "id": c.id, "case_ref": c.case_ref, "title": c.title,
            "status": c.status, "plan": c.plan,
            "overall_risk_band": c.overall_risk_band,
            "overall_risk_score": c.overall_risk_score,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "completed_at": c.completed_at.isoformat() if c.completed_at else None,
        }
        for c in cases
    ]

@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(404, "Case not found")
    if case.user_id != user.id and user.role not in ("admin", "superadmin"):
        raise HTTPException(403, "Access denied")

    # Analysis results
    ar_result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.case_id == case_id).order_by(AnalysisResult.check_id)
    )
    analysis = ar_result.scalars().all()

    # Reports
    rpt_result = await db.execute(select(Report).where(Report.case_id == case_id))
    reports = rpt_result.scalars().all()

    return {
        "id": case.id,
        "case_ref": case.case_ref,
        "title": case.title,
        "property_type": case.property_type,
        "property_address": case.property_address,
        "district": case.district,
        "upazila": case.upazila,
        "plan": case.plan,
        "status": case.status,
        "overall_risk_band": case.overall_risk_band,
        "overall_risk_score": case.overall_risk_score,
        "risk_hash": case.risk_hash,
        "notes": case.notes,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "completed_at": case.completed_at.isoformat() if case.completed_at else None,
        "analysis": [
            {
                "check_id": a.check_id, "check_name": a.check_name, "check_name_bn": a.check_name_bn,
                "status": a.status, "risk_band": a.risk_band, "risk_score": a.risk_score,
                "finding_en": a.finding_en, "finding_bn": a.finding_bn,
                "recommendation_en": a.recommendation_en, "recommendation_bn": a.recommendation_bn,
                "legal_refs": a.legal_refs,
            }
            for a in analysis
        ],
        "reports": [
            {"id": r.id, "report_type": r.report_type, "lang": r.lang, "hash_chain": r.hash_chain,
             "created_at": r.created_at.isoformat() if r.created_at else None}
            for r in reports
        ],
    }
