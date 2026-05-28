# 🤖 AI Context File — SkillScout Nusantara

> **Tujuan file ini:** Memberikan konteks lengkap kepada AI assistant (Gemini, Claude, ChatGPT, dll) agar langsung memahami projek ini tanpa perlu eksplorasi ulang dari nol.
>
> **Terakhir diperbarui:** 26 Mei 2026 (rev.3 — ml-service + Railway deploy)

---

## 1. IDENTITAS PROJEK

| Key | Value |
|-----|-------|
| **Nama** | SkillScout Nusantara |
| **Tim** | CC26-PSU215 |
| **Tipe** | Capstone Project — Platform Pencari Kerja Berbasis AI |
| **Deskripsi** | Web app yang mencocokkan CV pengguna dengan lowongan kerja menggunakan Deep Learning (Siamese BiLSTM). User upload PDF CV → AI ekstrak skill → model ranking lowongan terbaik → tampilkan skor + skill gap. |
| **Anggota Tim** | Full-Stack: Orellius & Bagus · AI: Jennifer & Velicia · Data: Fikran & Albi |
| **Repository** | Monorepo — satu repo berisi `frontend/`, `backend/`, `ai/`, `ml-service/`, `datasets/` |

---

## 2. ARSITEKTUR & STACK TEKNOLOGI

```
USER (Browser :3000)
  │
  ▼
FRONTEND ── Next.js 16 · React 19 · TypeScript · Tailwind CSS 4
  │          Lucide React icons · Recharts
  │          Port: 3000
  │
  │ fetch() → NEXT_PUBLIC_API_URL
  ▼
BACKEND ─── FastAPI · Python 3.11 · SQLAlchemy 2.0 (async) · asyncpg
  │          pdfplumber + Sastrawi + NLTK (CV parsing)
  │          scikit-learn TF-IDF (fallback matcher)
  │          httpx → ML Service
  │          Port: 8000
  │
  ├──→ SUPABASE ── PostgreSQL (3 tabel: jobs, cv_uploads, match_logs)
  │                 Storage bucket: cv-uploads (PDF files)
  │                 Pooler: aws-1-ap-south-1.pooler.supabase.com:6543
  │
  └──→ ML SERVICE ─ FastAPI · TensorFlow · Keras 3
                     Model: Siamese BiLSTM (best_model.keras, 14 MB)
                     Tokenizer: tokenizer.pkl (BELUM ADA — harus diekspor)
                     Port: 8001
```

### Database Schema (3 tabel)

```
jobs           → id, title, company, description, skills (JSONB), location, source_url, scraped_at
cv_uploads     → id, filename, storage_path, raw_text, skills (JSONB), uploaded_at
match_logs     → id, cv_id (FK), job_id (FK), score, matched_skills (JSONB), gap_skills (JSONB), matched_at
```

---

## 3. STRUKTUR FILE LENGKAP

