# src/ui/results_panel.py
from PyQt5 import QtWidgets, QtCore, QtGui
from typing import List, Callable
from ..database.models import SearchResult

class ResultsPanel(QtWidgets.QWidget):
    """panel untuk menampilkan hasil pencarian"""
    
    # signals
    summary_requested = QtCore.pyqtSignal(str)  # resume_id
    view_cv_requested = QtCore.pyqtSignal(str)  # resume_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_results = []
        self.setup_ui()
    
    def setup_ui(self):
        """setup user interface"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # timing section
        self.timing_label = QtWidgets.QLabel("")
        self.timing_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 12px;
                color: #2c3e50;
            }
        """)
        self.timing_label.hide()  # hide initially
        layout.addWidget(self.timing_label)
        
        # results header
        self.results_header = QtWidgets.QLabel("Results")
        self.results_header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        self.results_header.hide()  # hide initially
        layout.addWidget(self.results_header)
        
        # scroll area for results
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # container widget for results
        self.results_widget = QtWidgets.QWidget()
        self.results_layout = QtWidgets.QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(10)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area.setWidget(self.results_widget)
        layout.addWidget(self.scroll_area)
        
        # initial message
        self.show_initial_message()
    
    def show_initial_message(self):
        """tampilkan pesan awal"""
        msg = QtWidgets.QLabel("Enter keywords and click Search to find matching CVs")
        msg.setAlignment(QtCore.Qt.AlignCenter)
        msg.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 16px;
                padding: 50px;
            }
        """)
        self.results_layout.addWidget(msg)
        self.results_layout.addStretch()
    
    def show_search_results(self, results: List[SearchResult], timing_info: str):
        """tampilkan hasil pencarian"""
        # clear previous results
        self.clear_results()
        
        # show timing info
        self.timing_label.setText(timing_info)
        self.timing_label.show()
        
        # show results header
        result_count = len(results)
        self.results_header.setText(f"Results ({result_count} CVs scanned)")
        self.results_header.show()
        
        if not results:
            self.show_no_results()
            return
        
        # store results
        self.search_results = results
        
        # create result cards
        for i, result in enumerate(results):
            card = self._create_result_card(result, i + 1)
            self.results_layout.addWidget(card)
        
        # add stretch at end
        self.results_layout.addStretch()
    
    def show_no_results(self):
        """tampilkan pesan tidak ada hasil"""
        msg = QtWidgets.QLabel("No matching CVs found")
        msg.setAlignment(QtCore.Qt.AlignCenter)
        msg.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 16px;
                padding: 30px;
            }
        """)
        self.results_layout.addWidget(msg)
        self.results_layout.addStretch()
    
    def clear_results(self):
        """bersihkan hasil sebelumnya"""
        # clear layout
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # hide timing and header
        self.timing_label.hide()
        self.results_header.hide()
    
    def _create_result_card(self, result: SearchResult, rank: int) -> QtWidgets.QWidget:
        """buat card untuk satu hasil pencarian"""
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px;
            }
            QFrame:hover {
                border-color: #3498db;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # header dengan nama dan rank
        header_layout = QtWidgets.QHBoxLayout()
        
        # nama candidate
        name = result.resume.name or result.resume.id
        name_label = QtWidgets.QLabel(f"{rank}. {name}")
        name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(name_label)
        
        # total matches
        matches_label = QtWidgets.QLabel(f"{result.total_matches} matches")
        matches_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #27ae60;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(matches_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # matched keywords
        keywords_text = self._format_matched_keywords(result.keyword_matches)
        keywords_label = QtWidgets.QLabel(keywords_text)
        keywords_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 10px;
            }
        """)
        keywords_label.setWordWrap(True)
        layout.addWidget(keywords_label)
        
        # buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        # summary button
        summary_btn = QtWidgets.QPushButton("Summary")
        summary_btn.setStyleSheet(self._get_button_style("#3498db"))
        summary_btn.clicked.connect(
            lambda: self.summary_requested.emit(result.resume.id)
        )
        buttons_layout.addWidget(summary_btn)
        
        # view cv button
        view_btn = QtWidgets.QPushButton("View CV")
        view_btn.setStyleSheet(self._get_button_style("#2ecc71"))
        view_btn.clicked.connect(
            lambda: self.view_cv_requested.emit(result.resume.id)
        )
        buttons_layout.addWidget(view_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return card
    
    def _format_matched_keywords(self, keyword_matches: dict) -> str:
        """format matched keywords untuk display"""
        if not keyword_matches:
            return "No keywords matched"
        
        formatted = []
        for keyword, count in keyword_matches.items():
            if count > 0:
                formatted.append(f"{keyword}: {count} occurrence{'s' if count > 1 else ''}")
        
        return "; ".join(formatted) if formatted else "No keywords matched"
    
    def _get_button_style(self, color: str) -> str:
        """ambil style untuk button"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """
    
    def show_loading(self, message: str = "Searching..."):
        """tampilkan loading state"""
        self.clear_results()
        
        loading_widget = QtWidgets.QWidget()
        loading_layout = QtWidgets.QVBoxLayout(loading_widget)
        loading_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # loading spinner (simple text for now)
        loading_label = QtWidgets.QLabel(message)
        loading_label.setAlignment(QtCore.Qt.AlignCenter)
        loading_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #3498db;
                padding: 50px;
            }
        """)
        
        loading_layout.addWidget(loading_label)
        self.results_layout.addWidget(loading_widget)
    
    def get_result_by_id(self, resume_id: str) -> SearchResult:
        """ambil search result berdasarkan resume id"""
        for result in self.search_results:
            if result.resume.id == resume_id:
                return result
        return None