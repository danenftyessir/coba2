class LevenshteinMatcher:
    """implementasi levenshtein distance untuk fuzzy matching dengan optimasi"""
    
    def __init__(self):
        self.cache = {}  # cache untuk memoization
    
    def distance(self, s1: str, s2: str) -> int:
        """hitung levenshtein distance antara dua string dengan optimasi"""
        # cek cache
        cache_key = (s1, s2)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # base cases
        if not s1:
            return len(s2)
        if not s2:
            return len(s1)
        
        # quick check untuk exact match
        if s1 == s2:
            self.cache[cache_key] = 0
            return 0
        
        # optimasi untuk string yang sangat berbeda panjangnya
        len_diff = abs(len(s1) - len(s2))
        if len_diff > min(len(s1), len(s2)):
            result = max(len(s1), len(s2))
            self.cache[cache_key] = result
            return result
        
        # buat matrix dengan optimasi space
        m, n = len(s1), len(s2)
        
        # gunakan dua baris saja untuk menghemat memory
        prev_row = list(range(n + 1))
        curr_row = [0] * (n + 1)
        
        for i in range(1, m + 1):
            curr_row[0] = i
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    curr_row[j] = prev_row[j-1]  # no operation needed
                else:
                    curr_row[j] = 1 + min(
                        prev_row[j],      # deletion
                        curr_row[j-1],    # insertion
                        prev_row[j-1]     # substitution
                    )
            
            # swap rows
            prev_row, curr_row = curr_row, prev_row
        
        result = prev_row[n]
        self.cache[cache_key] = result
        return result
    
    def similarity(self, s1: str, s2: str) -> float:
        """hitung similarity score (0.0 - 1.0) antara dua string"""
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        # normalize strings untuk case-insensitive
        s1_lower = s1.lower().strip()
        s2_lower = s2.lower().strip()
        
        # exact match
        if s1_lower == s2_lower:
            return 1.0
        
        # hitung distance
        dist = self.distance(s1_lower, s2_lower)
        max_len = max(len(s1), len(s2))
        
        # convert distance ke similarity score
        if max_len == 0:
            return 1.0
        
        similarity = 1.0 - (dist / max_len)
        return max(0.0, similarity)
    
    def search(self, text: str, pattern: str, threshold: float = 0.7) -> dict:
        """cari pattern dalam text dengan fuzzy matching - interface untuk kompatibilitas"""
        if not text or not pattern:
            return {}
        
        results = {}
        words = text.split()
        pattern_lower = pattern.lower()
        
        matches = []
        for i, word in enumerate(words):
            # hitung similarity dengan pattern
            score = self.similarity(word, pattern)
            
            if score >= threshold:
                matches.append(i)  # simpan index kata yang match
        
        if matches:
            # format hasil seperti algoritma lain (pattern: [positions])
            # untuk fuzzy, kita hitung posisi karakter di text
            positions = []
            for word_idx in matches:
                # hitung posisi karakter awal kata di text
                char_pos = sum(len(words[j]) + 1 for j in range(word_idx))
                positions.append(char_pos)
            
            results[pattern] = positions
        
        return results
    
    def search_multiple(self, text: str, patterns: list, threshold: float = 0.7) -> dict:
        """cari multiple patterns dalam text dengan fuzzy matching"""
        all_results = {}
        
        for pattern in patterns:
            pattern = pattern.strip()
            if pattern:
                results = self.search(text, pattern, threshold)
                if results:
                    # tambahkan info fuzzy ke nama pattern
                    for key, positions in results.items():
                        fuzzy_key = f"{key} (fuzzy)"
                        all_results[fuzzy_key] = positions
        
        return all_results
    
    def find_best_matches(self, target: str, text: str, threshold: float = 0.7, max_results: int = 10) -> list:
        """cari kata-kata terbaik yang mirip dengan target"""
        if not text or not target:
            return []
        
        words = text.split()
        target_lower = target.lower()
        
        # hitung similarity untuk semua kata
        word_scores = []
        for word in words:
            score = self.similarity(word, target)
            if score >= threshold:
                word_scores.append((word, score))
        
        # sort berdasarkan score (descending)
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        # return top results
        return word_scores[:max_results]
    
    def get_suggestions(self, target: str, candidates: list, threshold: float = 0.6, max_suggestions: int = 5) -> list:
        """dapatkan saran kata yang mirip"""
        if not candidates or not target:
            return []
        
        target_lower = target.lower()
        suggestions = []
        
        for candidate in candidates:
            score = self.similarity(candidate, target)
            if score >= threshold:
                suggestions.append((candidate, score))
        
        # sort berdasarkan score
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return [word for word, score in suggestions[:max_suggestions]]
    
    def clear_cache(self):
        """clear cache untuk memory management"""
        self.cache.clear()
    
    def get_cache_size(self):
        """ambil ukuran cache untuk monitoring"""
        return len(self.cache)

# testing function
def test_levenshtein():
    """test levenshtein implementation"""
    matcher = LevenshteinMatcher()
    
    test_cases = [
        ("python", "pyton", 0.8),      # typo
        ("javascript", "java", 0.5),   # partial match
        ("sql", "mysql", 0.6),         # contains
        ("react", "angular", 0.1),     # different
    ]
    
    print("=== LEVENSHTEIN TEST ===")
    for s1, s2, expected_min in test_cases:
        similarity = matcher.similarity(s1, s2)
        distance = matcher.distance(s1, s2)
        
        print(f"'{s1}' vs '{s2}':")
        print(f"  Distance: {distance}")
        print(f"  Similarity: {similarity:.2f}")
        print(f"  Expected >= {expected_min}: {'✅' if similarity >= expected_min else '❌'}")
        print()
    
    # test search functionality
    text = "python java javascript sql mysql postgresql"
    pattern = "java"
    results = matcher.search(text, pattern, threshold=0.6)
    
    print(f"Search '{pattern}' in '{text}':")
    print(f"Results: {results}")
    
    return True

if __name__ == "__main__":
    test_levenshtein()