```
skillscout-nusantara/
│
├── frontend/                          # ✅ SELESAI 100%
│   ├── app/
│   │   ├── layout.tsx                 # Root layout: Navbar + Footer wrapper
│   │   ├── page.tsx                   # Landing page (hero, fitur, CTA)
│   │   ├── globals.css                # Design system (dark glassmorphism, 12KB)
│   │   ├── upload/page.tsx            # Upload CV: drag & drop → auto-match
│   │   ├── jobs/page.tsx              # Browse lowongan: search + pagination
│   │   ├── match/[cvId]/page.tsx      # Hasil matching: score ring + skill gap
│   │   ├── trends/page.tsx            # Tren skill: progress bar demand
│   │   ├── lib/api.ts                 # API client: apiGet, apiPost, apiUpload + typed wrappers
│   │   ├── types/api.ts               # TypeScript interfaces (mirror backend schemas.py)
│   │   └── components/
│   │       ├── Navbar.tsx             # Glassmorphism fixed nav, mobile hamburger
│   │       ├── Footer.tsx             # Footer: links, tech stack, tim info
│   │       ├── CVUploadForm.tsx       # Drag-drop zone, validasi PDF, auto redirect
│   │       ├── JobCard.tsx            # Card lowongan: skills badge, meta info
│   │       ├── MatchResultCard.tsx    # SVG score ring animasi + matched/gap skills
│   │       └── SkillBadge.tsx         # Badge reusable: primary/success/warning/error
│   ├── .env.local                     # NEXT_PUBLIC_API_URL=http://localhost:8000
│   ├── package.json                   # next 16.2.4, react 19, lucide, recharts
│   ├── Dockerfile                     # Dev: npm run dev
│   └── tsconfig.json                  # paths: @/* → ./*
│
├── backend/                           # ✅ SELESAI 90%
│   ├── app/
│   │   ├── main.py                    # FastAPI app, 3 routers, CORS, /api/health
│   │   ├── config.py                  # pydantic-settings: DB, Supabase, ML, CORS, JWT
│   │   ├── database.py                # async engine + session factory + get_db dependency
│   │   ├── db/models.py               # ORM: Job, CVUpload, MatchLog (SQLAlchemy 2.0 Mapped)
│   │   ├── models/schemas.py          # Pydantic: JobCreate/Response, CVUpload, Match, Trend
│   │   ├── routers/
│   │   │   ├── cv.py                  # POST /api/cv/upload, GET /api/cv/{id}
│   │   │   ├── jobs.py                # GET /api/jobs (filter+pagination), GET /{id}, POST
│   │   │   └── match.py               # POST /api/match (ML→fallback TF-IDF), GET /trends
│   │   ├── services/
│   │   │   ├── cv_parser.py           # pdfplumber + Sastrawi + NLTK + skill gazetteer bilingual
│   │   │   ├── matcher.py             # TF-IDF cosine + skill overlap (60:40) — fallback
│   │   │   └── storage.py             # Supabase Storage upload/get_public_url
│   │   ├── ml/
│   │   │   ├── __init__.py            # Dokumentasi modul
│   │   │   └── placeholder.py         # ✅ Arsitektur Siamese BiLSTM (sesuai model asli)
│   │   ├── scraping/
│   │   │   └── glints_scraper.py      # GlintsScraper: scrape Glints.com → CSV
│   │   └── cleaning/
│   │       └── clean_raw_data.py      # ✅ Pipeline cleaning (Glints, JobMarket, CV)
│   ├── .env                           # BERISI credentials Supabase (AKTIF)
│   ├── requirements.txt               # fastapi, sqlalchemy, asyncpg, pdfplumber, dll
│   ├── vercel.json                    # Serverless deploy config
│   ├── api/index.py                   # Vercel entry point
│   └── supabase/
│       ├── 001_init_tables.sql        # CREATE TABLE jobs, cv_uploads, match_logs
│       └── 002_create_bucket.sql      # Storage bucket + RLS policy
│
├── ai/                                # ⚠️ MODEL ADA, AKURASI RENDAH
│   ├── best_model.keras               # Siamese BiLSTM (14 MB) — accuracy 45%
│   ├── model.ipynb                    # Training notebook (Keras 3.13.2)
│   ├── cv_processing.ipynb            # Notebook pengolahan CV
│   ├── CV.csv                         # 505 raw CV (133 KB)
│   ├── cv_processed.csv               # CV yang sudah diproses (123 KB)
│   ├── JobMarket_Preprocessed.csv     # 800+ lowongan bersih (816 KB)
│   ├── fix_preprocessing.py           # Script fix preprocessing
│   ├── fix_cells.py                   # Script fix notebook cells
│   └── export_tokenizer.py           # ✅ Export tokenizer.pkl dari data training
│
├── ml-service/                        # ✅ LENGKAP — siap deploy Railway
│   ├── main.py                        # FastAPI: /rank (batch), /trends, /health + TF-IDF fallback
│   ├── requirements.txt               # fastapi, tensorflow, scikit-learn, gunicorn
│   ├── Dockerfile                     # Multi-stage, $PORT env, healthcheck
│   ├── railway.toml                   # Railway deploy config (Dockerfile builder)
│   └── .dockerignore                  # Exclude cache, docs, tests
│
├── datasets/
│   └── raw/glints_jobs.csv            # 23 lowongan scraping (11 KB)
│
├── doc/                               # ✅ Dokumentasi lengkap
│   ├── 01-langkah-integrasi.md
│   ├── 02-arsitektur-sistem.md
│   ├── 03-peningkatan-akurasi-model.md
│   ├── 04-panduan-frontend.md
│   ├── 05-panduan-backend-api.md
│   ├── 06-panduan-deployment.md
│   ├── 07-deploy-railway.md           # ✅ BARU — Panduan khusus Railway
│   └── AI.md                          # FILE INI
│
├── docker-compose.yml                 # 4 services: db, backend, frontend, ml
├── langkahintegrasi.md                # Dokumen integrasi lama (v1, 23 KB)
└── penjabaranFull.md                  # Analisis penyatuan awal (lama)
```

