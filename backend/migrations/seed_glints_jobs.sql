-- ============================================================================
-- SkillScout Nusantara — Seed Data dari glints_jobs.csv
-- Jalankan di Supabase SQL Editor (https://supabase.com/dashboard → SQL Editor)
-- ============================================================================
-- Script ini:
--   1. Memastikan tabel `jobs` sudah ada (CREATE IF NOT EXISTS)
--   2. Insert 31 data lowongan dari glints_jobs.csv
--   3. Skip duplikat berdasarkan source_url (ON CONFLICT DO NOTHING)
--   4. Menampilkan jumlah data yang berhasil di-insert
-- ============================================================================

-- ── Step 0: Pastikan extension pgcrypto aktif ──────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Step 1: Pastikan tabel `jobs` ada ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    id           TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    title        VARCHAR(255)  NOT NULL,
    company      VARCHAR(255)  NOT NULL,
    description  TEXT          NOT NULL,
    skills       JSONB         NOT NULL DEFAULT '[]',
    location     VARCHAR(100),
    source_url   VARCHAR(500),
    scraped_at   TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jobs_skills     ON jobs USING GIN (skills);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs (scraped_at DESC);

-- Tambah UNIQUE constraint pada source_url agar bisa ON CONFLICT
-- (akan di-skip jika sudah ada)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_jobs_source_url'
    ) THEN
        ALTER TABLE jobs ADD CONSTRAINT uq_jobs_source_url UNIQUE (source_url);
    END IF;
END $$;

