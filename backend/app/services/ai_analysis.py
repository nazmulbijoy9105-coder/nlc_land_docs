import json
import re
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

FORENSIC_PROMPT = """
You are a Bangladesh property law forensic AI expert at Neum Lex Counsel.
Analyze the following OCR-extracted text from property documents.

Return ONLY a valid JSON object (no markdown, no preamble) with these exact keys:

{
  "forgery_detected": boolean,
  "signature_anomaly": boolean,
  "khatian_chain_complete": boolean,
  "khatian_chain_gaps": number (0-5),
  "baya_chain_gaps": number (0-5),
  "mutation_document_present": boolean,
  "mutation_name_mismatch": boolean,
  "timeline_contradictions": number (0-5),
  "overlapping_documents": boolean,
  "rajuk_approval_present": boolean,
  "dap_compliant": boolean,
  "developer_redma_registered": boolean,
  "mortgage_lien_found": boolean,
  "artha_rin_case_found": boolean,
  "land_classification_issue": boolean,
  "boundary_dispute_probability": number (0-100),
  "price_anomaly_detected": boolean,
  "stamp_seal_issue": boolean,
  "nrb_foreign_party": boolean,
  "nrb_eligibility_issue": boolean,
  "extracted_dates": [list of dates found],
  "extracted_parties": [list of party names],
  "property_description": string,
  "key_concerns_en": [list of top concerns in English],
  "key_concerns_bn": [list of top concerns in Bengali],
  "legal_opinion_summary_en": string (2-3 sentences),
  "legal_opinion_summary_bn": string (2-3 sentences)
}

Document types provided: {doc_types}
Property type: {property_type}
District: {district}

Document text:
{ocr_text}
"""

async def analyze_documents(
    ocr_text: str,
    doc_types: list[str],
    property_type: str,
    district: str,
) -> dict:
    prompt = FORENSIC_PROMPT.format(
        ocr_text=ocr_text[:12000],  # Token limit
        doc_types=", ".join(doc_types),
        property_type=property_type,
        district=district,
    )
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown fences if present
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except Exception as e:
        # Return safe defaults on failure
        return {
            "forgery_detected": False,
            "signature_anomaly": False,
            "khatian_chain_complete": False,
            "khatian_chain_gaps": 1,
            "baya_chain_gaps": 1,
            "mutation_document_present": False,
            "mutation_name_mismatch": False,
            "timeline_contradictions": 0,
            "overlapping_documents": False,
            "rajuk_approval_present": False,
            "dap_compliant": True,
            "developer_redma_registered": False,
            "mortgage_lien_found": False,
            "artha_rin_case_found": False,
            "land_classification_issue": False,
            "boundary_dispute_probability": 10,
            "price_anomaly_detected": False,
            "stamp_seal_issue": False,
            "nrb_foreign_party": False,
            "nrb_eligibility_issue": False,
            "extracted_dates": [],
            "extracted_parties": [],
            "property_description": "Unable to parse — manual review required",
            "key_concerns_en": [f"AI analysis error: {str(e)}"],
            "key_concerns_bn": ["বিশ্লেষণ ত্রুটি — ম্যানুয়াল পর্যালোচনা প্রয়োজন"],
            "legal_opinion_summary_en": "Document analysis incomplete due to technical error. Manual legal review required.",
            "legal_opinion_summary_bn": "প্রযুক্তিগত ত্রুটির কারণে বিশ্লেষণ অসম্পূর্ণ।",
        }
