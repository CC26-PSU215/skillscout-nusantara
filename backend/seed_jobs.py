"""
Script untuk seed data lowongan kerja ke database.
Jalankan: python seed_jobs.py
"""
import httpx
import time

API_URL = "http://localhost:8000/api/jobs"

SAMPLE_JOBS = [
    {
        "title": "Data Scientist",
        "company": "Gojek",
        "description": "Bergabunglah dengan tim Data Science Gojek untuk mengembangkan model machine learning yang mendukung jutaan pengguna. Anda akan bekerja dengan big data, membangun model prediktif, dan mengoptimalkan algoritma rekomendasi. Keahlian dalam Python, TensorFlow, dan analisis statistik sangat diutamakan.",
        "skills": ["python", "machine learning", "tensorflow", "pandas", "numpy", "postgresql", "docker"],
        "location": "Jakarta",
        "source_url": "https://www.gojek.com/careers"
    },
    {
        "title": "Backend Engineer",
        "company": "Bukalapak",
        "description": "Kami membutuhkan Backend Engineer untuk merancang dan mengembangkan layanan mikro yang skalabel. Anda akan bertanggung jawab atas arsitektur sistem, optimasi database, dan integrasi API. Pengalaman dengan Golang, PostgreSQL, dan Kubernetes menjadi nilai tambah.",
        "skills": ["golang", "postgresql", "kubernetes", "docker", "rest api", "redis", "git"],
        "location": "Bandung",
        "source_url": "https://www.bukalapak.com/careers"
    },
    {
        "title": "Frontend Developer (React)",
        "company": "Traveloka",
        "description": "Traveloka mencari Frontend Developer yang bersemangat untuk membangun antarmuka pengguna yang indah dan responsif. Anda akan bekerja dengan React, TypeScript, dan framework modern untuk menciptakan pengalaman booking travel terbaik di Asia Tenggara.",
        "skills": ["react", "typescript", "javascript", "nextjs", "git", "rest api"],
        "location": "Jakarta",
        "source_url": "https://www.traveloka.com/careers"
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Shopee Indonesia",
        "description": "Posisi Machine Learning Engineer di Shopee Indonesia untuk mengembangkan sistem rekomendasi produk dan search ranking. Anda akan membangun pipeline data, melatih model deep learning, dan mendeploy model ke production dengan skala besar.",
        "skills": ["python", "pytorch", "machine learning", "deep learning", "docker", "kubernetes", "aws"],
        "location": "Jakarta",
        "source_url": "https://careers.shopee.co.id"
    },
    {
        "title": "DevOps Engineer",
        "company": "Dana Indonesia",
        "description": "Dana Indonesia membutuhkan DevOps Engineer untuk mengelola infrastruktur cloud dan CI/CD pipeline. Anda akan bekerja dengan Docker, Kubernetes, dan AWS untuk memastikan ketersediaan tinggi dan skalabilitas sistem fintech kami.",
        "skills": ["docker", "kubernetes", "aws", "linux", "git", "python"],
        "location": "Jakarta",
        "source_url": "https://www.dana.id/careers"
    },
    {
        "title": "Mobile Developer (Android)",
        "company": "OVO",
        "description": "OVO mencari Mobile Developer Android untuk mengembangkan aplikasi fintech yang digunakan jutaan pengguna Indonesia. Pengalaman dengan Kotlin, arsitektur MVVM, dan integrasi REST API sangat diperlukan.",
        "skills": ["kotlin", "java", "rest api", "git", "postgresql"],
        "location": "Jakarta",
        "source_url": "https://www.ovo.id/careers"
    },
    {
        "title": "Data Analyst",
        "company": "Blibli.com",
        "description": "Blibli mencari Data Analyst untuk menganalisis data penjualan, perilaku pengguna, dan tren pasar. Anda akan menggunakan SQL, Python, dan tools visualisasi data untuk memberikan insight yang actionable kepada tim bisnis.",
        "skills": ["python", "postgresql", "data analysis", "pandas", "communication"],
        "location": "Jakarta",
        "source_url": "https://www.blibli.com/careers"
    },
    {
        "title": "AI Engineer",
        "company": "Telkom Indonesia",
        "description": "Telkom Indonesia membuka posisi AI Engineer untuk mengembangkan solusi NLP dan computer vision. Anda akan bekerja dengan model deep learning, memproses bahasa Indonesia, dan mengintegrasikan AI ke dalam produk enterprise.",
        "skills": ["python", "tensorflow", "nlp", "deep learning", "docker", "fastapi"],
        "location": "Bandung",
        "source_url": "https://www.telkom.co.id/careers"
    },
    {
        "title": "Full Stack Engineer (Python + React)",
        "company": "Xendit",
        "description": "Xendit mencari Full Stack Engineer untuk membangun infrastruktur pembayaran digital. Anda akan mengembangkan RESTful API menggunakan FastAPI/Django dan frontend dengan React. Pengalaman dengan PostgreSQL dan Docker sangat diutamakan.",
        "skills": ["python", "react", "fastapi", "postgresql", "docker", "typescript", "rest api", "git"],
        "location": "Jakarta",
        "source_url": "https://www.xendit.co/careers"
    },
    {
        "title": "Cloud Engineer",
        "company": "Tiket.com",
        "description": "Tiket.com membutuhkan Cloud Engineer untuk mengelola infrastruktur cloud di GCP. Anda akan bertanggung jawab atas keamanan cloud, monitoring, dan optimasi biaya infrastruktur.",
        "skills": ["gcp", "kubernetes", "docker", "linux", "python", "git"],
        "location": "Jakarta",
        "source_url": "https://www.tiket.com/careers"
    },
    {
        "title": "Software Engineer",
        "company": "Grab Indonesia",
        "description": "Grab Indonesia mencari Software Engineer untuk tim ride-hailing. Pengalaman dalam membangun sistem terdistribusi, microservices, dan real-time processing sangat dibutuhkan. Familiar dengan Java, Golang, atau Python.",
        "skills": ["java", "golang", "python", "kubernetes", "docker", "redis", "postgresql"],
        "location": "Jakarta",
        "source_url": "https://grab.careers"
    },
    {
        "title": "Quality Assurance Engineer",
        "company": "Kompas Gramedia Digital",
        "description": "Kompas Gramedia Digital membutuhkan QA Engineer untuk memastikan kualitas produk digital kami. Anda akan melakukan testing manual dan otomatis, menulis test script, dan berkolaborasi dengan tim development.",
        "skills": ["python", "javascript", "git", "rest api", "communication"],
        "location": "Jakarta",
        "source_url": "https://www.kompasgramedia.com/careers"
    },
    {
        "title": "Product Manager (Tech)",
        "company": "Ruangguru",
        "description": "Ruangguru mencari Product Manager untuk memimpin pengembangan produk edtech. Anda akan mendefinisikan roadmap produk, bekerja dengan tim engineering dan design, serta menganalisis metrik produk.",
        "skills": ["data analysis", "communication", "leadership", "project management"],
        "location": "Jakarta",
        "source_url": "https://www.ruangguru.com/careers"
    },
    {
        "title": "Database Administrator",
        "company": "Bank Mandiri",
        "description": "Bank Mandiri membutuhkan Database Administrator untuk mengelola database critical banking system. Pengalaman dengan PostgreSQL, MySQL, dan database performance tuning sangat diperlukan.",
        "skills": ["postgresql", "mysql", "linux", "python", "docker"],
        "location": "Jakarta",
        "source_url": "https://www.bankmandiri.co.id/careers"
    },
    {
        "title": "Cybersecurity Analyst",
        "company": "Bank Central Asia (BCA)",
        "description": "BCA mencari Cybersecurity Analyst untuk mengamankan infrastruktur perbankan digital. Anda akan melakukan vulnerability assessment, incident response, dan implementasi security best practices.",
        "skills": ["linux", "python", "aws", "docker", "communication"],
        "location": "Jakarta",
        "source_url": "https://www.bca.co.id/careers"
    },
]

def seed():
    client = httpx.Client(timeout=30)
    for i, job in enumerate(SAMPLE_JOBS, 1):
        try:
            resp = client.post(API_URL, json=job)
            resp.raise_for_status()
            data = resp.json()
            print(f"[{i}/{len(SAMPLE_JOBS)}] ✅ {data['title']} @ {data['company']} (ID: {data['id'][:8]}...)")
        except Exception as e:
            print(f"[{i}/{len(SAMPLE_JOBS)}] ❌ {job['title']} — {e}")
        time.sleep(0.2)  # Rate limiting
    print(f"\n🎉 Selesai! {len(SAMPLE_JOBS)} lowongan telah di-seed.")

if __name__ == "__main__":
    seed()
