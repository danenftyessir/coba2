# src/database/models.py
from dataclasses import dataclass
from typing import Optional, List
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
class SearchResult:
    """model hasil pencarian cv"""
    resume: Resume
    keyword_matches: dict  # {keyword: count}
    total_matches: int
    matched_keywords: List[str]
    fuzzy_matches: dict = None  # untuk fuzzy matching results

@dataclass
class CVSummary:
    """model summary cv yang diekstrak"""
    name: str
    contact_info: dict  # phone, email, address
    skills: List[str]
    experience: List[dict]  # work history
    education: List[dict]  # education history
    summary: str  # overview/summary text