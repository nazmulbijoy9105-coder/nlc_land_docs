import io
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# NLC Brand Colors
NAVY = colors.HexColor("#1a2744")
GOLD = colors.HexColor("#c9a84c")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
MID_GRAY = colors.HexColor("#e0e0e0")
WHITE = colors.white

BAND_COLORS = {
    "GREEN": colors.HexColor("#166534"),
    "YELLOW": colors.HexColor("#854d0e"),
    "RED": colors.HexColor("#991b1b"),
    "BLACK": colors.HexColor("#000000"),
}
BAND_BG = {
    "GREEN": colors.HexColor("#dcfce7"),
    "YELLOW": colors.HexColor("#fef9c3"),
    "RED": colors.HexColor("#fee2e2"),
    "BLACK": colors.HexColor("#d1d5db"),
}

def _styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=16,
                                textColor=NAVY, alignment=TA_CENTER, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=11,
                                   textColor=GOLD, alignment=TA_CENTER, spaceAfter=2),
        "heading": ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=12,
                                  textColor=NAVY, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9,
                               textColor=colors.HexColor("#1f2937"), leading=14,
                               alignment=TA_JUSTIFY),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8,
                                textColor=colors.HexColor("#6b7280")),
        "bold": ParagraphStyle("bold", fontName="Helvetica-Bold", fontSize=9,
                               textColor=NAVY),
        "center": ParagraphStyle("center", fontName="Helvetica", fontSize=9,
                                 alignment=TA_CENTER),
        "right": ParagraphStyle("right", fontName="Helvetica", fontSize=8,
                                alignment=TA_RIGHT, textColor=colors.HexColor("#6b7280")),
    }

