# install.bat - Windows batch script untuk install dependencies
@echo off
echo ========================================
echo ATS CV SEARCH - INSTALLATION SCRIPT
echo ========================================

echo.
echo 📦 Installing Python dependencies...
pip install mysql-connector-python>=8.0.0
pip install PyPDF2>=3.0.0
pip install PyQt5>=5.15.0
pip install sqlalchemy>=2.0.0

echo.
echo 🔧 Checking installations...
python -c "import mysql.connector; print('✅ mysql-connector-python')"
python -c "import PyPDF2; print('✅ PyPDF2')"
python -c "import PyQt5; print('✅ PyQt5')"

echo.
echo 📋 Installation completed!
echo.
echo 💡 Next steps:
echo    1. Setup MySQL database
echo    2. Update kaggle dataset path in setup_complete.py
echo    3. Run: python setup_complete.py
echo    4. Run: python run_app.py
echo.
pause

# install.sh - Linux/Mac shell script
#!/bin/bash
echo "========================================"
echo "ATS CV SEARCH - INSTALLATION SCRIPT"
echo "========================================"

echo ""
echo "📦 Installing Python dependencies..."
pip3 install mysql-connector-python>=8.0.0
pip3 install PyPDF2>=3.0.0
pip3 install PyQt5>=5.15.0
pip3 install sqlalchemy>=2.0.0

echo ""
echo "🔧 Checking installations..."
python3 -c "import mysql.connector; print('✅ mysql-connector-python')"
python3 -c "import PyPDF2; print('✅ PyPDF2')"
python3 -c "import PyQt5; print('✅ PyQt5')"

echo ""
echo "📋 Installation completed!"
echo ""
echo "💡 Next steps:"
echo "   1. Setup MySQL database"
echo "   2. Update kaggle dataset path in setup_complete.py"
echo "   3. Run: python3 setup_complete.py"
echo "   4. Run: python3 run_app.py"
echo ""

# quick_start.py - script cepat untuk memulai
import os
import sys
import subprocess

