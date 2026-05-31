/**
 * API Client — komunikasi frontend ↔ backend (FastAPI).
 * Selalu menggunakan relative path ("") agar request dikirim ke same-origin.
 * Next.js rewrites di next.config.ts mem-proxy /api/* ke backend.
 * Ini menghindari masalah CORS sepenuhnya.
 */

const API_BASE = "";

/** Custom error class with HTTP status */
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

/** Generic GET request (with optional AbortSignal for cancellation) */
export async function apiGet<T>(
  endpoint: string,
  signal?: AbortSignal
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    cache: "no-store",
    signal,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail || `API Error ${res.status}`);
  }
  return res.json();
}

/** Generic POST (JSON body) */
export async function apiPost<T>(
  endpoint: string,
  body?: unknown
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new ApiError(res.status, data.detail || `API Error ${res.status}`);
  }
  return res.json();
}

/** Upload file via FormData */
export async function apiUpload<T>(
  endpoint: string,
  file: File
): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new ApiError(res.status, data.detail || `Upload Error ${res.status}`);
  }
  return res.json();
}

/**
 * Convenience wrappers — endpoints sesuai dengan backend routers.
 */
import type {
  JobListResponse,
  JobResponse,
  CVUploadResponse,
  MatchResponse,
  TrendResponse,
} from "@/app/types/api";

/** List lowongan (paginated + filter, supports cancellation) */
export function getJobs(params?: {
  page?: number;
  per_page?: number;
  location?: string;
  skill?: string;
  search?: string;
  signal?: AbortSignal;
}): Promise<JobListResponse> {
  const q = new URLSearchParams();
  if (params?.page) q.set("page", String(params.page));
  if (params?.per_page) q.set("per_page", String(params.per_page));
  if (params?.location) q.set("location", params.location);
  if (params?.skill) q.set("skill", params.skill);
  if (params?.search) q.set("search", params.search);
  const qs = q.toString();
  return apiGet<JobListResponse>(`/api/jobs${qs ? `?${qs}` : ""}`, params?.signal);
}

/** Detail satu lowongan */
export function getJob(id: string): Promise<JobResponse> {
  return apiGet<JobResponse>(`/api/jobs/${id}`);
}

/** Upload CV (PDF) */
export function uploadCV(file: File): Promise<CVUploadResponse> {
  return apiUpload<CVUploadResponse>("/api/cv/upload", file);
}

/** Detail CV */
export function getCV(id: string): Promise<CVUploadResponse> {
  return apiGet<CVUploadResponse>(`/api/cv/${id}`);
}

/** Match CV ke semua lowongan */
export function matchCV(
  cvId: string,
  topK: number = 10
): Promise<MatchResponse> {
  return apiPost<MatchResponse>("/api/match", {
    cv_id: cvId,
    top_k: topK,
  });
}

/** Prediksi tren skill */
export function getTrends(): Promise<TrendResponse> {
  return apiGet<TrendResponse>("/api/match/trends");
}

/** Health check */
export function healthCheck(): Promise<{ status: string; service: string }> {
  return apiGet("/api/health");
}
