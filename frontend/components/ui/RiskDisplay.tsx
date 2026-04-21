"use client";
import clsx from "clsx";
import { Shield, ShieldAlert, ShieldX, ShieldOff } from "lucide-react";

const BAND_CONFIG = {
  GREEN:  { icon: Shield,     label: "GREEN",  labelBn: "সবুজ",   bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", iconColor: "text-emerald-600" },
  YELLOW: { icon: ShieldAlert, label: "YELLOW", labelBn: "হলুদ",   bg: "bg-amber-50",   border: "border-amber-200",   text: "text-amber-700",   iconColor: "text-amber-600" },
  RED:    { icon: ShieldX,    label: "RED",    labelBn: "লাল",    bg: "bg-red-50",     border: "border-red-200",     text: "text-red-700",     iconColor: "text-red-600" },
  BLACK:  { icon: ShieldOff,  label: "BLACK",  labelBn: "কালো",   bg: "bg-gray-900",   border: "border-gray-700",    text: "text-white",       iconColor: "text-gray-300" },
};

export function RiskBadge({ band, size = "sm" }: { band: string; size?: "sm" | "md" | "lg" }) {
  const cfg = BAND_CONFIG[band as keyof typeof BAND_CONFIG] || BAND_CONFIG.GREEN;
  const Icon = cfg.icon;
  return (
    <span className={clsx(
      "inline-flex items-center gap-1.5 font-bold rounded-full border",
      cfg.bg, cfg.border, cfg.text,
      size === "sm" && "text-xs px-2.5 py-1",
      size === "md" && "text-sm px-3 py-1.5",
      size === "lg" && "text-base px-4 py-2",
    )}>
      <Icon className={clsx("w-3.5 h-3.5", cfg.iconColor)} />
      {cfg.label}
    </span>
  );
}

export function RiskCard({
  band, score, lang = "en",
}: { band: string; score: number; lang?: "en" | "bn" }) {
  const cfg = BAND_CONFIG[band as keyof typeof BAND_CONFIG] || BAND_CONFIG.GREEN;
  const Icon = cfg.icon;

  const descs: Record<string, { en: string; bn: string }> = {
    GREEN:  { en: "Low risk — proceed with standard due diligence", bn: "কম ঝুঁকি — স্বাভাবিক যথাযথ পরিশ্রম করুন" },
    YELLOW: { en: "Moderate risk — verify flagged items before proceeding", bn: "মাঝারি ঝুঁকি — চিহ্নিত বিষয়গুলো যাচাই করুন" },
    RED:    { en: "High risk — do not proceed without legal clearance", bn: "উচ্চ ঝুঁকি — আইনি ছাড়পত্র ছাড়া এগিয়ে যাবেন না" },
    BLACK:  { en: "Critical risk — halt all transactions immediately", bn: "সংকটজনক ঝুঁকি — সকল লেনদেন তাৎক্ষণিকভাবে বন্ধ করুন" },
  };
  const desc = descs[band] || descs.GREEN;

  return (
    <div className={clsx("rounded-2xl border-2 p-6", cfg.bg, cfg.border)}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={clsx("w-12 h-12 rounded-xl flex items-center justify-center",
            band === "BLACK" ? "bg-gray-700" : "bg-white shadow-sm"
          )}>
            <Icon className={clsx("w-6 h-6", cfg.iconColor)} />
          </div>
          <div>
            <div className={clsx("text-xs font-semibold uppercase tracking-wider opacity-60", cfg.text)}>
              {lang === "en" ? "Overall Risk Band" : "সামগ্রিক ঝুঁকি স্তর"}
            </div>
            <div className={clsx("text-3xl font-display font-bold", cfg.text)}>{band}</div>
          </div>
        </div>
        <div className="text-right">
          <div className={clsx("text-xs font-semibold uppercase tracking-wider opacity-60 mb-1", cfg.text)}>
            {lang === "en" ? "Risk Score" : "ঝুঁকি স্কোর"}
          </div>
          <div className={clsx("text-4xl font-bold font-mono", cfg.text)}>{score.toFixed(0)}</div>
          <div className={clsx("text-xs opacity-50", cfg.text)}>/100</div>
        </div>
      </div>
      <p className={clsx("text-sm", cfg.text, "opacity-80")}>
        {lang === "en" ? desc.en : desc.bn}
      </p>
    </div>
  );
}

export function StatusPill({ status }: { status: string }) {
  const map: Record<string, string> = {
    draft: "bg-gray-100 text-gray-600",
    pending_payment: "bg-amber-100 text-amber-700",
    paid: "bg-blue-100 text-blue-700",
    processing: "bg-purple-100 text-purple-700",
    completed: "bg-emerald-100 text-emerald-700",
    failed: "bg-red-100 text-red-700",
  };
  return (
    <span className={clsx("text-xs font-bold px-2.5 py-1 rounded-full capitalize", map[status] || "bg-gray-100 text-gray-600")}>
      {status.replace("_", " ")}
    </span>
  );
}
