# SkillScout Nusantara — Integration & Deployment Plan

## Ringkasan Masalah

Saat ini ada **gap** antara:
- **`ai/` folder**: Model terbaru (Siamese BiLSTM, tokenizer via `joblib`, data 501 CV × 501 Job, menggunakan `extracted_skills_structured`)
- **`ml-service/`**: Menggunakan tokenizer lama (`tokenizer.pkl` via pickle + `StandaloneTokenizer`), arsitektur cocok tapi tokenizer format berbeda

**Masalah utama:**
1. `ml-service` menggunakan `tokenizer.pkl` (pickle format dengan class `StandaloneTokenizer`), tetapi `ai/model.ipynb` men-export tokenizer sebagai `tokenizer.joblib` (Keras Tokenizer via joblib)
2. Model `best_model.keras` di `ai/` (14.5 MB) dan di `ml-service/` (14.5 MB) mungkin versi berbeda
3. Data yang digunakan di `ai/` menggunakan kolom `extracted_skills_structured` (bukan `raw_cv_text`)
4. ML service belum di-deploy ke Railway
5. Data Science dashboard belum ada

---

## User Review Required

> [!IMPORTANT]
> **Railway Account**: Apakah sudah punya akun Railway? Perlu credit card untuk verifikasi (free tier tersedia $5/bulan).
> Alternatif gratis: **Render** (free tier 750 jam/bulan, auto-sleep setelah 15 menit idle).

> [!IMPORTANT]
> **GitHub Repository**: Apakah repo GitHub sudah ada dan terhubung? Untuk Railway/Render deployment, perlu push ke GitHub dulu.

> [!WARNING]
> **Tokenizer Mismatch**: `ai/tokenizer.joblib` menggunakan Keras `Tokenizer` class (via joblib), tapi `ml-service/tokenizer.pkl` menggunakan custom `StandaloneTokenizer` (via pickle). Kita perlu menyelaraskan ini.

## Open Questions

1. **Model version**: Apakah `ai/best_model.keras` (14,509,990 bytes) sudah final? Atau perlu retrain?
2. **Database Supabase**: Apakah sudah setup Supabase untuk PostgreSQL + Storage?
3. **Streamlit Cloud**: Punya akun Streamlit Cloud untuk deploy dashboard?
4. **Prioritas**: Mau fokus Phase 1-3 (ML Service + Deployment) dulu, atau sekaligus semua?

---

## Proposed Changes

### Phase 1: Update ML Service dengan Model/Tokenizer Terbaru

Sinkronisasi `ml-service/` dengan output terbaru dari `ai/model.ipynb`.

---

#### [NEW] [export_tokenizer.py](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/ml-service/export_tokenizer.py)

Script untuk mengkonversi `tokenizer.joblib` (Keras Tokenizer) dari `ai/` ke format yang compatible dengan ml-service. Dua opsi:
- **Opsi A**: Langsung load `tokenizer.joblib` via joblib di ml-service (simple, tapi butuh keras di ml-service — sudah ada tensorflow)
- **Opsi B**: Convert ke `StandaloneTokenizer` pickle (compatible dengan yang sudah ada)

**Rekomendasi: Opsi A** karena ml-service sudah install TensorFlow.

#### [MODIFY] [main.py](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/ml-service/main.py)

Perubahan:
1. Ganti tokenizer loading dari pickle ke joblib (`tokenizer.joblib`)
2. Hapus dependency ke `StandaloneTokenizer` dan pickle hack
3. Tambahkan `normalize_skills()` function (sama seperti di `ai/model.ipynb`) agar preprocessing konsisten
4. Tambahkan endpoint `GET /model-info` untuk monitoring
5. Tambahkan CORS middleware

#### [MODIFY] [requirements.txt](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/ml-service/requirements.txt)

Tambah:
- `joblib>=1.4` (untuk load tokenizer.joblib)
- `nltk>=3.9` (untuk text preprocessing konsisten)

#### [DELETE] [tokenizer_compat.py](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/ml-service/tokenizer_compat.py)

Tidak diperlukan lagi setelah switch ke joblib format.

#### [DELETE] [tokenizer.pkl](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/ml-service/tokenizer.pkl)

Diganti dengan `tokenizer.joblib`.

