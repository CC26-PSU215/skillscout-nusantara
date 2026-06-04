"use client";
import { useState, useEffect } from "react";
import { getJobStats } from "@/app/lib/api";

/**
 * Komponen StatsRow — menampilkan statistik real-time dari database.
 * Digunakan di homepage untuk menggantikan angka hardcoded.
 */
export default function StatsRow() {
  const [totalJobs, setTotalJobs] = useState<number | null>(null);
  const [totalCompanies, setTotalCompanies] = useState<number | null>(null);

  useEffect(() => {
    getJobStats()
      .then((data) => {
        setTotalJobs(data.total_jobs);
        setTotalCompanies(data.total_companies);
      })
      .catch(() => {
        // Fallback jika API belum tersedia
        setTotalJobs(null);
        setTotalCompanies(null);
      });
  }, []);

  const stats = [
    {
      num: totalJobs !== null ? `${totalJobs}+` : "...",
      label: "Lowongan",
    },
    {
      num: totalCompanies !== null ? `${totalCompanies}+` : "...",
      label: "Perusahaan",
    },
    {
      num: "AI",
      label: "Siamese BiLSTM",
    },
  ];

  return (
    <div
      style={{
        display: "flex",
        gap: 48,
        justifyContent: "center",
        marginTop: 64,
        flexWrap: "wrap",
      }}
    >
      {stats.map((s) => (
        <div key={s.label} style={{ textAlign: "center" }}>
          <div
            style={{
              fontSize: "2rem",
              fontWeight: 800,
              background: "var(--gradient-primary)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            {s.num}
          </div>
          <div style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
            {s.label}
          </div>
        </div>
      ))}
    </div>
  );
}
