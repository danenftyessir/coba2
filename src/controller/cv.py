# src/controller/cv.py
import os
import subprocess
import platform
from typing import Optional
from ..database.models import CVSummary
from ..database.repo import ResumeRepository
from ..utils.pdf_extractor import PDFExtractor
from ..utils.regex_extractor import RegexExtractor

class CVController:
    """controller untuk operasi cv dengan regex extraction yang lengkap"""
    
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
        """buat summary cv menggunakan regex extraction yang comprehensive"""
        print(f"📄 generating cv summary for resume {resume_id}")
        
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume:
            print(f"❌ resume {resume_id} not found")
            return None
        
        # extract text from cv
        cv_text = self.pdf_extractor.extract_text(resume.file_path)
        if not cv_text or cv_text == "large file skipped":
            print(f"❌ failed to extract text from {resume.file_path}")
            return None
        
        print(f"✓ extracted {len(cv_text)} characters from cv")
        
        # extract summary using regex
        summary = self.regex_extractor.extract_summary(cv_text)
        
        # enhance with database info if available
        if resume.name:
            summary.name = resume.name
        if resume.phone:
            summary.contact_info['phone'] = resume.phone
        if resume.address:
            summary.contact_info['address'] = resume.address
        
        print(f"✓ extracted summary with {len(summary.skills)} skills, {len(summary.job_history)} jobs, {len(summary.education)} education")
        
        return summary
    
    def open_cv_file(self, resume_id: str) -> bool:
        """buka file cv dengan aplikasi default"""
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume or not os.path.exists(resume.file_path):
            print(f"❌ cv file not found for resume {resume_id}")
            return False
        
        try:
            print(f"📄 opening cv file: {resume.file_path}")
            
            # open file based on os
            if platform.system() == 'Windows':
                os.startfile(resume.file_path)
            elif platform.system() == 'Darwin':  # macos
                subprocess.run(['open', resume.file_path])
            else:  # linux
                subprocess.run(['xdg-open', resume.file_path])
            
            print("✓ cv file opened successfully")
            return True
            
        except Exception as e:
            print(f"❌ error opening cv {resume_id}: {e}")
            return False
    
    def get_resume_info(self, resume_id: str):
        """get basic resume info from database"""
        return self.repo.get_resume_by_id(resume_id)
    
    def validate_cv_file(self, resume_id: str) -> bool:
        """validate apakah cv file exists dan readable"""
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume:
            return False
        
        return os.path.exists(resume.file_path) and os.path.isfile(resume.file_path)
    
    def get_cv_preview(self, resume_id: str, max_length: int = 500) -> Optional[str]:
        """get preview text dari cv untuk quick view"""
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume:
            return None
        
        cv_text = self.pdf_extractor.extract_text(resume.file_path)
        if cv_text and cv_text != "large file skipped":
            # return first portion as preview
            preview = cv_text[:max_length]
            if len(cv_text) > max_length:
                preview += "..."
            return preview
        
        return None