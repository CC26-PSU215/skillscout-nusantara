"""
Arsitektur Model: Siamese BiLSTM — SkillScout Nusantara
(CC26-PSU215)

File ini mendefinisikan arsitektur Deep Learning yang SAMA dengan
model terlatih `best_model.keras` (14 MB), menggunakan
TensorFlow Functional API.

Arsitektur Asli (sesuai model.ipynb):
  cv_input  (None, 256) ──┐
                           ├── shared encoder "skillscout_nusantara"
  job_input (None, 256) ──┘     ├── Embedding(10000, 300)
                                ├── Bidirectional LSTM(128, return_sequences=True)
                                ├── Bidirectional LSTM(64,  return_sequences=False)
                                ├── Dense(64, relu)
                                ├── Dropout(0.2)
                                └── L2 Normalize (Lambda)
                           ↓
                      Dot (cosine, axes=1)
                           ↓
                      Dense(1, sigmoid) → match_score (0-1)

Catatan Penting:
  - File ini TIDAK dijalankan oleh backend Vercel
  - Model final di-load oleh ML service terpisah (ml-service/main.py)
  - TensorFlow hanya diperlukan di ML service, BUKAN di backend
  - File .keras dan .pkl TIDAK di-commit ke git

Checklist CC26-PSU215:
  ✓ TensorFlow / Keras
  ✓ Functional API (bukan Sequential)
  ✓ Deep Learning (BiLSTM)
  ✓ Export ke .keras format
  ✓ Siamese architecture (shared weights)

Dilatih:
  - Keras 3.13.2, TensorFlow 2.18+
  - Data: 505 CV × 800+ Job descriptions
  - Akurasi saat ini: ~45% (perlu ditingkatkan, lihat doc/03)
"""


# ── Konfigurasi Default (sesuai model terlatih) ─────────────────────────────

MODEL_CONFIG = {
    "vocab_size": 10000,
    "embedding_dim": 300,
    "max_length": 256,
    "lstm_units_1": 128,      # BiLSTM layer 1 (menjadi 256 karena bidirectional)
    "lstm_units_2": 64,       # BiLSTM layer 2 (menjadi 128 karena bidirectional)
    "dense_units": 64,
    "dropout_rate": 0.2,
    "model_name": "siamese_bilstm",
    "encoder_name": "skillscout_nusantara",
}


def build_siamese_bilstm(
    vocab_size: int = 10000,
    embedding_dim: int = 300,
    max_length: int = 256,
    lstm_units_1: int = 128,
    lstm_units_2: int = 64,
    dense_units: int = 64,
    dropout_rate: float = 0.2,
):
    """
    Bangun model Siamese BiLSTM menggunakan TensorFlow Functional API.

    Arsitektur ini IDENTIK dengan `ai/best_model.keras`.

    Args:
        vocab_size:    ukuran vocabulary tokenizer (default 10000)
        embedding_dim: dimensi word embedding (default 300)
        max_length:    panjang maksimum sequence input (default 256)
        lstm_units_1:  unit BiLSTM layer pertama (default 128)
        lstm_units_2:  unit BiLSTM layer kedua (default 64)
        dense_units:   unit Dense layer encoder (default 64)
        dropout_rate:  dropout rate (default 0.2)

    Returns:
        (model, encoder): tuple of full Siamese model dan shared encoder

    Raises:
        ImportError: jika TensorFlow belum terinstall
    """
    try:
        import tensorflow as tf
        from tensorflow import keras
        from keras import layers
    except ImportError:
        raise ImportError(
            "TensorFlow belum terinstall. Jalankan: pip install tensorflow\n"
            "Catatan: TF tidak dibutuhkan di backend Vercel, hanya di ML service."
        )

    # ── Shared Encoder ──────────────────────────────────────────────
    # Encoder ini dipakai bersama oleh cv_input dan job_input
    # (weight sharing → Siamese architecture)

    encoder_input = layers.Input(shape=(max_length,), name="text_input")

    # Embedding: token ID → dense vector
    x = layers.Embedding(
        input_dim=vocab_size,
        output_dim=embedding_dim,
        name="embedding",
    )(encoder_input)

    # Bidirectional LSTM layer 1 — return_sequences=True untuk stacking
    x = layers.Bidirectional(
        layers.LSTM(lstm_units_1, return_sequences=True, name="lstm_1"),
        name="bilstm_1",
    )(x)

    # Bidirectional LSTM layer 2 — return_sequences=False (output terakhir saja)
    x = layers.Bidirectional(
        layers.LSTM(lstm_units_2, return_sequences=False, name="lstm_2"),
        name="bilstm_2",
    )(x)

    # Dense projection
    x = layers.Dense(dense_units, activation="relu", name="dense_encoder")(x)

    # Regularization
    x = layers.Dropout(dropout_rate, name="dropout_encoder")(x)

    # L2 Normalize — membuat vektor unit-length untuk cosine similarity
    x = layers.Lambda(
        lambda v: tf.math.l2_normalize(v, axis=1),
        name="l2_normalize",
    )(x)

    encoder = keras.Model(
        encoder_input, x, name="skillscout_nusantara"
    )

    # ── Siamese Model ───────────────────────────────────────────────
    cv_input = layers.Input(shape=(max_length,), name="cv_input")
    job_input = layers.Input(shape=(max_length,), name="job_input")

    # Kedua input melewati encoder yang SAMA (shared weights)
    cv_encoded = encoder(cv_input)
    job_encoded = encoder(job_input)

    # Cosine similarity via Dot product (karena sudah L2-normalized)
    cosine = layers.Dot(axes=1, normalize=False, name="cosine")(
        [cv_encoded, job_encoded]
    )

    # Output: skor kecocokan 0-1
    output = layers.Dense(1, activation="sigmoid", name="output")(cosine)

    model = keras.Model(
        inputs=[cv_input, job_input],
        outputs=output,
        name="siamese_bilstm",
    )

    return model, encoder


def compile_model(model):
    """
    Compile model dengan optimizer dan metrics standar.

    Returns:
        Compiled model
    """
    from tensorflow import keras

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


def get_training_callbacks(checkpoint_path: str = "best_model.keras"):
    """
    Buat callbacks standar untuk training.

    Returns:
        List of Keras callbacks
    """
    from tensorflow import keras

    return [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=7,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
        keras.callbacks.ModelCheckpoint(
            checkpoint_path,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
    ]


# ── Contoh Penggunaan ────────────────────────────────────────────────────────
#
# from app.ml.placeholder import build_siamese_bilstm, compile_model
#
# model, encoder = build_siamese_bilstm()
# model = compile_model(model)
# model.summary()
#
# # Training:
# # model.fit([X_cv, X_job], y, validation_split=0.2,
# #           epochs=50, batch_size=32,
# #           callbacks=get_training_callbacks())
#
# # Export:
# # model.save("best_model.keras")
