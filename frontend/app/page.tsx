import Link from "next/link";
import { Upload, Briefcase, Brain, Zap, Shield, ArrowRight, Sparkles, Target } from "lucide-react";

export default function HomePage() {
  return (
    <>
      {/* ── HERO ──────────────────────────────────────────── */}
      <section style={{ position: "relative", overflow: "hidden", padding: "100px 0 80px" }}>
        {/* Decorative orbs */}
        <div className="hero-orb" style={{ width: 500, height: 500, top: -100, right: -200, background: "var(--primary-600)" }} />
        <div className="hero-orb" style={{ width: 400, height: 400, bottom: -150, left: -100, background: "var(--accent-500)" }} />

        <div className="page-container" style={{ position: "relative", zIndex: 1, textAlign: "center" }}>
          {/* Announcement badge */}
          <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 16px", borderRadius: 9999, background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.2)", marginBottom: 32, fontSize: "0.8125rem", color: "var(--primary-300)" }}>
            <Sparkles size={14} />
            Powered by Siamese BiLSTM Deep Learning
          </div>

          <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", fontWeight: 900, lineHeight: 1.1, marginBottom: 24, maxWidth: 800, margin: "0 auto 24px" }}>
            Temukan <span style={{ background: "var(--gradient-primary)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>Pekerjaan Impian</span> Anda dengan AI
          </h1>
          <p style={{ fontSize: "1.125rem", color: "var(--text-secondary)", maxWidth: 600, margin: "0 auto 40px", lineHeight: 1.7 }}>
            Upload CV Anda dan biarkan AI kami mencocokkan skill Anda dengan lowongan kerja terbaik di Indonesia. Dapatkan analisis skill gap dan rekomendasi karir.
          </p>

          <div style={{ display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}>
            <Link href="/upload" className="btn btn-primary btn-lg">
              <Upload size={18} /> Upload CV Sekarang
            </Link>
            <Link href="/jobs" className="btn btn-secondary btn-lg">
              Lihat Lowongan <ArrowRight size={18} />
            </Link>
          </div>

          {/* Stats row */}
          <div style={{ display: "flex", gap: 48, justifyContent: "center", marginTop: 64, flexWrap: "wrap" }}>
            {[
              { num: "800+", label: "Lowongan" },
              { num: "505", label: "CV Dianalisis" },
              { num: "AI", label: "Siamese BiLSTM" },
            ].map(s => (
              <div key={s.label} style={{ textAlign: "center" }}>
                <div style={{ fontSize: "2rem", fontWeight: 800, background: "var(--gradient-primary)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>{s.num}</div>
                <div style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="divider" />

      {/* ── HOW IT WORKS ──────────────────────────────────── */}
      <section className="page-container" style={{ padding: "60px 0" }}>
        <div style={{ textAlign: "center", marginBottom: 48 }}>
          <h2 className="section-title" style={{ marginBottom: 12 }}>Cara Kerja</h2>
          <p className="section-subtitle" style={{ margin: "0 auto" }}>Tiga langkah sederhana untuk menemukan pekerjaan yang sesuai</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 24 }}>
          {[
            { icon: Upload, step: "01", title: "Upload CV", desc: "Upload CV dalam format PDF. AI kami akan mengekstrak skill secara otomatis menggunakan NLP bilingual." },
            { icon: Brain, step: "02", title: "Analisis AI", desc: "Model Siamese BiLSTM membandingkan profil Anda dengan semua lowongan menggunakan deep learning." },
            { icon: Target, step: "03", title: "Hasil & Rekomendasi", desc: "Lihat skor kecocokan, skill yang match, dan skill gap yang perlu dipelajari." },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.step} className="glass-card" style={{ padding: 32, position: "relative" }}>
                <div style={{ position: "absolute", top: 16, right: 20, fontSize: "3rem", fontWeight: 900, color: "rgba(99,102,241,0.08)" }}>{item.step}</div>
                <div style={{ width: 48, height: 48, borderRadius: "var(--radius-md)", background: "rgba(99,102,241,0.12)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
                  <Icon size={24} style={{ color: "var(--primary-400)" }} />
                </div>
                <h3 style={{ fontWeight: 700, fontSize: "1.125rem", marginBottom: 8 }}>{item.title}</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.9375rem", lineHeight: 1.6 }}>{item.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      <div className="divider" />

      {/* ── FEATURES ──────────────────────────────────────── */}
      <section className="page-container" style={{ padding: "60px 0" }}>
        <div style={{ textAlign: "center", marginBottom: 48 }}>
          <h2 className="section-title" style={{ marginBottom: 12 }}>Fitur Utama</h2>
          <p className="section-subtitle" style={{ margin: "0 auto" }}>Dibangun dengan teknologi terdepan untuk pasar kerja Indonesia</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20 }}>
          {[
            { icon: Brain, title: "Deep Learning", desc: "Siamese BiLSTM TensorFlow" },
            { icon: Zap, title: "CV Parser", desc: "Ekstraksi skill bilingual" },
            { icon: Shield, title: "Fallback Cerdas", desc: "TF-IDF jika ML offline" },
            { icon: Briefcase, title: "800+ Lowongan", desc: "Data dari Glints & lainnya" },
            { icon: Sparkles, title: "Skill Gap", desc: "Rekomendasi skill belajar" },
          ].map((f) => {
            const Icon = f.icon;
            return (
              <div key={f.title} className="glass-card" style={{ padding: 24, textAlign: "center" }}>
                <Icon size={28} style={{ color: "var(--primary-400)", marginBottom: 12 }} />
                <h4 style={{ fontWeight: 700, fontSize: "0.9375rem", marginBottom: 4 }}>{f.title}</h4>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8125rem" }}>{f.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      <div className="divider" />

      {/* ── CTA ────────────────────────────────────────────── */}
      <section style={{ padding: "80px 0", textAlign: "center", position: "relative", overflow: "hidden" }}>
        <div className="hero-orb" style={{ width: 300, height: 300, top: 0, left: "50%", transform: "translateX(-50%)", background: "var(--primary-600)" }} />
        <div className="page-container" style={{ position: "relative", zIndex: 1 }}>
          <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: 16 }}>Siap Menemukan Karir Impian?</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: 32, maxWidth: 480, margin: "0 auto 32px" }}>Upload CV Anda sekarang dan temukan lowongan yang paling cocok.</p>
          <Link href="/upload" className="btn btn-primary btn-lg">
            <Upload size={18} /> Mulai Sekarang
          </Link>
        </div>
      </section>
    </>
  );
}
