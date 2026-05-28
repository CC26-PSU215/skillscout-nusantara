# 🔗 Panduan Integrasi Backend ↔ ML Service

## Overview

Backend (Vercel) berkomunikasi dengan ML Service (Railway) melalui HTTP REST API.
Komunikasi ini **unidirectional**: backend → ML service.

```
Frontend (Vercel)
    │
    ▼
Backend (Vercel/FastAPI)
    │
    ├──▶ POST /rank (ML Service/Railway)     ← Matching CV-Job
    ├──▶ GET  /trends (ML Service/Railway)   ← Prediksi tren skill
    └──▶ GET  /health (ML Service/Railway)   ← Cek status
```

---

## Arsitektur Integrasi

### File-file yang Terlibat

| Lokasi | File | Fungsi |
|--------|------|--------|
| Backend | `app/config.py` | Menyimpan URL ML service (`ml_service_url`) |
| Backend | `app/routers/match.py` | Memanggil ML service via `httpx` |
| Backend | `app/services/matcher.py` | Fallback TF-IDF lokal |
| ML Service | `main.py` | Menerima request, menjalankan model |

### Flow Detail

#### 1. Matching (POST /api/match)

```python
# backend/app/routers/match.py

@router.post("")
async def match_cv_to_jobs(payload, db):
    # 1. Ambil CV dari database
    cv = await db.execute(select(CVUpload).where(CVUpload.id == payload.cv_id))

    # 2. Ambil semua jobs dari database
    jobs = await db.execute(select(Job))

    # 3. Coba kirim ke ML Service (Railway)
    try:
        results = await _call_ml_service(cv.raw_text, jobs, payload.top_k)
    except Exception:
        # 4. Fallback ke local TF-IDF jika ML service error/timeout
        results = rank_jobs(cv.raw_text, cv.skills, jobs, payload.top_k)

    # 5. Log hasil ke database
    for item in results:
        db.add(MatchLog(cv_id=cv.id, job_id=item["job_id"], score=item["score"], ...))

    return MatchResponse(cv_id=payload.cv_id, results=results)
```

#### 2. Trends (GET /api/match/trends)

```python
# backend/app/routers/match.py

@router.get("/trends")
async def get_skill_trends():
    # Proxy langsung ke ML service
    async with httpx.AsyncClient(timeout=settings.ml_service_timeout) as client:
        resp = await client.get(f"{settings.ml_service_url}/trends")
        return resp.json()
    # Fallback: return data statis jika ML offline
```

---

## Konfigurasi

### Environment Variables di Backend (Vercel)

```bash
# .env atau Vercel Environment Variables
ML_SERVICE_URL=https://skillscout-ml-production-xxxx.up.railway.app
ML_SERVICE_TIMEOUT=60
```

> ⚠️ **JANGAN** akhiri URL dengan `/` (trailing slash)
>
> ✅ Benar: `https://xxx.up.railway.app`
> ❌ Salah: `https://xxx.up.railway.app/`

### Environment Variables di ML Service (Railway)

```bash
MODEL_PATH=best_model.keras
TOKENIZER_PATH=tokenizer.joblib
MAX_LENGTH=256
BATCH_SIZE=32
ALLOWED_ORIGINS=https://skillscout-nusantara-7kxc.vercel.app,https://skillscout-nusantara.vercel.app
```

---

## Fallback Mechanism

Jika ML Service tidak tersedia (down, timeout, error), backend **otomatis fallback** ke TF-IDF matcher lokal:

```python
# backend/app/services/matcher.py

def rank_jobs(cv_text, cv_skills, jobs, top_k=10):
    """
    Fallback: TF-IDF + Cosine Similarity + Skill Overlap
    Score = 0.6 × TF-IDF + 0.4 × Skill Overlap
    """
```

**Perbedaan Deep Learning vs Fallback:**

| Aspek | Siamese BiLSTM | TF-IDF Fallback |
|-------|---------------|-----------------|
| Akurasi | Tinggi (ROC-AUC 0.9997) | Sedang |
| Kecepatan | 1-3 detik (batch) | <1 detik |
| Pemahaman semantik | Ya (embedding) | Tidak (bag-of-words) |
| Dependency | TensorFlow (~400MB RAM) | scikit-learn (~50MB) |
| `model_used` | `"siamese_bilstm"` | `"tfidf_fallback"` |

---

## Testing Integrasi

### Test 1: Cek ML Service Tersedia

```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/health
# Harus: {"status": "ok", "model_loaded": true, ...}
```

### Test 2: Test Inference Langsung

```bash
curl -X POST https://YOUR-RAILWAY-URL.up.railway.app/rank \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "python sql data analysis machine learning",
    "jobs": [
      {"id": "1", "title": "Data Analyst", "company": "PT A", "description": "analyze data", "skills": ["python","sql"]},
      {"id": "2", "title": "Web Developer", "company": "PT B", "description": "build websites", "skills": ["react","nodejs"]}
    ],
    "top_k": 2
  }'
```

### Test 3: Test via Backend

```bash
# Trends (harus proxy ke ML service)
curl https://skillscout-nusantara.vercel.app/api/match/trends

# Health
curl https://skillscout-nusantara.vercel.app/api/health
```

### Test 4: Test Full Flow (Frontend)

1. Buka https://skillscout-nusantara-7kxc.vercel.app
2. Upload CV PDF
3. Klik "Match" / "Cocokkan"
4. Lihat hasil — perhatikan `model_used`:
   - `"siamese_bilstm"` → ML Service berhasil dipanggil ✅
   - `"tfidf_fallback"` → ML Service gagal, menggunakan fallback ⚠️

---

## Diagram Sequence

```
User          Frontend         Backend(Vercel)      ML Service(Railway)    Database
 │               │                  │                     │                  │
 │──Upload CV──▶│                  │                     │                  │
 │               │──POST /api/cv──▶│                     │                  │
 │               │                  │──Extract text/skills│                  │
 │               │                  │──────────────────────────────────────▶│ Save CV
 │               │◀──cv_id─────────│                     │                  │
 │               │                  │                     │                  │
 │──Click Match─▶│                  │                     │                  │
 │               │──POST /api/match▶│                     │                  │
 │               │                  │──────────────────────────────────────▶│ Get CV + Jobs
 │               │                  │◀─────────────────────────────────────│
 │               │                  │                     │                  │
 │               │                  │──POST /rank────────▶│                  │
 │               │                  │                     │──Load model     │
 │               │                  │                     │──Normalize      │
 │               │                  │                     │──Tokenize       │
 │               │                  │                     │──Predict        │
 │               │                  │◀──results──────────│                  │
 │               │                  │                     │                  │
 │               │                  │──────────────────────────────────────▶│ Save MatchLog
 │               │◀──match results──│                     │                  │
 │◀──Display─────│                  │                     │                  │
```
