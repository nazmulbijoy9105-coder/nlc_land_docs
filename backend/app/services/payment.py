import httpx
import hashlib
import hmac
import base64
import json
from datetime import datetime
from app.core.config import settings

PLANS = {
    "basic":    {"price": 499,  "label": "Basic / বেসিক",    "docs": 1,  "checks": 5},
    "standard": {"price": 999,  "label": "Standard / স্ট্যান্ডার্ড", "docs": 5, "checks": 10},
    "premium":  {"price": 2499, "label": "Premium / প্রিমিয়াম",  "docs": 0,  "checks": 14},
}

BKASH_MERCHANT_NUMBER = "01XXXXXXXXX"  # Replace with live number
NAGAD_MERCHANT_NUMBER = "01XXXXXXXXX"  # Replace with live number
NLC_BANK_ACCOUNT = "XXXXX-XXX-XXXXXXXXX"  # Replace with bank account

class PaymentService:

    async def initiate_bkash(self, amount: float, case_ref: str, user_phone: str) -> dict:
        """bKash tokenized payment initiation"""
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Get token
                token_resp = await client.post(
                    f"{settings.BKASH_BASE_URL}/tokenized/checkout/token/grant",
                    json={
                        "app_key": settings.BKASH_APP_KEY,
                        "app_secret": settings.BKASH_APP_SECRET,
                    },
                    headers={
                        "username": settings.BKASH_USERNAME,
                        "password": settings.BKASH_PASSWORD,
                        "Content-Type": "application/json",
                    },
                    timeout=15,
                )
                token_data = token_resp.json()
                id_token = token_data.get("id_token")
                if not id_token:
                    raise Exception("bKash token failed")

                # Step 2: Create payment
                pay_resp = await client.post(
                    f"{settings.BKASH_BASE_URL}/tokenized/checkout/create",
                    json={
                        "mode": "0011",
                        "payerReference": user_phone,
                        "callbackURL": f"{settings.FRONTEND_URL}/payment/callback/bkash",
                        "amount": str(amount),
                        "currency": "BDT",
                        "intent": "sale",
                        "merchantInvoiceNumber": case_ref,
                    },
                    headers={
                        "Authorization": id_token,
                        "X-APP-Key": settings.BKASH_APP_KEY,
                        "Content-Type": "application/json",
                    },
                    timeout=15,
                )
                pay_data = pay_resp.json()
                return {
                    "success": True,
                    "payment_id": pay_data.get("paymentID"),
                    "redirect_url": pay_data.get("bkashURL"),
                    "method": "bkash",
                }
        except Exception as e:
            # Fallback: manual bKash instructions
            return {
                "success": False,
                "method": "bkash",
                "manual": True,
                "merchant_number": BKASH_MERCHANT_NUMBER,
                "amount": amount,
                "reference": case_ref,
                "instructions_en": f"Send ৳{amount} to bKash merchant number {BKASH_MERCHANT_NUMBER}. Use reference: {case_ref}",
                "instructions_bn": f"bKash মার্চেন্ট নম্বর {BKASH_MERCHANT_NUMBER}-এ ৳{amount} পাঠান। রেফারেন্স ব্যবহার করুন: {case_ref}",
                "error": str(e),
            }

    async def initiate_nagad(self, amount: float, case_ref: str) -> dict:
        """Nagad payment — manual fallback"""
        return {
            "success": True,
            "method": "nagad",
            "manual": True,
            "merchant_number": NAGAD_MERCHANT_NUMBER,
            "amount": amount,
            "reference": case_ref,
            "instructions_en": f"Send ৳{amount} to Nagad merchant number {NAGAD_MERCHANT_NUMBER}. Use reference: {case_ref}",
            "instructions_bn": f"নগদ মার্চেন্ট নম্বর {NAGAD_MERCHANT_NUMBER}-এ ৳{amount} পাঠান। রেফারেন্স: {case_ref}",
        }

    def get_bank_instructions(self, amount: float, case_ref: str) -> dict:
        return {
            "method": "bank",
            "account": NLC_BANK_ACCOUNT,
            "bank_name": "Dutch-Bangla Bank Limited",
            "branch": "Panthapath Branch",
            "account_name": "Neum Lex Counsel",
            "amount": amount,
            "reference": case_ref,
            "instructions_en": f"Transfer ৳{amount} to account {NLC_BANK_ACCOUNT}. Use reference: {case_ref}. Upload transfer proof.",
            "instructions_bn": f"অ্যাকাউন্ট {NLC_BANK_ACCOUNT}-এ ৳{amount} ট্রান্সফার করুন। রেফারেন্স: {case_ref}। প্রমাণ আপলোড করুন।",
        }

    def get_cash_instructions(self, amount: float, case_ref: str) -> dict:
        return {
            "method": "cash",
            "amount": amount,
            "reference": case_ref,
            "instructions_en": f"Pay ৳{amount} cash at NLC office, Panthapath, Dhaka. Show reference: {case_ref}",
            "instructions_bn": f"এনএলসি অফিস, পান্থপথ, ঢাকায় ৳{amount} নগদ পরিশোধ করুন। রেফারেন্স: {case_ref}",
            "address": "Panthapath, Dhaka — Neum Lex Counsel",
        }

payment_service = PaymentService()
