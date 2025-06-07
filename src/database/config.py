import mysql.connector
import os
from mysql.connector import Error
from typing import Optional

class DatabaseConfig:
    """konfigurasi dan koneksi database"""
    
    def __init__(self):
        # default config untuk development
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'ats_cv_search'),
            'port': int(os.getenv('DB_PORT', '3306'))
        }
        self.connection = None
    
    def get_connection(self):
        """ambil koneksi database"""
        try:
            if self.connection and self.connection.is_connected():
                return self.connection
            
            # coba connect ke database
            self.connection = mysql.connector.connect(**self.config)
            
            if self.connection.is_connected():
                print("✅ koneksi database berhasil")
                return self.connection
            
        except Error as e:
            # jika database belum ada, buat dulu
            if "Unknown database" in str(e):
                if self._create_database():
                    # coba connect lagi
                    self.connection = mysql.connector.connect(**self.config)
                    return self.connection
            
            print(f"❌ error koneksi database: {e}")
            raise e
    
    def _create_database(self) -> bool:
        """buat database jika belum ada"""
        try:
            # connect tanpa database
            temp_config = self.config.copy()
            temp_config.pop('database')
            
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            
            # buat database
            db_name = self.config['database']
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"✅ database '{db_name}' berhasil dibuat")
            
            cursor.close()
            conn.close()
            return True
            
        except Error as e:
            print(f"❌ error membuat database: {e}")
            return False
    
    def init_tables(self):
        """inisialisasi tabel database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # create table applicant_profile
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applicant_profile (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    phone VARCHAR(50),
                    address TEXT,
                    linkedin_url VARCHAR(255),
                    date_of_birth DATE,
                    skills TEXT,
                    work_experience TEXT,
                    education_history TEXT,
                    summary_overview TEXT
                )
            """)
            
            # create table application_detail
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS application_detail (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    applicant_id INT NOT NULL,
                    cv_path VARCHAR(255) NOT NULL,
                    application_date DATE,
                    job_position VARCHAR(255),
                    FOREIGN KEY (applicant_id) REFERENCES applicant_profile(id)
                        ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            print("✅ tabel database berhasil dibuat")
            
        except Error as e:
            print(f"❌ error membuat tabel: {e}")
            raise e
    
    def seed_sample_data(self):
        """seed data sample untuk testing"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # cek apakah sudah ada data
            cursor.execute("SELECT COUNT(*) FROM applicant_profile")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print("ℹ️ data sample sudah ada")
                return
            
            # insert sample applicants
            applicants = [
                {
                    'name': 'Bryan P. Hutagalung',
                    'email': 'bryan@gmail.com',
                    'phone': '+6281234567890',
                    'address': 'Jakarta, Indonesia',
                    'linkedin_url': 'linkedin.com/in/bryan',
                    'date_of_birth': '1998-05-15',
                    'skills': 'Python, Java, SQL, React, Machine Learning, Docker',
                    'work_experience': 'Software Engineer at Tech Corp (2020-Present)',
                    'education_history': 'Computer Science, ITB (2018-2022)',
                    'summary_overview': 'Experienced software engineer with focus on backend development'
                },
                {
                    'name': 'Danendra Shafi Athallah',
                    'email': 'danendra@gmail.com',
                    'phone': '+6281234567891',
                    'address': 'Yogya, Indonesia',
                    'linkedin_url': 'linkedin.com/in/danendra',
                    'date_of_birth': '1999-03-20',
                    'skills': 'JavaScript, React, Node.js, MongoDB, AWS',
                    'work_experience': 'Full Stack Developer at StartUp Inc (2021-Present)',
                    'education_history': 'Informatics, ITB (2018-2022)',
                    'summary_overview': 'Full stack developer specializing in modern web applications'
                },
                {
                    'name': 'Raihaan Perdana',
                    'email': 'raihaan@gmail.com',
                    'phone': '+6281234567892',
                    'address': 'Palembang, Indonesia',
                    'linkedin_url': 'linkedin.com/in/raihaan',
                    'date_of_birth': '1998-11-10',
                    'skills': 'C++, Python, Data Science, TensorFlow, Kubernetes',
                    'work_experience': 'Data Scientist at AI Company (2022-Present)',
                    'education_history': 'Computer Science, ITS (2018-2022)',
                    'summary_overview': 'Data scientist with expertise in machine learning and AI'
                }
            ]
            
            # insert applicants
            for applicant in applicants:
                cursor.execute("""
                    INSERT INTO applicant_profile 
                    (name, email, phone, address, linkedin_url, date_of_birth, 
                     skills, work_experience, education_history, summary_overview)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(applicant.values()))
                
                applicant_id = cursor.lastrowid
                
                # insert application detail
                cv_path = f"../data/CV_{applicant['name'].split()[0]}.pdf"
                cursor.execute("""
                    INSERT INTO application_detail
                    (applicant_id, cv_path, application_date, job_position)
                    VALUES (%s, %s, CURDATE(), %s)
                """, (applicant_id, cv_path, "Software Engineer"))
            
            conn.commit()
            print("✅ data sample berhasil ditambahkan")
            
        except Error as e:
            print(f"❌ error seed data: {e}")
            conn.rollback()
    
    def close_connection(self):
        """tutup koneksi database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ koneksi database ditutup")