---

## 4. STATUS PROGRES PER KOMPONEN

### ✅ Frontend — 100% Selesai

- 5 halaman: `/` (landing), `/upload`, `/jobs`, `/match/[cvId]`, `/trends`
- 6 komponen UI: Navbar, Footer, CVUploadForm, JobCard, MatchResultCard, SkillBadge
- API client dengan typed wrappers untuk semua backend endpoint
- TypeScript types yang sinkron dengan backend Pydantic schemas
- Design system: dark theme, glassmorphism, gradient animations, SVG score ring
- Build verified: `next build` ✅ sukses tanpa error
- Responsive: desktop + mobile

### ✅ Backend — 90% Selesai

**Yang sudah jalan:**
- FastAPI app dengan 3 router group (cv, jobs, match)
- SQLAlchemy 2.0 async ORM (3 tabel)
- CV parser: pdfplumber + Sastrawi stemmer + NLTK + skill gazetteer bilingual
- Local TF-IDF matcher sebagai fallback
- Supabase Storage upload
- Vercel serverless deployment config
- Supabase SQL migrations (2 file)
- CORS configured
- GlintsScraper untuk data collection

**Yang sudah diperbaiki (rev.2):**
- ✅ `clean_raw_data.py` — full pipeline (normalize, parse salary, extract skill, clean Glints + AI data)
- ✅ Testing: 86 tests (85 passed + 1 xfail DB) — test_cv, test_cv_parser, test_matcher, test_cleaning
- ✅ `placeholder.py` — arsitektur Siamese BiLSTM sesuai model asli (Embedding→BiLSTM×2→Dense→L2Norm)
- ✅ `cv_parser.py` — fixed regex untuk C++/C# (lookaround untuk special char skills)

### ⚠️ ML / AI — 45% Akurasi (PERLU DIPERBAIKI)

**Yang ada:**
- `best_model.keras` (14 MB) — Siamese BiLSTM, Keras 3.13.2
- Arsitektur: 2 input (cv_input, job_input) → shared encoder (Embedding→BiLSTM×2→Dense→L2Norm) → Cosine Dot → sigmoid
- Config: max_length=256, vocab_size=10000, embedding_dim=300
- Data: 505 CV + 800 lowongan

**Yang sudah diperbaiki (rev.3):**
- ✅ `ml-service/main.py` — rewrite lengkap: graceful startup, batch predict, TF-IDF fallback, lifespan
- ✅ `ai/export_tokenizer.py` — script export tokenizer dari data training
- ✅ `railway.toml` + Dockerfile multi-stage siap deploy
- ✅ Bug fix `match.py` — `item["job"].id` → `item["job_id"]`

**Yang masih perlu (AI Engineer):**
- ⚠️ `tokenizer.pkl` — jalankan `python ai/export_tokenizer.py`
- ⚠️ Akurasi hanya 45% — lihat `doc/03-peningkatan-akurasi-model.md`

### ✅ Docker & Infra — Selesai

- `docker-compose.yml` dengan 4 services (db, backend, frontend, ml)
- Supabase sebagai managed database + storage (credentials di `backend/.env`)
- Backend configurable via `pydantic-settings` + `.env`
- Railway deploy guide: `doc/07-deploy-railway.md`

---

## 5. BACKEND API ENDPOINTS (Quick Reference)

