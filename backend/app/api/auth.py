"""
Auth routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
import uuid
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_token
from app.models.models import User
from app.services.email import send_welcome

router = APIRouter(prefix="/auth", tags=["Auth"])

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    full_name_bn: str = ""
    phone: str = ""
    preferred_lang: str = "en"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(body: RegisterIn, bg: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        full_name=body.full_name,
        full_name_bn=body.full_name_bn,
        phone=body.phone,
        preferred_lang=body.preferred_lang,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.commit()
    bg.add_task(send_welcome, body.email, body.full_name)
    token = create_token({"sub": user.id, "role": user.role})
    return {"token": token, "user": {"id": user.id, "email": user.email, "name": user.full_name, "role": user.role}}

@router.post("/login")
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(403, "Account disabled")
    token = create_token({"sub": user.id, "role": user.role})
    return {"token": token, "user": {"id": user.id, "email": user.email, "name": user.full_name, "role": user.role, "preferred_lang": user.preferred_lang}}

@router.get("/me")
async def me(current_user=Depends(__import__("app.core.security", fromlist=["get_current_user"]).get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "full_name_bn": current_user.full_name_bn,
        "role": current_user.role,
        "preferred_lang": current_user.preferred_lang,
        "phone": current_user.phone,
    }
