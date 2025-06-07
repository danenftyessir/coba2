from PyQt5 import QtWidgets, QtCore, QtGui
import os
import platform
import subprocess

class SkillBadge(QtWidgets.QLabel):
    """Skill badge widget"""
    def __init__(self, skill_name, parent=None):
        super().__init__(parent)
        self.setText(skill_name)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("""
            background-color: #4a90e2;
            color: white;
            border-radius: 15px;
            padding: 5px 15px;
            margin: 5px;
            font-weight: bold;
        """)

def open_file_in_default_app(file_path):
    """buka file dengan aplikasi default sistem"""
    try:
        system = platform.system()
        
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macos
            subprocess.run(["open", file_path])
        else:  # linux/unix
            subprocess.run(["xdg-open", file_path])
        
        return True
    except Exception as e:
        print(f"❌ Error membuka file: {e}")
        return False

class SummaryView(QtWidgets.QDialog):
    """CV summary display dialog"""
    def __init__(self, parent, applicant_data, cv_path):
        super().__init__(parent)
        self.setWindowTitle("CV Summary")
        self.setGeometry(200, 200, 650, 750)
        self.setModal(True)
        
        self.applicant_data = applicant_data
        self.cv_path = cv_path
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create UI elements"""
        # Use a scrollable layout in case of long content
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(main_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        dialog_layout = QtWidgets.QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll)
        
        # Title
        title = QtWidgets.QLabel("CV Summary")
        title.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #333333; padding-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Applicant Identity Card
        identity_card = QtWidgets.QWidget()
        identity_card.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 15px;
            border: 1px solid #dddddd;
        """)
        identity_layout = QtWidgets.QVBoxLayout(identity_card)
        
        # Name header
        name_header = QtWidgets.QLabel(self.applicant_data.get("name", "N/A"))
        name_header.setStyleSheet("""
            background-color: #4a90e2;
            color: white;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            padding: 15px;
            font-weight: bold;
        """)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        name_header.setFont(font)
        identity_layout.addWidget(name_header)
        
        # Personal details
        details_layout = QtWidgets.QVBoxLayout()
        details_layout.setSpacing(12)
        details_layout.setContentsMargins(15, 15, 15, 15)
        
        # Birth date
        birthdate = self.applicant_data.get("date_of_birth", "N/A")
        birthdate_layout = QtWidgets.QHBoxLayout()
        birthdate_icon = QtWidgets.QLabel("🎂")
        birthdate_icon.setStyleSheet("font-size: 16px; padding-right: 10px;")
        birthdate_layout.addWidget(birthdate_icon)
        birthdate_label = QtWidgets.QLabel(f"Date of Birth: {birthdate}")
        birthdate_label.setStyleSheet("font-size: 14px;")
        birthdate_layout.addWidget(birthdate_label)
        birthdate_layout.addStretch()
        details_layout.addLayout(birthdate_layout)
        
        # Address
        address = self.applicant_data.get("address", "N/A")
        address_layout = QtWidgets.QHBoxLayout()
        address_icon = QtWidgets.QLabel("📍")
        address_icon.setStyleSheet("font-size: 16px; padding-right: 10px;")
        address_layout.addWidget(address_icon)
        address_label = QtWidgets.QLabel(f"Address: {address}")
        address_label.setStyleSheet("font-size: 14px;")
        address_layout.addWidget(address_label)
        address_layout.addStretch()
        details_layout.addLayout(address_layout)
        
        # Phone
        phone = self.applicant_data.get("phone", "N/A")
        phone_layout = QtWidgets.QHBoxLayout()
        phone_icon = QtWidgets.QLabel("📱")
        phone_icon.setStyleSheet("font-size: 16px; padding-right: 10px;")
        phone_layout.addWidget(phone_icon)
        phone_label = QtWidgets.QLabel(f"Phone: {phone}")
        phone_label.setStyleSheet("font-size: 14px;")
        phone_layout.addWidget(phone_label)
        phone_layout.addStretch()
        details_layout.addLayout(phone_layout)
        
        # Email
        email = self.applicant_data.get("email", "")
        if email:
            email_layout = QtWidgets.QHBoxLayout()
            email_icon = QtWidgets.QLabel("📧")
            email_icon.setStyleSheet("font-size: 16px; padding-right: 10px;")
            email_layout.addWidget(email_icon)
            email_label = QtWidgets.QLabel(f"Email: {email}")
            email_label.setStyleSheet("font-size: 14px;")
            email_layout.addWidget(email_label)
            email_layout.addStretch()
            details_layout.addLayout(email_layout)
        
        # LinkedIn
        linkedin_url = self.applicant_data.get("linkedin_url", "")
        if linkedin_url:
            linkedin_layout = QtWidgets.QHBoxLayout()
            linkedin_icon = QtWidgets.QLabel("🔗")
            linkedin_icon.setStyleSheet("font-size: 16px; padding-right: 10px;")
            linkedin_layout.addWidget(linkedin_icon)
            linkedin_label = QtWidgets.QLabel(f"LinkedIn: {linkedin_url}")
            linkedin_label.setStyleSheet("font-size: 14px;")
            linkedin_layout.addWidget(linkedin_label)
            linkedin_layout.addStretch()
            details_layout.addLayout(linkedin_layout)
            
        # Add details to identity card
        identity_layout.addLayout(details_layout)
        main_layout.addWidget(identity_card)
        
        # Skills Section
        skills_title = self._create_section_header("Skills")
        main_layout.addWidget(skills_title)
        
        # Skills container
        skills_container = QtWidgets.QWidget()
        skills_container.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 15px;
            padding: 15px;
            border: 1px solid #dddddd;
        """)
        skills_layout = QtWidgets.QHBoxLayout(skills_container)
        skills_layout.setAlignment(QtCore.Qt.AlignLeft)
        
        # Parse skills and create badges
        skills_text = self.applicant_data.get("skills", "")
        skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
        
        if skills:
            flow_layout = FlowLayout(horizontal_spacing=10, vertical_spacing=10)
            
            for skill in skills:
                if skill:
                    skill_badge = SkillBadge(skill)
                    flow_layout.addWidget(skill_badge)
            
            skills_wrapper = QtWidgets.QWidget()
            skills_wrapper.setLayout(flow_layout)
            skills_layout.addWidget(skills_wrapper)
        else:
            no_skills = QtWidgets.QLabel("No skills listed")
            no_skills.setStyleSheet("font-style: italic; color: #888888;")
            skills_layout.addWidget(no_skills)
            
        skills_layout.addStretch()
        main_layout.addWidget(skills_container)
        
        # Work Experience Section
        work_title = self._create_section_header("Work Experience")
        main_layout.addWidget(work_title)
        
        # Work container
        work_container = QtWidgets.QWidget()
        work_container.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 15px;
            border: 1px solid #dddddd;
            padding: 15px;
        """)
        work_layout = QtWidgets.QVBoxLayout(work_container)
        
        work_exp = self.applicant_data.get("work_experience", "")
        if work_exp:
            # Parse work experience
            experiences = work_exp.split("\n")
            for exp in experiences:
                if not exp.strip():
                    continue
                    
                exp_label = QtWidgets.QLabel(exp)
                exp_label.setWordWrap(True)
                exp_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
                work_layout.addWidget(exp_label)
        else:
            no_work = QtWidgets.QLabel("No work experience listed")
            no_work.setStyleSheet("font-style: italic; color: #888888;")
            work_layout.addWidget(no_work)
        
        main_layout.addWidget(work_container)
        
        # Education Section
        edu_title = self._create_section_header("Education")
        main_layout.addWidget(edu_title)
        
        # Education container
        edu_container = QtWidgets.QWidget()
        edu_container.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 15px;
            border: 1px solid #dddddd;
            padding: 15px;
        """)
        edu_layout = QtWidgets.QVBoxLayout(edu_container)
        
        education = self.applicant_data.get("education_history", "")
        if education:
            # Parse education history
            edu_items = education.split("\n")
            for edu in edu_items:
                if not edu.strip():
                    continue
                    
                edu_label = QtWidgets.QLabel(edu)
                edu_label.setWordWrap(True)
                edu_label.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
                edu_layout.addWidget(edu_label)
        else:
            no_edu = QtWidgets.QLabel("No education history listed")
            no_edu.setStyleSheet("font-style: italic; color: #888888;")
            edu_layout.addWidget(no_edu)
        
        main_layout.addWidget(edu_container)
        
        # Add spacer to push everything up
        main_layout.addStretch(1)
        
        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        view_cv_button = QtWidgets.QPushButton("View Full CV")
        view_cv_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        view_cv_button.setMinimumHeight(40)
        view_cv_button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                padding: 10px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4ca84c;
            }
            QPushButton:pressed {
                background-color: #3c983c;
            }
        """)
        view_cv_button.clicked.connect(self._view_cv)
        button_layout.addWidget(view_cv_button)
        
        button_layout.addStretch()
        
        close_button = QtWidgets.QPushButton("Close")
        close_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        close_button.setMinimumHeight(40)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333333;
                border-radius: 10px;
                font-weight: bold;
                padding: 10px 15px;
                font-size: 14px;
                border: 1px solid #cccccc;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
    
    def _create_section_header(self, title):
        """Create a styled section header"""
        header = QtWidgets.QLabel(title)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(16)
        header.setFont(font)
        header.setStyleSheet("color: #333333; margin-top: 10px;")
        return header
        
    def _view_cv(self):
        """Open the CV file"""
        try:
            if os.path.exists(self.cv_path):
                success = open_file_in_default_app(self.cv_path)
                if not success:
                    QtWidgets.QMessageBox.warning(self, "Error", f"Could not open CV file: {self.cv_path}")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", f"CV file not found: {self.cv_path}")
        except Exception as e:
            print(f"❌ Error view CV: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Error opening CV: {str(e)}")

