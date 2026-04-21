from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.models import Payment, Case
from app.services.payment import payment_service, PLANS
from app.services.email import send_payment_pending, send_payment_confirmed
from app.core.config import settings
from supabase import create_client

router = APIRouter(prefix="/payments", tags=["Payments"])

class PaymentIn(BaseModel):
    case_id: str
    method: str  # bkash, nagad, bank, cash
    payment_number: Optional[str] = None  # bKash/Nagad number

class AdminConfirmIn(BaseModel):
    payment_id: str
    action: str  # confirm / reject
    note: Optional[str] = None

@router.get("/plans")
async def get_plans():
    return PLANS

@router.post("/initiate")
async def initiate_payment(body: PaymentIn, bg: BackgroundTasks, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(Case).where(Case.id == body.case_id))
    case = result.scalar_one_or_none()
    if not case or case.user_id != user.id:
        raise HTTPException(403, "Access denied")

    plan = PLANS.get(case.plan, PLANS["basic"])
    amount = plan["price"]

    payment = Payment(
        id=str(uuid.uuid4()),
        case_id=body.case_id,
        user_id=user.id,
        amount=amount,
        method=body.method,
        payment_number=body.payment_number,
        status="pending",
    )
    db.add(payment)
    await db.commit()

    bg.add_task(send_payment_pending, user.email, user.full_name, case.case_ref, amount, body.method)

    gateway_result = {}
    if body.method == "bkash":
        gateway_result = await payment_service.initiate_bkash(amount, case.case_ref, body.payment_number or user.phone or "")
    elif body.method == "nagad":
        gateway_result = await payment_service.initiate_nagad(amount, case.case_ref)
    elif body.method == "bank":
        gateway_result = payment_service.get_bank_instructions(amount, case.case_ref)
    elif body.method == "cash":
        gateway_result = payment_service.get_cash_instructions(amount, case.case_ref)

    return {"payment_id": payment.id, "amount": amount, "method": body.method, "gateway": gateway_result}

@router.post("/upload-proof")
async def upload_proof(
    payment_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(Payment).where(Payment.id == payment_id, Payment.user_id == user.id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(404, "Payment not found")

    file_bytes = await file.read()
    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    proof_path = f"payment-proofs/{payment_id}/{file.filename}"
    sb.storage.from_(settings.SUPABASE_BUCKET).upload(
        proof_path, file_bytes, {"content-type": file.content_type, "upsert": "true"}
    )
    await db.execute(update(Payment).where(Payment.id == payment_id).values(proof_path=proof_path))
    await db.commit()
    return {"message": "Proof uploaded successfully"}

@router.post("/admin/confirm")
async def admin_confirm(body: AdminConfirmIn, bg: BackgroundTasks, db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(Payment).where(Payment.id == body.payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(404, "Payment not found")

    if body.action == "confirm":
        await db.execute(update(Payment).where(Payment.id == body.payment_id).values(
            status="confirmed", admin_note=body.note,
            confirmed_by=admin.email, confirmed_at=datetime.utcnow()
        ))
        await db.execute(update(Case).where(Case.id == payment.case_id).values(status="paid"))
        await db.commit()

        # Fetch user and send email
        from app.models.models import User
        from sqlalchemy import select as sel
        user_result = await db.execute(sel(User).where(User.id == payment.user_id))
        user = user_result.scalar_one_or_none()
        case_result = await db.execute(sel(Case).where(Case.id == payment.case_id))
        case = case_result.scalar_one_or_none()
        if user and case:
            bg.add_task(send_payment_confirmed, user.email, user.full_name, case.case_ref)
            # Trigger analysis
            from app.workers.tasks import run_analysis_task
            run_analysis_task.delay(payment.case_id)

        return {"message": "Payment confirmed. Analysis queued."}
    else:
        await db.execute(update(Payment).where(Payment.id == body.payment_id).values(
            status="rejected", admin_note=body.note
        ))
        await db.commit()
        return {"message": "Payment rejected"}

@router.get("/admin/pending")
async def admin_pending(db: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.execute(select(Payment).where(Payment.status == "pending").order_by(Payment.created_at.desc()))
    payments = result.scalars().all()
    return [
        {"id": p.id, "case_id": p.case_id, "user_id": p.user_id, "amount": p.amount,
         "method": p.method, "payment_number": p.payment_number, "proof_path": p.proof_path,
         "created_at": p.created_at.isoformat() if p.created_at else None}
        for p in payments
    ]
