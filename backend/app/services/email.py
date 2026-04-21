import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY

def _send(to: str, subject: str, html: str):
    try:
        resend.Emails.send({
            "from": f"Neum Lex Counsel <{settings.FROM_EMAIL}>",
            "to": [to],
            "subject": subject,
            "html": html,
        })
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

NLC_STYLE = """
<style>
  body { font-family: Georgia, serif; background: #f9f9f9; }
  .container { max-width: 600px; margin: 0 auto; background: white; border-top: 4px solid #c9a84c; }
  .header { background: #1a2744; color: white; padding: 24px; }
  .header h1 { margin: 0; font-size: 22px; }
  .header p { margin: 4px 0 0; color: #c9a84c; font-style: italic; font-size: 13px; }
  .body { padding: 24px; color: #1f2937; line-height: 1.6; }
  .badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-weight: bold; }
  .footer { background: #f3f4f6; padding: 12px 24px; font-size: 11px; color: #6b7280; }
</style>
"""

def send_welcome(to: str, name: str):
    html = f"""{NLC_STYLE}
<div class="container">
  <div class="header"><h1>Neum Lex Counsel</h1><p>Justice. Reimagined.</p></div>
  <div class="body">
    <p>Dear {name},</p>
    <p>Welcome to NLC Land & Real Estate Evidence Analysis Platform. Your account has been created successfully.</p>
    <p>প্রিয় {name}, এনএলসি ল্যান্ড প্ল্যাটফর্মে স্বাগতম। আপনার অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে।</p>
    <p>You can now submit property documents for AI-powered forensic analysis.</p>
  </div>
  <div class="footer">Neum Lex Counsel | Panthapath, Dhaka | neumlexcounsel.com</div>
</div>"""
    _send(to, "Welcome to NLC Land Evidence Platform", html)

def send_payment_pending(to: str, name: str, case_ref: str, amount: float, method: str):
    html = f"""{NLC_STYLE}
<div class="container">
  <div class="header"><h1>Neum Lex Counsel</h1><p>Payment Confirmation Pending</p></div>
  <div class="body">
    <p>Dear {name},</p>
    <p>Your payment of <strong>৳{amount}</strong> via <strong>{method.upper()}</strong> for case <strong>{case_ref}</strong> is under review.</p>
    <p>আপনার ৳{amount} পেমেন্ট ({method.upper()}) কেস {case_ref}-এর জন্য যাচাই চলছে।</p>
    <p>You will receive an email once confirmed. Processing begins immediately after confirmation.</p>
  </div>
  <div class="footer">Neum Lex Counsel | Panthapath, Dhaka</div>
</div>"""
    _send(to, f"Payment Pending — {case_ref}", html)

def send_payment_confirmed(to: str, name: str, case_ref: str):
    html = f"""{NLC_STYLE}
<div class="container">
  <div class="header"><h1>Neum Lex Counsel</h1><p>Payment Confirmed ✓</p></div>
  <div class="body">
    <p>Dear {name},</p>
    <p>Payment confirmed for case <strong>{case_ref}</strong>. AI analysis has been queued and will begin shortly.</p>
    <p>কেস {case_ref}-এর পেমেন্ট নিশ্চিত হয়েছে। বিশ্লেষণ শুরু হচ্ছে।</p>
  </div>
  <div class="footer">Neum Lex Counsel | Panthapath, Dhaka</div>
</div>"""
    _send(to, f"Payment Confirmed — {case_ref}", html)

def send_analysis_complete(to: str, name: str, case_ref: str, risk_band: str, risk_score: float):
    band_color = {"GREEN": "#16a34a", "YELLOW": "#ca8a04", "RED": "#dc2626", "BLACK": "#111827"}.get(risk_band, "#666")
    html = f"""{NLC_STYLE}
<div class="container">
  <div class="header"><h1>Neum Lex Counsel</h1><p>Analysis Complete</p></div>
  <div class="body">
    <p>Dear {name},</p>
    <p>AI forensic analysis for case <strong>{case_ref}</strong> is complete.</p>
    <p>Overall Risk: <span class="badge" style="background:{band_color};color:white">{risk_band}</span> — Score: {risk_score:.1f}/100</p>
    <p>কেস {case_ref}-এর বিশ্লেষণ সম্পন্ন। সামগ্রিক ঝুঁকি: {risk_band} ({risk_score:.1f}/100)</p>
    <p>Download your bilingual PDF report from your dashboard.</p>
  </div>
  <div class="footer">Neum Lex Counsel | Panthapath, Dhaka</div>
</div>"""
    _send(to, f"Analysis Complete — {case_ref} | Risk: {risk_band}", html)

def send_black_alert_admin(admin_email: str, case_ref: str, client_name: str):
    html = f"""{NLC_STYLE}
<div class="container">
  <div class="header" style="background:#111827"><h1>⚠ BLACK RISK ALERT</h1></div>
  <div class="body">
    <p><strong>BLACK band risk</strong> detected for case <strong>{case_ref}</strong> — Client: {client_name}</p>
    <p>Immediate admin review required.</p>
  </div>
</div>"""
    _send(admin_email, f"BLACK RISK ALERT — {case_ref}", html)