| Method | Endpoint | Deskripsi | Request | Response |
|--------|----------|-----------|---------|----------|
| GET | `/api/health` | Health check | — | `{status, service}` |
| POST | `/api/cv/upload` | Upload CV PDF | `multipart/form-data: file` | `{id, filename, storage_path, skills[], uploaded_at}` |
| GET | `/api/cv/{id}` | Detail CV | — | CVUploadResponse |
| GET | `/api/jobs` | List lowongan | `?page&per_page&location&skill&search` | `{total, page, per_page, data[]}` |
| GET | `/api/jobs/{id}` | Detail lowongan | — | JobResponse |
| POST | `/api/jobs` | Tambah lowongan | JSON body | JobResponse |
| POST | `/api/match` | Match CV↔Jobs | `{cv_id, top_k}` | `{cv_id, results[{job_id, title, company, score, matched_skills, gap_skills}]}` |
| GET | `/api/match/trends` | Tren skill (proxy ML) | — | `{period, trends[{skill, current_demand, predicted_demand, growth_pct}]}` |

**Matching flow:** Backend coba panggil ML Service (`POST /rank`) → jika gagal/timeout → fallback ke local TF-IDF matcher (60% cosine + 40% skill overlap).

---

## 6. ENVIRONMENT VARIABLES

### Backend (`backend/.env`) — SUDAH TERISI

```
DATABASE_URL=postgresql+asyncpg://postgres.ktoyprdosloxelbsclkj:***@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://ktoyprdosloxelbsclkj.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_BUCKET=cv-uploads
CORS_ORIGINS=["http://127.0.0.1:3000","https://skillscout-nusantara.vercel.app","http://localhost:8000"]
MAX_CV_SIZE_MB=5
# ML_SERVICE_URL belum diset (default: http://localhost:8001)
```

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 7. CARA MENJALANKAN

```bash
# Frontend (dev)
cd frontend && npm install --no-bin-links --ignore-scripts && npm run dev
# → http://localhost:3000

# Backend (dev)
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/api/docs (Swagger)

# ML Service (dev) — BELUM BISA tanpa tokenizer.pkl
cd ml-service && pip install -r requirements.txt && uvicorn main:app --reload --port 8001

# Docker (semua sekaligus)
docker-compose up --build
```

**Catatan filesystem:** Projek ada di USB drive (FAT32/exFAT) → `npm install` perlu flag `--no-bin-links --ignore-scripts` karena filesystem tidak mendukung symlinks.

---

## 8. MASALAH KRITIS & PRIORITAS

| # | Masalah | Status | Prioritas | Solusi |
|---|---------|--------|-----------|--------|
| 1 | **Model accuracy 45%** | ❌ | 🔴 KRITIS | Data balancing + attention + better preprocessing. Detail: `doc/03-peningkatan-akurasi-model.md` |
| 2 | **tokenizer.pkl tidak ada** | ❌ | 🔴 KRITIS | Jalankan ulang notebook, simpan tokenizer via pickle |
| 3 | **clean_raw_data.py kosong** | ✅ SELESAI | — | Pipeline lengkap: Glints, JobMarket, CV cleaning |
| 4 | **Data lowongan sedikit** | ⚠️ | 🟡 SEDANG | Scrape lebih banyak halaman Glints (saat ini hanya 23 jobs di raw) |
| 5 | **Testing minim** | ✅ SELESAI | — | 86 tests: API, cv_parser, matcher, cleaning |
| 6 | **placeholder.py ≠ model asli** | ✅ SELESAI | — | Diupdate ke arsitektur Siamese BiLSTM yang benar |

---

## 9. ALUR DATA END-TO-END

