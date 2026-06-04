import csv
import random
import uuid
from datetime import datetime, timedelta

# Pre-defined lists for fast generation of 10,000+ rows without relying heavily on slow Faker loops
FIRST_NAMES = ["Budi", "Siti", "Andi", "Dewi", "Eko", "Rina", "Rudi", "Agus", "Sri", "Bambang", "Mega", "Fajar", "Deni", "Anita", "Hendra", "Yanto", "Rian", "Putri", "Taufik", "Ahmad", "Naufal", "Albi", "Jennifer", "Velicia", "Orell", "Bagus", "Fikran", "Rizky", "Aditya", "Amalia"]
LAST_NAMES = ["Utomo", "Susanto", "Wijaya", "Saputra", "Hidayat", "Sitorus", "Nasution", "Prabowo", "Kurniawan", "Sari", "Lestari", "Putra", "Putri", "Setiawan", "Ramadhan", "Nugroho", "Gunawan", "Budiman", "Santoso", "Siregar"]

COMPANY_PREFIX = ["Sinergi", "Solusi", "Inovasi", "Global", "Nusantara", "Digital", "Pratama", "Karya", "Inti", "Sentosa", "Utama", "Tekno", "Media", "Berjaya", "Maju", "Lancar", "Artha", "Citra", "Nusa", "Buana"]
COMPANY_SUFFIX = ["Teknologi", "Digital Indonesia", "Software", "Analitika", "Creative", "System", "Cloud", "Sistem", "Data", "Hub"]

JOB_TITLES = [
    "Data Scientist", "Data Analyst", "Machine Learning Engineer", 
    "Backend Developer", "Frontend Developer", "Full Stack Developer",
    "UI/UX Designer", "Product Manager", "IT Recruiter", "DevOps Engineer"
]

EXPERIENCE_LEVELS = ["Entry Level", "1-3 Tahun", "3-5 Tahun", "Senior Level"]

SKILL_MAP = {
    "Data": ["Python", "SQL", "TensorFlow", "Pandas", "Machine Learning", "Statistika", "Data Visualization", "Tableau", "Scikit-learn", "R", "PowerBI"],
    "Developer": ["JavaScript", "Python", "FastAPI", "Nuxt.js", "Vue.js", "PostgreSQL", "Docker", "Git", "TypeScript", "Node.js", "React", "MongoDB", "Redis"],
    "Design": ["Figma", "UI/UX", "Wireframing", "Prototyping", "User Research", "Adobe Illustrator", "Photoshop", "Design System"],
    "Management": ["Agile", "Scrum", "Jira", "Leadership", "Komunikasi", "Project Management", "Problem Solving", "Strategic Planning", "Negosiasi"]
}

PROFILES = {
    "Data": {
        "roles": ["Junior Data Analyst", "Asisten Peneliti", "Staf Administrasi Data", "Fresh Graduate Matematika", "Statistisi Junior"],
        "skills": ["Python", "SQL", "Excel", "Tableau", "Statistika", "Data Visualization", "Problem Solving"]
    },
    "Developer": {
        "roles": ["Junior Programmer", "IT Support", "Technical Writer", "Web Developer Magang", "Asisten Laboratorium Komputer"],
        "skills": ["JavaScript", "Python", "HTML/CSS", "PostgreSQL", "Git", "Problem Solving", "Komunikasi"]
    },
    "Design": {
        "roles": ["Graphic Designer", "Staf Marketing", "Content Creator", "UI Designer Magang", "Social Media Specialist"],
        "skills": ["Figma", "UI/UX", "Adobe Illustrator", "Prototyping", "User Research", "Kreativitas"]
    },
    "Management": {
        "roles": ["Ketua BEM", "Project Administrator", "Sales Executive", "HR Staff", "Business Development Intern"],
        "skills": ["Leadership", "Komunikasi", "Manajemen Waktu", "Agile", "Microsoft Office", "Negosiasi"]
    }
}

UNIVERSITIES = [
    "Institut Teknologi Bandung (ITB)", "Universitas Indonesia (UI)", 
    "Universitas Gadjah Mada (UGM)", "Institut Teknologi Sepuluh Nopember (ITS)", 
    "Universitas Telkom", "Universitas Padjadjaran", "Binus University", "Universitas Airlangga"
]

