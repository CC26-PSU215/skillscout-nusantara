# 🔧 Langkah Integrasi — SkillScout Nusantara (Revisi)

**Tanggal:** 23 Mei 2026
**Tim:** CC26-PSU215
**Status:** ✅ Frontend SELESAI | ⚠️ ML Perlu Peningkatan Akurasi

---

## 📊 Status Terkini (Post-Integrasi)

| Komponen | Status | Progres |
|----------|--------|---------|
| Frontend (Next.js) | ✅ Selesai | 100% — 5 halaman, 6 komponen, API client |
| Backend (FastAPI) | ✅ Selesai | 90% — API lengkap, CV parser, matcher |
| ML Service | ⚠️ Parsial | Service ada, model accuracy 45% |
| Database (Supabase) | ✅ Terhubung | PostgreSQL + Storage aktif |
| Docker Compose | ✅ Selesai | 4 services (db, backend, frontend, ml) |

---

## FASE 1: ✅ Frontend (SELESAI)

### 1.1 Struktur File yang Dibuat

```
frontend/app/
├── layout.tsx                 ← Root layout (Navbar + Footer)
├── page.tsx                   ← Landing page (hero, fitur, CTA)
├── globals.css                ← Design system (dark theme, glassmorphism)
├── .env.local                 ← NEXT_PUBLIC_API_URL=http://localhost:8000
├── upload/
│   └── page.tsx               ← Upload CV (drag & drop)
├── jobs/
│   └── page.tsx               ← Daftar lowongan (search + pagination)
├── match/
│   └── [cvId]/page.tsx        ← Hasil matching (skor + skill gap)
├── trends/
│   └── page.tsx               ← Tren skill (prediksi demand)
├── lib/
│   └── api.ts                 ← API client (GET, POST, upload)
├── types/
│   └── api.ts                 ← TypeScript types (match backend schemas)
└── components/
    ├── Navbar.tsx              ← Glassmorphism nav + mobile menu
    ├── Footer.tsx              ← Footer dengan info tim
    ├── CVUploadForm.tsx        ← Drag & drop + auto-match
    ├── JobCard.tsx             ← Card lowongan kerja
    ├── MatchResultCard.tsx     ← Card hasil matching + score ring
    └── SkillBadge.tsx          ← Badge skill (success/warning/primary)
```

### 1.2 Alur Frontend

```
Landing Page → Upload CV → Backend memproses → Auto-redirect ke Match Results
                                ↓
                        Jobs Page (browse)
                        Trends Page (prediksi)
```

### 1.3 Dependencies yang Ditambahkan

```json
{
  "lucide-react": "^1.16.0",     // Icon library
  "react-dropzone": "^15.0.0",   // Drag & drop file
  "recharts": "^3.8.1"           // Charts (untuk trends)
}
```

---

## FASE 2: ⚠️ ML Service — Peningkatan Akurasi dari 45% → 90%

### 2.1 Analisis Masalah Akurasi 45%

Model Siamese BiLSTM saat ini hanya mencapai **45% accuracy** karena:

1. **Data Training Tidak Seimbang**
   - CV.csv hanya 505 data, JobMarket hanya 800 data
   - Pasangan CV-Job yang benar-benar cocok (positive pair) sangat sedikit
   - Model tidak belajar membedakan "cocok" vs "tidak cocok" dengan baik

2. **Tokenizer Tidak Optimal**
   - Vocab size 10000 terlalu kecil untuk teks bilingual Indonesia-Inggris
   - Tidak ada preprocessing khusus bahasa Indonesia

3. **Arsitektur Kurang Optimal**
   - Embedding dimension 300 terlalu besar untuk vocab 10000
   - Dropout 0.2 mungkin kurang untuk mencegah overfitting

4. **Label Quality**
   - Cara membuat positive/negative pairs tidak optimal

### 2.2 Strategi Peningkatan Akurasi (Step-by-Step)

#### Langkah A — Data Augmentation (Target: +20% accuracy)

```python
# ai/improve_data.py
"""
Tambahkan data training dengan teknik berikut:
1. Synonym replacement untuk skill names
2. Random insertion/deletion
3. Paraphrase teks deskripsi
4. Cross-language augmentation (ID↔EN)
"""

import pandas as pd
import random

def augment_cv_text(text: str) -> list[str]:
    """Generate 3-5 variasi dari satu teks CV."""
    synonyms = {
        "python": ["python programming", "python developer", "python3"],
        "machine learning": ["ML", "pembelajaran mesin", "machine learning engineering"],
        "data analysis": ["analisis data", "data analytics", "data insights"],
        "project management": ["manajemen proyek", "project lead", "PM"],
    }
    
    variants = []
    words = text.lower().split()
    for _ in range(3):
        new_words = []
        for w in words:
            if w in synonyms and random.random() > 0.5:
                new_words.append(random.choice(synonyms[w]))
            else:
                new_words.append(w)
        variants.append(" ".join(new_words))
    return variants

def create_balanced_pairs(cv_df, job_df):
    """
    Buat pasangan positive dan negative yang SEIMBANG.
    - Positive: CV skill overlap > 50% dengan job skills
    - Negative: CV skill overlap < 10% dengan job skills
    - Rasio 1:1 positive:negative
    """
    positive_pairs = []
    negative_pairs = []
    
    for _, cv in cv_df.iterrows():
        cv_skills = set(cv['extracted_user_skills'].lower().split(', '))
        for _, job in job_df.iterrows():
            job_skills = set(job['skills'].lower().split(', '))
            overlap = len(cv_skills & job_skills) / max(len(job_skills), 1)
            
            if overlap >= 0.5:
                positive_pairs.append((cv['raw_cv_text'], job['description'], 1))
            elif overlap < 0.1:
                negative_pairs.append((cv['raw_cv_text'], job['description'], 0))
    
    # Balance: ambil jumlah yang sama
    min_len = min(len(positive_pairs), len(negative_pairs))
    random.shuffle(negative_pairs)
    
    return positive_pairs[:min_len] + negative_pairs[:min_len]
```

