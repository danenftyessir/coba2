# src/ui/main_window.py
from PyQt5 import QtWidgets, QtCore, QtGui
from .search_panel import SearchPanel
from .results_panel import ResultsPanel
from .summary_view import SummaryView
from ..controller.search import SearchController
from ..controller.cv import CVController
from ..database.config import DatabaseConfig

class MainWindow(QtWidgets.QMainWindow):
    """main window aplikasi cv search"""
    
    def __init__(self):
        super().__init__()
        
        # controllers
        self.search_controller = SearchController()
        self.cv_controller = CVController()
        
        # ui components
        self.search_panel = None
        self.results_panel = None
        self.summary_view = None
        
        # setup
        self.setup_ui()
        self.setup_connections()
        self.check_database_connection()
    
    def setup_ui(self):
        """setup user interface"""
        self.setWindowTitle("ATS CV Search Application")
        self.setGeometry(100, 100, 1200, 800)
        
        # set window icon (optional)
        self.setWindowIcon(QtGui.QIcon())
        
        # central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # main layout
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # left panel (search)
        self.search_panel = SearchPanel()
        self.search_panel.setFixedWidth(350)
        self.search_panel.setStyleSheet("""
            SearchPanel {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        main_layout.addWidget(self.search_panel)
        
        # right panel (results)
        self.results_panel = ResultsPanel()
        self.results_panel.setStyleSheet("""
            ResultsPanel {
                background-color: white;
            }
        """)
        main_layout.addWidget(self.results_panel)
        
        # summary view (dialog)
        self.summary_view = SummaryView(self)
        
        # status bar
        self.statusBar().showMessage("Ready - Enter keywords to search CVs")
        
        # style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                padding: 5px;
            }
        """)
    
    def setup_connections(self):
        """setup signal connections"""
        # search panel signals
        self.search_panel.search_requested.connect(self.perform_search)
        
        # results panel signals
        self.results_panel.summary_requested.connect(self.show_cv_summary)
        self.results_panel.view_cv_requested.connect(self.view_cv_file)
        
        # summary view signals
        self.summary_view.view_cv_requested.connect(self.view_cv_file)
    
    def check_database_connection(self):
        """cek koneksi database saat startup"""
        db_config = DatabaseConfig()
        if not db_config.test_connection():
            QtWidgets.QMessageBox.critical(
                self,
                "Database Error",
                "Cannot connect to database. Please check your MySQL connection."
            )
            self.statusBar().showMessage("Database connection failed")
        else:
            self.statusBar().showMessage("Database connected - Ready to search")
    
    @QtCore.pyqtSlot(list, str, int)
    def perform_search(self, keywords, algorithm, top_n):
        """handle search request"""
        try:
            # update ui state
            self.search_panel.set_search_enabled(False)
            self.results_panel.show_loading("Searching CVs...")
            self.statusBar().showMessage(f"Searching for: {', '.join(keywords)}")
            
            # process events to update ui
            QtWidgets.QApplication.processEvents()
            
            # perform search
            results, timing_info = self.search_controller.search_cvs(
                keywords=keywords,
                algorithm=algorithm,
                top_n=top_n,
                fuzzy_threshold=0.7
            )
            
            # show results
            self.results_panel.show_search_results(results, timing_info)
            
            # update status
            result_count = len(results)
            self.statusBar().showMessage(
                f"Found {result_count} matching CVs for: {', '.join(keywords)}"
            )
            
        except Exception as e:
            # handle errors
            QtWidgets.QMessageBox.critical(
                self,
                "Search Error", 
                f"An error occurred during search:\n{str(e)}"
            )
            self.statusBar().showMessage("Search failed")
            
        finally:
            # restore ui state
            self.search_panel.set_search_enabled(True)
    
    @QtCore.pyqtSlot(str)
    def show_cv_summary(self, resume_id):
        """tampilkan summary cv"""
        try:
            self.statusBar().showMessage("Loading CV summary...")
            
            # ambil summary cv
            cv_summary = self.cv_controller.get_cv_summary(resume_id)
            
            if cv_summary:
                self.summary_view.show_summary(resume_id, cv_summary)
                self.statusBar().showMessage("CV summary loaded")
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "Could not load CV summary. The file might be corrupted or missing."
                )
                self.statusBar().showMessage("Failed to load CV summary")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Summary Error",
                f"Error loading CV summary:\n{str(e)}"
            )
            self.statusBar().showMessage("Summary loading failed")
    
    @QtCore.pyqtSlot(str)
    def view_cv_file(self, resume_id):
        """buka file cv"""
        try:
            self.statusBar().showMessage("Opening CV file...")
            
            success = self.cv_controller.open_cv_file(resume_id)
            
            if success:
                self.statusBar().showMessage("CV file opened")
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "Could not open CV file. The file might be missing or corrupted."
                )
                self.statusBar().showMessage("Failed to open CV file")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "File Error",
                f"Error opening CV file:\n{str(e)}"
            )
            self.statusBar().showMessage("File opening failed")
    
    def closeEvent(self, event):
        """handle aplikasi closing"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()