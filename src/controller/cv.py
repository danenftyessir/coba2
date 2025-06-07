# src/controller/cv.py
import os
import subprocess
import platform
from typing import Optional
from ..database.models import Resume, CVSummary
from ..database.repo import ResumeRepository
from ..utils.pdf_extractor import PDFExtractor
from ..utils.regex_extractor import RegexExtractor

class CVController:
    """controller untuk operasi cv"""
    
    def __init__(self):
        self.repo = ResumeRepository()
        self.pdf_extractor = PDFExtractor()
        self.regex_extractor = RegexExtractor()
    
    def get_cv_text(self, resume_id: str) -> Optional[str]:
        """ambil teks cv untuk pattern matching"""
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume:
            return None
        
        return self.pdf_extractor.extract_text_for_matching(resume.file_path)
    
    def get_cv_summary(self, resume_id: str) -> Optional[CVSummary]:
        """buat summary cv menggunakan regex extraction"""
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume:
            return None
        
        # ambil text cv
        cv_text = self.pdf_extractor.extract_text(resume.file_path)
        if not cv_text:
            return None
        
        # ekstrak menggunakan regex
        summary = self.regex_extractor.extract_summary(cv_text)
        
        # tambahkan data dari database jika ada
        if resume.name:
            summary.name = resume.name
        if resume.phone:
            summary.contact_info['phone'] = resume.phone
        if resume.address:
            summary.contact_info['address'] = resume.address
        
        return summary
    
    def open_cv_file(self, resume_id: str) -> bool:
        """buka file cv dengan aplikasi default"""
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume or not os.path.exists(resume.file_path):
            return False
        
        try:
            # buka file sesuai os
            if platform.system() == 'Windows':
                os.startfile(resume.file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', resume.file_path])
            else:  # Linux
                subprocess.run(['xdg-open', resume.file_path])
            
            return True
        except Exception as e:
            print(f"error membuka cv {resume_id}: {e}")
            return False
    
    def get_resume_info(self, resume_id: str) -> Optional[Resume]:
        """ambil informasi resume dari database"""
        return self.repo.get_resume_by_id(resume_id)
    
    def validate_cv_file(self, resume_id: str) -> bool:
        """validasi apakah file cv ada dan bisa dibaca"""
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume:
            return False
        
        return os.path.exists(resume.file_path) and os.path.isfile(resume.file_path)