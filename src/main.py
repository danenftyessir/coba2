# main.py - ATS CV Search Application Entry Point
import sys
import os
import argparse

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5 import QtWidgets, QtCore
from ui.main_window import MainWindow
from utils.test_mode import TestModeManager

def check_dependencies():
    """check critical dependencies before starting"""
    try:
        import psycopg2
        import PyPDF2
        from PyQt5 import QtWidgets
        print("all required dependencies found")
        return True
    except ImportError as e:
        print(f"missing dependency: {e}")
        print("please install: uv sync")
        return False

def check_data_directory():
    """check if data directory exists"""
    # Fix path to look in project root, not parent of project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(project_root, 'data')
    
    if os.path.exists(data_path):
        print(f"data directory found: {data_path}")
        
        # count pdf files
        pdf_count = 0
        for root, dirs, files in os.walk(data_path):
            pdf_count += len([f for f in files if f.endswith('.pdf')])
        
        print(f"found {pdf_count} pdf files in data directory")
        return True
    else:
        print(f"data directory not found: {data_path}")
        print("please create data directory and add CV files")
        return False

def main():
    """entry point aplikasi ats cv search dengan enhanced error handling"""
    parser = argparse.ArgumentParser(description='ATS CV Search Application')
    parser.add_argument('--test-mode', action='store_true', help='Enable test mode with limited data')
    parser.add_argument('--create-test-data', action='store_true', help='Create test dataset and exit')
    
    args = parser.parse_args()
    
    print("=== ATS CV SEARCH APPLICATION ===")
    print("starting application...")
    
    # handle test mode
    if args.create_test_data:
        test_manager = TestModeManager()
        test_manager.create_test_dataset(max_cvs_per_category=10)
        return
    
    if args.test_mode:
        test_manager = TestModeManager()
        test_manager.enable_test_mode()
    
    # check dependencies
    if not check_dependencies():
        print("dependency check failed")
        input("press enter to continue anyway...")
    
    # check data directory
    if not check_data_directory():
        print("data directory check failed")
        input("press enter to continue anyway...")
    
    try:
        # create qt application
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("ATS CV Search")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("Stima Tubes 3")
        
        print("qt application created")
        
        # test database connection before creating ui
        print("testing database connection...")
        from database.config_simple import DatabaseConfig
        db_config = DatabaseConfig()
        
        if db_config.test_connection():
            print("database connection successful")
        else:
            print("database connection failed")
            reply = input("continue without database? (y/n): ").lower()
            if reply != 'y':
                print("application cancelled")
                return
        
        # create and show main window
        print("creating main window...")
        window = MainWindow()
        window.show()
        
        print("main window ready")
        print("application started successfully!")
        
        if args.test_mode:
            print("⚠️ RUNNING IN TEST MODE - Limited dataset active")
        
        # run application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"error starting application: {e}")
        import traceback
        traceback.print_exc()
        
        # try to show error dialog if qt is available
        try:
            error_app = QtWidgets.QApplication.instance()
            if not error_app:
                error_app = QtWidgets.QApplication(sys.argv)
            
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Application Error")
            msg.setText(f"Failed to start ATS CV Search Application:\n\n{str(e)}")
            msg.setDetailedText(traceback.format_exc())
            msg.exec_()
        except:
            pass
        
        input("press enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()