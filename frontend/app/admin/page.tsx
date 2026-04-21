"use client";
import { useEffect, useState } from "react";
import { adminApi, paymentsApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { RiskBadge, StatusPill } from "@/components/ui/RiskDisplay";
import toast from "react-hot-toast";
import clsx from "clsx";
import {
  Users, Briefcase, TrendingUp, Clock, CheckCircle2,
  XCircle, RotateCcw, RefreshCw, ShieldCheck, FileSearch
} from "lucide-react";
import Link from "next/link";

type Tab = "overview" | "payments" | "cases" | "users";

export default function AdminPage() {
  const { lang } = useAuthStore();
  const [tab, setTab] = useState<Tab>("overview");
  const [stats, setStats] = useState<any>(null);
  const [payments, setPayments] = useState<any[]>([]);
  const [cases, setCases] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [confirmNote, setConfirmNote] = useState<Record<string, string>>({});

  const fetchStats = async () => {
    try { setStats((await adminApi.stats()).data); } catch {}
  };
  const fetchPayments = async () => {
    try { setPayments((await paymentsApi.adminPending()).data); } catch {}
  };
  const fetchCases = async () => {
    try { setCases((await adminApi.cases()).data); } catch {}
  };
  const fetchUsers = async () => {
    try { setUsers((await adminApi.users()).data); } catch {}
  };

  useEffect(() => {
    fetchStats();
    fetchPayments();
  }, []);
  useEffect(() => {
    if (tab === "cases") fetchCases();
    if (tab === "users") fetchUsers();
  }, [tab]);

  const handleConfirm = async (payId: string, action: "confirm" | "reject") => {
    setLoading(true);
    try {
      await paymentsApi.adminConfirm({ payment_id: payId, action, note: confirmNote[payId] || "" });
      toast.success(action === "confirm" ? "Payment confirmed. Analysis queued!" : "Payment rejected.");
      fetchPayments();
      fetchStats();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Action failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRerun = async (caseId: string) => {
    try {
      await adminApi.rerunAnalysis(caseId);
      toast.success("Analysis re-queued");
    } catch { toast.error("Failed"); }
  };

  const handleToggleUser = async (userId: string) => {
    try {
      await adminApi.toggleUser(userId);
      toast.success("User updated");
      fetchUsers();
    } catch { toast.error("Failed"); }
  };

  const TABS: { id: Tab; label: string; labelBn: string; icon: any }[] = [
    { id: "overview",  label: "Overview",         labelBn: "সংক্ষিপ্ত বিবরণ", icon: ShieldCheck },
    { id: "payments",  label: "Pending Payments",  labelBn: "মুলতুবি পেমেন্ট",  icon: Clock },
    { id: "cases",     label: "All Cases",          labelBn: "সকল কেস",          icon: Briefcase },
    { id: "users",     label: "Users",              labelBn: "ব্যবহারকারী",       icon: Users },
  ];

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="section-title flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-gold" />
            {lang === "en" ? "Admin Dashboard" : "অ্যাডমিন ড্যাশবোর্ড"}
          </h1>
          <p className="section-sub">{lang === "en" ? "NLC Land Evidence Management" : "এনএলসি ভূমি প্রমাণ ব্যবস্থাপনা"}</p>
        </div>
        <button onClick={() => { fetchStats(); fetchPayments(); }} className="btn-ghost flex items-center gap-1.5 text-xs">
          <RefreshCw className="w-3.5 h-3.5" /> {lang === "en" ? "Refresh" : "রিফ্রেশ"}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-navy-50/60 rounded-xl p-1 mb-8 overflow-x-auto">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={clsx(
              "flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all",
              tab === t.id ? "bg-navy text-white shadow-sm" : "text-navy/50 hover:text-navy hover:bg-white/60"
            )}>
            <t.icon className="w-4 h-4" />
            {lang === "en" ? t.label : t.labelBn}
            {t.id === "payments" && payments.length > 0 && (
              <span className="bg-amber-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-full">
                {payments.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ── Overview ────────────────────────────────────── */}
      {tab === "overview" && stats && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: lang === "en" ? "Total Users" : "মোট ব্যবহারকারী", value: stats.total_users, icon: Users, color: "text-blue-600 bg-blue-50" },
              { label: lang === "en" ? "Total Cases" : "মোট কেস", value: stats.total_cases, icon: Briefcase, color: "text-navy bg-navy-50" },
              { label: lang === "en" ? "Completed" : "সম্পন্ন", value: stats.completed_cases, icon: CheckCircle2, color: "text-emerald-600 bg-emerald-50" },
              { label: lang === "en" ? "Revenue (BDT)" : "আয় (টাকা)", value: `৳${stats.total_revenue_bdt?.toLocaleString()}`, icon: TrendingUp, color: "text-gold bg-gold/10" },
            ].map(s => (
              <div key={s.label} className="card p-5">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${s.color}`}>
                  <s.icon className="w-5 h-5" />
                </div>
                <div className="text-2xl font-bold font-mono text-navy">{s.value}</div>
                <div className="text-xs text-navy/40 mt-1">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Risk distribution */}
          <div className="card p-6">
            <h3 className="font-display text-base font-semibold text-navy mb-4">
              {lang === "en" ? "Risk Distribution" : "ঝুঁকি বণ্টন"}
            </h3>
            <div className="grid grid-cols-4 gap-3">
              {Object.entries(stats.risk_distribution || {}).map(([band, count]: [string, any]) => (
                <div key={band} className="text-center">
                  <div className="text-2xl font-bold font-mono text-navy">{count}</div>
                  <RiskBadge band={band} size="sm" />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Pending Payments ────────────────────────────── */}
      {tab === "payments" && (
        <div className="space-y-4">
          {payments.length === 0 ? (
            <div className="card p-12 text-center">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
              <p className="text-navy/40">{lang === "en" ? "No pending payments" : "কোনো মুলতুবি পেমেন্ট নেই"}</p>
            </div>
          ) : payments.map(p => (
            <div key={p.id} className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="font-semibold text-navy text-sm">{p.case_id}</div>
                  <div className="text-xs text-navy/40 mt-0.5">
                    {p.method?.toUpperCase()} · ৳{p.amount} · {p.payment_number || "—"}
                  </div>
                  <div className="text-xs text-navy/30 mt-0.5">
                    {p.created_at ? new Date(p.created_at).toLocaleString("en-BD") : "—"}
                  </div>
                </div>
                {p.proof_path && (
                  <span className="text-xs text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-200 font-medium">
                    Proof uploaded
                  </span>
                )}
              </div>
              <input
                placeholder={lang === "en" ? "Admin note (optional)" : "অ্যাডমিন মন্তব্য (ঐচ্ছিক)"}
                value={confirmNote[p.id] || ""}
                onChange={e => setConfirmNote(prev => ({ ...prev, [p.id]: e.target.value }))}
                className="input mb-3 text-sm"
              />
              <div className="flex gap-2">
                <button onClick={() => handleConfirm(p.id, "confirm")} disabled={loading}
                  className="btn-gold flex items-center gap-1.5 text-sm py-2">
                  <CheckCircle2 className="w-4 h-4" />
                  {lang === "en" ? "Confirm & Queue Analysis" : "নিশ্চিত করুন"}
                </button>
                <button onClick={() => handleConfirm(p.id, "reject")} disabled={loading}
                  className="btn-outline flex items-center gap-1.5 text-sm py-2 text-red-600 border-red-200 hover:bg-red-50">
                  <XCircle className="w-4 h-4" />
                  {lang === "en" ? "Reject" : "প্রত্যাখ্যান"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── All Cases ───────────────────────────────────── */}
      {tab === "cases" && (
        <div className="card overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Case Ref</th>
                <th>Title</th>
                <th>Status</th>
                <th>Risk</th>
                <th>Plan</th>
                <th>District</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cases.map(c => (
                <tr key={c.id}>
                  <td className="font-mono text-xs">{c.case_ref}</td>
                  <td className="max-w-xs truncate">{c.title}</td>
                  <td><StatusPill status={c.status} /></td>
                  <td>{c.overall_risk_band ? <RiskBadge band={c.overall_risk_band} /> : "—"}</td>
                  <td className="capitalize">{c.plan}</td>
                  <td>{c.district || "—"}</td>
                  <td className="text-xs">{c.created_at ? new Date(c.created_at).toLocaleDateString("en-BD") : "—"}</td>
                  <td>
                    <div className="flex gap-1">
                      <Link href={`/case/${c.id}`} className="btn-ghost py-1 px-2 text-xs flex items-center gap-1">
                        <FileSearch className="w-3 h-3" /> View
                      </Link>
                      <button onClick={() => handleRerun(c.id)} className="btn-ghost py-1 px-2 text-xs flex items-center gap-1">
                        <RotateCcw className="w-3 h-3" /> Rerun
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {cases.length === 0 && (
            <div className="p-12 text-center text-navy/30">{lang === "en" ? "No cases found" : "কোনো কেস পাওয়া যায়নি"}</div>
          )}
        </div>
      )}

      {/* ── Users ───────────────────────────────────────── */}
      {tab === "users" && (
        <div className="card overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role</th>
                <th>Active</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td className="font-medium">{u.full_name}</td>
                  <td className="text-xs text-navy/60">{u.email}</td>
                  <td className="font-mono text-xs">{u.phone || "—"}</td>
                  <td><span className={clsx("text-xs font-bold px-2 py-0.5 rounded-full", u.role === "admin" ? "bg-navy text-white" : "bg-navy-50 text-navy")}>{u.role}</span></td>
                  <td>
                    <span className={clsx("text-xs font-bold px-2 py-0.5 rounded-full", u.is_active ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700")}>
                      {u.is_active ? "Active" : "Disabled"}
                    </span>
                  </td>
                  <td className="text-xs">{u.created_at ? new Date(u.created_at).toLocaleDateString("en-BD") : "—"}</td>
                  <td>
                    <button onClick={() => handleToggleUser(u.id)} className="btn-ghost py-1 px-2 text-xs">
                      {u.is_active ? "Disable" : "Enable"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {users.length === 0 && (
            <div className="p-12 text-center text-navy/30">{lang === "en" ? "No users found" : "কোনো ব্যবহারকারী পাওয়া যায়নি"}</div>
          )}
        </div>
      )}
    </div>
  );
}