def generate_company_name():
    p = random.choice(COMPANY_PREFIX)
    s = random.choice(COMPANY_SUFFIX)
    t = "Tbk" if random.random() > 0.8 else "PT"
    if t == "PT":
        return f"PT {p} {s}"
    else:
        return f"PT {p} {s} Tbk"

def generate_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

# 1. Generate 10,000 Job Records
jobs_filename = "dummy_jobs_10k.csv"
headers_jobs = ["job_id", "job_title", "company_name", "industry_category", "raw_description", "extracted_skills", "experience_level", "posted_date"]

start_date = datetime.now() - timedelta(days=365)

with open(jobs_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers_jobs)
    writer.writeheader()
    
    for i in range(10000):
        title = random.choice(JOB_TITLES)
        
        if "Data" in title or "Machine Learning" in title:
            category = "Data"
        elif "Developer" in title or "Engineer" in title:
            category = "Developer"
        elif "Designer" in title:
            category = "Design"
        else:
            category = "Management"
            
        core_skills = random.sample(SKILL_MAP[category], k=random.randint(3, min(6, len(SKILL_MAP[category]))))
        soft_skills = random.sample(SKILL_MAP["Management"], k=random.randint(1, 2))
        extracted_skills = list(set(core_skills + soft_skills))
        
        company = generate_company_name()
        
        raw_description = (
            f"Kami di {company} sedang membuka kesempatan karir untuk posisi {title}. "
            f"Kandidat yang ideal diharapkan mampu beradaptasi cepat dalam lingkungan teknologi yang dinamis. "
            f"Tanggung jawab utama meliputi eksekusi proyek strategis dan kolaborasi lintas divisi. "
            f"Kualifikasi teknis wajib: Menguasai {', '.join(extracted_skills[:-1])}, serta {extracted_skills[-1]}. "
            f"Memiliki kemampuan problem solving yang baik sangat diutamakan."
        )
        
        posted_date = start_date + timedelta(minutes=random.randint(0, 525600)) # Random minute within 1 year
        
        writer.writerow({
            "job_id": str(uuid.uuid4()),
            "job_title": title,
            "company_name": company,
            "industry_category": "Teknologi & Informasi",
            "raw_description": raw_description,
            "extracted_skills": ", ".join(extracted_skills),
            "experience_level": random.choice(EXPERIENCE_LEVELS),
            "posted_date": posted_date.strftime("%Y-%m-%d %H:%M:%S")
        })

# 2. Generate 10,000 CV Records
cvs_filename = "dummy_cvs_10k.csv"
headers_cvs = ["user_id", "name", "last_role", "raw_cv_text", "extracted_user_skills"]

with open(cvs_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers_cvs)
    writer.writeheader()
    
    for i in range(10000):
        category = random.choice(list(PROFILES.keys()))
        last_role = random.choice(PROFILES[category]["roles"])
        user_skills = random.sample(PROFILES[category]["skills"], k=random.randint(3, 5))
        
        name = generate_name()
        university = random.choice(UNIVERSITIES)
        graduation_year = random.randint(2021, 2026)
        company = generate_company_name()
        
        raw_cv_text = (
            f"Curriculum Vitae Ringkas | Nama: {name} | Kontak: {name.lower().replace(' ', '')}@email.com\n"
            f"Riwayat Pendidikan: {university}, Kelulusan Tahun {graduation_year}.\n"
            f"Pengalaman Profesional Terakhir: Bekerja sebagai {last_role} di {company}.\n"
            f"Deskripsi Kompetensi: Saya memiliki dedikasi tinggi dalam menyelesaikan tugas-tugas analitis maupun teknis. "
            f"Keahlian utama yang saya miliki dan sering saya terapkan meliputi {', '.join(user_skills[:-1])}, serta {user_skills[-1]}. "
            f"Saat ini berkomitmen penuh untuk melakukan akselerasi karir dan transisi kompetensi menuju industri digital dan ekosistem teknologi."
        )
        
        writer.writerow({
            "user_id": str(uuid.uuid4()),
            "name": name,
            "last_role": last_role,
            "raw_cv_text": raw_cv_text.replace("\n", " "),
            "extracted_user_skills": ", ".join(user_skills)
        })

print("Generation complete.")