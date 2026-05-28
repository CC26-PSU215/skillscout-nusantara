# 🚂 Panduan Deploy ke Railway — SkillScout Nusantara

> **Dokumen ini** berisi panduan lengkap deploy **backend + ML service** ke Railway.
> Railway dipilih karena mendukung **long-running processes** (bukan serverless),
> sehingga cocok untuk model TensorFlow yang butuh waktu load lama.

---

## Daftar Isi

1. [Kenapa Railway, Bukan Vercel?](#1-kenapa-railway-bukan-vercel)
2. [Arsitektur Deploy](#2-arsitektur-deploy)
3. [Persiapan Sebelum Deploy](#3-persiapan-sebelum-deploy)
4. [Deploy ML Service](#4-deploy-ml-service-ke-railway)
5. [Deploy Backend API](#5-deploy-backend-api-ke-railway)
6. [Menghubungkan Frontend (Vercel)](#6-menghubungkan-frontend-vercel)
7. [Environment Variables Lengkap](#7-environment-variables-lengkap)
8. [Monitoring & Troubleshooting](#8-monitoring--troubleshooting)
9. [Estimasi Biaya](#9-estimasi-biaya)
10. [Checklist Deploy](#10-checklist-deploy)

---

## 1. Kenapa Railway, Bukan Vercel?

### ❌ Masalah Vercel untuk Backend + ML

| Masalah | Penjelasan |
|---------|-----------|
| **Serverless timeout** | Vercel Functions max 10 detik (free) / 60 detik (pro). Model TF load butuh ~30 detik. |
| **Cold start** | Setiap request bisa kena cold start → TensorFlow harus load ulang dari nol. |
| **Memory limit** | Vercel Functions max 1024 MB. TensorFlow + model = ~800 MB RAM. |
| **No persistent process** | Tidak bisa keep model di memory. Setiap invocation = proses baru. |
| **File system read-only** | Tidak bisa write `tokenizer.pkl` atau cache apapun. |

### ✅ Kenapa Railway Cocok

| Keunggulan | Penjelasan |
|-----------|-----------|
| **Always-on container** | Model di-load SEKALI saat startup, tetap di memory. |
| **Flexible resources** | Bisa atur RAM hingga 8 GB, CPU hingga 8 vCPU. |
| **Docker support** | Deploy via Dockerfile → kontrol penuh atas environment. |
| **Auto-deploy** | Push ke GitHub → auto build & deploy. |
| **Custom domain** | Gratis subdomain `*.railway.app` + support custom domain. |
| **Free tier** | $5 credit/bulan gratis (cukup untuk development). |

### 📐 Strategi Hybrid Deploy

```
Frontend (Vercel) ← gratis, CDN global, cocok untuk Next.js
    │
    │ NEXT_PUBLIC_API_URL
    ▼
Backend API (Railway) ← always-on, bisa akses DB lama
    │
    │ ML_SERVICE_URL
    ▼
ML Service (Railway) ← always-on, model di memory
    │
    └── Supabase (managed DB + Storage)
```

> **Frontend tetap di Vercel** karena Next.js sangat optimal di sana.
> **Backend + ML pindah ke Railway** untuk menghindari semua limitasi serverless.

---

## 2. Arsitektur Deploy

```
                    ┌─────────────────────┐
                    │   Vercel (Free)      │
                    │   Next.js Frontend   │
                    │   Port: 443 (HTTPS)  │
                    └──────────┬──────────┘
                               │ API calls
                               ▼
┌──────────────────────────────────────────────────┐
│                Railway Project                     │
│                                                    │
│  ┌──────────────────┐    ┌──────────────────────┐ │
│  │ Service 1:       │    │ Service 2:            │ │
│  │ Backend API      │───→│ ML Service            │ │
│  │ (FastAPI)        │    │ (TensorFlow)          │ │
│  │ Port: $PORT      │    │ Port: $PORT           │ │
│  │ RAM: ~256 MB     │    │ RAM: ~1 GB            │ │
│  └────────┬─────────┘    └───────────────────────┘ │
│            │                                        │
└────────────┼────────────────────────────────────────┘
             │
             ▼
    ┌─────────────────────┐
    │ Supabase (Managed)  │
    │ PostgreSQL + Storage│
    └─────────────────────┘
```

Railway mendukung **multiple services dalam 1 project**.
Setiap service punya URL sendiri dan bisa berkomunikasi via internal network.

---

## 3. Persiapan Sebelum Deploy

### 3.1 Install Railway CLI (opsional, tapi recommended)

```bash
# macOS / Linux
curl -fsSL https://railway.com/install.sh | sh

# Atau via npm
npm install -g @railway/cli

# Login
railway login
```

### 3.2 Pastikan File Model Ada

```bash
# Di folder ai/, jalankan export tokenizer:
cd ai/
pip install tensorflow pandas
python export_tokenizer.py

# Verifikasi file:
ls -la ai/tokenizer.pkl          # harus ada
ls -la ai/best_model.keras       # harus ada (~14 MB)
ls -la ml-service/tokenizer.pkl  # harus ada (di-copy otomatis)
```

> ⚠️ **PENTING:** File `tokenizer.pkl` HARUS ada sebelum deploy.
> Tanpa tokenizer, ML service akan fallback ke TF-IDF (bukan deep learning).

### 3.3 Copy Model ke ml-service

```bash
# Copy model file
cp ai/best_model.keras ml-service/best_model.keras

# Verifikasi
ls -la ml-service/
# Harus ada:
#   main.py
#   requirements.txt
#   Dockerfile
#   railway.toml
#   best_model.keras    (~14 MB)
#   tokenizer.pkl       (~500 KB)
```

### 3.4 Push ke GitHub

```bash
# Pastikan .gitignore TIDAK mengabaikan file model di ml-service
# Tapi ABAIKAN file model di ai/ (terlalu besar untuk commit berulang)

git add ml-service/
git add backend/
git commit -m "feat: prepare for Railway deployment"
git push origin main
```

> **Catatan .gitignore:** Jika `*.keras` dan `*.pkl` ada di `.gitignore` global,
> tambahkan exception:
> ```gitignore
> # Allow model files in ml-service
> !ml-service/best_model.keras
> !ml-service/tokenizer.pkl
> ```

---

## 4. Deploy ML Service ke Railway

### Cara 1: Via Railway Dashboard (Recommended untuk pertama kali)

#### Step 1 — Buat Project

1. Buka [railway.app/new](https://railway.app/new)
2. Klik **"Deploy from GitHub Repo"**
3. Pilih repo `skillscout-nusantara`
4. Railway akan detect monorepo → pilih **"Configure"**

#### Step 2 — Buat Service "ML"

1. Klik **"New Service"** → **"GitHub Repo"**
2. Pilih repo yang sama
3. Di tab **Settings**:
   - **Root Directory:** `ml-service`
   - **Builder:** Dockerfile (otomatis detect dari `railway.toml`)
4. Di tab **Variables**, tambahkan:
   ```
   PORT=8001
   MODEL_PATH=best_model.keras
   TOKENIZER_PATH=tokenizer.pkl
   MAX_LENGTH=256
   BATCH_SIZE=32
   ```
5. Di tab **Networking**:
   - Klik **"Generate Domain"** → akan mendapat URL seperti:
     `ml-service-production-xxxx.up.railway.app`
6. Klik **"Deploy"**

#### Step 3 — Verifikasi

```bash
# Ganti URL dengan yang dari Railway
curl https://ml-service-production-xxxx.up.railway.app/health

# Response yang diharapkan:
{
  "status": "ok",
  "service": "skillscout-ml",
  "model_loaded": true,
  "model_name": "siamese_bilstm",
  "tokenizer_loaded": true,
  "max_length": 256
}
```

### Cara 2: Via Railway CLI

```bash
cd ml-service

# Init project
railway init

# Link ke service
railway link

# Set environment variables
railway variables set PORT=8001
railway variables set MODEL_PATH=best_model.keras
railway variables set TOKENIZER_PATH=tokenizer.pkl
railway variables set MAX_LENGTH=256

# Deploy
railway up

# Cek logs
railway logs
```

---

## 5. Deploy Backend API ke Railway

### Step 1 — Buat Service "Backend" dalam Project yang Sama

1. Di Railway project yang sudah dibuat, klik **"New Service"** → **"GitHub Repo"**
2. Pilih repo yang sama
3. **Settings:**
   - **Root Directory:** `backend`
   - **Builder:** Nixpacks (auto-detect Python)
4. **Start Command** (override di Settings → Deploy):
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Step 2 — Set Environment Variables

Di tab **Variables**, tambahkan SEMUA variable berikut:

```env
# Database — Supabase Connection Pooler
DATABASE_URL=postgresql+asyncpg://postgres.ktoyprdosloxelbsclkj:PASSWORD@aws-1-ap-south-1.pooler.supabase.com:6543/postgres

# Supabase Storage
SUPABASE_URL=https://ktoyprdosloxelbsclkj.supabase.co
SUPABASE_SERVICE_KEY=eyJ...your_key...
SUPABASE_BUCKET=cv-uploads

# ML Service — gunakan INTERNAL URL dari Railway
ML_SERVICE_URL=http://ml-service.railway.internal:8001

# CORS — izinkan domain Vercel + localhost
CORS_ORIGINS=["https://skillscout-nusantara.vercel.app","http://localhost:3000"]

# Upload
MAX_CV_SIZE_MB=5
```

> 💡 **Tips Internal Networking:**
> Railway service dalam 1 project bisa saling akses via **private network**:
> `http://<service-name>.railway.internal:<port>`
>
> Ini JAUH lebih cepat dan aman daripada via public URL.
> Untuk ML service, gunakan: `http://ml-service.railway.internal:8001`
>
> Jika service name kamu berbeda, cek di Railway Dashboard → service → Settings → Service Name.

### Step 3 — Generate Domain

1. Tab **Networking** → **"Generate Domain"**
2. URL: `backend-production-xxxx.up.railway.app`
3. Ini yang akan dipakai sebagai `NEXT_PUBLIC_API_URL` di frontend

### Step 4 — Verifikasi

```bash
curl https://backend-production-xxxx.up.railway.app/api/health
# → {"status": "ok", "service": "skillscout-api"}

curl https://backend-production-xxxx.up.railway.app/api/docs
# → Swagger UI
```

---

## 6. Menghubungkan Frontend (Vercel)

Frontend tetap di-deploy di Vercel — hanya perlu update env var.

### Step 1 — Update Vercel Environment Variable

1. Buka [vercel.com](https://vercel.com) → project `skillscout-nusantara`
2. **Settings** → **Environment Variables**
3. Ubah / tambahkan:
   ```
   NEXT_PUBLIC_API_URL=https://backend-production-xxxx.up.railway.app
   ```
4. Redeploy frontend

### Step 2 — Verifikasi End-to-End

1. Buka frontend di browser: `https://skillscout-nusantara.vercel.app`
2. Upload CV → harus berhasil
3. Browse Jobs → harus menampilkan data dari DB
4. Match → harus memberikan skor dan skill gap

### Alur Request Setelah Deploy

```
Browser (Vercel CDN)
    → GET /api/jobs
    → POST /api/cv/upload
    → POST /api/match
        ↓
Backend (Railway)
    → httpx POST http://ml-service.railway.internal:8001/rank
        ↓
ML Service (Railway, internal network)
    → model.predict() → return scores
        ↓
Backend
    → INSERT match_logs → Supabase
    → return results to Frontend
```

---

## 7. Environment Variables Lengkap

### ML Service (Railway)

| Variable | Wajib | Default | Deskripsi |
|----------|-------|---------|-----------|
| `PORT` | ✅ | `8001` | Railway auto-set |
| `MODEL_PATH` | ❌ | `best_model.keras` | Path ke model file |
| `TOKENIZER_PATH` | ❌ | `tokenizer.pkl` | Path ke tokenizer |
| `MAX_LENGTH` | ❌ | `256` | Max sequence length |
| `BATCH_SIZE` | ❌ | `32` | Batch size prediksi |

### Backend API (Railway)

| Variable | Wajib | Default | Deskripsi |
|----------|-------|---------|-----------|
| `DATABASE_URL` | ✅ | — | Supabase connection string |
| `SUPABASE_URL` | ✅ | — | URL Supabase project |
| `SUPABASE_SERVICE_KEY` | ✅ | — | Service role key |
| `SUPABASE_BUCKET` | ❌ | `cv-uploads` | Storage bucket name |
| `ML_SERVICE_URL` | ✅ | `http://localhost:8001` | URL ML service (gunakan internal) |
| `ML_SERVICE_TIMEOUT` | ❌ | `30` | Timeout panggil ML (detik) |
| `CORS_ORIGINS` | ✅ | `["http://localhost:3000"]` | JSON array origin |
| `MAX_CV_SIZE_MB` | ❌ | `5` | Max ukuran CV upload (MB) |

### Frontend (Vercel)

| Variable | Wajib | Deskripsi |
|----------|-------|-----------|
| `NEXT_PUBLIC_API_URL` | ✅ | URL backend Railway |

---

## 8. Monitoring & Troubleshooting

### Cek Logs

```bash
# Via CLI
railway logs --service ml-service
railway logs --service backend

# Via Dashboard
# Railway → Project → Service → Logs tab
```

### Masalah Umum

| Masalah | Penyebab | Solusi |
|---------|----------|-------|
| ML health: `model_loaded: false` | File `.keras` atau `.pkl` tidak ada | Pastikan file ter-copy ke `ml-service/` dan ter-commit |
| Backend 503 saat match | ML service belum ready | Tunggu ML startup (~30 detik). Cek health endpoint. |
| CORS error di browser | Origin frontend tidak di whitelist | Tambahkan URL Vercel ke `CORS_ORIGINS` |
| DB connection refused | `DATABASE_URL` salah | Cek connection string Supabase (harus `asyncpg`) |
| Build timeout | Image terlalu besar | Pastikan `.dockerignore` aktif. TF image ~1.5 GB (normal) |
| Memory crash | TF + model > RAM limit | Upgrade Railway plan atau gunakan `tensorflow-cpu` |
| Upload gagal | Supabase key expired/salah | Regenerate service key di Supabase dashboard |

### Health Check URLs

```
ML Service:  https://ml-xxx.up.railway.app/health
Backend:     https://backend-xxx.up.railway.app/api/health
Supabase:    https://xxx.supabase.co/rest/v1/ (via browser)
Frontend:    https://skillscout-nusantara.vercel.app
```

---

## 9. Estimasi Biaya

### Railway Pricing (per bulan)

| Plan | RAM | vCPU | Free Credit | Harga |
|------|-----|------|-------------|-------|
| **Trial** | 512 MB | shared | $5 | Gratis |
| **Hobby** | 8 GB | 8 vCPU | $5 | $5/bulan |
| **Pro** | 32 GB | 32 vCPU | — | $20/bulan |

### Estimasi Usage SkillScout

| Service | RAM Usage | CPU | Estimasi/bulan |
|---------|-----------|-----|---------------|
| ML Service | ~800 MB | 0.5 vCPU | ~$3 |
| Backend API | ~256 MB | 0.25 vCPU | ~$1.50 |
| **Total** | | | **~$4.50** |

> 💡 Dengan plan **Hobby ($5/bulan)**, kedua service muat dengan sisa credit.
> Untuk capstone demo/presentation saja, plan **Trial (gratis)** cukup.

### Vercel (Frontend)

- **Hobby Plan:** Gratis (100 GB bandwidth, unlimited deploys)
- Cukup untuk capstone project

### Supabase (Database)

- **Free Plan:** 500 MB database, 1 GB storage, 50K requests/bulan
- Cukup untuk capstone project

---

## 10. Checklist Deploy

### Pre-Deploy ✅

- [ ] `ai/export_tokenizer.py` dijalankan → `tokenizer.pkl` tercipta
- [ ] `best_model.keras` di-copy ke `ml-service/`
- [ ] `tokenizer.pkl` di-copy ke `ml-service/`
- [ ] `.gitignore` memiliki exception untuk `ml-service/*.keras` dan `ml-service/*.pkl`
- [ ] Supabase tables sudah dibuat (jalankan `001_init_tables.sql`)
- [ ] Supabase storage bucket `cv-uploads` sudah ada
- [ ] GitHub repo sudah push semua perubahan

### Railway Deploy ✅

- [ ] Railway project dibuat
- [ ] ML Service: root directory = `ml-service`, builder = Dockerfile
- [ ] ML Service: environment variables diset
- [ ] ML Service: domain di-generate
- [ ] ML Service: health check → `model_loaded: true`
- [ ] Backend: root directory = `backend`, start command diset
- [ ] Backend: environment variables diset (termasuk `ML_SERVICE_URL` internal)
- [ ] Backend: domain di-generate
- [ ] Backend: `/api/health` → `status: ok`
- [ ] Backend: `/api/docs` → Swagger UI bisa diakses

### Vercel + End-to-End ✅

- [ ] Vercel: `NEXT_PUBLIC_API_URL` diubah ke URL Railway backend
- [ ] Frontend: halaman bisa diakses
- [ ] Upload CV: berhasil upload + ekstrak skill
- [ ] Browse Jobs: data muncul dari database
- [ ] Match: skor matching + skill gap muncul
- [ ] Trends: data tren skill muncul

---

## Referensi

- [Railway Docs](https://docs.railway.com/)
- [Railway Monorepo Guide](https://docs.railway.com/guides/monorepo)
- [Railway Docker Deploy](https://docs.railway.com/guides/dockerfiles)
- [Railway Networking](https://docs.railway.com/reference/private-networking)
- [Railway CLI Reference](https://docs.railway.com/reference/cli-api)

---

> **Dibuat untuk:** Tim CC26-PSU215, SkillScout Nusantara
> **Terakhir diperbarui:** 26 Mei 2026
