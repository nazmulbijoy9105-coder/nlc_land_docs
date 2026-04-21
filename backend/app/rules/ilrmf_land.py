"""
ILRMF v2 — Land Evidence Rule Engine
Bangladesh Property Law — 14 Deterministic Checks
Neum Lex Counsel (NLC) Proprietary
"""
from dataclasses import dataclass, field
from typing import Optional
import re
from datetime import datetime

RISK_BANDS = {"GREEN": 0, "YELLOW": 25, "RED": 60, "BLACK": 90}

LEGAL_REFS = {
    1: ["Registration Act 1908 §17", "Evidence Act 1872 §67"],
    2: ["State Acquisition & Tenancy Act 1950", "DLRS Khatian Records"],
    3: ["Transfer of Property Act 1882 §54", "Succession Act 1925"],
    4: ["Land Acquisition Act 1894", "SAT Act 1950 §143"],
    5: ["Registration Act 1908 §23", "Limitation Act 1908"],
    6: ["Transfer of Property Act 1882 §41", "Specific Relief Act 1877"],
    7: ["RAJUK Building Rules 2008", "Town Improvement Act 1953"],
    8: ["REDMA 2010 §§3-15", "DNCC/DSCC Building Permit Rules"],
    9: ["Artha Rin Adalat Ain 2003 §5", "Mortgage Act 1882 §58"],
    10: ["Non-Agricultural Land Use Control Act 1963", "Agriculture Act 1950"],
    11: ["Survey Act 1875", "SAT Act 1950 §86"],
    12: ["Money Laundering Prevention Act 2012", "Anti-Corruption Commission Act 2004"],
    13: ["Registration Act 1908 §28", "Stamp Act 1899"],
    14: ["Foreign Exchange Regulation Act 1947 §18", "Bangladesh Investment Development Authority Act 2016"],
}

CHECK_NAMES = {
    1: ("Deed Forgery & Signature Anomaly", "দলিল জালিয়াতি ও স্বাক্ষর অসঙ্গতি"),
    2: ("CS→SA→RS→BS Khatian Chain", "সিএস→এসএ→আরএস→বিএস খতিয়ান চেইন"),
    3: ("Baya (Ownership History) Chain", "বায়া দলিল শৃঙ্খল যাচাই"),
    4: ("Mutation / Namjari Verification", "নামজারি ও মিউটেশন যাচাই"),
    5: ("Timeline Contradiction Scoring", "সময়রেখা অসঙ্গতি স্কোরিং"),
    6: ("Overlapping / Duplicate Document", "ওভারল্যাপিং ও ডুপ্লিকেট দলিল"),
    7: ("RAJUK DAP Plan Compliance", "রাজউক ড্যাপ পরিকল্পনা সম্মতি"),
    8: ("REDMA Developer Registration", "রেডমা ডেভেলপার নিবন্ধন"),
    9: ("Mortgage Lien / Artha Rin Flag", "বন্ধক দায় ও অর্থঋণ পতাকা"),
    10: ("Land Classification Check", "ভূমি শ্রেণীবিভাগ যাচাই"),
    11: ("Boundary Dispute Probability", "সীমানা বিরোধ সম্ভাবনা"),
    12: ("Payment Anomaly Detection", "মূল্য অসঙ্গতি সনাক্তকরণ"),
    13: ("Sub-Registry Stamp & Seal", "সাব-রেজিস্ট্রি স্ট্যাম্প ও সিল"),
    14: ("NRB / Foreign Ownership Eligibility", "এনআরবি বিদেশী মালিকানা যোগ্যতা"),
}

@dataclass
class RuleResult:
    check_id: int
    check_name: str
    check_name_bn: str
    status: str  # PASS / WARN / FAIL / NA
    risk_band: str
    risk_score: float
    finding_en: str
    finding_bn: str
    recommendation_en: str
    recommendation_bn: str
    legal_refs: list[str]

@dataclass
class ILRMFContext:
    ocr_texts: list[str] = field(default_factory=list)
    ai_analysis: dict = field(default_factory=dict)
    property_type: str = "land"
    district: str = ""
    doc_types: list[str] = field(default_factory=list)

