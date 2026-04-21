import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://nlc-land-docs-api.onrender.com";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = Cookies.get("nlc_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      Cookies.remove("nlc_token");
      window.location.href = "/auth/login";
    }
    return Promise.reject(err);
  }
);

// ── Auth ─────────────────────────────────────────────────
export const authApi = {
  register: (data: any) => api.post("/auth/register", data),
  login: (data: any) => api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
};

// ── Cases ─────────────────────────────────────────────────
export const casesApi = {
  create: (data: any) => api.post("/cases/", data),
  list: () => api.get("/cases/"),
  get: (id: string) => api.get(`/cases/${id}`),
};

// ── Documents ─────────────────────────────────────────────
export const docsApi = {
  upload: (formData: FormData) => api.post("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  }),
  list: (caseId: string) => api.get(`/documents/case/${caseId}`),
};

// ── Payments ──────────────────────────────────────────────
export const paymentsApi = {
  plans: () => api.get("/payments/plans"),
  initiate: (data: any) => api.post("/payments/initiate", data),
  uploadProof: (formData: FormData) => api.post("/payments/upload-proof", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }),
  adminPending: () => api.get("/payments/admin/pending"),
  adminConfirm: (data: any) => api.post("/payments/admin/confirm", data),
};

// ── Reports ───────────────────────────────────────────────
export const reportsApi = {
  list: (caseId: string) => api.get(`/reports/case/${caseId}`),
  download: (reportId: string) => api.get(`/reports/download/${reportId}`, { responseType: "blob" }),
};

// ── Admin ─────────────────────────────────────────────────
export const adminApi = {
  stats: () => api.get("/admin/stats"),
  users: () => api.get("/admin/users"),
  toggleUser: (id: string) => api.patch(`/admin/users/${id}/toggle`),
  cases: (status?: string) => api.get("/admin/cases", { params: { status } }),
  rerunAnalysis: (id: string) => api.post(`/admin/cases/${id}/rerun`),
  payments: () => api.get("/admin/payments"),
};
