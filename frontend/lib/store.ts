import { create } from "zustand";
import Cookies from "js-cookie";

interface User {
  id: string;
  email: string;
  full_name: string;
  full_name_bn?: string;
  role: string;
  preferred_lang: string;
  phone?: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  lang: "en" | "bn";
  setAuth: (token: string, user: User) => void;
  setLang: (lang: "en" | "bn") => void;
  logout: () => void;
  isAdmin: () => boolean;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: typeof window !== "undefined" ? Cookies.get("nlc_token") || null : null,
  lang: "en",

  setAuth: (token, user) => {
    Cookies.set("nlc_token", token, { expires: 1 });
    set({ token, user, lang: (user.preferred_lang as "en" | "bn") || "en" });
  },

  setLang: (lang) => set({ lang }),

  logout: () => {
    Cookies.remove("nlc_token");
    set({ token: null, user: null });
    window.location.href = "/auth/login";
  },

  isAdmin: () => {
    const { user } = get();
    return user?.role === "admin" || user?.role === "superadmin";
  },
}));