class LandRuleEngine:
    """ILRMF v2 — 14-check Bangladesh property law engine"""

    def run_all(self, ctx: ILRMFContext) -> list[RuleResult]:
        results = []
        for i in range(1, 15):
            method = getattr(self, f"_check_{i}", None)
            if method:
                results.append(method(ctx))
        return results

    def compute_composite_score(self, results: list[RuleResult]) -> tuple[float, str]:
        if not results:
            return 0.0, "GREEN"
        scores = [r.risk_score for r in results]
        composite = sum(scores) / len(scores)
        # BLACK override if any single check is BLACK
        if any(r.risk_band == "BLACK" for r in results):
            return composite, "BLACK"
        if composite >= 60:
            return composite, "RED"
        if composite >= 25:
            return composite, "YELLOW"
        return composite, "GREEN"

    def _resolve_band(self, score: float) -> str:
        if score >= 90: return "BLACK"
        if score >= 60: return "RED"
        if score >= 25: return "YELLOW"
        return "GREEN"

    def _ai_flag(self, ctx: ILRMFContext, key: str, default: bool = False) -> bool:
        return ctx.ai_analysis.get(key, default)

    def _ai_score(self, ctx: ILRMFContext, key: str, default: float = 0.0) -> float:
        return float(ctx.ai_analysis.get(key, default))

    def _check_1(self, ctx: ILRMFContext) -> RuleResult:
        """Deed Forgery & Signature Anomaly"""
        n, bn = CHECK_NAMES[1]
        forgery_flag = self._ai_flag(ctx, "forgery_detected")
        sig_anomaly = self._ai_flag(ctx, "signature_anomaly")
        score = 0.0
        if forgery_flag: score += 70
        if sig_anomaly: score += 20
        status = "FAIL" if score >= 60 else ("WARN" if score >= 20 else "PASS")
        band = self._resolve_band(score)
        if forgery_flag:
            finding_en = "AI forensic analysis detected probable deed forgery. Signatures show inconsistency with authentic records."
            finding_bn = "এআই ফরেনসিক বিশ্লেষণে সম্ভাব্য দলিল জালিয়াতি সনাক্ত হয়েছে। স্বাক্ষরে অসঙ্গতি পাওয়া গেছে।"
            rec_en = "Immediately refer for forensic document examination. Do not proceed with transaction."
            rec_bn = "অবিলম্বে ফরেনসিক দলিল পরীক্ষার জন্য প্রেরণ করুন। লেনদেন স্থগিত রাখুন।"
        elif sig_anomaly:
            finding_en = "Signature patterns show minor inconsistencies. Manual verification recommended."
            finding_bn = "স্বাক্ষরের ধরনে সামান্য অসঙ্গতি রয়েছে। ম্যানুয়াল যাচাই প্রয়োজন।"
            rec_en = "Obtain certified copies and compare with sub-registry records."
            rec_bn = "সার্টিফাইড কপি সংগ্রহ করে সাব-রেজিস্ট্রি রেকর্ডের সাথে মিলান।"
        else:
            finding_en = "No forgery indicators detected in submitted documents."
            finding_bn = "জমা দেওয়া দলিলে কোনো জালিয়াতির চিহ্ন পাওয়া যায়নি।"
            rec_en = "Continue due diligence with other checks."
            rec_bn = "অন্যান্য যাচাই প্রক্রিয়া অব্যাহত রাখুন।"
        return RuleResult(1, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[1])

    def _check_2(self, ctx: ILRMFContext) -> RuleResult:
        """CS→SA→RS→BS Khatian Chain"""
        n, bn = CHECK_NAMES[2]
        chain_complete = self._ai_flag(ctx, "khatian_chain_complete", True)
        chain_gaps = self._ai_score(ctx, "khatian_chain_gaps", 0)
        score = min(chain_gaps * 20, 90)
        status = "FAIL" if score >= 60 else ("WARN" if score >= 20 else "PASS")
        band = self._resolve_band(score)
        if score >= 60:
            finding_en = f"Critical gaps found in khatian chain. {int(chain_gaps)} missing link(s) between CS, SA, RS, BS records."
            finding_bn = f"খতিয়ান চেইনে গুরুতর ফাঁক পাওয়া গেছে। {int(chain_gaps)}টি সংযোগ অনুপস্থিত।"
            rec_en = "Obtain missing khatian records from DLRS office. Verify RS khatian against BS khatian at AC Land office."
            rec_bn = "ডিএলআরএস অফিস থেকে অনুপস্থিত খতিয়ান সংগ্রহ করুন।"
        elif score >= 20:
            finding_en = "Minor gaps in khatian chain. Some records need verification."
            finding_bn = "খতিয়ান চেইনে সামান্য ফাঁক পাওয়া গেছে।"
            rec_en = "Verify RS khatian and ensure BS khatian reflects current ownership."
            rec_bn = "আরএস খতিয়ান যাচাই করুন এবং বিএস খতিয়ানে বর্তমান মালিকানা নিশ্চিত করুন।"
        else:
            finding_en = "Khatian chain CS→SA→RS→BS appears complete and consistent."
            finding_bn = "সিএস→এসএ→আরএস→বিএস খতিয়ান চেইন সম্পূর্ণ ও সামঞ্জস্যপূর্ণ।"
            rec_en = "Cross-verify BS khatian with current DC office records."
            rec_bn = "বিএস খতিয়ান বর্তমান ডিসি অফিস রেকর্ডের সাথে যাচাই করুন।"
        return RuleResult(2, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[2])

    def _check_3(self, ctx: ILRMFContext) -> RuleResult:
        """Baya Chain Gaps"""
        n, bn = CHECK_NAMES[3]
        baya_gaps = self._ai_score(ctx, "baya_chain_gaps", 0)
        score = min(baya_gaps * 25, 95)
        status = "FAIL" if score >= 60 else ("WARN" if score >= 20 else "PASS")
        band = self._resolve_band(score)
        if score >= 60:
            finding_en = f"Ownership history (baya) chain has {int(baya_gaps)} unverified transfer(s). Title cannot be confirmed clean."
            finding_bn = f"মালিকানার ইতিহাস (বায়া) চেইনে {int(baya_gaps)}টি অযাচাইকৃত হস্তান্তর রয়েছে।"
            rec_en = "Obtain full baya deed chain going back 12 years minimum per Registration Act. Verify succession via probate/heirship certificate."
            rec_bn = "ন্যূনতম ১২ বছরের সম্পূর্ণ বায়া দলিল সংগ্রহ করুন।"
        else:
            finding_en = "Baya chain shows continuous ownership history with no major gaps."
            finding_bn = "বায়া চেইনে ধারাবাহিক মালিকানার ইতিহাস পাওয়া গেছে।"
            rec_en = "Confirm latest deed registered within sub-registry jurisdiction."
            rec_bn = "সর্বশেষ দলিল সাব-রেজিস্ট্রি এখতিয়ারে নিবন্ধিত কিনা নিশ্চিত করুন।"
        return RuleResult(3, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[3])

    def _check_4(self, ctx: ILRMFContext) -> RuleResult:
        """Mutation / Namjari"""
        n, bn = CHECK_NAMES[4]
        mutation_present = self._ai_flag(ctx, "mutation_document_present", False)
        mutation_mismatch = self._ai_flag(ctx, "mutation_name_mismatch", False)
        score = 0.0
        if not mutation_present: score = 40
        if mutation_mismatch: score = max(score, 60)
        status = "FAIL" if score >= 60 else ("WARN" if score >= 20 else "PASS")
        band = self._resolve_band(score)
        if not mutation_present:
            finding_en = "Mutation/Namjari certificate not provided. Ownership transfer to current owner unverified in government records."
            finding_bn = "নামজারি সনদ সরবরাহ করা হয়নি। সরকারি রেকর্ডে মালিকানা হস্তান্তর অযাচাইকৃত।"
            rec_en = "Obtain mutation certificate from AC Land office. Verify khatian updated in owner's name."
            rec_bn = "এসি ল্যান্ড অফিস থেকে নামজারি সনদ সংগ্রহ করুন।"
        elif mutation_mismatch:
            finding_en = "Mutation record name does not match deed seller/buyer name. Discrepancy requires resolution."
            finding_bn = "নামজারি রেকর্ডের নাম দলিলের বিক্রেতা/ক্রেতার নামের সাথে মিলছে না।"
            rec_en = "File correction petition at AC Land office before proceeding."
            rec_bn = "অগ্রসর হওয়ার আগে এসি ল্যান্ড অফিসে সংশোধন আবেদন করুন।"
        else:
            finding_en = "Mutation/Namjari certificate present and consistent with deed records."
            finding_bn = "নামজারি সনদ উপস্থিত এবং দলিল রেকর্ডের সাথে সামঞ্জস্যপূর্ণ।"
            rec_en = "No action required for mutation."
            rec_bn = "নামজারির জন্য কোনো পদক্ষেপ প্রয়োজন নেই।"
        return RuleResult(4, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[4])

    def _check_5(self, ctx: ILRMFContext) -> RuleResult:
        """Timeline Contradiction"""
        n, bn = CHECK_NAMES[5]
        contradictions = self._ai_score(ctx, "timeline_contradictions", 0)
        score = min(contradictions * 30, 90)
        status = "FAIL" if score >= 60 else ("WARN" if score >= 20 else "PASS")
        band = self._resolve_band(score)
        finding_en = f"Timeline analysis found {int(contradictions)} date contradiction(s) across submitted documents." if contradictions else "Timeline analysis shows consistent dates across all documents."
        finding_bn = f"সময়রেখা বিশ্লেষণে {int(contradictions)}টি তারিখ অসঙ্গতি পাওয়া গেছে।" if contradictions else "সময়রেখা বিশ্লেষণে সকল দলিলের তারিখ সামঞ্জস্যপূর্ণ।"
        rec_en = "Cross-check all deed dates with sub-registry certified copies." if contradictions else "Timeline verified. No action required."
        rec_bn = "সকল দলিলের তারিখ সাব-রেজিস্ট্রি সার্টিফাইড কপির সাথে মিলান।" if contradictions else "সময়রেখা যাচাইকৃত।"
        return RuleResult(5, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[5])

    def _check_6(self, ctx: ILRMFContext) -> RuleResult:
        """Overlapping Documents"""
        n, bn = CHECK_NAMES[6]
        overlap = self._ai_flag(ctx, "overlapping_documents", False)
        score = 80.0 if overlap else 0.0
        status = "FAIL" if overlap else "PASS"
        band = self._resolve_band(score)
        finding_en = "Overlapping or duplicate deeds detected. Same property appears in multiple ownership claims." if overlap else "No overlapping or duplicate documents detected."
        finding_bn = "ওভারল্যাপিং বা ডুপ্লিকেট দলিল সনাক্ত হয়েছে। একই সম্পত্তিতে একাধিক মালিকানা দাবি।" if overlap else "কোনো ওভারল্যাপিং বা ডুপ্লিকেট দলিল সনাক্ত হয়নি।"
        rec_en = "Immediately halt transaction. File suit for declaration of title under Specific Relief Act." if overlap else "Proceed with confidence on uniqueness check."
        rec_bn = "অবিলম্বে লেনদেন বন্ধ করুন। স্পেসিফিক রিলিফ আইনে মালিকানা ঘোষণার মামলা করুন।" if overlap else "অনন্যতা যাচাইয়ে এগিয়ে যান।"
        return RuleResult(6, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[6])

    def _check_7(self, ctx: ILRMFContext) -> RuleResult:
        """RAJUK DAP Compliance"""
        n, bn = CHECK_NAMES[7]
        if ctx.property_type not in ("flat", "commercial", "apartment"):
            return RuleResult(7, n, bn, "NA", "GREEN", 0, "Not applicable for this property type.", "এই সম্পত্তির ধরনের জন্য প্রযোজ্য নয়।", "N/A", "প্রযোজ্য নয়।", LEGAL_REFS[7])
        rajuk_approved = self._ai_flag(ctx, "rajuk_approval_present", False)
        dap_compliant = self._ai_flag(ctx, "dap_compliant", True)
        score = 0.0
        if not rajuk_approved: score += 50
        if not dap_compliant: score += 30
        status = "FAIL" if score >= 60 else ("WARN" if score > 0 else "PASS")
        band = self._resolve_band(score)
        finding_en = "RAJUK approval documents missing or DAP non-compliance detected." if score > 0 else "RAJUK approval and DAP compliance confirmed."
        finding_bn = "রাজউক অনুমোদন অনুপস্থিত বা ড্যাপ অসামঞ্জস্য সনাক্ত হয়েছে।" if score > 0 else "রাজউক অনুমোদন এবং ড্যাপ সম্মতি নিশ্চিত।"
        rec_en = "Obtain RAJUK building plan approval and DAP clearance before purchase." if score > 0 else "Continue due diligence."
        rec_bn = "ক্রয়ের আগে রাজউক বিল্ডিং প্ল্যান অনুমোদন সংগ্রহ করুন।" if score > 0 else "যথাযথ পরিশ্রম অব্যাহত রাখুন।"
        return RuleResult(7, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[7])

    def _check_8(self, ctx: ILRMFContext) -> RuleResult:
        """REDMA Developer Registration"""
        n, bn = CHECK_NAMES[8]
        if ctx.property_type not in ("flat", "apartment"):
            return RuleResult(8, n, bn, "NA", "GREEN", 0, "Not applicable.", "প্রযোজ্য নয়।", "N/A", "প্রযোজ্য নয়।", LEGAL_REFS[8])
        redma_registered = self._ai_flag(ctx, "developer_redma_registered", False)
        score = 70.0 if not redma_registered else 0.0
        status = "FAIL" if not redma_registered else "PASS"
        band = self._resolve_band(score)
        finding_en = "Developer NOT registered under REDMA 2010. This is a statutory violation." if not redma_registered else "Developer is registered under REDMA 2010."
        finding_bn = "ডেভেলপার রেডমা ২০১০ এর অধীনে নিবন্ধিত নয়। এটি একটি বিধিবদ্ধ লঙ্ঘন।" if not redma_registered else "ডেভেলপার রেডমা ২০১০ এর অধীনে নিবন্ধিত।"
        rec_en = "Verify REDMA registration at Ministry of Housing website before signing any agreement." if not redma_registered else "Verify registration currency (not expired)."
        rec_bn = "চুক্তি স্বাক্ষরের আগে আবাসন মন্ত্রণালয়ের ওয়েবসাইটে রেডমা নিবন্ধন যাচাই করুন।" if not redma_registered else "নিবন্ধনের মেয়াদ পরীক্ষা করুন।"
        return RuleResult(8, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[8])

    def _check_9(self, ctx: ILRMFContext) -> RuleResult:
        """Mortgage Lien / Artha Rin"""
        n, bn = CHECK_NAMES[9]
        lien_found = self._ai_flag(ctx, "mortgage_lien_found", False)
        artha_rin = self._ai_flag(ctx, "artha_rin_case_found", False)
        score = 0.0
        if lien_found: score += 60
        if artha_rin: score += 30
        status = "FAIL" if score >= 60 else ("WARN" if score > 0 else "PASS")
        band = self._resolve_band(score)
        if score >= 60:
            finding_en = "Active mortgage lien and/or Artha Rin case found. Property may be encumbered."
            finding_bn = "সক্রিয় বন্ধক দায় ও/অথবা অর্থঋণ মামলা পাওয়া গেছে। সম্পত্তি দায়বদ্ধ থাকতে পারে।"
            rec_en = "Obtain bank NOC for lien discharge before transfer. Check Artha Rin court status."
            rec_bn = "হস্তান্তরের আগে লিয়েন মুক্তির জন্য ব্যাংক এনওসি সংগ্রহ করুন।"
        else:
            finding_en = "No active mortgage lien or Artha Rin case detected."
            finding_bn = "কোনো সক্রিয় বন্ধক দায় বা অর্থঋণ মামলা সনাক্ত হয়নি।"
            rec_en = "Confirm with concerned bank via written query before final registration."
            rec_bn = "চূড়ান্ত নিবন্ধনের আগে সংশ্লিষ্ট ব্যাংকের কাছে লিখিত জিজ্ঞাসা করুন।"
        return RuleResult(9, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[9])

    def _check_10(self, ctx: ILRMFContext) -> RuleResult:
        """Land Classification"""
        n, bn = CHECK_NAMES[10]
        classification_issue = self._ai_flag(ctx, "land_classification_issue", False)
        score = 50.0 if classification_issue else 0.0
        status = "WARN" if classification_issue else "PASS"
        band = self._resolve_band(score)
        finding_en = "Land classification (agricultural/non-agricultural) requires review. Conversion may be needed." if classification_issue else "Land classification appears consistent with intended use."
        finding_bn = "ভূমির শ্রেণীবিভাগ (কৃষি/অকৃষি) পর্যালোচনা প্রয়োজন।" if classification_issue else "ভূমির শ্রেণীবিভাগ উদ্দেশ্যমূলক ব্যবহারের সাথে সামঞ্জস্যপূর্ণ।"
        rec_en = "Apply for land use conversion at DC office under Non-Agricultural Land Use Control Act 1963." if classification_issue else "Classification confirmed. No action needed."
        rec_bn = "অকৃষি ভূমি ব্যবহার নিয়ন্ত্রণ আইন ১৯৬৩ এর অধীনে ডিসি অফিসে রূপান্তরের জন্য আবেদন করুন।" if classification_issue else "শ্রেণীবিভাগ নিশ্চিত।"
        return RuleResult(10, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[10])

    def _check_11(self, ctx: ILRMFContext) -> RuleResult:
        """Boundary Dispute"""
        n, bn = CHECK_NAMES[11]
        boundary_risk = self._ai_score(ctx, "boundary_dispute_probability", 0)
        score = boundary_risk
        status = "FAIL" if score >= 60 else ("WARN" if score >= 25 else "PASS")
        band = self._resolve_band(score)
        finding_en = f"Boundary dispute probability: {score:.0f}%. Survey discrepancies or neighbor disputes may exist." if score >= 25 else "Low boundary dispute risk detected."
        finding_bn = f"সীমানা বিরোধের সম্ভাবনা: {score:.0f}%।" if score >= 25 else "সীমানা বিরোধের ঝুঁকি কম।"
        rec_en = "Commission fresh survey by licensed surveyor. Compare with CS/RS maps." if score >= 25 else "Verify boundary pillars on physical inspection."
        rec_bn = "লাইসেন্সপ্রাপ্ত সার্ভেয়ার দ্বারা নতুন জরিপ করান।" if score >= 25 else "সরেজমিনে সীমানা পিলার যাচাই করুন।"
        return RuleResult(11, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[11])

    def _check_12(self, ctx: ILRMFContext) -> RuleResult:
        """Payment Anomaly"""
        n, bn = CHECK_NAMES[12]
        price_anomaly = self._ai_flag(ctx, "price_anomaly_detected", False)
        score = 55.0 if price_anomaly else 0.0
        status = "WARN" if price_anomaly else "PASS"
        band = self._resolve_band(score)
        finding_en = "Declared consideration value significantly below market rate. Possible under-valuation or money laundering risk." if price_anomaly else "Declared consideration appears within reasonable market range."
        finding_bn = "ঘোষিত বিক্রয়মূল্য বাজারমূল্যের তুলনায় উল্লেখযোগ্যভাবে কম। অর্থ পাচারের ঝুঁকি থাকতে পারে।" if price_anomaly else "ঘোষিত মূল্য বাজারমূল্যের সাথে সামঞ্জস্যপূর্ণ।"
        rec_en = "Ensure stamp duty calculated on actual market value. Consult AC Land for official valuation." if price_anomaly else "No action required for payment anomaly."
        rec_bn = "প্রকৃত বাজারমূল্যে স্ট্যাম্প শুল্ক নিশ্চিত করুন।" if price_anomaly else "পেমেন্ট অসঙ্গতির জন্য কোনো পদক্ষেপ প্রয়োজন নেই।"
        return RuleResult(12, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[12])

    def _check_13(self, ctx: ILRMFContext) -> RuleResult:
        """Sub-Registry Stamp & Seal"""
        n, bn = CHECK_NAMES[13]
        stamp_issue = self._ai_flag(ctx, "stamp_seal_issue", False)
        score = 65.0 if stamp_issue else 0.0
        status = "FAIL" if stamp_issue else "PASS"
        band = self._resolve_band(score)
        finding_en = "Sub-registry stamp or seal anomaly detected. Document may be unregistered or improperly executed." if stamp_issue else "Sub-registry stamp and seal appear authentic and complete."
        finding_bn = "সাব-রেজিস্ট্রি স্ট্যাম্প বা সিলে অসঙ্গতি সনাক্ত হয়েছে।" if stamp_issue else "সাব-রেজিস্ট্রি স্ট্যাম্প ও সিল সত্যতাপূর্ণ।"
        rec_en = "Obtain certified copy from sub-registry to verify original registration." if stamp_issue else "Confirm stamp duty paid per Stamp Act 1899."
        rec_bn = "আসল নিবন্ধন যাচাই করতে সাব-রেজিস্ট্রি থেকে সার্টিফাইড কপি সংগ্রহ করুন।" if stamp_issue else "স্ট্যাম্প আইন ১৮৯৯ অনুযায়ী স্ট্যাম্প শুল্ক পরিশোধ নিশ্চিত করুন।"
        return RuleResult(13, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[13])

    def _check_14(self, ctx: ILRMFContext) -> RuleResult:
        """NRB / Foreign Ownership Eligibility"""
        n, bn = CHECK_NAMES[14]
        is_nrb = self._ai_flag(ctx, "nrb_foreign_party", False)
        eligibility_issue = self._ai_flag(ctx, "nrb_eligibility_issue", False)
        if not is_nrb:
            return RuleResult(14, n, bn, "NA", "GREEN", 0, "Not applicable. No NRB/foreign party identified.", "এনআরবি/বিদেশী পক্ষ নেই। প্রযোজ্য নয়।", "N/A", "প্রযোজ্য নয়।", LEGAL_REFS[14])
        score = 70.0 if eligibility_issue else 10.0
        status = "FAIL" if eligibility_issue else "WARN"
        band = self._resolve_band(score)
        finding_en = "NRB/foreign party involved. FERA 1947 restrictions and BIDA clearance may apply." if eligibility_issue else "NRB party identified. Standard FERA compliance documentation needed."
        finding_bn = "এনআরবি/বিদেশী পক্ষ জড়িত। ফেরা ১৯৪৭ বিধিনিষেধ এবং বিডা ছাড়পত্র প্রযোজ্য হতে পারে।" if eligibility_issue else "এনআরবি পক্ষ চিহ্নিত। ফেরা সম্মতি দলিল প্রয়োজন।"
        rec_en = "Obtain BIDA investment clearance and Bangladesh Bank approval for remittance. Verify FERA §18 compliance." if eligibility_issue else "Prepare FERA compliance package including BB approval for fund remittance."
        rec_bn = "বিডা বিনিয়োগ ছাড়পত্র এবং রেমিট্যান্সের জন্য বাংলাদেশ ব্যাংক অনুমোদন সংগ্রহ করুন।" if eligibility_issue else "বিবি অনুমোদনসহ ফেরা সম্মতি প্যাকেজ প্রস্তুত করুন।"
        return RuleResult(14, n, bn, status, band, score, finding_en, finding_bn, rec_en, rec_bn, LEGAL_REFS[14])

rule_engine = LandRuleEngine()