#### Copy file dari `ai/` ke `ml-service/`:
- `ai/tokenizer.joblib` → `ml-service/tokenizer.joblib`
- `ai/best_model.keras` → `ml-service/best_model.keras` (update jika versi berbeda)

---

### Phase 2: Backend Integration Improvements

Perbaiki koneksi backend → ML Service agar robust.

---

#### [MODIFY] [config.py](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/backend/app/config.py)

- Tambahkan `ml_service_api_key` (opsional, untuk auth antar service)
- Update `ml_service_url` default ke Railway URL setelah deploy

#### [MODIFY] [match.py (router)](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/backend/app/routers/match.py)

- Improve error handling dan logging pada `_call_ml_service()`
- Tambahkan retry logic (1x retry)
- Tambahkan `GET /api/match/ml-status` endpoint untuk cek status ML service

#### [MODIFY] [main.py (backend)](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/backend/app/main.py)

- Tambahkan startup event untuk warmup ML service connection
- Improve health check dengan ML service status

---

### Phase 3: Deployment ML Service ke Railway

---

#### [MODIFY] [Dockerfile](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/ml-service/Dockerfile)

- Update untuk joblib dependency
- Optimize layer caching
- Tambah NLTK data download step

#### [MODIFY] [railway.toml](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/ml-service/railway.toml)

- Pastikan konfigurasi sudah optimal

#### [NEW] [.github/workflows/deploy-ml.yml](file:///c:/Users/Admin/Backup/Desktop/Capstonee/skillscout-nusantara/.github/workflows/deploy-ml.yml) *(opsional)*

GitHub Actions workflow untuk auto-deploy ml-service ke Railway saat ada perubahan di folder `ml-service/`.

---

### Deployment Steps (Manual)

```text
1. Push repo ke GitHub
2. Login ke Railway (railway.app)
3. New Project → Deploy from GitHub Repo
4. Set root directory: ml-service/
5. Railway auto-detect Dockerfile
6. Set env vars:
   - MODEL_PATH=best_model.keras
   - TOKENIZER_PATH=tokenizer.joblib
   - MAX_LENGTH=256
   - PORT=8001  (Railway auto-set)
7. Deploy → dapatkan URL (misal: https://skillscout-ml-xxxx.up.railway.app)
8. Set env di Vercel backend:
   - ML_SERVICE_URL=https://skillscout-ml-xxxx.up.railway.app
9. Redeploy backend di Vercel
```

---

### Phase 4: Data Science Dashboard (Streamlit)

---

#### [NEW] Folder `datascience/` dengan file:

| File | Deskripsi |
|------|-----------|
| `datascience/app.py` | Main Streamlit app dengan multi-page |
| `datascience/pages/01_eda.py` | EDA & Exploratory Analysis |
| `datascience/pages/02_visualisasi.py` | Visualisasi data & Business Questions |
| `datascience/pages/03_cv_analysis.py` | CV Analysis (setelah upload) |
| `datascience/requirements.txt` | Dependencies Streamlit |
| `datascience/Procfile` | Untuk Streamlit Cloud |

**Fitur Dashboard:**
1. **EDA Page**: Distribusi skills, word cloud, top jobs, correlation heatmap
2. **Visualisasi Page**: Jawab business questions (skill mismatch rate, trending skills, top perusahaan)
3. **CV Analysis Page**: Upload CV → tampilkan analisis skill match via API backend

---

### Phase 5: Dokumentasi

---

#### [NEW] Folder `dokumentasi/` dengan file:

| File | Deskripsi |
|------|-----------|
| `dokumentasi/01-arsitektur-sistem.md` | Arsitektur keseluruhan + diagram |
| `dokumentasi/02-setup-development.md` | Cara setup lokal |
| `dokumentasi/03-ml-service.md` | Dokumentasi ML Service API |
| `dokumentasi/04-deployment-guide.md` | Panduan deploy ke Vercel + Railway |
| `dokumentasi/05-api-reference.md` | REST API reference lengkap |
| `dokumentasi/06-ai-model.md` | Dokumentasi model AI (arsitektur, training, metrics) |
| `dokumentasi/07-data-science.md` | Dokumentasi Data Science (EDA, visualisasi) |

---

## Checklist Pemenuhan Requirement

