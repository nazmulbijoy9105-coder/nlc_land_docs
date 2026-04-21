"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { casesApi, reportsApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { RiskCard, RiskBadge, StatusPill } from "@/components/ui/RiskDisplay";
import toast from "react-hot-toast";
import clsx from "clsx";
import {
  Download, RefreshCw, ChevronDown, ChevronUp,
  BookOpen, Gavel, CheckCircle, AlertTriangle, XCircle, MinusCircle, ArrowLeft
} from "lucide-react";
import Link from "next/link";

const STATUS_ICON: Record<string, any> = {
  PASS: CheckCircle,
  WARN: AlertTriangle,
  FAIL: XCircle,
  NA: MinusCircle,
};
const STATUS_COLOR: Record<string, string> = {
  PASS: "text-emerald-600",
  WARN: "text-amber-600",
  FAIL: "text-red-600",
  NA: "text-gray-400",
};

function CheckRow({ check, lang }: { check: any; lang: "en" | "bn" }) {
  const [open, setOpen] = useState(false);
  const Icon = STATUS_ICON[check.status] || MinusCircle;

  return (
    <div className={clsx(
      "border rounded-xl overflow-hidden transition-all",
      check.status === "FAIL" ? "border-red-200" :
      check.status === "WARN" ? "border-amber-200" :
      check.status === "PASS" ? "border-emerald-200" : "border-gray-200"
    )}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-4 p-4 bg-white hover:bg-navy-50/30 transition-colors text-left"
      >
        <div className={clsx("w-7 h-7 rounded-lg flex items-center justify-center bg-navy-50 flex-shrink-0",)}>
          <span className="text-xs font-bold text-navy/50">{check.check_id}</span>
        </div>
        <Icon className={clsx("w-4 h-4 flex-shrink-0", STATUS_COLOR[check.status])} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-navy">
            {lang === "en" ? check.check_name : check.check_name_bn}
          </p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <RiskBadge band={check.risk_band} />
          <span className="text-xs font-mono text-navy/40">{check.risk_score?.toFixed(0)}</span>
          {open ? <ChevronUp className="w-4 h-4 text-navy/30" /> : <ChevronDown className="w-4 h-4 text-navy/30" />}
        </div>
      </button>

      {open && (
        <div className="px-5 pb-5 pt-2 bg-white border-t border-navy-100/30 space-y-4">
          {/* Finding */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="bg-navy-50/50 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <BookOpen className="w-4 h-4 text-navy/40" />
                <span className="text-xs font-semibold text-navy/50 uppercase tracking-wide">
                  {lang === "en" ? "Finding" : "ফলাফল"}
                </span>
              </div>
              <p className="text-sm text-navy/80 leading-relaxed">
                {lang === "en" ? check.finding_en : check.finding_bn}
              </p>
            </div>
            <div className="bg-gold/5 rounded-xl p-4 border border-gold/20">
              <div className="flex items-center gap-2 mb-2">
                <Gavel className="w-4 h-4 text-gold/60" />
                <span className="text-xs font-semibold text-gold/60 uppercase tracking-wide">
                  {lang === "en" ? "Recommendation" : "সুপারিশ"}
                </span>
              </div>
              <p className="text-sm text-navy/80 leading-relaxed">
                {lang === "en" ? check.recommendation_en : check.recommendation_bn}
              </p>
            </div>
          </div>
          {/* Legal refs */}
          {check.legal_refs?.refs?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {check.legal_refs.refs.map((ref: string, i: number) => (
                <span key={i} className="text-xs px-3 py-1 bg-navy-50 text-navy/60 rounded-full border border-navy-100/40 font-mono">
                  {ref}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useAuthStore();
  const [caseData, setCaseData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  const fetchCase = async () => {
    try {
      const res = await casesApi.get(id);
      setCaseData(res.data);
    } catch {
      toast.error("Failed to load case");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCase(); }, [id]);

  const downloadReport = async (reportId: string) => {
    setDownloading(true);
    try {
      const res = await reportsApi.download(reportId);
      const url = URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
      const a = document.createElement("a");
      a.href = url; a.download = `${caseData.case_ref}_report.pdf`; a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Download failed");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-navy/20 border-t-navy rounded-full animate-spin" />
    </div>
  );

  if (!caseData) return null;

  const isComplete = caseData.status === "completed";
  const analysis = caseData.analysis || [];
  const passCount = analysis.filter((a: any) => a.status === "PASS").length;
  const warnCount = analysis.filter((a: any) => a.status === "WARN").length;
  const failCount = analysis.filter((a: any) => a.status === "FAIL").length;

  return (
    <div className="fade-in space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link href="/dashboard" className="inline-flex items-center gap-1.5 text-xs text-navy/40 hover:text-navy mb-3 transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" /> {lang === "en" ? "Back to Dashboard" : "ড্যাশবোর্ডে ফিরুন"}
          </Link>
          <h1 className="section-title">{caseData.title}</h1>
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className="text-xs text-navy/30 font-mono">{caseData.case_ref}</span>
            <StatusPill status={caseData.status} />
            <span className="text-xs text-navy/30 capitalize">{caseData.property_type} · {caseData.plan}</span>
            {caseData.district && <span className="text-xs text-navy/30">{caseData.district}</span>}
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchCase} className="btn-ghost flex items-center gap-1.5 text-xs">
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
          {isComplete && caseData.reports?.[0] && (
            <button onClick={() => downloadReport(caseData.reports[0].id)} disabled={downloading}
              className="btn-gold flex items-center gap-2 text-sm">
              {downloading
                ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : <Download className="w-4 h-4" />}
              {lang === "en" ? "Download PDF" : "পিডিএফ ডাউনলোড"}
            </button>
          )}
        </div>
      </div>

      {/* Status banners */}
      {caseData.status === "pending_payment" && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          {lang === "en" ? "Payment pending. Admin will confirm and analysis will begin." : "পেমেন্ট বাকি। অ্যাডমিন নিশ্চিত করলে বিশ্লেষণ শুরু হবে।"}
        </div>
      )}
      {caseData.status === "processing" && (
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 text-sm text-purple-800 flex items-center gap-3">
          <div className="w-4 h-4 border-2 border-purple-300 border-t-purple-600 rounded-full animate-spin flex-shrink-0" />
          {lang === "en" ? "AI forensic analysis in progress. Please check back shortly." : "এআই ফরেনসিক বিশ্লেষণ চলছে।"}
        </div>
      )}

      {/* Risk summary */}
      {isComplete && caseData.overall_risk_band && (
        <>
          <RiskCard band={caseData.overall_risk_band} score={caseData.overall_risk_score || 0} lang={lang} />

          {/* Score breakdown */}
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: "PASS", labelBn: "পাস", count: passCount, color: "text-emerald-700 bg-emerald-50 border-emerald-200" },
              { label: "WARN", labelBn: "সতর্কতা", count: warnCount, color: "text-amber-700 bg-amber-50 border-amber-200" },
              { label: "FAIL", labelBn: "ব্যর্থ", count: failCount, color: "text-red-700 bg-red-50 border-red-200" },
              { label: "N/A", labelBn: "প্রযোজ্য নয়", count: analysis.filter((a: any) => a.status === "NA").length, color: "text-gray-500 bg-gray-50 border-gray-200" },
            ].map(s => (
              <div key={s.label} className={`rounded-xl border p-4 text-center ${s.color}`}>
                <div className="text-2xl font-bold font-mono">{s.count}</div>
                <div className="text-xs font-semibold mt-0.5">{lang === "en" ? s.label : s.labelBn}</div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Audit hash */}
      {caseData.risk_hash && (
        <div className="bg-navy-50/50 rounded-xl p-4 border border-navy-100/40">
          <p className="text-xs text-navy/40">
            <span className="font-semibold">SHA256 Audit Hash:</span>{" "}
            <span className="font-mono">{caseData.risk_hash}</span>
          </p>
        </div>
      )}

      {/* 14-check results */}
      {isComplete && analysis.length > 0 && (
        <div>
          <h2 className="section-title mb-4">{lang === "en" ? "Forensic Analysis Results" : "ফরেনসিক বিশ্লেষণের ফলাফল"}</h2>
          <div className="space-y-2">
            {analysis.map((check: any) => (
              <CheckRow key={check.check_id} check={check} lang={lang} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