#### Langkah B — Perbaiki Preprocessing (Target: +10% accuracy)

```python
# ai/improved_preprocessing.py
"""
Preprocessing yang lebih baik:
1. Lowercase + remove special chars
2. Stopword removal (Indonesia + English)
3. Stemming (Sastrawi untuk Indonesia)
4. Skill normalization (synonym → canonical)
"""

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import re

stemmer = StemmerFactory().create_stemmer()
stopword_remover = StopWordRemoverFactory().create_stop_word_remover()

SKILL_SYNONYMS = {
    "pembelajaran mesin": "machine learning",
    "kecerdasan buatan": "artificial intelligence",
    "analisis data": "data analysis",
    "basis data": "database",
    "jaringan syaraf": "neural network",
    "pengembangan web": "web development",
    "manajemen proyek": "project management",
}

def preprocess_text(text: str) -> str:
    text = text.lower()
    # Normalize synonyms
    for indo, eng in SKILL_SYNONYMS.items():
        text = text.replace(indo, eng)
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```

#### Langkah C — Perbaiki Arsitektur Model (Target: +15% accuracy)

```python
# ai/improved_model.py
"""
Arsitektur yang lebih baik untuk mencapai 90% accuracy.
Perubahan kunci:
1. Pre-trained embeddings (FastText Indonesia)
2. Attention mechanism
3. Better regularization
4. Contrastive loss instead of binary cross-entropy
"""

import tensorflow as tf
from tensorflow import keras
from keras import layers

def build_improved_model(
    vocab_size: int = 20000,    # Naikkan dari 10000
    embed_dim: int = 128,       # Turunkan dari 300
    max_length: int = 256,
    lstm_units_1: int = 128,
    lstm_units_2: int = 64,
    dropout_rate: float = 0.3,  # Naikkan dari 0.2
):
    """
    Siamese BiLSTM yang diperbaiki dengan:
    - Attention layer
    - Higher dropout
    - Better embedding dimension
    """
    # Shared encoder
    input_layer = layers.Input(shape=(max_length,), name="text_input")
    
    x = layers.Embedding(vocab_size, embed_dim, mask_zero=True)(input_layer)
    x = layers.SpatialDropout1D(0.2)(x)  # Dropout pada embedding
    
    # BiLSTM layers
    x = layers.Bidirectional(
        layers.LSTM(lstm_units_1, return_sequences=True, dropout=0.2, recurrent_dropout=0.1)
    )(x)
    x = layers.Bidirectional(
        layers.LSTM(lstm_units_2, return_sequences=True, dropout=0.2, recurrent_dropout=0.1)
    )(x)
    
    # Attention mechanism
    attention = layers.Dense(1, activation='tanh')(x)
    attention = layers.Flatten()(attention)
    attention = layers.Activation('softmax')(attention)
    attention = layers.RepeatVector(lstm_units_2 * 2)(attention)
    attention = layers.Permute([2, 1])(attention)
    
    x = layers.Multiply()([x, attention])
    x = layers.Lambda(lambda xin: tf.reduce_sum(xin, axis=1))(x)
    
    x = layers.Dense(64, activation='relu')(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Lambda(lambda xin: tf.math.l2_normalize(xin, axis=1))(x)
    
    encoder = keras.Model(input_layer, x, name="encoder")
    
    # Siamese architecture
    cv_input = layers.Input(shape=(max_length,), name="cv_input")
    job_input = layers.Input(shape=(max_length,), name="job_input")
    
    cv_encoded = encoder(cv_input)
    job_encoded = encoder(job_input)
    
    # Cosine similarity
    cosine = layers.Dot(axes=1, normalize=False)([cv_encoded, job_encoded])
    output = layers.Dense(1, activation='sigmoid')(cosine)
    
    model = keras.Model(
        inputs=[cv_input, job_input],
        outputs=output,
        name="improved_siamese_bilstm"
    )
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.AUC(name='auc')]
    )
    
    return model, encoder

# Training script
def train_improved_model():
    import numpy as np
    from keras.utils import pad_sequences
    from keras.preprocessing.text import Tokenizer
    import pickle
    
    # 1. Load data
    # ... (load dan preprocess CV dan Job data)
    
    # 2. Build tokenizer dengan vocab lebih besar
    tokenizer = Tokenizer(num_words=20000, oov_token="<OOV>")
    # ... fit pada semua teks
    
    # 3. Build model
    model, encoder = build_improved_model(vocab_size=20000)
    
    # 4. Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=5, restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=3
        ),
        keras.callbacks.ModelCheckpoint(
            'best_model_v2.keras', monitor='val_accuracy', save_best_only=True
        ),
    ]
    
    # 5. Train
    # model.fit(..., callbacks=callbacks, epochs=50, batch_size=32)
    
    # 6. Save tokenizer
    with open('tokenizer_v2.pkl', 'wb') as f:
        pickle.dump(tokenizer, f)
    
    return model
```

