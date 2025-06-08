class LevenshteinMatcher:
    """implementasi levenshtein distance untuk fuzzy matching dengan optimasi dan sensitivity tinggi"""
    
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
        """hitung similarity score (0.0 - 1.0) antara dua string dengan precision tinggi"""
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
        
        # untuk string pendek, gunakan jaro-winkler style calculation
        if len(s1_lower) <= 3 or len(s2_lower) <= 3:
            return self._short_string_similarity(s1_lower, s2_lower)
        
        # hitung distance
        dist = self.distance(s1_lower, s2_lower)
        max_len = max(len(s1_lower), len(s2_lower))
        min_len = min(len(s1_lower), len(s2_lower))
        
        # advanced similarity calculation dengan weighting
        if max_len == 0:
            return 1.0
        
        # base similarity dengan normalized levenshtein
        base_sim = 1.0 - (dist / max_len)
        
        # bonus untuk common prefix/suffix
        prefix_bonus = self._get_prefix_bonus(s1_lower, s2_lower)
        suffix_bonus = self._get_suffix_bonus(s1_lower, s2_lower)
        
        # bonus untuk common substrings
        substring_bonus = self._get_substring_bonus(s1_lower, s2_lower)
        
        # penalty untuk length difference
        length_penalty = abs(len(s1_lower) - len(s2_lower)) / max_len * 0.15
        
        # bonus untuk character frequency similarity
        char_freq_bonus = self._get_char_frequency_bonus(s1_lower, s2_lower)
        
        # final similarity dengan fine-tuning yang lebih sensitif
        final_sim = (base_sim + 
                    prefix_bonus + 
                    suffix_bonus + 
                    substring_bonus + 
                    char_freq_bonus - 
                    length_penalty)
        
        # apply logarithmic scaling untuk sensitivity yang lebih tinggi
        if final_sim > 0.5:
            final_sim = 0.5 + (final_sim - 0.5) * 1.2
        elif final_sim > 0.3:
            final_sim = 0.3 + (final_sim - 0.3) * 1.1
        
        return max(0.0, min(1.0, final_sim))
    
    def _short_string_similarity(self, s1: str, s2: str) -> float:
        """similarity khusus untuk string pendek dengan sensitivity tinggi"""
        if s1 == s2:
            return 1.0
        
        # hitung common characters
        common_chars = sum(1 for c in s1 if c in s2)
        max_chars = max(len(s1), len(s2))
        
        if max_chars == 0:
            return 1.0
            
        base_sim = common_chars / max_chars
        
        # bonus jika ada subsequence match
        if self._is_subsequence(s1, s2) or self._is_subsequence(s2, s1):
            base_sim += 0.25
            
        # bonus untuk partial match di awal/akhir
        if s1.startswith(s2[:2]) or s2.startswith(s1[:2]):
            base_sim += 0.15
            
        return min(1.0, base_sim)
    
    def _get_prefix_bonus(self, s1: str, s2: str) -> float:
        """bonus untuk common prefix dengan scaling"""
        common_prefix = 0
        min_len = min(len(s1), len(s2))
        
        for i in range(min(4, min_len)):  # max 4 char prefix
            if s1[i] == s2[i]:
                common_prefix += 1
            else:
                break
        
        if common_prefix > 0:
            # scaling bonus berdasarkan panjang prefix
            bonus = (common_prefix / min(4, min_len)) * 0.2
            if common_prefix >= 3:
                bonus *= 1.5  # extra bonus untuk prefix panjang
            return bonus
        return 0.0
    
    def _get_suffix_bonus(self, s1: str, s2: str) -> float:
        """bonus untuk common suffix dengan scaling"""
        common_suffix = 0
        min_len = min(len(s1), len(s2))
        
        for i in range(1, min(4, min_len) + 1):  # max 3 char suffix
            if s1[-i] == s2[-i]:
                common_suffix += 1
            else:
                break
        
        if common_suffix > 0:
            bonus = (common_suffix / min(3, min_len)) * 0.1
            if common_suffix >= 2:
                bonus *= 1.3
            return bonus
        return 0.0
    
    def _get_substring_bonus(self, s1: str, s2: str) -> float:
        """bonus untuk common substrings"""
        if len(s1) < 3 or len(s2) < 3:
            return 0.0
        
        # cari longest common substring
        max_common = 0
        for i in range(len(s1) - 2):
            for j in range(i + 3, min(len(s1) + 1, i + 6)):  # max 5 char substring
                substr = s1[i:j]
                if substr in s2:
                    max_common = max(max_common, len(substr))
        
        if max_common >= 3:
            return (max_common / max(len(s1), len(s2))) * 0.15
        return 0.0
    
    def _get_char_frequency_bonus(self, s1: str, s2: str) -> float:
        """bonus berdasarkan similarity frequency karakter"""
        from collections import Counter
        
        freq1 = Counter(s1)
        freq2 = Counter(s2)
        
        # hitung cosine similarity dari frequency vectors
        common_chars = set(freq1.keys()) & set(freq2.keys())
        if not common_chars:
            return 0.0
        
        dot_product = sum(freq1[char] * freq2[char] for char in common_chars)
        norm1 = sum(freq ** 2 for freq in freq1.values()) ** 0.5
        norm2 = sum(freq ** 2 for freq in freq2.values()) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        cosine_sim = dot_product / (norm1 * norm2)
        return cosine_sim * 0.1
    
    def _is_subsequence(self, s1: str, s2: str) -> bool:
        """cek apakah s1 adalah subsequence dari s2"""
        i = 0
        for char in s2:
            if i < len(s1) and s1[i] == char:
                i += 1
        return i == len(s1)
    
    def search(self, text: str, pattern: str, threshold: float = 0.7) -> dict:
        """cari pattern dalam text dengan fuzzy matching yang lebih sensitif"""
        if not text or not pattern:
            return {}
        
        results = {}
        words = text.split()
        pattern_lower = pattern.lower()
        
        matches = []
        scores = []  # simpan scores untuk debugging
        
        for i, word in enumerate(words):
            # bersihkan word dari punctuation
            clean_word = ''.join(c for c in word if c.isalnum()).lower()
            if not clean_word:
                continue
                
            # hitung similarity dengan pattern
            score = self.similarity(clean_word, pattern_lower)
            scores.append((word, score))
            
            # gunakan threshold yang lebih strict
            if score >= threshold:
                matches.append(i)
        
        if matches:
            # format hasil seperti algoritma lain (pattern: [positions])
            positions = []
            for word_idx in matches:
                # hitung posisi karakter awal kata di text
                char_pos = 0
                for j in range(word_idx):
                    char_pos += len(words[j]) + 1  # +1 for space
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
        """cari kata-kata terbaik yang mirip dengan target dengan ranking yang lebih akurat"""
        if not text or not target:
            return []
        
        words = text.split()
        target_lower = target.lower()
        
        # hitung similarity untuk semua kata
        word_scores = []
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum()).lower()
            if not clean_word:
                continue
                
            score = self.similarity(clean_word, target_lower)
            if score >= threshold:
                word_scores.append((word, score))
        
        # sort berdasarkan score (descending) dengan precision tinggi
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        # return top results
        return word_scores[:max_results]
    
    def get_suggestions(self, target: str, candidates: list, threshold: float = 0.6, max_suggestions: int = 5) -> list:
        """dapatkan saran kata yang mirip dengan threshold sensitivity"""
        if not candidates or not target:
            return []
        
        target_lower = target.lower()
        suggestions = []
        
        for candidate in candidates:
            clean_candidate = ''.join(c for c in candidate if c.isalnum()).lower()
            score = self.similarity(clean_candidate, target_lower)
            if score >= threshold:
                suggestions.append((candidate, score))
        
        # sort berdasarkan score dengan precision
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return [word for word, score in suggestions[:max_suggestions]]
    
    def clear_cache(self):
        """clear cache untuk memory management"""
        self.cache.clear()
    
    def get_cache_size(self):
        """ambil ukuran cache untuk monitoring"""
        return len(self.cache)
    
    def debug_similarity(self, s1: str, s2: str) -> dict:
        """debugging function untuk melihat komponen similarity"""
        s1_lower = s1.lower().strip()
        s2_lower = s2.lower().strip()
        
        dist = self.distance(s1_lower, s2_lower)
        max_len = max(len(s1_lower), len(s2_lower))
        base_sim = 1.0 - (dist / max_len) if max_len > 0 else 1.0
        
        prefix_bonus = self._get_prefix_bonus(s1_lower, s2_lower)
        suffix_bonus = self._get_suffix_bonus(s1_lower, s2_lower)
        substring_bonus = self._get_substring_bonus(s1_lower, s2_lower)
        char_freq_bonus = self._get_char_frequency_bonus(s1_lower, s2_lower)
        length_penalty = abs(len(s1_lower) - len(s2_lower)) / max_len * 0.15 if max_len > 0 else 0
        
        final_sim = self.similarity(s1, s2)
        
        return {
            'distance': dist,
            'base_similarity': base_sim,
            'prefix_bonus': prefix_bonus,
            'suffix_bonus': suffix_bonus,
            'substring_bonus': substring_bonus,
            'char_freq_bonus': char_freq_bonus,
            'length_penalty': length_penalty,
            'final_similarity': final_sim
        }

