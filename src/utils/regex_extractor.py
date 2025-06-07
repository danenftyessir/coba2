# src/utils/regex_extractor.py
import re
from typing import List, Dict, Optional
from ..database.models import CVSummary

class RegexExtractor:
    """ekstraksi informasi cv menggunakan regex"""
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        self.date_pattern = r'\b(?:0?[1-9]|1[0-2])[\/\-](?:0?[1-9]|[12][0-9]|3[01])[\/\-](?:19|20)\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:0?[1-9]|[12][0-9]|3[01])[\s,]+(?:19|20)\d{2}\b'
        
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
            # asumsi nama ada di baris pertama yang tidak kosong
            for line in lines:
                line = line.strip()
                if line and not re.match(r'^[A-Z\s]+$', line):  # bukan header all caps
                    # ambil kata-kata yang dimulai huruf kapital
                    words = line.split()
                    name_words = []
                    for word in words[:3]:  # max 3 kata untuk nama
                        if re.match(r'^[A-Z][a-z]+', word):
                            name_words.append(word)
                    if name_words:
                        return " ".join(name_words)
        return "Unknown"
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """ekstrak informasi kontak"""
        contact = {}
        
        # email
        email_match = re.search(self.email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()
        
        # phone
        phone_match = re.search(self.phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        # address (sederhana - ambil setelah kata address)
        address_pattern = r'(?:address|location):\s*([^\n]+)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            contact['address'] = address_match.group(1).strip()
        
        return contact
    
    def _extract_skills(self, text: str) -> List[str]:
        """ekstrak skills dari cv"""
        skills = []
        
        # cari section skills
        skills_pattern = r'(?:skills?|technical skills?|core competencies):\s*([^\.]+?)(?:\n\n|\.\s*[A-Z]|$)'
        skills_match = re.search(skills_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            # split by common delimiters
            skill_items = re.split(r'[,;\n•\-\*]', skills_text)
            
            for skill in skill_items:
                skill = skill.strip()
                if skill and len(skill) > 1:
                    skills.append(skill)
        
        # fallback: cari skill keywords umum
        if not skills:
            skill_keywords = [
                'python', 'java', 'javascript', 'react', 'html', 'css', 'sql',
                'mysql', 'postgresql', 'mongodb', 'docker', 'kubernetes',
                'machine learning', 'data analysis', 'project management',
                'teamwork', 'leadership', 'communication'
            ]
            
            for keyword in skill_keywords:
                if keyword.lower() in text.lower():
                    skills.append(keyword.title())
        
        return skills[:10]  # max 10 skills
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """ekstrak pengalaman kerja"""
        experiences = []
        
        # pattern untuk experience section
        exp_pattern = r'(?:experience|work history|employment):(.*?)(?:education|skills|$)'
        exp_match = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if exp_match:
            exp_text = exp_match.group(1)
            
            # cari date ranges dan job titles
            job_pattern = r'(\d{2}/\d{4}\s*-\s*\d{2}/\d{4}|\d{4}\s*-\s*\d{4}).*?([A-Z][^.\n]+)'
            job_matches = re.findall(job_pattern, exp_text)
            
            for date_range, title in job_matches:
                experiences.append({
                    'period': date_range.strip(),
                    'position': title.strip(),
                    'company': 'Company Name'  # placeholder
                })
        
        return experiences[:5]  # max 5 experiences
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """ekstrak riwayat pendidikan"""
        education = []
        
        # pattern untuk education section
        edu_pattern = r'(?:education|academic background):(.*?)(?:experience|skills|$)'
        edu_match = re.search(edu_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if edu_match:
            edu_text = edu_match.group(1)
            
            # cari degree dan institution
            degree_pattern = r'(\d{4})\s*([^,\n]+),?\s*([^,\n]+)'
            degree_matches = re.findall(degree_pattern, edu_text)
            
            for year, degree, institution in degree_matches:
                education.append({
                    'year': year.strip(),
                    'degree': degree.strip(),
                    'institution': institution.strip()
                })
        
        return education[:3]  # max 3 education entries
    
    def _extract_overview(self, text: str) -> str:
        """ekstrak overview/summary"""
        # cari summary section
        summary_pattern = r'(?:summary|overview|profile):\s*([^\.]+\.)'
        summary_match = re.search(summary_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if summary_match:
            summary = summary_match.group(1).strip()
            return summary
        
        # fallback: ambil beberapa kalimat pertama
        sentences = re.split(r'\.\s+', text)
        if len(sentences) > 1:
            return ". ".join(sentences[:2]) + "."
        
        return "Professional with experience in the field."