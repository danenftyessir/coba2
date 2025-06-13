# src/ui/search_panel.py
from PyQt5 import QtWidgets, QtCore
from typing import Dict

class SearchPanel(QtWidgets.QWidget):
    """panel input untuk pencarian cv tanpa 4-param emit issue"""
    
    # signal dengan 3 parameter saja untuk menghindari overload issue
    search_requested = QtCore.pyqtSignal(dict)  # single dict parameter
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """setup user interface dengan design yang clean"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # title
        title = QtWidgets.QLabel("CV Analyzer App")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # keywords input section
        keywords_group = self._create_keywords_section()
        layout.addWidget(keywords_group)
        
        # algorithm selection section
        algorithm_group = self._create_algorithm_section()
        layout.addWidget(algorithm_group)
        
        # top matches section
        matches_group = self._create_matches_section()
        layout.addWidget(matches_group)
        
        # search button
        search_btn = self._create_search_button()
        layout.addWidget(search_btn)
        
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
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group)
        
        self.keywords_input = QtWidgets.QLineEdit()
        self.keywords_input.setPlaceholderText("React, Express, HTML, Python...")
        self.keywords_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(self.keywords_input)
        
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
        self.ac_radio = QtWidgets.QRadioButton("AC")
        
        # fuzzy matching algorithm
        self.levenshtein_radio = QtWidgets.QRadioButton("Levenshtein")
        
        # default selection
        self.kmp_radio.setChecked(True)
        
        # styling
        radio_style = """
            QRadioButton {
                font-size: 14px;
                spacing: 5px;
                margin: 2px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
        """
        
        for radio in [self.kmp_radio, self.bm_radio, self.ac_radio, self.levenshtein_radio]:
            radio.setStyleSheet(radio_style)
        
        exact_layout.addWidget(self.kmp_radio)
        exact_layout.addWidget(self.bm_radio)
        exact_layout.addWidget(self.ac_radio)
        exact_layout.addStretch()
        
        layout.addLayout(exact_layout)
        
        # fuzzy matching section
        fuzzy_label = QtWidgets.QLabel("Fuzzy Matching:")
        fuzzy_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-top: 10px;")
        layout.addWidget(fuzzy_label)
        
        fuzzy_layout = QtWidgets.QHBoxLayout()
        fuzzy_layout.addWidget(self.levenshtein_radio)
        fuzzy_layout.addStretch()
        
        layout.addLayout(fuzzy_layout)
        
        # similarity threshold for levenshtein
        threshold_layout = QtWidgets.QHBoxLayout()
        threshold_label = QtWidgets.QLabel("Similarity Threshold:")
        threshold_label.setStyleSheet("font-size: 11px; color: #7f8c8d; margin-left: 20px;")
        
        self.threshold_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.threshold_slider.setRange(30, 100)  # 0.3 to 1.0
        self.threshold_slider.setValue(70)       # default 0.7
        self.threshold_slider.setMaximumWidth(100)
        self.threshold_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 6px;
                background: #ecf0f1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)
        
        self.threshold_value_label = QtWidgets.QLabel("0.70")
        self.threshold_value_label.setStyleSheet("font-size: 11px; color: #2c3e50; font-weight: bold; min-width: 30px;")
        
        # connect slider to label update
        self.threshold_slider.valueChanged.connect(self._update_threshold_label)
        
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value_label)
        threshold_layout.addStretch()
        
        layout.addLayout(threshold_layout)
        
        # enable/disable threshold based on algorithm selection
        self.levenshtein_radio.toggled.connect(self._on_algorithm_changed)
        self.kmp_radio.toggled.connect(self._on_algorithm_changed)
        self.bm_radio.toggled.connect(self._on_algorithm_changed)
        self.ac_radio.toggled.connect(self._on_algorithm_changed)
        
        # set initial state
        self._on_algorithm_changed()
        
        # note about fuzzy matching
        note_label = QtWidgets.QLabel("Note: Fuzzy matching also runs automatically if exact matching finds no results")
        note_label.setStyleSheet("""
            font-size: 10px; 
            color: #95a5a6; 
            margin-top: 5px;
            font-style: italic;
        """)
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        return group
    
    def _update_threshold_label(self, value):
        """update threshold label when slider changes"""
        threshold = value / 100.0
        self.threshold_value_label.setText(f"{threshold:.2f}")
    
    def _on_algorithm_changed(self):
        """enable/disable threshold control based on algorithm"""
        is_levenshtein = self.levenshtein_radio.isChecked()
        self.threshold_slider.setEnabled(is_levenshtein)
        self.threshold_value_label.setEnabled(is_levenshtein)
        
        # update threshold label style
        if is_levenshtein:
            self.threshold_value_label.setStyleSheet("font-size: 11px; color: #2c3e50; font-weight: bold; min-width: 30px;")
        else:
            self.threshold_value_label.setStyleSheet("font-size: 11px; color: #bdc3c7; font-weight: bold; min-width: 30px;")
    
    def _create_matches_section(self) -> QtWidgets.QGroupBox:
        """create top matches selector"""
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
        
        layout = QtWidgets.QHBoxLayout(group)
        
        self.top_matches_spin = QtWidgets.QSpinBox()
        self.top_matches_spin.setRange(1, 50)
        self.top_matches_spin.setValue(10)
        self.top_matches_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 60px;
            }
        """)
        
        layout.addWidget(self.top_matches_spin)
        layout.addStretch()
        
        return group
    
    def _create_search_button(self) -> QtWidgets.QPushButton:
        """create search button"""
        btn = QtWidgets.QPushButton("Search")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
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
            }
        """)
        
        btn.clicked.connect(self._on_search_clicked)
        return btn
    
    def _on_search_clicked(self):
        """handle search button click - emit single dict parameter"""
        keywords_text = self.keywords_input.text().strip()
        if not keywords_text:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter keywords to search"
            )
            return
        
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        keywords = [kw for kw in keywords if kw]
        
        if not keywords:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter valid keywords"
            )
            return
        
        # get selected algorithm
        algorithm = 'KMP'  # default
        if self.bm_radio.isChecked():
            algorithm = 'BM'
        elif self.ac_radio.isChecked():
            algorithm = 'AC'
        elif self.levenshtein_radio.isChecked():
            algorithm = 'LEVENSHTEIN'
        
        # get threshold value
        threshold = self.threshold_slider.value() / 100.0
        
        top_n = self.top_matches_spin.value()
        
        # create search parameters dict - single parameter to avoid overload issues
        search_params = {
            'keywords': keywords,
            'algorithm': algorithm,
            'top_n': top_n,
            'threshold': threshold
        }
        
        print(f"🎯 emitting search signal with params: {search_params}")
        
        # emit single dict parameter
        self.search_requested.emit(search_params)
    
    def set_search_enabled(self, enabled: bool):
        """enable/disable search functionality"""
        self.keywords_input.setEnabled(enabled)
        self.kmp_radio.setEnabled(enabled)
        self.bm_radio.setEnabled(enabled)
        self.ac_radio.setEnabled(enabled)
        self.levenshtein_radio.setEnabled(enabled)
        self.threshold_slider.setEnabled(enabled and self.levenshtein_radio.isChecked())
        self.top_matches_spin.setEnabled(enabled)
        
        # find and update search button
        for child in self.findChildren(QtWidgets.QPushButton):
            if child.text() in ["Search", "Searching..."]:
                child.setEnabled(enabled)
                if enabled:
                    child.setText("Search")
                    child.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            font-size: 16px;
                            font-weight: bold;
                            border-radius: 6px;
                            min-height: 20px;
                        }
                        QPushButton:hover {
                            background-color: #2980b9;
                        }
                    """)
                else:
                    child.setText("Searching...")
                    child.setStyleSheet("""
                        QPushButton {
                            background-color: #bdc3c7;
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            font-size: 16px;
                            font-weight: bold;
                            border-radius: 6px;
                            min-height: 20px;
                        }
                    """)
                break