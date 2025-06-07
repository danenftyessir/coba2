class AhoCorasick:
    def __init__(self, keywords=None):
        """inisialisasi aho-corasick automaton"""
        self.goto = [{}]  # trie structure
        self.output = [[] for _ in range(1)]  # output untuk setiap node
        self.failure = [0]  # failure links
        
        if keywords:
            self._build_trie(keywords)
            self._build_failure_links()

    def _build_trie(self, keywords):
        """bangun trie dari keywords"""
        for keyword in keywords:
            if not keyword:  # skip empty keywords
                continue
                
            node = 0
            for char in keyword:
                if char not in self.goto[node]:
                    self.goto[node][char] = len(self.goto)
                    self.goto.append({})
                    self.output.append([])
                    self.failure.append(0)
                node = self.goto[node][char]
            
            # simpan keyword di end node
            self.output[node].append(keyword)

    def _build_failure_links(self):
        """bangun failure links menggunakan bfs"""
        from collections import deque
        queue = deque()
        
        # level 1 nodes (children of root)
        for char, node in self.goto[0].items():
            queue.append(node)
            self.failure[node] = 0  # failure dari root children ke root

        # bfs untuk level selanjutnya
        while queue:
            current_node = queue.popleft()
            
            for char, next_node in self.goto[current_node].items():
                queue.append(next_node)
                
                # cari failure link untuk next_node
                fail_node = self.failure[current_node]
                
                # traverse failure links sampai ketemu yang ada transisi untuk char
                while fail_node != 0 and char not in self.goto[fail_node]:
                    fail_node = self.failure[fail_node]
                
                # set failure link
                if char in self.goto[fail_node]:
                    self.failure[next_node] = self.goto[fail_node][char]
                else:
                    self.failure[next_node] = 0  # back to root
                
                # merge output dari failure node
                failure_output = self.output[self.failure[next_node]]
                self.output[next_node].extend(failure_output)

    def search(self, text):
        """cari semua keywords dalam text"""
        if not text:
            return {}
        
        results = {}  # keyword: [positions]
        current_node = 0

        for i, char in enumerate(text):
            # follow failure links jika tidak ada transisi
            while current_node != 0 and char not in self.goto[current_node]:
                current_node = self.failure[current_node]
            
            # move to next state jika ada transisi
            if char in self.goto[current_node]:
                current_node = self.goto[current_node][char]
            
            # check output untuk node saat ini
            if self.output[current_node]:
                for keyword in self.output[current_node]:
                    if keyword not in results:
                        results[keyword] = []
                    # posisi awal keyword = posisi akhir - panjang + 1
                    start_pos = i - len(keyword) + 1
                    results[keyword].append(start_pos)

        return results
    
    def search_multiple(self, text, keywords):
        """search multiple keywords - interface untuk kompatibilitas"""
        # rebuild automaton dengan keywords baru
        self.__init__(keywords)
        return self.search(text)

# testing function
def test_aho_corasick():
    """test aho-corasick implementation"""
    keywords = ["he", "she", "his", "hers"]
    text = "ushers"
    
    ac = AhoCorasick(keywords)
    results = ac.search(text)
    
    print("=== AHO-CORASICK TEST ===")
    print(f"Keywords: {keywords}")
    print(f"Text: '{text}'")
    print(f"Results: {results}")
    
    # expected: {'she': [2], 'he': [3], 'hers': [1]}
    expected = {'she': [2], 'he': [3], 'hers': [1]}
    
    if results == expected:
        print("✅ Test PASSED")
    else:
        print("❌ Test FAILED")
        print(f"Expected: {expected}")
    
    return results == expected

if __name__ == "__main__":
    test_aho_corasick()