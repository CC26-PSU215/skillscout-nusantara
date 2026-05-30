# skillscout-backend

## Struktur Folder

```
skillscout-backend/
├── api/
│   └── index.py              ← entry point Vercel (re-export app)
├── app/
│   ├── __init__.py
│   ├── main.py               ← FastAPI factory + CORS + router mount
│   ├── config.py             ← env vars via pydantic-settings
│   ├── database.py           ← async SQLAlchemy engine + get_db()
│   ├── db/
│   │   ├── __init__.py
│   │   └── models.py         ← ORM: Job, CVUpload, MatchLog
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py        ← Pydantic: request & response shapes
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── cv.py             ← POST /upload, GET /{cv_id}
│   │   ├── jobs.py           ← GET/POST /jobs (+ filter & pagination)
│   │   └── match.py          ← POST /match, GET /match/trends
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cv_parser.py      ← ekstraksi teks PDF + deteksi skill
│   │   ├── matcher.py        ← TF-IDF fallback matcher (lokal)
│   │   └── storage.py        ← upload PDF ke Supabase Storage
│   └── ml/
│       ├── __init__.py
│       └── placeholder.py    ← arsitektur TF Functional API (referensi)
├── migrations/
│   └── init.sql              ← DDL: jobs, cv_uploads, match_logs
├── tests/
│   ├── __init__.py
│   └── test_cv.py            ← test health + upload validation
├── .env.example              ← template environment variables
├── .gitignore
├── requirements.txt          ← semua dependencies (sudah terinstall)
└── vercel.json               ← konfigurasi routing Vercel
```

---