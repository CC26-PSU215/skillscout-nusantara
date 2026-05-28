# 📦 SkillScout ML Service — Dokumentasi

## Daftar Isi
- [Overview](#overview)
- [Arsitektur Model](#arsitektur-model)
- [File Structure](#file-structure)
- [Deployment ke Railway](#deployment-ke-railway)
- [Integrasi dengan Backend](#integrasi-dengan-backend)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---

## Overview

ML Service adalah **microservice terpisah** yang menjalankan model Deep Learning (Siamese BiLSTM) untuk mencocokkan CV dengan lowongan kerja. Service ini di-deploy ke **Railway** karena Vercel tidak mendukung proses long-running yang dibutuhkan TensorFlow.

**Arsitektur Deployment:**
```
┌──────────────────┐      ┌────────────────────┐      ┌──────────────────┐
│   Frontend       │      │    Backend          │      │   ML Service     │
│   (Next.js)      │─────▶│    (FastAPI)         │─────▶│   (FastAPI+TF)   │
│   Vercel         │      │    Vercel            │      │   Railway        │
└──────────────────┘      └────────────────────┘      └──────────────────┘
                                │                            │
                                ▼                            ▼
                          ┌──────────┐              ┌──────────────┐
                          │PostgreSQL│              │best_model    │
                          │Supabase  │              │.keras (14MB) │
                          └──────────┘              │tokenizer     │
                                                    │.joblib (2KB) │
                                                    └──────────────┘
```

**Kenapa terpisah dari Vercel?**
- Vercel serverless functions timeout setelah 10-60 detik
- TensorFlow membutuhkan ~500MB RAM dan startup 30-60 detik
- Model harus persistent di memory (tidak bisa cold start setiap request)

---

## Arsitektur Model

### Siamese BiLSTM

```
cv_input  (None, 256) ──┐
                         ├── shared encoder "skillscout_nusantara"
job_input (None, 256) ──┘     ├── Embedding(10000, 300, mask_zero=True)
                              ├── Bidirectional LSTM(128, return_sequences=True)
                              ├── Bidirectional LSTM(64,  return_sequences=False)
                              ├── Dense(64, relu)
                              ├── Dropout(0.2)
                              └── L2 Normalize (Lambda)
                         ↓
                    Dot product (cosine similarity)
                         ↓
                    similarity score (0-1)
```

**Training Details:**
- **Data:** 501 CV × 501 Job (188,784 pairs, balanced positive/negative)
- **Loss:** MSE (regression pada Jaccard score)
- **Optimizer:** Adam (lr=0.001)
- **Epochs trained:** 9 (early stopping)
- **Best val MAE:** 0.0169 (target ≤ 0.02 ✅)
- **ROC-AUC:** 0.9997

**Fallback:** Jika model tidak tersedia, service otomatis fallback ke TF-IDF + Cosine Similarity + Skill Overlap scoring.

---

## File Structure

```
ml-service/
├── main.py              # FastAPI app (inference, endpoints, fallback)
├── best_model.keras     # Trained Siamese BiLSTM model (~14 MB)
├── tokenizer.joblib     # Keras Tokenizer (vocab 10000, dari ai/model.ipynb)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Multi-stage Docker build
├── railway.toml         # Railway deployment config
└── .dockerignore        # Files excluded from Docker build
```

### Perubahan dari versi sebelumnya:
| Sebelum | Sesudah | Alasan |
|---------|---------|--------|
| `tokenizer.pkl` (pickle) | `tokenizer.joblib` (joblib) | Konsisten dengan format export `ai/model.ipynb` |
| `tokenizer_compat.py` (StandaloneTokenizer) | Dihapus | Tidak diperlukan, langsung pakai Keras Tokenizer |
| Tanpa `normalize_skills()` | Dengan `normalize_skills()` | Preprocessing harus identik dengan training |
| Tanpa CORS | Dengan CORS middleware | Diperlukan untuk cross-origin requests |
| Version 1.0.0 | Version 2.0.0 | Major update |

---

## Deployment ke Railway

### Prasyarat
1. Akun [Railway](https://railway.app) (sudah terverifikasi)
2. Repository GitHub (sudah push code terbaru)
3. File `best_model.keras` dan `tokenizer.joblib` ada di folder `ml-service/`

### Langkah-langkah

#### 1. Push ke GitHub
```bash
cd skillscout-nusantara
git add ml-service/
git commit -m "feat: update ml-service v2.0 - joblib tokenizer, normalize_skills, CORS"
git push origin main
```

> ⚠️ **PENTING:** Pastikan `best_model.keras` (~14MB) dan `tokenizer.joblib` (~2KB) ter-commit.
> Cek: `git ls-files ml-service/` harus menampilkan kedua file tersebut.

#### 2. Buat Project di Railway
1. Login ke [railway.app](https://railway.app)
2. Klik **"New Project"** → **"Deploy from GitHub Repo"**
3. Pilih repository `skillscout-nusantara`
4. Railway akan auto-detect repo

#### 3. Konfigurasi Service
1. Di Railway dashboard, klik service yang baru dibuat
2. Pergi ke **Settings** tab:
   - **Root Directory:** `ml-service`
   - **Builder:** Dockerfile (otomatis terdeteksi dari `railway.toml`)

3. Pergi ke **Variables** tab, tambahkan:
   ```
   MODEL_PATH=best_model.keras
   TOKENIZER_PATH=tokenizer.joblib
   MAX_LENGTH=256
   BATCH_SIZE=32
   ALLOWED_ORIGINS=https://skillscout-nusantara-7kxc.vercel.app,https://skillscout-nusantara.vercel.app
   ```

#### 4. Generate Domain
1. Di **Settings** → **Networking** → **Generate Domain**
2. Railway akan memberi URL seperti: `https://skillscout-ml-production-xxxx.up.railway.app`
3. **Catat URL ini** — dibutuhkan untuk integrasi backend

#### 5. Deploy
- Railway akan otomatis build dan deploy setelah konfigurasi selesai
- Monitor di **Deployments** tab
- Tunggu sampai status **"Active"** (biasanya 3-5 menit)

#### 6. Verifikasi
Buka browser atau gunakan curl:
```bash
# Health check
curl https://YOUR-RAILWAY-URL.up.railway.app/health

# Model info
curl https://YOUR-RAILWAY-URL.up.railway.app/model-info

# API docs
# Buka: https://YOUR-RAILWAY-URL.up.railway.app/docs
```

Response health yang benar:
```json
{
  "status": "ok",
  "service": "skillscout-ml",
  "version": "2.0.0",
  "model_loaded": true,
  "model_name": "siamese_bilstm",
  "tokenizer_loaded": true,
  "tokenizer_vocab": 153,
  "max_length": 256
}
```

### Monitoring
- **Logs:** Railway dashboard → service → **Logs** tab
- **Metrics:** Railway dashboard → service → **Metrics** tab (CPU, RAM, Network)
- **Alerts:** Jika health check gagal 3x berturut-turut, Railway auto-restart

---

## Integrasi dengan Backend

Setelah ML service berhasil di-deploy ke Railway, hubungkan dengan backend Vercel.

### Langkah 1: Update Environment Variable di Vercel

1. Login ke [vercel.com](https://vercel.com)
2. Buka project **backend** (`skillscout-nusantara`)
3. Pergi ke **Settings** → **Environment Variables**
4. Tambahkan/Update:
   ```
   ML_SERVICE_URL = https://YOUR-RAILWAY-URL.up.railway.app
   ML_SERVICE_TIMEOUT = 60
   ```
5. Klik **Save**

### Langkah 2: Redeploy Backend

1. Di Vercel dashboard → **Deployments** tab
2. Klik **"..."** pada deployment terakhir → **"Redeploy"**
3. Atau push perubahan ke GitHub (auto-deploy)

### Langkah 3: Verifikasi Integrasi

```bash
# Test dari backend → ML service
curl https://skillscout-nusantara.vercel.app/api/health

# Test matching endpoint (butuh CV dan jobs di database)
curl -X POST https://skillscout-nusantara.vercel.app/api/match \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "YOUR_CV_ID", "top_k": 5}'

# Test trends (proxy ke ML service)
curl https://skillscout-nusantara.vercel.app/api/match/trends
```

### Bagaimana Flow Kerjanya

```
1. User upload CV di Frontend
   └─▶ POST /api/cv/upload → Backend
       └─▶ Ekstrak teks (pdfplumber)
       └─▶ Ekstrak skills (NLP)
       └─▶ Simpan ke PostgreSQL
       └─▶ Return cv_id

2. User klik "Match"
   └─▶ POST /api/match → Backend
       └─▶ Ambil CV dari DB
       └─▶ Ambil semua Jobs dari DB
       └─▶ Kirim ke ML Service (Railway):
           POST https://railway-url/rank
           Body: { cv_text, jobs[], top_k }
       └─▶ ML Service:
           - Normalize skills
           - Tokenize (joblib tokenizer)
           - Batch predict (Siamese BiLSTM)
           - Return ranked results
       └─▶ Jika ML Service error → Fallback TF-IDF lokal
       └─▶ Log hasil ke match_logs table
       └─▶ Return results ke Frontend

3. Frontend tampilkan hasil matching
   └─▶ Score, matched skills, skill gap
```

### Kode Backend yang Relevan

File `backend/app/config.py` — config ML service URL:
```python
# ── ML Service ──────────────────────────────────────
ml_service_url: str = "http://localhost:8001"  # Override via env var
ml_service_timeout: int = 30
```

File `backend/app/routers/match.py` — panggil ML service:
```python
async def _call_ml_service(cv_text, jobs, top_k):
    payload = {
        "cv_text": cv_text,
        "jobs": [{"id": j.id, "title": j.title, ...} for j in jobs],
        "top_k": top_k,
    }
    async with httpx.AsyncClient(timeout=settings.ml_service_timeout) as client:
        resp = await client.post(f"{settings.ml_service_url}/rank", json=payload)
        resp.raise_for_status()
        return resp.json()["results"]
```

---

## API Reference

### `POST /rank` — Ranking Lowongan

Mencocokkan teks CV dengan daftar lowongan, mengembalikan top-K hasil terurut.

**Request:**
```json
{
  "cv_text": "curriculum vitae ringkas nama rian setiawan...",
  "jobs": [
    {
      "id": "uuid-1",
      "title": "Data Analyst",
      "company": "PT Maju Jaya",
      "description": "Menganalisis data...",
      "skills": ["python", "sql", "tableau"]
    }
  ],
  "top_k": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "job_id": "uuid-1",
      "title": "Data Analyst",
      "company": "PT Maju Jaya",
      "score": 0.8542,
      "matched_skills": ["python", "sql"],
      "gap_skills": ["tableau"]
    }
  ],
  "model_used": "siamese_bilstm"
}
```

`model_used` bisa `"siamese_bilstm"` (deep learning) atau `"tfidf_fallback"` (jika model gagal load).

---

### `GET /trends` — Prediksi Tren Skill

**Response:**
```json
{
  "period": "2026-Q2",
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

---

### `GET /health` — Health Check

**Response:**
```json
{
  "status": "ok",
  "service": "skillscout-ml",
  "version": "2.0.0",
  "model_loaded": true,
  "model_name": "siamese_bilstm",
  "tokenizer_loaded": true,
  "tokenizer_vocab": 153,
  "max_length": 256
}
```

---

### `GET /model-info` — Detail Model

Menampilkan arsitektur, konfigurasi, dan training metrics model.

---

## Troubleshooting

### Model tidak load di Railway
**Gejala:** `health` menampilkan `"model_loaded": false`

**Solusi:**
1. Cek log Railway → apakah ada error saat startup
2. Pastikan `best_model.keras` ter-commit ke Git:
   ```bash
   git ls-files ml-service/best_model.keras
   ```
3. Pastikan file tidak masuk `.gitignore`
4. Pastikan RAM cukup (minimum 512MB, rekomendsai 1GB)

### Railway build gagal
**Gejala:** Deployment error di Railway

**Solusi:**
1. Cek log build → biasanya dependency conflict
2. Pastikan `requirements.txt` benar
3. Coba hapus version constraint yang terlalu ketat
4. Pastikan `Dockerfile` dan `railway.toml` ada di `ml-service/`

### Backend tidak bisa connect ke ML service
**Gejala:** Matching selalu fallback ke TF-IDF

**Solusi:**
1. Cek env var `ML_SERVICE_URL` di Vercel sudah benar
2. Pastikan URL Railway **tidak** diakhiri `/` (trailing slash)
3. Cek CORS: `ALLOWED_ORIGINS` harus include domain Vercel
4. Test langsung: `curl https://YOUR-RAILWAY-URL/health`
5. Cek timeout: naikkan `ML_SERVICE_TIMEOUT` ke 60 detik

### Prediksi score selalu 0 atau sangat rendah
**Gejala:** Semua matching score mendekati 0

**Solusi:**
1. Pastikan `normalize_skills()` di ml-service identik dengan yang di `ai/model.ipynb`
2. Pastikan `tokenizer.joblib` berasal dari training yang sama dengan `best_model.keras`
3. Cek input: teks CV dan job description harus non-empty

### Railway free tier kehabisan credit
**Gejala:** Service berhenti berjalan

**Solusi:**
1. Railway free tier: $5/bulan (cukup untuk ML service)
2. Monitor usage di Railway dashboard → **Usage** tab
3. Optimasi: kurangi `--workers` ke 1, gunakan `--timeout-keep-alive 30`
