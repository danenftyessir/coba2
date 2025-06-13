# src/utils/timer.py
import time
from typing import Dict, Optional

class SearchTimer:
    """timer khusus untuk operasi search dengan timing yang akurat dan optimized"""
    
    def __init__(self):
        self.start_times: Dict[str, float] = {}
        self.search_results: Dict[str, any] = {}
    
    def start_exact_search(self, algorithm: str, num_cvs: int):
        """mulai timer untuk exact search"""
        self.search_results['algorithm'] = algorithm
        self.search_results['num_cvs'] = num_cvs
        self.start_times['exact_search'] = time.perf_counter()
    
    def stop_exact_search(self) -> float:
        """stop timer exact search dan return duration ms"""
        if 'exact_search' in self.start_times:
            duration = (time.perf_counter() - self.start_times['exact_search']) * 1000
            self.search_results['exact_duration'] = duration
            del self.start_times['exact_search']
            return duration
        return 0.0
    
    def start_fuzzy_search(self, num_keywords: int):
        """mulai timer untuk fuzzy search"""
        self.search_results['fuzzy_keywords'] = num_keywords
        self.start_times['fuzzy_search'] = time.perf_counter()
    
    def stop_fuzzy_search(self) -> float:
        """stop timer fuzzy search dan return duration ms"""
        if 'fuzzy_search' in self.start_times:
            duration = (time.perf_counter() - self.start_times['fuzzy_search']) * 1000
            self.search_results['fuzzy_duration'] = duration
            del self.start_times['fuzzy_search']
            return duration
        return 0.0
    
    def get_search_summary(self) -> str:
        """buat summary hasil search timing"""
        if 'exact_duration' not in self.search_results:
            return "no search performed"
        
        algorithm = self.search_results.get('algorithm', 'unknown')
        num_cvs = self.search_results.get('num_cvs', 0)
        exact_time = f"{self.search_results['exact_duration']:.0f}ms"
        
        summary = f"exact match ({algorithm}): {num_cvs} cvs scanned in {exact_time}"
        
        if 'fuzzy_duration' in self.search_results:
            fuzzy_keywords = self.search_results.get('fuzzy_keywords', 0)
            fuzzy_time = f"{self.search_results['fuzzy_duration']:.0f}ms"
            summary += f"\nfuzzy match: {fuzzy_keywords} keywords processed in {fuzzy_time}"
        
        return summary
    
    def reset(self):
        """reset search timer"""
        self.start_times.clear()
        self.search_results.clear()

class Timer:
    """general purpose timer utility dengan high precision"""
    
    def __init__(self):
        self.start_time = None
    
    def start(self):
        """start timer dengan high precision"""
        self.start_time = time.perf_counter()
    
    def stop(self) -> float:
        """stop timer dan return elapsed time dalam ms"""
        if self.start_time:
            elapsed = (time.perf_counter() - self.start_time) * 1000
            self.start_time = None
            return elapsed
        return 0.0
    
    def elapsed(self) -> float:
        """get elapsed time tanpa stop timer"""
        if self.start_time:
            return (time.perf_counter() - self.start_time) * 1000
        return 0.0
    
    def lap(self) -> float:
        """get lap time tanpa stop timer"""
        return self.elapsed()

class PerformanceTimer:
    """advanced timer untuk performance monitoring"""
    
    def __init__(self):
        self.timings = {}
        self.active_timers = {}
    
    def start_timer(self, name: str):
        """start named timer"""
        self.active_timers[name] = time.perf_counter()
    
    def stop_timer(self, name: str) -> float:
        """stop named timer dan return duration"""
        if name in self.active_timers:
            duration = (time.perf_counter() - self.active_timers[name]) * 1000
            self.timings[name] = duration
            del self.active_timers[name]
            return duration
        return 0.0
    
    def get_timing(self, name: str) -> float:
        """get timing result"""
        return self.timings.get(name, 0.0)
    
    def get_all_timings(self) -> Dict[str, float]:
        """get all timing results"""
        return self.timings.copy()
    
    def clear(self):
        """clear all timings"""
        self.timings.clear()
        self.active_timers.clear()
    
    def summary(self) -> str:
        """generate timing summary"""
        if not self.timings:
            return "no timings recorded"
        
        lines = []
        for name, duration in self.timings.items():
            lines.append(f"{name}: {duration:.2f}ms")
        
        return "\n".join(lines)