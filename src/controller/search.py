import time
from src.algorithm.kmp import KMPMatcher
from src.algorithm.bm import BoyerMooreMatcher
from src.algorithm.aho_corasick import AhoCorasick
from src.algorithm.levenshtein import LevenshteinMatcher
from src.utils.timer import Timer

# temporary mock classes
class MockPDFExtractor:
    """mock pdf extractor dengan text realistis"""
    
    def __init__(self):
        # mock cv texts berdasarkan nama file
        self.mock_texts = {
            1: """Bryan P. Hutagalung
Software Engineer
Email: bryan.p.hutagalung@gmail.com
Phone: +6282211878972
Address: Jakarta, Indonesia
LinkedIn: linkedin.com/in/bryan-hutagalung

SUMMARY
Experienced software engineer with focus on backend development and machine learning.
Proficient in multiple programming languages and modern development frameworks.

SKILLS
Programming Languages: Python, Java, SQL, JavaScript
Frameworks: React, Django, Spring Boot
Technologies: Machine Learning, Docker, AWS, Git, PostgreSQL
Development: Backend Development, API Design, Database Management

WORK EXPERIENCE
Software Engineer at Tech Corp (2020-Present)
- Developed scalable backend services using Python and Java
- Implemented machine learning models for data analysis
- Collaborated with cross-functional teams on product development

Backend Developer at StartUp Inc (2018-2020)
- Built RESTful APIs using Django and PostgreSQL
- Optimized database queries and improved system performance
- Mentored junior developers on best practices

EDUCATION
Computer Science, Institut Teknologi Bandung (2018-2022)
Bachelor of Computer Science
GPA: 3.75/4.00""",

            2: """Danendra Shafi Athallah
Full Stack Developer
Email: danendra.shafi@gmail.com
Phone: +6281234567891
Address: Yogyakarta, Indonesia
LinkedIn: linkedin.com/in/danendra-athallah

SUMMARY
Full stack developer specializing in modern web applications and cloud deployment.
Expert in JavaScript ecosystem and modern frontend frameworks.

SKILLS
Frontend: JavaScript, React, HTML5, CSS3, TypeScript
Backend: Node.js, Express.js, MongoDB, PostgreSQL
DevOps: AWS, Docker, Git, Jenkins
Tools: Webpack, Babel, Jest, ESLint

WORK EXPERIENCE
Full Stack Developer at StartUp Inc (2021-Present)
- Developed responsive web applications using React and Node.js
- Implemented user authentication and authorization systems
- Deployed applications on AWS with Docker containers

Frontend Developer at Web Agency (2020-2021)
- Created interactive user interfaces with React and JavaScript
- Collaborated with designers on UI/UX implementation
- Optimized website performance and SEO""",

            3: """Raihaan Perdana
Data Scientist
Email: raihaan.perdana@gmail.com
Phone: +6281234567892
Address: Palembang, Indonesia
LinkedIn: linkedin.com/in/raihaan-perdana

SUMMARY
Data scientist with expertise in machine learning, deep learning, and big data processing.
Strong background in statistical analysis and algorithm development.

SKILLS
Programming: Python, C++, R, SQL
Machine Learning: TensorFlow, PyTorch, Scikit-learn, Keras
Data Processing: Pandas, NumPy, Apache Spark
Visualization: Matplotlib, Seaborn, Tableau
Infrastructure: Kubernetes, Docker, AWS, GCP

WORK EXPERIENCE
Data Scientist at AI Company (2022-Present)
- Developed machine learning models for predictive analytics
- Implemented deep learning solutions using TensorFlow and PyTorch
- Processed large datasets using Apache Spark and Python

Software Engineer at Tech Startup (2021-2022)
- Built data pipelines for ETL processes
- Developed algorithms for data analysis and pattern recognition
- Collaborated with product team on data-driven features""",

            4: """Alice Johnson
Backend Developer
Email: alice.johnson@email.com
Phone: +6281234567893
Address: Bandung, Indonesia
LinkedIn: linkedin.com/in/alice-johnson

SUMMARY
Backend developer experienced in building scalable web applications and APIs.
Specialized in Python web frameworks and database optimization.

SKILLS
Backend: Python, Django, Flask, FastAPI
Databases: PostgreSQL, MySQL, Redis, MongoDB
Infrastructure: Docker, Kubernetes, AWS, Linux
Testing: PyTest, Unit Testing, Integration Testing

WORK EXPERIENCE
Backend Developer at E-commerce Co (2020-Present)
- Built high-performance APIs using Django and PostgreSQL
- Implemented caching strategies with Redis
- Optimized database queries for large-scale applications""",

            5: """Bob Smith
Java Developer
Email: bob.smith@email.com
Phone: +6281234567894
Address: Surabaya, Indonesia
LinkedIn: linkedin.com/in/bob-smith

SUMMARY
Senior Java developer with expertise in enterprise applications and microservices.
Strong experience in Spring ecosystem and cloud-native development.

SKILLS
Programming: Java, Spring Boot, Spring Framework
Frontend: React, Angular, JavaScript, HTML, CSS
Databases: MySQL, PostgreSQL, Oracle, MongoDB
Tools: Maven, Gradle, Jenkins, Docker, Kubernetes

WORK EXPERIENCE
Senior Java Developer at Banking Corp (2021-Present)
- Developed microservices architecture using Spring Boot
- Implemented security features for financial applications
- Led team of 5 developers on enterprise projects

Java Developer at Fintech Startup (2019-2021)
- Built RESTful web services using Java and Spring
- Integrated payment gateways and financial APIs
- Participated in agile development processes""",
            6: """Catherine Lee Frontend Developer Vue.js Nuxt.js JavaScript TypeScript Node.js MongoDB Firebase GraphQL Tailwind CSS responsive design user experience""",
            7: """David Chen DevOps Engineer AWS Azure Terraform Jenkins Docker Kubernetes Linux Ansible monitoring cloud infrastructure automation CI/CD""",
            8: """Elena Rodriguez Mobile Developer React Native Flutter Dart Swift Kotlin Java Firebase SQLite iOS Android cross-platform mobile applications""",
            9: """Faisal Ahmad Senior PHP Developer Laravel CodeIgniter MySQL PostgreSQL Redis JavaScript jQuery Bootstrap REST API web applications""",
            10: """Grace Tan UI/UX Designer Figma Adobe XD Sketch Photoshop Illustrator prototyping user research wireframing visual design"""
        }
    
    def extract_text(self, pdf_path):
        """return realistic text berdasarkan path cv"""
        try:
            if 'Bryan' in pdf_path:
                return self.mock_texts.get(1, "")
            elif 'Danendra' in pdf_path:
                return self.mock_texts.get(2, "")
            elif 'Raihaan' in pdf_path:
                return self.mock_texts.get(3, "")
            elif 'Alice' in pdf_path:
                return self.mock_texts.get(4, "")
            elif 'Bob' in pdf_path:
                return self.mock_texts.get(5, "")
            elif 'Catherine' in pdf_path:
                return self.mock_texts.get(6, "")
            elif 'David' in pdf_path:
                return self.mock_texts.get(7, "")
            elif 'Elena' in pdf_path:
                return self.mock_texts.get(8, "")
            elif 'Faisal' in pdf_path:
                return self.mock_texts.get(9, "")
            elif 'Grace' in pdf_path:
                return self.mock_texts.get(10, "")
            else:
                return f"Generic CV text from {pdf_path}. Skills: Python Java SQL React JavaScript HTML CSS"
        
        except Exception as e:
            print(f"❌ Error extracting mock text: {e}")
            return ""

