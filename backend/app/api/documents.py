from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Document, Case
from app.core.config import settings
from supabase import create_client

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_TYPES = {
    "application/pdf", "image/jpeg", "image/png", "image/tiff",
    "image/jpg", "image/webp",
}
MAX_SIZE = 20 * 1024 * 1024  # 20MB

DOC_TYPES = [
    "deed", "khatian", "mutation", "baya", "rajuk_approval",
    "redma_certificate", "mortgage_document", "survey_map",
    "tax_receipt", "noc", "power_of_attorney", "succession_certificate",
    "court_order", "other",
]

@router.post("/upload")
async def upload_document(
    case_id: str = Form(...),
    doc_type: str = Form(...),
    doc_name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    # Validate case ownership
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case or (case.user_id != user.id and user.role not in ("admin", "superadmin")):
        raise HTTPException(403, "Access denied")
    if case.status not in ("pending_payment", "paid"):
        raise HTTPException(400, "Case not in uploadable state")

    # Validate file
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type {file.content_type} not allowed")
    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(400, "File too large. Max 20MB.")

    # Upload to Supabase Storage
    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    storage_path = f"cases/{case_id}/docs/{uuid.uuid4()}/{file.filename}"
    sb.storage.from_(settings.SUPABASE_BUCKET).upload(
        storage_path, file_bytes,
        {"content-type": file.content_type, "upsert": "true"}
    )

    # Create document record
    doc = Document(
        id=str(uuid.uuid4()),
        case_id=case_id,
        doc_type=doc_type,
        doc_name=doc_name,
        storage_path=storage_path,
        file_size=len(file_bytes),
        mime_type=file.content_type,
    )
    db.add(doc)
    await db.commit()

    return {"id": doc.id, "doc_name": doc_name, "doc_type": doc_type, "storage_path": storage_path}

@router.get("/case/{case_id}")
async def list_documents(case_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(Document).where(Document.case_id == case_id))
    docs = result.scalars().all()
    return [
        {"id": d.id, "doc_name": d.doc_name, "doc_type": d.doc_type,
         "file_size": d.file_size, "doc_risk_band": d.doc_risk_band,
         "created_at": d.created_at.isoformat() if d.created_at else None}
        for d in docs
    ]
