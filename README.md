# NLC Land Evidence Platform
**AI-Powered Land & Real Estate Evidence Analysis**  
Neum Lex Counsel (NLC) — Bangladesh Property Law · ILRMF v2.0

---

## Stack
| Layer | Tech |
|---|---|
| Backend | FastAPI · Celery · Supabase PostgreSQL |
| Frontend | Next.js 14 (App Router) · Tailwind CSS |
| AI Engine | Gemini 2.0 Flash · ILRMF v2.0 |
| OCR | PyMuPDF · Tesseract (Bengali + English) |
| PDF Reports | ReportLab (Bilingual NLC letterhead) |
| Payments | bKash · Nagad · Bank · Cash |
| Queue | Celery + Upstash Redis |
| Email | Resend |
| DevOps | Render (backend + worker) · Vercel (frontend) |
| CI/CD | GitHub Actions |

---

## Quick Deploy

### 1. Supabase Setup
```
1. Create bucket: land-evidence (public: false)
2. Run migration: alembic upgrade head
3. Note: all tables use schema = land_evidence
```

### 2. Backend → Render
```bash
# Set all env vars from backend/.env.example
# Services: web (main API) + worker (Celery)
# Dockerfile: backend/Dockerfile
# Health check: /health
```

### 3. Frontend → Vercel
```bash
cd frontend
bun install
vercel --prod
# Set env: NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com
```

### 4. GitHub Actions
Set these repository secrets:
```
RENDER_DEPLOY_HOOK_URL   # from Render dashboard
VERCEL_TOKEN             # from Vercel dashboard
VERCEL_ORG_ID
VERCEL_PROJECT_ID
NEXT_PUBLIC_API_URL
```

### 5. Create First Admin
```bash
# POST /api/v1/auth/register
# Then in Supabase SQL editor:
UPDATE land_evidence.users SET role = 'admin' WHERE email = 'your@email.com';
```

---

## 14 Forensic Checks (ILRMF v2.0)

| # | Check | Law |
|---|---|---|
| 1 | Deed Forgery & Signature Anomaly | Registration Act 1908 |
| 2 | CS→SA→RS→BS Khatian Chain | SAT Act 1950 |
| 3 | Baya Chain Gaps | Transfer of Property Act 1882 |
| 4 | Mutation / Namjari | Land Acquisition Act 1894 |
| 5 | Timeline Contradictions | Registration Act 1908 |
| 6 | Overlapping Documents | Specific Relief Act 1877 |
| 7 | RAJUK DAP Compliance | Town Improvement Act 1953 |
| 8 | REDMA Developer Registration | REDMA 2010 |
| 9 | Mortgage / Artha Rin Flag | Artha Rin Adalat Ain 2003 |
| 10 | Land Classification | Non-Agri Land Use Control Act 1963 |
| 11 | Boundary Dispute Probability | Survey Act 1875 |
| 12 | Payment Anomaly | Money Laundering Prevention Act 2012 |
| 13 | Sub-Registry Stamp & Seal | Stamp Act 1899 |
| 14 | NRB / Foreign Ownership | FERA 1947 · BIDA Act 2016 |

---

## Plans
| Plan | Price | Docs | Checks |
|---|---|---|---|
| Basic | ৳499 | 1 | 5 |
| Standard | ৳999 | 5 | 10 |
| Premium | ৳2499 | ∞ | 14 |

---

## Git Push
```bash
git init
git remote add origin https://github.com/nazmulbijoy9105-coder/nlc-land-docs.git
git add . && git commit -m "feat: initial NLC Land Evidence Platform" && git push -u origin main
```

---

**Neum Lex Counsel · Panthapath, Dhaka · Justice. Reimagined.**
# nlc_land_docs