def quick_start():
    """quick start script untuk ats cv search"""
    
    print("🚀 ATS CV SEARCH - QUICK START")
    print("=" * 40)
    
    # cek python version
    print(f"🐍 Python version: {sys.version}")
    
    # cek operating system
    if os.name == 'nt':
        print("💻 OS: Windows")
        python_cmd = "python"
        pip_cmd = "pip"
    else:
        print("💻 OS: Unix/Linux/Mac")
        python_cmd = "python3"
        pip_cmd = "pip3"
    
    print("\n📋 PILIHAN SETUP:")
    print("1. Install dependencies + Setup database (FULL)")
    print("2. Install dependencies saja")
    print("3. Test aplikasi dengan mock data")
    print("4. Run aplikasi langsung")
    print("5. Setup database dari kaggle")
    
    choice = input("\nPilih opsi (1-5): ").strip()
    
    if choice == "1":
        # full setup
        print("\n🔧 FULL SETUP - Installing dependencies...")
        
        packages = [
            "mysql-connector-python>=8.0.0",
            "PyPDF2>=3.0.0", 
            "PyQt5>=5.15.0",
            "sqlalchemy>=2.0.0"
        ]
        
        for package in packages:
            print(f"📦 Installing {package}")
            result = subprocess.run([pip_cmd, "install", package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {package}")
            else:
                print(f"   ❌ {package} - {result.stderr}")
        
        print("\n🗄️ Setup database...")
        os.system(f"{python_cmd} setup_complete.py")
        
    elif choice == "2":
        # install dependencies only
        print("\n📦 Installing dependencies...")
        os.system("pip install -r requirements.txt")
        
    elif choice == "3":
        # test dengan mock data
        print("\n🧪 Testing dengan mock data...")
        os.system(f"{python_cmd} run_app.py --mock")
        
    elif choice == "4":
        # run aplikasi langsung
        print("\n🚀 Running aplikasi...")
        os.system(f"{python_cmd} run_app.py")
        
    elif choice == "5":
        # setup database saja
        print("\n🗄️ Setup database dari kaggle...")
        os.system(f"{python_cmd} database_loader.py")
        
    else:
        print("❌ Pilihan tidak valid")
        return
    
    print("\n✅ Quick start selesai!")

if __name__ == "__main__":
    quick_start()

# config_check.py - script untuk cek konfigurasi
import os
import sys
import mysql.connector
from pathlib import Path

def check_configuration():
    """cek konfigurasi sistem untuk ats cv search"""
    
    print("🔍 ATS CV SEARCH - CONFIGURATION CHECK")
    print("=" * 50)
    
    issues = []
    warnings = []
    
    # 1. python version
    print("\n📍 PYTHON ENVIRONMENT")
    python_version = sys.version_info
    print(f"   Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        issues.append("Python 3.8+ required")
    else:
        print("   ✅ Python version OK")
    
    # 2. required packages
    print("\n📍 PYTHON PACKAGES")
    required_packages = {
        'mysql.connector': 'mysql-connector-python',
        'PyPDF2': 'PyPDF2',
        'PyQt5': 'PyQt5 (or PySide6)',
        'sqlalchemy': 'sqlalchemy'
    }
    
    for module, package in required_packages.items():
        try:
            __import__(module.replace('.', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            issues.append(f"Missing package: {package}")
    
    # 3. file structure
    print("\n📍 FILE STRUCTURE")
    required_files = [
        'src/algorithm/kmp.py',
        'src/algorithm/bm.py', 
        'src/algorithm/aho_corasick.py',
        'src/algorithm/levenshtein.py',
        'src/ui/main_window.py',
        'src/controller/search.py',
        'src/database/config.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            issues.append(f"Missing file: {file_path}")
    
    # 4. database connection
    print("\n📍 DATABASE CONNECTION")
    db_configs = [
        {'host': 'localhost', 'user': 'root', 'password': ''},
        {'host': '127.0.0.1', 'user': 'root', 'password': ''},
    ]
    
    db_connected = False
    for config in db_configs:
        try:
            conn = mysql.connector.connect(**config, autocommit=True)
            conn.close()
            print(f"   ✅ MySQL connection OK ({config['host']})")
            db_connected = True
            break
        except Exception as e:
            print(f"   ⚠️ MySQL connection failed ({config['host']}): {e}")
    
    if not db_connected:
        warnings.append("MySQL connection issues - will use mock data")
    
    # 5. kaggle dataset
    print("\n📍 KAGGLE DATASET")
    possible_kaggle_paths = [
        r"C:\Users\DANENDRA\.cache\kagglehub\datasets\snehaanbhawal\resume-dataset\versions\1",
        "./data",
        "../data",
        "~/Downloads/resume-dataset"
    ]
    
    dataset_found = False
    for path in possible_kaggle_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            print(f"   ✅ Dataset found at: {expanded_path}")
            dataset_found = True
            break
        else:
            print(f"   🔍 Checked: {expanded_path}")
    
    if not dataset_found:
        warnings.append("Kaggle dataset not found - update path in database_loader.py")
    
    # 6. summary
    print("\n📊 SUMMARY")
    print("=" * 50)
    
    if not issues and not warnings:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ System ready to run ATS CV Search")
        print("\n💡 Run: python run_app.py")
        
    elif not issues:
        print("✅ CORE REQUIREMENTS OK")
        print("⚠️ Warnings (non-critical):")
        for warning in warnings:
            print(f"   • {warning}")
        print("\n💡 You can run with: python run_app.py --mock")
        
    else:
        print("❌ CRITICAL ISSUES FOUND:")
        for issue in issues:
            print(f"   • {issue}")
        
        if warnings:
            print("\n⚠️ Additional warnings:")
            for warning in warnings:
                print(f"   • {warning}")
        
        print("\n💡 Fix issues then run: python quick_start.py")
    
    return len(issues) == 0

if __name__ == "__main__":
    check_configuration()

# run_tests.py - script untuk testing
import unittest
import sys
import os

class TestATSComponents(unittest.TestCase):
    """test cases untuk komponen ats"""
    
    def setUp(self):
        """setup untuk testing"""
        # add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
    
    def test_algorithms_import(self):
        """test import semua algoritma"""
        try:
            from src.algorithm.kmp import KMPMatcher
            from src.algorithm.bm import BoyerMooreMatcher  
            from src.algorithm.aho_corasick import AhoCorasick
            from src.algorithm.levenshtein import LevenshteinMatcher
            self.assertTrue(True, "All algorithms imported successfully")
        except ImportError as e:
            self.fail(f"Algorithm import failed: {e}")
    
    def test_kmp_algorithm(self):
        """test kmp algorithm"""
        from src.algorithm.kmp import KMPMatcher
        
        matcher = KMPMatcher()
        text = "python programming language"
        pattern = "python"
        
        results = matcher.search(text, pattern)
        self.assertIn(pattern, results)
        self.assertEqual(len(results[pattern]), 1)
        self.assertEqual(results[pattern][0], 0)
    
    def test_boyer_moore_algorithm(self):
        """test boyer-moore algorithm"""
        from src.algorithm.bm import BoyerMooreMatcher
        
        matcher = BoyerMooreMatcher()
        text = "java programming with java"
        pattern = "java"
        
        results = matcher.search(text, pattern)
        self.assertIn(pattern, results)
        self.assertEqual(len(results[pattern]), 2)
    
    def test_aho_corasick_algorithm(self):
        """test aho-corasick algorithm"""
        from src.algorithm.aho_corasick import AhoCorasick
        
        keywords = ["python", "java", "sql"]
        text = "python and java with sql database"
        
        ac = AhoCorasick(keywords)
        results = ac.search(text)
        
        for keyword in keywords:
            self.assertIn(keyword, results)
    
    def test_levenshtein_algorithm(self):
        """test levenshtein distance"""
        from src.algorithm.levenshtein import LevenshteinMatcher
        
        matcher = LevenshteinMatcher()
        
        # test exact match
        distance = matcher.distance("python", "python")
        self.assertEqual(distance, 0)
        
        # test similarity
        similarity = matcher.similarity("python", "pyton")
        self.assertGreater(similarity, 0.7)
    
    def test_mock_repository(self):
        """test mock repository"""
        from src.database.mock_repository import MockRepository
        
        repo = MockRepository()
        cvs = repo.get_all_cvs()
        
        self.assertIsInstance(cvs, list)
        self.assertGreater(len(cvs), 0)
        
        # test get by id
        if cvs:
            first_cv = cvs[0]
            applicant = repo.get_applicant_by_id(first_cv['applicant_id'])
            self.assertIsNotNone(applicant)

def run_tests():
    """run all tests"""
    print("🧪 ATS CV SEARCH - RUNNING TESTS")
    print("=" * 40)
    
    # discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestATSComponents)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n📊 TEST SUMMARY")
    print("=" * 40)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)