"use client";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";
import clsx from "clsx";
import { casesApi, docsApi, paymentsApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { t } from "@/lib/i18n";
import {
  FileText, Upload, CreditCard, CheckCircle2, X,
  CloudUpload, Banknote, Smartphone, Building, Coins,
  ChevronRight, ChevronLeft, Check
} from "lucide-react";

const DISTRICTS = ["Dhaka","Chittagong","Rajshahi","Khulna","Sylhet","Barisal","Rangpur","Mymensingh","Comilla","Narayanganj","Gazipur","Tangail","Bogra","Jessore","Dinajpur","Faridpur","Noakhali","Cox's Bazar","Brahmanbaria","Narsingdi"];
const DOC_TYPES = ["deed","khatian","mutation","baya","rajuk_approval","redma_certificate","mortgage_document","survey_map","tax_receipt","noc","court_order","other"];
const PAYMENT_METHODS = [
  { id: "bkash",  icon: Smartphone,  label: "bKash",          labelBn: "বিকাশ",         color: "border-pink-200 bg-pink-50" },
  { id: "nagad",  icon: Smartphone,  label: "Nagad",          labelBn: "নগদ",           color: "border-orange-200 bg-orange-50" },
  { id: "bank",   icon: Building,    label: "Bank Transfer",  labelBn: "ব্যাংক ট্রান্সফার", color: "border-blue-200 bg-blue-50" },
  { id: "cash",   icon: Coins,       label: "Cash",           labelBn: "নগদ অর্থ",       color: "border-green-200 bg-green-50" },
];

const caseSchema = z.object({
  title: z.string().min(3, "Required"),
  property_type: z.string().min(1, "Required"),
  district: z.string().optional(),
  upazila: z.string().optional(),
  property_address: z.string().optional(),
  plan: z.string(),
  notes: z.string().optional(),
});

const PLAN_PRICES: Record<string, number> = { basic: 499, standard: 999, premium: 2499 };
const PLAN_DOCS: Record<string, number | string> = { basic: 1, standard: 5, premium: "∞" };
const PLAN_CHECKS: Record<string, number> = { basic: 5, standard: 10, premium: 14 };

const STEPS = ["Case Details", "Upload Documents", "Payment"];
const STEPS_BN = ["কেসের বিবরণ", "দলিল আপলোড", "পেমেন্ট"];

export default function NewCasePage() {
  const router = useRouter();
  const { lang } = useAuthStore();
  const [step, setStep] = useState(0);
  const [caseId, setCaseId] = useState<string | null>(null);
  const [caseRef, setCaseRef] = useState<string | null>(null);
  const [files, setFiles] = useState<{ file: File; docType: string; uploaded: boolean }[]>([]);
  const [payMethod, setPayMethod] = useState("bkash");
  const [payPhone, setPayPhone] = useState("");
  const [proofFile, setProofFile] = useState<File | null>(null);
  const [paymentInfo, setPaymentInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState("standard");

  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    resolver: zodResolver(caseSchema),
    defaultValues: { plan: "standard", property_type: "land" },
  });

  // Step 1 — Create case
  const onCreateCase = handleSubmit(async (data) => {
    setLoading(true);
    try {
      const res = await casesApi.create({ ...data, plan });
      setCaseId(res.data.id);
      setCaseRef(res.data.case_ref);
      setStep(1);
      toast.success(lang === "en" ? "Case created!" : "কেস তৈরি হয়েছে!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to create case");
    } finally {
      setLoading(false);
    }
  });

  // File drop
  const onDrop = useCallback((accepted: File[]) => {
    setFiles(prev => [...prev, ...accepted.map(f => ({ file: f, docType: "deed", uploaded: false }))]);
  }, []);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "application/pdf": [], "image/*": [] }, maxSize: 20 * 1024 * 1024,
  });

  // Step 2 — Upload docs
  const onUploadDocs = async () => {
    if (files.length === 0) { toast.error("Upload at least one document"); return; }
    setLoading(true);
    let allOk = true;
    for (let i = 0; i < files.length; i++) {
      if (files[i].uploaded) continue;
      const fd = new FormData();
      fd.append("case_id", caseId!);
      fd.append("doc_type", files[i].docType);
      fd.append("doc_name", files[i].file.name);
      fd.append("file", files[i].file);
      try {
        await docsApi.upload(fd);
        setFiles(prev => prev.map((f, idx) => idx === i ? { ...f, uploaded: true } : f));
      } catch {
        allOk = false;
        toast.error(`Failed: ${files[i].file.name}`);
      }
    }
    setLoading(false);
    if (allOk) { setStep(2); toast.success(lang === "en" ? "Documents uploaded!" : "দলিল আপলোড হয়েছে!"); }
  };

  // Step 3 — Payment
  const onPay = async () => {
    setLoading(true);
    try {
      const res = await paymentsApi.initiate({ case_id: caseId, method: payMethod, payment_number: payPhone });
      setPaymentInfo(res.data);
      toast.success(lang === "en" ? "Payment initiated!" : "পেমেন্ট শুরু হয়েছে!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Payment failed");
    } finally {
      setLoading(false);
    }
  };

  const onUploadProof = async () => {
    if (!proofFile || !paymentInfo) return;
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("payment_id", paymentInfo.payment_id);
      fd.append("file", proofFile);
      await paymentsApi.uploadProof(fd);
      toast.success(lang === "en" ? "Proof uploaded! Admin will confirm shortly." : "প্রমাণ আপলোড হয়েছে! অ্যাডমিন শীঘ্রই নিশ্চিত করবেন।");
      router.push("/dashboard");
    } catch {
      toast.error("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="section-title">{lang === "en" ? "New Analysis" : "নতুন বিশ্লেষণ"}</h1>
        <p className="section-sub">{lang === "en" ? "AI forensic property analysis — Bangladesh law" : "এআই ফরেনসিক সম্পত্তি বিশ্লেষণ"}</p>
      </div>

      {/* Stepper */}
      <div className="flex items-center gap-0 mb-10">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center flex-1 last:flex-none">
            <div className={clsx(
              "flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-sm font-medium transition-all",
              i === step ? "bg-navy text-white shadow-md" : i < step ? "bg-emerald-100 text-emerald-700" : "bg-white text-navy/30 border border-navy-100/40"
            )}>
              <div className={clsx("w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
                i === step ? "bg-white/20" : i < step ? "bg-emerald-200" : "bg-navy-100/30"
              )}>
                {i < step ? <Check className="w-3.5 h-3.5" /> : i + 1}
              </div>
              <span className="hidden sm:inline">{lang === "en" ? s : STEPS_BN[i]}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={clsx("h-px flex-1 mx-2 transition-colors", i < step ? "bg-emerald-300" : "bg-navy-100/40")} />
            )}
          </div>
        ))}
      </div>

      {/* ── Step 0: Case Details ─────────────────────────── */}
      {step === 0 && (
        <div className="card p-8 space-y-6">
          <div>
            <label className="label">{t(lang, "caseTitle")} *</label>
            <input {...register("title")} placeholder={lang === "en" ? "e.g. Gulshan Plot Purchase Verification" : "যেমন: গুলশান প্লট ক্রয় যাচাই"} className="input" />
            {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title.message as string}</p>}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">{t(lang, "propertyType")} *</label>
              <select {...register("property_type")} className="select">
                <option value="land">{lang === "en" ? "Land / Plot" : "জমি / প্লট"}</option>
                <option value="flat">{lang === "en" ? "Flat / Apartment" : "ফ্ল্যাট / অ্যাপার্টমেন্ট"}</option>
                <option value="commercial">{lang === "en" ? "Commercial Space" : "বাণিজ্যিক স্থান"}</option>
                <option value="building">{lang === "en" ? "Building" : "ভবন"}</option>
              </select>
            </div>
            <div>
              <label className="label">{t(lang, "district")}</label>
              <select {...register("district")} className="select">
                <option value="">{lang === "en" ? "Select district" : "জেলা বেছে নিন"}</option>
                {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">{t(lang, "upazila")}</label>
              <input {...register("upazila")} placeholder={lang === "en" ? "Upazila / Thana" : "উপজেলা / থানা"} className="input" />
            </div>
            <div>
              <label className="label">{t(lang, "propertyAddress")}</label>
              <input {...register("property_address")} placeholder={lang === "en" ? "Mouza, Dag No." : "মৌজা, দাগ নং"} className="input" />
            </div>
          </div>

          {/* Plan selector */}
          <div>
            <label className="label">{t(lang, "selectPlan")}</label>
            <div className="grid grid-cols-3 gap-3 mt-1">
              {["basic", "standard", "premium"].map(p => (
                <button key={p} type="button" onClick={() => setPlan(p)}
                  className={clsx("border-2 rounded-xl p-4 text-left transition-all",
                    plan === p ? "border-gold bg-gold/5 shadow-gold-glow" : "border-navy-100/40 hover:border-navy/20"
                  )}>
                  <div className="font-semibold text-navy capitalize text-sm">{p}</div>
                  <div className="text-gold font-bold font-mono mt-1">৳{PLAN_PRICES[p]}</div>
                  <div className="text-xs text-navy/40 mt-1">{PLAN_DOCS[p]} docs · {PLAN_CHECKS[p]} checks</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="label">{lang === "en" ? "Notes (optional)" : "মন্তব্য (ঐচ্ছিক)"}</label>
            <textarea {...register("notes")} rows={2} placeholder={lang === "en" ? "Any specific concerns..." : "কোনো বিশেষ উদ্বেগ..."} className="input resize-none" />
          </div>

          <div className="flex justify-end pt-2">
            <button onClick={onCreateCase} disabled={loading} className="btn-gold flex items-center gap-2">
              {loading && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
              {t(lang, "createCase")} <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ── Step 1: Upload Documents ─────────────────────── */}
      {step === 1 && (
        <div className="card p-8 space-y-6">
          <div>
            <h3 className="font-display text-lg font-semibold text-navy mb-1">
              {t(lang, "uploadDocuments")}
            </h3>
            <p className="text-navy/40 text-sm">
              {lang === "en" ? "Upload PDF or images. Max 20MB each. Supported: deed, khatian, mutation, RAJUK, survey maps..." : "পিডিএফ বা ছবি আপলোড করুন। সর্বোচ্চ ২০ এমবি।"}
            </p>
          </div>

          {/* Drop zone */}
          <div {...getRootProps()} className={clsx(
            "border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all",
            isDragActive ? "border-gold bg-gold/5" : "border-navy-100/60 hover:border-gold/60 hover:bg-gold/2"
          )}>
            <input {...getInputProps()} />
            <CloudUpload className={clsx("w-10 h-10 mx-auto mb-3", isDragActive ? "text-gold" : "text-navy/20")} />
            <p className="text-navy/60 font-medium text-sm">
              {isDragActive
                ? (lang === "en" ? "Drop files here" : "ফাইল ছাড়ুন")
                : (lang === "en" ? "Drag & drop files, or click to browse" : "ফাইল টেনে আনুন বা ক্লিক করুন")}
            </p>
            <p className="text-navy/30 text-xs mt-1">PDF, JPG, PNG · Max 20MB</p>
          </div>

          {/* File list */}
          {files.length > 0 && (
            <div className="space-y-2">
              {files.map((f, i) => (
                <div key={i} className={clsx("flex items-center gap-3 p-3 rounded-xl border", f.uploaded ? "border-emerald-200 bg-emerald-50" : "border-navy-100/40 bg-white")}>
                  <FileText className={clsx("w-5 h-5 flex-shrink-0", f.uploaded ? "text-emerald-600" : "text-navy/40")} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-navy truncate">{f.file.name}</p>
                    <p className="text-xs text-navy/30">{(f.file.size / 1024).toFixed(0)} KB</p>
                  </div>
                  <select
                    value={f.docType}
                    onChange={e => setFiles(prev => prev.map((x, idx) => idx === i ? { ...x, docType: e.target.value } : x))}
                    className="text-xs border border-navy-100/40 rounded-lg px-2 py-1.5 bg-white outline-none focus:border-gold/60"
                    disabled={f.uploaded}
                  >
                    {DOC_TYPES.map(dt => (
                      <option key={dt} value={dt}>{(t(lang, dt as any) || dt)}</option>
                    ))}
                  </select>
                  {f.uploaded
                    ? <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                    : <button onClick={() => setFiles(prev => prev.filter((_, idx) => idx !== i))} className="text-navy/20 hover:text-red-500 transition-colors"><X className="w-4 h-4" /></button>
                  }
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between pt-2">
            <button onClick={() => setStep(0)} className="btn-ghost flex items-center gap-2">
              <ChevronLeft className="w-4 h-4" /> {lang === "en" ? "Back" : "পেছনে"}
            </button>
            <button onClick={onUploadDocs} disabled={loading || files.length === 0} className="btn-gold flex items-center gap-2">
              {loading && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
              <Upload className="w-4 h-4" />
              {lang === "en" ? "Upload & Continue" : "আপলোড করুন"} <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* ── Step 2: Payment ──────────────────────────────── */}
      {step === 2 && (
        <div className="card p-8 space-y-6">
          <div>
            <h3 className="font-display text-lg font-semibold text-navy mb-1">{t(lang, "payNow")}</h3>
            <p className="text-navy/40 text-sm">
              {lang === "en" ? `Case: ${caseRef} · Plan: ${plan} · Amount: ৳${PLAN_PRICES[plan]}` : `কেস: ${caseRef} · পরিকল্পনা: ${plan} · পরিমাণ: ৳${PLAN_PRICES[plan]}`}
            </p>
          </div>

          {!paymentInfo ? (
            <>
              {/* Method selector */}
              <div>
                <label className="label">{t(lang, "paymentMethod")}</label>
                <div className="grid grid-cols-2 gap-3 mt-1">
                  {PAYMENT_METHODS.map(m => (
                    <button key={m.id} type="button" onClick={() => setPayMethod(m.id)}
                      className={clsx("border-2 rounded-xl p-4 flex items-center gap-3 transition-all",
                        payMethod === m.id ? "border-gold bg-gold/5" : `${m.color} border-opacity-50`
                      )}>
                      <m.icon className={clsx("w-5 h-5", payMethod === m.id ? "text-gold" : "text-navy/50")} />
                      <div className="text-left">
                        <div className="font-semibold text-sm text-navy">{lang === "en" ? m.label : m.labelBn}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {(payMethod === "bkash" || payMethod === "nagad") && (
                <div>
                  <label className="label">{lang === "en" ? "Your bKash/Nagad Number" : "আপনার বিকাশ/নগদ নম্বর"}</label>
                  <input value={payPhone} onChange={e => setPayPhone(e.target.value)} placeholder="01XXXXXXXXX" className="input" />
                </div>
              )}

              <div className="flex items-center justify-between">
                <button onClick={() => setStep(1)} className="btn-ghost flex items-center gap-2">
                  <ChevronLeft className="w-4 h-4" /> {lang === "en" ? "Back" : "পেছনে"}
                </button>
                <button onClick={onPay} disabled={loading} className="btn-gold flex items-center gap-2">
                  {loading && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
                  <CreditCard className="w-4 h-4" />
                  {lang === "en" ? "Proceed to Pay" : "পেমেন্টে যান"} <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            /* Payment instructions */
            <div className="space-y-5">
              <div className="bg-navy-50 rounded-2xl p-6 border border-navy-100/40">
                <h4 className="font-semibold text-navy mb-3 flex items-center gap-2">
                  <Banknote className="w-5 h-5 text-gold" />
                  {lang === "en" ? "Payment Instructions" : "পেমেন্টের নির্দেশনা"}
                </h4>
                <p className="text-navy/70 text-sm leading-relaxed">
                  {lang === "en" ? paymentInfo.gateway?.instructions_en : paymentInfo.gateway?.instructions_bn}
                </p>
                {paymentInfo.gateway?.redirect_url && (
                  <a href={paymentInfo.gateway.redirect_url} target="_blank" rel="noopener noreferrer"
                    className="btn-gold mt-4 inline-flex items-center gap-2 text-sm">
                    Pay via {payMethod === "bkash" ? "bKash" : "Nagad"} <ChevronRight className="w-4 h-4" />
                  </a>
                )}
              </div>

              {/* Proof upload */}
              <div>
                <label className="label">{t(lang, "uploadProof")}</label>
                <input
                  type="file" accept="image/*,application/pdf"
                  onChange={e => setProofFile(e.target.files?.[0] || null)}
                  className="input text-sm file:mr-3 file:py-1.5 file:px-4 file:rounded-lg file:border-0 file:bg-navy file:text-white file:text-xs file:font-medium cursor-pointer"
                />
              </div>

              <button onClick={onUploadProof} disabled={loading || !proofFile} className="btn-gold w-full flex items-center justify-center gap-2">
                {loading && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
                <Upload className="w-4 h-4" />
                {lang === "en" ? "Submit Proof & Go to Dashboard" : "প্রমাণ জমা দিন ও ড্যাশবোর্ডে যান"}
              </button>

              <p className="text-xs text-navy/30 text-center">
                {lang === "en"
                  ? "Admin will confirm your payment and analysis will begin automatically."
                  : "অ্যাডমিন আপনার পেমেন্ট নিশ্চিত করবেন এবং বিশ্লেষণ স্বয়ংক্রিয়ভাবে শুরু হবে।"}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
