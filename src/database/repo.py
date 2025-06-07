# src/database/repo.py
from typing import List, Optional
from .config import DatabaseConfig
from .models import Resume

class ResumeRepository:
    """repository untuk akses data resume"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
    
    def get_all_resumes(self) -> List[Resume]:
        """ambil semua data resume dari database"""
        conn = self.db_config.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, file_path, name, phone, birthdate, address
                FROM resumes
                ORDER BY category, id
            """)
            
            results = cursor.fetchall()
            resumes = []
            
            for row in results:
                resume = Resume(
                    id=row[0],
                    category=row[1], 
                    file_path=row[2],
                    name=row[3],
                    phone=row[4],
                    birthdate=row[5],
                    address=row[6]
                )
                resumes.append(resume)
            
            return resumes
            
        except Exception as e:
            print(f"error mengambil data resume: {e}")
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_resume_by_id(self, resume_id: str) -> Optional[Resume]:
        """ambil resume berdasarkan id"""
        conn = self.db_config.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, file_path, name, phone, birthdate, address
                FROM resumes WHERE id = %s
            """, (resume_id,))
            
            row = cursor.fetchone()
            if row:
                return Resume(
                    id=row[0],
                    category=row[1],
                    file_path=row[2], 
                    name=row[3],
                    phone=row[4],
                    birthdate=row[5],
                    address=row[6]
                )
            return None
            
        except Exception as e:
            print(f"error mengambil resume {resume_id}: {e}")
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_resumes_by_category(self, category: str) -> List[Resume]:
        """ambil resume berdasarkan kategori"""
        conn = self.db_config.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, file_path, name, phone, birthdate, address
                FROM resumes WHERE category = %s
                ORDER BY id
            """, (category,))
            
            results = cursor.fetchall()
            resumes = []
            
            for row in results:
                resume = Resume(
                    id=row[0],
                    category=row[1],
                    file_path=row[2],
                    name=row[3], 
                    phone=row[4],
                    birthdate=row[5],
                    address=row[6]
                )
                resumes.append(resume)
            
            return resumes
            
        except Exception as e:
            print(f"error mengambil resume kategori {category}: {e}")
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()