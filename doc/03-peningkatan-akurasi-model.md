# 🧠 Panduan Peningkatan Akurasi Model — 45% → 90%

## Masalah Utama

Model Siamese BiLSTM saat ini (`ai/best_model.keras`) hanya mencapai **akurasi 45%**. 
Ini hampir sama dengan random chance (50% untuk binary classification), artinya model belum belajar pattern yang bermakna.

---

## Analisis Root Cause

### 1. Data Quality (Penyebab Utama)

| Masalah | Detail |
|---------|--------|
| **Jumlah data terlalu sedikit** | 505 CV + 800 jobs = ~400,000 pasangan. Tapi mayoritas adalah negative pairs |
| **Label tidak jelas** | Bagaimana menentukan CV "cocok" dengan job? Threshold skill overlap berapa? |
| **Imbalanced classes** | Jika setiap CV hanya cocok dengan 5-10 dari 800 jobs, rasio positive:negative = 1:80 |
| **Data bilingual campur** | CV bisa campuran Indonesia-Inggris, tokenizer tidak optimal |

### 2. Preprocessing Issues

| Masalah | Detail |
|---------|--------|
| **Tokenizer vocab terlalu kecil** | 10,000 words untuk bilingual text sangat terbatas |
| **Tidak ada skill normalization** | "python" dan "python programming" dianggap berbeda |
| **Tidak ada text cleaning** | HTML tags, special chars, email masih ada dalam teks |

### 3. Architecture Issues

| Masalah | Detail |
|---------|--------|
| **Embedding terlalu besar** | 300 dim untuk 10K vocab → overfitting |
| **Dropout terlalu rendah** | 0.2 dropout kurang untuk small dataset |
| **Tidak ada attention** | BiLSTM tanpa attention kehilangan informasi penting |

---

## Solusi Step-by-Step

### Step 1: Perbaiki Data Pipeline (Estimasi: 3-4 jam)

#### 1A. Buat script augmentasi data

Buat file baru `ai/augment_data.py`:

```python
"""
Data augmentation untuk memperbanyak training data.
Target: dari 505 CV → 2000+ CV (dengan augmentasi)
"""
import pandas as pd
import random
import re

def augment_text(text: str, n_augments: int = 3) -> list[str]:
    """Generate variasi teks dengan teknik sederhana."""
    variants = []
    words = text.split()
    
    for _ in range(n_augments):
        new_words = words.copy()
        
        # 1. Random deletion (10% words)
        if len(new_words) > 10:
            n_delete = max(1, len(new_words) // 10)
            for _ in range(n_delete):
                idx = random.randint(0, len(new_words) - 1)
                new_words.pop(idx)
        
        # 2. Random swap (5% words)
        n_swap = max(1, len(new_words) // 20)
        for _ in range(n_swap):
            if len(new_words) > 1:
                i = random.randint(0, len(new_words) - 2)
                new_words[i], new_words[i+1] = new_words[i+1], new_words[i]
        
        variants.append(" ".join(new_words))
    
    return variants

def create_quality_pairs(cv_df: pd.DataFrame, job_df: pd.DataFrame) -> pd.DataFrame:
    """
    Buat pasangan CV-Job yang berkualitas.
    
    Positive pair: skill overlap >= 40%
    Hard negative: skill overlap 10-30% (lebih informatif daripada 0%)
    Easy negative: skill overlap < 10%
    
    Rasio: 1 positive : 1 hard_neg : 1 easy_neg
    """
    pairs = []
    
    for _, cv in cv_df.iterrows():
        cv_skills = set(str(cv.get('extracted_user_skills', '')).lower().split(', '))
        cv_skills = {s.strip() for s in cv_skills if s.strip()}
        
        positives = []
        hard_negatives = []
        easy_negatives = []
        
        for _, job in job_df.iterrows():
            job_skills = set(str(job.get('skills', '')).lower().split(', '))
            job_skills = {s.strip() for s in job_skills if s.strip()}
            
            if not job_skills:
                continue
            
            overlap = len(cv_skills & job_skills) / len(job_skills)
            
            if overlap >= 0.4:
                positives.append((cv['raw_cv_text'], str(job.get('description', '')), 1.0))
            elif 0.1 <= overlap < 0.3:
                hard_negatives.append((cv['raw_cv_text'], str(job.get('description', '')), 0.0))
            elif overlap < 0.1:
                easy_negatives.append((cv['raw_cv_text'], str(job.get('description', '')), 0.0))
        
        # Balance per CV
        n = len(positives)
        if n > 0:
            random.shuffle(hard_negatives)
            random.shuffle(easy_negatives)
            pairs.extend(positives)
            pairs.extend(hard_negatives[:n])
            pairs.extend(easy_negatives[:n])
    
    random.shuffle(pairs)
    return pd.DataFrame(pairs, columns=['cv_text', 'job_text', 'label'])

if __name__ == "__main__":
    cv_df = pd.read_csv("CV.csv")
    job_df = pd.read_csv("JobMarket_Preprocessed.csv")
    
    # Augment CVs
    augmented_rows = []
    for _, row in cv_df.iterrows():
        augmented_rows.append(row)
        for aug_text in augment_text(str(row.get('raw_cv_text', '')), 3):
            new_row = row.copy()
            new_row['raw_cv_text'] = aug_text
            augmented_rows.append(new_row)
    
    cv_augmented = pd.DataFrame(augmented_rows)
    print(f"CV data: {len(cv_df)} → {len(cv_augmented)}")
    
    # Create pairs
    pairs_df = create_quality_pairs(cv_augmented, job_df)
    print(f"Total pairs: {len(pairs_df)}")
    print(f"Positive: {(pairs_df['label'] == 1).sum()}")
    print(f"Negative: {(pairs_df['label'] == 0).sum()}")
    
    pairs_df.to_csv("training_pairs.csv", index=False)
    print("✅ Saved to training_pairs.csv")
```

