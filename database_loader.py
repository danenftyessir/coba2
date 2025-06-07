# database_loader.py - script untuk load dataset kaggle ke mysql
import os
import sys
import mysql.connector
from mysql.connector import Error
import PyPDF2
import re
from datetime import datetime, date
import json

class KaggleDatasetLoader:
    """load dataset kaggle resume ke mysql database"""
    
    def __init__(self, kaggle_path, db_config):
        self.kaggle_path = kaggle_path
        self.db_config = db_config
        self.connection = None
        
        # kategori yang akan diambil (20 data per kategori)
        self.categories = [
            'ACCOUNTANT', 'ADVOCATE', 'AGRICULTURE', 'APPAREL', 'ARTS',
            'AUTOMOBILE', 'AVIATION', 'BANKING', 'BPO', 'BUSINESS-DEVELOPMENT',
            'CHEF', 'CONSTRUCTION', 'CONSULTANT', 'DESIGNER', 'DIGITAL-MEDIA',
            'ENGINEERING', 'FITNESS', 'HEALTHCARE', 'HR', 'INFORMATION-TECHNOLOGY'
        ]
    
    def connect_database(self):
        """koneksi ke mysql database"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("✅ koneksi database berhasil")
            return True
        except Error as e:
            print(f"❌ error koneksi database: {e}")
            return False
    
    def setup_database(self):
        """buat database dan tabel jika belum ada"""
        try:
            cursor = self.connection.cursor()
            
            # create database
            db_name = self.db_config['database']
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applicant_profile (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    address TEXT,
                    linkedin_url VARCHAR(255),
                    date_of_birth DATE,
                    skills TEXT,
                    work_experience TEXT,
                    education_history TEXT,
                    summary_overview TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS application_detail (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    applicant_id INT NOT NULL,
                    cv_path VARCHAR(255) NOT NULL,
                    job_position VARCHAR(255),
                    application_date DATE DEFAULT (CURDATE()),
                    raw_text LONGTEXT,
                    category VARCHAR(100),
                    FOREIGN KEY (applicant_id) REFERENCES applicant_profile(id) ON DELETE CASCADE
                )
            """)
            
            self.connection.commit()
            print("✅ database dan tabel berhasil dibuat")
            return True
            
        except Error as e:
            print(f"❌ error setup database: {e}")
            return False
    
    def extract_pdf_text(self, pdf_path):
        """ekstrak text dari pdf file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text.strip()
        except Exception as e:
            print(f"❌ error extract pdf {pdf_path}: {e}")
            return ""
    
    def extract_info_with_regex(self, text):
        """ekstrak informasi menggunakan regex"""
        if not text:
            return {}
        
        # regex patterns
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+',
            'skills_section': r'(?i)(?:skills?|technical skills|competencies)[\s:]*\n?((?:[^\n]+\n?){1,10})',
            'experience_section': r'(?i)(?:experience|employment|work history)[\s:]*\n?((?:[^\n]+\n?){1,15})',
            'education_section': r'(?i)(?:education|academic|qualifications)[\s:]*\n?((?:[^\n]+\n?){1,8})',
            'summary_section': r'(?i)(?:summary|profile|objective|about)[\s:]*\n?((?:[^\n]+\n?){1,5})'
        }
        
        result = {}
        
        # extract email
        email_match = re.search(patterns['email'], text)
        result['email'] = email_match.group(0) if email_match else None
        
        # extract phone
        phone_match = re.search(patterns['phone'], text)
        result['phone'] = phone_match.group(0) if phone_match else None
        
        # extract linkedin
        linkedin_match = re.search(patterns['linkedin'], text, re.IGNORECASE)
        result['linkedin_url'] = linkedin_match.group(0) if linkedin_match else None
        
        # extract skills
        skills_match = re.search(patterns['skills_section'], text, re.MULTILINE)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            skills_text = re.sub(r'\n+', ', ', skills_text)
            result['skills'] = skills_text[:500]  # limit length
        else:
            # fallback: cari tech keywords di text
            tech_keywords = [
                'python', 'java', 'javascript', 'react', 'sql', 'mysql', 'postgresql',
                'docker', 'kubernetes', 'aws', 'git', 'machine learning', 'html', 'css',
                'node.js', 'angular', 'vue', 'php', 'laravel', 'django', 'flask'
            ]
            found_skills = []
            text_lower = text.lower()
            for skill in tech_keywords:
                if skill in text_lower:
                    found_skills.append(skill)
            result['skills'] = ', '.join(found_skills[:10]) if found_skills else ''
        
        # extract work experience
        exp_match = re.search(patterns['experience_section'], text, re.MULTILINE)
        if exp_match:
            exp_text = exp_match.group(1).strip()
            result['work_experience'] = exp_text[:1000]  # limit length
        else:
            result['work_experience'] = ''
        
        # extract education
        edu_match = re.search(patterns['education_section'], text, re.MULTILINE)
        if edu_match:
            edu_text = edu_match.group(1).strip()
            result['education_history'] = edu_text[:500]  # limit length
        else:
            result['education_history'] = ''
        
        # extract summary
        summary_match = re.search(patterns['summary_section'], text, re.MULTILINE)
        if summary_match:
            summary_text = summary_match.group(1).strip()
            result['summary_overview'] = summary_text[:300]  # limit length
        else:
            result['summary_overview'] = ''
        
        return result
    
    def generate_name_from_filename(self, filename, category):
        """generate nama dari filename dan category"""
        base_name = filename.replace('.pdf', '')
        
        # extract number dari filename jika ada
        number_match = re.search(r'(\d+)', base_name)
        if number_match:
            number = number_match.group(1)
            return f"{category.title()} Candidate {number}"
        else:
            return f"{category.title()} Professional"
    
    def load_category_data(self, category, limit=20):
        """load data dari satu kategori"""
        category_path = os.path.join(self.kaggle_path, 'data', category)
        
        if not os.path.exists(category_path):
            print(f"⚠️ kategori {category} tidak ditemukan di {category_path}")
            return 0
        
        pdf_files = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
        pdf_files.sort()  # sort untuk konsistensi
        
        loaded_count = 0
        cursor = self.connection.cursor()
        
        for i, pdf_file in enumerate(pdf_files[:limit]):
            try:
                pdf_path = os.path.join(category_path, pdf_file)
                
                print(f"📄 processing {category}/{pdf_file}")
                
                # extract text dari pdf
                raw_text = self.extract_pdf_text(pdf_path)
                if not raw_text:
                    print(f"⚠️ tidak bisa extract text dari {pdf_file}")
                    continue
                
                # extract info dengan regex
                extracted_info = self.extract_info_with_regex(raw_text)
                
                # generate name
                name = self.generate_name_from_filename(pdf_file, category)
                
                # insert ke applicant_profile
                profile_data = (
                    name,
                    extracted_info.get('email', ''),
                    extracted_info.get('phone', ''),
                    f"{category.title()} Area, Indonesia",  # default address
                    extracted_info.get('linkedin_url', ''),
                    None,  # date_of_birth
                    extracted_info.get('skills', ''),
                    extracted_info.get('work_experience', ''),
                    extracted_info.get('education_history', ''),
                    extracted_info.get('summary_overview', '')
                )
                
                cursor.execute("""
                    INSERT INTO applicant_profile 
                    (name, email, phone, address, linkedin_url, date_of_birth, 
                     skills, work_experience, education_history, summary_overview)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, profile_data)
                
                applicant_id = cursor.lastrowid
                
                # insert ke application_detail
                # path relatif untuk aplikasi
                relative_cv_path = f"data/{category}/{pdf_file}"
                
                detail_data = (
                    applicant_id,
                    relative_cv_path,
                    f"{category.title()} Position",
                    raw_text,
                    category
                )
                
                cursor.execute("""
                    INSERT INTO application_detail
                    (applicant_id, cv_path, job_position, raw_text, category)
                    VALUES (%s, %s, %s, %s, %s)
                """, detail_data)
                
                loaded_count += 1
                
                if loaded_count % 5 == 0:
                    self.connection.commit()
                    print(f"✅ committed {loaded_count} records untuk {category}")
                
            except Exception as e:
                print(f"❌ error processing {pdf_file}: {e}")
                continue
        
        self.connection.commit()
        print(f"✅ selesai load {loaded_count} CV dari kategori {category}")
        return loaded_count
    
    def load_all_data(self, limit_per_category=20):
        """load semua data dari kaggle dataset"""
        if not self.connect_database():
            return False
        
        if not self.setup_database():
            return False
        
        total_loaded = 0
        
        print(f"🚀 mulai load dataset dari {self.kaggle_path}")
        print(f"📊 target: {limit_per_category} CV per kategori, {len(self.categories)} kategori")
        
        for category in self.categories:
            try:
                count = self.load_category_data(category, limit_per_category)
                total_loaded += count
                print(f"📈 progress: {total_loaded} total CV loaded")
            except Exception as e:
                print(f"❌ error load kategori {category}: {e}")
                continue
        
        print(f"🎉 selesai! total {total_loaded} CV berhasil dimuat ke database")
        
        # tampilkan statistik
        self.show_statistics()
        
        return True
    
    def show_statistics(self):
        """tampilkan statistik data yang dimuat"""
        try:
            cursor = self.connection.cursor()
            
            # total applicants
            cursor.execute("SELECT COUNT(*) FROM applicant_profile")
            total_applicants = cursor.fetchone()[0]
            
            # total applications
            cursor.execute("SELECT COUNT(*) FROM application_detail")
            total_applications = cursor.fetchone()[0]
            
            # breakdown per kategori
            cursor.execute("""
                SELECT category, COUNT(*) 
                FROM application_detail 
                GROUP BY category 
                ORDER BY category
            """)
            category_breakdown = cursor.fetchall()
            
            print("\n📊 STATISTIK DATABASE:")
            print(f"   Total Applicants: {total_applicants}")
            print(f"   Total Applications: {total_applications}")
            print("\n📋 Breakdown per Kategori:")
            for category, count in category_breakdown:
                print(f"   {category}: {count} CVs")
            
        except Exception as e:
            print(f"❌ error show statistics: {e}")
    
    def close_connection(self):
        """tutup koneksi database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ koneksi database ditutup")

def main():
    """main function untuk load dataset"""
    
    # konfigurasi database
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'danen332',  # sesuaikan dengan setup mysqlnya sendiri
        'database': 'ats_cv_search'
    }
    
    # path dataset kaggle
    kaggle_path = r"C:\Users\DANENDRA\.cache\kagglehub\datasets\snehaanbhawal\resume-dataset\versions\1"
    
    # cek apakah path exists
    if not os.path.exists(kaggle_path):
        print(f"❌ path kaggle dataset tidak ditemukan: {kaggle_path}")
        print("💡 pastikan path sesuai dengan lokasi dataset di sistem anda")
        return
    
    # buat loader instance
    loader = KaggleDatasetLoader(kaggle_path, db_config)
    
    print("🔧 ATS CV Search - Database Loader")
    print("=" * 50)
    
    try:
        # load data
        success = loader.load_all_data(limit_per_category=20)
        
        if success:
            print("\n🎉 database loading berhasil!")
            print("💡 sekarang aplikasi siap menggunakan data real dari kaggle")
        else:
            print("\n❌ database loading gagal!")
            
    except KeyboardInterrupt:
        print("\n⏹️ loading dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ error tidak terduga: {e}")
    finally:
        loader.close_connection()

if __name__ == "__main__":
    main()