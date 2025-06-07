import os
import platform
import subprocess
import json
from typing import Dict, Optional, Any

class CVController:
    """controller untuk manage cv dan applicant data"""
    
    def __init__(self, repository):
        self.repository = repository
    
    def get_applicant_data(self, applicant_id: int) -> Optional[Dict[str, Any]]:
        """ambil data lengkap applicant berdasarkan id"""
        try:
            # ambil data dari repository
            applicant = self.repository.get_applicant_by_id(applicant_id)
            
            if not applicant:
                return None
            
            # format data untuk summary view
            data = {
                'applicant_id': applicant.get('id', applicant_id),
                'name': applicant.get('name', 'Unknown'),
                'email': applicant.get('email', ''),
                'phone': applicant.get('phone', ''),
                'address': applicant.get('address', ''),
                'linkedin_url': applicant.get('linkedin_url', ''),
                'date_of_birth': applicant.get('date_of_birth', ''),
                'skills': applicant.get('skills', ''),
                'work_experience': applicant.get('work_experience', ''),
                'education_history': applicant.get('education_history', ''),
                'summary_overview': applicant.get('summary_overview', '')
            }
            
            return data
            
        except Exception as e:
            print(f"error get applicant data: {e}")
            return None
    
    def open_cv_file(self, cv_path: str) -> bool:
        """buka file cv dengan default application - FIXED untuk mock data"""
        try:
            print(f"🔍 Attempting to open CV: {cv_path}")
            
            # MOCK DATA MODE: cek apakah ini mock data
            if cv_path.startswith('data/CV_') and not os.path.exists(cv_path):
                print(f"📄 Mock CV detected: {cv_path}")
                
                # coba cari file yang ada di direktori data
                filename = os.path.basename(cv_path)  # misal: CV_Bryan.pdf
                
                # coba berbagai lokasi
                possible_paths = [
                    cv_path,  # original path
                    f"data/{filename}",  # direct in data folder
                    f"./{cv_path}",  # relative to current dir
                    f"../{cv_path}",  # parent directory
                    filename,  # just filename
                ]
                
                file_found = None
                for path in possible_paths:
                    if os.path.exists(path):
                        file_found = path
                        print(f"✅ Found CV file at: {path}")
                        break
                
                if file_found:
                    return self._open_file_system(file_found)
                else:
                    # jika tidak ada file fisik, tampilkan info mock
                    self._show_mock_cv_info(cv_path)
                    return True  # return true karena sudah handle dengan baik
            
            # REAL FILE MODE: file exists
            elif os.path.exists(cv_path):
                print(f"✅ Real CV file found: {cv_path}")
                return self._open_file_system(cv_path)
            
            # FILE NOT FOUND
            else:
                print(f"❌ CV file not found: {cv_path}")
                self._show_file_not_found_info(cv_path)
                return False
            
        except Exception as e:
            print(f"❌ Error opening CV: {e}")
            return False
    
    def _open_file_system(self, file_path: str) -> bool:
        """buka file dengan sistem default - FIXED untuk path dengan spasi"""
        try:
            print(f"🔍 Opening file: {file_path}")
            system = platform.system()
            
            # convert ke absolute path
            abs_path = os.path.abspath(file_path)
            print(f"🔍 Absolute path: {abs_path}")
            
            if system == "Windows":
                # Windows - gunakan os.startfile (handle spasi otomatis)
                os.startfile(abs_path)
                print("✅ Opened with Windows startfile")
            elif system == "Darwin":  
                # macOS - quote path untuk handle spasi
                subprocess.run(["open", abs_path], check=True)
                print("✅ Opened with macOS open")
            else:  
                # Linux - quote path untuk handle spasi  
                subprocess.run(["xdg-open", abs_path], check=True)
                print("✅ Opened with Linux xdg-open")
            
            return True
            
        except Exception as e:
            print(f"❌ Error opening file: {e}")
            
            # FALLBACK 1: coba dengan webbrowser
            try:
                import webbrowser
                file_url = f"file:///{abs_path.replace(os.sep, '/')}"
                print(f"🔄 Trying webbrowser: {file_url}")
                webbrowser.open(file_url)
                print("✅ Opened with webbrowser")
                return True
            except Exception as e2:
                print(f"❌ Webbrowser failed: {e2}")
            
            # FALLBACK 2: coba dengan shell execute (Windows)
            if system == "Windows":
                try:
                    import subprocess
                    subprocess.run(f'start "" "{abs_path}"', shell=True, check=True)
                    print("✅ Opened with Windows shell")
                    return True
                except Exception as e3:
                    print(f"❌ Shell failed: {e3}")
            
            # FALLBACK 3: show path untuk manual open
            try:
                # import PyQt
                try:
                    from PyQt5.QtWidgets import QMessageBox, QApplication
                    import PyQt5.QtGui as QtGui
                except ImportError:
                    from PySide6.QtWidgets import QMessageBox, QApplication
                    import PySide6.QtGui as QtGui
                
                msg = QMessageBox()
                msg.setWindowTitle("Open PDF Manually")
                msg.setText("Automatic PDF opening failed")
                msg.setInformativeText(
                    f"Please open this file manually:\n\n"
                    f"📁 {abs_path}\n\n"
                    f"Copy path to clipboard?"
                )
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                
                if msg.exec_() == QMessageBox.Yes:
                    # copy to clipboard
                    clipboard = QApplication.clipboard()
                    clipboard.setText(abs_path)
                    print("✅ Path copied to clipboard")
                
                return True
                
            except Exception as e4:
                print(f"❌ Fallback dialog failed: {e4}")
                print(f"📄 MANUAL: Please open: {abs_path}")
                return False
    
    def _show_mock_cv_info(self, cv_path: str):
        """tampilkan info untuk mock CV"""
        try:
            # import di sini untuk avoid circular import
            from PyQt5.QtWidgets import QMessageBox
            
            # extract nama dari path
            name = cv_path.replace('data/CV_', '').replace('.pdf', '')
            
            msg = QMessageBox()
            msg.setWindowTitle("Mock CV - Demo Mode")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"📄 CV Demo: {name}")
            msg.setInformativeText(
                f"Ini adalah mock data untuk demonstrasi aplikasi.\n\n"
                f"CV Path: {cv_path}\n"
                f"Status: Data dummy untuk testing algoritma pencarian\n\n"
                f"Dalam implementasi nyata, file PDF akan terbuka di sini."
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
        except ImportError:
            # fallback jika tidak ada PyQt5
            print(f"📄 MOCK CV INFO:")
            print(f"   Name: {cv_path}")
            print(f"   Status: Demo data for algorithm testing")
            print(f"   Note: In real implementation, PDF would open here")
    
    def _show_file_not_found_info(self, cv_path: str):
        """tampilkan info file tidak ditemukan"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox()
            msg.setWindowTitle("File Tidak Ditemukan")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("CV File Tidak Ditemukan")
            msg.setInformativeText(
                f"File: {cv_path}\n\n"
                f"Kemungkinan penyebab:\n"
                f"• File belum ada di sistem\n"
                f"• Path file tidak benar\n"
                f"• Menggunakan mock data (demo mode)\n\n"
                f"Silakan periksa keberadaan file atau gunakan mock data."
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
        except ImportError:
            print(f"❌ FILE NOT FOUND: {cv_path}")
    
    def extract_cv_info(self, cv_path: str) -> Dict[str, Any]:
        """ekstrak informasi dari cv (untuk future implementation)"""
        # placeholder untuk ekstraksi regex
        return {
            'skills': '',
            'work_experience': '',
            'education_history': '',
            'summary_overview': ''
        }
    
    def save_applicant_data(self, applicant_data: Dict[str, Any]) -> bool:
        """simpan atau update data applicant"""
        try:
            # validasi data
            if not applicant_data.get('name'):
                raise ValueError("nama applicant harus diisi")
            
            # simpan ke repository
            result = self.repository.save_applicant(applicant_data)
            return result
            
        except Exception as e:
            print(f"error save applicant: {e}")
            return False
    
    def delete_applicant(self, applicant_id: int) -> bool:
        """hapus data applicant"""
        try:
            return self.repository.delete_applicant(applicant_id)
        except Exception as e:
            print(f"error delete applicant: {e}")
            return False