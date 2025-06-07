# src/controller/search.py
from typing import List, Dict, Tuple
from ..database.models import Resume, SearchResult
from ..database.repo import ResumeRepository
from ..utils.pdf_extractor import PDFExtractor
from ..utils.timer import SearchTimer
from ..algorithms.kmp import KMPMatcher
from ..algorithms.bm import BoyerMooreMatcher
from ..algorithms.aho_corasick import AhoCorasick
from ..algorithms.levenshtein import LevenshteinMatcher

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
        
        # reset timer
        self.timer.reset()
        
        # ambil semua resume
        resumes = self.repo.get_all_resumes()
        if not resumes:
            return [], "No CVs found in database"
        
        # mulai exact search
        self.timer.start_exact_search(algorithm, len(resumes))
        
        # exact matching
        exact_results = self._exact_search(resumes, keywords, algorithm)
        exact_duration = self.timer.stop_exact_search()
        
        # cek keyword yang tidak ditemukan untuk fuzzy search
        unfound_keywords = self._get_unfound_keywords(exact_results, keywords)
        
        # fuzzy matching jika ada keyword yang tidak ditemukan
        if unfound_keywords:
            self.timer.start_fuzzy_search(len(unfound_keywords))
            fuzzy_results = self._fuzzy_search(resumes, unfound_keywords, fuzzy_threshold)
            fuzzy_duration = self.timer.stop_fuzzy_search()
            
            # gabungkan hasil exact dan fuzzy
            combined_results = self._combine_results(exact_results, fuzzy_results)
        else:
            combined_results = exact_results
        
        # urutkan berdasarkan total matches
        combined_results.sort(key=lambda x: x.total_matches, reverse=True)
        
        # ambil top n
        top_results = combined_results[:top_n]
        
        # buat summary timing
        timing_summary = self.timer.get_search_summary()
        
        return top_results, timing_summary
    
    def _exact_search(self, resumes: List[Resume], keywords: List[str], 
                     algorithm: str) -> List[SearchResult]:
        """exact matching menggunakan algoritma yang dipilih"""
        results = []
        
        for resume in resumes:
            # ekstrak teks cv
            cv_text = self.pdf_extractor.extract_text_for_matching(resume.file_path)
            if not cv_text:
                continue
            
            # hitung matches untuk setiap keyword
            keyword_matches = {}
            total_matches = 0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                if not keyword_lower:
                    continue
                
                # pilih algoritma
                if algorithm.upper() == 'KMP':
                    matches = self.kmp_matcher.search(cv_text, keyword_lower)
                elif algorithm.upper() == 'BM':
                    matches = self.bm_matcher.search(cv_text, keyword_lower)
                elif algorithm.upper() == 'AC':  # aho-corasick
                    matches = self.aho_corasick.search_multiple(cv_text, [keyword_lower])
                else:
                    matches = self.kmp_matcher.search(cv_text, keyword_lower)
                
                # hitung jumlah matches
                if matches and keyword_lower in matches:
                    match_count = len(matches[keyword_lower])
                    keyword_matches[keyword] = match_count
                    total_matches += match_count
                    matched_keywords.append(keyword)
            
            # tambahkan ke hasil jika ada matches
            if total_matches > 0:
                result = SearchResult(
                    resume=resume,
                    keyword_matches=keyword_matches,
                    total_matches=total_matches,
                    matched_keywords=matched_keywords
                )
                results.append(result)
        
        return results
    
    def _fuzzy_search(self, resumes: List[Resume], keywords: List[str], 
                     threshold: float) -> List[SearchResult]:
        """fuzzy matching menggunakan levenshtein distance"""
        results = []
        
        for resume in resumes:
            # ekstrak teks cv
            cv_text = self.pdf_extractor.extract_text(resume.file_path)
            if not cv_text:
                continue
            
            # fuzzy search untuk setiap keyword
            fuzzy_matches = {}
            total_fuzzy_matches = 0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                if not keyword_lower:
                    continue
                
                # gunakan levenshtein matcher
                matches = self.levenshtein_matcher.search(cv_text, keyword_lower, threshold)
                
                if matches and keyword_lower in matches:
                    match_count = len(matches[keyword_lower])
                    fuzzy_matches[f"{keyword} (fuzzy)"] = match_count
                    total_fuzzy_matches += match_count
                    matched_keywords.append(f"{keyword} (fuzzy)")
            
            # tambahkan ke hasil jika ada fuzzy matches
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
    
    def _get_unfound_keywords(self, results: List[SearchResult], 
                             original_keywords: List[str]) -> List[str]:
        """ambil keyword yang tidak ditemukan dalam exact search"""
        found_keywords = set()
        
        for result in results:
            found_keywords.update(result.matched_keywords)
        
        unfound = []
        for keyword in original_keywords:
            if keyword not in found_keywords:
                unfound.append(keyword)
        
        return unfound
    
    def _combine_results(self, exact_results: List[SearchResult], 
                        fuzzy_results: List[SearchResult]) -> List[SearchResult]:
        """gabungkan hasil exact dan fuzzy search"""
        # buat dict untuk menggabungkan berdasarkan resume id
        combined_dict = {}
        
        # tambahkan exact results
        for result in exact_results:
            combined_dict[result.resume.id] = result
        
        # tambahkan fuzzy results
        for fuzzy_result in fuzzy_results:
            resume_id = fuzzy_result.resume.id
            
            if resume_id in combined_dict:
                # gabungkan dengan existing result
                existing = combined_dict[resume_id]
                existing.keyword_matches.update(fuzzy_result.keyword_matches)
                existing.total_matches += fuzzy_result.total_matches
                existing.matched_keywords.extend(fuzzy_result.matched_keywords)
                existing.fuzzy_matches = fuzzy_result.fuzzy_matches
            else:
                # tambah sebagai result baru
                combined_dict[resume_id] = fuzzy_result
        
        return list(combined_dict.values())
    
    def get_available_algorithms(self) -> List[str]:
        """ambil daftar algoritma yang tersedia"""
        return ['KMP', 'BM', 'AC']  # AC = Aho-Corasick
    
    def validate_keywords(self, keywords_text: str) -> Tuple[bool, List[str], str]:
        """validasi dan parse keywords input"""
        if not keywords_text.strip():
            return False, [], "Keywords cannot be empty"
        
        # split by comma dan bersihkan
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        keywords = [kw for kw in keywords if kw]  # hapus yang kosong
        
        if not keywords:
            return False, [], "No valid keywords found"
        
        if len(keywords) > 10:
            return False, [], "Maximum 10 keywords allowed"
        
        return True, keywords, "Keywords valid"