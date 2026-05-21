"""
Placeholder: Arsitektur Deep Learning model menggunakan
TensorFlow Functional API — memenuhi checklist CC26-PSU215.

Model ini akan dilatih oleh AI Engineer dan diekspor ke format .keras.
Service terpisah (Railway/Render) akan me-load model ini untuk inference.

Arsitektur:
  Input teks (CV / Job description)
  → TF-IDF / Token embedding
  → Dense layers
  → Output similarity score

Catatan:
  - Ini BUKAN file yang dijalankan langsung oleh backend Vercel
  - File ini menjadi referensi arsitektur untuk AI Engineer
  - Model final disimpan sebagai .keras dan di-load di ML service
"""


def build_skill_matcher_model(vocab_size: int = 10000, embedding_dim: int = 128):
    """
    Bangun Siamese-style model menggunakan TensorFlow Functional API
    untuk mencocokkan CV dengan Job description.

    Memenuhi requirement checklist:
    ✓ TensorFlow
    ✓ Functional API
    ✓ Export ke .keras

    Args:
        vocab_size: ukuran vocabulary TF-IDF / tokenizer
        embedding_dim: dimensi embedding layer

    Returns:
        tf.keras.Model yang belum di-compile
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

    # ── Input layers ────────────────────────────────────────
    cv_input = keras.Input(shape=(vocab_size,), name="cv_tfidf")
    job_input = keras.Input(shape=(vocab_size,), name="job_tfidf")

    # ── Shared encoder (weight sharing) ─────────────────────
    shared_dense = keras.Sequential([
        layers.Dense(256, activation="relu", name="shared_dense_1"),
        layers.Dropout(0.3),
        layers.Dense(embedding_dim, activation="relu", name="shared_dense_2"),
        layers.BatchNormalization(),
    ], name="shared_encoder")

    cv_embedding = shared_dense(cv_input)
    job_embedding = shared_dense(job_input)

    # ── Cosine similarity layer ─────────────────────────────
    dot_product = layers.Dot(axes=1, normalize=True, name="cosine_sim")(
        [cv_embedding, job_embedding]
    )

    # ── Output ──────────────────────────────────────────────
    output = layers.Dense(1, activation="sigmoid", name="match_score")(dot_product)

    model = keras.Model(
        inputs=[cv_input, job_input],
        outputs=output,
        name="skillscout_matcher",
    )

    return model


def compile_and_summary(model):
    """Compile model dan print summary."""
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()
    return model


# ── Contoh penggunaan (untuk AI Engineer) ───────────────────
#
# model = build_skill_matcher_model(vocab_size=5000, embedding_dim=64)
# model = compile_and_summary(model)
# model.save("skillscout_matcher.keras")
