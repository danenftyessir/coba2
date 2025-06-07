# src/ui/search_panel.py
from PyQt5 import QtWidgets, QtCore, QtGui
from typing import List, Callable

class SearchPanel(QtWidgets.QWidget):
    """panel input untuk pencarian cv"""
    
    # signal untuk komunikasi dengan main window
    search_requested = QtCore.pyqtSignal(list, str, int)  # keywords, algorithm, top_n
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """setup user interface"""
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
        
        # keywords input
        keywords_group = self._create_keywords_section()
        layout.addWidget(keywords_group)
        
        # algorithm selection
        algorithm_group = self._create_algorithm_section()
        layout.addWidget(algorithm_group)
        
        # top matches selector
        matches_group = self._create_matches_section()
        layout.addWidget(matches_group)
        
        # search button
        search_btn = self._create_search_button()
        layout.addWidget(search_btn)
        
        # spacing
        layout.addStretch()
    
    def _create_keywords_section(self) -> QtWidgets.QGroupBox:
        """buat section input keywords"""
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
        
        # input field
        self.keywords_input = QtWidgets.QLineEdit()
        self.keywords_input.setPlaceholderText("React, Express, HTML...")
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
        """buat section pemilihan algoritma"""
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
        
        layout = QtWidgets.QHBoxLayout(group)
        
        # radio buttons
        self.kmp_radio = QtWidgets.QRadioButton("KMP")
        self.bm_radio = QtWidgets.QRadioButton("BM")
        self.ac_radio = QtWidgets.QRadioButton("AC")
        
        # default selection
        self.kmp_radio.setChecked(True)
        
        # styling
        radio_style = """
            QRadioButton {
                font-size: 14px;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
        """
        self.kmp_radio.setStyleSheet(radio_style)
        self.bm_radio.setStyleSheet(radio_style)
        self.ac_radio.setStyleSheet(radio_style)
        
        layout.addWidget(self.kmp_radio)
        layout.addWidget(self.bm_radio)
        layout.addWidget(self.ac_radio)
        layout.addStretch()
        
        return group
    
    def _create_matches_section(self) -> QtWidgets.QGroupBox:
        """buat section top matches selector"""
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
        
        # spinner
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
        """buat search button"""
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
        """handle search button click"""
        # ambil keywords
        keywords_text = self.keywords_input.text().strip()
        if not keywords_text:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter keywords to search"
            )
            return
        
        # parse keywords
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        keywords = [kw for kw in keywords if kw]
        
        if not keywords:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter valid keywords"
            )
            return
        
        # ambil algorithm
        algorithm = 'KMP'
        if self.bm_radio.isChecked():
            algorithm = 'BM'
        elif self.ac_radio.isChecked():
            algorithm = 'AC'
        
        # ambil top matches
        top_n = self.top_matches_spin.value()
        
        # emit signal
        self.search_requested.emit(keywords, algorithm, top_n)
    
    def set_search_enabled(self, enabled: bool):
        """enable/disable search functionality"""
        self.keywords_input.setEnabled(enabled)
        self.kmp_radio.setEnabled(enabled)
        self.bm_radio.setEnabled(enabled)
        self.ac_radio.setEnabled(enabled)
        self.top_matches_spin.setEnabled(enabled)
        
        # update search button
        search_btn = self.findChild(QtWidgets.QPushButton)
        if search_btn:
            search_btn.setEnabled(enabled)
            search_btn.setText("Searching..." if not enabled else "Search")
    
    def get_current_keywords(self) -> List[str]:
        """ambil keywords yang sedang diinput"""
        keywords_text = self.keywords_input.text().strip()
        if not keywords_text:
            return []
        
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        return [kw for kw in keywords if kw]
    
    def clear_input(self):
        """bersihkan input"""
        self.keywords_input.clear()
        self.kmp_radio.setChecked(True)
        self.top_matches_spin.setValue(10)