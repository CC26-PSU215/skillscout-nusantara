"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { Loader2, ArrowLeft, FileText, Upload } from "lucide-react";
import Link from "next/link";
import MatchResultCard from "@/app/components/MatchResultCard";
import SkillBadge from "@/app/components/SkillBadge";
import { getCV, matchCV } from "@/app/lib/api";
import type { CVUploadResponse, MatchResultItem } from "@/app/types/api";

export default function MatchPage() {
  const params = useParams();
  const cvId = params.cvId as string;

  const [cv, setCv] = useState<CVUploadResponse | null>(null);
  const [results, setResults] = useState<MatchResultItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const [cvData, matchData] = await Promise.all([
          getCV(cvId),
          matchCV(cvId, 10),
        ]);
        setCv(cvData);
        setResults(matchData.results);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Gagal memuat hasil.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [cvId]);

  if (loading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 120, gap: 16 }}>
        <Loader2 size={40} className="animate-spin" style={{ color: "var(--primary-400)" }} />
        <p style={{ color: "var(--text-secondary)" }}>Menganalisis kecocokan...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container" style={{ padding: "80px 0", textAlign: "center" }}>
        <p style={{ color: "var(--error-500)", fontSize: "1.125rem", marginBottom: 16 }}>{error}</p>
        <Link href="/upload" className="btn btn-primary">
          <Upload size={16} /> Upload CV Baru
        </Link>
      </div>
    );
  }

  return (
    <section className="page-container" style={{ padding: "40px 0 80px" }}>
      {/* Back */}
      <Link href="/upload" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "var(--text-muted)", fontSize: "0.875rem", marginBottom: 24, transition: "var(--transition-fast)" }}>
        <ArrowLeft size={16} /> Upload CV lain
      </Link>

      {/* CV Info */}
      {cv && (
        <div className="glass-card" style={{ padding: 24, marginBottom: 32 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
            <div style={{ width: 48, height: 48, borderRadius: "var(--radius-md)", background: "rgba(99,102,241,0.12)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <FileText size={24} style={{ color: "var(--primary-400)" }} />
            </div>
            <div style={{ flex: 1 }}>
              <h2 style={{ fontWeight: 700, fontSize: "1.25rem", marginBottom: 4 }}>{cv.filename}</h2>
              <p style={{ color: "var(--text-muted)", fontSize: "0.8125rem" }}>
                {cv.skills.length} skill terdeteksi • Diupload {new Date(cv.uploaded_at).toLocaleDateString("id-ID")}
              </p>
            </div>
          </div>
          {cv.skills.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 16 }}>
              {cv.skills.map(s => <SkillBadge key={s} skill={s} />)}
            </div>
          )}
        </div>
      )}

      {/* Results header */}
      <h2 style={{ fontWeight: 800, fontSize: "1.5rem", marginBottom: 8 }}>
        Hasil Pencocokan
      </h2>
      <p style={{ color: "var(--text-secondary)", fontSize: "0.9375rem", marginBottom: 32 }}>
        Ditemukan {results.length} lowongan yang cocok, diurutkan berdasarkan skor kecocokan.
      </p>

      {/* Result cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {results.map((r, i) => (
          <MatchResultCard key={r.job_id} result={r} rank={i + 1} />
        ))}
      </div>

      {results.length === 0 && (
        <div style={{ textAlign: "center", padding: 60 }}>
          <p style={{ color: "var(--text-muted)" }}>Tidak ada hasil pencocokan.</p>
        </div>
      )}
    </section>
  );
}
