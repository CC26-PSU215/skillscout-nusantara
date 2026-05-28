"use client";
import { useState, useEffect } from "react";
import { TrendingUp, Loader2, ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";
import { getTrends } from "@/app/lib/api";
import type { TrendItem } from "@/app/types/api";

export default function TrendsPage() {
  const [trends, setTrends] = useState<TrendItem[]>([]);
  const [period, setPeriod] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getTrends();
        setTrends(data.trends);
        setPeriod(data.period);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Gagal memuat tren.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <section className="page-container" style={{ padding: "60px 0 80px" }}>
      <div style={{ textAlign: "center", marginBottom: 48 }}>
        <div style={{ width: 64, height: 64, borderRadius: "var(--radius-lg)", background: "rgba(6,182,212,0.12)", display: "inline-flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
          <TrendingUp size={32} style={{ color: "var(--accent-400)" }} />
        </div>
        <h1 className="section-title" style={{ marginBottom: 12 }}>Tren Skill</h1>
        <p className="section-subtitle" style={{ margin: "0 auto" }}>
          Prediksi demand skill berdasarkan analisis pasar kerja Indonesia
          {period && <span style={{ display: "block", marginTop: 8, fontSize: "0.875rem", color: "var(--text-muted)" }}>Periode: {period}</span>}
        </p>
      </div>

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 80 }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent-400)" }} />
        </div>
      ) : error ? (
        <div style={{ textAlign: "center", padding: 60 }}>
          <p style={{ color: "var(--error-500)", marginBottom: 8 }}>{error}</p>
          <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>ML Service mungkin belum aktif.</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 20 }}>
          {trends.map((t) => {
            const isUp = t.growth_pct > 0;
            const isFlat = t.growth_pct === 0;
            const GrowthIcon = isUp ? ArrowUpRight : isFlat ? Minus : ArrowDownRight;
            const growthColor = isUp ? "#4ade80" : isFlat ? "var(--text-muted)" : "#f87171";
            const currentPct = Math.round(t.current_demand * 100);
            const predictedPct = Math.round(t.predicted_demand * 100);

            return (
              <div key={t.skill} className="glass-card" style={{ padding: 24 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
                  <h3 style={{ fontWeight: 700, fontSize: "1.125rem", textTransform: "capitalize" }}>{t.skill}</h3>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: 4, padding: "4px 10px", borderRadius: 9999, fontSize: "0.75rem", fontWeight: 600, color: growthColor, background: isUp ? "rgba(34,197,94,0.1)" : isFlat ? "rgba(100,116,139,0.1)" : "rgba(239,68,68,0.1)" }}>
                    <GrowthIcon size={14} />
                    {t.growth_pct > 0 ? "+" : ""}{t.growth_pct.toFixed(1)}%
                  </span>
                </div>

                {/* Bar comparison */}
                <div style={{ marginBottom: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 6 }}>
                    <span>Demand Saat Ini</span>
                    <span>{currentPct}%</span>
                  </div>
                  <div style={{ height: 8, borderRadius: 4, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
                    <div style={{ height: "100%", borderRadius: 4, width: `${currentPct}%`, background: "var(--primary-500)", transition: "width 0.8s ease" }} />
                  </div>
                </div>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 6 }}>
                    <span>Prediksi</span>
                    <span>{predictedPct}%</span>
                  </div>
                  <div style={{ height: 8, borderRadius: 4, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
                    <div style={{ height: "100%", borderRadius: 4, width: `${predictedPct}%`, background: "var(--accent-500)", transition: "width 0.8s ease" }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Info note */}
      <div className="glass-card" style={{ padding: 20, marginTop: 40, textAlign: "center" }}>
        <p style={{ color: "var(--text-muted)", fontSize: "0.8125rem" }}>
          Data tren dihasilkan oleh ML Service menggunakan analisis time-series terhadap pasar kerja Indonesia.
        </p>
      </div>
    </section>
  );
}
