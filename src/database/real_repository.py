from typing import List, Dict, Optional, Any
from mysql.connector import Error
import mysql.connector
import os

class RealRepository:
    """repository production untuk akses database mysql"""
    
    def __init__(self, connection):
        self.connection = connection
    
    def get_all_cvs(self) -> List[Dict[str, Any]]:
        """ambil semua cv dari database dengan informasi lengkap"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    ap.id as applicant_id,
                    ap.name,
                    ap.email,
                    ap.phone,
                    ap.skills,
                    ad.cv_path,
                    ad.job_position,
                    ad.raw_text,
                    ad.category
                FROM applicant_profile ap
                JOIN application_detail ad ON ap.id = ad.applicant_id
                ORDER BY ap.name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            print(f"loaded {len(results)} CVs from database")
            return results
            
        except Error as e:
            print(f"error get all cvs: {e}")
            return []
    
    def get_applicant_by_id(self, applicant_id: int) -> Optional[Dict[str, Any]]:
        """ambil data lengkap applicant berdasarkan id"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    ap.*,
                    ad.cv_path,
                    ad.job_position,
                    ad.application_date,
                    ad.category
                FROM applicant_profile ap
                LEFT JOIN application_detail ad ON ap.id = ad.applicant_id
                WHERE ap.id = %s
            """
            
            cursor.execute(query, (applicant_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return result
            
        except Error as e:
            print(f"❌ error get applicant by id: {e}")
            return None
    
    def search_applicants(self, keyword: str) -> List[Dict[str, Any]]:
        """cari applicant berdasarkan keyword"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            search_pattern = f"%{keyword}%"
            query = """
                SELECT 
                    ap.id as applicant_id,
                    ap.name,
                    ap.email,
                    ap.skills,
                    ad.cv_path,
                    ad.job_position
                FROM applicant_profile ap
                JOIN application_detail ad ON ap.id = ad.applicant_id
                WHERE ap.name LIKE %s 
                   OR ap.skills LIKE %s
                   OR ap.work_experience LIKE %s
                   OR ap.education_history LIKE %s
                   OR ad.raw_text LIKE %s
            """
            
            cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Error as e:
            print(f"error search applicants: {e}")
            return []
    
    def save_applicant(self, applicant_data: Dict[str, Any]) -> bool:
        """simpan atau update data applicant"""
        try:
            cursor = self.connection.cursor()
            
            applicant_id = applicant_data.get('id')
            
            if applicant_id:
                # update existing
                query = """
                    UPDATE applicant_profile 
                    SET name = %s, email = %s, phone = %s, address = %s,
                        linkedin_url = %s, date_of_birth = %s, skills = %s,
                        work_experience = %s, education_history = %s,
                        summary_overview = %s
                    WHERE id = %s
                """
                params = (
                    applicant_data.get('name'),
                    applicant_data.get('email'),
                    applicant_data.get('phone'),
                    applicant_data.get('address'),
                    applicant_data.get('linkedin_url'),
                    applicant_data.get('date_of_birth'),
                    applicant_data.get('skills'),
                    applicant_data.get('work_experience'),
                    applicant_data.get('education_history'),
                    applicant_data.get('summary_overview'),
                    applicant_id
                )
            else:
                # insert new
                query = """
                    INSERT INTO applicant_profile 
                    (name, email, phone, address, linkedin_url, date_of_birth,
                     skills, work_experience, education_history, summary_overview)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    applicant_data.get('name'),
                    applicant_data.get('email'),
                    applicant_data.get('phone'),
                    applicant_data.get('address'),
                    applicant_data.get('linkedin_url'),
                    applicant_data.get('date_of_birth'),
                    applicant_data.get('skills'),
                    applicant_data.get('work_experience'),
                    applicant_data.get('education_history'),
                    applicant_data.get('summary_overview')
                )
            
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Error as e:
            print(f"❌ error save applicant: {e}")
            self.connection.rollback()
            return False
    
    def delete_applicant(self, applicant_id: int) -> bool:
        """hapus data applicant"""
        try:
            cursor = self.connection.cursor()
            
            # hapus dari application_detail dulu (foreign key)
            cursor.execute("DELETE FROM application_detail WHERE applicant_id = %s", (applicant_id,))
            
            # hapus dari applicant_profile
            cursor.execute("DELETE FROM applicant_profile WHERE id = %s", (applicant_id,))
            
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Error as e:
            print(f"error delete applicant: {e}")
            self.connection.rollback()
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """ambil statistik database"""
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # total applicants
            cursor.execute("SELECT COUNT(*) FROM applicant_profile")
            stats['total_applicants'] = cursor.fetchone()[0]
            
            # total applications
            cursor.execute("SELECT COUNT(*) FROM application_detail")
            stats['total_applications'] = cursor.fetchone()[0]
            
            # breakdown per kategori
            cursor.execute("""
                SELECT category, COUNT(*) 
                FROM application_detail 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """)
            category_data = cursor.fetchall()
            stats['top_categories'] = dict(category_data)
            
            cursor.close()
            
            return stats
            
        except Exception as e:
            print(f"error get statistics: {e}")
            return {'total_applicants': 0, 'total_applications': 0, 'top_categories': {}}