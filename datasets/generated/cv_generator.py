"""
Synthetic CV Generator for SkillScout Nusantara
Generates realistic fake CVs for testing CV-to-Job matching system

Usage:
    python cv_generator.py

Output:
    data/raw/cvs_junior.json (100 CVs)
    data/raw/cvs_mid.json (100 CVs)
    data/raw/cvs_senior.json (100 CVs)
    data/raw/cvs_lead.json (100 CVs)
"""

import json
import random
from datetime import datetime, timedelta
import os


class CVGenerator:
    """Generate synthetic CV data for testing"""
    
    # Skills pool
    SKILLS = {
        'tech': [
            'Python', 'JavaScript', 'Java', 'C++', 'C#',
            'React', 'Vue.js', 'Angular', 'Node.js', 'Django',
            'Flask', 'FastAPI', 'Spring Boot', 'Laravel', 'Ruby on Rails',
            'PostgreSQL', 'MongoDB', 'MySQL', 'Redis', 'ElasticSearch',
            'AWS', 'Google Cloud', 'Azure', 'Docker', 'Kubernetes',
            'Git', 'CI/CD', 'Jenkins', 'Terraform', 'Linux',
            'Machine Learning', 'TensorFlow', 'PyTorch', 'Scikit-Learn',
            'Data Analysis', 'Pandas', 'NumPy', 'SQL', 'Spark',
            'REST API', 'GraphQL', 'Microservices', 'Agile'
        ],
        'soft': [
            'Leadership', 'Team Management', 'Communication', 'Presentation',
            'Problem Solving', 'Critical Thinking', 'Creativity',
            'Project Management', 'Stakeholder Management', 'Mentoring',
            'Adaptability', 'Time Management', 'Collaboration'
        ],
        'tools': [
            'Excel', 'SQL', 'Tableau', 'Power BI', 'Jira',
            'Slack', 'Confluence', 'Notion', 'Git', 'UNIX',
            'AWS Console', 'Docker', 'Postman', 'VS Code'
        ]
    }
    
    # Job titles by experience level
    TITLES = {
        'junior': [
            'Junior Developer',
            'Junior Software Engineer',
            'Associate Software Engineer',
            'Entry-Level Developer',
            'Junior Full Stack Developer',
            'Junior Backend Engineer'
        ],
        'mid': [
            'Software Engineer',
            'Senior Developer',
            'Full Stack Engineer',
            'Backend Engineer',
            'Frontend Engineer',
            'Data Engineer',
            'DevOps Engineer'
        ],
        'senior': [
            'Senior Software Engineer',
            'Senior Developer',
            'Staff Engineer',
            'Senior Full Stack Engineer',
            'Principal Engineer',
            'Tech Lead'
        ],
        'lead': [
            'Engineering Manager',
            'Engineering Director',
            'Principal Architect',
            'VP of Engineering',
            'CTO',
            'VP of Technology'
        ]
    }
    
    # Company names (Indonesian context)
    COMPANIES = [
        'PT ABC Indonesia', 'PT Tech Corp', 'PT Digital Agency',
        'PT E-Commerce Platform', 'PT FinTech Indonesia',
        'PT Cloud Services Provider', 'PT Consulting Firm',
        'PT Software House', 'PT IT Solutions', 'PT Startup XYZ',
        'PT Innovation Lab', 'PT Digital Transform',
        'PT Enterprise Solutions', 'Bandung Tech', 'Jakarta Digital',
        'Surabaya Tech Hub', 'Indonesia Cloud', 'Indo Software'
    ]
    
    # Education
    EDUCATION = [
        {'degree': 'Bachelor', 'field': 'Computer Science', 'uni': 'ITB'},
        {'degree': 'Bachelor', 'field': 'Information Technology', 'uni': 'UI'},
        {'degree': 'Bachelor', 'field': 'Software Engineering', 'uni': 'UNAIR'},
        {'degree': 'Master', 'field': 'Computer Science', 'uni': 'ITB'},
        {'degree': 'Diploma', 'field': 'Information Technology', 'uni': 'Politeknik'},
        {'degree': 'Bachelor', 'field': 'Engineering', 'uni': 'Universitas Gajah Mada'},
        {'degree': 'Bachelor', 'field': 'Information Systems', 'uni': 'Binus University'},
    ]
    
    # Experience level configurations
    EXPERIENCE_CONFIG = {
        'junior': {
            'years': (0, 2),
            'num_jobs': (1, 3),
            'job_years': (0.5, 1.5)
        },
        'mid': {
            'years': (2, 5),
            'num_jobs': (2, 4),
            'job_years': (1, 3)
        },
        'senior': {
            'years': (5, 10),
            'num_jobs': (3, 5),
            'job_years': (1.5, 4)
        },
        'lead': {
            'years': (10, 20),
            'num_jobs': (4, 7),
            'job_years': (2, 6)
        }
    }
    
    def __init__(self, seed=None):
        """Initialize generator"""
        if seed:
            random.seed(seed)
    
    @staticmethod
    def generate_cv(experience_level='mid', num_cvs=100):
        """
        Generate synthetic CVs
        
        Args:
            experience_level: 'junior', 'mid', 'senior', or 'lead'
            num_cvs: number of CVs to generate
        
        Returns:
            List of CV dictionaries
        """
        cvs = []
        config = CVGenerator.EXPERIENCE_CONFIG[experience_level]
        
        for i in range(num_cvs):
            # Generate years of experience
            years_exp = random.randint(*config['years'])
            
            # Generate number of jobs
            num_jobs = random.randint(*config['num_jobs'])
            
            # Build experience entries
            experiences = []
            end_date = datetime.now()
            
            for j in range(num_jobs):
                job_years = random.uniform(*config['job_years'])
                start_date = end_date - timedelta(days=job_years * 365)
                
                experiences.append({
                    'title': random.choice(CVGenerator.TITLES[experience_level]),
                    'company': random.choice(CVGenerator.COMPANIES),
                    'start_date': start_date.strftime('%Y-%m'),
                    'end_date': end_date.strftime('%Y-%m'),
                    'duration_months': int(job_years * 12),
                    'description': CVGenerator._generate_job_description()
                })
                
                end_date = start_date - timedelta(days=30)  # Gap between jobs
            
            # Select skills appropriate for level
            num_technical = {
                'junior': 4,
                'mid': 6,
                'senior': 8,
                'lead': 7
            }[experience_level]
            
            cv = {
                'cv_id': f'{experience_level}_{i:05d}',
                'personal_info': {
                    'name': f'{experience_level.title()}_Prof_{i:03d}',
                    'email': f'{experience_level}{i}@email.com',
                    'phone': f'+62-812-{random.randint(10000000, 99999999)}',
                    'location': random.choice([
                        'Jakarta', 'Bandung', 'Surabaya',
                        'Yogyakarta', 'Medan', 'Bali'
                    ]),
                    'linkedin': f'linkedin.com/in/{experience_level}{i}'
                },
                'summary': CVGenerator._generate_summary(experience_level, years_exp),
                'experience': experiences,
                'education': random.choice(CVGenerator.EDUCATION),
                'skills': {
                    'technical': random.sample(CVGenerator.SKILLS['tech'], k=num_technical),
                    'soft': random.sample(CVGenerator.SKILLS['soft'], k=3),
                    'tools': random.sample(CVGenerator.SKILLS['tools'], k=2)
                },
                'certifications': CVGenerator._generate_certifications(experience_level),
                'years_experience': years_exp,
                'experience_level': experience_level,
                'generated_at': datetime.now().isoformat(),
                'raw_cv_text': ''  # Will be populated with full CV text
            }
            
            # Generate raw CV text
            cv['raw_cv_text'] = CVGenerator._generate_raw_text(cv)
            
            cvs.append(cv)
        
        return cvs
    
    @staticmethod
    def _generate_summary(level, years):
        """Generate professional summary"""
        summaries = {
            'junior': f'Recent graduate with {years} year(s) of software development experience. Passionate about learning new technologies and contributing to innovative projects.',
            'mid': f'Software engineer with {years} years of experience in full-stack development. Experienced in building scalable applications and mentoring junior developers.',
            'senior': f'Senior software engineer with {years} years of experience in architecting and delivering enterprise solutions. Strong track record of leading technical teams and driving innovation.',
            'lead': f'Engineering leader with {years} years of experience building and scaling high-performing technical teams. Expertise in strategic technical planning and organizational growth.'
        }
        return summaries.get(level, 'Professional software engineer')
    
    @staticmethod
    def _generate_job_description():
        """Generate realistic job description"""
        descriptions = [
            'Developed and maintained RESTful APIs serving 1M+ daily users. Led code reviews and mentored 3 junior developers.',
            'Built microservices architecture using Docker and Kubernetes. Improved system performance by 40%.',
            'Implemented real-time data processing pipeline using Apache Spark. Reduced data latency from 24h to 5 minutes.',
            'Led cross-functional team of 5 engineers. Delivered major product feature 2 weeks ahead of schedule.',
            'Architected cloud infrastructure on AWS. Reduced infrastructure costs by 30% while improving availability.',
            'Developed machine learning models for recommendation system. Improved user engagement by 25%.',
            'Implemented CI/CD pipeline using Jenkins and GitLab. Reduced deployment time from 2 hours to 5 minutes.',
            'Refactored legacy codebase resulting in 50% reduction in technical debt. Improved test coverage to 85%.'
        ]
        return random.choice(descriptions)
    
    @staticmethod
    def _generate_certifications(level):
        """Generate certifications by level"""
        all_certs = [
            'AWS Solutions Architect', 'Google Cloud Certified', 'Kubernetes Administrator',
            'Certified Scrum Master', 'Oracle Java Programmer', 'CompTIA Security+',
            'MongoDB Developer', 'Terraform Associate', 'Docker Certified'
        ]
        
        num_certs = {
            'junior': random.randint(0, 2),
            'mid': random.randint(1, 3),
            'senior': random.randint(2, 4),
            'lead': random.randint(2, 3)
        }[level]
        
        return random.sample(all_certs, k=min(num_certs, len(all_certs)))
    
    @staticmethod
    def _generate_raw_text(cv):
        """Generate full raw CV text"""
        text = f"""
{cv['personal_info']['name']}
Email: {cv['personal_info']['email']}
Phone: {cv['personal_info']['phone']}
Location: {cv['personal_info']['location']}
LinkedIn: {cv['personal_info']['linkedin']}

PROFESSIONAL SUMMARY
{cv['summary']}

EXPERIENCE
"""
        for exp in cv['experience']:
            text += f"""
{exp['title']}
{exp['company']} | {exp['start_date']} - {exp['end_date']}
{exp['description']}
"""
        
        text += f"""
EDUCATION
{cv['education']['degree']} in {cv['education']['field']}
{cv['education']['uni']}

SKILLS
Technical: {', '.join(cv['skills']['technical'])}
Soft Skills: {', '.join(cv['skills']['soft'])}
Tools: {', '.join(cv['skills']['tools'])}
"""
        
        if cv['certifications']:
            text += f"\nCERTIFICATIONS\n" + '\n'.join(cv['certifications'])
        
        return text.strip()
    
    @staticmethod
    def save_cvs_to_json(cvs, filename, output_dir='../raw/cv'):
        """Save CVs to JSON file"""
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cvs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(cvs)} CVs to {filepath}")
        return filepath
    
    @staticmethod
    def save_cvs_to_csv(cvs, filename, output_dir='../raw/cv'):
        """Save CVs to CSV (flattened format)"""
        try:
            import pandas as pd
        except ImportError:
            print("⚠️ pandas not installed. Skipping CSV export.")
            return
        
        # Flatten the CV data for CSV
        flat_data = []
        for cv in cvs:
            flat_data.append({
                'cv_id': cv['cv_id'],
                'name': cv['personal_info']['name'],
                'experience_level': cv['experience_level'],
                'years_experience': cv['years_experience'],
                'email': cv['personal_info']['email'],
                'phone': cv['personal_info']['phone'],
                'location': cv['personal_info']['location'],
                'education_degree': cv['education']['degree'],
                'education_field': cv['education']['field'],
                'technical_skills': ','.join(cv['skills']['technical']),
                'soft_skills': ','.join(cv['skills']['soft']),
                'num_jobs': len(cv['experience']),
                'num_certifications': len(cv['certifications'])
            })
        
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        df = pd.DataFrame(flat_data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"✅ Saved {len(cvs)} CVs to CSV: {filepath}")
        return filepath


