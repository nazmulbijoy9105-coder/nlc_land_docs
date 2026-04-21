"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { Scale, Eye, EyeOff, LogIn } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(1, "Required"),
});

export default function LoginPage() {
  const router = useRouter();
  const { setAuth, lang } = useAuthStore();
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      const res = await authApi.login(data);
      setAuth(res.data.token, res.data.user);
      toast.success("Welcome back!");
      router.push(res.data.user.role === "admin" || res.data.user.role === "superadmin" ? "/admin" : "/dashboard");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-hero-pattern flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-navy rounded-2xl shadow-lg mb-4">
            <Scale className="w-7 h-7 text-gold" />
          </div>
          <h1 className="font-display text-2xl font-bold text-navy">Neum Lex Counsel</h1>
          <p className="text-gold text-sm italic mt-1">Justice. Reimagined.</p>
        </div>

        <div className="card p-8">
          <h2 className="font-display text-xl font-semibold text-navy mb-1">
            {lang === "en" ? "Sign In" : "লগইন"}
          </h2>
          <p className="text-navy/40 text-sm mb-6">
            {lang === "en" ? "Access your NLC Land Evidence account" : "আপনার এনএলসি অ্যাকাউন্টে প্রবেশ করুন"}
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="label">Email</label>
              <input {...register("email")} type="email" placeholder="you@example.com" className="input" />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message as string}</p>}
            </div>
            <div>
              <label className="label">{lang === "en" ? "Password" : "পাসওয়ার্ড"}</label>
              <div className="relative">
                <input {...register("password")} type={show ? "text" : "password"} placeholder="••••••••" className="input pr-10" />
                <button type="button" onClick={() => setShow(!show)} className="absolute right-3 top-1/2 -translate-y-1/2 text-navy/30 hover:text-navy/60">
                  {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message as string}</p>}
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 mt-2">
              {loading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : <LogIn className="w-4 h-4" />}
              {lang === "en" ? "Sign In" : "লগইন করুন"}
            </button>
          </form>

          <div className="gold-line" />
          <p className="text-center text-sm text-navy/40">
            {lang === "en" ? "Don't have an account?" : "অ্যাকাউন্ট নেই?"}{" "}
            <Link href="/auth/register" className="text-gold font-medium hover:text-gold-600">
              {lang === "en" ? "Register" : "নিবন্ধন করুন"}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