#### 1B. Jalankan script

```bash
cd ai
python augment_data.py
```

### Step 2: Perbaiki Tokenizer (Estimasi: 1-2 jam)

Tambahkan cell baru di `ai/model.ipynb`:

```python
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
import pickle

# Load training pairs
pairs_df = pd.read_csv("training_pairs.csv")

# Gabungkan semua teks untuk tokenizer
all_texts = list(pairs_df['cv_text']) + list(pairs_df['job_text'])

# Tokenizer dengan vocab lebih besar
tokenizer = Tokenizer(
    num_words=20000,        # Naikkan dari 10000
    oov_token="<OOV>",      # Handle out-of-vocabulary
    lower=True,
    filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'
)
tokenizer.fit_on_texts(all_texts)

print(f"Total unique words: {len(tokenizer.word_index)}")
print(f"Using top {tokenizer.num_words} words")

# Save tokenizer
with open("tokenizer_v2.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

print("✅ Tokenizer saved!")
```

### Step 3: Retrain Model (Estimasi: 3-4 jam)

```python
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers

# Hyperparameters
VOCAB_SIZE = 20000
EMBED_DIM = 128       # Turunkan dari 300
MAX_LENGTH = 256
BATCH_SIZE = 32
EPOCHS = 50

# === Build Improved Model ===
def build_encoder():
    inp = layers.Input(shape=(MAX_LENGTH,))
    x = layers.Embedding(VOCAB_SIZE, EMBED_DIM, mask_zero=True)(inp)
    x = layers.SpatialDropout1D(0.2)(x)
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=True, dropout=0.2))(x)
    x = layers.Bidirectional(layers.LSTM(64, return_sequences=False, dropout=0.2))(x)
    x = layers.Dense(64, activation='relu')(x)
    x = layers.Dropout(0.3)(x)              # Naikkan dari 0.2
    x = layers.Lambda(lambda v: tf.math.l2_normalize(v, axis=1))(x)
    return keras.Model(inp, x, name="encoder")

encoder = build_encoder()
cv_input = layers.Input(shape=(MAX_LENGTH,), name="cv_input")
job_input = layers.Input(shape=(MAX_LENGTH,), name="job_input")

cv_enc = encoder(cv_input)
job_enc = encoder(job_input)

cosine = layers.Dot(axes=1, normalize=False)([cv_enc, job_enc])
output = layers.Dense(1, activation='sigmoid')(cosine)

model = keras.Model([cv_input, job_input], output, name="siamese_bilstm_v2")
model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss='binary_crossentropy',
    metrics=['accuracy', keras.metrics.AUC(name='auc')]
)
model.summary()

# === Prepare Data ===
pairs_df = pd.read_csv("training_pairs.csv")

cv_seqs = tokenizer.texts_to_sequences(pairs_df['cv_text'].tolist())
job_seqs = tokenizer.texts_to_sequences(pairs_df['job_text'].tolist())

X_cv = pad_sequences(cv_seqs, maxlen=MAX_LENGTH, padding='post', truncating='post')
X_job = pad_sequences(job_seqs, maxlen=MAX_LENGTH, padding='post', truncating='post')
y = pairs_df['label'].values.astype(np.float32)

# Train/val split
from sklearn.model_selection import train_test_split
X_cv_train, X_cv_val, X_job_train, X_job_val, y_train, y_val = train_test_split(
    X_cv, X_job, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {len(y_train)}, Val: {len(y_val)}")
print(f"Positive rate (train): {y_train.mean():.2%}")
print(f"Positive rate (val):   {y_val.mean():.2%}")

# === Train ===
callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_accuracy', patience=7, restore_best_weights=True
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6
    ),
    keras.callbacks.ModelCheckpoint(
        'best_model_v2.keras', monitor='val_accuracy', save_best_only=True
    ),
]

history = model.fit(
    [X_cv_train, X_job_train], y_train,
    validation_data=([X_cv_val, X_job_val], y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    class_weight={0: 1.0, 1: 1.0},  # Sudah balanced dari augmentation
)

# === Evaluate ===
from sklearn.metrics import classification_report
y_pred = model.predict([X_cv_val, X_job_val])
y_pred_binary = (y_pred.flatten() > 0.5).astype(int)

print("\n=== Classification Report ===")
print(classification_report(y_val, y_pred_binary, target_names=['Not Match', 'Match']))

val_loss, val_acc, val_auc = model.evaluate([X_cv_val, X_job_val], y_val)
print(f"\nVal Accuracy: {val_acc:.4f}")
print(f"Val AUC: {val_auc:.4f}")
```

