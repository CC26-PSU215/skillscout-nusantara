# 🏗️ Arsitektur Sistem — SkillScout Nusantara

## Overview

SkillScout Nusantara adalah platform pencari kerja berbasis AI yang mencocokkan CV dengan lowongan kerja menggunakan Deep Learning (Siamese BiLSTM).

---

## Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                        USER (Browser)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP (port 3000)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js 16)                      │
│                                                              │
│  app/                                                        │
│  ├── page.tsx         → Landing Page                         │
│  ├── upload/          → Upload CV (drag & drop)              │
│  ├── jobs/            → Browse lowongan                      │
│  ├── match/[cvId]/    → Hasil matching                       │
│  ├── trends/          → Prediksi tren skill                  │
│  ├── lib/api.ts       → API Client (fetch wrapper)           │
│  ├── types/api.ts     → TypeScript interfaces                │
│  └── components/      → UI components                        │
│                                                              │
│  Tech: React 19, TypeScript, Tailwind CSS 4, Lucide Icons    │
│  Port: 3000                                                  │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP API calls
                          │ NEXT_PUBLIC_API_URL
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                           │
│                                                              │
│  Endpoints:                                                  │
│  ├── GET  /api/health          → Health check                │
│  ├── POST /api/cv/upload       → Upload + parse PDF          │
│  ├── GET  /api/cv/{id}         → Detail CV                   │
│  ├── GET  /api/jobs            → List lowongan (pagination)  │
│  ├── GET  /api/jobs/{id}       → Detail lowongan             │
│  ├── POST /api/jobs            → Tambah lowongan             │
│  ├── POST /api/match           → Match CV ↔ Jobs             │
│  └── GET  /api/match/trends    → Proxy ke ML Service         │
│                                                              │
│  Services:                                                   │
│  ├── cv_parser.py   → pdfplumber + NLP (Sastrawi, NLTK)     │
│  ├── matcher.py     → TF-IDF + Cosine Similarity (fallback) │
│  └── storage.py     → Upload ke Supabase Storage             │
│                                                              │
│  Tech: Python 3.11, SQLAlchemy 2.0, asyncpg, pydantic        │
│  Port: 8000                                                  │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
┌────────────────────────┐  ┌────────────────────────────────┐
│  SUPABASE              │  │     ML SERVICE (FastAPI)        │
│                        │  │                                 │
│  PostgreSQL:           │  │  Endpoints:                     │
│  ├── jobs              │  │  ├── POST /rank                 │
│  ├── cv_uploads        │  │  ├── GET  /trends               │
│  └── match_logs        │  │  └── GET  /health               │
│                        │  │                                 │
│  Storage:              │  │  Model: Siamese BiLSTM          │
│  └── cv-uploads bucket │  │  File:  best_model.keras (14MB) │
│                        │  │  Tokenizer: tokenizer.pkl       │
│  Connection via:       │  │                                 │
│  asyncpg (pooler:6543) │  │  Tech: TensorFlow, Keras 3      │
│  Supabase SDK (REST)   │  │  Port: 8001                     │
└────────────────────────┘  └────────────────────────────────┘
```

---

## Alur Data (End-to-End)

### 1. Upload CV

```
User → [Frontend] POST /api/cv/upload (file PDF)
                 → [Backend] validate (type, size)
                 → [Backend] upload_to_supabase() → Supabase Storage
                 → [Backend] extract_text_from_pdf() → raw text
                 → [Backend] extract_skills() → ["python", "react", ...]
                 → [Backend] save to DB (cv_uploads table)
                 → Response: { id, filename, storage_path, skills, uploaded_at }
```

### 2. Match CV dengan Jobs

```
User → [Frontend] POST /api/match { cv_id, top_k }
                 → [Backend] load CV dari DB
                 → [Backend] load semua Jobs dari DB
                 → [Backend] TRY: call ML Service /rank
                   │
                   ├─ SUCCESS → ML Service: Siamese BiLSTM inference
                   │            Model menerima (cv_sequence, job_sequence)
                   │            Return: ranked results dengan skor 0-1
                   │
                   └─ FAIL (timeout/error) → Fallback: Local TF-IDF Matcher
                              matcher.py: TF-IDF + Cosine Similarity + Skill Overlap
                              Scoring: 60% TF-IDF + 40% Skill Match
                 
                 → [Backend] save ke match_logs
                 → Response: { cv_id, results: [{ job_id, title, score, matched_skills, gap_skills }] }
```

### 3. Browse Lowongan

```
User → [Frontend] GET /api/jobs?page=1&per_page=20&search=python
                 → [Backend] query DB dengan filter + pagination
                 → Response: { total, page, per_page, data: [JobResponse] }
```

### 4. Tren Skill

```
User → [Frontend] GET /api/match/trends
                 → [Backend] proxy ke ML Service GET /trends
                 → [ML Service] time-series analysis
                 → Response: { period, trends: [{ skill, current_demand, predicted_demand, growth_pct }] }
```

---

## Database Schema

```sql
-- Tabel 1: Lowongan Kerja
CREATE TABLE jobs (
    id          VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title       VARCHAR(255) NOT NULL,
    company     VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    skills      JSONB NOT NULL DEFAULT '[]',
    location    VARCHAR(100),
    source_url  VARCHAR(500),
    scraped_at  TIMESTAMP DEFAULT now()
);

-- Tabel 2: CV yang Diupload
CREATE TABLE cv_uploads (
    id           VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    filename     VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    raw_text     TEXT,
    skills       JSONB NOT NULL DEFAULT '[]',
    uploaded_at  TIMESTAMP DEFAULT now()
);

-- Tabel 3: Log Hasil Matching
CREATE TABLE match_logs (
    id              VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    cv_id           VARCHAR REFERENCES cv_uploads(id) ON DELETE CASCADE,
    job_id          VARCHAR REFERENCES jobs(id) ON DELETE CASCADE,
    score           FLOAT NOT NULL,
    matched_skills  JSONB NOT NULL DEFAULT '[]',
    gap_skills      JSONB NOT NULL DEFAULT '[]',
    matched_at      TIMESTAMP DEFAULT now()
);
```

---

## Environment Variables

### Backend (`backend/.env`)

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_BUCKET=cv-uploads
ML_SERVICE_URL=http://localhost:8001
ML_SERVICE_TIMEOUT=30
CORS_ORIGINS=["http://localhost:3000"]
MAX_CV_SIZE_MB=5
```

### Frontend (`frontend/.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Deployment

### Opsi 1: Docker Compose (Development)

```bash
docker-compose up --build
# db:       localhost:5432
# backend:  localhost:8000
# frontend: localhost:3000
# ml:       localhost:8001
```

### Opsi 2: Cloud (Production)

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Vercel | skillscout-nusantara.vercel.app |
| Backend | Vercel (serverless) | skillscout-api.vercel.app |
| ML Service | Railway / Render | skillscout-ml-xxx.up.railway.app |
| Database | Supabase | ktoyprdosloxelbsclkj.supabase.co |
