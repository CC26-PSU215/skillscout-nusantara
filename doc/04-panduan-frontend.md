# 🖥️ Panduan Frontend — SkillScout Nusantara

## Stack Teknologi

| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| Next.js | 16.2.4 | React framework (App Router) |
| React | 19.2.4 | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Utility CSS (via PostCSS) |
| Lucide React | 1.16+ | Icon library |
| Recharts | 3.8+ | Chart library (tren skill) |

---

## Struktur File

```
frontend/
├── app/
│   ├── layout.tsx                  # Root layout (Navbar + Footer)
│   ├── page.tsx                    # Landing page
│   ├── globals.css                 # Design system lengkap
│   │
│   ├── upload/
│   │   └── page.tsx                # Upload CV (drag & drop)
│   ├── jobs/
│   │   └── page.tsx                # Browse lowongan (search + pagination)
│   ├── match/
│   │   └── [cvId]/
│   │       └── page.tsx            # Hasil matching (skor + skill gap)
│   ├── trends/
│   │   └── page.tsx                # Tren skill (chart + bar)
│   │
│   ├── lib/
│   │   └── api.ts                  # API client (typed wrappers)
│   ├── types/
│   │   └── api.ts                  # TypeScript interfaces
│   └── components/
│       ├── Navbar.tsx              # Navigation bar (glassmorphism)
│       ├── Footer.tsx              # Footer dengan info tim
│       ├── CVUploadForm.tsx        # Form upload (drag & drop)
│       ├── JobCard.tsx             # Card untuk lowongan
│       ├── MatchResultCard.tsx     # Card hasil matching + score ring
│       └── SkillBadge.tsx          # Badge skill (multi-variant)
│
├── .env.local                      # Environment variables
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
└── Dockerfile
```

---

## Design System

### Warna (Dark Theme)

| Token | Hex | Fungsi |
|-------|-----|--------|
| `--bg-primary` | `#0b0f1a` | Background utama |
| `--bg-secondary` | `#111827` | Background section |
| `--bg-card` | `#1a1f2e` | Background card |
| `--primary-500` | `#6366f1` | Indigo (primary) |
| `--accent-500` | `#06b6d4` | Cyan (accent) |
| `--success-500` | `#22c55e` | Hijau (skill cocok) |
| `--warning-500` | `#f59e0b` | Kuning (skill gap) |
| `--error-500` | `#ef4444` | Merah (error) |

### Efek Visual

- **Glassmorphism**: `.glass-card` — blur 12px, semi-transparan
- **Gradient text**: `.section-title` — animasi gradient shift
- **Glow shadow**: `.animate-pulse-glow` — efek bersinar
- **Score ring**: SVG animated circular progress

### Responsif

- Desktop: Grid multi-kolom, horizontal nav
- Mobile (<768px): Single column, hamburger menu

---

## Halaman

### 1. Landing Page (`/`)

**Komponen:**
- Hero section dengan gradient orbs
- Badge "Powered by Siamese BiLSTM"
- Statistik (800+ lowongan, 505 CV, dll)
- 3-step "Cara Kerja"
- Grid 6 fitur utama
- CTA section

### 2. Upload CV (`/upload`)

**Komponen:**
- `CVUploadForm` — drag & drop zone
- Validasi: hanya PDF, maks 5 MB
- Auto-redirect ke halaman matching setelah upload
- Info cards (format, ukuran, bilingual)

**Alur:**
1. User drag/drop PDF
2. Klik "Upload & Cocokkan"
3. Frontend POST `/api/cv/upload`
4. Frontend POST `/api/match`
5. Redirect ke `/match/[cvId]`

### 3. Lowongan (`/jobs`)

**Komponen:**
- Search bar (real-time filter)
- Grid `JobCard` dengan pagination
- Loading spinner + error state

**API:** `GET /api/jobs?page=1&per_page=12&search=python`

### 4. Hasil Matching (`/match/[cvId]`)

**Komponen:**
- Info CV (filename, skills terdeteksi)
- List `MatchResultCard` (ranked)
- SVG score ring (animated)
- Skill badges: hijau (cocok) + kuning (gap)

**API:** 
- `GET /api/cv/{cvId}`
- `POST /api/match { cv_id, top_k: 10 }`

### 5. Tren Skill (`/trends`)

**Komponen:**
- Grid cards dengan progress bars
- Current demand vs predicted demand
- Growth percentage badge

**API:** `GET /api/match/trends`

---

## API Client (`app/lib/api.ts`)

### Fungsi Tersedia

```typescript
// Generic
apiGet<T>(endpoint)           // GET request
apiPost<T>(endpoint, body)    // POST JSON
apiUpload<T>(endpoint, file)  // POST FormData

// Typed wrappers
getJobs(params?)              // GET /api/jobs
getJob(id)                    // GET /api/jobs/{id}
uploadCV(file)                // POST /api/cv/upload
getCV(id)                     // GET /api/cv/{id}
matchCV(cvId, topK)           // POST /api/match
getTrends()                   // GET /api/match/trends
healthCheck()                 // GET /api/health
```

### Error Handling

```typescript
class ApiError extends Error {
  status: number;  // HTTP status code
}

// Contoh penggunaan:
try {
  const result = await uploadCV(file);
} catch (err) {
  if (err instanceof ApiError) {
    console.error(`HTTP ${err.status}: ${err.message}`);
  }
}
```

---

## Cara Menjalankan

```bash
# Development
cd frontend
npm install --no-bin-links --ignore-scripts
npm run dev
# → http://localhost:3000

# Production build
npm run build
npm start
```

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| "API Error" di halaman | Pastikan backend jalan di port 8000 |
| CORS error | Cek `CORS_ORIGINS` di backend `.env` |
| Halaman loading terus | Cek `NEXT_PUBLIC_API_URL` di `.env.local` |
| Upload gagal | Pastikan file PDF, maks 5 MB |
| Tren error 503 | ML Service belum aktif (port 8001) |
