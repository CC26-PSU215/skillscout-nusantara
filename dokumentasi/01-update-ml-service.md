# 📋 Dokumentasi Update ML Service v2.0

## Tanggal: 28 Mei 2026
## Task: Update ML Service & Persiapan Deployment Railway

---

## Apa yang Dilakukan

### 1. Sinkronisasi Tokenizer (ai/ → ml-service/)

**Masalah:**
- `ai/model.ipynb` meng-export tokenizer sebagai `tokenizer.joblib` (Keras Tokenizer via joblib)
- `ml-service/` sebelumnya menggunakan `tokenizer.pkl` (pickle + custom `StandaloneTokenizer`)
- Format berbeda → tokenizer di ml-service tidak konsisten dengan model training

**Solusi:**
- Copy `ai/tokenizer.joblib` ke `ml-service/tokenizer.joblib`
- Ubah loading mechanism dari `pickle` → `joblib`
- Hapus `tokenizer_compat.py` (class `StandaloneTokenizer` tidak diperlukan lagi)
- Hapus `tokenizer.pkl` (format lama)

### 2. Tambah `normalize_skills()` di ML Service

**Masalah:**
- Di `ai/model.ipynb`, sebelum tokenize, dilakukan normalisasi multi-word skills:
  ```python
  "machine learning" → "machinelearning"
  "data science" → "datascience"
  ```
- `ml-service` sebelumnya **tidak** melakukan normalisasi ini
- Menyebabkan sequence yang dihasilkan berbeda dari training → prediksi tidak akurat

**Solusi:**
- Tambahkan fungsi `normalize_skills()` yang **identik** dengan `ai/model.ipynb`
- Panggil normalisasi sebelum `texts_to_sequences()` di `batch_predict()`

### 3. Tambah CORS Middleware

**Masalah:**
- ML service tidak memiliki CORS headers
- Jika ada direct call dari browser (misalnya untuk testing), akan di-block

**Solusi:**
- Tambahkan `CORSMiddleware` dengan configurable `ALLOWED_ORIGINS`
- Default: `*` (semua origin), bisa dibatasi via env var

### 4. Tambah Endpoint Baru

- `GET /model-info` — menampilkan detail arsitektur, konfigurasi, dan training metrics

### 5. Update Dockerfile & railway.toml

- Tambah explicit env var defaults di Dockerfile
- Extend health check `start-period` dari 60s → 120s (TF model loading lambat)
- Extend `healthcheckTimeout` di railway.toml dari 120 → 180

### 6. Update .gitignore

- Allow `ml-service/tokenizer.joblib` (baru)
- Ignore `ml-service/tokenizer.pkl` (lama)
- Ignore `ml-service/tokenizer_compat.py` (lama)

---

## File yang Diubah

| File | Aksi | Detail |
|------|------|--------|
| `ml-service/main.py` | ✏️ Rewrite | joblib tokenizer, normalize_skills, CORS, /model-info |
| `ml-service/requirements.txt` | ✏️ Update | +joblib |
| `ml-service/Dockerfile` | ✏️ Update | env defaults, start-period |
| `ml-service/railway.toml` | ✏️ Update | healthcheckTimeout 180 |
| `ml-service/.dockerignore` | ✏️ Update | cleanup |
| `ml-service/tokenizer.joblib` | ➕ Baru | Copy dari ai/ |
| `ml-service/README.md` | ➕ Baru | Dokumentasi lengkap |
| `ml-service/tokenizer_compat.py` | ❌ Dihapus | Tidak diperlukan |
| `ml-service/tokenizer.pkl` | ❌ Dihapus | Diganti joblib |
| `.gitignore` | ✏️ Update | Allow joblib, ignore pkl |

---

## Langkah Selanjutnya

1. **Deploy ml-service ke Railway** (lihat `ml-service/README.md`)
2. **Set env var di Vercel backend:** `ML_SERVICE_URL=https://xxx.up.railway.app`
3. **Redeploy backend** di Vercel
4. **Test end-to-end:** Upload CV → Match → Lihat hasil

---

## Checklist Pemenuhan Requirement

### AI Requirements yang Terpenuhi oleh ML Service:
- ✅ Model Deep Learning (TensorFlow / Keras)
- ✅ TensorFlow Functional API (Siamese architecture)
- ✅ Export .keras format (`best_model.keras`)
- ✅ REST API mandiri (FastAPI) — `ml-service/main.py`
- ✅ Kode inference (`batch_predict()`, `text_to_sequence()`)
- ✅ Custom training loop (`tf.GradientTape` di `ai/model.ipynb`)
- ✅ MAE ≤ 0.02 (val_mae = 0.0169)

### Full Stack Requirements yang Terpenuhi:
- ✅ RESTful API (FastAPI) — `POST /rank`, `GET /trends`, `GET /health`
- ✅ AI/ML integration via backend → ML service HTTP call
- ✅ Fallback cerdas (TF-IDF jika ML offline)
- ✅ Deployment terpisah dari Vercel (Railway)
