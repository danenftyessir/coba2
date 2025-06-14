# src/controller/cv.py
import os
import subprocess
import platform
import shutil
from typing import Optional
from database.models import CVSummary
from database.repo import ResumeRepository
from utils.pdf_extractor import PDFExtractor
from utils.regex_extractor import RegexExtractor

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
        """buka file cv dengan aplikasi default - improved Linux support"""
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
            else:  # linux - multiple fallback options
                # Try different linux file openers in order of preference
                linux_openers = [
                    'xdg-open',      # standard
                    'gnome-open',    # gnome
                    'kde-open',      # kde
                    'exo-open',      # xfce
                    'gvfs-open',     # older gnome
                    'firefox',       # browser fallback
                    'google-chrome', # chrome fallback
                    'chromium',      # chromium fallback
                ]
                
                opened = False
                for opener in linux_openers:
                    if shutil.which(opener):  # check if command exists
                        try:
                            if opener in ['firefox', 'google-chrome', 'chromium']:
                                # open in browser
                                subprocess.run([opener, f"file://{os.path.abspath(resume.file_path)}"], 
                                             check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            else:
                                # use system file opener
                                subprocess.run([opener, resume.file_path], 
                                             check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            opened = True
                            print(f"✓ cv file opened using {opener}")
                            break
                        except Exception as e:
                            print(f"⚠️ failed to open with {opener}: {e}")
                            continue
                
                if not opened:
                    # Final fallback - try to find any PDF viewer
                    pdf_viewers = ['evince', 'okular', 'atril', 'mupdf', 'zathura']
                    for viewer in pdf_viewers:
                        if shutil.which(viewer):
                            try:
                                subprocess.run([viewer, resume.file_path], 
                                             check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                opened = True
                                print(f"✓ cv file opened using PDF viewer {viewer}")
                                break
                            except Exception as e:
                                print(f"⚠️ failed to open with {viewer}: {e}")
                                continue
                
                if not opened:
                    print("❌ no suitable file opener found on this Linux system")
                    print("💡 please install one of: xdg-open, evince, okular, firefox")
                    print(f"💡 or manually open: {resume.file_path}")
                    return False
            
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