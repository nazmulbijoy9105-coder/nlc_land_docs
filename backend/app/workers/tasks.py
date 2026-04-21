import asyncio
from app.workers.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def run_analysis_task(self, case_id: str):
    """Main async analysis task triggered after payment confirmation"""
    try:
        asyncio.run(_run_analysis(case_id))
    except Exception as exc:
        raise self.retry(exc=exc)

async def _run_analysis(case_id: str):
    from sqlalchemy import select, update
    from app.core.database import AsyncSessionLocal
    from app.models.models import Case, Document, AnalysisResult, Report
    from app.services.ocr import ocr_service
    from app.services.ai_analysis import analyze_documents
    from app.services.report_gen import generate_analysis_report
    from app.rules.ilrmf_land import rule_engine, ILRMFContext
    from app.services.email import send_analysis_complete, send_black_alert_admin
    from app.core.config import settings
    from supabase import create_client
    import hashlib
    from datetime import datetime

    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    async with AsyncSessionLocal() as db:
        # Fetch case
        result = await db.execute(select(Case).where(Case.id == case_id))
        case = result.scalar_one_or_none()
        if not case:
            return

        # Update status
        await db.execute(update(Case).where(Case.id == case_id).values(status="processing"))
        await db.commit()

        # Fetch documents
        doc_result = await db.execute(select(Document).where(Document.case_id == case_id))
        documents = doc_result.scalars().all()

        # OCR each document
        all_texts = []
        doc_types = []
        for doc in documents:
            try:
                file_data = sb.storage.from_(settings.SUPABASE_BUCKET).download(doc.storage_path)
                text = ocr_service.extract_from_bytes(file_data, doc.mime_type or "application/pdf")
                await db.execute(
                    update(Document).where(Document.id == doc.id).values(ocr_text=text)
                )
                all_texts.append(text)
                doc_types.append(doc.doc_type)
            except Exception as e:
                all_texts.append(f"[OCR Failed: {e}]")

        await db.commit()
        combined_text = "\n\n===DOCUMENT SEPARATOR===\n\n".join(all_texts)

        # AI Analysis
        ai_result = await analyze_documents(
            combined_text, doc_types,
            case.property_type or "land",
            case.district or "",
        )

        # ILRMF Rules
        ctx = ILRMFContext(
            ocr_texts=all_texts,
            ai_analysis=ai_result,
            property_type=case.property_type or "land",
            district=case.district or "",
            doc_types=doc_types,
        )
        rule_results = rule_engine.run_all(ctx)
        composite_score, composite_band = rule_engine.compute_composite_score(rule_results)

        # Save analysis results
        for r in rule_results:
            ar = AnalysisResult(
                case_id=case_id,
                check_id=r.check_id,
                check_name=r.check_name,
                check_name_bn=r.check_name_bn,
                status=r.status,
                risk_band=r.risk_band,
                risk_score=r.risk_score,
                finding_en=r.finding_en,
                finding_bn=r.finding_bn,
                recommendation_en=r.recommendation_en,
                recommendation_bn=r.recommendation_bn,
                legal_refs={"refs": r.legal_refs},
                raw_ai_response=str(ai_result),
            )
            db.add(ar)

        # Generate PDF
        result_dicts = [
            {
                "check_id": r.check_id, "check_name": r.check_name,
                "check_name_bn": r.check_name_bn, "status": r.status,
                "risk_band": r.risk_band, "risk_score": r.risk_score,
                "finding_en": r.finding_en, "finding_bn": r.finding_bn,
                "recommendation_en": r.recommendation_en,
                "recommendation_bn": r.recommendation_bn,
                "legal_refs": r.legal_refs,
            }
            for r in rule_results
        ]

        # Fetch user name
        from app.models.models import User
        user_result = await db.execute(select(User).where(User.id == case.user_id))
        user = user_result.scalar_one_or_none()
        client_name = user.full_name if user else "N/A"

        pdf_bytes, content_hash = generate_analysis_report(
            case_ref=case.case_ref,
            client_name=client_name,
            property_address=case.property_address or case.district or "N/A",
            analysis_results=result_dicts,
            composite_score=composite_score,
            composite_band=composite_band,
            ai_summary_en=ai_result.get("legal_opinion_summary_en", ""),
            ai_summary_bn=ai_result.get("legal_opinion_summary_bn", ""),
            key_concerns_en=ai_result.get("key_concerns_en", []),
            key_concerns_bn=ai_result.get("key_concerns_bn", []),
        )

        # Upload PDF
        pdf_path = f"reports/{case_id}/{case.case_ref}_analysis.pdf"
        sb.storage.from_(settings.SUPABASE_BUCKET).upload(
            pdf_path, pdf_bytes, {"content-type": "application/pdf", "upsert": "true"}
        )

        # Save report record
        report = Report(
            case_id=case_id,
            report_type="analysis",
            storage_path=pdf_path,
            lang="bilingual",
            hash_chain=content_hash,
        )
        db.add(report)

        # Update case
        risk_hash = hashlib.sha256(f"{case_id}{composite_band}{composite_score}".encode()).hexdigest()
        await db.execute(
            update(Case).where(Case.id == case_id).values(
                status="completed",
                overall_risk_band=composite_band,
                overall_risk_score=composite_score,
                risk_hash=risk_hash,
                completed_at=datetime.utcnow(),
            )
        )
        await db.commit()

        # Emails
        if user:
            send_analysis_complete(user.email, user.full_name, case.case_ref, composite_band, composite_score)
            if composite_band == "BLACK":
                send_black_alert_admin("nazmulbijoy9105@gmail.com", case.case_ref, user.full_name)
