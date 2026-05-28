# 🚀 Panduan Deploy ML Service ke Railway

## Prasyarat
- [x] Akun Railway (sudah terverifikasi)
- [ ] Repository GitHub (sudah push code terbaru)
- [ ] `best_model.keras` dan `tokenizer.joblib` ada di `ml-service/`

---

## Step 1: Pastikan File Ter-commit

```bash
# Di root project
cd skillscout-nusantara

# Cek file ml-service yang akan di-deploy
git status ml-service/

# Add semua perubahan ml-service
git add ml-service/
git add .gitignore

# Commit
git commit -m "feat: update ml-service v2.0 - joblib tokenizer, normalize_skills, CORS"

# Push
git push origin main
```

**Verifikasi:**
```bash
# Pastikan file model ter-commit (HARUS ada output)
git ls-files ml-service/best_model.keras
git ls-files ml-service/tokenizer.joblib
git ls-files ml-service/main.py
git ls-files ml-service/Dockerfile
git ls-files ml-service/railway.toml
```

> ⚠️ Jika `best_model.keras` tidak muncul, cek `.gitignore` — pastikan ada baris `!ml-service/best_model.keras`

---

## Step 2: Buat Project di Railway

1. Buka [railway.app](https://railway.app) → Login
2. Klik **"New Project"**
3. Pilih **"Deploy from GitHub Repo"**
4. Authorize Railway mengakses GitHub (jika belum)
5. Pilih repository `skillscout-nusantara`

![Railway New Project](# "Klik Deploy from GitHub Repo")

---

## Step 3: Konfigurasi Root Directory

Railway akan mencoba build dari root. Kita perlu set ke `ml-service/`:

1. Klik service yang baru dibuat
2. Pergi ke **Settings** tab
3. Scroll ke **"Source"** section
4. Set **"Root Directory"** → ketik: `ml-service`
5. Railway otomatis detect `Dockerfile` dan `railway.toml`

---

## Step 4: Set Environment Variables

Pergi ke **Variables** tab, klik **"New Variable"** untuk tiap item:

| Variable | Value | Keterangan |
|----------|-------|------------|
| `MODEL_PATH` | `best_model.keras` | Path relatif ke model file |
| `TOKENIZER_PATH` | `tokenizer.joblib` | Path relatif ke tokenizer |
| `MAX_LENGTH` | `256` | Sequence length (harus 256) |
| `BATCH_SIZE` | `32` | Ukuran batch prediksi |
| `ALLOWED_ORIGINS` | `https://skillscout-nusantara-7kxc.vercel.app,https://skillscout-nusantara.vercel.app` | CORS origins |

> 💡 `PORT` **tidak perlu di-set** — Railway otomatis set variabel ini.

---

## Step 5: Generate Public Domain

1. Di service → **Settings** tab
2. Scroll ke **"Networking"** section
3. Klik **"Generate Domain"**
4. Railway akan memberi URL, misalnya:
   ```
   https://skillscout-ml-production-a1b2.up.railway.app
   ```
5. **📋 Catat URL ini!** Dibutuhkan untuk integrasi backend.

---

## Step 6: Trigger Deploy

- Railway biasanya auto-deploy setelah setup
- Jika belum, klik **"Deploy"** di Deployments tab
- **Tunggu 3-5 menit** untuk build + startup

### Monitor Build
1. Pergi ke **Deployments** tab
2. Klik deployment terbaru
3. Lihat **Build Logs** — harus success:
   ```
   Step 1/10: FROM python:3.11-slim AS builder
   ...
   Successfully built abc123
   ```

### Monitor Runtime
4. Setelah build selesai, lihat **Deploy Logs**:
   ```
   📦 Loading model dari 'best_model.keras'...
   ✅ Model loaded: siamese_bilstm
   📦 Loading tokenizer dari 'tokenizer.joblib'...
   ✅ Tokenizer loaded (vocab: 153 words)
   🚀 ML Service ready | model_loaded=True
   ```

---

## Step 7: Verifikasi Deployment

### Via Browser
Buka di browser:
- **Swagger UI:** `https://YOUR-URL.up.railway.app/docs`
- **Health Check:** `https://YOUR-URL.up.railway.app/health`
- **Model Info:** `https://YOUR-URL.up.railway.app/model-info`

### Via Command Line
```bash
# Health check
curl https://YOUR-URL.up.railway.app/health

# Expected response:
# {
#   "status": "ok",
#   "service": "skillscout-ml",
#   "version": "2.0.0",
#   "model_loaded": true,
#   ...
# }

# Test inference (opsional)
curl -X POST https://YOUR-URL.up.railway.app/rank \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "curriculum vitae python sql machine learning data analysis",
    "jobs": [
      {
        "id": "test-1",
        "title": "Data Analyst",
        "company": "PT Test",
        "description": "Menganalisis data menggunakan python dan sql",
        "skills": ["python", "sql", "tableau"]
      }
    ],
    "top_k": 5
  }'
```

---

## Step 8: Hubungkan dengan Backend (Vercel)

### 8a. Set Environment Variable di Vercel

1. Login ke [vercel.com](https://vercel.com)
2. Buka project **backend** (atau project yang memuat `backend/`)
3. **Settings** → **Environment Variables**
4. Tambah/Edit:

| Key | Value |
|-----|-------|
| `ML_SERVICE_URL` | `https://YOUR-RAILWAY-URL.up.railway.app` |
| `ML_SERVICE_TIMEOUT` | `60` |

5. Klik **Save**

### 8b. Redeploy Backend

1. Di Vercel dashboard → **Deployments** tab
2. Klik **"..."** → **"Redeploy"**
3. Tunggu deployment selesai

### 8c. Test End-to-End

```bash
# Test backend health
curl https://skillscout-nusantara.vercel.app/api/health

# Test trends (proxy ke ML service)
curl https://skillscout-nusantara.vercel.app/api/match/trends

# Test matching (butuh CV dan jobs di database)
# Upload CV dulu via frontend, lalu test matching
```

---

## Troubleshooting

### ❌ Build Error: "Out of Memory"
- Railway free tier: 512MB RAM
- TensorFlow butuh ~400MB
- **Solusi:** Upgrade ke Hobby plan ($5/bulan) atau gunakan `tensorflow-cpu`

### ❌ Deploy Timeout
- Model loading butuh 30-60 detik
- `healthcheckTimeout` sudah set ke 180 detik
- **Solusi:** Jika masih timeout, naikkan di `railway.toml`

### ❌ Model tidak ter-commit (file terlalu besar)
- GitHub default limit: 100MB per file
- `best_model.keras` = 14MB → **aman**
- **Jika terlalu besar:** Gunakan Git LFS:
  ```bash
  git lfs install
  git lfs track "ml-service/best_model.keras"
  git add .gitattributes
  git add ml-service/best_model.keras
  git commit -m "feat: add model via LFS"
  ```

### ❌ CORS Error dari Frontend
- Pastikan `ALLOWED_ORIGINS` di Railway include domain frontend
- Contoh: `https://skillscout-nusantara-7kxc.vercel.app`
- Jangan tambah trailing slash!

---

## Ringkasan URL Setelah Deploy

| Service | URL | Platform |
|---------|-----|----------|
| Frontend | https://skillscout-nusantara-7kxc.vercel.app | Vercel |
| Backend API | https://skillscout-nusantara.vercel.app | Vercel |
| ML Service | https://YOUR-RAILWAY-URL.up.railway.app | Railway |
| ML API Docs | https://YOUR-RAILWAY-URL.up.railway.app/docs | Railway |
| ML Health | https://YOUR-RAILWAY-URL.up.railway.app/health | Railway |
