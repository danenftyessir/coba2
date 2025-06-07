# Extract text from PDFs
import os
import PyPDF2

class PDFExtractor:
    """ekstrak text dari file pdf"""
    
    def __init__(self):
        self.last_error = None
    
    def extract_text(self, pdf_path):
        """ekstrak text dari pdf file"""
        try:
            if not os.path.exists(pdf_path):
                print(f"file tidak ditemukan: {pdf_path}")
                self.last_error = f"File not found: {pdf_path}"
                return None
                
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            print(f"error extracting: {e}")
            self.last_error = str(e)
            return None
    
    def get_last_error(self):
        """ambil error terakhir"""
        return self.last_error
    
    def extract_text_by_page(self, pdf_path):
        """ekstrak text per halaman"""
        try:
            if not os.path.exists(pdf_path):
                return []
                
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                pages = []
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text() or ""
                    pages.append(page_text)
                return pages
        except Exception as e:
            print(f"error extracting pages: {e}")
            return []
    
    def get_pdf_info(self, pdf_path):
        """ambil informasi pdf"""
        try:
            if not os.path.exists(pdf_path):
                return None
                
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                info = {
                    'num_pages': len(reader.pages),
                    'metadata': reader.metadata,
                    'is_encrypted': reader.is_encrypted
                }
                return info
        except Exception as e:
            print(f"error getting pdf info: {e}")
            return None

if __name__ == '__main__':
    extractor = PDFExtractor()
    test_path = "../data/CV_Bryan.pdf"
    text = extractor.extract_text(test_path)
    if text:
        print(f"extracted {len(text)} characters")
    else:
        print("extraction failed")