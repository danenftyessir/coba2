# src/ui/search_panel.py
from PyQt5 import QtWidgets, QtCore

class SearchPanel(QtWidgets.QWidget):
    """panel input untuk pencarian cv tanpa 4-param emit issue"""
    
    search_requested = QtCore.pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """setup ui components dengan styling professional"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # title
        title_label = QtWidgets.QLabel("🔍 ATS CV Search")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # keywords input section
        keywords_group = self._create_keywords_section()
        layout.addWidget(keywords_group)
        
        # algorithm selection section
        algorithm_group = self._create_algorithm_section()
        layout.addWidget(algorithm_group)
        
        # top matches section
        matches_group = self._create_matches_section()
        layout.addWidget(matches_group)
        
        # threshold section
        threshold_group = self._create_threshold_section()
        layout.addWidget(threshold_group)
        
        # search button
        search_button = self._create_search_button()
        layout.addWidget(search_button)
        
        # add stretch to push everything to top
        layout.addStretch()
    
    def _create_keywords_section(self) -> QtWidgets.QGroupBox:
        """create keywords input section"""
        group = QtWidgets.QGroupBox("Keywords:")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group)
        
        self.keywords_input = QtWidgets.QLineEdit()
        self.keywords_input.setPlaceholderText("Enter keywords separated by commas (e.g., Python, React, SQL)")
        self.keywords_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(self.keywords_input)
        
        # example label
        example_label = QtWidgets.QLabel("💡 Examples: JavaScript, Machine Learning, Project Management")
        example_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                margin-top: 5px;
                font-weight: normal;
            }
        """)
        layout.addWidget(example_label)
        
        return group
    
    def _create_algorithm_section(self) -> QtWidgets.QGroupBox:
        """create algorithm selection section"""
        group = QtWidgets.QGroupBox("Search Algorithm:")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group)
        
        # exact matching algorithms
        exact_label = QtWidgets.QLabel("Exact Matching:")
        exact_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-top: 5px;")
        layout.addWidget(exact_label)
        
        exact_layout = QtWidgets.QHBoxLayout()
        
        self.kmp_radio = QtWidgets.QRadioButton("KMP")
        self.bm_radio = QtWidgets.QRadioButton("BM")
        self.ac_radio = QtWidgets.QRadioButton("AC")  # Aho-Corasick
        
        # set KMP as default
        self.kmp_radio.setChecked(True)
        
        exact_layout.addWidget(self.kmp_radio)
        exact_layout.addWidget(self.bm_radio)
        exact_layout.addWidget(self.ac_radio)
        layout.addLayout(exact_layout)
        
        # fuzzy matching algorithm
        fuzzy_label = QtWidgets.QLabel("Fuzzy Matching:")
        fuzzy_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-top: 10px;")
        layout.addWidget(fuzzy_label)
        
        self.levenshtein_radio = QtWidgets.QRadioButton("Levenshtein Distance")
        layout.addWidget(self.levenshtein_radio)
        
        # algorithm descriptions
        desc_label = QtWidgets.QLabel(
            "• KMP: Fast single pattern matching\n"
            "• BM: Efficient for longer patterns\n"
            "• AC: Multiple pattern matching (bonus)\n"
            "• Levenshtein: Handles typos and variations"
        )
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #95a5a6;
                margin-top: 8px;
                font-weight: normal;
                background-color: #f8f9fa;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(desc_label)
        
        return group
    
    def _create_matches_section(self) -> QtWidgets.QGroupBox:
        """create top matches selection section"""
        group = QtWidgets.QGroupBox("Top Matches:")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group)
        
        self.matches_spin = QtWidgets.QSpinBox()
        self.matches_spin.setRange(1, 50)
        self.matches_spin.setValue(10)
        self.matches_spin.setSuffix(" CVs")
        self.matches_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px 12px;
                font-size: 14px;
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(self.matches_spin)
        
        return group
    
    def _create_threshold_section(self) -> QtWidgets.QGroupBox:
        """create fuzzy matching threshold section"""
        group = QtWidgets.QGroupBox("Fuzzy Threshold:")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group)
        
        # threshold slider
        self.threshold_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.threshold_slider.setRange(50, 100)  # 0.5 to 1.0
        self.threshold_slider.setValue(70)  # 0.7 default
        self.threshold_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(10)
        layout.addWidget(self.threshold_slider)
        
        # threshold label
        self.threshold_label = QtWidgets.QLabel("0.70 (70% similarity)")
        self.threshold_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                text-align: center;
                font-weight: normal;
            }
        """)
        self.threshold_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.threshold_label)
        
        return group
    
    def _create_search_button(self) -> QtWidgets.QPushButton:
        """create search button"""
        search_btn = QtWidgets.QPushButton("🔍 Search CVs")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        self.search_button = search_btn
        return search_btn
    
    def setup_connections(self):
        """setup signal connections"""
        self.search_button.clicked.connect(self.on_search_clicked)
        self.keywords_input.returnPressed.connect(self.on_search_clicked)
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
    
    def update_threshold_label(self, value):
        """update threshold label based on slider value"""
        threshold = value / 100.0
        self.threshold_label.setText(f"{threshold:.2f} ({value}% similarity)")
    
    def on_search_clicked(self):
        """handle search button click"""
        keywords_text = self.keywords_input.text().strip()
        
        if not keywords_text:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter keywords to search"
            )
            return
        
        # parse keywords
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        keywords = [kw for kw in keywords if kw]  # remove empty
        
        if not keywords:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter valid keywords"
            )
            return
        
        # determine algorithm
        algorithm = "KMP"  # default
        if self.bm_radio.isChecked():
            algorithm = "BM"
        elif self.ac_radio.isChecked():
            algorithm = "AC"
        elif self.levenshtein_radio.isChecked():
            algorithm = "LEVENSHTEIN"
        
        # get other parameters
        top_n = self.matches_spin.value()
        threshold = self.threshold_slider.value() / 100.0
        
        # create search parameters dict
        search_params = {
            'keywords': keywords,
            'algorithm': algorithm,
            'top_n': top_n,
            'threshold': threshold
        }
        
        print(f"🎯 emitting search signal with params: {search_params}")
        self.search_requested.emit(search_params)
    
    def set_search_enabled(self, enabled: bool):
        """enable/disable search functionality"""
        self.search_button.setEnabled(enabled)
        self.keywords_input.setEnabled(enabled)
        
        if enabled:
            self.search_button.setText("🔍 Search CVs")
        else:
            self.search_button.setText("⏳ Searching...")