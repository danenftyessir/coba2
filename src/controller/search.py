# src/controller/search.py
from typing import List, Tuple
from ..database.models import SearchResult, SearchTimingInfo
from ..database.repo import ResumeRepository
from ..utils.pdf_extractor import PDFExtractor
from ..utils.timer import SearchTimer
from ..algorithm.kmp import KMPMatcher
from ..algorithm.bm import BoyerMooreMatcher
from ..algorithm.aho_corasick import AhoCorasick
from ..algorithm.levenshtein import LevenshteinMatcher

class SearchController:
    """controller untuk operasi pencarian cv dengan algoritma yang tepat"""
    
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
        """pencarian cv dengan exact dan fuzzy matching yang optimal"""
        
        print(f"🔍 starting search: keywords={keywords}, algorithm={algorithm}, threshold={fuzzy_threshold}")
        
        # reset timer
        self.timer.reset()
        
        # ambil semua resume
        resumes = self.repo.get_all_resumes()
        if not resumes:
            return [], "no cvs found in database"
        
        print(f"📄 found {len(resumes)} resumes to search")
        
        # jika user pilih levenshtein sebagai algoritma utama
        if algorithm.upper() == 'LEVENSHTEIN':
            print("🔍 using levenshtein as primary algorithm")
            self.timer.start_fuzzy_search(len(keywords))
            results = self._fuzzy_search(resumes, keywords, fuzzy_threshold)
            self.timer.stop_fuzzy_search()
            
            # sort and return
            results.sort(key=lambda x: x.total_matches, reverse=True)
            top_results = results[:top_n]
            timing_summary = self.timer.get_search_summary()
            
            print(f"🎯 levenshtein search completed with {len(top_results)} results")
            return top_results, timing_summary
        
        # untuk exact matching algorithms (KMP, BM, AC)
        self.timer.start_exact_search(algorithm, len(resumes))
        exact_results = self._exact_search(resumes, keywords, algorithm)
        self.timer.stop_exact_search()
        
        print(f"✅ exact search completed with {len(exact_results)} matches")
        
        # fuzzy matching sebagai fallback jika ada keyword yang tidak ketemu
        unfound_keywords = self._get_unfound_keywords(exact_results, keywords)
        
        if unfound_keywords:
            print(f"🔍 starting fuzzy fallback for: {unfound_keywords}")
            self.timer.start_fuzzy_search(len(unfound_keywords))
            fuzzy_results = self._fuzzy_search(resumes, unfound_keywords, fuzzy_threshold)
            self.timer.stop_fuzzy_search()
            combined_results = self._combine_results(exact_results, fuzzy_results)
            print(f"✅ fuzzy fallback completed. total results: {len(combined_results)}")
        else:
            combined_results = exact_results
        
        # sort by total matches
        combined_results.sort(key=lambda x: x.total_matches, reverse=True)
        top_results = combined_results[:top_n]
        timing_summary = self.timer.get_search_summary()
        
        print(f"🎯 returning top {len(top_results)} results")
        return top_results, timing_summary
    
    def _exact_search(self, resumes, keywords, algorithm):
        """exact matching menggunakan algoritma yang dipilih"""
        results = []
        
        for resume in resumes:
            cv_text = self.pdf_extractor.extract_text_for_matching(resume.file_path)
            if not cv_text or cv_text == "large file skipped":
                continue
            
            keyword_matches = {}
            total_matches = 0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                if not keyword_lower:
                    continue
                
                # pilih algoritma
                matches = {}
                if algorithm.upper() == 'KMP':
                    positions = self.kmp_matcher.search(cv_text, keyword_lower)
                    if positions:
                        matches[keyword_lower] = positions
                elif algorithm.upper() == 'BM':
                    positions = self.bm_matcher.search(cv_text, keyword_lower)
                    if positions:
                        matches[keyword_lower] = positions
                elif algorithm.upper() == 'AC':
                    matches = self.aho_corasick.search_multiple(cv_text, [keyword_lower])
                else:
                    # default to KMP
                    positions = self.kmp_matcher.search(cv_text, keyword_lower)
                    if positions:
                        matches[keyword_lower] = positions
                
                # count matches
                if matches and keyword_lower in matches:
                    match_count = len(matches[keyword_lower])
                    keyword_matches[keyword] = match_count
                    total_matches += match_count
                    matched_keywords.append(keyword)
            
            # add to results if has matches
            if total_matches > 0:
                result = SearchResult(
                    resume=resume,
                    keyword_matches=keyword_matches,
                    total_matches=total_matches,
                    matched_keywords=matched_keywords
                )
                results.append(result)
        
        return results
    
    def _fuzzy_search(self, resumes, keywords, threshold):
        """fuzzy matching menggunakan levenshtein distance"""
        results = []
        
        for resume in resumes:
            cv_text = self.pdf_extractor.extract_text(resume.file_path)
            if not cv_text or cv_text == "large file skipped":
                continue
            
            fuzzy_matches = {}
            total_fuzzy_matches = 0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                if not keyword_lower:
                    continue
                
                # use levenshtein matcher
                matches = self.levenshtein_matcher.search(cv_text, keyword_lower, threshold)
                
                if matches and keyword_lower in matches:
                    match_count = len(matches[keyword_lower])
                    fuzzy_key = f"{keyword} (fuzzy)"
                    fuzzy_matches[fuzzy_key] = match_count
                    total_fuzzy_matches += match_count
                    matched_keywords.append(fuzzy_key)
            
            # add to results if has fuzzy matches
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
    
    def _get_unfound_keywords(self, results, original_keywords):
        """get keywords yang tidak ditemukan dalam exact search"""
        found_keywords = set()
        
        for result in results:
            found_keywords.update(result.matched_keywords)
        
        unfound = []
        for keyword in original_keywords:
            if keyword not in found_keywords:
                unfound.append(keyword)
        
        return unfound
    
    def _combine_results(self, exact_results, fuzzy_results):
        """combine exact dan fuzzy search results"""
        combined_dict = {}
        
        # add exact results
        for result in exact_results:
            combined_dict[result.resume.id] = result
        
        # add fuzzy results
        for fuzzy_result in fuzzy_results:
            resume_id = fuzzy_result.resume.id
            
            if resume_id in combined_dict:
                # merge with existing result
                existing = combined_dict[resume_id]
                existing.keyword_matches.update(fuzzy_result.keyword_matches)
                existing.total_matches += fuzzy_result.total_matches
                existing.matched_keywords.extend(fuzzy_result.matched_keywords)
                existing.fuzzy_matches = fuzzy_result.fuzzy_matches
            else:
                # add as new result
                combined_dict[resume_id] = fuzzy_result
        
        return list(combined_dict.values())
    
    def get_available_algorithms(self) -> List[str]:
        """get daftar algoritma yang tersedia"""
        return ['KMP', 'BM', 'AC', 'LEVENSHTEIN']
    
    def validate_keywords(self, keywords_text: str) -> Tuple[bool, List[str], str]:
        """validate dan parse keywords input"""
        if not keywords_text.strip():
            return False, [], "keywords cannot be empty"
        
        # split by comma and clean
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        keywords = [kw for kw in keywords if kw]  # remove empty
        
        if not keywords:
            return False, [], "no valid keywords found"
        
        if len(keywords) > 10:
            return False, [], "maximum 10 keywords allowed"
        
        return True, keywords, "keywords valid"