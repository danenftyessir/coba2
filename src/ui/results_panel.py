# src/ui/results_panel.py
from PyQt5 import QtWidgets, QtCore
from typing import List
from database.models import SearchResult

class ResultsPanel(QtWidgets.QWidget):
    """panel untuk menampilkan hasil pencarian cv"""
    
    summary_requested = QtCore.pyqtSignal(str)  # resume_id
    view_cv_requested = QtCore.pyqtSignal(str)  # resume_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_results = []
        self.setup_ui()
    
    def setup_ui(self):
        """setup user interface dengan design yang responsive"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # timing info section
        self.timing_label = QtWidgets.QLabel("")
        self.timing_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 12px;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
            }
        """)
        self.timing_label.hide()
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
        self.results_header.hide()
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
        
        # show initial message
        self.show_initial_message()
    
    def show_initial_message(self):
        """show initial welcome message"""
        msg = QtWidgets.QLabel("Enter keywords and click Search to find matching CVs")
        msg.setAlignment(QtCore.Qt.AlignCenter)
        msg.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 16px;
                padding: 50px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 2px dashed #bdc3c7;
            }
        """)
        self.results_layout.addWidget(msg)
        self.results_layout.addStretch()
    
    def show_search_results(self, results: List[SearchResult], timing_info: str):
        """show search results dengan detailed info"""
        self.clear_results()
        
        # show timing info
        self.timing_label.setText(timing_info)
        self.timing_label.show()
        
        # show results header
        result_count = len(results)
        self.results_header.setText(f"Results ({result_count} CVs found)")
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
        
        self.results_layout.addStretch()
    
    def show_no_results(self):
        """show no results message"""
        msg = QtWidgets.QLabel("No matching CVs found.\nTry different keywords or use fuzzy matching.")
        msg.setAlignment(QtCore.Qt.AlignCenter)
        msg.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 16px;
                padding: 30px;
                background-color: #fdf2f2;
                border-radius: 8px;
                border: 2px solid #f5c6cb;
            }
        """)
        self.results_layout.addWidget(msg)
        self.results_layout.addStretch()
    
    def clear_results(self):
        """clear previous results"""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.timing_label.hide()
        self.results_header.hide()
    
    def _create_result_card(self, result: SearchResult, rank: int) -> QtWidgets.QWidget:
        """create result card untuk satu cv dengan detailed info"""
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 5px;
                margin: 2px;
            }
            QFrame:hover {
                border-color: #3498db;
                box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # header with name and rank
        header_layout = QtWidgets.QHBoxLayout()
        
        # candidate name
        name = result.resume.name or f"Candidate {result.resume.id}"
        name_label = QtWidgets.QLabel(f"#{rank}. {name}")
        name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(name_label)
        
        # category badge
        category_badge = QtWidgets.QLabel(result.resume.category)
        category_badge.setStyleSheet("""
            QLabel {
                background-color: #e9ecef;
                color: #495057;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(category_badge)
        
        # total matches
        matches_label = QtWidgets.QLabel(f"{result.total_matches} matches")
        matches_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #27ae60;
                font-weight: bold;
                background-color: #d4edda;
                padding: 4px 8px;
                border-radius: 12px;
            }
        """)
        header_layout.addWidget(matches_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # matched keywords with counts
        keywords_text = self._format_matched_keywords(result.keyword_matches)
        keywords_label = QtWidgets.QLabel(keywords_text)
        keywords_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                background-color: #f8f9fa;
                padding: 8px;
                border-radius: 4px;
                border-left: 3px solid #3498db;
            }
        """)
        keywords_label.setWordWrap(True)
        layout.addWidget(keywords_label)
        
        # contact info if available
        if result.resume.phone or result.resume.address:
            contact_parts = []
            if result.resume.phone:
                contact_parts.append(f"📞 {result.resume.phone}")
            if result.resume.address:
                contact_parts.append(f"📍 {result.resume.address[:50]}...")
            
            contact_label = QtWidgets.QLabel(" | ".join(contact_parts))
            contact_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #868e96;
                    padding: 4px 0;
                }
            """)
            layout.addWidget(contact_label)
        
        # action buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        # summary button
        summary_btn = QtWidgets.QPushButton("📋 Summary")
        summary_btn.setStyleSheet(self._get_button_style("#3498db"))
        summary_btn.clicked.connect(
            lambda: self.summary_requested.emit(result.resume.id)
        )
        buttons_layout.addWidget(summary_btn)
        
        # view cv button
        view_btn = QtWidgets.QPushButton("📄 View CV")
        view_btn.setStyleSheet(self._get_button_style("#2ecc71"))
        view_btn.clicked.connect(
            lambda: self.view_cv_requested.emit(result.resume.id)
        )
        buttons_layout.addWidget(view_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return card
    
    def _format_matched_keywords(self, keyword_matches: dict) -> str:
        """format matched keywords untuk display yang readable"""
        if not keyword_matches:
            return "❌ No keywords matched"
        
        formatted = []
        for keyword, count in keyword_matches.items():
            if count > 0:
                if "(fuzzy)" in keyword.lower():
                    formatted.append(f"🔍 {keyword}: {count}x")
                else:
                    formatted.append(f"✅ {keyword}: {count}x")
        
        return "  •  ".join(formatted) if formatted else "❌ No keywords matched"
    
    def _get_button_style(self, color: str) -> str:
        """get button style dengan hover effects"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                min-width: 90px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
                transform: translateY(0px);
            }}
        """
    
    def show_loading(self, message: str = "Searching..."):
        """show loading state dengan animation"""
        self.clear_results()
        
        loading_widget = QtWidgets.QWidget()
        loading_layout = QtWidgets.QVBoxLayout(loading_widget)
        loading_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        loading_label = QtWidgets.QLabel(f"🔍 {message}")
        loading_label.setAlignment(QtCore.Qt.AlignCenter)
        loading_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #3498db;
                padding: 50px;
                background-color: #f0f8ff;
                border-radius: 8px;
                border: 2px solid #3498db;
            }
        """)
        
        loading_layout.addWidget(loading_label)
        self.results_layout.addWidget(loading_widget)
    
    def get_result_by_id(self, resume_id: str) -> SearchResult:
        """get search result by resume id"""
        for result in self.search_results:
            if result.resume.id == resume_id:
                return result
        return None