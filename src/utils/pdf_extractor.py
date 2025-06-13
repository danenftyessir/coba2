# src/utils/pdf_extractor.py
import PyPDF2
import os
import re
from typing import Optional

class PDFExtractor:
    """ekstraksi teks dari file pdf dengan optimasi"""
    
    def __init__(self):
        self.max_file_size_mb = 5  # skip files larger than 5mb
    
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """ekstrak teks dari file pdf dengan error handling"""
        if not os.path.exists(pdf_path):
            print(f"⚠️ file not found: {pdf_path}")
            return None
        
        # check file size
        try:
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                print(f"⚠️ skipping large file ({file_size_mb:.1f}mb): {pdf_path}")
                return "large file skipped"
        except:
            pass
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                # extract text from all pages
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # clean extracted text
                cleaned_text = self._clean_text(text)
                return cleaned_text if cleaned_text else ""
                
        except Exception as e:
            print(f"❌ error extracting pdf {pdf_path}: {e}")
            return None
    
    def extract_text_for_matching(self, pdf_path: str) -> Optional[str]:
        """ekstrak teks khusus untuk pattern matching (lowercase, cleaned)"""
        text = self.extract_text(pdf_path)
        if text and text != "large file skipped":
            # convert to lowercase for matching
            text = text.lower()
            # limit length for performance
            if len(text) > 50000:
                text = text[:50000]
            return text
        return text
    
    def _clean_text(self, text: str) -> str:
        """bersihkan teks hasil ekstraksi dengan preserve structure untuk regex"""
        if not text:
            return ""
        
        # replace windows line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # remove excessive whitespace but preserve line structure
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # remove multiple spaces within line
                line = re.sub(r'\s+', ' ', line)
                cleaned_lines.append(line)
        
        # join with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # ensure proper section spacing for regex
        cleaned_text = self._fix_section_spacing(cleaned_text)
        
        return cleaned_text.strip()
    
    def _fix_section_spacing(self, text: str) -> str:
        """fix spacing between sections untuk regex detection"""
        # common section headers
        section_headers = [
            'SUMMARY', 'PROFILE', 'OVERVIEW', 'OBJECTIVE',
            'EXPERIENCE', 'WORK HISTORY', 'EMPLOYMENT',
            'EDUCATION', 'ACADEMIC', 'QUALIFICATIONS',
            'SKILLS', 'TECHNICAL SKILLS', 'COMPETENCIES',
            'ACHIEVEMENTS', 'ACCOMPLISHMENTS', 'AWARDS',
            'PROJECTS', 'CERTIFICATIONS', 'LICENSES'
        ]
        
        lines = text.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            line_upper = line.upper().strip()
            
            # check if this line is a section header
            is_section = any(header in line_upper for header in section_headers)
            
            if is_section and i > 0:
                # add blank line before section header if not already there
                if result_lines and result_lines[-1].strip():
                    result_lines.append('')
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)