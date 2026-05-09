# SkillScout Nusantara — Backend Project Setup Complete

## Struktur Folder Final

```
skillscout-backend/
├── api/
│   └── index.py              ← entry point Vercel (re-export app)
├── app/
│   ├── __init__.py
│   ├── main.py               ← FastAPI factory + CORS + router mount
│   ├── config.py             ← env vars via pydantic-settings
│   ├── database.py           ← async SQLAlchemy engine + get_db()
│   ├── db/
│   │   ├── __init__.py
│   │   └── models.py         ← ORM: Job, CVUpload, MatchLog
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py        ← Pydantic: request & response shapes
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── cv.py             ← POST /upload, GET /{cv_id}
│   │   ├── jobs.py           ← GET/POST /jobs (+ filter & pagination)
│   │   └── match.py          ← POST /match, GET /match/trends
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cv_parser.py      ← ekstraksi teks PDF + deteksi skill
│   │   ├── matcher.py        ← TF-IDF fallback matcher (lokal)
│   │   └── storage.py        ← upload PDF ke Supabase Storage
│   └── ml/
│       ├── __init__.py
│       └── placeholder.py    ← arsitektur TF Functional API (referensi)
├── migrations/
│   └── init.sql              ← DDL: jobs, cv_uploads, match_logs
├── tests/
│   ├── __init__.py
│   └── test_cv.py            ← test health + upload validation
├── .env.example              ← template environment variables
├── .gitignore
├── requirements.txt          ← semua dependencies (sudah terinstall)
└── vercel.json               ← konfigurasi routing Vercel
```

---

## Yang Sudah Dikerjakan

### 1. Config & Environment
| File | Isi |
|---|---|
| [config.py](file:///home/bagusjr/capstone/skillscout-backend/app/config.py) | `pydantic-settings` — memuat `DATABASE_URL`, Supabase creds, ML service URL, CORS origins, JWT settings |
| [.env.example](file:///home/bagusjr/capstone/skillscout-backend/.env.example) | Template semua env var yang dibutuhkan |

### 2. Database (Async PostgreSQL)
| File | Isi |
|---|---|
| [database.py](file:///home/bagusjr/capstone/skillscout-backend/app/database.py) | `create_async_engine` + `async_sessionmaker` + `get_db()` dependency dengan auto-commit/rollback |
| [models.py](file:///home/bagusjr/capstone/skillscout-backend/app/db/models.py) | SQLAlchemy 2.0 ORM — `Job`, `CVUpload`, `MatchLog` dengan relasi dan JSONB columns |
| [init.sql](file:///home/bagusjr/capstone/skillscout-backend/migrations/init.sql) | DDL langsung untuk Supabase — 3 tabel + GIN index pada skills |

### 3. API Endpoints (11 routes terdaftar)
| Route | File | Fungsi |
|---|---|---|
| `GET /api/health` | [main.py](file:///home/bagusjr/capstone/skillscout-backend/app/main.py) | Health check |
| `POST /api/cv/upload` | [cv.py](file:///home/bagusjr/capstone/skillscout-backend/app/routers/cv.py) | Upload PDF → Supabase → ekstrak skill |
| `GET /api/cv/{id}` | cv.py | Detail CV |
| `GET /api/jobs` | [jobs.py](file:///home/bagusjr/capstone/skillscout-backend/app/routers/jobs.py) | List + filter (location, skill, search) + pagination |
| `GET /api/jobs/{id}` | jobs.py | Detail lowongan |
| `POST /api/jobs` | jobs.py | Tambah lowongan (scraper/admin) |
| `POST /api/match` | [match.py](file:///home/bagusjr/capstone/skillscout-backend/app/routers/match.py) | Cocokkan CV ↔ jobs (ML service → fallback TF-IDF lokal) |
| `GET /api/match/trends` | match.py | Proxy ke ML service untuk tren skill |

### 4. Services
| File | Fungsi |
|---|---|
| [cv_parser.py](file:///home/bagusjr/capstone/skillscout-backend/app/services/cv_parser.py) | `pdfplumber` + gazetteer bilingual (ID/EN) + sinonim |
| [matcher.py](file:///home/bagusjr/capstone/skillscout-backend/app/services/matcher.py) | TF-IDF + cosine similarity (60%) + skill overlap (40%) |
| [storage.py](file:///home/bagusjr/capstone/skillscout-backend/app/services/storage.py) | Upload ke Supabase Storage bucket |

### 5. ML (Deep Learning — Checklist CC26-PSU215)
| File | Fungsi |
|---|---|
| [placeholder.py](file:///home/bagusjr/capstone/skillscout-backend/app/ml/placeholder.py) | Siamese model dengan **TensorFlow Functional API** — referensi arsitektur untuk AI Engineer |

> [!IMPORTANT]
> Model DL ini di-deploy terpisah di **Railway/Render** (bukan di Vercel). Backend Vercel hanya memanggil via HTTP (`POST /rank`, `GET /trends`). Fallback ke TF-IDF lokal jika ML service tidak tersedia.

### 6. Deploy (Vercel)
| File | Fungsi |
|---|---|
| [index.py](file:///home/bagusjr/capstone/skillscout-backend/api/index.py) | Re-export `app` dari `app.main` |
| [vercel.json](file:///home/bagusjr/capstone/skillscout-backend/vercel.json) | Route `/api/*` → `api/index.py` |

---

## Verifikasi

- ✅ `pip install -r requirements.txt` — semua 70+ packages terinstall
- ✅ `python -c "from app.main import app"` — app berhasil di-import, 11 routes terdaftar
- ✅ Struktur folder sesuai requirement Vercel (`api/index.py` sebagai entry point)

## Langkah Selanjutnya

1. **Isi `.env`** — salin `.env.example` → `.env`, isi credentials Supabase
2. **Jalankan `init.sql`** di Supabase SQL Editor untuk buat tabel
3. **Test lokal**: `uvicorn app.main:app --reload` → buka `/api/docs`
4. **AI Engineer**: kembangkan model DL di `app/ml/` menggunakan arsitektur di `placeholder.py`, ekspor ke `.keras`
5. **Deploy ML service** ke Railway/Render, set `ML_SERVICE_URL` di env
6. **Deploy backend** ke Vercel: `vercel --prod`
