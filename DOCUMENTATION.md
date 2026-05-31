# 📚 SkillScout Nusantara — Dokumentasi API & Path Lengkap

> Dokumentasi resmi untuk seluruh endpoint RESTful API (Backend) dan halaman Frontend
> **Terakhir diperbarui:** 31 Mei 2026

---

## 📌 Daftar Isi

1. [Arsitektur Sistem](#-arsitektur-sistem)
2. [Tech Stack](#-tech-stack)
3. [Checklist Main Quest](#-checklist-main-quest)
4. [Backend — RESTful API Endpoints](#-backend--restful-api-endpoints)
   - [Health Check](#1-health-check)
   - [Jobs API](#2-jobs-api)
   - [CV Upload API](#3-cv-upload-api)
   - [Match API](#4-match-api)
   - [Trends API](#5-trends-api)
5. [Frontend — Halaman & Routing](#-frontend--halaman--routing)
6. [ML Service — Endpoint](#-ml-service--endpoint)
7. [Database Schema](#-database-schema)
8. [Cara Menjalankan Lokal](#-cara-menjalankan-lokal)
9. [Deployment Links](#-deployment-links)

---

## 🏗 Arsitektur Sistem

```
┌──────────────────┐     HTTP/Proxy      ┌──────────────────┐
│                  │ ──────────────────>  │                  │
│  Frontend        │  /api/* (rewrite)   │  Backend (API)   │
│  (Next.js)       │ <──────────────────  │  (FastAPI)       │
│  Port: 3000      │     JSON Response   │  Port: 8000      │
│                  │                     │                  │
└──────────────────┘                     └────────┬─────────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    │             │             │
                              ┌─────▼─────┐ ┌────▼────┐ ┌──────▼──────┐
                              │ Supabase  │ │ Supabase│ │ ML Service  │
                              │ PostgreSQL│ │ Storage │ │ (Railway)   │
                              │ Database  │ │ (CV)    │ │ Port: 8001  │
                              └───────────┘ └─────────┘ └─────────────┘
```

---

## 🛠 Tech Stack

| Layer          | Teknologi                                          | Checklist Item                                        |
|----------------|---------------------------------------------------|------------------------------------------------------|
| **Frontend**   | Next.js 16 + React 19 + TypeScript                | ✅ Module bundler (Turbopack/Webpack via Next.js)    |
| **Styling**    | Tailwind CSS 4 + Custom CSS (Glassmorphism)        | ✅ Responsive layout                                |
| **API Client** | `fetch()` native via `app/lib/api.ts`              | ✅ Networking calls untuk interaksi API              |
| **Backend**    | Python FastAPI + Uvicorn                           | ✅ RESTful API mendukung frontend                   |
| **Database**   | PostgreSQL (Supabase) + SQLAlchemy Async ORM       | ✅ RESTful API menyimpan data ke database            |
| **Storage**    | Supabase Storage (bucket: `cv-uploads`)            | ✅ Upload & penyimpanan file CV                      |
| **AI/ML**      | TF-IDF + Cosine Similarity (lokal) / Siamese BiLSTM (Railway) | ✅ Integrasi AI/ML sebagai fitur utama |
| **Deployment** | Vercel (Frontend + Backend) + Railway (ML Service) | ✅ Deployment ke server                              |

---

## ✅ Checklist Main Quest

| #  | Requirement                                                          | Status | Keterangan                                                                                |
|----|----------------------------------------------------------------------|--------|-------------------------------------------------------------------------------------------|
| 1  | Menggunakan networking calls untuk interaksi API                     | ✅     | `fetch()` di `app/lib/api.ts` — `apiGet`, `apiPost`, `apiUpload`                          |
| 2  | Menggunakan module bundler (Webpack/Vite)                            | ✅     | Next.js 16 menggunakan Turbopack (dev) dan Webpack (build)                                 |
| 3  | Membangun RESTful API                                                | ✅     | FastAPI: `/api/jobs`, `/api/cv`, `/api/match`, `/api/match/trends`                         |
| 4  | RESTful API menyimpan data (dengan/tanpa database)                   | ✅     | PostgreSQL (Supabase) via SQLAlchemy async + Supabase Storage                              |
| 5  | URL mengikuti standar konvensi RESTful                               | ✅     | GET/POST `/api/jobs`, GET `/api/jobs/{id}`, POST `/api/cv/upload`, POST `/api/match`       |
| 6  | Integrasi AI/ML sebagai fitur utama                                  | ✅     | CV skill extraction (NLP), TF-IDF matching, Siamese BiLSTM (ML Service)                   |
| 7  | Fitur utama berjalan tanpa crash                                     | ✅     | Upload CV → Extract Skills → Match Jobs → Skill Gap Analysis                               |
| 8  | Tidak menggunakan Web Generator                                      | ✅     | Seluruh kode ditulis manual (from scratch)                                                 |

### Side Quest (Optional)
| #  | Requirement                                  | Status | Keterangan                                      |
|----|----------------------------------------------|--------|--------------------------------------------------|
| 1  | Mockup aplikasi (UI representation)          | ✅     | Dark theme, glassmorphism, responsive             |
| 2  | Layout responsif                             | ✅     | CSS Grid + media queries, mobile toggle navbar    |
| 3  | Database storage                             | ✅     | PostgreSQL Supabase                               |
| 4  | Framework Express → FastAPI (Python equiv)   | ✅     | FastAPI sebagai framework backend                 |
| 5  | Tailwind CSS                                 | ✅     | Tailwind CSS v4                                   |
| 6  | Deployment                                   | ✅     | Vercel (FE+BE) + Railway (ML)                     |

---

## 🔌 Backend — RESTful API Endpoints

**Base URL Lokal:** `http://localhost:8000`  
**Base URL Production:** `https://skillscout-nusantara-backend.vercel.app`  
**Swagger Docs:** `{BASE_URL}/api/docs`  
**ReDoc:** `{BASE_URL}/api/redoc`  

### 1. Health Check

| Method | Endpoint       | Deskripsi                            |
|--------|----------------|--------------------------------------|
| `GET`  | `/api/health`  | Cek apakah server API aktif dan sehat |

**Response (200):**
```json
{
  "status": "ok",
  "service": "skillscout-api"
}
```

---

### 2. Jobs API

#### 2a. List Lowongan (Paginated + Filter)

| Method | Endpoint    | Deskripsi                                         |
|--------|-------------|---------------------------------------------------|
| `GET`  | `/api/jobs` | Daftar lowongan dengan pagination dan filter      |

**Query Parameters:**
| Parameter  | Tipe    | Default | Deskripsi                         |
|------------|---------|---------|-----------------------------------|
| `page`     | int     | 1       | Nomor halaman (≥1)                |
| `per_page` | int     | 20      | Item per halaman (1-100)          |
| `location` | string  | null    | Filter berdasarkan lokasi          |
| `skill`    | string  | null    | Filter berdasarkan skill (JSONB)   |
| `search`   | string  | null    | Pencarian judul/perusahaan         |

**Response (200):**
```json
{
  "total": 23,
  "page": 1,
  "per_page": 20,
  "data": [
    {
      "id": "7497613f-5c39-4773-8650-ceaf326346cc",
      "title": "Full Stack Developer",
      "company": "Tokopedia",
      "description": "Kami mencari Full Stack Developer...",
      "skills": ["react", "javascript", "typescript", "postgresql"],
      "location": "Jakarta",
      "source_url": "https://www.tokopedia.com/careers",
      "scraped_at": "2026-05-31T11:44:31.084688"
    }
  ]
}
```

#### 2b. Detail Lowongan

| Method | Endpoint           | Deskripsi                      |
|--------|--------------------|--------------------------------|
| `GET`  | `/api/jobs/{job_id}` | Detail satu lowongan         |

**Response (200):**
```json
{
  "id": "7497613f-...",
  "title": "Full Stack Developer",
  "company": "Tokopedia",
  "description": "...",
  "skills": ["react", "javascript"],
  "location": "Jakarta",
  "source_url": "https://...",
  "scraped_at": "2026-05-31T11:44:31.084688"
}
```

**Error (404):**
```json
{"detail": "Lowongan tidak ditemukan."}
```

#### 2c. Tambah Lowongan

| Method | Endpoint    | Deskripsi                               |
|--------|-------------|-----------------------------------------|
| `POST` | `/api/jobs` | Tambah lowongan baru (admin/scraper)    |

**Request Body (JSON):**
```json
{
  "title": "Data Scientist",
  "company": "Gojek",
  "description": "Bergabunglah dengan tim Data Science...",
  "skills": ["python", "machine learning", "tensorflow"],
  "location": "Jakarta",
  "source_url": "https://www.gojek.com/careers"
}
```

**Response (201):** Sama seperti detail lowongan di atas.

---

### 3. CV Upload API

#### 3a. Upload CV

| Method | Endpoint         | Deskripsi                                       |
|--------|------------------|-------------------------------------------------|
| `POST` | `/api/cv/upload` | Upload file PDF CV, ekstrak teks & skill otomatis |

**Request:** `multipart/form-data`
| Field  | Tipe | Deskripsi                    |
|--------|------|------------------------------|
| `file` | File | File PDF CV (maks 5 MB)      |

**Response (201):**
```json
{
  "id": "abc12345-...",
  "filename": "cv_bagus.pdf",
  "storage_path": "cv/20260531_114500_a1b2c3d4.pdf",
  "skills": ["python", "react", "machine learning", "docker"],
  "uploaded_at": "2026-05-31T11:45:00.000000"
}
```

**Proses Internal:**
1. Validasi tipe file (hanya PDF)
2. Validasi ukuran (maks 5 MB)
3. Upload ke Supabase Storage
4. Ekstrak teks dari PDF (pdfplumber)
5. Deteksi skill menggunakan NLP (Sastrawi + NLTK + Gazetteer bilingual)
6. Simpan ke database PostgreSQL

**Error:**
- `400`: Hanya file PDF yang diizinkan
- `413`: Ukuran file melebihi 5 MB

#### 3b. Detail CV

| Method | Endpoint          | Deskripsi                         |
|--------|-------------------|-----------------------------------|
| `GET`  | `/api/cv/{cv_id}` | Ambil detail CV yang sudah diproses |

**Response (200):** Sama seperti upload response.

**Error (404):**
```json
{"detail": "CV tidak ditemukan."}
```

---

### 4. Match API

#### 4a. Cocokkan CV dengan Lowongan

| Method | Endpoint     | Deskripsi                                                  |
|--------|--------------|------------------------------------------------------------|
| `POST` | `/api/match` | Cocokkan skill CV dengan semua lowongan, kembalikan top-K   |

**Request Body (JSON):**
```json
{
  "cv_id": "abc12345-...",
  "top_k": 10
}
```

**Response (200):**
```json
{
  "cv_id": "abc12345-...",
  "results": [
    {
      "job_id": "7497613f-...",
      "title": "Full Stack Developer",
      "company": "Tokopedia",
      "score": 0.7234,
      "matched_skills": ["react", "javascript", "docker"],
      "gap_skills": ["typescript", "postgresql"]
    }
  ]
}
```

**Proses Internal:**
1. Ambil CV dari database (by `cv_id`)
2. Ambil semua lowongan dari database
3. **Coba kirim ke ML Service** (Railway — Siamese BiLSTM):
   - Jika berhasil → gunakan ranking dari deep learning model
4. **Fallback ke TF-IDF lokal** jika ML Service error:
   - TF-IDF Vectorizer + Cosine Similarity (60%)
   - Skill Overlap Scoring (40%)
5. Log hasil ke `match_logs` table

**Error:**
- `404`: CV tidak ditemukan / Belum ada data lowongan

---

### 5. Trends API

#### 5a. Prediksi Tren Skill

| Method | Endpoint             | Deskripsi                                |
|--------|----------------------|------------------------------------------|
| `GET`  | `/api/match/trends`  | Prediksi tren skill dari ML Service       |

**Response (200):**
```json
{
  "period": "2026-Q2",
  "trends": [
    {
      "skill": "python",
      "current_demand": 0.85,
      "predicted_demand": 0.90,
      "growth_pct": 5.88
    },
    {
      "skill": "machine learning",
      "current_demand": 0.72,
      "predicted_demand": 0.82,
      "growth_pct": 13.89
    }
  ]
}
```

**Catatan:** Jika ML Service offline, backend mengembalikan data fallback statis.

---

## 🖥 Frontend — Halaman & Routing

**Base URL Lokal:** `http://localhost:3000`  
**Base URL Production:** `https://skillscout-nusantara.vercel.app`  
**Module Bundler:** Next.js 16 (Turbopack dev / Webpack production)

### Daftar Halaman

| Path               | File                              | Deskripsi                                      | Tipe Render  |
|--------------------|-----------------------------------|-------------------------------------------------|-------------|
| `/`                | `app/page.tsx`                    | Homepage — Hero, cara kerja, fitur utama, CTA   | SSR (Server) |
| `/upload`          | `app/upload/page.tsx`             | Form upload CV (drag & drop PDF)                | SSR (Server) |
| `/jobs`            | `app/jobs/page.tsx`               | Daftar lowongan kerja (pagination + search)     | CSR (Client) |
| `/match/[cvId]`    | `app/match/[cvId]/page.tsx`       | Hasil matching CV dengan lowongan               | CSR (Client) |
| `/trends`          | `app/trends/page.tsx`             | Prediksi tren skill (demand chart)              | CSR (Client) |

### Komponen Utama

| Komponen             | File                                  | Deskripsi                                 |
|----------------------|---------------------------------------|-------------------------------------------|
| `Navbar`             | `app/components/Navbar.tsx`           | Navigation bar (responsive, mobile toggle)|
| `Footer`             | `app/components/Footer.tsx`           | Footer dengan info tim & teknologi        |
| `CVUploadForm`       | `app/components/CVUploadForm.tsx`     | Drag & drop upload form + auto redirect   |
| `JobCard`            | `app/components/JobCard.tsx`          | Kartu lowongan (skills, lokasi, sumber)   |
| `MatchResultCard`    | `app/components/MatchResultCard.tsx`  | Kartu hasil matching (score ring, skills) |
| `SkillBadge`         | `app/components/SkillBadge.tsx`       | Badge skill (4 variant warna)             |

### API Client (`app/lib/api.ts`)

| Fungsi         | Endpoint                  | Method | Deskripsi                        |
|----------------|---------------------------|--------|----------------------------------|
| `healthCheck()`| `/api/health`             | GET    | Health check backend              |
| `getJobs()`    | `/api/jobs`               | GET    | Ambil daftar lowongan (paginated)|
| `getJob(id)`   | `/api/jobs/{id}`          | GET    | Detail satu lowongan              |
| `uploadCV(file)` | `/api/cv/upload`        | POST   | Upload file CV (FormData)         |
| `getCV(id)`    | `/api/cv/{id}`            | GET    | Detail CV yang sudah diproses     |
| `matchCV(cvId, topK)` | `/api/match`       | POST   | Matching CV dengan lowongan       |
| `getTrends()`  | `/api/match/trends`       | GET    | Prediksi tren skill               |

### TypeScript Types (`app/types/api.ts`)

```typescript
interface JobResponse {
  id: string; title: string; company: string;
  description: string; skills: string[];
  location: string | null; source_url: string | null;
  scraped_at: string;
}

interface JobListResponse {
  total: number; page: number; per_page: number;
  data: JobResponse[];
}

interface CVUploadResponse {
  id: string; filename: string; storage_path: string;
  skills: string[]; uploaded_at: string;
}

interface MatchResultItem {
  job_id: string; title: string; company: string;
  score: number; matched_skills: string[]; gap_skills: string[];
}

interface MatchResponse { cv_id: string; results: MatchResultItem[]; }

interface TrendItem {
  skill: string; current_demand: number;
  predicted_demand: number; growth_pct: number;
}

interface TrendResponse { period: string; trends: TrendItem[]; }
```

---

## 🤖 ML Service — Endpoint

**Base URL:** `https://skillscout-nusantara-ml-service.up.railway.app`

| Method | Endpoint   | Deskripsi                                         |
|--------|------------|---------------------------------------------------|
| `POST` | `/rank`    | Ranking CV terhadap jobs menggunakan Siamese BiLSTM |
| `GET`  | `/trends`  | Prediksi tren demand skill                         |
| `GET`  | `/health`  | Health check ML service                            |

### POST `/rank` — Request:
```json
{
  "cv_text": "Teks CV lengkap...",
  "jobs": [
    { "id": "...", "title": "...", "company": "...", "description": "...", "skills": [] }
  ],
  "top_k": 10
}
```

### POST `/rank` — Response:
```json
{
  "results": [
    { "job_id": "...", "title": "...", "company": "...", "score": 0.85, "matched_skills": [], "gap_skills": [] }
  ]
}
```

---

## 🗄 Database Schema

**Engine:** PostgreSQL (Supabase)  
**ORM:** SQLAlchemy 2.0 (async)  
**Driver:** asyncpg  
**Migration:** `backend/migrations/init.sql`

### Tabel: `jobs`
| Kolom        | Tipe          | Deskripsi                    |
|-------------|---------------|------------------------------|
| `id`        | TEXT (PK)     | UUID auto-generated          |
| `title`     | VARCHAR(255)  | Judul lowongan               |
| `company`   | VARCHAR(255)  | Nama perusahaan              |
| `description` | TEXT        | Deskripsi lengkap            |
| `skills`    | JSONB         | Array of skill strings       |
| `location`  | VARCHAR(100)  | Lokasi kerja                 |
| `source_url`| VARCHAR(500)  | URL sumber lowongan          |
| `scraped_at`| TIMESTAMP     | Waktu scraping               |

### Tabel: `cv_uploads`
| Kolom          | Tipe          | Deskripsi                   |
|---------------|---------------|-----------------------------|
| `id`          | TEXT (PK)     | UUID auto-generated         |
| `filename`    | VARCHAR(255)  | Nama file asli              |
| `storage_path`| VARCHAR(500)  | Path di Supabase Storage    |
| `raw_text`    | TEXT          | Teks hasil ekstraksi PDF    |
| `skills`      | JSONB         | Array skill terdeteksi      |
| `uploaded_at` | TIMESTAMP     | Waktu upload                |

### Tabel: `match_logs`
| Kolom            | Tipe    | Deskripsi                    |
|-----------------|---------|------------------------------|
| `id`            | TEXT (PK) | UUID auto-generated        |
| `cv_id`         | TEXT (FK) | Referensi ke cv_uploads    |
| `job_id`        | TEXT (FK) | Referensi ke jobs          |
| `score`         | FLOAT   | Skor kecocokan (0-1)        |
| `matched_skills`| JSONB   | Skill yang cocok             |
| `gap_skills`    | JSONB   | Skill yang perlu dipelajari  |
| `matched_at`    | TIMESTAMP | Waktu matching             |

### Database Indexes
- `idx_jobs_skills` — GIN index pada `jobs.skills` (JSONB search)
- `idx_jobs_scraped_at` — B-tree index pada `jobs.scraped_at` (sorting)
- `idx_match_logs_cv_id` — B-tree index pada `match_logs.cv_id`
- `idx_match_logs_score` — B-tree index pada `match_logs.score`

---

## 🚀 Cara Menjalankan Lokal

### Prerequisites
- **Node.js** ≥ 18.x
- **Python** ≥ 3.10
- **PostgreSQL** (atau gunakan Supabase cloud)

### 1. Setup Backend

```bash
cd backend

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab')"

# Buat file .env (copy dari .env.production lalu sesuaikan)
cp .env.production .env

# Jalankan server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend aktif di:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/api/docs`

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Buat file .env.local
echo 'NEXT_PUBLIC_API_URL=http://localhost:8000' > .env.local

# Jalankan server
npm run dev
```

**Frontend aktif di:** `http://localhost:3000`

### 3. Seed Data (Optional)

```bash
cd backend
source venv/bin/activate
python seed_jobs.py
```

---

## 🌐 Deployment Links

| Service      | URL                                                                  | Platform |
|-------------|----------------------------------------------------------------------|----------|
| **Frontend** | https://skillscout-nusantara.vercel.app                              | Vercel   |
| **Backend**  | https://skillscout-nusantara-backend.vercel.app                      | Vercel   |
| **ML Service** | https://skillscout-nusantara-ml-service.up.railway.app             | Railway  |
| **API Docs** | https://skillscout-nusantara-backend.vercel.app/api/docs             | Vercel   |

---

## 📁 Struktur File Lengkap

```
skillscout-nusantara/
├── frontend/                          # Next.js 16 + React 19
│   ├── app/
│   │   ├── components/
│   │   │   ├── CVUploadForm.tsx       # Form upload CV (drag & drop)
│   │   │   ├── Footer.tsx             # Footer layout
│   │   │   ├── JobCard.tsx            # Kartu lowongan
│   │   │   ├── MatchResultCard.tsx    # Kartu hasil matching
│   │   │   ├── Navbar.tsx             # Navigation bar responsive
│   │   │   └── SkillBadge.tsx         # Badge skill (4 variant)
│   │   ├── jobs/page.tsx              # Halaman lowongan
│   │   ├── lib/api.ts                 # API client (fetch wrapper)
│   │   ├── match/[cvId]/page.tsx      # Halaman hasil matching
│   │   ├── trends/page.tsx            # Halaman tren skill
│   │   ├── types/api.ts               # TypeScript interfaces
│   │   ├── upload/page.tsx            # Halaman upload CV
│   │   ├── globals.css                # Design system + animations
│   │   ├── layout.tsx                 # Root layout (Navbar + Footer)
│   │   └── page.tsx                   # Homepage
│   ├── next.config.ts                 # API rewrites (proxy ke backend)
│   ├── package.json                   # Dependencies
│   └── vercel.json                    # Vercel deployment config
│
├── backend/                           # Python FastAPI
│   ├── api/index.py                   # Vercel serverless entrypoint
│   ├── app/
│   │   ├── config.py                  # Environment variables (pydantic-settings)
│   │   ├── database.py                # SQLAlchemy async engine + session
│   │   ├── main.py                    # FastAPI app + CORS + routing
│   │   ├── db/models.py               # ORM models (Job, CVUpload, MatchLog)
│   │   ├── models/schemas.py          # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── cv.py                  # /api/cv/* endpoints
│   │   │   ├── jobs.py                # /api/jobs/* endpoints
│   │   │   └── match.py               # /api/match/* endpoints
│   │   └── services/
│   │       ├── cv_parser.py           # PDF extraction + NLP skill detection
│   │       ├── matcher.py             # TF-IDF + Cosine Similarity (fallback)
│   │       └── storage.py             # Supabase Storage upload
│   ├── migrations/init.sql            # Database schema SQL
│   ├── requirements.txt               # Python dependencies
│   ├── seed_jobs.py                   # Seed data lowongan
│   └── vercel.json                    # Vercel deployment config
│
├── ml-service/                        # ML Microservice (Railway)
│   ├── main.py                        # FastAPI + Siamese BiLSTM inference
│   ├── best_model.keras               # Trained model weights
│   ├── tokenizer.joblib               # Tokenizer untuk text preprocessing
│   ├── Dockerfile                     # Docker build config
│   ├── railway.toml                   # Railway deployment config
│   └── requirements.txt               # Python ML dependencies
│
├── datasets/                          # Data scraping & training
├── docker-compose.yml                 # Multi-service Docker setup
├── DOCUMENTATION.md                   # 📌 File ini
└── README.md                          # Overview proyek
```

---

> **Dibuat oleh Tim CC26-PSU215** — SkillScout Nusantara © 2026
