"use client";
import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileText, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { uploadCV } from "@/app/lib/api";

export default function CVUploadForm() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  // ── Throttle: prevent double-click on upload ──────────────
  // Tombol upload hanya bisa diklik 1x. Setelah diklik,
  // tidak bisa diklik lagi sampai proses selesai.
  const isSubmitting = useRef(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const f = e.dataTransfer.files?.[0];
    if (f?.type === "application/pdf") { setFile(f); setStatus("idle"); setMessage(""); }
    else { setStatus("error"); setMessage("Hanya file PDF yang diizinkan."); }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) { setFile(f); setStatus("idle"); setMessage(""); }
  };

  const handleSubmit = async () => {
    // ── Throttle guard: cegah double-click ──
    // Jika sudah dalam proses upload, abaikan klik berikutnya.
    if (!file || isSubmitting.current) return;
    isSubmitting.current = true;

    setUploading(true);
    setStatus("idle");
    setMessage("");
    try {
      const cv = await uploadCV(file);
      setStatus("success");
      setMessage(`CV "${cv.filename}" berhasil diupload! Ditemukan ${cv.skills.length} skill. Mengarahkan ke halaman matching...`);
      // Auto redirect to matching page (match will be triggered on that page)
      setTimeout(() => router.push(`/match/${cv.id}`), 1000);
    } catch (err: unknown) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Upload gagal.");
      // Reset throttle saat error agar user bisa coba lagi
      isSubmitting.current = false;
    } finally {
      setUploading(false);
      // Jangan reset isSubmitting saat sukses (akan redirect)
      // Reset saat error sudah dilakukan di catch
    }
  };

  return (
    <div style={{ maxWidth: 560, margin: "0 auto" }}>
      {/* Dropzone */}
      <div
        onDragEnter={handleDrag} onDragOver={handleDrag}
        onDragLeave={handleDrag} onDrop={handleDrop}
        onClick={() => document.getElementById("cv-input")?.click()}
        className="glass-card"
        style={{
          padding: 48, textAlign: "center", cursor: "pointer",
          borderStyle: "dashed",
          borderColor: dragActive ? "var(--primary-400)" : file ? "var(--success-500)" : "var(--border-glow)",
          borderWidth: 2,
          background: dragActive ? "rgba(99,102,241,0.08)" : "var(--glass-bg)",
          transition: "var(--transition-base)",
        }}
      >
        <input id="cv-input" type="file" accept=".pdf" hidden onChange={handleFileChange} />
        <div style={{ marginBottom: 16 }}>
          {file ? (
            <FileText size={48} style={{ color: "var(--success-500)", margin: "0 auto" }} />
          ) : (
            <Upload size={48} style={{ color: dragActive ? "var(--primary-400)" : "var(--text-muted)", margin: "0 auto" }} />
          )}
        </div>
        {file ? (
          <>
            <p style={{ fontWeight: 600, fontSize: "1rem", marginBottom: 4 }}>{file.name}</p>
            <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>{(file.size / 1024 / 1024).toFixed(2)} MB — Klik untuk ganti</p>
          </>
        ) : (
          <>
            <p style={{ fontWeight: 600, fontSize: "1rem", marginBottom: 4 }}>
              {dragActive ? "Lepaskan file di sini" : "Drag & Drop CV Anda di sini"}
            </p>
            <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>atau klik untuk memilih file (PDF, maks 5 MB)</p>
          </>
        )}
      </div>

      {/* Submit — disabled saat uploading (throttle visual) */}
      <button
        className="btn btn-primary btn-lg"
        style={{ width: "100%", marginTop: 20 }}
        onClick={handleSubmit}
        disabled={!file || uploading}
      >
        {uploading ? <><Loader2 size={18} className="animate-spin" /> Menganalisis CV...</> : <>Upload & Cocokkan</>}
      </button>

      {/* Status message */}
      {message && (
        <div style={{
          marginTop: 16, padding: "12px 16px", borderRadius: "var(--radius-md)",
          display: "flex", alignItems: "center", gap: 8,
          fontSize: "0.875rem", fontWeight: 500,
          background: status === "success" ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.1)",
          color: status === "success" ? "#4ade80" : "#f87171",
          border: `1px solid ${status === "success" ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.2)"}`,
        }}>
          {status === "success" ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          {message}
        </div>
      )}
    </div>
  );
}
