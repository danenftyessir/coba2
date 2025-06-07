# src/ui/main_window_real.py - main window dengan real database integration
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
        raise ImportError("tidak ada framework Qt yang tersedia")

# import komponen ui
from .search_panel import SearchPanel
from .results_panel import ResultsPanel
from .summary_view import SummaryView

# import controllers - real version
try:
    from ..controller.real_search import RealSearchController
    from ..controller.cv import CVController
    from ..database.real_repository import RealRepository
    from ..database.config import DatabaseConfig
    from ..database.mock_repository import MockRepository
    from ..utils.timer import Timer
except ImportError:
    print("❌ error importing real modules - check file structure")
    raise

class DatabaseManager:
    """manager untuk handle koneksi database"""
    
    def __init__(self):
        self.connection = None
        self.config = None
        self.is_connected = False
    
    def connect(self, use_real_db=True):
        """connect ke database"""
        if use_real_db:
            try:
                self.config = DatabaseConfig()
                self.connection = self.config.get_connection()
                self.is_connected = True
                print("✅ koneksi real database berhasil")
                return True
            except Exception as e:
                print(f"❌ koneksi real database gagal: {e}")
                print("🔄 fallback ke mock repository")
                self.is_connected = False
                return False
        else:
            print("🔧 menggunakan mock repository")
            self.is_connected = False
            return False
    
    def get_repository(self):
        """ambil repository instance"""
        if self.is_connected and self.connection:
            return RealRepository(self.connection)
        else:
            return MockRepository()
    
    def close(self):
        """tutup koneksi database"""
        if self.connection and self.is_connected:
            self.connection.close()
            print("✅ koneksi database ditutup")

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
            print(f"❌ search worker error: {e}")
            traceback.print_exc()

