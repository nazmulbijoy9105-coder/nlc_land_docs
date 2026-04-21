from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Report, Case
from app.core.config import settings
from supabase import create_client

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/case/{case_id}")
async def list_reports(case_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    case_result = await db.execute(select(Case).where(Case.id == case_id))
    case = case_result.scalar_one_or_none()
    if not case or (case.user_id != user.id and user.role not in ("admin", "superadmin")):
        raise HTTPException(403, "Access denied")
    result = await db.execute(select(Report).where(Report.case_id == case_id))
    reports = result.scalars().all()
    return [
        {"id": r.id, "report_type": r.report_type, "lang": r.lang,
         "hash_chain": r.hash_chain, "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in reports
    ]

@router.get("/download/{report_id}")
async def download_report(report_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "Report not found")
    # Verify case ownership
    case_result = await db.execute(select(Case).where(Case.id == report.case_id))
    case = case_result.scalar_one_or_none()
    if not case or (case.user_id != user.id and user.role not in ("admin", "superadmin")):
        raise HTTPException(403, "Access denied")
    # Stream PDF from Supabase
    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    try:
        pdf_bytes = sb.storage.from_(settings.SUPABASE_BUCKET).download(report.storage_path)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{case.case_ref}_report.pdf"'}
        )
    except Exception as e:
        raise HTTPException(500, f"Report download failed: {str(e)}")
