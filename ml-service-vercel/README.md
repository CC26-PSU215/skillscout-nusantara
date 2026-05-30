# SkillScout Nusantara — ML Service (Vercel)

Versi ringan ML Service untuk deploy ke **Vercel Serverless Functions**.

## ⚡ Perbedaan dengan Railway Version

| Fitur | Railway (`ml-service/`) | Vercel (`ml-service-vercel/`) |
|-------|------------------------|-------------------------------|
| **Matcher** | Siamese BiLSTM (TensorFlow) | TF-IDF + Cosine Similarity |
| **Akurasi** | Tinggi (ROC AUC 0.9997) | Cukup baik (heuristic-based) |
| **Model File** | `best_model.keras` (14.5MB) | Tidak perlu model file |
| **Dependencies** | ~500MB (TensorFlow) | ~50MB (scikit-learn) |
| **Cold Start** | Lambat (load model) | Cepat |
| **Platform** | Docker / Railway | Vercel Serverless |

## 🚀 Deploy ke Vercel

### Cara 1: Via Vercel CLI

```bash
cd ml-service-vercel
npx vercel --prod
```

### Cara 2: Via Vercel Dashboard

1. Buka [vercel.com](https://vercel.com) → New Project
2. Import repo GitHub
3. Set **Root Directory** ke `ml-service-vercel`
4. Deploy!

## 📡 API Endpoints

Semua endpoint **100% kompatibel** dengan Railway version:

| Method | Path | Deskripsi |
|--------|------|-----------|
| `POST` | `/rank` | Ranking lowongan berdasarkan CV |
| `GET` | `/trends` | Prediksi tren skill |
| `GET` | `/health` | Health check |
| `GET` | `/model-info` | Info model & konfigurasi |
| `GET` | `/docs` | Swagger UI (auto-generated) |

### Contoh Request `/rank`

```bash
curl -X POST https://your-app.vercel.app/rank \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Python developer with experience in machine learning, data analysis, and React",
    "jobs": [
      {
        "id": "job-1",
        "title": "Data Scientist",
        "company": "Tokopedia",
        "description": "Looking for data scientist with Python and ML experience",
        "skills": ["python", "machine learning", "sql", "tensorflow"]
      }
    ],
    "top_k": 5
  }'
```

## 🔧 Development Lokal

```bash
cd ml-service-vercel
pip install -r requirements.txt
uvicorn api.index:app --reload --port 8002
```

## 📝 Catatan

- Vercel memiliki batas **250MB** untuk deployment size, sehingga TensorFlow tidak bisa digunakan.
- Untuk inference Deep Learning (Siamese BiLSTM), gunakan **Railway deployment** (`ml-service/`).
- API contract identik — frontend bisa switch antara Railway dan Vercel tanpa perubahan kode.
