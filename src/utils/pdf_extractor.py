# src/utils/pdf_extractor.py
import PyPDF2
import os
import re
from typing import Optional
import time

class PDFExtractor:
    """ekstraksi teks dari file pdf dengan optimasi aggressive"""
    
    def __init__(self):
        self.max_file_size_mb = 5  # reduced from 10MB
        self.max_pages = 2  # reduced from 5 pages
        self.max_extraction_time = 3  # max 3 seconds per file
        self.text_cache = {}  # simple cache
        self.failed_files = set()  # track failed files
    
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """ekstrak teks dari file pdf dengan timeout dan aggressive limits"""
        if not os.path.exists(pdf_path):
            return None
        
        # check if already failed
        if pdf_path in self.failed_files:
            return "failed file skipped"
        
        # check cache first
        if pdf_path in self.text_cache:
            return self.text_cache[pdf_path]
        
        # check file size
        try:
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                self.failed_files.add(pdf_path)
                return "large file skipped"
        except:
            self.failed_files.add(pdf_path)
            return None

        start_time = time.time()
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # quick check - if too many pages, skip
                if len(pdf_reader.pages) > 10:
                    self.failed_files.add(pdf_path)
                    return "too many pages skipped"
                
                text = ""
                max_pages = min(len(pdf_reader.pages), self.max_pages)
                
                for i in range(max_pages):
                    # check timeout
                    if time.time() - start_time > self.max_extraction_time:
                        print(f"⏱️ timeout extracting {pdf_path}")
                        self.failed_files.add(pdf_path)
                        return "timeout skipped"
                    
                    try:
                        page = pdf_reader.pages[i]
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        
                        # if we have enough text, stop
                        if len(text) > 5000:
                            break
                            
                    except Exception as e:
                        print(f"⚠️ error extracting page {i} from {pdf_path}: {e}")
                        continue
                
                # clean and cache the text
                if text.strip():
                    cleaned_text = self._clean_text(text)
                    self.text_cache[pdf_path] = cleaned_text
                    return cleaned_text
                else:
                    self.failed_files.add(pdf_path)
                    return "no text extracted"
                
        except Exception as e:
            print(f"⚠️ error reading pdf {pdf_path}: {e}")
            self.failed_files.add(pdf_path)
            return None

    def extract_text_for_matching(self, pdf_path: str) -> Optional[str]:
        """ekstrak teks khusus untuk pattern matching (lowercase, cleaned)"""
        text = self.extract_text(pdf_path)
        if text and text not in ["large file skipped", "failed file skipped", "timeout skipped", "too many pages skipped", "no text extracted"]:
            # convert to lowercase for matching
            text = text.lower()
            # limit length for performance - very aggressive
            if len(text) > 3000:  # reduced from 10000
                text = text[:3000]
            return text
        return text
    
    def _clean_text(self, text: str) -> str:
        """bersihkan teks hasil ekstraksi dengan minimal processing"""
        if not text:
            return ""

        # very simple cleaning
        text = re.sub(r'\s+', ' ', text)  # normalize whitespace
        text = text.strip()
        
        # limit length aggressively
        if len(text) > 5000:
            text = text[:5000]
        
        return text

    def get_extraction_stats(self):
        """get extraction statistics"""
        return {
            'cached_files': len(self.text_cache),
            'failed_files': len(self.failed_files),
            'total_processed': len(self.text_cache) + len(self.failed_files)
        }