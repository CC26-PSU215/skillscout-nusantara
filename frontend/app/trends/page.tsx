"use client";
import { Construction } from "lucide-react";
import Link from "next/link";

export default function TrendsPage() {
  return (
    <section className="page-container" style={{ padding: "120px 0 80px", textAlign: "center" }}>
      <div style={{ width: 80, height: 80, borderRadius: "var(--radius-lg)", background: "rgba(99,102,241,0.12)", display: "inline-flex", alignItems: "center", justifyContent: "center", marginBottom: 24 }}>
        <Construction size={40} style={{ color: "var(--primary-400)" }} />
      </div>
      <h1 className="section-title" style={{ marginBottom: 12 }}>Segera Hadir</h1>
      <p className="section-subtitle" style={{ margin: "0 auto 32px", maxWidth: 480 }}>
        Fitur Tren Skill sedang dalam pengembangan. Nantikan update selanjutnya!
      </p>
      <Link href="/" className="btn btn-primary">
        Kembali ke Beranda
      </Link>
    </section>
  );
}