def main():
    """Main execution - generate all CV levels"""
    
    print("=" * 70)
    print("🚀 SYNTHETIC CV GENERATOR - SkillScout Nusantara")
    print("=" * 70)
    
    levels = ['junior', 'mid', 'senior', 'lead']
    num_per_level = 100
    
    total_generated = 0
    
    for level in levels:
        print(f"\n📝 Generating {num_per_level} {level.upper()} level CVs...")
        
        # Generate CVs
        cvs = CVGenerator.generate_cv(experience_level=level, num_cvs=num_per_level)
        
        # Save to JSON
        json_file = f'cvs_{level}.json'
        CVGenerator.save_cvs_to_json(cvs, json_file)
        
        # Try to save to CSV
        csv_file = f'cvs_{level}.csv'
        try:
            CVGenerator.save_cvs_to_csv(cvs, csv_file)
        except Exception as e:
            print(f"⚠️ Could not save CSV: {e}")
        
        total_generated += len(cvs)
        
        # Print sample
        print(f"\n📋 Sample {level} CV (ID: {cvs[0]['cv_id']}):")
        print(f"   Name: {cvs[0]['personal_info']['name']}")
        print(f"   Experience: {cvs[0]['years_experience']} years")
        print(f"   Skills: {', '.join(cvs[0]['skills']['technical'][:3])}...")
    
    print("\n" + "=" * 70)
    print(f"✅ SUCCESS - Generated {total_generated} synthetic CVs!")
    print("=" * 70)
    print("\nOutput files:")
    for level in levels:
        print(f"  - data/raw/cvs_{level}.json")
    print("\nReady for AI Engineer to test CV-to-Job matching system!")
    print("=" * 70)


if __name__ == "__main__":
    main()