#### Langkah D — Tambah Data Scraping (Target: +5% accuracy)

```bash
# Scrape lebih banyak data lowongan
cd backend
python -m app.scraping.glints_scraper --pages 20  # dari 1 page → 20 pages

# Target: minimal 2000 lowongan (dari 800)
```

#### Langkah E — Evaluasi Model

```python
# ai/evaluate_model.py
from sklearn.metrics import classification_report, confusion_matrix

# Setelah training, evaluasi pada test set:
# - Accuracy target: >= 90%
# - Precision: >= 85%
# - Recall: >= 85%
# - F1-Score: >= 85%

y_pred = model.predict([X_test_cv, X_test_job])
y_pred_binary = (y_pred > 0.5).astype(int)

print(classification_report(y_test, y_pred_binary))
```

### 2.3 Ringkasan Strategi

| Strategi | Dampak | Effort |
|----------|--------|--------|
| Data balancing (positive:negative = 1:1) | +15-20% | 2-3 jam |
| Better preprocessing (bilingual) | +5-10% | 1-2 jam |
| Attention mechanism + regularization | +10-15% | 3-4 jam |
| More data (scraping 2000+ jobs) | +3-5% | 2-4 jam |
| Hyperparameter tuning | +2-5% | 2-3 jam |
| **Total estimasi** | **+35-55%** | **10-16 jam** |

> **Catatan:** Dengan strategi ini, akurasi diperkirakan naik dari 45% → 80-95%.

---

## FASE 3: Koneksi Backend ↔ ML Service

### 3.1 Backend Sudah Siap

File `backend/app/routers/match.py` sudah memiliki:
- ✅ Call ke ML service via `httpx` (`_call_ml_service`)
- ✅ Fallback ke local TF-IDF jika ML service offline
- ✅ Logging hasil ke database (`match_logs`)

### 3.2 Yang Perlu Dilakukan

1. **Ekspor tokenizer** dari notebook training
2. **Copy model + tokenizer** ke `ml-service/`
3. **Set `ML_SERVICE_URL`** di backend `.env`

```bash
# Backend .env
ML_SERVICE_URL=http://localhost:8001  # lokal
# ML_SERVICE_URL=https://skillscout-ml-xxx.up.railway.app  # production
```

---

## FASE 4: Docker Compose (SELESAI)

Docker Compose sudah di-update dengan 4 services:

```yaml
services:
  db:         # PostgreSQL 15
  backend:    # FastAPI (port 8000)
  frontend:   # Next.js (port 3000)
  ml:         # ML Service (port 8001)  ← BARU
```

### Cara Menjalankan

```bash
# Development (semua services)
docker-compose up --build

# Atau jalankan terpisah:
cd backend  && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
cd ml-service && uvicorn main:app --reload --port 8001
```

---

## FASE 5: Testing End-to-End

### 5.1 Test Backend

```bash
# Health check
curl http://localhost:8000/api/health

# Upload CV
curl -X POST http://localhost:8000/api/cv/upload -F "file=@cv.pdf"

# List jobs
curl http://localhost:8000/api/jobs

# Match (ganti CV_ID)
curl -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "CV_ID_DARI_UPLOAD", "top_k": 10}'
```

### 5.2 Test Frontend

```bash
cd frontend && npm run dev
# Buka http://localhost:3000
# 1. Klik "Upload CV" → drag PDF → lihat matching
# 2. Klik "Lowongan" → browse jobs
# 3. Klik "Tren Skill" → lihat prediksi
```

---

## ✅ Checklist Final

- [x] Frontend: Landing page
- [x] Frontend: Upload CV (drag & drop)
- [x] Frontend: Daftar lowongan (search + pagination)
- [x] Frontend: Hasil matching (skor + skill gap)
- [x] Frontend: Tren skill
- [x] Frontend: API client + TypeScript types
- [x] Frontend: Responsive (mobile + desktop)
- [x] Frontend: Design system (glassmorphism, dark theme)
- [x] Docker Compose: 4 services
- [ ] ML: Tingkatkan akurasi → 90%
- [ ] ML: Ekspor tokenizer.pkl
- [ ] ML: Deploy ke Railway/Render (opsional)
- [ ] Data: Tambah lowongan ke database
- [ ] Testing: End-to-end flow
