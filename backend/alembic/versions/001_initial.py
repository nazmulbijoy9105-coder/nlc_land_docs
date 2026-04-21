"""initial land evidence schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS land_evidence")

    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('full_name_bn', sa.String(255), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), default='user'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('preferred_lang', sa.String(5), default='en'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        schema='land_evidence',
    )
    op.create_index('ix_land_evidence_users_email', 'users', ['email'], schema='land_evidence')

    op.create_table(
        'cases',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=False), sa.ForeignKey('land_evidence.users.id'), nullable=False),
        sa.Column('case_ref', sa.String(50), unique=True, nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('property_type', sa.String(100), nullable=True),
        sa.Column('property_address', sa.Text, nullable=True),
        sa.Column('district', sa.String(100), nullable=True),
        sa.Column('upazila', sa.String(100), nullable=True),
        sa.Column('plan', sa.String(20), default='basic'),
        sa.Column('status', sa.String(30), default='draft'),
        sa.Column('overall_risk_band', sa.String(10), nullable=True),
        sa.Column('overall_risk_score', sa.Float, nullable=True),
        sa.Column('risk_hash', sa.String(64), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        schema='land_evidence',
    )

    op.create_table(
        'documents',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('case_id', UUID(as_uuid=False), sa.ForeignKey('land_evidence.cases.id'), nullable=False),
        sa.Column('doc_type', sa.String(100), nullable=False),
        sa.Column('doc_name', sa.String(500), nullable=False),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('ocr_text', sa.Text, nullable=True),
        sa.Column('ocr_text_bn', sa.Text, nullable=True),
        sa.Column('extracted_dates', sa.JSON, nullable=True),
        sa.Column('extracted_parties', sa.JSON, nullable=True),
        sa.Column('doc_risk_band', sa.String(10), nullable=True),
        sa.Column('doc_risk_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        schema='land_evidence',
    )

    op.create_table(
        'analysis_results',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('case_id', UUID(as_uuid=False), sa.ForeignKey('land_evidence.cases.id'), nullable=False),
        sa.Column('check_id', sa.Integer, nullable=False),
        sa.Column('check_name', sa.String(200), nullable=False),
        sa.Column('check_name_bn', sa.String(200), nullable=False),
        sa.Column('status', sa.String(10), nullable=False),
        sa.Column('risk_band', sa.String(10), nullable=False),
        sa.Column('risk_score', sa.Float, nullable=False),
        sa.Column('finding_en', sa.Text, nullable=False),
        sa.Column('finding_bn', sa.Text, nullable=False),
        sa.Column('recommendation_en', sa.Text, nullable=True),
        sa.Column('recommendation_bn', sa.Text, nullable=True),
        sa.Column('legal_refs', sa.JSON, nullable=True),
        sa.Column('raw_ai_response', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        schema='land_evidence',
    )

    op.create_table(
        'payments',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('case_id', UUID(as_uuid=False), sa.ForeignKey('land_evidence.cases.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=False), sa.ForeignKey('land_evidence.users.id'), nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(5), default='BDT'),
        sa.Column('method', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('transaction_id', sa.String(255), nullable=True),
        sa.Column('gateway_ref', sa.String(255), nullable=True),
        sa.Column('payment_number', sa.String(20), nullable=True),
        sa.Column('bank_ref', sa.String(255), nullable=True),
        sa.Column('proof_path', sa.String(1000), nullable=True),
        sa.Column('admin_note', sa.Text, nullable=True),
        sa.Column('confirmed_by', sa.String(255), nullable=True),
        sa.Column('confirmed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        schema='land_evidence',
    )

    op.create_table(
        'reports',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('case_id', UUID(as_uuid=False), sa.ForeignKey('land_evidence.cases.id'), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('lang', sa.String(5), default='bilingual'),
        sa.Column('hash_chain', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        schema='land_evidence',
    )

def downgrade() -> None:
    for table in ['reports', 'payments', 'analysis_results', 'documents', 'cases', 'users']:
        op.drop_table(table, schema='land_evidence')
    op.execute("DROP SCHEMA IF EXISTS land_evidence CASCADE")
