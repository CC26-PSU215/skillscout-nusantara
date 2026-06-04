"use client";
import { useState, useEffect } from "react";
import { Search, Briefcase, Loader2, ChevronLeft, ChevronRight } from "lucide-react";
import JobCard from "@/app/components/JobCard";
import { getJobs } from "@/app/lib/api";
import { useDebounce } from "@/app/lib/hooks";
import type { JobResponse } from "@/app/types/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const perPage = 12;

  // ── Debounce search ────────────────────────────────────────
  // Menunda request API 500ms setelah user berhenti mengetik.
  // Analoginya seperti pintu lift yang baru menutup jika
  // tidak ada orang lewat selama beberapa detik.
  const debouncedSearch = useDebounce(search, 500);

  // Reset page ketika debounced search berubah
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch]);

  // Fetch jobs ketika page atau debouncedSearch berubah
  // AbortController membatalkan request HTTP yang masih in-flight
  // saat user mengetik karakter baru (debounce berubah).
  useEffect(() => {
    const controller = new AbortController();

    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await getJobs({
          page,
          per_page: perPage,
          search: debouncedSearch || undefined,
          signal: controller.signal,
        });
        setJobs(data.data);
        setTotal(data.total);
      } catch (err: unknown) {
        // Abaikan error dari request yang di-cancel
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Gagal memuat lowongan.");
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };
    load();

    // Cleanup: batalkan request HTTP yang masih berjalan
    return () => {
      controller.abort();
    };
  }, [page, debouncedSearch]);

  const totalPages = Math.ceil(total / perPage);

  return (
    <section className="page-container" style={{ padding: "60px 0 80px" }}>
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <h1 className="section-title" style={{ marginBottom: 12 }}>
          <Briefcase size={28} style={{ display: "inline", verticalAlign: "middle", marginRight: 8 }} />
          Lowongan Kerja
        </h1>
        <p className="section-subtitle" style={{ margin: "0 auto" }}>
          Jelajahi {total > 0 ? total : ""} lowongan kerja dari berbagai sumber
        </p>
      </div>

      {/* Search bar with debounce info */}
      <div style={{ maxWidth: 480, margin: "0 auto 32px", position: "relative" }}>
        <Search size={18} style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
        <input
          className="input"
          style={{ paddingLeft: 40 }}
          placeholder="Cari judul atau perusahaan..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        {/* Visual indicator saat mengetik (belum di-fetch) */}
        {search !== debouncedSearch && search.length > 0 && (
          <div style={{
            position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
            display: "flex", alignItems: "center", gap: 6,
            fontSize: "0.75rem", color: "var(--text-muted)",
          }}>
            <Loader2 size={12} className="animate-spin" />
          </div>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 80 }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--primary-400)" }} />
        </div>
      ) : error ? (
        <div style={{ textAlign: "center", padding: 60 }}>
          <p style={{ color: "var(--error-500)", fontSize: "1rem", marginBottom: 8 }}>{error}</p>
          <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Pastikan backend berjalan.</p>
        </div>
      ) : jobs.length === 0 ? (
        <div style={{ textAlign: "center", padding: 60 }}>
          <Briefcase size={48} style={{ color: "var(--text-muted)", marginBottom: 12 }} />
          <p style={{ color: "var(--text-secondary)" }}>Tidak ada lowongan ditemukan.</p>
        </div>
      ) : (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 20 }}>
            {jobs.map(j => <JobCard key={j.id} job={j} />)}
          </div>
          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 16, marginTop: 40 }}>
              <button className="btn btn-ghost btn-sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}>
                <ChevronLeft size={16} /> Sebelumnya
              </button>
              <span style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>
                Hal {page} dari {totalPages}
              </span>
              <button className="btn btn-ghost btn-sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
                Berikutnya <ChevronRight size={16} />
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
