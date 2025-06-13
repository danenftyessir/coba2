# debug_connection.py
import mysql.connector
import time
import sys
import os

def test_basic_connection():
    """test basic mysql connection dengan timeout handling"""
    print("=== BASIC CONNECTION TEST ===")
    
    configs = [
        {
            'host': 'localhost',
            'user': 'root', 
            'password': 'danen332',
            'port': 3306,
            'connection_timeout': 5,
            'autocommit': True
        },
        {
            'host': '127.0.0.1',
            'user': 'root',
            'password': 'danen332', 
            'port': 3306,
            'connection_timeout': 5,
            'autocommit': True
        }
    ]
    
    for i, config in enumerate(configs):
        print(f"\ntest {i+1}: {config['host']}:{config['port']}")
        try:
            print("attempting connection...")
            start_time = time.time()
            
            conn = mysql.connector.connect(**config)
            
            elapsed = time.time() - start_time
            print(f"connection successful in {elapsed:.2f}s")
            
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                print(f"mysql version: {version}")
                
                cursor.execute("SHOW DATABASES")
                databases = [db[0] for db in cursor.fetchall()]
                print(f"databases: {databases}")
                
                if 'kaggle_resumes' in databases:
                    print("kaggle_resumes database found")
                    cursor.execute("USE kaggle_resumes")
                    cursor.execute("SHOW TABLES")
                    tables = [table[0] for table in cursor.fetchall()]
                    print(f"tables: {tables}")
                    
                    if 'resumes' in tables:
                        cursor.execute("SELECT COUNT(*) FROM resumes")
                        count = cursor.fetchone()[0]
                        print(f"resumes count: {count}")
                        
                        cursor.execute("SELECT id, category FROM resumes LIMIT 3")
                        samples = cursor.fetchall()
                        print(f"sample records: {samples}")
                
                cursor.close()
                conn.close()
                print("connection test passed")
                return True
                
        except mysql.connector.Error as e:
            print(f"mysql error: {e}")
        except Exception as e:
            print(f"connection error: {e}")
    
    return False

def test_application_config():
    """test application database config"""
    print("\n=== APPLICATION CONFIG TEST ===")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.database.config import DatabaseConfig
        from src.database.repo import ResumeRepository
        
        print("testing database config...")
        db_config = DatabaseConfig()
        
        if db_config.test_connection():
            print("database config test passed")
            
            print("testing repository...")
            repo = ResumeRepository()
            
            # test data directory
            repo.test_data_directory()
            
            # test loading resumes
            print("loading resumes...")
            resumes = repo.get_all_resumes()
            print(f"loaded {len(resumes)} resumes")
            
            if resumes:
                sample = resumes[0]
                print(f"sample resume: {sample.id} - {sample.category}")
                print(f"file path: {sample.file_path}")
                print(f"file exists: {os.path.exists(sample.file_path)}")
            
            return True
        else:
            print("database config test failed")
            return False
            
    except ImportError as e:
        print(f"import error: {e}")
        return False
    except Exception as e:
        print(f"application config error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_startup():
    """test gui startup without full application"""
    print("\n=== GUI STARTUP TEST ===")
    
    try:
        from PyQt5 import QtWidgets
        import sys
        
        app = QtWidgets.QApplication(sys.argv)
        print("qt application created successfully")
        
        # test simple dialog
        dialog = QtWidgets.QMessageBox()
        dialog.setWindowTitle("Test")
        dialog.setText("GUI test successful")
        dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        print("test dialog created")
        
        # don't show the dialog, just test creation
        app.quit()
        return True
        
    except Exception as e:
        print(f"gui test error: {e}")
        return False

def main():
    """run all debug tests"""
    print("ATS CV SEARCH - CONNECTION DEBUG")
    print("=" * 50)
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Application Config", test_application_config), 
        ("GUI Startup", test_gui_startup)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print(f"\n{'='*20} SUMMARY {'='*20}")
    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\nall tests passed! application should work.")
        print("try running: python main.py")
    else:
        print("\nsome tests failed. check the output above.")
        print("try running detect_mysql_port.py first")
    
    input("\npress enter to exit...")

if __name__ == "__main__":
    main()