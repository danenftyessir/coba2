# src/utils/regex_extractor.py
import re
from typing import List, Dict, Optional
from database.models import CVSummary, JobHistory, Education

class RegexExtractor:
    """ekstraksi informasi cv menggunakan regex dengan job history dan education lengkap"""
    
    def __init__(self):
        # regex patterns untuk berbagai format
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        self.date_pattern = r'\b(?:0?[1-9]|1[0-2])[\/\-](?:0?[1-9]|[12][0-9]|3[01])[\/\-](?:19|20)\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:0?[1-9]|[12][0-9]|3[01])[\s,]+(?:19|20)\d{2}\b'
        
        # section keywords
        self.experience_keywords = ['EXPERIENCE', 'WORK HISTORY', 'EMPLOYMENT', 'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE']
        self.education_keywords = ['EDUCATION', 'ACADEMIC', 'QUALIFICATIONS', 'ACADEMIC BACKGROUND']
        self.skills_keywords = ['SKILLS', 'TECHNICAL SKILLS', 'COMPETENCIES', 'CORE COMPETENCIES', 'TECHNICAL COMPETENCIES']
        self.summary_keywords = ['SUMMARY', 'PROFILE', 'OVERVIEW', 'OBJECTIVE', 'PROFESSIONAL SUMMARY']
    
    def extract_summary(self, text: str) -> CVSummary:
        """ekstrak summary lengkap dari cv text dengan job history dan education"""
        return CVSummary(
            name=self._extract_name(text),
            contact_info=self._extract_contact_info(text),
            skills=self._extract_skills(text),
            job_history=self._extract_job_history(text),
            education=self._extract_education(text),
            summary=self._extract_overview(text)
        )
    
    def _extract_name(self, text: str) -> str:
        """ekstrak nama dari cv dengan multiple patterns"""
        lines = text.split('\n')
        
        # try first few non-empty lines
        for line in lines[:5]:
            line = line.strip()
            if not line:
                continue
            
            # skip common headers
            if any(word in line.upper() for word in ['CURRICULUM', 'VITAE', 'RESUME', 'CV']):
                continue
            
            # look for name pattern (2-3 capitalized words)
            words = line.split()
            name_words = []
            
            for word in words[:4]:  # max 4 words for name
                # check if word looks like a name (starts with capital)
                if re.match(r'^[A-Z][a-z]+$', word) and len(word) > 1:
                    name_words.append(word)
                elif re.match(r'^[A-Z][a-z]*\.$', word):  # middle initial
                    name_words.append(word)
            
            if len(name_words) >= 2:  # at least first and last name
                return " ".join(name_words)
        
        return "Unknown"
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """ekstrak informasi kontak dengan multiple patterns"""
        contact = {}
        
        # email
        email_match = re.search(self.email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()
        
        # phone - more flexible pattern
        phone_patterns = [
            r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\b(?:\+62|62|0)[\s-]?8[1-9][\s-]?\d{1,2}[\s-]?\d{3,4}[\s-]?\d{3,4}\b',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact['phone'] = phone_match.group()
                break
        
        # address - look for address patterns
        address_patterns = [
            r'(?:Address|Location):\s*([^\n]+)',
            r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b[^\n]*',
            r'\b[A-Za-z\s]+,\s*[A-Za-z\s]+\s+\d{5}\b'
        ]
        
        for pattern in address_patterns:
            address_match = re.search(pattern, text, re.IGNORECASE)
            if address_match:
                contact['address'] = address_match.group(1) if address_match.groups() else address_match.group()
                break
        
        return contact
    
    def _extract_skills(self, text: str) -> List[str]:
        """ekstrak skills dengan pattern recognition yang lebih baik"""
        skills = []
        
        # find skills section
        skills_section = self._extract_section(text, self.skills_keywords)
        
        if skills_section:
            # clean and split skills
            skills_text = re.sub(r'\n+', '\n', skills_section)
            
            # common delimiters for skills
            skills_items = re.split(r'[,;\n•\-\*\|]', skills_text)
            
            for skill in skills_items:
                skill = skill.strip()
                # filter out common non-skill words
                if skill and len(skill) > 1 and not any(word in skill.lower() for word in ['skills', 'technical', 'proficient']):
                    # clean parentheses and extra characters
                    skill = re.sub(r'[():]', '', skill).strip()
                    if skill:
                        skills.append(skill)
        
        # if no skills section found, look for common technical skills
        if not skills:
            common_skills = [
                'Python', 'Java', 'JavaScript', 'React', 'HTML', 'CSS', 'SQL',
                'MySQL', 'PostgreSQL', 'MongoDB', 'Docker', 'Kubernetes',
                'Git', 'Linux', 'Windows', 'MacOS', 'AWS', 'Azure',
                'Machine Learning', 'Data Analysis', 'Project Management',
                'Microsoft Office', 'Excel', 'PowerPoint', 'Word'
            ]
            
            for skill in common_skills:
                if skill.lower() in text.lower():
                    skills.append(skill)
        
        return skills[:15]  # limit to 15 skills
    
    def _extract_job_history(self, text: str) -> List[JobHistory]:
        """ekstrak job history dengan pattern recognition yang comprehensive"""
        job_history = []
        
        # find experience section
        experience_section = self._extract_section(text, self.experience_keywords)
        
        if not experience_section:
            return job_history
        
        # split into job entries
        # look for date patterns to identify job entries
        date_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)',
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|Present|Current)',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4}|Present)',
        ]
        
        # find all date ranges
        date_matches = []
        for pattern in date_patterns:
            matches = list(re.finditer(pattern, experience_section, re.IGNORECASE))
            date_matches.extend(matches)
        
        # sort by position in text
        date_matches.sort(key=lambda x: x.start())
        
        # extract job entries
        for i, match in enumerate(date_matches):
            start_pos = match.start()
            end_pos = date_matches[i + 1].start() if i + 1 < len(date_matches) else len(experience_section)
            
            job_text = experience_section[start_pos:end_pos].strip()
            
            # extract job details
            job = self._parse_job_entry(job_text)
            if job:
                job_history.append(job)
        
        # if no date-based entries found, try alternative parsing
        if not job_history:
            job_history = self._extract_jobs_alternative(experience_section)
        
        return job_history[:5]  # limit to 5 jobs
    
    def _extract_education(self, text: str) -> List[Education]:
        """ekstrak education dengan pattern recognition yang comprehensive"""
        education_list = []
        
        # find education section
        education_section = self._extract_section(text, self.education_keywords)
        
        if not education_section:
            return education_list
        
        # look for degree patterns
        degree_patterns = [
            r'(Bachelor|Master|PhD|Ph\.D|MBA|BS|BA|MS|MA|B\.S|B\.A|M\.S|M\.A)\.?\s+(?:of\s+|in\s+)?([^\n,]+)',
            r'(High School|Diploma|Certificate)\s+(?:in\s+)?([^\n,]*)',
            r'(\d{4})\s*[-–]\s*(\d{4})\s*[:\-]?\s*([^\n]+)',
            r'([^\n]+(?:University|College|Institute|School)[^\n]*)'
        ]
        
        # find institutions and years
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, education_section)
        
        # try to match degree patterns
        for pattern in degree_patterns:
            matches = re.finditer(pattern, education_section, re.IGNORECASE)
            
            for match in matches:
                if len(match.groups()) >= 2:
                    degree = match.group(1).strip()
                    detail = match.group(2).strip()
                    
                    # find associated year
                    year = ""
                    if years:
                        # find closest year to this match
                        match_pos = match.start()
                        year_matches = [(y, abs(education_section.find(y) - match_pos)) for y in years]
                        year_matches.sort(key=lambda x: x[1])
                        if year_matches:
                            year = year_matches[0][0]
                    
                    # determine if detail is institution or field
                    if any(word in detail.lower() for word in ['university', 'college', 'institute', 'school']):
                        institution = detail
                        degree_field = degree
                    else:
                        institution = "Institution"
                        degree_field = f"{degree} in {detail}"
                    
                    education_list.append(Education(
                        degree=degree_field,
                        institution=institution,
                        year=year,
                        details=match.group(0)
                    ))
        
        # if no structured education found, try simple extraction
        if not education_list:
            lines = education_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 10:  # meaningful line
                    education_list.append(Education(
                        degree="Education",
                        institution=line,
                        year="",
                        details=line
                    ))
                    break
        
        return education_list[:3]  # limit to 3 education entries
    
    def _extract_overview(self, text: str) -> Optional[str]:
        """ekstrak overview/summary dari cv"""
        # find summary section
        summary_section = self._extract_section(text, self.summary_keywords)
        
        if summary_section:
            # clean and format summary
            summary = re.sub(r'\n+', ' ', summary_section)
            summary = re.sub(r'\s+', ' ', summary).strip()
            
            # limit length
            if len(summary) > 500:
                summary = summary[:500] + "..."
            
            return summary
        
        # fallback: use first few sentences of CV
        sentences = re.split(r'[.!?]+', text)
        meaningful_sentences = []
        
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if len(sentence) > 20 and not any(word in sentence.upper() for word in ['CURRICULUM', 'VITAE', 'RESUME']):
                meaningful_sentences.append(sentence)
        
        if meaningful_sentences:
            summary = '. '.join(meaningful_sentences[:2]) + '.'
            return summary
        
        return "Professional with experience in the field."
    
    def _extract_section(self, text: str, keywords: List[str]) -> Optional[str]:
        """ekstrak section berdasarkan keywords"""
        lines = text.split('\n')
        
        # find section start
        section_start = -1
        for i, line in enumerate(lines):
            line_upper = line.upper().strip()
            if any(keyword in line_upper for keyword in keywords):
                section_start = i
                break
        
        if section_start == -1:
            return None
        
        # find section end (next major section or end of text)
        section_end = len(lines)
        major_keywords = ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS', 'AWARDS']
        
        for i in range(section_start + 1, len(lines)):
            line_upper = lines[i].upper().strip()
            # check if this line starts a new major section
            if any(keyword in line_upper for keyword in major_keywords):
                # make sure it's not the same section
                if not any(keyword in line_upper for keyword in keywords):
                    section_end = i
                    break
        
        # extract section content
        section_lines = lines[section_start + 1:section_end]
        section_content = '\n'.join(section_lines).strip()
        
        return section_content if section_content else None
    
    def _parse_job_entry(self, job_text: str) -> Optional[JobHistory]:
        """parse single job entry dari text"""
        if not job_text:
            return None
        
        # extract dates
        date_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)',
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|Present|Current)',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4}|Present)',
        ]
        
        start_date = ""
        end_date = ""
        
        for pattern in date_patterns:
            match = re.search(pattern, job_text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    start_date = match.group(1)
                    end_date = match.group(2)
                elif len(match.groups()) == 4:
                    start_date = f"{match.group(1)} {match.group(2)}"
                    end_date = f"{match.group(3)} {match.group(4)}"
                break
        
        # extract position and company
        lines = job_text.split('\n')
        position = ""
        company = ""
        description = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # skip date line
            if any(pattern in line for pattern in ['-', '–', 'Present', 'Current']) and any(char.isdigit() for char in line):
                continue
            
            # first meaningful line is usually position/company
            if not position and len(line) > 3:
                # check if line contains common position keywords
                if any(word in line.lower() for word in ['engineer', 'manager', 'developer', 'analyst', 'coordinator', 'specialist']):
                    position = line
                elif any(word in line.lower() for word in ['company', 'corp', 'inc', 'ltd', 'llc']):
                    company = line
                else:
                    position = line
            elif not company and len(line) > 3:
                company = line
            else:
                if description:
                    description += " " + line
                else:
                    description = line
        
        # if no clear separation, try to split position/company
        if position and not company:
            parts = position.split(' - ')
            if len(parts) == 2:
                position = parts[0].strip()
                company = parts[1].strip()
            elif ',' in position:
                parts = position.split(',')
                position = parts[0].strip()
                company = parts[1].strip()
        
        # set defaults if empty
        if not position:
            position = "Position"
        if not company:
            company = "Company"
        
        return JobHistory(
            position=position,
            company=company,
            start_date=start_date,
            end_date=end_date,
            description=description[:200] if description else None
        )
    
    def _extract_jobs_alternative(self, experience_text: str) -> List[JobHistory]:
        """alternative method untuk extract jobs jika date-based parsing gagal"""
        jobs = []
        
        # split by double newlines or common separators
        job_sections = re.split(r'\n\n+|\n(?=[A-Z][a-z])', experience_text)
        
        for section in job_sections:
            section = section.strip()
            if len(section) > 20:  # meaningful section
                lines = section.split('\n')
                if len(lines) >= 2:
                    # assume first line is position, second is company
                    position = lines[0].strip()
                    company = lines[1].strip() if len(lines) > 1 else "Company"
                    description = '\n'.join(lines[2:]) if len(lines) > 2 else ""
                    
                    jobs.append(JobHistory(
                        position=position,
                        company=company,
                        start_date="",
                        end_date="",
                        description=description[:200] if description else None
                    ))
        
        return jobs[:3]  # limit to 3 jobs