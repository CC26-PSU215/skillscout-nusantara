
# ============================================================
# PERBAIKAN 1: extract_skills() yang lebih baik
# Ganti fungsi extract_skills di cv_processing.ipynb
# ============================================================

def extract_skills(text):
    """
    Ekstrak skill teknis dari teks CV.
    Skill list diperbaiki agar match dengan job_df['extracted_job_skills']
    yang berisi tool/teknologi nyata (sql, python, tableau, dst).
    """
    skill_keywords = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'cpp', 'c++', 'c#', 'golang', 'scala', 'rust', 'r',
        # Data & Analytics Tools
        'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite',
        'tableau', 'power bi', 'looker', 'qlik', 'metabase', 'superset',
        'excel', 'spreadsheet',
        'spss', 'sas', 'stata',
        # Data Science / ML
        'machine learning', 'deep learning', 'neural network',
        'natural language processing', 'nlp', 'natural language',
        'computer vision', 'object detection',
        'data science', 'data analysis', 'data analytics', 'analytics',
        'statistics', 'statistical',
        'reinforcement learning', 'time series',
        'big data', 'data engineering', 'data pipeline',
        # ML Frameworks & Libraries
        'tensorflow', 'pytorch', 'keras',
        'scikit-learn', 'scikitlearn', 'sklearn',
        'xgboost', 'lightgbm', 'catboost',
        'numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy',
        # Cloud & DevOps
        'aws', 'gcp', 'azure', 'cloud',
        'docker', 'kubernetes', 'spark', 'hadoop', 'kafka',
        'airflow', 'dbt', 'etl',
        # Web / Software
        'react', 'angular', 'nodejs', 'django', 'flask', 'fastapi',
        'git', 'github', 'gitlab', 'cicd',
        'agile', 'scrum',
        # Soft/Domain skills (hanya yang relevan)
        'algorithm', 'data visualization', 'visualization',
        'project management',
    ]

    found_skills = []
    text_lower = text.lower()
    for skill in skill_keywords:
        if skill in text_lower and skill not in found_skills:
            found_skills.append(skill)

    return ', '.join(found_skills) if found_skills else 'not specified'


# ============================================================
# PERBAIKAN 2: Cleaning job_df['extracted_job_skills']
# Jalankan ini di model.ipynb sebelum membangun pasangan training
# ============================================================

import re

# Kata-kata garbage yang harus dibuang dari extracted_job_skills
GARBAGE_TOKENS = {
    'unspecified', 'tidak', 'ada', 'spesifik', 'tools', 'tool',
    'dan', 'atau', 'yang', 'dengan', 'untuk', 'dalam', 'dari',
    'na', 'n/a', 'none', 'null', '-', 'tbd', 'other', 'lainnya',
    'berbagai', 'beberapa', 'semua', 'sesuai', 'kebutuhan',
}

def clean_job_skills(text):
    """
    Bersihkan extracted_job_skills dari nilai garbage.
    Job skills yang valid: tool/teknologi nyata (min 2 karakter, bukan stopword).
    """
    if pd.isna(text) or str(text).strip() == '':
        return 'not specified'

    text = str(text).lower().strip()

    # Jika ada koma, berarti sudah comma-separated → split by comma
    if ',' in text:
        tokens = [t.strip() for t in text.split(',')]
    else:
        # Space-separated (format umum di job_df)
        tokens = text.split()

    # Filter: buang garbage, terlalu pendek, atau angka murni
    clean_tokens = []
    for t in tokens:
        t = t.strip()
        if (
            len(t) >= 2
            and t not in GARBAGE_TOKENS
            and not re.match(r'^\d+$', t)     # bukan angka murni
            and not re.match(r'^[^a-z]+$', t)  # harus ada huruf
        ):
            clean_tokens.append(t)

    return ' '.join(clean_tokens) if clean_tokens else 'not specified'


# ============================================================
# CARA PAKAI DI NOTEBOOK:
#
# Di cv_processing.ipynb:
#   1. Ganti fungsi extract_skills() lama dengan yang di atas
#   2. Jalankan ulang cell extract_skills dan simpan csv
#
# Di model.ipynb (sebelum build training pairs):
#   3. Tambahkan cell berikut:
#
#      job_df['extracted_job_skills'] = job_df['extracted_job_skills'].apply(clean_job_skills)
#      # Cek hasilnya
#      print(job_df['extracted_job_skills'].value_counts().head(20))
#      print("Jobs dengan 'not specified':", (job_df['extracted_job_skills'] == 'not specified').sum())
#
# ============================================================

# ============================================================
# PERBAIKAN 3: parse_cv_skills & parse_job_skills di model.ipynb
# ============================================================

def parse_cv_skills(text):
    """CV skills: comma-separated → set of individual skill tokens."""
    skills = set(s.strip().lower() for s in str(text).replace('/', ',').split(',') if s.strip())
    # Tambah token individual untuk multi-word skills agar bisa match
    tokens = set(word for skill in skills for word in skill.split())
    return skills | tokens

def parse_job_skills(text):
    """Job skills: space-separated → set of tokens, buang garbage."""
    garbage = {'unspecified', 'tidak', 'ada', 'spesifik', 'tools', 'not', 'specified'}
    return set(
        s.strip().lower() for s in str(text).split()
        if s.strip() and len(s.strip()) >= 2 and s.strip().lower() not in garbage
    )

def match_cv_to_jobs(cv_idx, top_k=20):
    cv_emb  = cv_embedded[cv_idx].reshape(1, -1)
    scores  = cosine_similarity(cv_emb, job_embedded)[0]
    top_idx = np.argsort(scores)[::-1][:top_k]

    cv_skills_raw = parse_cv_skills(cv_df['extracted_skills_structured'].iloc[cv_idx])

    results = []
    for job_idx in top_idx:
        job_row        = job_df.iloc[job_idx]
        job_skills_raw = parse_job_skills(job_df['extracted_job_skills'].iloc[job_idx])

        # Skip job dengan skills yang tidak informatif
        if job_skills_raw in [set(), {'not'}, {'specified'}]:
            continue

        matched_skills = job_skills_raw & cv_skills_raw
        gap_skills     = job_skills_raw - cv_skills_raw

        results.append({
            'job_title'      : job_row['job_title'],
            'matching_score' : f"{scores[job_idx]*100:.2f}%",
            'matched_skills' : sorted(matched_skills),
            'skill_gap'      : sorted(gap_skills),
        })

    return results
