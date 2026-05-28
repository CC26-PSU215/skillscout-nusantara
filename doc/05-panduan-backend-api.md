# 🔌 Panduan Backend API — SkillScout Nusantara

## Base URL

- **Development:** `http://localhost:8000`
- **Production:** `https://skillscout-api.vercel.app` (atau domain Anda)
- **API Docs (Swagger):** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`

---

## Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{ "status": "ok", "service": "skillscout-api" }
```

---

### CV Upload

```http
POST /api/cv/upload
Content-Type: multipart/form-data
```

**Body:** `file` — PDF file (maks 5 MB)

**Response (201):**
```json
{
  "id": "uuid-v4",
  "filename": "cv_bagus.pdf",
  "storage_path": "cv-uploads/uuid.pdf",
  "skills": ["python", "react", "machine learning", "docker"],
  "uploaded_at": "2026-05-23T14:30:00Z"
}
```

**Errors:**
- `400` — Bukan file PDF
- `413` — File > 5 MB

---

### Get CV Detail

```http
GET /api/cv/{cv_id}
```

**Response (200):** Sama format dengan upload response.

**Errors:**
- `404` — CV tidak ditemukan

---

### List Jobs

```http
GET /api/jobs?page=1&per_page=20&location=Jakarta&skill=python&search=data
```

**Query Parameters:**

| Param | Type | Default | Deskripsi |
|-------|------|---------|-----------|
| `page` | int | 1 | Nomor halaman |
| `per_page` | int | 20 | Item per halaman (1-100) |
| `location` | string | null | Filter lokasi (ILIKE) |
| `skill` | string | null | Filter skill (JSONB contains) |
| `search` | string | null | Pencarian judul/perusahaan |

**Response (200):**
```json
{
  "total": 823,
  "page": 1,
  "per_page": 20,
  "data": [
    {
      "id": "uuid",
      "title": "Data Analyst",
      "company": "Gojek",
      "description": "...",
      "skills": ["python", "sql", "tableau"],
      "location": "Jakarta",
      "source_url": "https://glints.com/...",
      "scraped_at": "2026-05-20T10:00:00Z"
    }
  ]
}
```

---

### Get Job Detail

```http
GET /api/jobs/{job_id}
```

**Response (200):** Satu `JobResponse` object.

---

### Create Job

```http
POST /api/jobs
Content-Type: application/json
```

**Body:**
```json
{
  "title": "Frontend Developer",
  "company": "Tokopedia",
  "description": "...",
  "skills": ["react", "typescript", "nextjs"],
  "location": "Jakarta",
  "source_url": "https://..."
}
```

**Response (201):** `JobResponse` object.

---

### Match CV to Jobs

```http
POST /api/match
Content-Type: application/json
```

**Body:**
```json
{
  "cv_id": "uuid-dari-upload",
  "top_k": 10
}
```

**Response (200):**
```json
{
  "cv_id": "uuid",
  "results": [
    {
      "job_id": "uuid",
      "title": "Data Scientist",
      "company": "Gojek",
      "score": 0.8756,
      "matched_skills": ["python", "machine learning", "pandas"],
      "gap_skills": ["spark", "airflow"]
    }
  ]
}
```

**Logika Matching:**
1. Ambil CV dari database
2. Ambil semua jobs dari database
3. Coba panggil ML Service (`POST /rank`)
4. Jika ML Service gagal → fallback ke local TF-IDF matcher
5. Log hasil ke `match_logs` table

---

### Skill Trends

```http
GET /api/match/trends
```

**Response (200):**
```json
{
  "period": "2026-Q3",
  "trends": [
    {
      "skill": "python",
      "current_demand": 0.85,
      "predicted_demand": 0.90,
      "growth_pct": 5.88
    }
  ]
}
```

**Errors:**
- `503` — ML Service tidak tersedia

---

## Arsitektur Backend

```
backend/
├── app/
│   ├── main.py              # FastAPI app + router mounting
│   ├── config.py            # pydantic-settings (.env loader)
│   ├── database.py          # SQLAlchemy async session
│   │
│   ├── db/
│   │   └── models.py        # ORM: Job, CVUpload, MatchLog
│   ├── models/
│   │   └── schemas.py       # Pydantic: request/response schemas
│   │
│   ├── routers/
│   │   ├── cv.py            # /api/cv endpoints
│   │   ├── jobs.py          # /api/jobs endpoints
│   │   └── match.py         # /api/match endpoints
│   │
│   └── services/
│       ├── cv_parser.py     # PDF parsing + skill extraction
│       ├── matcher.py       # TF-IDF local matcher (fallback)
│       └── storage.py       # Supabase storage upload
│
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel serverless config
└── api/
    └── index.py             # Vercel entry point
```

## Cara Menjalankan

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
