import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"

class RiskBand(str, enum.Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    BLACK = "BLACK"

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"
    refunded = "refunded"

class PaymentMethod(str, enum.Enum):
    bkash = "bkash"
    nagad = "nagad"
    bank = "bank"
    cash = "cash"

class CaseStatus(str, enum.Enum):
    draft = "draft"
    pending_payment = "pending_payment"
    paid = "paid"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class PlanType(str, enum.Enum):
    basic = "basic"
    standard = "standard"
    premium = "premium"

# ─── User ───────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "land_evidence"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    full_name_bn: Mapped[str] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_lang: Mapped[str] = mapped_column(String(5), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cases: Mapped[list["Case"]] = relationship("Case", back_populates="user")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user")

# ─── Case ────────────────────────────────────────────────────
class Case(Base):
    __tablename__ = "cases"
    __table_args__ = {"schema": "land_evidence"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("land_evidence.users.id"))
    case_ref: Mapped[str] = mapped_column(String(50), unique=True)  # NLC-LAND-2024-0001
    title: Mapped[str] = mapped_column(String(500))
    property_type: Mapped[str] = mapped_column(String(100))  # land, flat, commercial
    property_address: Mapped[str] = mapped_column(Text, nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=True)
    upazila: Mapped[str] = mapped_column(String(100), nullable=True)
    plan: Mapped[str] = mapped_column(String(20), default=PlanType.basic)
    status: Mapped[str] = mapped_column(String(30), default=CaseStatus.draft)
    overall_risk_band: Mapped[str] = mapped_column(String(10), nullable=True)
    overall_risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    risk_hash: Mapped[str] = mapped_column(String(64), nullable=True)  # SHA256 audit hash
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="cases")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="case")
    analysis: Mapped[list["AnalysisResult"]] = relationship("AnalysisResult", back_populates="case")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="case")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="case")

# ─── Document ────────────────────────────────────────────────
class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "land_evidence"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(ForeignKey("land_evidence.cases.id"))
    doc_type: Mapped[str] = mapped_column(String(100))  # deed, khatian, mutation, etc
    doc_name: Mapped[str] = mapped_column(String(500))
    storage_path: Mapped[str] = mapped_column(String(1000))  # Supabase storage path
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=True)
    ocr_text: Mapped[str] = mapped_column(Text, nullable=True)
    ocr_text_bn: Mapped[str] = mapped_column(Text, nullable=True)
    extracted_dates: Mapped[dict] = mapped_column(JSON, nullable=True)
    extracted_parties: Mapped[dict] = mapped_column(JSON, nullable=True)
    doc_risk_band: Mapped[str] = mapped_column(String(10), nullable=True)
    doc_risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship("Case", back_populates="documents")

# ─── Analysis Result ─────────────────────────────────────────
class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    __table_args__ = {"schema": "land_evidence"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(ForeignKey("land_evidence.cases.id"))
    check_id: Mapped[int] = mapped_column(Integer)  # 1-14
    check_name: Mapped[str] = mapped_column(String(200))
    check_name_bn: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(10))  # PASS / WARN / FAIL / NA
    risk_band: Mapped[str] = mapped_column(String(10))
    risk_score: Mapped[float] = mapped_column(Float)
    finding_en: Mapped[str] = mapped_column(Text)
    finding_bn: Mapped[str] = mapped_column(Text)
    recommendation_en: Mapped[str] = mapped_column(Text, nullable=True)
    recommendation_bn: Mapped[str] = mapped_column(Text, nullable=True)
    legal_refs: Mapped[dict] = mapped_column(JSON, nullable=True)
    raw_ai_response: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship("Case", back_populates="analysis")

# ─── Payment ─────────────────────────────────────────────────
class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {"schema": "land_evidence"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(ForeignKey("land_evidence.cases.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("land_evidence.users.id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(5), default="BDT")
    method: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default=PaymentStatus.pending)
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=True)
    gateway_ref: Mapped[str] = mapped_column(String(255), nullable=True)
    payment_number: Mapped[str] = mapped_column(String(20), nullable=True)  # bKash/Nagad number
    bank_ref: Mapped[str] = mapped_column(String(255), nullable=True)
    proof_path: Mapped[str] = mapped_column(String(1000), nullable=True)  # screenshot upload
    admin_note: Mapped[str] = mapped_column(Text, nullable=True)
    confirmed_by: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship("Case", back_populates="payments")
    user: Mapped["User"] = relationship("User", back_populates="payments")

# ─── Report ──────────────────────────────────────────────────
class Report(Base):
    __tablename__ = "reports"
    __table_args__ = {"schema": "land_evidence"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(ForeignKey("land_evidence.cases.id"))
    report_type: Mapped[str] = mapped_column(String(50))  # analysis, legal_opinion
    storage_path: Mapped[str] = mapped_column(String(1000))
    lang: Mapped[str] = mapped_column(String(5), default="bilingual")
    hash_chain: Mapped[str] = mapped_column(String(64))  # SHA256
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship("Case", back_populates="reports")