-- ── Step 2: Pastikan tabel cv_uploads dan match_logs ada ───────────────────
CREATE TABLE IF NOT EXISTS cv_uploads (
    id            TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    filename      VARCHAR(255) NOT NULL,
    storage_path  VARCHAR(500) NOT NULL,
    raw_text      TEXT,
    skills        JSONB        NOT NULL DEFAULT '[]',
    uploaded_at   TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS match_logs (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    cv_id           TEXT NOT NULL REFERENCES cv_uploads(id) ON DELETE CASCADE,
    job_id          TEXT NOT NULL REFERENCES jobs(id)       ON DELETE CASCADE,
    score           FLOAT NOT NULL,
    matched_skills  JSONB NOT NULL DEFAULT '[]',
    gap_skills      JSONB NOT NULL DEFAULT '[]',
    matched_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_match_logs_cv_id ON match_logs (cv_id);
CREATE INDEX IF NOT EXISTS idx_match_logs_score ON match_logs (score DESC);

-- ── Step 3: Insert 31 job listings dari glints_jobs.csv ────────────────────
-- Skills diekstrak dari job_title secara manual
-- Lokasi dinormalisasi

INSERT INTO jobs (id, title, company, description, skills, location, source_url, scraped_at)
VALUES
  -- 1. IT Support - Pt. Swadharma Duta Data
  (
    gen_random_uuid()::TEXT,
    'IT Support',
    'Pt. Swadharma Duta Data',
    'Posisi IT Support di Pt. Swadharma Duta Data. Kategori: Computer & Software. Gaji: Rp 4 jt-4,3 jt. Pengalaman: 1–3 tahun.',
    '[]'::jsonb,
    'Medan, Sumatera Utara',
    'https://glints.com/id/opportunities/jobs/it-support/aeb7c692-f9d8-4837-81ab-27bb87122ec6',
    NOW()
  ),

  -- 2. iDempiere Developer - PT Asiacross Investindo
  (
    gen_random_uuid()::TEXT,
    'iDempiere Developer',
    'PT Asiacross Investindo',
    'Posisi iDempiere Developer di PT Asiacross Investindo. Kategori: Computer & Software. Gaji: Rp 7 jt-10 jt. Pengalaman: 1–3 tahun.',
    '[]'::jsonb,
    'Jakarta Pusat, DKI Jakarta',
    'https://glints.com/opportunities/jobs/idempiere-developer/33de16b9-333a-40a0-bb33-d719b132ce14',
    NOW()
  ),

  -- 3. DevOps Engineer - GlobalXtreme
  (
    gen_random_uuid()::TEXT,
    'DevOps Engineer',
    'GlobalXtreme',
    'Posisi DevOps Engineer di GlobalXtreme. Kategori: Computer & Software. Gaji: Tidak Ditampilkan. Pengalaman: 1–3 tahun.',
    '["devops"]'::jsonb,
    'Bali',
    'https://glints.com/id/opportunities/jobs/devops-engineer/7cce46a9-710e-4508-accb-b34347dd7366',
    NOW()
  ),

  -- 4. Full Stack Developer - GlobalXtreme
  (
    gen_random_uuid()::TEXT,
    'Full Stack Developer',
    'GlobalXtreme',
    'Posisi Full Stack Developer di GlobalXtreme. Kategori: Computer & Software. Gaji: Tidak Ditampilkan. Pengalaman: 1–3 tahun.',
    '["full stack", "fullstack"]'::jsonb,
    'Bali',
    'https://glints.com/id/opportunities/jobs/full-stack-developer/123d4436-79e9-4958-a324-c0f87b3dbbe9',
    NOW()
  ),

  -- 5. Programmer - PT Yafira Digital Technology
  (
    gen_random_uuid()::TEXT,
    'Programmer',
    'PT Yafira Digital Technology',
    'Posisi Programmer di PT Yafira Digital Technology. Kategori: Computer & Software. Gaji: Rp 3,5 jt-7 jt. Pengalaman: 1–3 tahun.',
    '[]'::jsonb,
    'Kab. Lamongan, Jawa Timur',
    'https://glints.com/id/opportunities/jobs/programmer/bb63d0fa-2c6f-48bb-b052-fbb333a0a901',
    NOW()
  ),

  -- 6. Programmer (Japanese Speaker) - LSP Digital Marketing
  (
    gen_random_uuid()::TEXT,
    'Programmer (Japanese Speaker)',
    'LSP Digital Marketing',
    'Posisi Programmer (Japanese Speaker) di LSP Digital Marketing. Kategori: Computer & Software. Gaji: Rp 6 jt-9 jt. Pengalaman: Tidak disebutkan.',
    '[]'::jsonb,
    'Tangerang, Banten',
    'https://glints.com/id/opportunities/jobs/programmer-japanese-speaker/071b2aed-b0b0-4a6f-8fce-a92a43ea124f',
    NOW()
  ),

  -- 7. Administrasi Sistem Operasi - Sumber Teknik
  (
    gen_random_uuid()::TEXT,
    'Administrasi Sistem Operasi',
    'Sumber Teknik',
    'Posisi Administrasi Sistem Operasi di Sumber Teknik. Kategori: Computer & Software. Gaji: Rp 1 jt-2 jt. Pengalaman: 1–3 tahun.',
    '[]'::jsonb,
    'Kab. Sukoharjo, Jawa Tengah',
    'https://glints.com/id/opportunities/jobs/administrasi-sistem-operasi/39302224-a2d1-4231-9170-9cd4a3460d6d',
    NOW()
  ),

  -- 8. Remote Senior Developer - My Replica
  (
    gen_random_uuid()::TEXT,
    'Remote Senior Developer',
    'My Replica',
    'Posisi Remote Senior Developer di My Replica. Kategori: Computer & Software. Gaji: Rp 8 jt-16 jt. Pengalaman: 3–5 tahun.',
    '[]'::jsonb,
    'Tangerang, Banten',
    'https://glints.com/id/opportunities/jobs/remote-senior-developer/39124795-21db-4500-950a-71044f4afb56',
    NOW()
  ),

  -- 9. IT Developer - PT Jatelindo Perkasa Abadi
  (
    gen_random_uuid()::TEXT,
    'IT Developer',
    'PT Jatelindo Perkasa Abadi',
    'Posisi IT Developer di PT Jatelindo Perkasa Abadi. Kategori: Computer & Software. Gaji: Rp 5,7 jt-7 jt. Tipe: Kontrak. Pengalaman: 1–3 tahun.',
    '[]'::jsonb,
    'Jakarta Selatan, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/it-developer/39028449-d03d-440b-9821-e8b82523b0ba',
    NOW()
  ),

  -- 10. QA Engineer Intern - SimpliDOTS
  (
    gen_random_uuid()::TEXT,
    'QA Engineer Intern',
    'SimpliDOTS',
    'Posisi QA Engineer Intern di SimpliDOTS. Kategori: Computer & Software. Gaji: Tidak Ditampilkan. Pengalaman: Tidak disebutkan.',
    '["qa", "quality assurance"]'::jsonb,
    'Jakarta Selatan, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/qa-engineer-intern/387313d0-6266-4389-8652-d6ea03be70d7',
    NOW()
  ),

  -- 11. Data Analis/data eingeneer - PT. Entropi Global Martech
  (
    gen_random_uuid()::TEXT,
    'Data Analis/data eingeneer',
    'PT. Entropi Global Martech',
    'Posisi Data Analis/Data Engineer di PT. Entropi Global Martech. Kategori: Computer & Software. Gaji: Rp 5 jt-6 jt. Pengalaman: 1–3 tahun.',
    '["data analyst", "data engineer"]'::jsonb,
    'Kab. Tangerang, Banten',
    'https://glints.com/id/opportunities/jobs/data-analis-data-eingeneer/37f1cc8b-d69c-44d6-bfa5-674a5c2bc63e',
    NOW()
  ),

  -- 12. Security Engineer - Managed Service (EDR/DLP) - PT Dikstra Cipta Solusi
  (
    gen_random_uuid()::TEXT,
    'Security Engineer - Managed Service (EDR/DLP)',
    'PT Dikstra Cipta Solusi',
    'Posisi Security Engineer - Managed Service (EDR/DLP) di PT Dikstra Cipta Solusi. Kategori: Computer & Software. Gaji: Rp 6 jt-13 jt. Pengalaman: 1–3 tahun.',
    '["security"]'::jsonb,
    'Jakarta Selatan, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/security-engineer-managed-service-edr-dlp/37f013b1-b791-428a-8ae2-61d1da3d474c',
    NOW()
  ),

  -- 13. Backend Engineer - Keda Tech
  (
    gen_random_uuid()::TEXT,
    'Backend Engineer',
    'Keda Tech',
    'Posisi Backend Engineer di Keda Tech. Kategori: Computer & Software. Gaji: Tidak Ditampilkan. Pengalaman: 1–3 tahun.',
    '["backend"]'::jsonb,
    'Jakarta Barat, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/backend-engineer/37bd74e3-63ba-4584-984c-6c9c50555deb',
    NOW()
  ),

  -- 14. Cobol Developer - PT Sigma Global Teknologi
  (
    gen_random_uuid()::TEXT,
    'Cobol Developer',
    'PT Sigma Global Teknologi',
    'Posisi Cobol Developer di PT Sigma Global Teknologi. Kategori: Computer & Software. Gaji: Rp 12 jt-17 jt. Tipe: Kontrak. Pengalaman: 3–5 tahun.',
    '["cobol"]'::jsonb,
    'Jakarta Selatan, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/cobol-developer/375e945e-29ad-4c96-bd2e-0ba214f2f992',
    NOW()
  ),

  -- 15. Senior Fronted Developer - PT. Satu Visi Digital
  (
    gen_random_uuid()::TEXT,
    'Senior Fronted Developer',
    'PT. Satu Visi Digital',
    'Posisi Senior Frontend Developer di PT. Satu Visi Digital. Kategori: Computer & Software. Gaji: Tidak Ditampilkan. Pengalaman: 3–5 tahun.',
    '["frontend"]'::jsonb,
    'Jakarta Barat, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/senior-fronted-developer/374e3c70-2376-434c-9b39-16748e34a533',
    NOW()
  ),

  -- 16. Cloud Engineer Mid Level - Pt. Tiga Daya Digital Indonesia
  (
    gen_random_uuid()::TEXT,
    'Cloud Engineer Mid Level',
    'Pt. Tiga Daya Digital Indonesia',
    'Posisi Cloud Engineer Mid Level di Pt. Tiga Daya Digital Indonesia. Kategori: Computer & Software. Gaji: Rp 10 jt-15 jt. Tipe: Kontrak. Pengalaman: 3–5 tahun.',
    '["cloud"]'::jsonb,
    'Jakarta Selatan, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/cloud-engineer-mid-level/3749c25d-53f3-4334-ad7d-88f77fa3359a',
    NOW()
  ),

  -- 17. Engineer Support - PT Sanwamas Metal Industry
  (
    gen_random_uuid()::TEXT,
    'Engineer Support',
    'PT Sanwamas Metal Industry',
    'Posisi Engineer Support di PT Sanwamas Metal Industry. Kategori: Computer & Software. Gaji: Tidak Ditampilkan. Tipe: Kontrak. Pengalaman: 1–3 tahun.',
    '[]'::jsonb,
    'Bekasi, Jawa Barat',
    'https://glints.com/id/opportunities/jobs/engineer-support/25e19783-20a3-4894-9461-bdb97ea19ca2',
    NOW()
  ),

  -- 18. IT Compliance - PT GDC Multi Sarana (Jakarta)
  (
    gen_random_uuid()::TEXT,
    'IT Compliance',
    'PT GDC Multi Sarana (Jakarta)',
    'Posisi IT Compliance di PT GDC Multi Sarana (Jakarta). Kategori: Computer & Software. Gaji: Rp 7,5 jt-10 jt. Pengalaman: 3–5 tahun.',
    '[]'::jsonb,
    'Jakarta Selatan, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/it-compliance/126ad2be-4a68-436e-a2ef-5de7219b0b93',
    NOW()
  ),

  -- 19. Technical Support (Hosting & Cloud) - PT Qwords Company International
  (
    gen_random_uuid()::TEXT,
    'Technical Support (Hosting & Cloud)',
    'PT Qwords Company International',
    'Posisi Technical Support (Hosting & Cloud) di PT Qwords Company International. Kategori: Computer & Software. Gaji: Rp 4,5 jt-6 jt. Pengalaman: 1–3 tahun.',
    '["cloud"]'::jsonb,
    'Bandung, Jawa Barat',
    'https://glints.com/id/opportunities/jobs/technical-support-hosting-and-cloud/0d4e4039-e614-4eb4-a8ea-a7a54a28bf07',
    NOW()
  ),

  -- 20. Support Engineer - Pt Dua Empat Tujuh
  (
    gen_random_uuid()::TEXT,
    'Support Engineer',
    'Pt Dua Empat Tujuh',
    'Posisi Support Engineer di Pt Dua Empat Tujuh. Kategori: Computer & Software. Gaji: Rp 2,8 jt-3,5 jt. Tipe: Kontrak. Pengalaman: Tidak disebutkan.',
    '[]'::jsonb,
    'Yogyakarta, DI Yogyakarta',
    'https://glints.com/id/opportunities/jobs/support-engineer/0d0f8f27-099a-46bd-aad1-4e084622f756',
    NOW()
  ),

  -- 21. IT Support - Ultimo Solution
  (
    gen_random_uuid()::TEXT,
    'IT Support',
    'Ultimo Solution',
    'Posisi IT Support di Ultimo Solution. Kategori: Computer & Software. Gaji: Rp 2 jt-3 jt. Tipe: Kontrak. Pengalaman: 1–3 tahun.',
    '[]'::jsonb,
    'Kab. Bandung Barat, Jawa Barat',
    'https://glints.com/id/opportunities/jobs/it-support/0aa62690-fb12-46f8-bfaf-d88e6256e2f1',
    NOW()
  ),

  -- 22. Spesialis IT Support - PT. Bumi Mentari Cemerlang
  (
    gen_random_uuid()::TEXT,
    'Spesialis IT Support',
    'PT. Bumi Mentari Cemerlang',
    'Posisi Spesialis IT Support di PT. Bumi Mentari Cemerlang. Kategori: Computer & Software. Gaji: Rp 4 jt-5 jt. Tipe: Kontrak. Pengalaman: 1–3 tahun.',
    '[]'::jsonb,
    'Tangerang, Banten',
    'https://glints.com/id/opportunities/jobs/spesialis-it-support/3552dfc3-f7b8-4a2b-a3da-151a8ea3c1df',
    NOW()
  ),

  -- 23. Quality Assurance – Core Banking (Temenos T24) - PT Sigma Global Teknologi
  (
    gen_random_uuid()::TEXT,
    'Quality Assurance – Core Banking (Temenos T24)',
    'PT Sigma Global Teknologi',
    'Posisi Quality Assurance – Core Banking (Temenos T24) di PT Sigma Global Teknologi. Kategori: Computer & Software. Gaji: Rp 8,4 jt-8,9 jt. Tipe: Kontrak. Pengalaman: 3–5 tahun.',
    '["qa", "quality assurance"]'::jsonb,
    'Jakarta Selatan, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/quality-assurance-core-banking-temenos-t24/3478d28a-06fe-43fd-acfd-47f85b2f579a',
    NOW()
  ),

  -- 24. Teknisi Network Operations Center (NOC) - PT Trans Hybrid Communication
  (
    gen_random_uuid()::TEXT,
    'Teknisi Network Operations Center (NOC)',
    'PT Trans Hybrid Communication',
    'Posisi Teknisi Network Operations Center (NOC) di PT Trans Hybrid Communication. Kategori: Computer & Software. Gaji: Rp 5,5 jt-6,5 jt. Tipe: Kontrak. Pengalaman: 1–3 tahun.',
    '["network"]'::jsonb,
    'Depok, Jawa Barat',
    'https://glints.com/id/opportunities/jobs/teknisi-network-operations-center-noc/345f03a3-d25b-4d0b-815f-afc53adb9ed0',
    NOW()
  ),

  -- 25. Data Analyst Intern - PT Magenta Indopack Sejahtera
  (
    gen_random_uuid()::TEXT,
    'Data Analyst Intern',
    'PT Magenta Indopack Sejahtera',
    'Posisi Data Analyst Intern di PT Magenta Indopack Sejahtera. Kategori: Computer & Software. Gaji: Rp 800 rb-1 jt. Pengalaman: Tidak disebutkan.',
    '["data analyst"]'::jsonb,
    'Kab. Sleman, DI Yogyakarta',
    'https://glints.com/id/opportunities/jobs/data-analyst-intern/34387d92-80da-4686-9ae0-b4a74538a40c',
    NOW()
  ),

  -- 26. Network Engineer - PT Berca Hardayaperkasa
  (
    gen_random_uuid()::TEXT,
    'Network Engineer',
    'PT Berca Hardayaperkasa',
    'Posisi Network Engineer di PT Berca Hardayaperkasa. Kategori: Computer & Software. Gaji: Rp 6 jt-7 jt. Tipe: Kontrak. Pengalaman: 1–3 tahun.',
    '["network"]'::jsonb,
    'Jakarta Pusat, DKI Jakarta',
    'https://glints.com/id/opportunities/jobs/network-engineer/3075cd93-398e-49da-9bce-55a063c555c3',
    NOW()
  ),

  -- 27. Full Stack Developer - PT Andara Rejo Makmur
  (
    gen_random_uuid()::TEXT,
    'Full Stack Developer',
    'PT Andara Rejo Makmur',
    'Posisi Full Stack Developer di PT Andara Rejo Makmur. Kategori: Computer & Software. Gaji: Rp 2 jt-2,7 jt. Pengalaman: 3–5 tahun.',
    '["full stack", "fullstack"]'::jsonb,
    'Kab. Klaten, Jawa Tengah',
    'https://glints.com/id/opportunities/jobs/full-stack-developer/18a6004e-e96e-4b5c-ae52-66774ad0a10c',
    NOW()
  ),

  -- 28. IOT Developer - Kalimantan Timur (Mining Industry) - PT Sigma Global Teknologi
  (
    gen_random_uuid()::TEXT,
    'IOT Developer - Kalimantan Timur (Mining Industry)',
    'PT Sigma Global Teknologi',
    'Posisi IOT Developer di PT Sigma Global Teknologi. Lokasi: Kalimantan Timur (Mining Industry). Kategori: Computer & Software. Gaji: Rp 5,5 jt-5,7 jt. Tipe: Kontrak. Pengalaman: 3–5 tahun.',
    '["iot"]'::jsonb,
    'Balikpapan, Kalimantan Timur',
    'https://glints.com/id/opportunities/jobs/iot-developer-kalimantan-timur-mining-industry/1430a3da-ef17-4d43-bcd5-13991432f7c1',
    NOW()
  ),

  -- 29. Web Developer (Java, Golang + Rust) - Banking Industry - PT Sigma Global Teknologi
  (
    gen_random_uuid()::TEXT,
    'Web Developer (Java, Golang + Rust) - Banking Industry',
    'PT Sigma Global Teknologi',
    'Posisi Web Developer (Java, Golang + Rust) di PT Sigma Global Teknologi. Banking Industry. Kategori: Computer & Software. Gaji: Rp 15 jt. Tipe: Kontrak. Pengalaman: 5–10 tahun.',
    '["java", "golang", "go", "rust"]'::jsonb,
    'Tangerang Selatan, Banten',
    'https://glints.com/id/opportunities/jobs/web-developer-java-golang-rust-banking-industry/09d95471-e594-4311-893d-6c56eccb2eb2',
    NOW()
  ),

  -- 30. Full Stack Developer - CV Solusi Cipta Media
  (
    gen_random_uuid()::TEXT,
    'Full Stack Developer',
    'CV Solusi Cipta Media',
    'Posisi Full Stack Developer di CV Solusi Cipta Media. Kategori: Computer & Software. Gaji: Tidak Ditampilkan. Pengalaman: 1–3 tahun.',
    '["full stack", "fullstack"]'::jsonb,
    'Malang, Jawa Timur',
    'https://glints.com/id/opportunities/jobs/full-stack-developer/d8171d02-5091-4e54-acda-53f928227a59',
    NOW()
  )

ON CONFLICT (source_url) DO NOTHING;

-- ── Step 4: Verifikasi ─────────────────────────────────────────────────────
SELECT 
  'Total jobs di database: ' || COUNT(*)::TEXT AS status
FROM jobs;

SELECT 
  title, company, location, skills, source_url
FROM jobs
ORDER BY scraped_at DESC
LIMIT 35;
