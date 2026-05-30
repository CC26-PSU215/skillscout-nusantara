/**
 * TypeScript interfaces — harus match dengan backend/app/models/schemas.py
 */

// ── Jobs ─────────────────────────────────────────────────────

export interface JobResponse {
  id: string;
  title: string;
  company: string;
  description: string;
  skills: string[];
  location: string | null;
  source_url: string | null;
  scraped_at: string;
}

export interface JobListResponse {
  total: number;
  page: number;
  per_page: number;
  data: JobResponse[];
}

// ── CV Upload ────────────────────────────────────────────────

export interface CVUploadResponse {
  id: string;
  filename: string;
  storage_path: string;
  skills: string[];
  uploaded_at: string;
}

// ── Matching ─────────────────────────────────────────────────

export interface MatchResultItem {
  job_id: string;
  title: string;
  company: string;
  score: number;
  matched_skills: string[];
  gap_skills: string[];
}

export interface MatchResponse {
  cv_id: string;
  results: MatchResultItem[];
}

// ── Trends ───────────────────────────────────────────────────

export interface TrendItem {
  skill: string;
  current_demand: number;
  predicted_demand: number;
  growth_pct: number;
}

export interface TrendResponse {
  period: string;
  trends: TrendItem[];
}
