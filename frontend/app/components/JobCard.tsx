import { MapPin, Calendar, ExternalLink } from "lucide-react";
import SkillBadge from "./SkillBadge";
import type { JobResponse } from "@/app/types/api";

interface JobCardProps {
  job: JobResponse;
}

export default function JobCard({ job }: JobCardProps) {
  const dateStr = new Date(job.scraped_at).toLocaleDateString("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <div
      className="glass-card"
      style={{
        padding: 24,
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      {/* Header */}
      <div>
        <h3
          style={{
            fontWeight: 700,
            fontSize: "1.125rem",
            color: "var(--text-primary)",
            marginBottom: 4,
            lineHeight: 1.3,
          }}
        >
          {job.title}
        </h3>
        <p
          style={{
            fontWeight: 500,
            fontSize: "0.9375rem",
            color: "var(--primary-300)",
          }}
        >
          {job.company}
        </p>
      </div>

      {/* Meta */}
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        {job.location && (
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 4,
              fontSize: "0.8125rem",
              color: "var(--text-muted)",
            }}
          >
            <MapPin size={14} />
            {job.location}
          </span>
        )}
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            fontSize: "0.8125rem",
            color: "var(--text-muted)",
          }}
        >
          <Calendar size={14} />
          {dateStr}
        </span>
      </div>

      {/* Description (truncated) */}
      <p
        style={{
          fontSize: "0.875rem",
          color: "var(--text-secondary)",
          lineHeight: 1.6,
          display: "-webkit-box",
          WebkitLineClamp: 3,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
        }}
      >
        {job.description}
      </p>

      {/* Skills */}
      {job.skills.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {job.skills.slice(0, 6).map((s) => (
            <SkillBadge key={s} skill={s} size="sm" />
          ))}
          {job.skills.length > 6 && (
            <span
              style={{
                fontSize: "0.75rem",
                color: "var(--text-muted)",
                padding: "3px 8px",
              }}
            >
              +{job.skills.length - 6} lainnya
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginTop: "auto",
          paddingTop: 12,
          borderTop: "1px solid var(--border-color)",
        }}
      >
        {job.source_url && (
          <a
            href={job.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-ghost btn-sm"
            style={{ gap: 4, fontSize: "0.8125rem" }}
          >
            <ExternalLink size={14} />
            Sumber
          </a>
        )}
      </div>
    </div>
  );
}
