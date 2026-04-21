import Link from "next/link";
import { Scale, Shield, FileSearch, Clock, MapPin, Building2, Home, Briefcase, ChevronRight, CheckCircle2 } from "lucide-react";

const CHECKS_EN = [
  "Deed Forgery & Signature Anomaly Detection",
  "CS→SA→RS→BS Khatian Chain Verification",
  "Baya (Ownership History) Chain Analysis",
  "Mutation / Namjari Certificate Verification",
  "Timeline Contradiction Scoring",
  "Overlapping / Duplicate Document Detection",
  "RAJUK DAP Plan Compliance",
  "REDMA 2010 Developer Registration Check",
  "Mortgage Lien / Artha Rin Case Flag",
  "Land Classification Check",
  "Boundary Dispute Probability",
  "Payment Anomaly Detection",
  "Sub-Registry Stamp & Seal Validation",
  "NRB / Foreign Ownership Eligibility",
];

const CHECKS_BN = [
  "দলিল জালিয়াতি ও স্বাক্ষর অসঙ্গতি সনাক্তকরণ",
  "সিএস→এসএ→আরএস→বিএস খতিয়ান চেইন যাচাই",
  "বায়া দলিল মালিকানার ইতিহাস বিশ্লেষণ",
  "নামজারি / মিউটেশন সনদ যাচাই",
  "সময়রেখা অসঙ্গতি স্কোরিং",
  "ওভারল্যাপিং / ডুপ্লিকেট দলিল সনাক্তকরণ",
  "রাজউক ড্যাপ পরিকল্পনা সম্মতি",
  "রেডমা ২০১০ ডেভেলপার নিবন্ধন যাচাই",
  "বন্ধক দায় / অর্থঋণ মামলা পতাকা",
  "ভূমি শ্রেণীবিভাগ যাচাই",
  "সীমানা বিরোধ সম্ভাবনা",
  "মূল্য অসঙ্গতি সনাক্তকরণ",
  "সাব-রেজিস্ট্রি স্ট্যাম্প ও সিল যাচাই",
  "এনআরবি / বিদেশী মালিকানা যোগ্যতা",
];

