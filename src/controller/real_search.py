import time
from ..algorithm.kmp import KMPMatcher
from ..algorithm.bm import BoyerMooreMatcher
from ..algorithm.aho_corasick import AhoCorasick
from ..algorithm.levenshtein import LevenshteinMatcher
from ..utils.timer import Timer
from .real_pdf_extractor import RealPDFExtractor

class RealSearchController:
    """search controller dengan real database integration"""
    
    def __init__(self, repository):
        self.repository = repository
        self.kmp_matcher = KMPMatcher()
        self.bm_matcher = BoyerMooreMatcher()
        self.ac_matcher = AhoCorasick()
        self.levenshtein_matcher = LevenshteinMatcher()
        self.pdf_extractor = RealPDFExtractor()
        self.timer = Timer()
        
        # cache untuk raw text agar tidak extract berulang
        self.text_cache = {}
        
    def search(self, keywords, algorithm="KMP", top_n=10):
        """cari cv berdasarkan keywords dengan real database"""
        try:
            # parse keywords dan threshold untuk levenshtein
            threshold = 0.7
            if "|threshold=" in keywords:
                keywords, threshold_part = keywords.split("|threshold=")
                threshold = float(threshold_part)
            
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
            if not keyword_list:
                return {
                    'results': [],
                    'algorithm_time': 0,
                    'fuzzy_match_time': 0,
                    'total_cvs_scanned': 0,
                    'algorithm_used': algorithm,
                    'error': 'masukkan minimal 1 keyword'
                }
            
            # ambil semua cv dari database
            all_cvs = self.repository.get_all_cvs()
            if not all_cvs:
                return {
                    'results': [],
                    'algorithm_time': 0,
                    'fuzzy_match_time': 0,
                    'total_cvs_scanned': 0,
                    'algorithm_used': algorithm,
                    'error': 'tidak ada CV dalam database'
                }
            
            print(f"🔍 scanning {len(all_cvs)} CVs dengan algoritma {algorithm}")
            
            # proses pencarian berdasarkan algoritma
            self.timer.start()
            
            if algorithm == "LD":
                results = self._search_levenshtein(all_cvs, keyword_list, threshold)
            elif algorithm == "AC":
                results = self._search_aho_corasick(all_cvs, keyword_list)
            elif algorithm == "BM":
                results = self._search_boyer_moore(all_cvs, keyword_list)
            else:  # KMP (default)
                results = self._search_kmp(all_cvs, keyword_list)
            
            algorithm_time = self.timer.stop()
            
            # sort berdasarkan total matches
            results.sort(key=lambda x: x['total_matches'], reverse=True)
            
            # ambil top N
            final_results = results[:top_n]
            
            print(f"📊 [{algorithm}] total results: {len(results)}, showing top {len(final_results)}")
            
            return {
                'results': final_results,
                'algorithm_time': algorithm_time,
                'fuzzy_match_time': 0,
                'total_cvs_scanned': len(all_cvs),
                'algorithm_used': algorithm,
                'threshold': threshold if algorithm == "LD" else None
            }
        
        except Exception as e:
            print(f"❌ search error: {e}")
            return {
                'results': [],
                'algorithm_time': 0,
                'fuzzy_match_time': 0,
                'total_cvs_scanned': 0,
                'algorithm_used': algorithm,
                'error': f'error during search: {str(e)}'
            }
    
    def _get_cv_text(self, cv_data):
        """ambil text cv dengan caching"""
        cv_path = cv_data['cv_path']
        
        # cek cache dulu
        if cv_path in self.text_cache:
            return self.text_cache[cv_path]
        
        # prioritas: raw_text dari database, lalu extract pdf
        if cv_data.get('raw_text'):
            text = cv_data['raw_text']
        else:
            text = self.pdf_extractor.extract_text(cv_path)
        
        # cache text
        if text:
            self.text_cache[cv_path] = text
        
        return text or ""
    
    def _search_kmp(self, all_cvs, keyword_list):
        """pencarian menggunakan knuth-morris-pratt"""
        results = []
        
        for cv in all_cvs:
            try:
                text = self._get_cv_text(cv)
                if not text:
                    continue
                
                text_lower = text.lower()
                keyword_matches = {}
                total_matches = 0
                
                for keyword in keyword_list:
                    keyword_lower = keyword.lower()
                    matches = self.kmp_matcher.search(text_lower, keyword_lower)
                    
                    if keyword_lower in matches:
                        count = len(matches[keyword_lower])
                        keyword_matches[keyword] = count
                        total_matches += count
                
                if total_matches > 0:
                    results.append({
                        'applicant_id': cv['applicant_id'],
                        'name': cv['name'],
                        'cv_path': cv['cv_path'],
                        'total_matches': total_matches,
                        'keyword_matches': keyword_matches
                    })
            
            except Exception as e:
                print(f"❌ error processing CV {cv['cv_path']}: {e}")
                continue
        
        return results
    
    def _search_boyer_moore(self, all_cvs, keyword_list):
        """pencarian menggunakan boyer-moore"""
        results = []
        
        for cv in all_cvs:
            try:
                text = self._get_cv_text(cv)
                if not text:
                    continue
                
                text_lower = text.lower()
                keyword_matches = {}
                total_matches = 0
                
                for keyword in keyword_list:
                    keyword_lower = keyword.lower()
                    matches = self.bm_matcher.search(text_lower, keyword_lower)
                    
                    if keyword_lower in matches:
                        count = len(matches[keyword_lower])
                        keyword_matches[keyword] = count
                        total_matches += count
                
                if total_matches > 0:
                    results.append({
                        'applicant_id': cv['applicant_id'],
                        'name': cv['name'],
                        'cv_path': cv['cv_path'],
                        'total_matches': total_matches,
                        'keyword_matches': keyword_matches
                    })
            
            except Exception as e:
                print(f"❌ error processing CV {cv['cv_path']}: {e}")
                continue
        
        return results
    
    def _search_aho_corasick(self, all_cvs, keyword_list):
        """pencarian menggunakan aho-corasick"""
        results = []
        
        # build automaton untuk semua keywords
        keywords_lower = [kw.lower() for kw in keyword_list]
        ac_automaton = AhoCorasick(keywords_lower)
        
        for cv in all_cvs:
            try:
                text = self._get_cv_text(cv)
                if not text:
                    continue
                
                text_lower = text.lower()
                matches = ac_automaton.search(text_lower)
                
                if matches:
                    keyword_matches = {}
                    total_matches = 0
                    
                    for found_keyword, positions in matches.items():
                        # cari keyword asli
                        original_keyword = None
                        for orig in keyword_list:
                            if orig.lower() == found_keyword:
                                original_keyword = orig
                                break
                        
                        if original_keyword:
                            count = len(positions)
                            keyword_matches[original_keyword] = count
                            total_matches += count
                    
                    if total_matches > 0:
                        results.append({
                            'applicant_id': cv['applicant_id'],
                            'name': cv['name'],
                            'cv_path': cv['cv_path'],
                            'total_matches': total_matches,
                            'keyword_matches': keyword_matches
                        })
            
            except Exception as e:
                print(f"❌ error processing CV {cv['cv_path']}: {e}")
                continue
        
        return results
    
    def _search_levenshtein(self, all_cvs, keyword_list, threshold):
        """pencarian menggunakan levenshtein distance"""
        results = []
        
        for cv in all_cvs:
            try:
                text = self._get_cv_text(cv)
                if not text:
                    continue
                
                keyword_matches = {}
                total_matches = 0
                
                for keyword in keyword_list:
                    matches = self.levenshtein_matcher.search(text, keyword, threshold)
                    
                    if matches:
                        for match_key, positions in matches.items():
                            count = len(positions)
                            best_matches = self.levenshtein_matcher.find_best_matches(
                                keyword, text, threshold, max_results=1
                            )
                            if best_matches:
                                best_word, score = best_matches[0]
                                fuzzy_key = f"{keyword} (~{best_word}, {score:.2f})"
                            else:
                                fuzzy_key = f"{keyword} (fuzzy)"
                            
                            keyword_matches[fuzzy_key] = count
                            total_matches += count
                
                if total_matches > 0:
                    results.append({
                        'applicant_id': cv['applicant_id'],
                        'name': cv['name'],
                        'cv_path': cv['cv_path'],
                        'total_matches': total_matches,
                        'keyword_matches': keyword_matches
                    })
            
            except Exception as e:
                print(f"❌ error processing CV {cv['cv_path']}: {e}")
                continue
        
        return results