class SearchController:
    def __init__(self, repository):
        self.repository = repository
        self.kmp_matcher = KMPMatcher()
        self.bm_matcher = BoyerMooreMatcher()
        self.ac_matcher = AhoCorasick()
        self.levenshtein_matcher = LevenshteinMatcher()
        self.pdf_extractor = MockPDFExtractor()
        self.timer = Timer()
        
    def search(self, keywords, algorithm="KMP", top_n=10):
        """
        cari cv berdasarkan keywords dengan 4 algoritma berbeda
        
        Args:
            keywords: string keywords (bisa berisi threshold untuk levenshtein)
            algorithm: "KMP", "BM", "AC", "LD" 
            top_n: jumlah hasil teratas
            
        Returns:
            dict dengan results, timing, dan metadata
        """
        try:
            # parse keywords dan threshold untuk levenshtein
            threshold = 0.7  # default
            if "|threshold=" in keywords:
                keywords, threshold_part = keywords.split("|threshold=")
                threshold = float(threshold_part)
            
            # parse keywords
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
            if not keyword_list:
                return {
                    'results': [],
                    'algorithm_time': 0,
                    'fuzzy_match_time': 0,
                    'total_cvs_scanned': 0,
                    'algorithm_used': algorithm,
                    'error': 'Masukkan minimal 1 keyword'
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
                    'error': 'Tidak ada CV dalam database'
                }
            
            print(f"🔍 Scanning {len(all_cvs)} CVs dengan algoritma {algorithm}")
            
            # proses pencarian berdasarkan algoritma
            self.timer.start()
            
            if algorithm == "LD":
                # levenshtein distance - fuzzy search
                results = self._search_levenshtein(all_cvs, keyword_list, threshold)
            elif algorithm == "AC":
                # aho-corasick - multiple pattern search
                results = self._search_aho_corasick(all_cvs, keyword_list)
            elif algorithm == "BM":
                # boyer-moore - single pattern search
                results = self._search_boyer_moore(all_cvs, keyword_list)
            else:  # KMP (default)
                # knuth-morris-pratt - single pattern search
                results = self._search_kmp(all_cvs, keyword_list)
            
            algorithm_time = self.timer.stop()
            
            # sort berdasarkan total matches (descending)
            results.sort(key=lambda x: x['total_matches'], reverse=True)
            
            # ambil top N
            final_results = results[:top_n]
            
            print(f"📊 [{algorithm}] Total results: {len(results)}, showing top {len(final_results)}")
            
            return {
                'results': final_results,
                'algorithm_time': algorithm_time,
                'fuzzy_match_time': 0,  # legacy compatibility
                'total_cvs_scanned': len(all_cvs),
                'algorithm_used': algorithm,
                'threshold': threshold if algorithm == "LD" else None
            }
        
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {
                'results': [],
                'algorithm_time': 0,
                'fuzzy_match_time': 0,
                'total_cvs_scanned': 0,
                'algorithm_used': algorithm,
                'error': f'Error during search: {str(e)}'
            }
    
    def _search_kmp(self, all_cvs, keyword_list):
        """pencarian menggunakan knuth-morris-pratt"""
        results = []
        
        for cv in all_cvs:
            try:
                text = self.pdf_extractor.extract_text(cv['cv_path'])
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
                    print(f"✅ [KMP] Found {total_matches} matches in {cv['name']}: {keyword_matches}")
            
            except Exception as e:
                print(f"❌ Error processing CV {cv['cv_path']}: {e}")
                continue
        
        return results
    
    def _search_boyer_moore(self, all_cvs, keyword_list):
        """pencarian menggunakan boyer-moore"""
        results = []
        
        for cv in all_cvs:
            try:
                text = self.pdf_extractor.extract_text(cv['cv_path'])
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
                    print(f"✅ [BM] Found {total_matches} matches in {cv['name']}: {keyword_matches}")
            
            except Exception as e:
                print(f"❌ Error processing CV {cv['cv_path']}: {e}")
                continue
        
        return results
    
    def _search_aho_corasick(self, all_cvs, keyword_list):
        """pencarian menggunakan aho-corasick untuk multiple patterns"""
        results = []
        
        # build automaton untuk semua keywords sekaligus
        keywords_lower = [kw.lower() for kw in keyword_list]
        ac_automaton = AhoCorasick(keywords_lower)
        
        for cv in all_cvs:
            try:
                text = self.pdf_extractor.extract_text(cv['cv_path'])
                if not text:
                    continue
                
                text_lower = text.lower()
                
                # search semua patterns sekaligus
                matches = ac_automaton.search(text_lower)
                
                if matches:
                    keyword_matches = {}
                    total_matches = 0
                    
                    # map hasil ke keyword asli
                    for found_keyword, positions in matches.items():
                        # cari keyword asli dari keyword_list
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
                        print(f"✅ [AC] Found {total_matches} matches in {cv['name']}: {keyword_matches}")
            
            except Exception as e:
                print(f"❌ Error processing CV {cv['cv_path']}: {e}")
                continue
        
        return results
    
    def _search_levenshtein(self, all_cvs, keyword_list, threshold):
        """pencarian menggunakan levenshtein distance (fuzzy matching)"""
        results = []
        
        for cv in all_cvs:
            try:
                text = self.pdf_extractor.extract_text(cv['cv_path'])
                if not text:
                    continue
                
                keyword_matches = {}
                total_matches = 0
                
                for keyword in keyword_list:
                    # gunakan fuzzy search
                    matches = self.levenshtein_matcher.search(text, keyword, threshold)
                    
                    if matches:
                        # untuk fuzzy matching, tampilkan dengan format khusus
                        for match_key, positions in matches.items():
                            count = len(positions)
                            # tambahkan info similarity score
                            best_matches = self.levenshtein_matcher.find_best_matches(
                                keyword, text, threshold, max_results=3
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
                    print(f"✅ [LD] Found {total_matches} fuzzy matches in {cv['name']}: {keyword_matches}")
            
            except Exception as e:
                print(f"❌ Error processing CV {cv['cv_path']}: {e}")
                continue
        
        return results