# testing function dengan variasi threshold
def test_levenshtein_sensitivity():
    """test sensitivity levenshtein implementation dengan berbagai threshold"""
    matcher = LevenshteinMatcher()
    
    test_cases = [
        ("python", "pyton"),      # typo
        ("javascript", "java"),   # partial match
        ("sql", "mysql"),         # contains
        ("react", "angular"),     # different
        ("express", "expres"),    # minor typo
        ("node", "nodejs"),       # extension
        ("html", "htm"),          # abbreviation
        ("css", "scss"),          # similar
    ]
    
    thresholds = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]
    
    print("=== LEVENSHTEIN SENSITIVITY TEST ===")
    
    for s1, s2 in test_cases:
        print(f"\nComparing '{s1}' vs '{s2}':")
        
        # debug similarity components
        debug_info = matcher.debug_similarity(s1, s2)
        print(f"  Distance: {debug_info['distance']}")
        print(f"  Base similarity: {debug_info['base_similarity']:.4f}")
        print(f"  Final similarity: {debug_info['final_similarity']:.4f}")
        
        # test different thresholds
        print("  Threshold results:")
        for threshold in thresholds:
            results = matcher.search(f"test {s2} example", s1, threshold)
            match_status = "✓" if results else "✗"
            print(f"    {threshold:.2f}: {match_status}")
    
    return True

if __name__ == "__main__":
    test_levenshtein_sensitivity()