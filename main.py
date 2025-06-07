# main.py - ATS CV Search Application
import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
import mysql.connector
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import date
import PyPDF2
import re
import time
import subprocess
import platform

# add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try different import paths for algorithms
try:
    # Try method 1: direct import (algorithm files in root)
    from aho_corasick import AhoCorasick
    from kmp import KMPMatcher
    from bm import BoyerMooreMatcher
    from levenshtein import LevenshteinMatcher
    print("✓ Imported algorithms from root directory")
except ImportError:
    try:
        # Try method 2: from algorithm folder
        from src.algorithm.kmp import KMPMatcher
        from src.algorithm.bm import BoyerMooreMatcher  
        from src.algorithm.aho_corasick import AhoCorasick
        from src.algorithm.levenshtein import LevenshteinMatcher
        print("✓ Imported algorithms from algorithm/ folder")
    except ImportError:
        try:
            # Try method 3: from src/algorithms folder
            from src.algorithms.kmp import KMPMatcher
            from src.algorithms.bm import BoyerMooreMatcher  
            from src.algorithms.aho_corasick import AhoCorasick
            from src.algorithms.levenshtein import LevenshteinMatcher
            print("✓ Imported algorithms from src/algorithms/ folder")
        except ImportError as e:
            print(f"❌ Could not import algorithms: {e}")
            print("Please check if algorithm files exist in:")
            print("  - Root directory (aho_corasick.py, kmp.py, bm.py, levenshtein.py)")
            print("  - algorithm/ folder")
            print("  - src/algorithms/ folder")
            sys.exit(1)

# ===== DATA MODELS =====
@dataclass
class Resume:
    """model data resume dari database"""
    id: str
    category: str
    file_path: str
    name: Optional[str] = None
    phone: Optional[str] = None
    birthdate: Optional[date] = None
    address: Optional[str] = None

@dataclass
class SearchResult:
    """model hasil pencarian cv"""
    resume: Resume
    keyword_matches: dict
    total_matches: int
    matched_keywords: List[str]
    fuzzy_matches: dict = None

@dataclass
class CVSummary:
    """model summary cv yang diekstrak"""
    name: str
    contact_info: dict
    skills: List[str]
    experience: List[dict]
    education: List[dict]
    summary: str

