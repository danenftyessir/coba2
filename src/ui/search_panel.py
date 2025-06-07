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

class SearchPanel(QtWidgets.QFrame):
    """panel pencarian cv dengan 4 algoritma lengkap"""
    
    # signals
    search_requested = pyqtSignal(str, str, int)  # keywords, algorithm, top_n
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("search_panel")
        self._init_ui()
        self._apply_styles()
    
    def _init_ui(self):
        """setup ui components dengan 4 algoritma"""
        # main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(0)
        
        # title
        title = QtWidgets.QLabel("Cari CV Kandidat")
        title.setObjectName("panel_title")
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addSpacing(18)
        
        # keyword input
        self.keyword_input = QtWidgets.QLineEdit()
        self.keyword_input.setObjectName("keyword_input")
        self.keyword_input.setPlaceholderText("Python, SQL, React, Machine Learning, ...")
        self.keyword_input.setMinimumHeight(36)
        layout.addWidget(self.keyword_input)
        
        # hint label
        hint = QtWidgets.QLabel("Pisahkan keyword dengan koma (,)")
        hint.setObjectName("hint_label")
        font = QtGui.QFont()
        font.setPointSize(9)
        hint.setFont(font)
        layout.addWidget(hint)
        layout.addSpacing(12)
        
        # algorithm selection - 4 ALGORITMA
        algo_label = QtWidgets.QLabel("Algoritma Pencarian:")
        algo_label.setObjectName("section_label")
        layout.addWidget(algo_label)
        layout.addSpacing(8)
        
        # container untuk 4 tombol algoritma - grid 2x2
        algo_container = QtWidgets.QWidget()
        algo_grid = QtWidgets.QGridLayout(algo_container)
        algo_grid.setSpacing(8)
        
        self.algo_group = QtWidgets.QButtonGroup(self)
        
        # BARIS 1: KMP dan Boyer-Moore
        self.kmp_btn = QtWidgets.QPushButton("Knuth-Morris-Pratt")
        self.kmp_btn.setObjectName("algo_button")
        self.kmp_btn.setCheckable(True)
        self.kmp_btn.setChecked(True)  # default
        self.kmp_btn.setMinimumHeight(35)
        self.kmp_btn.setToolTip("KMP - Optimal untuk single pattern matching")
        self.algo_group.addButton(self.kmp_btn)
        algo_grid.addWidget(self.kmp_btn, 0, 0)
        
        self.bm_btn = QtWidgets.QPushButton("Boyer-Moore")
        self.bm_btn.setObjectName("algo_button")
        self.bm_btn.setCheckable(True)
        self.bm_btn.setMinimumHeight(35)
        self.bm_btn.setToolTip("BM - Efisien untuk pattern panjang")
        self.algo_group.addButton(self.bm_btn)
        algo_grid.addWidget(self.bm_btn, 0, 1)
        
        # BARIS 2: Aho-Corasick dan Levenshtein
        self.ac_btn = QtWidgets.QPushButton("Aho-Corasick")
        self.ac_btn.setObjectName("algo_button")
        self.ac_btn.setCheckable(True)
        self.ac_btn.setMinimumHeight(35)
        self.ac_btn.setToolTip("AC - Optimal untuk multiple patterns")
        self.algo_group.addButton(self.ac_btn)
        algo_grid.addWidget(self.ac_btn, 1, 0)
        
        self.ld_btn = QtWidgets.QPushButton("Levenshtein Distance")
        self.ld_btn.setObjectName("algo_button")
        self.ld_btn.setCheckable(True)
        self.ld_btn.setMinimumHeight(35)
        self.ld_btn.setToolTip("LD - Fuzzy matching dengan toleransi typo")
        self.algo_group.addButton(self.ld_btn)
        algo_grid.addWidget(self.ld_btn, 1, 1)
        
        layout.addWidget(algo_container)
        layout.addSpacing(16)
        
        # similarity threshold khusus untuk levenshtein
        self.threshold_container = QtWidgets.QWidget()
        threshold_layout = QtWidgets.QHBoxLayout(self.threshold_container)
        threshold_layout.setContentsMargins(0, 0, 0, 0)
        
        threshold_label = QtWidgets.QLabel("Similarity Threshold:")
        threshold_label.setObjectName("section_label")
        threshold_layout.addWidget(threshold_label)
        
        self.threshold_spinbox = QtWidgets.QDoubleSpinBox()
        self.threshold_spinbox.setObjectName("threshold_spinbox")
        self.threshold_spinbox.setMinimum(0.1)
        self.threshold_spinbox.setMaximum(1.0)
        self.threshold_spinbox.setSingleStep(0.1)
        self.threshold_spinbox.setValue(0.7)
        self.threshold_spinbox.setMinimumHeight(32)
        self.threshold_spinbox.setMaximumWidth(80)
        self.threshold_spinbox.setDecimals(1)
        threshold_layout.addWidget(self.threshold_spinbox)
        threshold_layout.addStretch()
        
        layout.addWidget(self.threshold_container)
        self.threshold_container.hide()  # default hidden
        layout.addSpacing(12)
        
        # top n selector
        topn_label = QtWidgets.QLabel("Jumlah hasil teratas:")
        topn_label.setObjectName("section_label")
        layout.addWidget(topn_label)
        layout.addSpacing(6)
        
        topn_layout = QtWidgets.QHBoxLayout()
        self.topn_spinbox = QtWidgets.QSpinBox()
        self.topn_spinbox.setObjectName("topn_spinbox")
        self.topn_spinbox.setMinimum(1)
        self.topn_spinbox.setMaximum(50)
        self.topn_spinbox.setValue(10)
        self.topn_spinbox.setMinimumHeight(32)
        self.topn_spinbox.setMaximumWidth(70)
        topn_layout.addWidget(self.topn_spinbox)
        topn_layout.addStretch()
        layout.addLayout(topn_layout)
        layout.addSpacing(20)
        
        # search button
        self.search_btn = QtWidgets.QPushButton("🔍 Search CV")
        self.search_btn.setObjectName("search_button")
        self.search_btn.setMinimumHeight(40)
        if QT_FRAMEWORK == "PySide6":
            self.search_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        else:
            self.search_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.search_btn.clicked.connect(self._on_search_clicked)
        layout.addWidget(self.search_btn)
        layout.addSpacing(8)
        
        # error/info message
        self.message_label = QtWidgets.QLabel()
        self.message_label.setObjectName("message_label")
        self.message_label.setWordWrap(True)
        self.message_label.hide()
        layout.addWidget(self.message_label)
        
        # loading indicator
        self.loading_label = QtWidgets.QLabel("Sedang mencari...")
        self.loading_label.setObjectName("loading_label")
        if QT_FRAMEWORK == "PySide6":
            self.loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        else:
            self.loading_label.setAlignment(QtCore.Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)
        
        # spacer
        layout.addStretch()
        
        # connect algorithm change untuk show/hide threshold
        self.ld_btn.toggled.connect(self._on_algorithm_changed)
        self.kmp_btn.toggled.connect(self._on_algorithm_changed)
        self.bm_btn.toggled.connect(self._on_algorithm_changed)
        self.ac_btn.toggled.connect(self._on_algorithm_changed)
    
    def _apply_styles(self):
        """apply panel styles untuk 4 algoritma"""
        self.setStyleSheet("""
            #search_panel {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 14px;
            }
            
            #panel_title {
                color: #22223B;
            }
            
            #keyword_input {
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 10px;
                font-size: 11pt;
                color: #22223B;
            }
            
            #keyword_input:focus {
                border-color: #457DF6;
                outline: none;
            }
            
            #hint_label {
                color: #64748B;
                font-size: 9.5pt;
                margin-top: 4px;
            }
            
            #section_label {
                color: #22223B;
                font-weight: 500;
                font-size: 10.5pt;
            }
            
            #algo_button {
                background-color: #F2F4F8;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 9pt;
                color: #22223B;
                font-weight: 500;
                text-align: center;
            }
            
            #algo_button:checked {
                background-color: #457DF6;
                border-color: #3461C1;
                color: #FFFFFF;
                font-weight: bold;
            }
            
            #algo_button:hover {
                border-color: #CBD5E1;
            }
            
            #algo_button:checked:hover {
                background-color: #3461C1;
            }
            
            #topn_spinbox, #threshold_spinbox {
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 8px;
                font-size: 11pt;
                color: #22223B;
            }
            
            #topn_spinbox:focus, #threshold_spinbox:focus {
                border-color: #457DF6;
            }
            
            #search_button {
                background-color: #457DF6;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 12pt;
                font-weight: bold;
            }
            
            #search_button:hover {
                background-color: #3461C1;
            }
            
            #search_button:pressed {
                background-color: #2C4F9F;
            }
            
            #search_button:disabled {
                background-color: #94A3B8;
            }
            
            #message_label {
                font-size: 10pt;
                font-style: italic;
                margin-top: 7px;
            }
            
            #loading_label {
                color: #64748B;
                font-size: 10pt;
                font-style: italic;
                margin-top: 10px;
            }
        """)
        
        # tambahkan shadow
        try:
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(16)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QtGui.QColor(52, 97, 193, 18))
            self.setGraphicsEffect(shadow)
        except Exception as e:
            print(f"⚠️ Shadow effect tidak tersedia: {e}")
    
    def _on_algorithm_changed(self):
        """handle perubahan algoritma - show/hide threshold untuk levenshtein"""
        if self.ld_btn.isChecked():
            self.threshold_container.show()
            self.search_btn.setText("🔍 Fuzzy Search")
        else:
            self.threshold_container.hide() 
            self.search_btn.setText("🔍 Search CV")
    
    def _on_search_clicked(self):
        """handle search button click untuk 4 algoritma"""
        # ambil input values
        keywords = self.keyword_input.text().strip()
        
        # validasi
        if not keywords:
            self.show_error("Masukkan minimal 1 keyword")
            return
        
        # clear error message
        self.hide_message()
        
        # tentukan algorithm berdasarkan tombol yang dipilih
        algorithm = "KMP"  # default
        if self.kmp_btn.isChecked():
            algorithm = "KMP"
        elif self.bm_btn.isChecked():
            algorithm = "BM" 
        elif self.ac_btn.isChecked():
            algorithm = "AC"
        elif self.ld_btn.isChecked():
            algorithm = "LD"
        
        # ambil top n
        top_n = self.topn_spinbox.value()
        
        # untuk levenshtein, kirim threshold sebagai parameter tambahan
        if algorithm == "LD":
            threshold = self.threshold_spinbox.value()
            keywords_with_threshold = f"{keywords}|threshold={threshold}"
            self.search_requested.emit(keywords_with_threshold, algorithm, top_n)
        else:
            self.search_requested.emit(keywords, algorithm, top_n)
        
        print(f"🚀 Search triggered with algorithm: {algorithm}")
    
    def set_loading(self, loading):
        """set loading state untuk semua kontrol"""
        widgets_to_disable = [
            self.search_btn, self.keyword_input, self.kmp_btn, 
            self.bm_btn, self.ac_btn, self.ld_btn, 
            self.topn_spinbox, self.threshold_spinbox
        ]
        
        if loading:
            for widget in widgets_to_disable:
                widget.setEnabled(False)
            self.loading_label.show()
        else:
            for widget in widgets_to_disable:
                widget.setEnabled(True)
            self.loading_label.hide()
    
    def show_error(self, message):
        """tampilkan error message"""
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: #EF4444;")
        self.message_label.show()
    
    def show_info(self, message):
        """tampilkan info message"""
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: #64748B;")
        self.message_label.show()
    
    def hide_message(self):
        """sembunyikan message"""
        self.message_label.hide()
        
    def keyPressEvent(self, event):
        """handle keyboard shortcuts"""
        if QT_FRAMEWORK == "PySide6":
            if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
                if self.search_btn.isEnabled():
                    self._on_search_clicked()
        else:
            if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                if self.search_btn.isEnabled():
                    self._on_search_clicked()
        super().keyPressEvent(event)