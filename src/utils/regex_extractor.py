import re
from typing import Dict, List, Optional, Any
from datetime import datetime

class RegexExtractor:
    """ekstrak informasi dari cv text menggunakan regex"""
    
    def __init__(self):
        # regex patterns untuk berbagai informasi
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+62|62|0)[\s-]?(?:\d{3,4}[\s-]?){2,3}\d{3,4}',
            'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+',
            'github': r'(?:https?://)?(?:www\.)?github\.com/[\w-]+',
            'date': r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b',
            'skills_section': r'(?i)(?:skills?|keahlian|kemampuan|competenc(?:y|ies))[\s:]*([^\n]+(?:\n[^\n]+)*)',
            'education_section': r'(?i)(?:education|pendidikan|academic)[\s:]*([^\n]+(?:\n[^\n]+)*)',
            'experience_section': r'(?i)(?:experience|pengalaman|work history|employment)[\s:]*([^\n]+(?:\n[^\n]+)*)',
            'summary_section': r'(?i)(?:summary|ringkasan|objective|profile|about)[\s:]*([^\n]+(?:\n[^\n]+)*)'
        }
        
        # common programming languages and tech skills
        self.tech_skills = [
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin',
            'go', 'rust', 'scala', 'r', 'matlab', 'sql', 'nosql', 'mongodb', 'postgresql',
            'mysql', 'oracle', 'redis', 'elasticsearch', 'docker', 'kubernetes', 'aws',
            'azure', 'gcp', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'spring', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'machine learning', 'deep learning', 'data science', 'ai', 'nlp',
            'computer vision', 'git', 'jenkins', 'ci/cd', 'agile', 'scrum'
        ]
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """ekstrak semua informasi dari cv text"""
        if not text:
            return {}
        
        result = {
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'linkedin_url': self.extract_linkedin(text),
            'github_url': self.extract_github(text),
            'skills': self.extract_skills(text),
            'education_history': self.extract_education(text),
            'work_experience': self.extract_experience(text),
            'summary_overview': self.extract_summary(text),
            'dates': self.extract_dates(text)
        }
        
        return result
    
    def extract_email(self, text: str) -> Optional[str]:
        """ekstrak email address"""
        matches = re.findall(self.patterns['email'], text)
        return matches[0] if matches else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """ekstrak phone number"""
        matches = re.findall(self.patterns['phone'], text)
        if matches:
            # normalize phone number
            phone = matches[0].replace(' ', '').replace('-', '')
            return phone
        return None
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """ekstrak linkedin url"""
        matches = re.findall(self.patterns['linkedin'], text, re.IGNORECASE)
        return matches[0] if matches else None
    
    def extract_github(self, text: str) -> Optional[str]:
        """ekstrak github url"""
        matches = re.findall(self.patterns['github'], text, re.IGNORECASE)
        return matches[0] if matches else None
    
    def extract_skills(self, text: str) -> str:
        """ekstrak skills dari cv"""
        # coba cari section skills
        skills_match = re.search(self.patterns['skills_section'], text, re.MULTILINE | re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            # clean up text
            skills_text = re.sub(r'\n+', ', ', skills_text)
            skills_text = re.sub(r'\s+', ' ', skills_text)
            return skills_text.strip()
        
        # fallback: cari tech skills di seluruh text
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.tech_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return ', '.join(found_skills) if found_skills else ''
    
    def extract_education(self, text: str) -> str:
        """ekstrak education history"""
        edu_match = re.search(self.patterns['education_section'], text, re.MULTILINE | re.DOTALL)
        
        if edu_match:
            edu_text = edu_match.group(1)
            # ambil beberapa baris saja
            lines = edu_text.split('\n')[:5]
            return '\n'.join(line.strip() for line in lines if line.strip())
        
        return ''
    
    def extract_experience(self, text: str) -> str:
        """ekstrak work experience"""
        exp_match = re.search(self.patterns['experience_section'], text, re.MULTILINE | re.DOTALL)
        
        if exp_match:
            exp_text = exp_match.group(1)
            # ambil beberapa baris saja
            lines = exp_text.split('\n')[:8]
            return '\n'.join(line.strip() for line in lines if line.strip())
        
        return ''
    
    def extract_summary(self, text: str) -> str:
        """ekstrak summary/objective"""
        summary_match = re.search(self.patterns['summary_section'], text, re.MULTILINE | re.DOTALL)
        
        if summary_match:
            summary_text = summary_match.group(1)
            # ambil beberapa baris saja
            lines = summary_text.split('\n')[:3]
            return ' '.join(line.strip() for line in lines if line.strip())
        
        return ''
    
    def extract_dates(self, text: str) -> List[str]:
        """ekstrak semua dates dari text"""
        dates = re.findall(self.patterns['date'], text)
        return dates
    
    def extract_years_of_experience(self, text: str) -> Optional[int]:
        """coba estimasi years of experience"""
        # cari pattern seperti "5 years experience", "5+ years", dll
        year_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def extract_gpa(self, text: str) -> Optional[float]:
        """ekstrak gpa/ipk"""
        gpa_patterns = [
            r'(?:GPA|IPK)[\s:]*(\d+\.\d+)',
            r'(\d+\.\d+)\s*/\s*4\.0',
            r'(?:Grade|Nilai)[\s:]*(\d+\.\d+)'
        ]
        
        for pattern in gpa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gpa = float(match.group(1))
                if 0 <= gpa <= 4.0:
                    return gpa
        
        return None