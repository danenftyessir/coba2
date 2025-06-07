# src/utils/pdf_extractor.py
import PyPDF2
import os
from typing import Optional

class PDFExtractor:
    """ekstraksi teks dari file pdf"""
    
    def __init__(self):
        pass
    
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """ekstrak teks dari file pdf"""
        if not os.path.exists(pdf_path):
            print(f"file tidak ditemukan: {pdf_path}")
            return None
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # bersihkan teks
                text = self._clean_text(text)
                return text
                
        except Exception as e:
            print(f"error ekstraksi pdf {pdf_path}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """bersihkan teks hasil ekstraksi"""
        if not text:
            return ""
        
        # hapus karakter spesial dan bersihkan whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # skip empty lines
                cleaned_lines.append(line)
        
        # gabung kembali dengan space
        cleaned_text = " ".join(cleaned_lines)
        
        # hapus multiple spaces
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    def extract_text_for_matching(self, pdf_path: str) -> Optional[str]:
        """ekstrak teks khusus untuk pattern matching (lowercase)"""
        text = self.extract_text(pdf_path)
        if text:
            return text.lower()
        return None