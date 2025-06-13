# src/database/models.py
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import date

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
class JobHistory:
    """model job history dari regex extraction"""
    position: str
    company: str
    start_date: str
    end_date: str
    description: Optional[str] = None

@dataclass
class Education:
    """model education dari regex extraction"""
    degree: str
    institution: str
    year: str
    details: Optional[str] = None

@dataclass
class CVSummary:
    """model summary cv yang diekstrak lengkap"""
    name: str
    contact_info: Dict[str, str]  # phone, email, address
    skills: List[str]
    job_history: List[JobHistory]
    education: List[Education]
    summary: Optional[str] = None

@dataclass
class SearchResult:
    """model hasil pencarian cv dengan semua detail"""
    resume: Resume
    keyword_matches: Dict[str, int]  # {keyword: count}
    total_matches: int
    matched_keywords: List[str]
    cv_summary: Optional[CVSummary] = None
    fuzzy_matches: Optional[Dict[str, int]] = None

@dataclass
class SearchTimingInfo:
    """model informasi timing search"""
    algorithm_used: str
    total_cvs_scanned: int
    exact_match_time: float = 0.0
    fuzzy_match_time: float = 0.0
    total_results: int = 0
    
    def to_display_string(self) -> str:
        """format timing info untuk display"""
        exact_time = f"{self.exact_match_time:.0f}ms"
        
        if self.fuzzy_match_time > 0:
            fuzzy_time = f"{self.fuzzy_match_time:.0f}ms"
            return f"exact match ({self.algorithm_used}): {self.total_cvs_scanned} cvs in {exact_time}\nfuzzy match: processed in {fuzzy_time}"
        else:
            return f"exact match ({self.algorithm_used}): {self.total_cvs_scanned} cvs in {exact_time}"