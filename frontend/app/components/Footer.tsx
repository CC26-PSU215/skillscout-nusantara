import { Search, Heart } from "lucide-react";
import Link from "next/link";

export default function Footer() {
  return (
    <footer
      style={{
        borderTop: "1px solid var(--glass-border)",
        background: "var(--bg-secondary)",
        padding: "48px 0 24px",
        marginTop: "auto",
      }}
    >
      <div
        className="page-container"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 40,
          marginBottom: 40,
        }}
      >
        {/* Brand */}
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              marginBottom: 16,
            }}
          >
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: 32,
                height: 32,
                borderRadius: "var(--radius-sm)",
                background: "var(--gradient-primary)",
              }}
            >
              <Search size={16} color="#fff" />
            </span>
            <span style={{ fontWeight: 800, fontSize: "1.125rem" }}>
              Skill<span style={{ color: "var(--primary-400)" }}>Scout</span>
            </span>
          </div>
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "0.875rem",
              lineHeight: 1.6,
              maxWidth: 280,
            }}
          >
            Platform pencari kerja berbasis AI untuk masyarakat Indonesia.
            Cocokkan CV Anda dengan lowongan terbaik.
          </p>
        </div>

        {/* Platform */}
        <div>
          <h4
            style={{
              fontWeight: 600,
              fontSize: "0.875rem",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              color: "var(--text-secondary)",
              marginBottom: 16,
            }}
          >
            Platform
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <Link
              href="/upload"
              style={{
                color: "var(--text-muted)",
                fontSize: "0.875rem",
                transition: "var(--transition-fast)",
              }}
            >
              Upload CV
            </Link>
            <Link
              href="/jobs"
              style={{
                color: "var(--text-muted)",
                fontSize: "0.875rem",
                transition: "var(--transition-fast)",
              }}
            >
              Lowongan Kerja
            </Link>
            <Link
              href="/trends"
              style={{
                color: "var(--text-muted)",
                fontSize: "0.875rem",
                transition: "var(--transition-fast)",
              }}
            >
              Tren Skill
            </Link>
          </div>
        </div>

        {/* Tech */}
        <div>
          <h4
            style={{
              fontWeight: 600,
              fontSize: "0.875rem",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              color: "var(--text-secondary)",
              marginBottom: 16,
            }}
          >
            Teknologi
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <span style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
              Next.js + React
            </span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
              FastAPI + PostgreSQL
            </span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
              TensorFlow (Siamese BiLSTM)
            </span>
          </div>
        </div>

        {/* Tim */}
        <div>
          <h4
            style={{
              fontWeight: 600,
              fontSize: "0.875rem",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              color: "var(--text-secondary)",
              marginBottom: 16,
            }}
          >
            Tim CC26-PSU215
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <span style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
              Full-Stack: Orellius & Bagus
            </span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
              AI: Jennifer & Velicia
            </span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
              Data: Fikran & Albi
            </span>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div
        className="page-container"
        style={{
          borderTop: "1px solid var(--border-color)",
          paddingTop: 24,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "0.8125rem",
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          © 2026 SkillScout Nusantara. Dibuat dengan{" "}
          <Heart size={12} style={{ color: "var(--error-500)" }} /> oleh Tim
          CC26-PSU215
        </p>
      </div>
    </footer>
  );
}
