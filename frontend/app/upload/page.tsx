import { FileSearch } from "lucide-react";
import CVUploadForm from "@/app/components/CVUploadForm";

export const metadata = {
  title: "Upload CV — SkillScout Nusantara",
  description: "Upload CV PDF Anda untuk dianalisis oleh AI dan dicocokkan dengan lowongan kerja terbaik.",
};

export default function UploadPage() {
  return (
    <section className="page-container" style={{ padding: "60px 0 80px" }}>
      <div style={{ textAlign: "center", marginBottom: 48 }}>
        <div style={{ width: 64, height: 64, borderRadius: "var(--radius-lg)", background: "rgba(99,102,241,0.12)", display: "inline-flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
          <FileSearch size={32} style={{ color: "var(--primary-400)" }} />
        </div>
        <h1 className="section-title" style={{ marginBottom: 12 }}>Upload CV Anda</h1>
        <p className="section-subtitle" style={{ margin: "0 auto" }}>
          Upload CV dalam format PDF. AI kami akan mengekstrak skill dan mencocokkan dengan lowongan yang tersedia.
        </p>
      </div>
      <CVUploadForm />

      {/* Info cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginTop: 48, maxWidth: 560, margin: "48px auto 0" }}>
        {[
          { title: "Format PDF", desc: "Hanya file .pdf yang diterima" },
          { title: "Maks 5 MB", desc: "Pastikan ukuran di bawah 5 MB" },
          { title: "Bilingual", desc: "Mendukung CV bahasa Indonesia & Inggris" },
        ].map(i => (
          <div key={i.title} className="glass-card" style={{ padding: 16, textAlign: "center" }}>
            <p style={{ fontWeight: 600, fontSize: "0.875rem", marginBottom: 4 }}>{i.title}</p>
            <p style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>{i.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
