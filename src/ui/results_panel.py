"""
results panel untuk menampilkan hasil pencarian cv
"""

# deteksi qt framework
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtCore import Signal as pyqtSignal
    QT_FRAMEWORK = "PySide6"
except ImportError:
    try:
        from PyQt5 import QtWidgets, QtCore, QtGui
        from PyQt5.QtCore import pyqtSignal
        QT_FRAMEWORK = "PyQt5"
    except ImportError:
        raise ImportError("Tidak ada framework Qt yang tersedia")

class CVResultCard(QtWidgets.QFrame):
    """card untuk menampilkan satu hasil cv"""
    
    summary_requested = pyqtSignal(int, str)  # applicant_id, cv_path
    view_cv_requested = pyqtSignal(str)  # cv_path
    
    def __init__(self, result_data, parent=None):
        super().__init__(parent)
        self.result_data = result_data
        self.setObjectName("cv_card")
        self._init_ui()
        self._apply_styles()
    
    def _init_ui(self):
        """setup ui card"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # header dengan nama dan match count
        header_layout = QtWidgets.QHBoxLayout()
        
        # nama kandidat
        name_label = QtWidgets.QLabel(self.result_data['name'])
        name_label.setObjectName("candidate_name")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        name_label.setFont(font)
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        # match count badge
        match_count = self.result_data['total_matches']
        match_badge = QtWidgets.QLabel(f"{match_count} matches")
        match_badge.setObjectName("match_badge")
        if QT_FRAMEWORK == "PySide6":
            match_badge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        else:
            match_badge.setAlignment(QtCore.Qt.AlignCenter)
        header_layout.addWidget(match_badge)
        
        layout.addLayout(header_layout)
        
        # keywords yang match
        if self.result_data['keyword_matches']:
            keywords_text = ", ".join([
                f"{keyword} ({count}x)" 
                for keyword, count in self.result_data['keyword_matches'].items()
            ])
            
            keywords_label = QtWidgets.QLabel(f"Keywords: {keywords_text}")
            keywords_label.setObjectName("keywords_label")
            keywords_label.setWordWrap(True)
            layout.addWidget(keywords_label)
        
        # buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        # summary button
        summary_btn = QtWidgets.QPushButton("📄 Summary")
        summary_btn.setObjectName("summary_button")
        if QT_FRAMEWORK == "PySide6":
            summary_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        else:
            summary_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        summary_btn.clicked.connect(self._on_summary_clicked)
        buttons_layout.addWidget(summary_btn)
        
        # view cv button
        view_btn = QtWidgets.QPushButton("👁️ View CV")
        view_btn.setObjectName("view_button")
        if QT_FRAMEWORK == "PySide6":
            view_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        else:
            view_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        view_btn.clicked.connect(self._on_view_clicked)
        buttons_layout.addWidget(view_btn)
        
        layout.addLayout(buttons_layout)
    
    def _apply_styles(self):
        """apply card styles"""
        self.setStyleSheet("""
            #cv_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                margin-bottom: 8px;
            }
            
            #cv_card:hover {
                border-color: #CBD5E1;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            #candidate_name {
                color: #22223B;
            }
            
            #match_badge {
                background-color: #457DF6;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11pt;
                font-weight: bold;
            }
            
            #keywords_label {
                color: #64748B;
                font-size: 10pt;
                margin: 4px 0;
            }
            
            #summary_button, #view_button {
                background-color: #F2F4F8;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: 500;
                color: #22223B;
            }
            
            #summary_button:hover {
                background-color: #457DF6;
                color: #FFFFFF;
                border-color: #3461C1;
            }
            
            #view_button:hover {
                background-color: #22C55E;
                color: #FFFFFF;
                border-color: #16A34A;
            }
        """)
    
    def _on_summary_clicked(self):
        """handle summary button click"""
        self.summary_requested.emit(
            self.result_data['applicant_id'],
            self.result_data['cv_path']
        )
    
    def _on_view_clicked(self):
        """handle view cv button click"""
        self.view_cv_requested.emit(self.result_data['cv_path'])

class ResultsPanel(QtWidgets.QFrame):
    """panel untuk menampilkan hasil pencarian"""
    
    summary_requested = pyqtSignal(int, str)  # applicant_id, cv_path
    view_cv_requested = pyqtSignal(str)  # cv_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("results_panel")
        self.result_cards = []  # track result cards
        self._init_ui()
        self._apply_styles()
    
    def _init_ui(self):
        """setup ui components"""
        # main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # title
        title = QtWidgets.QLabel("Hasil Pencarian")
        title.setObjectName("panel_title")
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addSpacing(16)
        
        # scroll area untuk results
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setObjectName("scroll_area")
        scroll_area.setWidgetResizable(True)
        if QT_FRAMEWORK == "PySide6":
            scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        
        # widget container untuk cards
        self.results_container = QtWidgets.QWidget()
        self.results_layout = QtWidgets.QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(8)
        
        # pesan default
        self.no_results_label = QtWidgets.QLabel("Belum ada pencarian.\nMasukkan keyword dan klik Search.")
        self.no_results_label.setObjectName("no_results")
        if QT_FRAMEWORK == "PySide6":
            self.no_results_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        else:
            self.no_results_label.setAlignment(QtCore.Qt.AlignCenter)
        self.no_results_label.setWordWrap(True)
        self.results_layout.addWidget(self.no_results_label)
        
        # spacer
        self.results_layout.addStretch()
        
        scroll_area.setWidget(self.results_container)
        layout.addWidget(scroll_area, 1)
    
    def _apply_styles(self):
        """apply panel styles"""
        self.setStyleSheet("""
            #results_panel {
                background-color: #F8FAFC;
                border: none;
            }
            
            #panel_title {
                color: #22223B;
                margin-bottom: 16px;
            }
            
            #scroll_area {
                border: none;
                background-color: transparent;
            }
            
            #no_results {
                color: #64748B;
                font-size: 14pt;
                font-style: italic;
                margin: 40px;
            }
        """)
    
    def display_results(self, results):
        """tampilkan hasil pencarian"""
        try:
            # clear existing results
            self.clear_results()
            
            if not results:
                self.no_results_label.setText("Tidak ada CV yang cocok dengan keyword.")
                self.no_results_label.show()
                return
            
            # hide no results message
            self.no_results_label.hide()
            
            # add result cards
            for result in results:
                card = CVResultCard(result, self)
                card.summary_requested.connect(self.summary_requested.emit)
                card.view_cv_requested.connect(self.view_cv_requested.emit)
                
                # insert before stretch
                self.results_layout.insertWidget(
                    self.results_layout.count() - 1, card
                )
                
                # track card
                self.result_cards.append(card)
            
            print(f"📋 Menampilkan {len(results)} hasil")
        
        except Exception as e:
            print(f"❌ Error display results: {e}")
            # fallback - tampilkan error message
            self.no_results_label.setText(f"Error menampilkan hasil: {str(e)}")
            self.no_results_label.show()
    
    def clear_results(self):
        """hapus semua hasil card tapi jangan hapus no_results_label"""
        # hapus semua result cards yang di-track
        for card in self.result_cards:
            if card is not None:
                self.results_layout.removeWidget(card)
                card.deleteLater()
        
        # clear list tracking
        self.result_cards.clear()
        
        # tampilkan no results message
        self.no_results_label.setText("Sedang mencari...")
        self.no_results_label.show()