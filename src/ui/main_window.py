import sys
import traceback
import os
# deteksi qt framework
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtCore import QThread, Signal as pyqtSignal
    QT_FRAMEWORK = "PySide6"
except ImportError:
    try:
        from PyQt5 import QtWidgets, QtCore, QtGui
        from PyQt5.QtCore import QThread, pyqtSignal
        QT_FRAMEWORK = "PyQt5"
    except ImportError:
        raise ImportError("Tidak ada framework Qt yang tersedia")

# import komponen ui
from .search_panel import SearchPanel
from .results_panel import ResultsPanel  
from .summary_view import SummaryView

# import controllers
try:
    from ..controller.search import SearchController
    from ..controller.cv import CVController
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from controller.search import SearchController
    from controller.cv import CVController

# import database
try:
    from ..database.mock_repository import MockRepository
except ImportError:
    from database.mock_repository import MockRepository

# import utils
try:
    from ..utils.timer import Timer
except ImportError:
    from utils.timer import Timer

class SearchWorker(QThread):
    """worker thread untuk background search processing"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, search_controller):
        super().__init__()
        self.search_controller = search_controller
        self.keywords = ""
        self.algorithm = "KMP"
        self.top_n = 10
    
    def setup(self, keywords, algorithm, top_n):
        """setup parameter untuk search"""
        self.keywords = keywords
        self.algorithm = algorithm 
        self.top_n = top_n
    
    def run(self):
        """jalankan search di background thread"""
        try:
            results = self.search_controller.search(
                self.keywords, 
                self.algorithm, 
                self.top_n
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))
            print(f"search worker error: {e}")
            traceback.print_exc()

class MainWindow(QtWidgets.QMainWindow):
    """main window aplikasi ats cv search dengan 4 algoritma"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATS CV Search - Tim StimaSukses (4 Algoritma)")
        self.setGeometry(100, 100, 1400, 900)  # sedikit lebih besar untuk UI baru
        self.setMinimumSize(1000, 700)
        
        # algorithm mapping untuk display
        self.algorithm_names = {
            'KMP': 'Knuth-Morris-Pratt',
            'BM': 'Boyer-Moore', 
            'AC': 'Aho-Corasick',
            'LD': 'Levenshtein Distance'
        }
        
        # init controllers
        self._init_controllers()
        
        # init ui
        self._init_ui()
        
        # setup connections
        self._setup_connections()
        
        # apply styles
        self._apply_styles()
        
        # init worker thread
        self.search_worker = SearchWorker(self.search_controller)
        self.search_worker.finished.connect(self._on_search_finished)
        self.search_worker.error.connect(self._on_search_error)
    
    def _init_controllers(self):
        try:
            print("🔌 [MOCK MODE] Menggunakan MockRepository (tidak konek DB)")
            self.repository = MockRepository()
            self.search_controller = SearchController(self.repository)
            self.cv_controller = CVController(self.repository)
            print("✅ Controllers siap (mock mode) - 4 algoritma tersedia")
        except Exception as e:
            print(f"❌ Error init controllers: {e}")
            raise e
    
    def _init_ui(self):
        """setup ui components"""
        # central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # main layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # content area dengan splitter
        if QT_FRAMEWORK == "PySide6":
            splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        else:
            splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # search panel (left) - lebih lebar untuk 4 algoritma
        self.search_panel = SearchPanel(self)
        splitter.addWidget(self.search_panel)
        
        # results panel (right)
        self.results_panel = ResultsPanel(self)
        splitter.addWidget(self.results_panel)
        
        # set initial sizes (35% search, 65% results)
        splitter.setSizes([490, 910])
        
        main_layout.addWidget(splitter, 1)
        
        # status bar dengan info tambahan
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # status bar labels
        self.algorithm_label = QtWidgets.QLabel("Algoritma: Knuth-Morris-Pratt")
        self.algorithm_label.setStyleSheet("color: #457DF6; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.algorithm_label)
        
        self.separator = QtWidgets.QLabel(" | ")
        self.separator.setStyleSheet("color: #64748B;")
        self.status_bar.addPermanentWidget(self.separator)
        
        self.timing_label = QtWidgets.QLabel("")
        self.timing_label.setStyleSheet("color: #22C55E; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.timing_label)
        
        self.status_bar.showMessage("Siap untuk pencarian CV dengan 4 algoritma berbeda")
    
    def _create_header(self):
        """buat header aplikasi yang diperluas"""
        header = QtWidgets.QWidget()
        header.setObjectName("header")
        header.setFixedHeight(70)  # sedikit lebih tinggi
        
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(25, 0, 25, 0)
        
        # title dengan subtitle
        title_container = QtWidgets.QVBoxLayout()
        
        title = QtWidgets.QLabel("ATS CV Search")
        title.setObjectName("app_title")
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        title.setFont(font)
        title_container.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Powered by 4 Advanced String Matching Algorithms")
        subtitle.setObjectName("app_subtitle")
        font = QtGui.QFont()
        font.setPointSize(10)
        subtitle.setFont(font)
        title_container.addWidget(subtitle)
        
        layout.addLayout(title_container)
        layout.addStretch()
        
        # team info
        team_info = QtWidgets.QLabel(f"Tim StimaSukses • {QT_FRAMEWORK}")
        team_info.setObjectName("team_info")
        font = QtGui.QFont()
        font.setPointSize(10)
        team_info.setFont(font)
        layout.addWidget(team_info)
        
        return header
    
    def _setup_connections(self):
        """setup signal slot connections"""
        # search panel signals
        self.search_panel.search_requested.connect(self._on_search_requested)
        
        # results panel signals  
        self.results_panel.summary_requested.connect(self._on_summary_requested)
        self.results_panel.view_cv_requested.connect(self._on_view_cv_requested)
    
    def _apply_styles(self):
        """apply global stylesheet dengan update untuk 4 algoritma"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8FAFC;
            }
            
            #header {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
            }
            
            #app_title {
                color: #22223B;
            }
            
            #app_subtitle {
                color: #457DF6;
                font-style: italic;
                margin-top: 2px;
            }
            
            #team_info {
                color: #64748B;
                font-style: italic;
            }
            
            QStatusBar {
                background-color: #FFFFFF;
                border-top: 1px solid #E2E8F0;
                color: #64748B;
                font-size: 12px;
                padding: 6px 12px;
            }
            
            QSplitter::handle {
                background-color: #E2E8F0;
                width: 1px;
            }
            
            QSplitter::handle:hover {
                background-color: #CBD5E1;
            }
        """)
    
    def _on_search_requested(self, keywords, algorithm, top_n):
        """handle search request dari search panel"""
        algorithm_name = self.algorithm_names.get(algorithm, algorithm)
        print(f"🔍 Mulai pencarian: '{keywords}' dengan {algorithm_name}")
        
        # update algorithm label di status bar
        self.algorithm_label.setText(f"Algoritma: {algorithm_name}")
        
        # update ui state
        self.search_panel.set_loading(True)
        self.results_panel.clear_results()
        self.status_bar.showMessage(f"Mencari CV dengan {algorithm_name}...")
        self.timing_label.setText("")
        
        # set cursor loading
        if QT_FRAMEWORK == "PySide6":
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        else:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        # setup dan start worker thread
        self.search_worker.setup(keywords, algorithm, top_n)
        self.search_worker.start()
    
    def _on_search_finished(self, results):
        """handle search results dari worker thread"""
        # restore cursor
        QtWidgets.QApplication.restoreOverrideCursor()
        
        # update ui state
        self.search_panel.set_loading(False)
        
        # check for errors
        if 'error' in results:
            self.search_panel.show_error(results['error'])
            self.status_bar.showMessage("Pencarian gagal")
            return
        
        algorithm_name = self.algorithm_names.get(results.get('algorithm_used', 'Unknown'))
        result_count = len(results['results'])
        
        print(f"✅ [{algorithm_name}] Pencarian selesai: {result_count} CV ditemukan")
        
        # display results
        self.results_panel.display_results(results['results'])
        
        # update status bar dengan info lengkap
        algorithm_time = Timer.format_time(results['algorithm_time'])
        total_cvs = results['total_cvs_scanned']
        
        # status message berdasarkan algoritma
        if results.get('algorithm_used') == 'LD':
            threshold = results.get('threshold', 0.7)
            status_msg = f"Fuzzy Search: {total_cvs} CVs, threshold {threshold:.1f}"
        elif results.get('algorithm_used') == 'AC':
            status_msg = f"Multi-Pattern Search: {total_cvs} CVs scanned"
        else:
            status_msg = f"Pattern Search: {total_cvs} CVs scanned"
        
        self.status_bar.showMessage(status_msg)
        self.timing_label.setText(f"⏱️ {algorithm_time}")
        
        # update results count di header jika perlu
        if result_count > 0:
            self.search_panel.show_info(f"✅ {result_count} CV ditemukan")
        else:
            self.search_panel.show_info("ℹ️ Tidak ada CV yang cocok")
    
    def _on_search_error(self, error_msg):
        """handle search error dari worker thread"""
        print(f"❌ Search error: {error_msg}")
        
        # restore cursor
        QtWidgets.QApplication.restoreOverrideCursor()
        
        # update ui
        self.search_panel.set_loading(False)
        self.search_panel.show_error(f"Error: {error_msg}")
        self.status_bar.showMessage("Pencarian error")
        self.timing_label.setText("")
    
    def _on_summary_requested(self, applicant_id, cv_path):
        """handle request untuk menampilkan summary cv"""
        try:
            print(f"📄 Membuka summary untuk applicant {applicant_id}")
            
            # ambil data applicant dari controller
            applicant_data = self.cv_controller.get_applicant_data(applicant_id)
            
            if applicant_data:
                # tampilkan summary dialog
                dialog = SummaryView(self, applicant_data, cv_path)
                if QT_FRAMEWORK == "PySide6":
                    dialog.exec()
                else:
                    dialog.exec_()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "Data applicant tidak ditemukan"
                )
        
        except Exception as e:
            print(f"❌ Error summary: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error", 
                f"Gagal membuka summary: {str(e)}"
            )
    
    def _on_view_cv_requested(self, cv_path):
        """handle request untuk view cv file - FIXED path resolution"""
        try:
            print(f"📁 Membuka CV file: {cv_path}")
            
            # coba berbagai path possibilities
            possible_paths = [
                cv_path,                    # original: "data/CV_Bryan.pdf"
                f"../{cv_path}",           # dari src ke parent: "../data/CV_Bryan.pdf"  
                f"./{cv_path}",            # current dir: "./data/CV_Bryan.pdf"
                os.path.abspath(cv_path),   # absolute path
            ]
            
            # cari file yang ada
            file_found = None
            for path in possible_paths:
                if os.path.exists(path):
                    file_found = path
                    print(f"✅ Found CV at: {path}")
                    break
            
            if file_found:
                # file ditemukan, buka dengan sistem
                success = self.cv_controller.open_cv_file(file_found)
                if not success:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Error",
                        f"Gagal membuka file: {file_found}"
                    )
            else:
                # file tidak ditemukan, tampilkan info paths
                name = os.path.basename(cv_path).replace('CV_', '').replace('.pdf', '')
                paths_info = '\n'.join([f"• {path}" for path in possible_paths])
                
                QtWidgets.QMessageBox.information(
                    self,
                    "File Tidak Ditemukan",
                    f"📄 CV: {name}\n\n"
                    f"File dicari di:\n{paths_info}\n\n"
                    f"Pastikan file ada di salah satu lokasi tersebut."
                )
        except Exception as e:
            print(f"❌ Error view CV: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error membuka CV: {str(e)}"
            )
        
    def closeEvent(self, event):
        """cleanup saat window ditutup"""
        try:
            print("🔄 Cleanup aplikasi...")
            
            # wait for worker thread
            if self.search_worker.isRunning():
                self.search_worker.quit()
                self.search_worker.wait()
            
            # cleanup algorithms cache
            if hasattr(self.search_controller, 'levenshtein_matcher'):
                self.search_controller.levenshtein_matcher.clear_cache()
            
            # close database connection
            if hasattr(self, 'db_conn') and self.db_conn:
                self.db_conn.close()
            
            print("✅ Cleanup selesai")
        
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
        
        event.accept()