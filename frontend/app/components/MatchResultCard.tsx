import { CheckCircle, AlertTriangle } from "lucide-react";
import SkillBadge from "./SkillBadge";
import type { MatchResultItem } from "@/app/types/api";

interface Props {
  result: MatchResultItem;
  rank: number;
}

export default function MatchResultCard({ result, rank }: Props) {
  const pct = Math.round(result.score * 100);
  let color = "#ef4444";
  if (pct >= 70) color = "#22c55e";
  else if (pct >= 40) color = "#f59e0b";

  const r = 36, circ = 2 * Math.PI * r;
  const offset = circ - (result.score * circ);

  return (
    <div className="glass-card" style={{ padding: 24, display: "flex", gap: 24, alignItems: "flex-start" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, flexShrink: 0 }}>
        <div style={{ width: 36, height: 36, borderRadius: "50%", background: rank <= 3 ? "var(--gradient-primary)" : "rgba(99,102,241,0.15)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: "0.875rem", color: rank <= 3 ? "#fff" : "var(--primary-300)" }}>
          #{rank}
        </div>
        <div className="score-ring">
          <svg width={88} height={88}>
            <circle cx={44} cy={44} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={5} />
            <circle cx={44} cy={44} r={r} fill="none" stroke={color} strokeWidth={5} strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset} style={{ transition: "stroke-dashoffset 1s ease" }} />
          </svg>
          <span className="score-value" style={{ color, fontSize: "1rem" }}>{pct}%</span>
        </div>
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <h3 style={{ fontWeight: 700, fontSize: "1.125rem", marginBottom: 4 }}>{result.title}</h3>
        <p style={{ fontWeight: 500, fontSize: "0.9375rem", color: "var(--primary-300)", marginBottom: 16 }}>{result.company}</p>
        {result.matched_skills.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, fontSize: "0.8125rem", fontWeight: 600, color: "#4ade80" }}>
              <CheckCircle size={14} /> Skill Cocok ({result.matched_skills.length})
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {result.matched_skills.map(s => <SkillBadge key={s} skill={s} variant="success" size="sm" />)}
            </div>
          </div>
        )}
        {result.gap_skills.length > 0 && (
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, fontSize: "0.8125rem", fontWeight: 600, color: "#fbbf24" }}>
              <AlertTriangle size={14} /> Perlu Dipelajari ({result.gap_skills.length})
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {result.gap_skills.map(s => <SkillBadge key={s} skill={s} variant="warning" size="sm" />)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