class MainWindowReal(QtWidgets.QMainWindow):
    """main window aplikasi dengan real database integration"""
    
    def __init__(self, use_real_db=True):
        super().__init__()
        self.setWindowTitle("ATS CV Search - Production (Real Database)")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # database manager
        self.db_manager = DatabaseManager()
        self.use_real_db = use_real_db
        
        # algorithm mapping untuk display
        self.algorithm_names = {
            'KMP': 'Knuth-Morris-Pratt',
            'BM': 'Boyer-Moore',
            'AC': 'Aho-Corasick',
            'LD': 'Levenshtein Distance'
        }
        
        # init database connection
        self._init_database()
        
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
    
    def _init_database(self):
        """inisialisasi koneksi database"""
        try:
            success = self.db_manager.connect(self.use_real_db)
            if success:
                self.database_mode = "REAL DATABASE"
            else:
                self.database_mode = "MOCK DATA"
                self.use_real_db = False
            
            print(f"🔧 mode: {self.database_mode}")
            
        except Exception as e:
            print(f"❌ error init database: {e}")
            self.database_mode = "MOCK DATA"
            self.use_real_db = False
    
    def _init_controllers(self):
        """inisialisasi controllers"""
        try:
            # ambil repository berdasarkan database mode
            self.repository = self.db_manager.get_repository()
            
            # init controllers
            if self.use_real_db:
                from ..controller.real_search import RealSearchController
                self.search_controller = RealSearchController(self.repository)
            else:
                from ..controller.search import SearchController
                self.search_controller = SearchController(self.repository)
            
            self.cv_controller = CVController(self.repository)
            
            print(f"✅ controllers siap ({self.database_mode})")
            
        except Exception as e:
            print(f"❌ error init controllers: {e}")
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
        
        # search panel (left)
        self.search_panel = SearchPanel(self)
        splitter.addWidget(self.search_panel)
        
        # results panel (right)
        self.results_panel = ResultsPanel(self)
        splitter.addWidget(self.results_panel)
        
        # set initial sizes
        splitter.setSizes([490, 910])
        
        main_layout.addWidget(splitter, 1)
        
        # status bar dengan info database
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # status bar labels
        self.algorithm_label = QtWidgets.QLabel("algoritma: knuth-morris-pratt")
        self.algorithm_label.setStyleSheet("color: #457DF6; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.algorithm_label)
        
        self.separator1 = QtWidgets.QLabel(" | ")
        self.separator1.setStyleSheet("color: #64748B;")
        self.status_bar.addPermanentWidget(self.separator1)
        
        self.timing_label = QtWidgets.QLabel("")
        self.timing_label.setStyleSheet("color: #22C55E; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.timing_label)
        
        self.separator2 = QtWidgets.QLabel(" | ")
        self.separator2.setStyleSheet("color: #64748B;")
        self.status_bar.addPermanentWidget(self.separator2)
        
        self.db_mode_label = QtWidgets.QLabel(f"database: {self.database_mode}")
        self.db_mode_label.setStyleSheet("color: #7C3AED; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.db_mode_label)
        
        # tampilkan statistik database jika real
        if self.use_real_db:
            try:
                stats = self.repository.get_statistics()
                status_msg = f"siap mencari dari {stats['total_applicants']} kandidat dalam database"
                self.status_bar.showMessage(status_msg)
            except:
                self.status_bar.showMessage("database real terhubung, siap untuk pencarian")
        else:
            self.status_bar.showMessage("mode demo dengan mock data - 10 cv sample")
    
    def _create_header(self):
        """buat header aplikasi"""
        header = QtWidgets.QWidget()
        header.setObjectName("header")
        header.setFixedHeight(70)
        
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
        
        subtitle_text = f"production mode • {self.database_mode.lower()}"
        subtitle = QtWidgets.QLabel(subtitle_text)
        subtitle.setObjectName("app_subtitle")
        font = QtGui.QFont()
        font.setPointSize(10)
        subtitle.setFont(font)
        title_container.addWidget(subtitle)
        
        layout.addLayout(title_container)
        layout.addStretch()
        
        # database status indicator
        db_status = QtWidgets.QLabel("🔗 connected" if self.use_real_db else "🔧 demo mode")
        db_status.setObjectName("db_status")
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        db_status.setFont(font)
        layout.addWidget(db_status)
        
        return header
    
    def _setup_connections(self):
        """setup signal slot connections"""
        self.search_panel.search_requested.connect(self._on_search_requested)
        self.results_panel.summary_requested.connect(self._on_summary_requested)
        self.results_panel.view_cv_requested.connect(self._on_view_cv_requested)
    
    def _apply_styles(self):
        """apply global stylesheet"""
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
            
            #db_status {
                color: #7C3AED;
                background-color: #F3F0FF;
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid #D8B4FE;
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
        """handle search request"""
        algorithm_name = self.algorithm_names.get(algorithm, algorithm)
        print(f"🔍 mulai pencarian: '{keywords}' dengan {algorithm_name}")
        
        # update ui
        self.algorithm_label.setText(f"algoritma: {algorithm_name}")
        self.search_panel.set_loading(True)
        self.results_panel.clear_results()
        self.status_bar.showMessage(f"mencari dengan {algorithm_name}...")
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
        """handle search results"""
        # restore cursor
        QtWidgets.QApplication.restoreOverrideCursor()
        
        # update ui state
        self.search_panel.set_loading(False)
        
        # check for errors
        if 'error' in results:
            self.search_panel.show_error(results['error'])
            self.status_bar.showMessage("pencarian gagal")
            return
        
        algorithm_name = self.algorithm_names.get(results.get('algorithm_used', 'unknown'))
        result_count = len(results['results'])
        
        print(f"✅ [{algorithm_name}] pencarian selesai: {result_count} CV ditemukan")
        
        # display results
        self.results_panel.display_results(results['results'])
        
        # update status bar
        algorithm_time = Timer.format_time(results['algorithm_time'])
        total_cvs = results['total_cvs_scanned']
        
        if results.get('algorithm_used') == 'LD':
            threshold = results.get('threshold', 0.7)
            status_msg = f"fuzzy search: {total_cvs} CVs, threshold {threshold:.1f}"
        elif results.get('algorithm_used') == 'AC':
            status_msg = f"multi-pattern search: {total_cvs} CVs scanned"
        else:
            status_msg = f"pattern search: {total_cvs} CVs scanned"
        
        self.status_bar.showMessage(status_msg)
        self.timing_label.setText(f"⏱️ {algorithm_time}")
        
        # update results info
        if result_count > 0:
            self.search_panel.show_info(f"✅ {result_count} CV ditemukan")
        else:
            self.search_panel.show_info("ℹ️ tidak ada CV yang cocok")
    
    def _on_search_error(self, error_msg):
        """handle search error"""
        print(f"❌ search error: {error_msg}")
        
        QtWidgets.QApplication.restoreOverrideCursor()
        self.search_panel.set_loading(False)
        self.search_panel.show_error(f"error: {error_msg}")
        self.status_bar.showMessage("pencarian error")
        self.timing_label.setText("")
    
    def _on_summary_requested(self, applicant_id, cv_path):
        """handle request untuk summary cv"""
        try:
            print(f"📄 membuka summary untuk applicant {applicant_id}")
            
            applicant_data = self.cv_controller.get_applicant_data(applicant_id)
            
            if applicant_data:
                dialog = SummaryView(self, applicant_data, cv_path)
                if QT_FRAMEWORK == "PySide6":
                    dialog.exec()
                else:
                    dialog.exec_()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "error",
                    "data applicant tidak ditemukan"
                )
        
        except Exception as e:
            print(f"❌ error summary: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "error",
                f"gagal membuka summary: {str(e)}"
            )
    
    def _on_view_cv_requested(self, cv_path):
        """handle request untuk view cv file"""
        try:
            print(f"📁 membuka CV file: {cv_path}")
            
            # untuk real database, coba berbagai path
            possible_paths = [
                cv_path,
                f"../{cv_path}",
                f"./{cv_path}",
                os.path.abspath(cv_path),
            ]
            
            # jika menggunakan real database, tambahkan kaggle dataset path
            if self.use_real_db:
                kaggle_base = r"C:\Users\DANENDRA\.cache\kagglehub\datasets\snehaanbhawal\resume-dataset\versions\1"
                possible_paths.append(os.path.join(kaggle_base, cv_path))
            
            file_found = None
            for path in possible_paths:
                if os.path.exists(path):
                    file_found = path
                    break
            
            if file_found:
                success = self.cv_controller.open_cv_file(file_found)
                if not success:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "error",
                        f"gagal membuka file: {file_found}"
                    )
            else:
                # tampilkan info paths yang dicoba
                paths_info = '\n'.join([f"• {path}" for path in possible_paths])
                
                QtWidgets.QMessageBox.information(
                    self,
                    "file tidak ditemukan",
                    f"📄 CV: {cv_path}\n\n"
                    f"file dicari di:\n{paths_info}\n\n"
                    f"pastikan file ada di salah satu lokasi tersebut."
                )
        
        except Exception as e:
            print(f"❌ error view CV: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "error",
                f"error membuka CV: {str(e)}"
            )
    
    def closeEvent(self, event):
        """cleanup saat window ditutup"""
        try:
            print("🔄 cleanup aplikasi...")
            
            # wait for worker thread
            if self.search_worker.isRunning():
                self.search_worker.quit()
                self.search_worker.wait()
            
            # cleanup algorithms cache
            if hasattr(self.search_controller, 'levenshtein_matcher'):
                self.search_controller.levenshtein_matcher.clear_cache()
            
            # close database connection
            self.db_manager.close()
            
            print("✅ cleanup selesai")
        
        except Exception as e:
            print(f"❌ error during cleanup: {e}")
        
        event.accept()

# run_app.py - script untuk menjalankan aplikasi
import sys
import os

def main():
    """main function untuk run aplikasi"""
    print("🚀 ATS CV search - starting application")
    print("=" * 50)
    
    # tambahkan project root ke path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # import qt
    try:
        from PyQt5 import QtWidgets
        QT_FRAMEWORK = "PyQt5"
    except ImportError:
        try:
            from PySide6 import QtWidgets
            QT_FRAMEWORK = "PySide6"
        except ImportError:
            print("❌ tidak ada framework Qt yang tersedia")
            print("💡 install PyQt5 atau PySide6:")
            print("   pip install PyQt5")
            print("   # atau")
            print("   pip install PySide6")
            return
    
    print(f"✅ menggunakan {QT_FRAMEWORK}")
    
    # cek argument untuk mode
    use_real_db = True
    if len(sys.argv) > 1:
        if sys.argv[1] == "--mock":
            use_real_db = False
            print("🔧 mode: mock data (demo)")
        elif sys.argv[1] == "--real":
            use_real_db = True
            print("🔗 mode: real database")
    else:
        print("🔗 mode: real database (default)")
        print("💡 gunakan --mock untuk demo mode")
    
    # import dan run aplikasi
    try:
        from src.ui.main_window_real import MainWindowReal
        
        app = QtWidgets.QApplication(sys.argv)
        main_win = MainWindowReal(use_real_db=use_real_db)
        main_win.show()
        
        print("✅ aplikasi berhasil dimulai")
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"❌ error import: {e}")
        print("💡 pastikan struktur project benar dan dependencies terinstall")
    except Exception as e:
        print(f"❌ error menjalankan aplikasi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()