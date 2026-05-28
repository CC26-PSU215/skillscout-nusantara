# 🚀 Panduan Deployment — SkillScout Nusantara

## Arsitektur Deployment

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│     Vercel       │    │ Railway / Render  │    │    Supabase    │
│   (Frontend +    │    │   (ML Service)    │    │  (DB + Storage)│
│    Backend)      │    │                   │    │                │
│   Next.js +      │    │   FastAPI +       │    │  PostgreSQL +  │
│   FastAPI        │    │   TensorFlow      │    │  File Storage  │
│   (Serverless)   │    │   (Container)     │    │                │
└────────┬────────┘    └────────┬──────────┘    └────────┬───────┘
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 │
                           Internet / VPC
```

---

## 1. Database (Supabase) — ✅ Sudah Aktif

### Credentials

```
Host: db.ktoyprdosloxelbsclkj.supabase.co
Pooler: aws-1-ap-south-1.pooler.supabase.com:6543
Database: postgres
Project URL: https://ktoyprdosloxelbsclkj.supabase.co
```

### Migrasi Database

```bash
# Jalankan SQL migration di Supabase SQL Editor:
# 1. backend/supabase/001_init_tables.sql
# 2. backend/supabase/002_create_bucket.sql
```

---

## 2. Backend (Vercel Serverless)

### File yang Diperlukan

**`backend/vercel.json`** (sudah ada):
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

**`backend/api/index.py`** (sudah ada):
Entry point yang mengimpor `app` dari `app.main`.

### Deploy ke Vercel

```bash
cd backend
vercel --prod

# Set environment variables di Vercel Dashboard:
# DATABASE_URL=postgresql+asyncpg://...
# SUPABASE_URL=https://...
# SUPABASE_SERVICE_KEY=eyJ...
# ML_SERVICE_URL=https://skillscout-ml-xxx.up.railway.app
# CORS_ORIGINS=["https://skillscout-nusantara.vercel.app"]
```

---

## 3. Frontend (Vercel)

### Deploy

```bash
cd frontend
vercel --prod

# Set environment variables:
# NEXT_PUBLIC_API_URL=https://skillscout-api.vercel.app
```

### Atau gabungkan dengan backend dalam satu Vercel project

Karena keduanya di Vercel, bisa di-monorepo:
```
Root Directory: frontend (untuk frontend deploy)
# Atau buat 2 Vercel projects terpisah
```

---

## 4. ML Service (Railway atau Render)

### Deploy ke Railway

```bash
cd ml-service

# Install Railway CLI
npm install -g @railway/cli

# Login & init
railway login
railway init

# Deploy
railway up

# Set environment variables di Railway Dashboard:
# PORT=8001
# Catat URL: https://skillscout-ml-xxx.up.railway.app
```

### Deploy ke Render

1. Push `ml-service/` ke GitHub
2. Buat **Web Service** baru di render.com
3. Settings:
   - **Root Directory:** `ml-service`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Docker:** Bisa pakai Dockerfile yang sudah ada

### Syarat ML Service

- `best_model.keras` harus ada di folder
- `tokenizer.pkl` harus ada di folder (ekspor dari notebook dulu!)
- Memory: minimal 512 MB RAM (TensorFlow butuh ~300 MB)

> ⚠️ **PENTING:** Jangan deploy jika akurasi masih 45%. Tingkatkan dulu ke 90% (lihat `03-peningkatan-akurasi-model.md`).

---

## 5. Docker Compose (Development Lokal)

```bash
# Jalankan semua services
docker-compose up --build

# Services:
# - db:       localhost:5432
# - backend:  localhost:8000
# - frontend: localhost:3000
# - ml:       localhost:8001

# Stop
docker-compose down

# Reset database
docker-compose down -v  # hapus volume
docker-compose up --build
```

---

## Checklist Pre-Deployment

- [ ] Database migration sudah dijalankan di Supabase
- [ ] Supabase Storage bucket `cv-uploads` sudah dibuat
- [ ] Backend `.env` berisi credentials yang benar
- [ ] Frontend `.env.local` berisi URL API yang benar
- [ ] ML model accuracy ≥ 85% (idealnya ≥ 90%)
- [ ] `tokenizer.pkl` sudah ada di `ml-service/`
- [ ] Backend health check OK (`/api/health`)
- [ ] ML Service health check OK (`/health`)
- [ ] CORS origins sudah disesuaikan untuk production domain
- [ ] Test upload CV → matching → tampilkan hasil E2E

---

## Monitoring Post-Deploy

### Vercel
- Dashboard: vercel.com → Logs → Function logs
- Errors: vercel.com → Errors tab

### Railway / Render
- Dashboard: Logs real-time
- Memory usage (TensorFlow bisa besar)
- Cold start time (~10-30 detik untuk TF)

### Supabase
- Dashboard: Database → Performance
- Storage usage
- Connection pooler (max connections)
