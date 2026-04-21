"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import { t } from "@/lib/i18n";
import { Scale, LayoutDashboard, FileSearch, ShieldCheck, LogOut, Globe, Menu, X } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

export default function Navbar() {
  const { user, logout, lang, setLang, isAdmin } = useAuthStore();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const navLinks = [
    { href: "/dashboard", label: t(lang, "dashboard"), icon: LayoutDashboard },
    { href: "/case/new", label: t(lang, "newCase"), icon: FileSearch },
    ...(isAdmin() ? [{ href: "/admin", label: t(lang, "admin"), icon: ShieldCheck }] : []),
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-navy-100/40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 bg-navy rounded-lg flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
              <Scale className="w-5 h-5 text-gold" />
            </div>
            <div className="hidden sm:block">
              <div className="font-display font-semibold text-navy text-sm leading-none">Neum Lex Counsel</div>
              <div className="text-gold text-[10px] italic tracking-wide leading-none mt-0.5">Justice. Reimagined.</div>
            </div>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {user && navLinks.map(({ href, label, icon: Icon }) => (
              <Link key={href} href={href}
                className={clsx("flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                  pathname.startsWith(href)
                    ? "bg-navy text-white"
                    : "text-navy/60 hover:text-navy hover:bg-navy-50"
                )}>
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            ))}
          </div>

          {/* Right actions */}
          <div className="flex items-center gap-2">
            {/* Language toggle */}
            <button
              onClick={() => setLang(lang === "en" ? "bn" : "en")}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-navy-100/60 text-xs font-medium text-navy/60 hover:text-navy hover:border-navy/30 transition-colors"
            >
              <Globe className="w-3.5 h-3.5" />
              {lang === "en" ? "বাং" : "EN"}
            </button>

            {user ? (
              <>
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-navy-50 rounded-lg">
                  <div className="w-6 h-6 bg-navy rounded-full flex items-center justify-center text-white text-xs font-bold">
                    {user.full_name[0]}
                  </div>
                  <span className="text-xs font-medium text-navy">{user.full_name.split(" ")[0]}</span>
                </div>
                <button onClick={logout} className="btn-ghost flex items-center gap-1.5 text-red-500 hover:bg-red-50">
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:inline text-xs">{t(lang, "logout")}</span>
                </button>
              </>
            ) : (
              <div className="flex gap-2">
                <Link href="/auth/login" className="btn-outline py-2 px-4 text-xs">{t(lang, "login")}</Link>
                <Link href="/auth/register" className="btn-primary py-2 px-4 text-xs">{t(lang, "register")}</Link>
              </div>
            )}

            {/* Mobile menu */}
            <button onClick={() => setOpen(!open)} className="md:hidden btn-ghost p-2">
              {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu drawer */}
      {open && (
        <div className="md:hidden border-t border-navy-100/30 bg-white px-4 py-3 space-y-1 fade-in">
          {user && navLinks.map(({ href, label, icon: Icon }) => (
            <Link key={href} href={href} onClick={() => setOpen(false)}
              className={clsx("flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors",
                pathname.startsWith(href) ? "bg-navy text-white" : "text-navy/70 hover:bg-navy-50"
              )}>
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}
