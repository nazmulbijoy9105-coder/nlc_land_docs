import Navbar from "@/components/layout/Navbar";

export default function CaseLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-cream">
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {children}
      </main>
    </div>
  );
}
