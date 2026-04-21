import type { Metadata } from "next";
import { Playfair_Display, DM_Sans } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "NLC Land Evidence | Neum Lex Counsel",
  description: "AI-Powered Land & Real Estate Evidence Analysis — Bangladesh",
  icons: { icon: "/favicon.ico" },
  openGraph: {
    title: "NLC Land Evidence Analysis",
    description: "Forensic AI analysis of Bangladesh property documents",
    siteName: "Neum Lex Counsel",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${playfair.variable} ${dmSans.variable}`}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
      </head>
      <body className="font-body bg-cream text-navy antialiased">
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "#1a2744",
              color: "#fff",
              border: "1px solid rgba(201,168,76,0.3)",
              borderRadius: "8px",
              fontFamily: "var(--font-body)",
              fontSize: "14px",
            },
            success: { iconTheme: { primary: "#c9a84c", secondary: "#fff" } },
          }}
        />
        {children}
      </body>
    </html>
  );
}