const PLANS = [
  { name: "Basic", nameBn: "বেসিক", price: 499, docs: 1, checks: 5, color: "border-navy-100" },
  { name: "Standard", nameBn: "স্ট্যান্ডার্ড", price: 999, docs: 5, checks: 10, color: "border-gold/60", featured: true },
  { name: "Premium", nameBn: "প্রিমিয়াম", price: 2499, docs: "Unlimited", checks: 14, color: "border-navy-100" },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-cream">
      {/* ── Hero ─────────────────────────────────────────── */}
      <section className="relative bg-hero-pattern overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-navy/3 to-transparent pointer-events-none" />
        <div className="max-w-7xl mx-auto px-6 pt-20 pb-24">
          {/* NLC badge */}
          <div className="flex justify-center mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-navy/5 border border-navy/10 text-xs font-medium text-navy/60">
              <Scale className="w-3.5 h-3.5 text-gold" />
              Neum Lex Counsel · ILRMF v2.0 · 40+ Bangladesh Laws
            </div>
          </div>

          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-navy text-center leading-tight mb-4">
            AI-Powered Land &<br />
            <span className="text-gold">Real Estate Evidence</span> Analysis
          </h1>
          <p className="text-center text-navy/50 text-lg mb-2">
            For Companies, Developers, Landowners & Flat Owners
          </p>
          <p className="text-center text-navy/40 text-sm font-medium mb-10">
            কোম্পানি, ডেভেলপার, জমির মালিক ও ফ্ল্যাট মালিকদের জন্য
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth/register" className="btn-primary text-base px-8 py-4 flex items-center gap-2 justify-center">
              Start Analysis <ChevronRight className="w-5 h-5" />
            </Link>
            <Link href="/auth/login" className="btn-outline text-base px-8 py-4 flex items-center gap-2 justify-center">
              Sign In
            </Link>
          </div>

          {/* Target clients */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-16 max-w-3xl mx-auto">
            {[
              { icon: Briefcase, label: "Companies", labelBn: "কোম্পানি" },
              { icon: Building2, label: "Developers", labelBn: "ডেভেলপার" },
              { icon: MapPin,    label: "Landowners", labelBn: "জমির মালিক" },
              { icon: Home,      label: "Flat Owners", labelBn: "ফ্ল্যাট মালিক" },
            ].map(({ icon: Icon, label, labelBn }) => (
              <div key={label} className="card p-5 text-center hover:shadow-card-hover transition-all">
                <div className="w-12 h-12 bg-navy-50 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Icon className="w-6 h-6 text-navy" />
                </div>
                <div className="font-semibold text-sm text-navy">{label}</div>
                <div className="text-xs text-navy/40 mt-0.5">{labelBn}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 14 Checks ────────────────────────────────────── */}
      <section className="py-20 bg-navy">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="font-display text-3xl font-bold text-white mb-2">14-Point Forensic Analysis</h2>
            <p className="text-gold/80 text-sm">১৪-দফা ফরেনসিক বিশ্লেষণ — Bangladesh Law Compliance</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {CHECKS_EN.map((check, i) => (
              <div key={i} className="flex items-start gap-3 bg-white/5 rounded-xl p-4 border border-white/10">
                <div className="w-7 h-7 rounded-lg bg-gold/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-gold text-xs font-bold">{i + 1}</span>
                </div>
                <div>
                  <p className="text-white/90 text-xs font-medium leading-snug">{check}</p>
                  <p className="text-white/40 text-xs mt-1 leading-snug">{CHECKS_BN[i]}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Risk Bands ────────────────────────────────────── */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="section-title">Risk Band System / ঝুঁকি স্তর পদ্ধতি</h2>
            <p className="section-sub">ILRMF v2.0 — Four-tier risk classification</p>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { band: "GREEN",  score: "0–24",  desc: "Low risk. Proceed.",              descBn: "কম ঝুঁকি।",        bg: "bg-emerald-50 border-emerald-200 text-emerald-800" },
              { band: "YELLOW", score: "25–59", desc: "Moderate. Verify flags.",         descBn: "মাঝারি ঝুঁকি।",    bg: "bg-amber-50 border-amber-200 text-amber-800" },
              { band: "RED",    score: "60–89", desc: "High risk. Get legal clearance.", descBn: "উচ্চ ঝুঁকি।",      bg: "bg-red-50 border-red-200 text-red-800" },
              { band: "BLACK",  score: "90+",   desc: "Critical. Halt all activity.",    descBn: "সংকটজনক ঝুঁকি।",  bg: "bg-gray-900 border-gray-700 text-white" },
            ].map(({ band, score, desc, descBn, bg }) => (
              <div key={band} className={`rounded-2xl border-2 p-6 ${bg}`}>
                <div className="text-2xl font-display font-bold mb-1">{band}</div>
                <div className="text-3xl font-mono font-bold mb-3 opacity-70">{score}</div>
                <p className="text-sm opacity-80">{desc}</p>
                <p className="text-xs opacity-50 mt-1">{descBn}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Plans ────────────────────────────────────────── */}
      <section className="py-20 bg-pearl">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="section-title">Plans & Pricing / পরিকল্পনা ও মূল্য</h2>
            <p className="section-sub">bKash · Nagad · Bank Transfer · Cash</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PLANS.map((plan) => (
              <div key={plan.name} className={`card p-8 border-2 ${plan.color} ${plan.featured ? "ring-2 ring-gold/30 shadow-gold-glow" : ""} relative`}>
                {plan.featured && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gold text-white text-xs font-bold px-4 py-1 rounded-full">
                    Most Popular
                  </div>
                )}
                <div className="font-display text-xl font-semibold text-navy mb-0.5">{plan.name}</div>
                <div className="text-navy/40 text-sm mb-6">{plan.nameBn}</div>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-bold text-navy font-mono">৳{plan.price}</span>
                  <span className="text-navy/40 text-sm">/ case</span>
                </div>
                <ul className="space-y-3 mb-8 text-sm text-navy/70">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-gold flex-shrink-0" /> {plan.docs === "Unlimited" ? "Unlimited documents" : `${plan.docs} document${plan.docs > 1 ? "s" : ""}`}</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-gold flex-shrink-0" /> {plan.checks} forensic checks</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-gold flex-shrink-0" /> {plan.name === "Premium" ? "Full bilingual report + Legal letter" : "Bilingual PDF report"}</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-gold flex-shrink-0" /> SHA256 tamper-proof audit</li>
                </ul>
                <Link href="/auth/register" className={plan.featured ? "btn-gold w-full text-center block" : "btn-outline w-full text-center block"}>
                  Get Started
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────── */}
      <footer className="bg-navy text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-white/10 rounded-lg flex items-center justify-center">
                <Scale className="w-5 h-5 text-gold" />
              </div>
              <div>
                <div className="font-display font-semibold">Neum Lex Counsel</div>
                <div className="text-gold/70 text-xs italic">Justice. Reimagined.</div>
              </div>
            </div>
            <div className="text-white/30 text-xs text-center">
              © 2024 Neum Lex Counsel. Panthapath, Dhaka, Bangladesh.<br />
              ILRMF v2.0 · 40+ Bangladesh Property Laws · SHA256 Audit Chain
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
