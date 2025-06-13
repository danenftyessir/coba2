# src/ui/main_window.py
from PyQt5 import QtWidgets, QtCore
from .search_panel import SearchPanel
from .results_panel import ResultsPanel
from .summary_view import SummaryView
from ..controller.search import SearchController
from ..controller.cv import CVController
from ..database.config import DatabaseConfig

class MainWindow(QtWidgets.QMainWindow):
    """main window aplikasi cv search dengan optimized startup"""
    
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
        
        # check database in background to avoid blocking ui
        QtCore.QTimer.singleShot(500, self.check_database_connection)
    
    def setup_ui(self):
        """setup user interface dengan layout yang professional"""
        self.setWindowTitle("ATS CV Search Application - Stima Tubes 3")
        self.setGeometry(100, 100, 1400, 900)
        
        # set window icon (optional)
        self.setWindowIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # main layout - horizontal split
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # left panel (search controls)
        self.search_panel = SearchPanel()
        self.search_panel.setFixedWidth(380)
        self.search_panel.setStyleSheet("""
            SearchPanel {
                background-color: #f8f9fa;
                border-right: 2px solid #dee2e6;
            }
        """)
        main_layout.addWidget(self.search_panel)
        
        # right panel (results display)
        self.results_panel = ResultsPanel()
        self.results_panel.setStyleSheet("""
            ResultsPanel {
                background-color: #ffffff;
            }
        """)
        main_layout.addWidget(self.results_panel)
        
        # summary view dialog
        self.summary_view = SummaryView(self)
        
        # status bar
        self.statusBar().showMessage("initializing application...")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #e9ecef;
                border-top: 1px solid #dee2e6;
                padding: 8px;
                font-size: 12px;
                color: #495057;
            }
        """)
        
        # menu bar (optional)
        self.create_menu_bar()
        
        # window styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def create_menu_bar(self):
        """create simple menu bar"""
        menubar = self.menuBar()
        
        # file menu
        file_menu = menubar.addMenu('File')
        
        # exit action
        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # help menu
        help_menu = menubar.addMenu('Help')
        
        # about action
        about_action = QtWidgets.QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_connections(self):
        """setup signal connections tanpa threading complexity"""
        print("setting up signal connections...")
        
        # search panel signals - handle dict parameter to avoid overload
        self.search_panel.search_requested.connect(self.perform_search)
        print("search panel connected")
        
        # results panel signals
        self.results_panel.summary_requested.connect(self.show_cv_summary)
        self.results_panel.view_cv_requested.connect(self.view_cv_file)
        print("results panel connected")
        
        # summary view signals
        self.summary_view.view_cv_requested.connect(self.view_cv_file)
        print("summary view connected")
        
        print("all signal connections established")
    
    def check_database_connection(self):
        """check database connection dengan non-blocking approach"""
        print("checking database connection...")
        
        try:
            # quick connection test
            db_config = DatabaseConfig()
            conn = db_config.get_connection()
            
            if conn and conn.is_connected():
                # quick table check
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM resumes")
                count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                print(f"database connected successfully! found {count} resumes")
                self.statusBar().showMessage(f"ready - database connected ({count} resumes available)")
                
                # enable search functionality
                self.search_panel.setEnabled(True)
                
            else:
                print("database connection failed")
                self.statusBar().showMessage("warning - database connection failed")
                
                # show warning but allow app to continue
                QtCore.QTimer.singleShot(1000, self.show_database_warning)
                
        except Exception as e:
            print(f"database check error: {e}")
            self.statusBar().showMessage("error - database connection failed")
            QtCore.QTimer.singleShot(1000, self.show_database_error)
    
    def show_database_warning(self):
        """show database warning dialog"""
        QtWidgets.QMessageBox.warning(
            self,
            "Database Warning",
            "Cannot connect to database.\n\n"
            "Application will work in limited mode.\n"
            "Please check MySQL connection and try again."
        )
    
    def show_database_error(self):
        """show database error dialog"""
        QtWidgets.QMessageBox.critical(
            self,
            "Database Error", 
            "Database connection failed.\n\n"
            "Please check:\n"
            "• MySQL server is running\n"
            "• Database credentials are correct\n"
            "• Run setup_database.py if needed"
        )
    
    @QtCore.pyqtSlot(dict)
    def perform_search(self, search_params):
        """handle search request dengan direct execution (no threading)"""
        try:
            # extract parameters from dict
            keywords = search_params.get('keywords', [])
            algorithm = search_params.get('algorithm', 'KMP')
            top_n = search_params.get('top_n', 10)
            threshold = search_params.get('threshold', 0.7)
            
            print(f"starting search:")
            print(f"keywords: {keywords}")
            print(f"algorithm: {algorithm}")
            print(f"top_n: {top_n}")
            print(f"threshold: {threshold}")
            
            # validate keywords
            if not keywords:
                QtWidgets.QMessageBox.warning(
                    self, "Warning", "Please enter keywords to search"
                )
                return
            
            # update ui state
            self.search_panel.set_search_enabled(False)
            self.results_panel.show_loading("Searching CVs...")
            self.statusBar().showMessage(f"searching for: {', '.join(keywords)}")
            
            # process events to update ui immediately
            QtWidgets.QApplication.processEvents()
            
            # perform search directly (no threading to avoid complexity)
            results, timing_info = self.search_controller.search_cvs(
                keywords=keywords,
                algorithm=algorithm,
                top_n=top_n,
                fuzzy_threshold=threshold
            )
            
            print(f"search completed with {len(results)} results")
            
            # show results
            self.results_panel.show_search_results(results, timing_info)
            
            # update status
            result_count = len(results)
            if result_count > 0:
                self.statusBar().showMessage(
                    f"found {result_count} matching cvs for: {', '.join(keywords)}"
                )
            else:
                self.statusBar().showMessage(
                    f"no cvs found for: {', '.join(keywords)} (try different keywords)"
                )
            
        except Exception as e:
            print(f"search error: {e}")
            import traceback
            traceback.print_exc()
            
            # show error dialog
            QtWidgets.QMessageBox.critical(
                self,
                "Search Error", 
                f"An error occurred during search:\n\n{str(e)}\n\n"
                f"Please check:\n"
                f"• Database connection\n"
                f"• CV files exist in data folder\n"
                f"• Keywords are valid"
            )
            self.statusBar().showMessage("search failed")
            
        finally:
            # restore ui state
            self.search_panel.set_search_enabled(True)
    
    @QtCore.pyqtSlot(str)
    def show_cv_summary(self, resume_id):
        """show cv summary dengan comprehensive regex extraction"""
        try:
            print(f"loading cv summary for resume {resume_id}")
            self.statusBar().showMessage(f"loading cv summary for {resume_id}...")
            
            # get cv summary
            cv_summary = self.cv_controller.get_cv_summary(resume_id)
            
            if cv_summary:
                print(f"summary loaded with {len(cv_summary.skills)} skills, {len(cv_summary.job_history)} jobs, {len(cv_summary.education)} education")
                self.summary_view.show_summary(resume_id, cv_summary)
                self.statusBar().showMessage("cv summary loaded successfully")
            else:
                print(f"failed to load summary for {resume_id}")
                QtWidgets.QMessageBox.warning(
                    self,
                    "Summary Error",
                    f"Could not load CV summary for {resume_id}.\n\n"
                    f"The file might be:\n"
                    f"• Corrupted or missing\n"
                    f"• Not a valid PDF\n"
                    f"• Too large to process"
                )
                self.statusBar().showMessage("failed to load cv summary")
                
        except Exception as e:
            print(f"summary error: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Summary Error",
                f"Error loading CV summary:\n\n{str(e)}"
            )
            self.statusBar().showMessage("summary loading failed")
    
    @QtCore.pyqtSlot(str)
    def view_cv_file(self, resume_id):
        """open cv file dengan default application"""
        try:
            print(f"opening cv file for resume {resume_id}")
            self.statusBar().showMessage(f"opening cv file for {resume_id}...")
            
            success = self.cv_controller.open_cv_file(resume_id)
            
            if success:
                print(f"cv file opened for {resume_id}")
                self.statusBar().showMessage("cv file opened successfully")
            else:
                print(f"failed to open cv file for {resume_id}")
                QtWidgets.QMessageBox.warning(
                    self,
                    "File Error",
                    f"Could not open CV file for {resume_id}.\n\n"
                    f"The file might be:\n"
                    f"• Missing from data folder\n"
                    f"• Corrupted\n"
                    f"• No default PDF application set"
                )
                self.statusBar().showMessage("failed to open cv file")
                
        except Exception as e:
            print(f"file open error: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "File Error",
                f"Error opening CV file:\n\n{str(e)}"
            )
            self.statusBar().showMessage("file opening failed")
    
    def show_about(self):
        """show about dialog"""
        QtWidgets.QMessageBox.about(
            self,
            "About ATS CV Search",
            "<h3>ATS CV Search Application</h3>"
            "<p><b>Tugas Besar 3 - IF2211 Strategi Algoritma</b></p>"
            "<p>Semester II tahun 2024/2025</p>"
            "<hr>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Pattern Matching (KMP, Boyer-Moore, Aho-Corasick)</li>"
            "<li>Fuzzy Matching (Levenshtein Distance)</li>"
            "<li>Regex-based Information Extraction</li>"
            "<li>MySQL Database Integration</li>"
            "</ul>"
            "<hr>"
            "<p><b>Built with:</b> Python, PyQt5, MySQL</p>"
            "<p><b>Institut Teknologi Bandung</b></p>"
        )
    
    def closeEvent(self, event):
        """handle application closing"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit ATS CV Search?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            print("application closing...")
            event.accept()
        else:
            event.ignore()