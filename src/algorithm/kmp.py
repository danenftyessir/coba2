class KMPMatcher:
    def __init__(self):
        self.pattern = None
        self.lps = None
    
    def _compute_lps(self, pattern):
        """hitung longest prefix suffix array untuk pattern"""
        length = len(pattern)
        lps = [0] * length
        prefix_len = 0
        i = 1
        
        while i < length:
            if pattern[i] == pattern[prefix_len]:
                prefix_len += 1
                lps[i] = prefix_len
                i += 1
            else:
                if prefix_len != 0:
                    prefix_len = lps[prefix_len - 1]
                else:
                    lps[i] = 0
                    i += 1
        
        return lps
    
    def search(self, text, pattern):
        """cari pattern dalam text menggunakan algoritma kmp"""
        if not pattern or not text:
            return {}
        
        # preprocessing pattern
        self.pattern = pattern
        self.lps = self._compute_lps(pattern)
        
        results = {}
        text_len = len(text)
        pattern_len = len(pattern)
        
        i = 0  # index untuk text
        j = 0  # index untuk pattern
        
        while i < text_len:
            if j < pattern_len and text[i] == pattern[j]:
                i += 1
                j += 1
            
            if j == pattern_len:
                # pattern ditemukan
                if pattern not in results:
                    results[pattern] = []
                results[pattern].append(i - j)
                
                # lanjut cari overlap
                j = self.lps[j - 1]
            elif i < text_len and (j == 0 or text[i] != pattern[j]):
                if j != 0:
                    j = self.lps[j - 1]
                else:
                    i += 1
        
        return results
    
    def search_multiple(self, text, patterns):
        """cari multiple patterns dalam text"""
        all_results = {}
        
        for pattern in patterns:
            pattern = pattern.strip()
            if pattern:
                results = self.search(text, pattern)
                if results:
                    all_results.update(results)
        
        return all_results