# ===== DATABASE =====
class DatabaseConfig:
    """konfigurasi database mysql"""
    
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'danen332',
            'database': 'kaggle_resumes',
            'port': 3306
        }
    
    def get_connection(self):
        """buat koneksi ke database"""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except mysql.connector.Error as e:
            print(f"error koneksi database: {e}")
            return None

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
                FROM resumes ORDER BY category, id
            """)
            
            results = cursor.fetchall()
            resumes = []
            
            for row in results:
                resume = Resume(
                    id=row[0], category=row[1], file_path=row[2],
                    name=row[3], phone=row[4], birthdate=row[5], address=row[6]
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
                    id=row[0], category=row[1], file_path=row[2],
                    name=row[3], phone=row[4], birthdate=row[5], address=row[6]
                )
            return None
            
        except Exception as e:
            print(f"error mengambil resume {resume_id}: {e}")
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

# ===== UTILS =====
class PDFExtractor:
    """ekstraksi teks dari file pdf"""
    
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
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        cleaned_text = " ".join(cleaned_lines)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    def extract_text_for_matching(self, pdf_path: str) -> Optional[str]:
        """ekstrak teks khusus untuk pattern matching (lowercase)"""
        text = self.extract_text(pdf_path)
        if text:
            return text.lower()
        return None

class RegexExtractor:
    """ekstraksi informasi cv menggunakan regex"""
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    
    def extract_summary(self, text: str) -> CVSummary:
        """ekstrak summary lengkap dari cv text"""
        return CVSummary(
            name=self._extract_name(text),
            contact_info=self._extract_contact_info(text),
            skills=self._extract_skills(text),
            experience=self._extract_experience(text),
            education=self._extract_education(text),
            summary=self._extract_overview(text)
        )
    
    def _extract_name(self, text: str) -> str:
        """ekstrak nama dari cv"""
        lines = text.split('\n')
        if lines:
            for line in lines:
                line = line.strip()
                if line and not re.match(r'^[A-Z\s]+$', line):
                    words = line.split()
                    name_words = []
                    for word in words[:3]:
                        if re.match(r'^[A-Z][a-z]+', word):
                            name_words.append(word)
                    if name_words:
                        return " ".join(name_words)
        return "Unknown"
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """ekstrak informasi kontak"""
        contact = {}
        
        email_match = re.search(self.email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()
        
        phone_match = re.search(self.phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        return contact
    
    def _extract_skills(self, text: str) -> List[str]:
        """ekstrak skills dari cv"""
        skills = []
        
        skills_pattern = r'(?:skills?|technical skills?):\s*([^\.]+?)(?:\n\n|\.\s*[A-Z]|$)'
        skills_match = re.search(skills_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            skill_items = re.split(r'[,;\n•\-\*]', skills_text)
            
            for skill in skill_items:
                skill = skill.strip()
                if skill and len(skill) > 1:
                    skills.append(skill)
        
        if not skills:
            skill_keywords = [
                'python', 'java', 'javascript', 'react', 'html', 'css', 'sql',
                'mysql', 'postgresql', 'mongodb', 'docker', 'kubernetes'
            ]
            
            for keyword in skill_keywords:
                if keyword.lower() in text.lower():
                    skills.append(keyword.title())
        
        return skills[:10]
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """ekstrak pengalaman kerja"""
        experiences = []
        
        exp_pattern = r'(?:experience|work history):(.*?)(?:education|skills|$)'
        exp_match = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if exp_match:
            exp_text = exp_match.group(1)
            job_pattern = r'(\d{2}/\d{4}\s*-\s*\d{2}/\d{4}|\d{4}\s*-\s*\d{4}).*?([A-Z][^.\n]+)'
            job_matches = re.findall(job_pattern, exp_text)
            
            for date_range, title in job_matches:
                experiences.append({
                    'period': date_range.strip(),
                    'position': title.strip(),
                    'company': 'Company Name'
                })
        
        return experiences[:5]
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """ekstrak riwayat pendidikan"""
        education = []
        
        edu_pattern = r'(?:education|academic background):(.*?)(?:experience|skills|$)'
        edu_match = re.search(edu_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if edu_match:
            edu_text = edu_match.group(1)
            degree_pattern = r'(\d{4})\s*([^,\n]+),?\s*([^,\n]+)'
            degree_matches = re.findall(degree_pattern, edu_text)
            
            for year, degree, institution in degree_matches:
                education.append({
                    'year': year.strip(),
                    'degree': degree.strip(),
                    'institution': institution.strip()
                })
        
        return education[:3]
    
    def _extract_overview(self, text: str) -> str:
        """ekstrak overview/summary"""
        summary_pattern = r'(?:summary|overview|profile):\s*([^\.]+\.)'
        summary_match = re.search(summary_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if summary_match:
            summary = summary_match.group(1).strip()
            return summary
        
        sentences = re.split(r'\.\s+', text)
        if len(sentences) > 1:
            return ". ".join(sentences[:2]) + "."
        
        return "Professional with experience in the field."

class SearchTimer:
    """timer khusus untuk operasi search"""
    
    def __init__(self):
        self.start_times = {}
        self.durations = {}
        self.search_results = {}
    
    def start_exact_search(self, algorithm: str, num_cvs: int):
        """mulai timer untuk exact search"""
        self.search_results['algorithm'] = algorithm
        self.search_results['num_cvs'] = num_cvs
        self.start_times['exact_search'] = time.time()
    
    def stop_exact_search(self) -> float:
        """stop timer exact search"""
        if 'exact_search' in self.start_times:
            duration = (time.time() - self.start_times['exact_search']) * 1000
            self.durations['exact_duration'] = duration
            self.search_results['exact_duration'] = duration
            del self.start_times['exact_search']
            return duration
        return 0.0
    
    def start_fuzzy_search(self, num_keywords: int):
        """mulai timer untuk fuzzy search"""
        self.search_results['fuzzy_keywords'] = num_keywords
        self.start_times['fuzzy_search'] = time.time()
    
    def stop_fuzzy_search(self) -> float:
        """stop timer fuzzy search"""
        if 'fuzzy_search' in self.start_times:
            duration = (time.time() - self.start_times['fuzzy_search']) * 1000
            self.durations['fuzzy_duration'] = duration
            self.search_results['fuzzy_duration'] = duration
            del self.start_times['fuzzy_search']
            return duration
        return 0.0
    
    def get_search_summary(self) -> str:
        """buat summary hasil search timing"""
        if 'exact_duration' not in self.search_results:
            return "No search performed"
        
        algorithm = self.search_results.get('algorithm', 'Unknown')
        num_cvs = self.search_results.get('num_cvs', 0)
        exact_time = f"{self.search_results['exact_duration']:.0f}ms"
        
        summary = f"Exact Match ({algorithm}): {num_cvs} CVs scanned in {exact_time}"
        
        if 'fuzzy_duration' in self.search_results:
            fuzzy_keywords = self.search_results.get('fuzzy_keywords', 0)
            fuzzy_time = f"{self.search_results['fuzzy_duration']:.0f}ms"
            summary += f"\nFuzzy Match: {fuzzy_keywords} keywords processed in {fuzzy_time}"
        
        return summary
    
    def reset(self):
        """reset search timer"""
        self.start_times.clear()
        self.durations.clear()
        self.search_results.clear()

# ===== CONTROLLERS =====
class SearchController:
    """controller untuk operasi pencarian cv"""
    
    def __init__(self):
        self.repo = ResumeRepository()
        self.pdf_extractor = PDFExtractor()
        self.timer = SearchTimer()
        
        # initialize matchers
        self.kmp_matcher = KMPMatcher()
        self.bm_matcher = BoyerMooreMatcher()
        self.aho_corasick = AhoCorasick()
        self.levenshtein_matcher = LevenshteinMatcher()
    
    def search_cvs(self, keywords: List[str], algorithm: str = 'KMP', 
                   top_n: int = 10, fuzzy_threshold: float = 0.7) -> Tuple[List[SearchResult], str]:
        """pencarian cv dengan exact dan fuzzy matching"""
        
        self.timer.reset()
        
        resumes = self.repo.get_all_resumes()
        if not resumes:
            return [], "No CVs found in database"
        
        self.timer.start_exact_search(algorithm, len(resumes))
        exact_results = self._exact_search(resumes, keywords, algorithm)
        self.timer.stop_exact_search()
        
        unfound_keywords = self._get_unfound_keywords(exact_results, keywords)
        
        if unfound_keywords:
            self.timer.start_fuzzy_search(len(unfound_keywords))
            fuzzy_results = self._fuzzy_search(resumes, unfound_keywords, fuzzy_threshold)
            self.timer.stop_fuzzy_search()
            combined_results = self._combine_results(exact_results, fuzzy_results)
        else:
            combined_results = exact_results
        
        combined_results.sort(key=lambda x: x.total_matches, reverse=True)
        top_results = combined_results[:top_n]
        timing_summary = self.timer.get_search_summary()
        
        return top_results, timing_summary
    
    def _exact_search(self, resumes: List[Resume], keywords: List[str], algorithm: str) -> List[SearchResult]:
        """exact matching menggunakan algoritma yang dipilih"""
        results = []
        
        for resume in resumes:
            cv_text = self.pdf_extractor.extract_text_for_matching(resume.file_path)
            if not cv_text:
                continue
            
            keyword_matches = {}
            total_matches = 0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                if not keyword_lower:
                    continue
                
                if algorithm.upper() == 'KMP':
                    matches = self.kmp_matcher.search(cv_text, keyword_lower)
                elif algorithm.upper() == 'BM':
                    matches = self.bm_matcher.search(cv_text, keyword_lower)
                elif algorithm.upper() == 'AC':
                    matches = self.aho_corasick.search_multiple(cv_text, [keyword_lower])
                else:
                    matches = self.kmp_matcher.search(cv_text, keyword_lower)
                
                if matches and keyword_lower in matches:
                    match_count = len(matches[keyword_lower])
                    keyword_matches[keyword] = match_count
                    total_matches += match_count
                    matched_keywords.append(keyword)
            
            if total_matches > 0:
                result = SearchResult(
                    resume=resume,
                    keyword_matches=keyword_matches,
                    total_matches=total_matches,
                    matched_keywords=matched_keywords
                )
                results.append(result)
        
        return results
    
    def _fuzzy_search(self, resumes: List[Resume], keywords: List[str], threshold: float) -> List[SearchResult]:
        """fuzzy matching menggunakan levenshtein distance"""
        results = []
        
        for resume in resumes:
            cv_text = self.pdf_extractor.extract_text(resume.file_path)
            if not cv_text:
                continue
            
            fuzzy_matches = {}
            total_fuzzy_matches = 0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                if not keyword_lower:
                    continue
                
                matches = self.levenshtein_matcher.search(cv_text, keyword_lower, threshold)
                
                if matches and keyword_lower in matches:
                    match_count = len(matches[keyword_lower])
                    fuzzy_matches[f"{keyword} (fuzzy)"] = match_count
                    total_fuzzy_matches += match_count
                    matched_keywords.append(f"{keyword} (fuzzy)")
            
            if total_fuzzy_matches > 0:
                result = SearchResult(
                    resume=resume,
                    keyword_matches=fuzzy_matches,
                    total_matches=total_fuzzy_matches,
                    matched_keywords=matched_keywords,
                    fuzzy_matches=fuzzy_matches
                )
                results.append(result)
        
        return results
    
    def _get_unfound_keywords(self, results: List[SearchResult], original_keywords: List[str]) -> List[str]:
        """ambil keyword yang tidak ditemukan dalam exact search"""
        found_keywords = set()
        
        for result in results:
            found_keywords.update(result.matched_keywords)
        
        unfound = []
        for keyword in original_keywords:
            if keyword not in found_keywords:
                unfound.append(keyword)
        
        return unfound
    
    def _combine_results(self, exact_results: List[SearchResult], fuzzy_results: List[SearchResult]) -> List[SearchResult]:
        """gabungkan hasil exact dan fuzzy search"""
        combined_dict = {}
        
        for result in exact_results:
            combined_dict[result.resume.id] = result
        
        for fuzzy_result in fuzzy_results:
            resume_id = fuzzy_result.resume.id
            
            if resume_id in combined_dict:
                existing = combined_dict[resume_id]
                existing.keyword_matches.update(fuzzy_result.keyword_matches)
                existing.total_matches += fuzzy_result.total_matches
                existing.matched_keywords.extend(fuzzy_result.matched_keywords)
                existing.fuzzy_matches = fuzzy_result.fuzzy_matches
            else:
                combined_dict[resume_id] = fuzzy_result
        
        return list(combined_dict.values())

class CVController:
    """controller untuk operasi cv"""
    
    def __init__(self):
        self.repo = ResumeRepository()
        self.pdf_extractor = PDFExtractor()
        self.regex_extractor = RegexExtractor()
    
    def get_cv_summary(self, resume_id: str) -> Optional[CVSummary]:
        """buat summary cv menggunakan regex extraction"""
        resume = self.repo.get_resume_by_id(resume_id)
        if not resume:
            return None
        
        cv_text = self.pdf_extractor.extract_text(resume.file_path)
        if not cv_text:
            return None
        
        summary = self.regex_extractor.extract_summary(cv_text)
        
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
            if platform.system() == 'Windows':
                os.startfile(resume.file_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', resume.file_path])
            else:
                subprocess.run(['xdg-open', resume.file_path])
            
            return True
        except Exception as e:
            print(f"error membuka cv {resume_id}: {e}")
            return False

# ===== GUI COMPONENTS =====
class SearchPanel(QtWidgets.QWidget):
    """panel input untuk pencarian cv"""
    
    search_requested = QtCore.pyqtSignal(list, str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """setup user interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # title
        title = QtWidgets.QLabel("CV Analyzer App")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # keywords input
        keywords_group = self._create_keywords_section()
        layout.addWidget(keywords_group)
        
        # algorithm selection
        algorithm_group = self._create_algorithm_section()
        layout.addWidget(algorithm_group)
        
        # top matches selector
        matches_group = self._create_matches_section()
        layout.addWidget(matches_group)
        
        # search button
        search_btn = self._create_search_button()
        layout.addWidget(search_btn)
        
        layout.addStretch()
    
    def _create_keywords_section(self) -> QtWidgets.QGroupBox:
        """buat section input keywords"""
        group = QtWidgets.QGroupBox("Keywords:")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group)
        
        self.keywords_input = QtWidgets.QLineEdit()
        self.keywords_input.setPlaceholderText("React, Express, HTML...")
        self.keywords_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(self.keywords_input)
        
        return group
    
    def _create_algorithm_section(self) -> QtWidgets.QGroupBox:
        """buat section pemilihan algoritma"""
        group = QtWidgets.QGroupBox("Search Algorithm:")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(group)
        
        self.kmp_radio = QtWidgets.QRadioButton("KMP")
        self.bm_radio = QtWidgets.QRadioButton("BM")
        self.ac_radio = QtWidgets.QRadioButton("AC")
        
        self.kmp_radio.setChecked(True)
        
        radio_style = """
            QRadioButton {
                font-size: 14px;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
        """
        self.kmp_radio.setStyleSheet(radio_style)
        self.bm_radio.setStyleSheet(radio_style)
        self.ac_radio.setStyleSheet(radio_style)
        
        layout.addWidget(self.kmp_radio)
        layout.addWidget(self.bm_radio)
        layout.addWidget(self.ac_radio)
        layout.addStretch()
        
        return group
    
    def _create_matches_section(self) -> QtWidgets.QGroupBox:
        """buat section top matches selector"""
        group = QtWidgets.QGroupBox("Top Matches:")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(group)
        
        self.top_matches_spin = QtWidgets.QSpinBox()
        self.top_matches_spin.setRange(1, 50)
        self.top_matches_spin.setValue(10)
        self.top_matches_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 60px;
            }
        """)
        
        layout.addWidget(self.top_matches_spin)
        layout.addStretch()
        
        return group
    
    def _create_search_button(self) -> QtWidgets.QPushButton:
        """buat search button"""
        btn = QtWidgets.QPushButton("Search")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        btn.clicked.connect(self._on_search_clicked)
        return btn
    
    def _on_search_clicked(self):
        """handle search button click"""
        keywords_text = self.keywords_input.text().strip()
        if not keywords_text:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter keywords to search"
            )
            return
        
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        keywords = [kw for kw in keywords if kw]
        
        if not keywords:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter valid keywords"
            )
            return
        
        algorithm = 'KMP'
        if self.bm_radio.isChecked():
            algorithm = 'BM'
        elif self.ac_radio.isChecked():
            algorithm = 'AC'
        
        top_n = self.top_matches_spin.value()
        
        self.search_requested.emit(keywords, algorithm, top_n)
    
    def set_search_enabled(self, enabled: bool):
        """enable/disable search functionality"""
        self.keywords_input.setEnabled(enabled)
        self.kmp_radio.setEnabled(enabled)
        self.bm_radio.setEnabled(enabled)
        self.ac_radio.setEnabled(enabled)
        self.top_matches_spin.setEnabled(enabled)

class ResultsPanel(QtWidgets.QWidget):
    """panel untuk menampilkan hasil pencarian"""
    
    summary_requested = QtCore.pyqtSignal(str)
    view_cv_requested = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_results = []
        self.setup_ui()
    
    def setup_ui(self):
        """setup user interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # timing section
        self.timing_label = QtWidgets.QLabel("")
        self.timing_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 12px;
                color: #2c3e50;
            }
        """)
        self.timing_label.hide()
        layout.addWidget(self.timing_label)
        
        # results header
        self.results_header = QtWidgets.QLabel("Results")
        self.results_header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        self.results_header.hide()
        layout.addWidget(self.results_header)
        
        # scroll area for results
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # container widget for results
        self.results_widget = QtWidgets.QWidget()
        self.results_layout = QtWidgets.QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(10)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area.setWidget(self.results_widget)
        layout.addWidget(self.scroll_area)
        
        # initial message
        self.show_initial_message()
    
    def show_initial_message(self):
        """tampilkan pesan awal"""
        msg = QtWidgets.QLabel("Enter keywords and click Search to find matching CVs")
        msg.setAlignment(QtCore.Qt.AlignCenter)
        msg.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 16px;
                padding: 50px;
            }
        """)
        self.results_layout.addWidget(msg)
        self.results_layout.addStretch()
    
    def show_search_results(self, results: List[SearchResult], timing_info: str):
        """tampilkan hasil pencarian"""
        self.clear_results()
        
        self.timing_label.setText(timing_info)
        self.timing_label.show()
        
        result_count = len(results)
        self.results_header.setText(f"Results ({result_count} CVs scanned)")
        self.results_header.show()
        
        if not results:
            self.show_no_results()
            return
        
        self.search_results = results
        
        for i, result in enumerate(results):
            card = self._create_result_card(result, i + 1)
            self.results_layout.addWidget(card)
        
        self.results_layout.addStretch()
    
    def show_no_results(self):
        """tampilkan pesan tidak ada hasil"""
        msg = QtWidgets.QLabel("No matching CVs found")
        msg.setAlignment(QtCore.Qt.AlignCenter)
        msg.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 16px;
                padding: 30px;
            }
        """)
        self.results_layout.addWidget(msg)
        self.results_layout.addStretch()
    
    def clear_results(self):
        """bersihkan hasil sebelumnya"""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.timing_label.hide()
        self.results_header.hide()
    
    def _create_result_card(self, result: SearchResult, rank: int) -> QtWidgets.QWidget:
        """buat card untuk satu hasil pencarian"""
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px;
            }
            QFrame:hover {
                border-color: #3498db;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # header dengan nama dan rank
        header_layout = QtWidgets.QHBoxLayout()
        
        # nama candidate
        name = result.resume.name or result.resume.id
        name_label = QtWidgets.QLabel(f"{rank}. {name}")
        name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(name_label)
        
        # total matches
        matches_label = QtWidgets.QLabel(f"{result.total_matches} matches")
        matches_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #27ae60;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(matches_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # matched keywords
        keywords_text = self._format_matched_keywords(result.keyword_matches)
        keywords_label = QtWidgets.QLabel(keywords_text)
        keywords_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 10px;
            }
        """)
        keywords_label.setWordWrap(True)
        layout.addWidget(keywords_label)
        
        # buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        # summary button
        summary_btn = QtWidgets.QPushButton("Summary")
        summary_btn.setStyleSheet(self._get_button_style("#3498db"))
        summary_btn.clicked.connect(
            lambda: self.summary_requested.emit(result.resume.id)
        )
        buttons_layout.addWidget(summary_btn)
        
        # view cv button
        view_btn = QtWidgets.QPushButton("View CV")
        view_btn.setStyleSheet(self._get_button_style("#2ecc71"))
        view_btn.clicked.connect(
            lambda: self.view_cv_requested.emit(result.resume.id)
        )
        buttons_layout.addWidget(view_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return card
    
    def _format_matched_keywords(self, keyword_matches: dict) -> str:
        """format matched keywords untuk display"""
        if not keyword_matches:
            return "No keywords matched"
        
        formatted = []
        for keyword, count in keyword_matches.items():
            if count > 0:
                formatted.append(f"{keyword}: {count} occurrence{'s' if count > 1 else ''}")
        
        return "; ".join(formatted) if formatted else "No keywords matched"
    
    def _get_button_style(self, color: str) -> str:
        """ambil style untuk button"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """
    
    def show_loading(self, message: str = "Searching..."):
        """tampilkan loading state"""
        self.clear_results()
        
        loading_widget = QtWidgets.QWidget()
        loading_layout = QtWidgets.QVBoxLayout(loading_widget)
        loading_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        loading_label = QtWidgets.QLabel(message)
        loading_label.setAlignment(QtCore.Qt.AlignCenter)
        loading_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #3498db;
                padding: 50px;
            }
        """)
        
        loading_layout.addWidget(loading_label)
        self.results_layout.addWidget(loading_widget)

class SummaryView(QtWidgets.QDialog):
    """dialog untuk menampilkan summary cv"""
    
    view_cv_requested = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resume_id = None
        self.setup_ui()
        
    def setup_ui(self):
        """setup user interface"""
        self.setWindowTitle("CV Summary")
        self.setModal(True)
        self.resize(600, 700)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # header
        header = self._create_header()
        layout.addWidget(header)
        
        # scroll area for content
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # content widget
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(0, 0, 10, 0)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        # buttons
        buttons = self._create_buttons()
        layout.addWidget(buttons)
    
    def _create_header(self) -> QtWidgets.QWidget:
        """buat header dengan nama"""
        header = QtWidgets.QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(header)
        
        self.name_label = QtWidgets.QLabel("CV Summary")
        self.name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        layout.addWidget(self.name_label)
        layout.addStretch()
        
        return header
    
    def _create_buttons(self) -> QtWidgets.QWidget:
        """buat buttons di bagian bawah"""
        buttons_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(buttons_widget)
        
        # view cv button
        view_cv_btn = QtWidgets.QPushButton("View CV")
        view_cv_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        view_cv_btn.clicked.connect(self._on_view_cv_clicked)
        layout.addWidget(view_cv_btn)
        
        layout.addStretch()
        
        # close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return buttons_widget
    
    def show_summary(self, resume_id: str, summary: CVSummary):
        """tampilkan cv summary"""
        self.resume_id = resume_id
        
        # update header
        self.name_label.setText(summary.name)
        
        # clear previous content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # contact info
        if summary.contact_info:
            self._add_section("Contact Information", self._format_contact_info(summary.contact_info))
        
        # overview
        if summary.summary:
            self._add_section("Summary", summary.summary)
        
        # skills
        if summary.skills:
            self._add_skills_section(summary.skills)
        
        # experience
        if summary.experience:
            self._add_experience_section(summary.experience)
        
        # education
        if summary.education:
            self._add_education_section(summary.education)
        
        # add stretch at end
        self.content_layout.addStretch()
        
        # show dialog
        self.show()
    
    def _add_section(self, title: str, content: str):
        """tambah section dengan title dan content"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # content
        content_label = QtWidgets.QLabel(content)
        content_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #34495e;
                background-color: transparent;
                line-height: 1.4;
            }
        """)
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        self.content_layout.addWidget(section)
    
    def _add_skills_section(self, skills: list):
        """tambah section skills dengan tags"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel("Skills")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # skills container
        skills_widget = QtWidgets.QWidget()
        skills_layout = QtWidgets.QHBoxLayout(skills_widget)
        skills_layout.setContentsMargins(0, 0, 0, 0)
        
        # create skill tags
        for skill in skills[:8]:
            skill_tag = QtWidgets.QLabel(skill)
            skill_tag.setStyleSheet("""
                QLabel {
                    background-color: #3498db;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            skill_tag.setAlignment(QtCore.Qt.AlignCenter)
            skills_layout.addWidget(skill_tag)
        
        skills_layout.addStretch()
        layout.addWidget(skills_widget)
        
        self.content_layout.addWidget(section)
    
    def _add_experience_section(self, experiences: list):
        """tambah section experience"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel("Job History")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # experience items
        for exp in experiences:
            exp_widget = QtWidgets.QWidget()
            exp_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 4px;
                    padding: 10px;
                }
            """)
            
            exp_layout = QtWidgets.QVBoxLayout(exp_widget)
            exp_layout.setSpacing(4)
            exp_layout.setContentsMargins(0, 0, 0, 0)
            
            # position and period
            header = QtWidgets.QLabel(f"{exp.get('position', 'Position')} • {exp.get('period', 'Period')}")
            header.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #2c3e50;
                    background-color: transparent;
                }
            """)
            exp_layout.addWidget(header)
            
            # company
            company = QtWidgets.QLabel(exp.get('company', 'Company'))
            company.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #7f8c8d;
                    background-color: transparent;
                }
            """)
            exp_layout.addWidget(company)
            
            layout.addWidget(exp_widget)
        
        self.content_layout.addWidget(section)
    
    def _add_education_section(self, education: list):
        """tambah section education"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel("Education")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # education items
        for edu in education:
            edu_widget = QtWidgets.QWidget()
            edu_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 4px;
                    padding: 10px;
                }
            """)
            
            edu_layout = QtWidgets.QVBoxLayout(edu_widget)
            edu_layout.setSpacing(4)
            edu_layout.setContentsMargins(0, 0, 0, 0)
            
            # degree and year
            header = QtWidgets.QLabel(f"{edu.get('degree', 'Degree')} • {edu.get('year', 'Year')}")
            header.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #2c3e50;
                    background-color: transparent;
                }
            """)
            edu_layout.addWidget(header)
            
            # institution
            institution = QtWidgets.QLabel(edu.get('institution', 'Institution'))
            institution.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #7f8c8d;
                    background-color: transparent;
                }
            """)
            edu_layout.addWidget(institution)
            
            layout.addWidget(edu_widget)
        
        self.content_layout.addWidget(section)
    
    def _format_contact_info(self, contact_info: dict) -> str:
        """format contact info untuk display"""
        formatted = []
        
        if 'phone' in contact_info:
            formatted.append(f"Phone: {contact_info['phone']}")
        
        if 'email' in contact_info:
            formatted.append(f"Email: {contact_info['email']}")
        
        if 'address' in contact_info:
            formatted.append(f"Address: {contact_info['address']}")
        
        return "\n".join(formatted) if formatted else "No contact information available"
    
    def _on_view_cv_clicked(self):
        """handle view cv button click"""
        if self.resume_id:
            self.view_cv_requested.emit(self.resume_id)

# ===== MAIN APPLICATION =====
class MainWindow(QtWidgets.QMainWindow):
    """main window aplikasi cv search"""
    
    def __init__(self):
        super().__init__()
        
        # controllers
        self.search_controller = SearchController()
        self.cv_controller = CVController()
        
        # ui components
        self.search_panel = None
        self.results_panel = None
        self.summary_view = None
        
        # setup
        self.setup_ui()
        self.setup_connections()
        self.check_database_connection()
    
    def setup_ui(self):
        """setup user interface"""
        self.setWindowTitle("ATS CV Search Application")
        self.setGeometry(100, 100, 1200, 800)
        
        # central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # main layout
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # left panel (search)
        self.search_panel = SearchPanel()
        self.search_panel.setFixedWidth(350)
        self.search_panel.setStyleSheet("""
            SearchPanel {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        main_layout.addWidget(self.search_panel)
        
        # right panel (results)
        self.results_panel = ResultsPanel()
        self.results_panel.setStyleSheet("""
            ResultsPanel {
                background-color: white;
            }
        """)
        main_layout.addWidget(self.results_panel)
        
        # summary view (dialog)
        self.summary_view = SummaryView(self)
        
        # status bar
        self.statusBar().showMessage("Ready - Enter keywords to search CVs")
        
        # style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                padding: 5px;
            }
        """)
    
    def setup_connections(self):
        """setup signal connections"""
        # search panel signals
        self.search_panel.search_requested.connect(self.perform_search)
        
        # results panel signals
        self.results_panel.summary_requested.connect(self.show_cv_summary)
        self.results_panel.view_cv_requested.connect(self.view_cv_file)
        
        # summary view signals
        self.summary_view.view_cv_requested.connect(self.view_cv_file)
    
    def check_database_connection(self):
        """cek koneksi database saat startup"""
        print("Checking database connection...")
        
        db_config = DatabaseConfig()
        conn = db_config.get_connection()
        
        if not conn:
            print("❌ Database connection failed")
            QtWidgets.QMessageBox.critical(
                self,
                "Database Error",
                "Cannot connect to database. Please check your MySQL connection."
            )
            self.statusBar().showMessage("Database connection failed")
        else:
            print("✓ Database connected successfully")
            conn.close()
            self.statusBar().showMessage("Database connected - Ready to search")
    
    @QtCore.pyqtSlot(list, str, int)
    def perform_search(self, keywords, algorithm, top_n):
        """handle search request"""
        try:
            # update ui state
            self.search_panel.set_search_enabled(False)
            self.results_panel.show_loading("Searching CVs...")
            self.statusBar().showMessage(f"Searching for: {', '.join(keywords)}")
            
            # process events to update ui
            QtWidgets.QApplication.processEvents()
            
            # perform search
            results, timing_info = self.search_controller.search_cvs(
                keywords=keywords,
                algorithm=algorithm,
                top_n=top_n,
                fuzzy_threshold=0.7
            )
            
            # show results
            self.results_panel.show_search_results(results, timing_info)
            
            # update status
            result_count = len(results)
            self.statusBar().showMessage(
                f"Found {result_count} matching CVs for: {', '.join(keywords)}"
            )
            
        except Exception as e:
            # handle errors
            QtWidgets.QMessageBox.critical(
                self,
                "Search Error", 
                f"An error occurred during search:\n{str(e)}"
            )
            self.statusBar().showMessage("Search failed")
            
        finally:
            # restore ui state
            self.search_panel.set_search_enabled(True)
    
    @QtCore.pyqtSlot(str)
    def show_cv_summary(self, resume_id):
        """tampilkan summary cv"""
        try:
            self.statusBar().showMessage("Loading CV summary...")
            
            # ambil summary cv
            cv_summary = self.cv_controller.get_cv_summary(resume_id)
            
            if cv_summary:
                self.summary_view.show_summary(resume_id, cv_summary)
                self.statusBar().showMessage("CV summary loaded")
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "Could not load CV summary. The file might be corrupted or missing."
                )
                self.statusBar().showMessage("Failed to load CV summary")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Summary Error",
                f"Error loading CV summary:\n{str(e)}"
            )
            self.statusBar().showMessage("Summary loading failed")
    
    @QtCore.pyqtSlot(str)
    def view_cv_file(self, resume_id):
        """buka file cv"""
        try:
            self.statusBar().showMessage("Opening CV file...")
            
            success = self.cv_controller.open_cv_file(resume_id)
            
            if success:
                self.statusBar().showMessage("CV file opened")
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "Could not open CV file. The file might be missing or corrupted."
                )
                self.statusBar().showMessage("Failed to open CV file")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "File Error",
                f"Error opening CV file:\n{str(e)}"
            )
            self.statusBar().showMessage("File opening failed")
    
    def closeEvent(self, event):
        """handle aplikasi closing"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    """entry point aplikasi"""
    print("=== ATS CV SEARCH APPLICATION ===")
    print("Starting application...")
    
    try:
        # create qt application
        app = QtWidgets.QApplication(sys.argv)
        
        # set application properties
        app.setApplicationName("ATS CV Search")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("Stima Tubes 3")
        
        print("✓ Qt Application created")
        
        # create and show main window
        window = MainWindow()
        window.show()
        
        print("✓ Main window created and shown")
        print("✓ Application ready!")
        
        # run application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()