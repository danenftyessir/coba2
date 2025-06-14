# src/ui/summary_view.py
from PyQt5 import QtWidgets, QtCore
from database.models import CVSummary, JobHistory, Education

class SummaryView(QtWidgets.QDialog):
    """dialog untuk menampilkan summary cv dengan job history dan education lengkap"""
    
    view_cv_requested = QtCore.pyqtSignal(str)  # resume_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resume_id = None
        self.setup_ui()
        
    def setup_ui(self):
        """setup user interface dengan comprehensive layout"""
        self.setWindowTitle("CV Summary")
        self.setModal(True)
        self.resize(700, 800)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # header with name
        header = self._create_header()
        layout.addWidget(header)
        
        # scroll area for content
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #ffffff;
            }
        """)
        
        # content widget
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        # action buttons
        buttons = self._create_buttons()
        layout.addWidget(buttons)
    
    def _create_header(self) -> QtWidgets.QWidget:
        """create header dengan candidate name"""
        header = QtWidgets.QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(header)
        
        self.name_label = QtWidgets.QLabel("CV Summary")
        self.name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        layout.addWidget(self.name_label)
        layout.addStretch()
        
        return header
    
    def _create_buttons(self) -> QtWidgets.QWidget:
        """create action buttons"""
        buttons_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(buttons_widget)
        
        # view cv button
        view_cv_btn = QtWidgets.QPushButton("📄 View Full CV")
        view_cv_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        view_cv_btn.clicked.connect(self._on_view_cv_clicked)
        layout.addWidget(view_cv_btn)
        
        layout.addStretch()
        
        # close button
        close_btn = QtWidgets.QPushButton("✖ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return buttons_widget
    
    def show_summary(self, resume_id: str, summary: CVSummary):
        """show comprehensive cv summary dengan semua detail"""
        self.resume_id = resume_id
        
        print(f"📋 displaying summary for {summary.name}")
        print(f"   skills: {len(summary.skills)}")
        print(f"   job history: {len(summary.job_history)}")
        print(f"   education: {len(summary.education)}")
        
        # update header
        self.name_label.setText(f"📋 {summary.name}")
        
        # clear previous content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # contact information
        if summary.contact_info:
            self._add_contact_section(summary.contact_info)
        
        # professional summary/overview
        if summary.summary:
            self._add_section("💼 Professional Summary", summary.summary, "#e8f4fd")
        
        # skills section
        if summary.skills:
            self._add_skills_section(summary.skills)
        
        # job history section - comprehensive
        if summary.job_history:
            self._add_job_history_section(summary.job_history)
        else:
            self._add_section("💼 Work Experience", "No work experience information found in CV.", "#fff3cd")
        
        # education section - comprehensive  
        if summary.education:
            self._add_education_section(summary.education)
        else:
            self._add_section("🎓 Education", "No education information found in CV.", "#fff3cd")
        
        # add stretch at end
        self.content_layout.addStretch()
        
        # show dialog
        self.show()
    
    def _add_contact_section(self, contact_info: dict):
        """add contact information section"""
        if not contact_info:
            return
            
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid #17a2b8;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel("📞 Contact Information")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(title_label)
        
        # contact details
        contact_layout = QtWidgets.QHBoxLayout()
        
        contact_items = []
        if 'email' in contact_info:
            contact_items.append(f"✉️ {contact_info['email']}")
        if 'phone' in contact_info:
            contact_items.append(f"📱 {contact_info['phone']}")
        if 'address' in contact_info:
            contact_items.append(f"📍 {contact_info['address']}")
        
        for item in contact_items:
            item_label = QtWidgets.QLabel(item)
            item_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #495057;
                    background-color: white;
                    padding: 6px 10px;
                    border-radius: 15px;
                    margin: 2px;
                }
            """)
            contact_layout.addWidget(item_label)
        
        contact_layout.addStretch()
        layout.addLayout(contact_layout)
        
        self.content_layout.addWidget(section)
    
    def _add_section(self, title: str, content: str, bg_color: str = "#ecf0f1"):
        """add general section dengan custom background"""
        section = QtWidgets.QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid #3498db;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
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
                font-size: 13px;
                color: #495057;
                background-color: transparent;
                line-height: 1.5;
                padding: 5px 0;
            }
        """)
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        self.content_layout.addWidget(section)
    
    def _add_skills_section(self, skills: list):
        """add skills section dengan tags style"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #e8f5e8;
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid #28a745;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel(f"⚡ Skills & Competencies ({len(skills)} items)")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # skills container with flow layout
        skills_widget = QtWidgets.QWidget()
        skills_layout = QtWidgets.QHBoxLayout(skills_widget)
        skills_layout.setContentsMargins(0, 0, 0, 0)
        skills_layout.setSpacing(8)
        
        # create skill tags (max 12 to avoid overflow)
        displayed_skills = skills[:12]
        colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6f42c1']
        
        for i, skill in enumerate(displayed_skills):
            skill_tag = QtWidgets.QLabel(skill)
            color = colors[i % len(colors)]
            skill_tag.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-size: 11px;
                    font-weight: bold;
                    margin: 2px;
                }}
            """)
            skill_tag.setAlignment(QtCore.Qt.AlignCenter)
            skills_layout.addWidget(skill_tag)
            
            # break to new line after 6 items
            if (i + 1) % 6 == 0 and i + 1 < len(displayed_skills):
                skills_layout.addStretch()
                break
        
        skills_layout.addStretch()
        layout.addWidget(skills_widget)
        
        # show remaining count if more than 12
        if len(skills) > 12:
            more_label = QtWidgets.QLabel(f"... and {len(skills) - 12} more skills")
            more_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #6c757d;
                    font-style: italic;
                    background-color: transparent;
                    margin-top: 5px;
                }
            """)
            layout.addWidget(more_label)
        
        self.content_layout.addWidget(section)
    
    def _add_job_history_section(self, job_history: list):
        """add comprehensive job history section"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #fff8e1;
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid #ff9800;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel(f"💼 Work Experience ({len(job_history)} positions)")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # job entries
        for i, job in enumerate(job_history):
            job_widget = self._create_job_entry(job, i + 1)
            layout.addWidget(job_widget)
        
        self.content_layout.addWidget(section)
    
    def _create_job_entry(self, job: JobHistory, index: int) -> QtWidgets.QWidget:
        """create detailed job entry widget"""
        job_widget = QtWidgets.QWidget()
        job_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 6px;
                padding: 12px;
                border: 1px solid #e9ecef;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(job_widget)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # job header
        header_layout = QtWidgets.QHBoxLayout()
        
        # position title
        position_label = QtWidgets.QLabel(f"{index}. {job.position}")
        position_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        header_layout.addWidget(position_label)
        
        # date range
        if job.start_date or job.end_date:
            date_range = f"{job.start_date or 'N/A'} - {job.end_date or 'N/A'}"
            date_label = QtWidgets.QLabel(date_range)
            date_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #6c757d;
                    background-color: #f8f9fa;
                    padding: 2px 8px;
                    border-radius: 10px;
                }
            """)
            header_layout.addWidget(date_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # company
        company_label = QtWidgets.QLabel(f"🏢 {job.company}")
        company_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #495057;
                background-color: transparent;
                margin-left: 10px;
            }
        """)
        layout.addWidget(company_label)
        
        # description if available
        if job.description and len(job.description.strip()) > 10:
            desc_label = QtWidgets.QLabel(f"📝 {job.description}")
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #6c757d;
                    background-color: transparent;
                    margin-left: 10px;
                    margin-top: 4px;
                    font-style: italic;
                }
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        return job_widget
    
    def _add_education_section(self, education: list):
        """add comprehensive education section"""
        section = QtWidgets.QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #e3f2fd;
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid #2196f3;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(section)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # title
        title_label = QtWidgets.QLabel(f"🎓 Education ({len(education)} entries)")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # education entries
        for i, edu in enumerate(education):
            edu_widget = self._create_education_entry(edu, i + 1)
            layout.addWidget(edu_widget)
        
        self.content_layout.addWidget(section)
    
    def _create_education_entry(self, edu: Education, index: int) -> QtWidgets.QWidget:
        """create detailed education entry widget"""
        edu_widget = QtWidgets.QWidget()
        edu_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 6px;
                padding: 12px;
                border: 1px solid #e9ecef;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(edu_widget)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # education header
        header_layout = QtWidgets.QHBoxLayout()
        
        # degree
        degree_label = QtWidgets.QLabel(f"{index}. {edu.degree}")
        degree_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                background-color: transparent;
            }
        """)
        header_layout.addWidget(degree_label)
        
        # year
        if edu.year:
            year_label = QtWidgets.QLabel(edu.year)
            year_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #6c757d;
                    background-color: #f8f9fa;
                    padding: 2px 8px;
                    border-radius: 10px;
                }
            """)
            header_layout.addWidget(year_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # institution
        institution_label = QtWidgets.QLabel(f"🏫 {edu.institution}")
        institution_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #495057;
                background-color: transparent;
                margin-left: 10px;
            }
        """)
        layout.addWidget(institution_label)
        
        # details if available
        if edu.details and len(edu.details.strip()) > 10 and edu.details != edu.institution:
            details_label = QtWidgets.QLabel(f"📋 {edu.details}")
            details_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #6c757d;
                    background-color: transparent;
                    margin-left: 10px;
                    margin-top: 4px;
                    font-style: italic;
                }
            """)
            details_label.setWordWrap(True)
            layout.addWidget(details_label)
        
        return edu_widget
    
    def _on_view_cv_clicked(self):
        """handle view cv button click"""
        if self.resume_id:
            print(f"📄 requesting to view cv for resume {self.resume_id}")
            self.view_cv_requested.emit(self.resume_id)