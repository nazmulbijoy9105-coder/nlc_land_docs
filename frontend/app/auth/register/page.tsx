"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { Scale, Eye, EyeOff, UserPlus } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

const schema = z.object({
  full_name: z.string().min(2, "Required"),
  full_name_bn: z.string().optional(),
  email: z.string().email("Invalid email"),
  phone: z.string().optional(),
  password: z.string().min(8, "Min 8 characters"),
  preferred_lang: z.enum(["en", "bn"]),
});

export default function RegisterPage() {
  const router = useRouter();
  const { setAuth, lang } = useAuthStore();
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { preferred_lang: "en" },
  });

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      const res = await authApi.register(data);
      setAuth(res.data.token, res.data.user);
      toast.success("Account created!");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-hero-pattern flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-navy rounded-2xl shadow-lg mb-4">
            <Scale className="w-7 h-7 text-gold" />
          </div>
          <h1 className="font-display text-2xl font-bold text-navy">Neum Lex Counsel</h1>
          <p className="text-gold text-sm italic mt-1">Justice. Reimagined.</p>
        </div>

        <div className="card p-8">
          <h2 className="font-display text-xl font-semibold text-navy mb-1">
            {lang === "en" ? "Create Account" : "অ্যাকাউন্ট তৈরি করুন"}
          </h2>
          <p className="text-navy/40 text-sm mb-6">
            {lang === "en" ? "Start your first property analysis" : "আপনার প্রথম সম্পত্তি বিশ্লেষণ শুরু করুন"}
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">{lang === "en" ? "Full Name" : "পূর্ণ নাম"} *</label>
                <input {...register("full_name")} placeholder="John Doe" className="input" />
                {errors.full_name && <p className="text-red-500 text-xs mt-1">{errors.full_name.message as string}</p>}
              </div>
              <div>
                <label className="label">নাম (বাংলা)</label>
                <input {...register("full_name_bn")} placeholder="জন ডো" className="input" />
              </div>
            </div>

            <div>
              <label className="label">Email *</label>
              <input {...register("email")} type="email" placeholder="you@example.com" className="input" />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message as string}</p>}
            </div>

            <div>
              <label className="label">{lang === "en" ? "Phone (bKash/Nagad)" : "ফোন (বিকাশ/নগদ)"}</label>
              <input {...register("phone")} placeholder="01XXXXXXXXX" className="input" />
            </div>

            <div>
              <label className="label">{lang === "en" ? "Password" : "পাসওয়ার্ড"} *</label>
              <div className="relative">
                <input {...register("password")} type={show ? "text" : "password"} placeholder="Min. 8 characters" className="input pr-10" />
                <button type="button" onClick={() => setShow(!show)} className="absolute right-3 top-1/2 -translate-y-1/2 text-navy/30 hover:text-navy/60">
                  {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message as string}</p>}
            </div>

            <div>
              <label className="label">{lang === "en" ? "Preferred Language" : "পছন্দের ভাষা"}</label>
              <select {...register("preferred_lang")} className="select">
                <option value="en">English</option>
                <option value="bn">বাংলা</option>
              </select>
            </div>

            <button type="submit" disabled={loading} className="btn-gold w-full flex items-center justify-center gap-2 mt-2">
              {loading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : <UserPlus className="w-4 h-4" />}
              {lang === "en" ? "Create Account" : "অ্যাকাউন্ট তৈরি করুন"}
            </button>
          </form>

          <div className="gold-line" />
          <p className="text-center text-sm text-navy/40">
            {lang === "en" ? "Already have an account?" : "ইতিমধ্যে অ্যাকাউন্ট আছে?"}{" "}
            <Link href="/auth/login" className="text-gold font-medium hover:text-gold-600">
              {lang === "en" ? "Sign In" : "লগইন করুন"}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
