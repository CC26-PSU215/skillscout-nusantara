<div align="center">

# 🚀 SkillScout Nusantara

**Platform Pencari Kerja Berbasis AI & Prediktor Keterampilan Masa Depan untuk Talenta Indonesia**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.18+-FF6F00?logo=tensorflow)](https://www.tensorflow.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Capstone_CC26-blue)]()

</div>

---

## 📖 Overview

**SkillScout Nusantara** adalah platform cerdas yang dirancang untuk mengatasi masalah *skill mismatch* (ketidakcocokan keterampilan) di pasar tenaga kerja Indonesia.

### Apa yang Dilakukan Platform Ini?

1. **📄 Ekstraksi Skill dari CV** — Upload CV dalam format PDF, sistem mengekstrak skill secara otomatis menggunakan NLP bilingual (Bahasa Indonesia & Inggris), termasuk skill non-formal.
2. **🤖 Pencocokan CV ↔ Lowongan** — Menggunakan model **Siamese BiLSTM** (Deep Learning) untuk menghitung skor kecocokan antara CV dan lowongan kerja yang tersedia.
3. **📊 Analisis Skill Gap** — Menampilkan skill yang sudah dimiliki (*matched skills*) dan skill yang perlu dipelajari (*gap skills*) untuk setiap lowongan.
4. **📈 Prediksi Tren Skill** — Memprediksi skill yang akan dibutuhkan di masa depan berdasarkan analisis data pasar kerja.
5. **🔍 Scraping Lowongan Otomatis** — Data lowongan kerja diambil secara otomatis dari **Glints.com** dengan scheduler harian.

> 💡 **Tanpa API LLM Komersial** — Semua proses AI/ML dibangun dari nol (*from scratch*), memastikan pemrosesan bahasa lokal yang akurat dan privasi data yang terjaga.

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vercel)                        │
│                     Next.js 16 + React 19                       │
│         /upload  /jobs  /match/[cvId]  /trends                  │
└──────────────┬──────────────────────────────────┬───────────────┘
               │  Next.js Rewrites (/api/*)       │
               ▼                                  ▼
┌──────────────────────────┐     ┌────────────────────────────────┐
│    BACKEND API (Vercel)  │     │     ML SERVICE (Railway)       │
│        FastAPI           │────▶│        FastAPI                 │
│                          │     │                                │
│  • /api/cv/upload        │     │  • POST /rank                  │
│  • /api/jobs             │     │    Siamese BiLSTM inference    │
│  • /api/match            │     │    (fallback: TF-IDF)          │
│  • /api/scrape           │     │                                │
│  • /api/match/trends     │     │  • GET /trends                 │
└──────────┬───────────────┘     │    Prediksi tren skill         │
           │                     │                                │
           ▼                     │  • GET /health                 │
┌──────────────────────────┐     │  • GET /model-info             │
│  SUPABASE                │     └────────────────────────────────┘
│  • PostgreSQL (Database) │
│  • Storage (CV PDFs)     │
└──────────────────────────┘
```

---

## 👥 Contributors

Proyek ini dikembangkan oleh Tim **CC26-PSU215** dalam rangka **Capstone Coding Camp 2026**:

| Nama | Role |
|------|------|
| **Muhammad Fikran Naufal** | Data Scientist |
| **Albi Arrizkya Putra** | Data Scientist |
| **Jennifer Khang** | AI Engineer |
| **Velicia Christina Gabriel** | AI Engineer |
| **Orellius Lee** | Full-Stack Web Developer |
| **Bagus Jiran** | Full-Stack Web Developer |

---

## 🛠️ Tech Stack

### Frontend
| Teknologi | Kegunaan |
|-----------|----------|
| **Next.js 16** | Framework React dengan App Router & SSR |
| **React 19** | Library UI |
| **Tailwind CSS 4** | Styling utility-first |
| **Lucide React** | Icon library |
| **Recharts** | Visualisasi data (chart) |
| **React Dropzone** | Upload file drag-and-drop |

### Backend & API
| Teknologi | Kegunaan |
|-----------|----------|
| **FastAPI** | Framework API async (Python) |
| **SQLAlchemy 2.0** | ORM async dengan mapped annotations |
| **asyncpg** | Driver PostgreSQL async |
| **Pydantic v2** | Validasi data & serialisasi |
| **httpx** | HTTP client async (ke ML Service) |
| **BeautifulSoup + lxml** | Web scraping Glints |
| **APScheduler** | Background job scheduler |

### Machine Learning & AI
| Teknologi | Kegunaan |
|-----------|----------|
| **TensorFlow / Keras** | Model Siamese BiLSTM |
| **Scikit-learn** | TF-IDF + Cosine Similarity (fallback) |
| **NLTK** | Natural Language Processing |
| **Sastrawi** | Stemmer Bahasa Indonesia |
| **pdfplumber** | Ekstraksi teks dari PDF |

### Infrastructure & Deployment
| Teknologi | Kegunaan |
|-----------|----------|
| **Vercel** | Hosting frontend + backend (serverless) |
| **Railway** | Hosting ML Service (Docker container) |
| **Supabase** | PostgreSQL database + file storage |
| **Docker** | Containerisasi untuk development lokal |

---

## 📂 Struktur Proyek

Monorepo dengan 4 komponen utama:

```text
skillscout-nusantara/
│
├── frontend/                         # 🌐 Next.js Frontend
│   ├── app/
│   │   ├── components/               # Komponen React
│   │   │   ├── CVUploadForm.tsx      #   Form upload CV (drag-and-drop)
│   │   │   ├── JobCard.tsx           #   Kartu lowongan kerja
│   │   │   ├── MatchResultCard.tsx   #   Kartu hasil matching
│   │   │   ├── SkillBadge.tsx        #   Badge skill (matched/gap)
│   │   │   ├── StatsRow.tsx          #   Statistik real-time (homepage)
│   │   │   ├── Navbar.tsx            #   Navigasi utama
│   │   │   └── Footer.tsx            #   Footer
│   │   ├── jobs/page.tsx             # Halaman daftar lowongan
│   │   ├── upload/page.tsx           # Halaman upload CV
│   │   ├── match/[cvId]/page.tsx     # Halaman hasil matching
│   │   ├── trends/page.tsx           # Halaman prediksi tren skill
│   │   ├── lib/
│   │   │   ├── api.ts                # API client (fetch wrapper)
│   │   │   └── hooks.ts             # Custom React hooks
│   │   ├── types/api.ts             # TypeScript interfaces
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                  # Homepage (landing page)
│   │   └── globals.css              # Global styles
│   ├── Dockerfile                    # Docker config (dev)
│   ├── vercel.json                   # Vercel deployment config
│   └── package.json
│
├── backend/                          # ⚙️ FastAPI Backend
│   ├── app/
│   │   ├── main.py                   # Entry point FastAPI
│   │   ├── config.py                 # Environment variables (pydantic-settings)
│   │   ├── database.py               # Async SQLAlchemy engine + session
│   │   ├── routers/                  # API endpoint handlers
│   │   │   ├── cv.py                 #   POST /api/cv/upload, GET /api/cv/{id}
│   │   │   ├── jobs.py               #   GET /api/jobs, GET /api/jobs/{id}
│   │   │   ├── match.py              #   POST /api/match, GET /api/match/trends
│   │   │   └── scrape.py             #   POST /api/scrape/trigger
│   │   ├── db/models.py              # SQLAlchemy ORM (Job, CVUpload, MatchLog)
│   │   ├── models/schemas.py         # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── cv_parser.py          # Ekstraksi teks PDF + deteksi skill (NLP)
│   │   │   ├── matcher.py            # Local TF-IDF matcher (fallback)
│   │   │   └── storage.py            # Upload/delete file di Supabase Storage
│   │   ├── scraping/
│   │   │   ├── glints_scraper.py     # Web scraper Glints.com
│   │   │   └── scheduler.py          # Background scheduler (APScheduler)
│   │   └── cleaning/
│   │       └── clean_raw_data.py     # Pembersihan data mentah
│   ├── migrations/
│   │   ├── init.sql                  # DDL (CREATE TABLE)
│   │   └── seed_glints_jobs.sql      # Data seed lowongan
│   ├── api/index.py                  # Vercel serverless entry point
│   ├── vercel.json                   # Vercel deployment config + cron jobs
│   ├── requirements.txt
│   └── .env                          # Environment variables (jangan commit!)
│
├── ml-service/                       # 🧠 ML Service (Siamese BiLSTM)
│   ├── main.py                       # FastAPI service (rank, trends, health)
│   ├── best_model.keras              # Trained model weights (~14 MB)
│   ├── tokenizer.joblib              # Keras tokenizer (vocab)
│   ├── Dockerfile                    # Multi-stage Docker build
│   ├── railway.toml                  # Railway deployment config
│   └── requirements.txt
│
├── ai/                               # 🔬 Training & Eksperimen
│   ├── model.ipynb                   # Notebook training Siamese BiLSTM
│   ├── cv_processing.ipynb           # Notebook preprocessing CV
│   ├── CV.csv                        # Dataset CV untuk training
│   └── JobMarket_Preprocessed.csv    # Dataset lowongan untuk training
│
├── datasets/                         # 📊 Data Collection & Generation
│   ├── raw/cv/                       # CV mentah (JSON + CSV per level)
│   │   ├── cvs_junior.{csv,json}
│   │   ├── cvs_mid.{csv,json}
│   │   ├── cvs_senior.{csv,json}
│   │   └── cvs_lead.{csv,json}
│   ├── generated/                    # Data sintetis (10K records)
│   │   ├── generate_data.py          # Script generator dummy data
│   │   ├── cv_generator.py           # Generator CV realistis
│   │   ├── dummy_cvs_10k.csv         # 10,000 CV sintetis
│   │   └── dummy_jobs_10k.csv        # 10,000 lowongan sintetis
│   ├── scraper/                      # ETL pipeline (extract/transform/load)
│   └── requirements.txt
│
├── docker-compose.yml                # Menjalankan semua service lokal
└── README.md
```

---

## 🤖 Model Machine Learning

### Siamese BiLSTM (Arsitektur Utama)

Model deep learning untuk menghitung skor kecocokan antara CV dan lowongan kerja:

```
         CV Text                           Job Text
            │                                  │
            ▼                                  ▼
     ┌──────────────┐                   ┌──────────────┐
     │   Tokenizer  │                   │   Tokenizer  │
     │ (vocab=10000)│                   │ (vocab=10000)│
     └──────┬───────┘                   └──────┬───────┘
            │                                  │
            ▼                                  ▼
   ┌────────────────────────────────────────────────────┐
   │            SHARED ENCODER (weight sharing)         │
   │                                                    │
   │   Embedding(10000, 300, mask_zero=True)            │
   │              ▼                                     │
   │   Bidirectional LSTM(128, return_sequences=True)   │
   │              ▼                                     │
   │   Dropout(0.2)                                     │
   │              ▼                                     │
   │   Bidirectional LSTM(64)                           │
   │              ▼                                     │
   │   Dropout(0.2)                                     │
   │              ▼                                     │
   │   Dense(64, relu) → L2 Normalize                   │
   └────────────────────────────────────────────────────┘
            │                                  │
            ▼                                  ▼
        cv_vector (64d)                  job_vector (64d)
            │                                  │
            └─────────── Dot Product ──────────┘
                            │
                            ▼
                    Similarity Score (0-1)
```

**Training:**
- Data: 501 CV × 501 Job (Jaccard-based pairs)
- Loss: MSE (regression)
- Optimizer: Adam (lr=0.001)
- Best Val MAE: **0.0169**
- ROC AUC: **0.9997**

### TF-IDF + Cosine Similarity (Fallback)

Jika ML Service offline, backend menggunakan fallback lokal:
- **60% TF-IDF Cosine Similarity** — kemiripan teks antara CV dan deskripsi lowongan
- **40% Skill Overlap Score** — rasio skill yang cocok

---

## 🔌 API Endpoints

### Backend API (`/api`)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/cv/upload` | Upload CV (PDF), ekstrak teks & skill |
| `GET` | `/api/cv/{cv_id}` | Detail CV yang sudah diproses |
| `POST` | `/api/cv/cleanup` | Hapus CV kedaluwarsa (>24 jam) |
| `GET` | `/api/jobs` | Daftar lowongan (pagination + filter) |
| `GET` | `/api/jobs/stats/summary` | Statistik lowongan (total jobs & companies) |
| `GET` | `/api/jobs/{job_id}` | Detail satu lowongan |
| `POST` | `/api/jobs` | Tambah lowongan baru |
| `POST` | `/api/match` | Cocokkan CV dengan lowongan (top-K) |
| `GET` | `/api/match/trends` | Prediksi tren skill |
| `POST` | `/api/scrape/trigger` | Manual trigger scraping Glints |
| `GET` | `/api/scrape/status` | Status scraping terakhir |

### ML Service

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `POST` | `/rank` | Ranking lowongan berdasarkan CV (Siamese BiLSTM) |
| `GET` | `/trends` | Prediksi tren skill masa depan |
| `GET` | `/health` | Health check + status model |
| `GET` | `/model-info` | Detail arsitektur & konfigurasi model |

---

## 💻 Cara Run di Local

### Prasyarat

- **Node.js** 20+
- **Python** 3.11+
- **PostgreSQL** 15+ (atau gunakan Supabase)
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/CC26-PSU215/skillscout-nusantara.git
cd skillscout-nusantara
```

### 2. Setup Backend (FastAPI)

```bash
cd backend

# Buat virtual environment
python -m venv .venv

# Aktifkan virtual environment
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependensi
pip install -r requirements.txt

# Setup database (jalankan init.sql di PostgreSQL)
psql $DATABASE_URL < migrations/init.sql

# Konfigurasi environment
cp .env.example .env
# Edit .env → isi DATABASE_URL, SUPABASE_URL, SUPABASE_SERVICE_KEY

# Jalankan server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend berjalan di: `http://localhost:8000`
API Docs (Swagger): `http://localhost:8000/api/docs`

### 3. Setup ML Service

```bash
cd ml-service

# Buat virtual environment
python -m venv .venv
source .venv/bin/activate  # atau .venv\Scripts\activate di Windows

# Install dependensi
pip install -r requirements.txt

# Pastikan file model ada:
#   - best_model.keras (~14 MB)
#   - tokenizer.joblib

# Jalankan server
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

ML Service berjalan di: `http://localhost:8001`

### 4. Setup Frontend (Next.js)

```bash
cd frontend

# Install dependensi
npm install

# Jalankan development server
npm run dev
```

Frontend berjalan di: `http://localhost:3000`

> **Catatan:** Frontend menggunakan Next.js rewrites di `next.config.ts` untuk mem-proxy `/api/*` ke backend. Pastikan backend sudah berjalan di port 8000.

---

## 🐳 Menjalankan dengan Docker

Jika tidak ingin install dependensi satu per satu:

```bash
# Build dan jalankan semua service
docker-compose up -d --build
```

**Akses Layanan:**
| Service | URL |
|---------|-----|
| Frontend (Next.js) | `http://localhost:3000` |
| Backend API (FastAPI) | `http://localhost:8000` |
| API Docs (Swagger) | `http://localhost:8000/api/docs` |
| Database (PostgreSQL) | Port `5432` |

```bash
# Mematikan semua service
docker-compose down
```

---

## ☁️ Deployment (Production)

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | **Vercel** | `skillscout-nusantara.vercel.app` |
| Backend API | **Vercel** (serverless) | Same domain, `/api/*` |
| ML Service | **Railway** (Docker) | Auto-deploy dari branch `main` |
| Database | **Supabase** | PostgreSQL + PgBouncer (port 6543) |
| File Storage | **Supabase Storage** | Bucket `cv-uploads` |

### Cron Jobs (Vercel)

| Schedule | Endpoint | Deskripsi |
|----------|----------|-----------|
| Setiap hari 00:00 UTC | `/api/scrape/trigger` | Auto-scraping lowongan Glints |
| Setiap hari 01:00 UTC | `/api/cv/cleanup` | Hapus CV kedaluwarsa (>24 jam) |

---

## 📊 Database Schema

```sql
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│      jobs         │     │   match_logs     │     │   cv_uploads     │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id          TEXT  │◀────│ job_id      TEXT  │     │ id          TEXT  │
│ title       TEXT  │     │ cv_id       TEXT  │────▶│ filename    TEXT  │
│ company     TEXT  │     │ score      FLOAT  │     │ storage_path TEXT │
│ description TEXT  │     │ matched_skills   │     │ raw_text    TEXT  │
│ skills     JSONB  │     │            JSONB  │     │ skills     JSONB  │
│ location    TEXT  │     │ gap_skills JSONB  │     │ uploaded_at      │
│ source_url  TEXT  │     │ matched_at       │     │          TIMESTAMP│
│ scraped_at       │     │          TIMESTAMP│     └──────────────────┘
│        TIMESTAMP  │     │ id          TEXT  │
└──────────────────┘     └──────────────────┘
```

---

## 📜 Environment Variables

### Backend (`.env`)

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `DATABASE_URL` | Connection string PostgreSQL (asyncpg) | `postgresql+asyncpg://...` |
| `SUPABASE_URL` | URL project Supabase | — |
| `SUPABASE_SERVICE_KEY` | Service role key Supabase | — |
| `SUPABASE_BUCKET` | Nama bucket untuk CV | `cv-uploads` |
| `ML_SERVICE_URL` | URL ML Service | `http://localhost:8001` |
| `ML_SERVICE_TIMEOUT` | Timeout panggilan ke ML Service (detik) | `30` |
| `CORS_ORIGINS` | Allowed origins (JSON array) | `["http://localhost:3000"]` |
| `SCRAPE_API_KEY` | API key untuk endpoint scraping | — |
| `ENABLE_SCRAPE_SCHEDULER` | Aktifkan background scheduler | `false` |
| `MAX_CV_SIZE_MB` | Ukuran maksimal file CV | `5` |

### ML Service

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `PORT` | Port server | `8001` |
| `MODEL_PATH` | Path ke file `.keras` | `best_model.keras` |
| `TOKENIZER_PATH` | Path ke file `.joblib` | `tokenizer.joblib` |
| `MAX_LENGTH` | Panjang sequence input | `256` |
| `BATCH_SIZE` | Ukuran batch prediksi | `32` |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | `*` |

---

## 📝 License

Proyek ini dikembangkan untuk keperluan edukasi dalam rangka **Capstone Coding Camp 2026**.