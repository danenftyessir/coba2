# src/database/repo.py
from typing import List, Optional
import os
from .config import DatabaseConfig
from .models import Resume

class ResumeRepository:
    """repository untuk akses data resume dengan path correction dan optimasi"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        # set data base path relative to project root
        self.data_base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
        self.data_base_path = os.path.abspath(self.data_base_path)
        print(f"data base path: {self.data_base_path}")
    
    def get_all_resumes(self) -> List[Resume]:
        """ambil semua data resume dari database dengan path validation yang diperbaiki"""
        conn = self.db_config.get_connection()
        if not conn:
            print("failed to connect to database")
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
                # build actual file path with multiple fallback options
                resume_id = row[0]
                category = row[1]
                stored_path = row[2]
                
                # try different path combinations
                possible_paths = [
                    stored_path,  # original path
                    os.path.join(self.data_base_path, f"{category}", f"{resume_id}.pdf"),  # category/id.pdf
                    os.path.join(self.data_base_path, stored_path),  # data/stored_path
                    os.path.join(self.data_base_path, category, os.path.basename(stored_path)),  # data/category/filename
                ]
                
                actual_path = None
                for path in possible_paths:
                    if os.path.exists(path) and os.path.isfile(path):
                        actual_path = os.path.abspath(path)
                        break
                
                if actual_path:
                    resume = Resume(
                        id=resume_id,
                        category=category, 
                        file_path=actual_path,
                        name=row[3],
                        phone=row[4],
                        birthdate=row[5],
                        address=row[6]
                    )
                    resumes.append(resume)
                else:
                    print(f"file not found for resume {resume_id}: {stored_path}")
            
            print(f"loaded {len(resumes)} valid resumes from database")
            return resumes
            
        except Exception as e:
            print(f"error loading resumes: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_resume_by_id(self, resume_id: str) -> Optional[Resume]:
        """ambil resume berdasarkan id dengan path validation yang diperbaiki"""
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
                # build actual file path
                category = row[1]
                stored_path = row[2]
                
                possible_paths = [
                    stored_path,
                    os.path.join(self.data_base_path, f"{category}", f"{resume_id}.pdf"),
                    os.path.join(self.data_base_path, stored_path),
                    os.path.join(self.data_base_path, category, os.path.basename(stored_path)),
                ]
                
                actual_path = None
                for path in possible_paths:
                    if os.path.exists(path) and os.path.isfile(path):
                        actual_path = os.path.abspath(path)
                        break
                
                if actual_path:
                    return Resume(
                        id=row[0],
                        category=row[1],
                        file_path=actual_path, 
                        name=row[3],
                        phone=row[4],
                        birthdate=row[5],
                        address=row[6]
                    )
                else:
                    print(f"file not found for resume {resume_id}")
            return None
            
        except Exception as e:
            print(f"error getting resume {resume_id}: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_resumes_by_category(self, category: str) -> List[Resume]:
        """ambil resume berdasarkan kategori dengan optimasi"""
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
                resume_id = row[0]
                stored_path = row[2]
                
                # apply same path fixing logic
                possible_paths = [
                    stored_path,
                    os.path.join(self.data_base_path, f"{category}", f"{resume_id}.pdf"),
                    os.path.join(self.data_base_path, stored_path),
                ]
                
                actual_path = None
                for path in possible_paths:
                    if os.path.exists(path) and os.path.isfile(path):
                        actual_path = os.path.abspath(path)
                        break
                
                if actual_path:
                    resume = Resume(
                        id=row[0],
                        category=row[1],
                        file_path=actual_path,
                        name=row[3], 
                        phone=row[4],
                        birthdate=row[5],
                        address=row[6]
                    )
                    resumes.append(resume)
            
            return resumes
            
        except Exception as e:
            print(f"error getting resumes for category {category}: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def test_data_directory(self):
        """test apakah directory data dan file pdf ada"""
        print(f"testing data directory: {self.data_base_path}")
        
        if not os.path.exists(self.data_base_path):
            print("data directory not found")
            return False
        
        # check for common categories
        categories = ['ACCOUNTANT', 'ADVOCATE', 'ARTS', 'CHEF', 'CONSTRUCTION']
        found_categories = []
        
        for category in categories:
            category_path = os.path.join(self.data_base_path, category)
            if os.path.exists(category_path):
                pdf_files = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
                if pdf_files:
                    found_categories.append(f"{category}: {len(pdf_files)} pdfs")
        
        if found_categories:
            print("found categories:")
            for cat in found_categories:
                print(f"  {cat}")
            return True
        else:
            print("no pdf files found in data directory")
            return False