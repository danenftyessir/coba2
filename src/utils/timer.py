# src/utils/timer.py
import time
from typing import Dict, Optional

class Timer:
    """utility untuk mengukur waktu eksekusi"""
    
    def __init__(self):
        self.start_times: Dict[str, float] = {}
        self.durations: Dict[str, float] = {}
    
    def start(self, name: str) -> None:
        """mulai timer dengan nama tertentu"""
        self.start_times[name] = time.time()
    
    def stop(self, name: str) -> float:
        """stop timer dan return duration dalam ms"""
        if name not in self.start_times:
            return 0.0
        
        end_time = time.time()
        duration = (end_time - self.start_times[name]) * 1000  # convert to ms
        self.durations[name] = duration
        
        # cleanup
        del self.start_times[name]
        
        return duration
    
    def get_duration(self, name: str) -> Optional[float]:
        """ambil duration timer yang sudah selesai"""
        return self.durations.get(name)
    
    def get_all_durations(self) -> Dict[str, float]:
        """ambil semua duration yang sudah diukur"""
        return self.durations.copy()
    
    def clear(self) -> None:
        """bersihkan semua timer"""
        self.start_times.clear()
        self.durations.clear()
    
    def format_duration(self, duration: float) -> str:
        """format duration ke string yang readable"""
        if duration < 1:
            return f"{duration:.2f}ms"
        elif duration < 1000:
            return f"{duration:.0f}ms"
        else:
            return f"{duration/1000:.2f}s"

class SearchTimer:
    """timer khusus untuk operasi search"""
    
    def __init__(self):
        self.timer = Timer()
        self.search_results = {}
    
    def start_exact_search(self, algorithm: str, num_cvs: int) -> None:
        """mulai timer untuk exact search"""
        self.search_results['algorithm'] = algorithm
        self.search_results['num_cvs'] = num_cvs
        self.timer.start('exact_search')
    
    def stop_exact_search(self) -> float:
        """stop timer exact search"""
        duration = self.timer.stop('exact_search')
        self.search_results['exact_duration'] = duration
        return duration
    
    def start_fuzzy_search(self, num_keywords: int) -> None:
        """mulai timer untuk fuzzy search"""
        self.search_results['fuzzy_keywords'] = num_keywords
        self.timer.start('fuzzy_search')
    
    def stop_fuzzy_search(self) -> float:
        """stop timer fuzzy search"""
        duration = self.timer.stop('fuzzy_search')
        self.search_results['fuzzy_duration'] = duration
        return duration
    
    def get_search_summary(self) -> str:
        """buat summary hasil search timing"""
        if 'exact_duration' not in self.search_results:
            return "No search performed"
        
        algorithm = self.search_results.get('algorithm', 'Unknown')
        num_cvs = self.search_results.get('num_cvs', 0)
        exact_time = self.timer.format_duration(self.search_results['exact_duration'])
        
        summary = f"Exact Match ({algorithm}): {num_cvs} CVs scanned in {exact_time}"
        
        if 'fuzzy_duration' in self.search_results:
            fuzzy_keywords = self.search_results.get('fuzzy_keywords', 0)
            fuzzy_time = self.timer.format_duration(self.search_results['fuzzy_duration'])
            summary += f"\nFuzzy Match: {fuzzy_keywords} keywords processed in {fuzzy_time}"
        
        return summary
    
    def reset(self) -> None:
        """reset search timer"""
        self.timer.clear()
        self.search_results.clear()