import os
import shutil

class TestModeManager:
    """manage test mode dengan limited data untuk performance testing"""
    
    def __init__(self):
        # Get the correct paths relative to project root
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to project root
        self.test_data_path = os.path.join(self.project_root, "data_test")
        self.original_data_path = os.path.join(self.project_root, "data")
        
        print(f"Project root: {self.project_root}")
        print(f"Original data path: {self.original_data_path}")
        print(f"Test data path: {self.test_data_path}")
        
    def create_test_dataset(self, max_cvs_per_category=5):
        """create limited test dataset"""
        
        # Check if original data directory exists
        if not os.path.exists(self.original_data_path):
            print(f"❌ Original data directory not found: {self.original_data_path}")
            print("Please ensure the data directory exists in the project root with CV files")
            return 0
        
        # Remove existing test data
        if os.path.exists(self.test_data_path):
            print(f"Removing existing test data: {self.test_data_path}")
            shutil.rmtree(self.test_data_path)
        
        os.makedirs(self.test_data_path, exist_ok=True)
        print(f"Created test data directory: {self.test_data_path}")
        
        total_copied = 0
        
        # List all categories in original data
        try:
            categories = os.listdir(self.original_data_path)
            print(f"Found categories: {categories}")
        except Exception as e:
            print(f"❌ Error listing categories: {e}")
            return 0
        
        for category in categories:
            category_path = os.path.join(self.original_data_path, category)
            if not os.path.isdir(category_path):
                print(f"Skipping non-directory: {category}")
                continue
                
            test_category_path = os.path.join(self.test_data_path, category)
            os.makedirs(test_category_path, exist_ok=True)
            
            # Get PDF files in this category
            try:
                pdf_files = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
                print(f"Category {category}: found {len(pdf_files)} PDF files")
            except Exception as e:
                print(f"❌ Error reading category {category}: {e}")
                continue
            
            # Copy limited number of PDFs
            copied_in_category = 0
            for i, pdf_file in enumerate(pdf_files[:max_cvs_per_category]):
                try:
                    src = os.path.join(category_path, pdf_file)
                    dst = os.path.join(test_category_path, pdf_file)
                    
                    # Check source file size
                    file_size = os.path.getsize(src) / (1024 * 1024)  # MB
                    if file_size > 10:  # Skip very large files
                        print(f"Skipping large file: {pdf_file} ({file_size:.1f}MB)")
                        continue
                    
                    shutil.copy2(src, dst)
                    total_copied += 1
                    copied_in_category += 1
                    
                except Exception as e:
                    print(f"❌ Error copying {pdf_file}: {e}")
                    continue
            
            print(f"✅ Category {category}: copied {copied_in_category} files")
        
        print(f"🎯 Created test dataset with {total_copied} CVs in {self.test_data_path}/")
        return total_copied
    
    def enable_test_mode(self):
        """switch to test mode"""
        if not os.path.exists(self.test_data_path):
            print("Test dataset not found, creating it...")
            self.create_test_dataset()
        
        # Create backup directory path
        backup_path = os.path.join(self.project_root, "data_backup")
        
        # backup original and switch
        if os.path.exists(backup_path):
            print(f"Removing existing backup: {backup_path}")
            shutil.rmtree(backup_path)
        
        if os.path.exists(self.original_data_path):
            print(f"Backing up original data: {self.original_data_path} -> {backup_path}")
            shutil.move(self.original_data_path, backup_path)
        
        print(f"Switching to test data: {self.test_data_path} -> {self.original_data_path}")
        shutil.move(self.test_data_path, self.original_data_path)
        
        print("✅ Test mode enabled - using limited dataset")
    
    def disable_test_mode(self):
        """switch back to full dataset"""
        backup_path = os.path.join(self.project_root, "data_backup")
        
        if os.path.exists(backup_path):
            # Move current data to test location
            if os.path.exists(self.original_data_path):
                print(f"Saving test data: {self.original_data_path} -> {self.test_data_path}")
                shutil.move(self.original_data_path, self.test_data_path)
            
            # Restore original data
            print(f"Restoring original data: {backup_path} -> {self.original_data_path}")
            shutil.move(backup_path, self.original_data_path)
            print("✅ Test mode disabled - using full dataset")
        else:
            print("❌ No backup found - cannot restore original dataset")
    
    def get_status(self):
        """get current mode status"""
        backup_exists = os.path.exists(os.path.join(self.project_root, "data_backup"))
        test_data_exists = os.path.exists(self.test_data_path)
        original_data_exists = os.path.exists(self.original_data_path)
        
        if backup_exists:
            return "test_mode_active"
        elif test_data_exists:
            return "test_data_ready"
        elif original_data_exists:
            return "normal_mode"
        else:
            return "no_data"