### Full Stack & Backend ✅
| # | Requirement | Status | Detail |
|---|------------|--------|--------|
| 1 | Networking calls (API) | ✅ Sudah | `frontend/app/lib/api.ts` → fetch calls |
| 2 | Module bundler | ✅ Sudah | Next.js (Webpack built-in) |
| 3 | RESTful API | ✅ Sudah | FastAPI: `/api/cv`, `/api/jobs`, `/api/match` |
| 4 | RESTful URL convention | ✅ Sudah | Standard REST patterns |
| 5 | AI/ML integration | 🔧 Phase 1-2 | Backend → ML Service via HTTP |
| 6 | Fitur utama tidak crash | 🔧 Phase 2 | Error handling + fallback |
| 7 | Mockup UI | ✅ Sudah | Next.js pages exist |
| 8 | Responsive layout | ✅ Sudah | CSS responsive di globals.css |
| 9 | Database storage | ✅ Sudah | PostgreSQL via SQLAlchemy |
| 10 | Bootstrap/Tailwind | ✅ Sudah | Tailwind CSS |
| 11 | Express → FastAPI | ✅ Sudah | FastAPI sudah digunakan |
| 12 | Deployment | 🔧 Phase 3 | Vercel (FE+BE) + Railway (ML) |
| 13 | Vercel hosting + ML terpisah | 🔧 Phase 3 | Railway untuk ML service |

### AI ✅
| # | Requirement | Status | Detail |
|---|------------|--------|--------|
| 1 | TF Functional API | ✅ Sudah | `ai/model.ipynb` + `backend/app/ml/placeholder.py` |
| 2 | Custom component | ✅ Sudah | Custom training loop (`tf.GradientTape`), Custom callback (Early Stopping + ReduceLR manual) |
| 3 | Export .keras | ✅ Sudah | `ai/best_model.keras` |
| 4 | Inference code | ✅ Sudah | `ml-service/main.py` |
| 5 | REST API (FastAPI) | ✅ Sudah | `ml-service/main.py` |
| 6 | Custom training loop | ✅ Sudah | `tf.GradientTape` di `ai/model.ipynb` |
| 7 | Generative AI | ⚠️ Belum | Perlu tambah (bisa Google Gemini untuk fitur chatbot/CV tips) |
| 8 | TensorBoard | ⚠️ Belum | Perlu tambah logging ke TensorBoard di training |
| 9 | Akurasi ≥ 85%, MAE ≤ 0.02 | ⚠️ Partial | MAE = 0.017 ✅, Accuracy = 50.5% ❌ (tapi ROC-AUC = 0.9997, ini regression bukan classification) |

### Data Science
| # | Requirement | Status | Detail |
|---|------------|--------|--------|
| 1 | EDA | 🔧 Phase 4 | Streamlit dashboard |
| 2 | Visualisasi + Business Questions | 🔧 Phase 4 | Streamlit dashboard |
| 3 | Interactive Dashboard (Streamlit) | 🔧 Phase 4 | New `datascience/` folder |
| 4 | Deploy ke Streamlit Cloud | 🔧 Phase 4 | Setelah dashboard selesai |

---

## Verification Plan

### Automated Tests
1. `curl POST http://localhost:8001/rank` — test ML service inference
2. `curl GET http://localhost:8001/health` — verify model loaded
3. `curl GET http://localhost:8001/trends` — test trends endpoint
4. `curl POST http://localhost:8000/api/match` — test backend → ML service flow
5. Run `pytest` di backend

### Manual Verification
1. Upload CV di frontend → verify skill extraction → run matching → lihat hasil
2. Check Railway deployment logs untuk memastikan model loaded
3. Test fallback: matikan ML service → backend harus fallback ke TF-IDF
4. Verify Streamlit dashboard bisa load dan menampilkan grafik

### Browser Testing
1. Buka `https://skillscout-nusantara-7kxc.vercel.app/`
2. Test upload CV flow end-to-end
3. Test halaman trends
4. Test responsive di mobile view

---

## Urutan Pengerjaan (Prioritas)

```
Phase 1 (ML Service Update)     → 🔴 PRIORITAS TERTINGGI
Phase 2 (Backend Integration)   → 🔴 PRIORITAS TINGGI
Phase 3 (Railway Deployment)    → 🟡 SETELAH Phase 1-2
Phase 5 (Dokumentasi)           → 🟡 SETIAP SELESAI PHASE
Phase 4 (Data Science Dashboard)→ 🟢 TERAKHIR
```
