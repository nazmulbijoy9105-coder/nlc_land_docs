"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { casesApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { t } from "@/lib/i18n";
import { RiskBadge, StatusPill } from "@/components/ui/RiskDisplay";
import { Plus, FileSearch, Calendar, MapPin, ArrowRight, Inbox } from "lucide-react";
import toast from "react-hot-toast";

export default function DashboardPage() {
  const { lang, user } = useAuthStore();
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    casesApi.list()
      .then(r => setCases(r.data))
      .catch(() => toast.error("Failed to load cases"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="section-title">
            {lang === "en" ? `Welcome, ${user?.full_name?.split(" ")[0]}` : `স্বাগতম, ${user?.full_name_bn || user?.full_name?.split(" ")[0]}`}
          </h1>
          <p className="section-sub">{t(lang, "myCases")} — {lang === "en" ? "AI-powered property forensics" : "এআই-চালিত সম্পত্তি ফরেনসিক"}</p>
        </div>
        <Link href="/case/new" className="btn-gold flex items-center gap-2">
          <Plus className="w-4 h-4" />
          {t(lang, "newAnalysis")}
        </Link>
      </div>

      {/* Stats strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        {[
          { label: lang === "en" ? "Total Cases" : "মোট কেস", value: cases.length, color: "text-navy" },
          { label: lang === "en" ? "Completed" : "সম্পন্ন", value: cases.filter(c => c.status === "completed").length, color: "text-emerald-700" },
          { label: lang === "en" ? "Processing" : "প্রক্রিয়াধীন", value: cases.filter(c => c.status === "processing").length, color: "text-purple-700" },
          { label: lang === "en" ? "Pending Payment" : "পেমেন্ট বাকি", value: cases.filter(c => c.status === "pending_payment").length, color: "text-amber-700" },
        ].map(s => (
          <div key={s.label} className="card p-4">
            <div className={`text-2xl font-bold font-mono ${s.color}`}>{s.value}</div>
            <div className="text-xs text-navy/40 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Cases list */}
      {loading ? (
        <div className="card p-12 text-center">
          <div className="w-8 h-8 border-2 border-navy/20 border-t-navy rounded-full animate-spin mx-auto mb-3" />
          <p className="text-navy/40 text-sm">{lang === "en" ? "Loading cases..." : "কেস লোড হচ্ছে..."}</p>
        </div>
      ) : cases.length === 0 ? (
        <div className="card p-16 text-center">
          <Inbox className="w-12 h-12 text-navy/20 mx-auto mb-4" />
          <h3 className="font-display text-lg font-semibold text-navy mb-2">
            {lang === "en" ? "No cases yet" : "এখনো কোনো কেস নেই"}
          </h3>
          <p className="text-navy/40 text-sm mb-6">
            {lang === "en" ? "Submit property documents for AI forensic analysis" : "এআই ফরেনসিক বিশ্লেষণের জন্য সম্পত্তির দলিল জমা দিন"}
          </p>
          <Link href="/case/new" className="btn-gold inline-flex items-center gap-2">
            <Plus className="w-4 h-4" />
            {t(lang, "newAnalysis")}
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {cases.map(c => (
            <Link key={c.id} href={`/case/${c.id}`} className="card-hover block p-5 group">
              <div className="flex items-center justify-between">
                <div className="flex items-start gap-4 flex-1 min-w-0">
                  <div className="w-10 h-10 bg-navy-50 rounded-xl flex items-center justify-center flex-shrink-0">
                    <FileSearch className="w-5 h-5 text-navy/60" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-navy text-sm truncate">{c.title}</span>
                      <span className="text-xs text-navy/30 font-mono">{c.case_ref}</span>
                    </div>
                    <div className="flex items-center gap-3 mt-1.5 flex-wrap">
                      <StatusPill status={c.status} />
                      {c.overall_risk_band && <RiskBadge band={c.overall_risk_band} />}
                      {c.overall_risk_score !== null && c.overall_risk_score !== undefined && (
                        <span className="text-xs text-navy/40 font-mono">Score: {c.overall_risk_score?.toFixed(0)}/100</span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-2 text-xs text-navy/30">
                      <span className="flex items-center gap-1 capitalize"><FileSearch className="w-3 h-3" />{c.plan}</span>
                      {c.district && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{c.district}</span>}
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {c.created_at ? new Date(c.created_at).toLocaleDateString("en-BD") : "—"}
                      </span>
                    </div>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-navy/20 group-hover:text-gold transition-colors flex-shrink-0 ml-4" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
