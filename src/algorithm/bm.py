class BoyerMooreMatcher:
    def __init__(self):
        self.pattern = None
        self.bad_char = None
        self.good_suffix = None
    
    def _compute_bad_char_table(self, pattern):
        """hitung bad character table untuk pattern"""
        bad_char = {}
        
        # isi tabel untuk semua karakter ascii
        for i in range(256):
            bad_char[chr(i)] = -1
        
        # update posisi terakhir setiap karakter dalam pattern
        for i in range(len(pattern)):
            bad_char[pattern[i]] = i
        
        return bad_char
    
    def _compute_good_suffix_table(self, pattern):
        """hitung good suffix table untuk pattern - DIPERBAIKI"""
        m = len(pattern)
        good_suffix = [m] * m  # default shift = pattern length
        
        # simple good suffix implementation untuk konsistensi
        for i in range(m):
            good_suffix[i] = max(1, m - i - 1)  # minimal shift 1
        
        return good_suffix
    
    def search(self, text, pattern):
        """cari pattern dalam text menggunakan algoritma boyer-moore - DIPERBAIKI"""
        if not pattern or not text:
            return {}
        
        # preprocessing
        self.pattern = pattern
        self.bad_char = self._compute_bad_char_table(pattern)
        self.good_suffix = self._compute_good_suffix_table(pattern)
        
        results = {}
        text_len = len(text)
        pattern_len = len(pattern)
        
        shift = 0
        
        while shift <= text_len - pattern_len:
            j = pattern_len - 1
            
            # matching dari kanan ke kiri
            while j >= 0 and pattern[j] == text[shift + j]:
                j -= 1
            
            if j < 0:
                # pattern ditemukan
                if pattern not in results:
                    results[pattern] = []
                results[pattern].append(shift)
                
                # PERBAIKAN: untuk overlapping search, shift minimal 1
                shift += 1
            else:
                # karakter tidak match, hitung shift
                # PERBAIKAN: gunakan bad character heuristic yang benar
                bad_char_shift = max(1, j - self.bad_char.get(text[shift + j], -1))
                
                # PERBAIKAN: good suffix shift yang lebih konservatif
                good_suffix_shift = 1 if j >= len(self.good_suffix) else max(1, self.good_suffix[j])
                
                # ambil shift maksimum tapi minimal 1
                shift += max(bad_char_shift, good_suffix_shift, 1)
        
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

# test function untuk validasi
def test_boyer_moore_consistency():
    """test apakah BM memberikan hasil sama dengan implementasi naive"""
    
    def naive_search(text, pattern):
        """implementasi naive untuk comparison"""
        results = {pattern: []}
        for i in range(len(text) - len(pattern) + 1):
            if text[i:i+len(pattern)] == pattern:
                results[pattern].append(i)
        return results if results[pattern] else {}
    
    # test cases
    test_cases = [
        ("python java sql python", "python"),
        ("aaaa", "aa"),  # overlapping
        ("hello world hello", "hello"),
        ("abcdefg", "xyz"),  # not found
        ("SQL database SQL queries SQL", "SQL"),
    ]
    
    bm = BoyerMooreMatcher()
    
    print("=== BOYER-MOORE CONSISTENCY TEST ===")
    all_passed = True
    
    for text, pattern in test_cases:
        bm_result = bm.search(text, pattern)
        naive_result = naive_search(text, pattern)
        
        print(f"Text: '{text}'")
        print(f"Pattern: '{pattern}'")
        print(f"BM Result: {bm_result}")
        print(f"Naive Result: {naive_result}")
        
        if bm_result == naive_result:
            print("✅ CONSISTENT")
        else:
            print("❌ INCONSISTENT!")
            all_passed = False
        
        print("-" * 40)
    
    return all_passed

if __name__ == "__main__":
    success = test_boyer_moore_consistency()
    if success:
        print("🎉 Boyer-Moore implementation is CORRECT!")
    else:
        print("❌ Boyer-Moore needs more fixes!")