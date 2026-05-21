-- SkillScout Nusantara — inisialisasi database PostgreSQL
-- Jalankan sekali: psql $DATABASE_URL < migrations/init.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Lowongan kerja hasil scraping
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

-- CV yang diupload pengguna
CREATE TABLE IF NOT EXISTS cv_uploads (
    id            TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    filename      VARCHAR(255) NOT NULL,
    storage_path  VARCHAR(500) NOT NULL,
    raw_text      TEXT,
    skills        JSONB        NOT NULL DEFAULT '[]',
    uploaded_at   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Log hasil pencocokan
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