def generate_analysis_report(
    case_ref: str,
    client_name: str,
    property_address: str,
    analysis_results: list,
    composite_score: float,
    composite_band: str,
    ai_summary_en: str,
    ai_summary_bn: str,
    key_concerns_en: list,
    key_concerns_bn: list,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=25*mm, bottomMargin=25*mm,
    )
    S = _styles()
    story = []

    # ── Header ──────────────────────────────────────────────
    header_data = [[
        Paragraph("NEUM LEX COUNSEL", ParagraphStyle("h1", fontName="Helvetica-Bold",
                  fontSize=18, textColor=WHITE, alignment=TA_LEFT)),
        Paragraph("Justice. Reimagined.", ParagraphStyle("h2", fontName="Helvetica-Oblique",
                  fontSize=10, textColor=GOLD, alignment=TA_RIGHT)),
    ]]
    header_table = Table(header_data, colWidths=[120*mm, 50*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (0, -1), 8),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4*mm))

    # ── Report Title ─────────────────────────────────────────
    story.append(Paragraph("AI-POWERED LAND & REAL ESTATE EVIDENCE ANALYSIS REPORT", S["title"]))
    story.append(Paragraph("ভূমি ও রিয়েল এস্টেট প্রমাণ বিশ্লেষণ প্রতিবেদন", S["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=4))

    # ── Case Info ────────────────────────────────────────────
    now = datetime.utcnow().strftime("%d %B %Y, %H:%M UTC")
    info_data = [
        ["Case Reference / কেস রেফারেন্স:", case_ref, "Report Date / তারিখ:", now],
        ["Client / ক্লায়েন্ট:", client_name, "Prepared By / প্রস্তুতকারী:", "Neum Lex Counsel"],
        ["Property / সম্পত্তি:", property_address, "Framework / কাঠামো:", "ILRMF v2.0"],
    ]
    info_table = Table(info_data, colWidths=[45*mm, 55*mm, 35*mm, 35*mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("TEXTCOLOR", (2, 0), (2, -1), NAVY),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 4*mm))

    # ── Overall Risk ─────────────────────────────────────────
    band_color = BAND_COLORS.get(composite_band, colors.gray)
    band_bg = BAND_BG.get(composite_band, LIGHT_GRAY)
    risk_data = [[
        Paragraph(f"OVERALL RISK BAND / সামগ্রিক ঝুঁকি স্তর", ParagraphStyle("rb",
                  fontName="Helvetica-Bold", fontSize=10, textColor=NAVY, alignment=TA_CENTER)),
        Paragraph(f"{composite_band}", ParagraphStyle("rb2", fontName="Helvetica-Bold",
                  fontSize=28, textColor=band_color, alignment=TA_CENTER)),
        Paragraph(f"Risk Score / ঝুঁকি স্কোর\n{composite_score:.1f} / 100",
                  ParagraphStyle("rs", fontName="Helvetica-Bold", fontSize=14,
                                 textColor=band_color, alignment=TA_CENTER)),
    ]]
    risk_table = Table(risk_data, colWidths=[60*mm, 50*mm, 60*mm])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), band_bg),
        ("BOX", (0, 0), (-1, -1), 2, band_color),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 4*mm))

    # ── 14-Check Summary Table ────────────────────────────────
    story.append(Paragraph("14-POINT FORENSIC ANALYSIS / ১৪-দফা ফরেনসিক বিশ্লেষণ", S["heading"]))
    check_headers = [
        Paragraph("#", S["bold"]),
        Paragraph("Check / যাচাই", S["bold"]),
        Paragraph("Status", S["bold"]),
        Paragraph("Band", S["bold"]),
        Paragraph("Score", S["bold"]),
    ]
    check_rows = [check_headers]
    for r in analysis_results:
        status_color = {"PASS": colors.HexColor("#166534"), "WARN": colors.HexColor("#854d0e"),
                        "FAIL": colors.HexColor("#991b1b"), "NA": colors.HexColor("#6b7280")}.get(r.get("status","NA"), colors.gray)
        check_rows.append([
            Paragraph(str(r.get("check_id", "")), S["center"]),
            Paragraph(f"{r.get('check_name','')}\n{r.get('check_name_bn','')}", S["body"]),
            Paragraph(r.get("status", "NA"), ParagraphStyle("st", fontName="Helvetica-Bold",
                      fontSize=8, textColor=status_color, alignment=TA_CENTER)),
            Paragraph(r.get("risk_band", ""), ParagraphStyle("rb3", fontName="Helvetica-Bold",
                      fontSize=8, textColor=BAND_COLORS.get(r.get("risk_band","GREEN"), colors.gray),
                      alignment=TA_CENTER)),
            Paragraph(f"{r.get('risk_score', 0):.0f}", S["center"]),
        ])
    check_table = Table(check_rows, colWidths=[10*mm, 90*mm, 18*mm, 18*mm, 15*mm])
    check_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(check_table)
    story.append(Spacer(1, 4*mm))

    # ── Detailed Findings ─────────────────────────────────────
    story.append(Paragraph("DETAILED FINDINGS & RECOMMENDATIONS / বিস্তারিত ফলাফল ও সুপারিশ", S["heading"]))
    for r in analysis_results:
        if r.get("status") == "NA":
            continue
        band = r.get("risk_band", "GREEN")
        bg = BAND_BG.get(band, LIGHT_GRAY)
        border = BAND_COLORS.get(band, colors.gray)
        block = [
            [Paragraph(f"Check {r.get('check_id')}: {r.get('check_name')} / {r.get('check_name_bn')}", S["bold"]),
             Paragraph(f"{r.get('status')} | {band} | Score: {r.get('risk_score',0):.0f}",
                       ParagraphStyle("info", fontName="Helvetica-Bold", fontSize=8,
                                      textColor=border, alignment=TA_RIGHT))],
            [Paragraph(f"<b>Finding (EN):</b> {r.get('finding_en','')}", S["body"]), ""],
            [Paragraph(f"<b>ফলাফল (BN):</b> {r.get('finding_bn','')}", S["body"]), ""],
            [Paragraph(f"<b>Recommendation:</b> {r.get('recommendation_en','')}", S["body"]), ""],
            [Paragraph(f"<b>সুপারিশ:</b> {r.get('recommendation_bn','')}", S["body"]), ""],
            [Paragraph(f"<b>Legal Refs:</b> {', '.join(r.get('legal_refs',[]))}", S["small"]), ""],
        ]
        bt = Table(block, colWidths=[130*mm, 40*mm])
        bt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("BOX", (0, 0), (-1, -1), 1, border),
            ("SPAN", (0, 1), (-1, 1)),
            ("SPAN", (0, 2), (-1, 2)),
            ("SPAN", (0, 3), (-1, 3)),
            ("SPAN", (0, 4), (-1, 4)),
            ("SPAN", (0, 5), (-1, 5)),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(KeepTogether([bt, Spacer(1, 2*mm)]))

    # ── Legal Opinion Summary ─────────────────────────────────
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("NLC LEGAL OPINION SUMMARY / আইনি মতামত সারসংক্ষেপ", S["heading"]))
    opinion_data = [
        [Paragraph("<b>English / ইংরেজি</b>", S["bold"])],
        [Paragraph(ai_summary_en, S["body"])],
        [Paragraph("<b>Bangla / বাংলা</b>", S["bold"])],
        [Paragraph(ai_summary_bn, S["body"])],
    ]
    opinion_table = Table(opinion_data, colWidths=[170*mm])
    opinion_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 1.5, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(opinion_table)
    story.append(Spacer(1, 4*mm))

    # ── Key Concerns ─────────────────────────────────────────
    if key_concerns_en:
        story.append(Paragraph("KEY CONCERNS / প্রধান উদ্বেগ", S["heading"]))
        concerns = []
        for en, bn in zip(key_concerns_en, key_concerns_bn):
            concerns.append([
                Paragraph(f"• {en}", S["body"]),
                Paragraph(f"• {bn}", S["body"]),
            ])
        ct = Table(concerns, colWidths=[85*mm, 85*mm])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
            ("GRID", (0, 0), (-1, -1), 0.3, MID_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(ct)

    # ── Footer ────────────────────────────────────────────────
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD))
    # Hash chain
    content_hash = hashlib.sha256(
        f"{case_ref}{composite_band}{composite_score}".encode()
    ).hexdigest()
    story.append(Paragraph(
        f"Document Hash (SHA256): {content_hash} | Generated: {now} | ILRMF v2.0",
        S["small"]
    ))
    story.append(Paragraph(
        "This report is generated by Neum Lex Counsel AI System. It does not constitute a legal opinion without NLC advocate signature. "
        "এই প্রতিবেদন নেউম লেক্স কাউন্সেল এআই সিস্টেম দ্বারা তৈরি। এনএলসি আইনজীবীর স্বাক্ষর ছাড়া এটি আইনি মতামত নয়।",
        S["small"]
    ))

    doc.build(story)
    return buffer.getvalue(), content_hash