```
[User browser]
    │
    ├── Upload CV (PDF) ──→ POST /api/cv/upload
    │                          ├── Validasi (PDF only, max 5MB)
    │                          ├── upload_to_supabase() → Supabase Storage
    │                          ├── extract_text_from_pdf() → pdfplumber
    │                          ├── extract_skills() → gazetteer + Sastrawi
    │                          ├── INSERT INTO cv_uploads
    │                          └── Return: {id, skills[]}
    │
    ├── Match CV ──→ POST /api/match {cv_id, top_k}
    │                   ├── SELECT cv FROM cv_uploads
    │                   ├── SELECT * FROM jobs
    │                   ├── TRY: httpx POST ml-service:8001/rank
    │                   │     ├── text_to_sequence(cv_text)  ← tokenizer
    │                   │     ├── text_to_sequence(job_text) ← tokenizer
    │                   │     ├── model.predict([cv_seq, job_seq])
    │                   │     └── Return ranked results
    │                   ├── CATCH: fallback → matcher.py (TF-IDF+cosine+skill overlap)
    │                   ├── INSERT INTO match_logs (per result)
    │                   └── Return: {cv_id, results[{score, matched_skills, gap_skills}]}
    │
    ├── Browse Jobs ──→ GET /api/jobs?search=...&page=1
    │                      └── SELECT FROM jobs WHERE ... LIMIT/OFFSET
    │
    └── Trends ──→ GET /api/match/trends
                      └── httpx GET ml-service:8001/trends → placeholder data
```

---

## 10. KONVENSI & POLA KODE

### Backend
- **Router pattern:** `app/routers/{resource}.py` → `APIRouter()` → mounted di `main.py` dengan prefix `/api/{resource}`
- **Schema pattern:** Pydantic models di `app/models/schemas.py`, ORM di `app/db/models.py`
- **Service pattern:** Business logic di `app/services/`, router hanya orchestration
- **Config:** Semua env vars via `pydantic-settings` (`app/config.py` → `settings` singleton)
- **DB session:** Dependency injection via `get_db()` → auto commit/rollback

### Frontend
- **App Router:** Next.js 16 `app/` directory, setiap route = folder + `page.tsx`
- **Client components:** File yang butuh state/hooks pakai `"use client"` directive
- **API calls:** Semua via `app/lib/api.ts` → typed return values
- **Styling:** Tailwind CSS utility classes + CSS custom properties di `globals.css`
- **Icons:** `lucide-react` (tree-shakable)

### ML Service
- **Inference pattern:** Load model + tokenizer saat startup (global), reuse per request
- **Input format:** `{cv_text: str, jobs: [{id, description, skills}], top_k: int}`
- **Output format:** `{results: [{job_id, title, company, score, matched_skills, gap_skills}]}`

---

## 11. FILE YANG JANGAN DIUBAH TANPA HATI-HATI

| File | Alasan |
|------|--------|
| `backend/.env` | Berisi credentials Supabase production |
| `backend/app/db/models.py` | ORM harus sinkron dengan migration SQL + schemas.py |
| `backend/app/models/schemas.py` | Harus sinkron dengan frontend `types/api.ts` + ORM |
| `frontend/app/types/api.ts` | Mirror dari backend schemas |
| `ai/best_model.keras` | Binary model file 14 MB |
| `backend/supabase/*.sql` | Database migration (sudah dijalankan di production) |

---

## 12. REFERENSI DOKUMENTASI LAINNYA

| File | Isi |
|------|-----|
| `doc/01-langkah-integrasi.md` | Langkah integrasi revisi + checklist |
| `doc/02-arsitektur-sistem.md` | Diagram arsitektur + DB schema + env vars |
| `doc/03-peningkatan-akurasi-model.md` | Panduan detail 45%→90% dengan code examples |
| `doc/04-panduan-frontend.md` | Dokumentasi frontend: halaman, komponen, design system |
| `doc/05-panduan-backend-api.md` | API reference semua endpoints |
| `doc/06-panduan-deployment.md` | Deploy: Vercel, Railway, Docker, Supabase |
| `doc/07-deploy-railway.md` | **BARU** — Panduan khusus Railway (strategi hybrid, step-by-step) |
| `langkahintegrasi.md` (root) | Dokumen integrasi v1 (lama, sebelum frontend dibuat) |
| `penjabaranFull.md` (root) | Analisis penyatuan awal (lama) |

---

> **Untuk AI assistant:** Jika diminta mengerjakan sesuatu di projek ini, baca file ini dulu. Semua konteks arsitektur, status, dan konvensi ada di sini. Untuk detail spesifik per komponen, lihat file dokumentasi yang relevan di `doc/`.