# FlowLayout for skills badges
class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, horizontal_spacing=0, vertical_spacing=0):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing
        self.items = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
        size += QtCore.QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, test_only):
        x = rect.x() + self.contentsMargins().left()
        y = rect.y() + self.contentsMargins().top()
        line_height = 0
        spacing_x = self.horizontal_spacing
        spacing_y = self.vertical_spacing

        for item in self.items:
            widget = item.widget()
            next_x = x + item.sizeHint().width() + spacing_x
            if next_x - spacing_x > rect.right() - self.contentsMargins().right() and line_height > 0:
                x = rect.x() + self.contentsMargins().left()
                y = y + line_height + spacing_y
                next_x = x + item.sizeHint().width() + spacing_x
                line_height = 0

            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + self.contentsMargins().bottom()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    sample_data = {
        'name': 'Bryan P. Hutagalung',
        'date_of_birth': '1998-05-25',
        'address': 'Jakarta, Indonesia',
        'phone': '+6282211878972',
        'email': 'bryan.p.hutagalung@gmail.com',
        'linkedin_url': 'linkedin.com/in/bryan-hutagalung',
        'skills': 'Python, Java, SQL, Software Engineering, Git, Docker, AWS, React',
        'work_experience': 'Software Developer at Tech Company (2020-Present)\nLed development of multiple applications\nBackend Developer at StartUp Inc. (2018-2020)',
        'education_history': 'Computer Science, Institut Teknologi Bandung (2018-2022)\nSenior High School, SMA 1 Jakarta (2015-2018)'
    }
    
    dialog = SummaryView(None, sample_data, "dummy.pdf")
    dialog.exec_()