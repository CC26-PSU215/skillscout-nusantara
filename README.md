# 🚀 SkillScout Nusantara

> Platform Pencari Kerja Berbasis AI dan Prediktor Keterampilan Masa Depan untuk Talenta Indonesia.

## 📖 Overview
**SkillScout Nusantara** adalah sebuah platform cerdas yang dirancang untuk mengatasi masalah *skill mismatch* (ketidakcocokan keterampilan) di pasar tenaga kerja Indonesia. Sistem ini mengekstrak keahlian dari CV pelamar (mendukung format bilingual dan pengalaman non-formal), mencocokkannya dengan lowongan kerja secara adil menggunakan *Machine Learning* (TF-IDF & Cosine Similarity), dan memprediksi tren kebutuhan keterampilan industri di masa depan menggunakan model *Time-Series*. 

Proyek ini dibangun dari nol (*from scratch*) tanpa bergantung pada API LLM komersial, memastikan pemrosesan bahasa lokal yang akurat dan privasi data yang terjaga. 

---

## 👥 Contributors
Proyek ini dikembangkan oleh Tim **CC26-PSU215** dalam rangka Capstone Coding Camp 2026:
* **Muhammad Fikran Naufal** - Data Scientist 
* **Albi Arrizkya Putra** - Data Scientist 
* **Jennifer Khang** - AI Engineer 
* **Velicia Christina Gabriel** - AI Engineer
* **Orellius Lee** - Full-Stack Web Developer
* **Bagus Jiran** - Full-Stack Web Developer 

---

## 🛠️ Tech Stack
**Frontend:**
* Next.js & React
* Shadcn UI & Tailwind CSS

**Backend & API:**
* Python (FastAPI)
* PostgreSQL (Database)
* Prisma ORM / SQLAlchemy

**Machine Learning & Data:**
* Scikit-learn (TF-IDF, Cosine Similarity)
* TensorFlow / Keras (LSTM untuk Time-Series)
* NLTK & Sastrawi (Natural Language Processing lokal)

---

### 📂 File Structure

Struktur direktori proyek ini menggunakan pendekatan **Monorepo** untuk memisahkan antara lingkungan pengembangan Frontend dan Backend/AI.

```text
skillscout-nusantara/
│
├── frontend/                      # 🌐 Dikelola oleh Tim Full-Stack (Frontend)
│   ├── public/                    # File statis (favicon.ico, logo.png)
│   ├── src/
│   │   ├── app/                   # App Router (Routing halaman otomatis Next.js)
│   │   │   ├── globals.css        # File CSS global (Tailwind)
│   │   │   ├── layout.tsx         # Pembungkus halaman utama (Root Layout)
│   │   │   └── page.tsx           # Halaman utama
│   │   ├── components/            # Komponen React yang bisa dipakai ulang
│   │   │   ├── ui/                # Instalasi komponen Shadcn UI
│   │   │   └── shared/            # Komponen kustom (Navbar, Footer, RadarChart)
│   │   ├── hooks/                 # Custom Hooks untuk logika (contoh: API calls)
│   │   ├── lib/                   # Utility functions & API configuration
│   │   └── types/                 # Definisi tipe TypeScript
│   ├── next.config.ts             # Konfigurasi utama Next.js
│   ├── tailwind.config.ts         # Pengaturan tema Tailwind CSS
│   └── package.json               # Dependensi Node.js
│
├── backend/                       # ⚙️ Dikelola oleh Tim Full-Stack (Backend) & AI
│   ├── app/
│   │   ├── api/                   # Endpoint REST API (routes)
│   │   ├── core/                  # Konfigurasi keamanan, CORS, Database
│   │   ├── ml_engine/             # 🧠 "Dapur" AI (Traditional ML & NLP)
│   │   │   ├── nlp_processor.py   # Script Sastrawi & NLTK
│   │   │   ├── tfidf_matcher.py   # Cosine Similarity untuk CV Matching
│   │   │   └── time_series.py     # Prediksi tren LSTM/ARIMA
│   │   ├── models/                # Definisi tabel ORM (Database)
│   │   ├── schemas/               # API Contract (Pydantic models)
│   │   ├── services/              # Logika penghubung API dan ml_engine
│   │   └── main.py                # File utama FastAPI
│   ├── prisma/                    # Skema tabel Prisma ORM (Opsional)
│   └── requirements.txt           # Dependensi Python
│
├── datasets/                      # 📊 Dikelola oleh Tim Data Scientist
│   ├── raw/                       # Data scraping mentah
│   ├── processed/                 # Data bersih siap latih
│   └── gazetteer/                 # Kamus "Skill" Bahasa Indonesia
│
├── docker-compose.yml             # Script untuk deployment via Docker
├── .gitignore                     # File yang dikecualikan dari Git
└── README.md                      # Dokumentasi utama
```

---

## 💻 Cara Run di Local (Local Development)

Pastikan Anda sudah menginstal **Node.js**, **Python 3.10+**, dan **PostgreSQL** di sistem Anda. Panduan di bawah ini disesuaikan untuk dijalankan melalui terminal Windows (PowerShell/Command Prompt).

### 1. Clone Repository
```bash
git clone [https://github.com/username-kalian/skillscout-nusantara.git](https://github.com/username-kalian/skillscout-nusantara.git)
cd skillscout-nusantara
```

## 🏃‍♂️ Menjalankan Aplikasi Secara Lokal (Tanpa Docker)

### 2. Setup Backend (FastAPI)
Buka terminal baru dan arahkan ke folder `backend/`:
```bash
cd backend
```
Buat Virtual Environment dan aktifkan:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```
Instal dependensi Python:
```bash
pip install -r requirements.txt
```
Jalankan server FastAPI:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*Backend akan berjalan di `http://localhost:8000`. Dokumentasi API (Swagger UI) tersedia di `http://localhost:8000/docs`.*

### 3. Setup Frontend (Next.js & React)
Buka terminal baru dan arahkan ke folder `frontend/`:
```bash
cd frontend
```
Instal dependensi Node.js:
```bash
npm install
# atau menggunakan yarn/pnpm:
# yarn install
# pnpm install
```
Buat file environment lokal (jika ada template):
```bash
cp .env.example .env.local
```
Jalankan server *development*:
```bash
npm run dev
# atau yarn dev / pnpm dev
```
*Frontend akan berjalan di `http://localhost:3000`.*

---

## 🐳 Menjalankan Aplikasi dengan Docker (Rekomendasi)

Jika Anda tidak ingin menginstal dependensi (Node.js, Python, PostgreSQL) satu per satu, Anda bisa menggunakan **Docker** untuk menjalankan seluruh aplikasi secara otomatis.

Pastikan **Docker Desktop** sudah terinstal dan berjalan, lalu jalankan perintah berikut di *root* direktori proyek:
```bash
docker-compose up -d --build
```

**Akses Layanan:**
- **Frontend (Next.js):** `http://localhost:3000`
- **Backend API (FastAPI):** `http://localhost:8000`
- **API Docs (Swagger UI):** `http://localhost:8000/docs`
- **Database (PostgreSQL):** Berjalan di port `5432`

Untuk mematikan container:
```bash
docker-compose down
```