### Step 4: Update ML Service (Estimasi: 1 jam)

Setelah model baru di-train, update `ml-service/`:

```bash
# Copy file baru
cp ai/best_model_v2.keras ml-service/best_model.keras
cp ai/tokenizer_v2.pkl    ml-service/tokenizer.pkl
```

Update `ml-service/main.py` jika perlu menyesuaikan `MAX_LENGTH` atau `VOCAB_SIZE`.

### Step 5: Evaluasi & Fine-tune (Estimasi: 2 jam)

Jika akurasi masih di bawah 85%, coba:

1. **Naikkan epochs** (50 → 100)
2. **Tambah data scraping** (jalankan GlintsScraper lebih banyak halaman)
3. **Coba learning rate lebih kecil** (1e-4)
4. **Tambah layer LSTM** (3 layer BiLSTM)
5. **Gunakan pre-trained embeddings** (FastText Indonesia)

---

## Timeline Estimasi

| Step | Waktu | Siapa |
|------|-------|-------|
| 1. Data augmentation | 3-4 jam | Tim AI |
| 2. Perbaiki tokenizer | 1-2 jam | Tim AI |
| 3. Retrain model | 3-4 jam | Tim AI |
| 4. Update ML Service | 1 jam | Tim AI / Full-Stack |
| 5. Evaluasi | 2 jam | Tim AI |
| **Total** | **10-13 jam** | |

---

## Target Metrik

| Metrik | Saat Ini | Target |
|--------|----------|--------|
| Accuracy | 45% | ≥ 90% |
| Precision | ~50% | ≥ 85% |
| Recall | ~40% | ≥ 85% |
| F1-Score | ~44% | ≥ 85% |
| AUC | ~0.50 | ≥ 0.95 |
