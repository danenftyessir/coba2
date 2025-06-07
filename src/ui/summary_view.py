# src/ui/summary_view.py
from PyQt5 import QtWidgets, QtCore, QtGui
from ..database.models import CVSummary

class SummaryView(QtWidgets.QDialog):
    """dialog untuk menampilkan summary cv"""
    
    # signal
    view_cv_requested = QtCore.pyqtSignal(str)  # resume_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resume_id = None
        self.setup_ui()
        
    def setup_ui(self):
        """setup user interface"""
        self.setWindowTitle("CV Summary")
        self.setModal(True)
        self.resize(600, 700)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # header
        header = self._create_header()
        layout.addWidget(header)
        
        # scroll area for content
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # content widget
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(0, 0, 10, 0)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        # buttons
        buttons = self._create_buttons()
        layout.addWidget(buttons)
    
    def _create_header(self) -> QtWidgets.QWidget:
        """buat header dengan nama"""
        header = QtWidgets.QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(header)
        
        self.name_label = QtWidgets.QLabel("CV Summary")
        self.name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        layout.addWidget(self.name_label)
        layout.addStretch()
        
        return header
    
    def _create_buttons(self) -> QtWidgets.QWidget:
        """buat buttons di bagian bawah"""
        buttons_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(buttons_widget)
        
        # view cv button
        view_cv_btn = QtWidgets.QPushButton("View CV")
        view_cv_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        view_cv_btn.clicked.connect(self._on_view_cv_clicked)
        layout.addWidget(view_cv_btn)
        
        layout.addStretch()
        
        # close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return buttons_widget
    
    def show_summary(self, resume_id: str, summary: CVSummary):
        """tampilkan cv summary"""
        self.resume_id = resume_id
        
        # update header
        self.name_label.setText(summary.name)
        
        # clear previous content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # contact info
        if summary.contact_info:
            self._add_section("Contact Information", self._format_contact_info(summary.contact_info))
        
        # overview
        if summary.summary:
            self._add_section("Summary", summary.summary)
        
        # skills
        if summary.skills:
            self._add_skills_section(summary.skills)
        
        # experience
        if summary.experience:
            self._add_experience_section(summary.experience)
        
        # education
        if summary.education:
            self._add_education_section(summary.education)
        
        # add stretch at end
        self.content_layout.addStretch()
        
        # show dialog
        self.show()
    
    def _add_section(self, title: str, content: str):
        """tambah section dengan title dan content"""
        # section container
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # content
        content_label = QtWidgets.QLabel(content)
        content_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #34495e;
                background-color: transparent;
                line-height: 1.4;
            }
        """)
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        self.content_layout.addWidget(section)
    
    def _add_skills_section(self, skills: list):
        """tambah section skills dengan tags"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel("Skills")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # skills container
        skills_widget = QtWidgets.QWidget()
        skills_layout = QtWidgets.QHBoxLayout(skills_widget)
        skills_layout.setContentsMargins(0, 0, 0, 0)
        
        # create skill tags
        col_count = 0
        for skill in skills[:8]:  # max 8 skills
            if col_count >= 4:  # new row after 4 items
                skills_layout.addStretch()
                # create new row (simplified - just continue in same row)
            
            skill_tag = QtWidgets.QLabel(skill)
            skill_tag.setStyleSheet("""
                QLabel {
                    background-color: #3498db;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            skill_tag.setAlignment(QtCore.Qt.AlignCenter)
            skills_layout.addWidget(skill_tag)
            col_count += 1
        
        skills_layout.addStretch()
        layout.addWidget(skills_widget)
        
        self.content_layout.addWidget(section)
    
    def _add_experience_section(self, experiences: list):
        """tambah section experience"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel("Job History")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # experience items
        for exp in experiences:
            exp_widget = QtWidgets.QWidget()
            exp_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 4px;
                    padding: 10px;
                }
            """)
            
            exp_layout = QtWidgets.QVBoxLayout(exp_widget)
            exp_layout.setSpacing(4)
            exp_layout.setContentsMargins(0, 0, 0, 0)
            
            # position and period
            header = QtWidgets.QLabel(f"{exp.get('position', 'Position')} • {exp.get('period', 'Period')}")
            header.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #2c3e50;
                    background-color: transparent;
                }
            """)
            exp_layout.addWidget(header)
            
            # company
            company = QtWidgets.QLabel(exp.get('company', 'Company'))
            company.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #7f8c8d;
                    background-color: transparent;
                }
            """)
            exp_layout.addWidget(company)
            
            layout.addWidget(exp_widget)
        
        self.content_layout.addWidget(section)
    
    def _add_education_section(self, education: list):
        """tambah section education"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel("Education")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # education items
        for edu in education:
            edu_widget = QtWidgets.QWidget()
            edu_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 4px;
                    padding: 10px;
                }
            """)
            
            edu_layout = QtWidgets.QVBoxLayout(edu_widget)
            edu_layout.setSpacing(4)
            edu_layout.setContentsMargins(0, 0, 0, 0)
            
            # degree and year
            header = QtWidgets.QLabel(f"{edu.get('degree', 'Degree')} • {edu.get('year', 'Year')}")
            header.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #2c3e50;
                    background-color: transparent;
                }
            """)
            edu_layout.addWidget(header)
            
            # institution
            institution = QtWidgets.QLabel(edu.get('institution', 'Institution'))
            institution.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #7f8c8d;
                    background-color: transparent;
                }
            """)
            edu_layout.addWidget(institution)
            
            layout.addWidget(edu_widget)
        
        self.content_layout.addWidget(section)
    
    def _format_contact_info(self, contact_info: dict) -> str:
        """format contact info untuk display"""
        formatted = []
        
        if 'phone' in contact_info:
            formatted.append(f"Phone: {contact_info['phone']}")
        
        if 'email' in contact_info:
            formatted.append(f"Email: {contact_info['email']}")
        
        if 'address' in contact_info:
            formatted.append(f"Address: {contact_info['address']}")
        
        return "\n".join(formatted) if formatted else "No contact information available"
    
    def _on_view_cv_clicked(self):
        """handle view cv button click"""
        if self.resume_id:
            self.view_cv_requested.emit(self.resume_id)