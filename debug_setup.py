"""
Debug Script untuk cek dataset dan setup database
"""

import os
import glob

def debug_dataset_path():
    """debug path dataset kaggle"""
    print("🔍 DEBUGGING DATASET PATH...")
    print("=" * 50)
    
    # path yang dicoba
    possible_paths = [
        r"C:\Users\DANENDRA\.cache\kagglehub\datasets\snehaanbhawal\resume-dataset\versions\1",
        r"C:\Users\DANENDRA\.cache\kagglehub\datasets\snehaanbhawal\resume-dataset\versions\1\data",
        r"C:\Users\DANENDRA\.kaggle\datasets\snehaanbhawal\resume-dataset",
        r"C:\Users\DANENDRA\Downloads\resume-dataset",
        r".\data",
        r"..\data",
        r"data"
    ]
    
    print("🔍 Checking possible dataset locations...")
    
    found_path = None
    
    for path in possible_paths:
        print(f"\n📁 Checking: {path}")
        
        if os.path.exists(path):
            print(f"✅ Path exists!")
            
            # list contents
            try:
                contents = os.listdir(path)
                print(f"📂 Contents: {contents}")
                
                # cek apakah ada folder data
                data_path = os.path.join(path, "data")
                if os.path.exists(data_path):
                    print(f"✅ Found 'data' folder!")
                    
                    # list categories in data folder
                    categories = [d for d in os.listdir(data_path) 
                                 if os.path.isdir(os.path.join(data_path, d))]
                    print(f"📂 Categories: {categories}")
                    
                    # count PDF files per category
                    total_pdfs = 0
                    for category in categories[:5]:  # check first 5 categories
                        category_path = os.path.join(data_path, category)
                        pdfs = glob.glob(os.path.join(category_path, "*.pdf"))
                        print(f"  - {category}: {len(pdfs)} PDFs")
                        total_pdfs += len(pdfs)
                    
                    if total_pdfs > 0:
                        print(f"🎉 FOUND VALID DATASET: {path}")
                        found_path = path
                        break
                
                # atau cek apakah path ini langsung folder data
                elif any(name.endswith('.pdf') for name in contents if os.path.isfile(os.path.join(path, name))):
                    print(f"✅ Found PDF files directly in this path!")
                    found_path = path
                    break
                    
            except Exception as e:
                print(f"❌ Error reading path: {e}")
        else:
            print(f"❌ Path not found")
    
    if found_path:
        print(f"\n🎉 DATASET FOUND AT: {found_path}")
        return found_path
    else:
        print(f"\n❌ NO DATASET FOUND!")
        print(f"\n💡 Manual steps:")
        print(f"1. Download dataset dari Kaggle")
        print(f"2. Extract ke folder yang mudah diakses")
        print(f"3. Update path di script")
        return None

def find_kaggle_cache():
    """cari folder kaggle cache"""
    print(f"\n🔍 SEARCHING KAGGLE CACHE...")
    
    username = os.getenv('USERNAME') or os.getenv('USER')
    
    possible_cache_locations = [
        f"C:\\Users\\{username}\\.cache\\kagglehub",
        f"C:\\Users\\{username}\\.kaggle",
        f"C:\\Users\\{username}\\AppData\\Local\\kagglehub",
        f"C:\\Users\\{username}\\Documents\\kaggle",
    ]
    
    for cache_path in possible_cache_locations:
        print(f"📁 Checking: {cache_path}")
        
        if os.path.exists(cache_path):
            print(f"✅ Found cache folder!")
            
            # search for resume dataset
            try:
                for root, dirs, files in os.walk(cache_path):
                    if 'resume-dataset' in root.lower():
                        print(f"🎉 Found resume dataset at: {root}")
                        
                        # check for data folder
                        data_path = os.path.join(root, "data")
                        if os.path.exists(data_path):
                            return root
                        
                        # or check subfolders
                        for subdir in os.listdir(root):
                            sub_path = os.path.join(root, subdir)
                            if os.path.isdir(sub_path):
                                data_sub_path = os.path.join(sub_path, "data")
                                if os.path.exists(data_sub_path):
                                    return sub_path
            except Exception as e:
                print(f"❌ Error searching: {e}")
        else:
            print(f"❌ Not found")
    
    return None

def create_setup_with_correct_path():
    """buat setup script dengan path yang benar"""
    
    # debug path dulu
    dataset_path = debug_dataset_path()
    
    if not dataset_path:
        # coba cari di kaggle cache
        dataset_path = find_kaggle_cache()
    
    if not dataset_path:
        print(f"\n❌ DATASET NOT FOUND ANYWHERE!")
        print(f"\n💡 SOLUTION:")
        print(f"1. Download dataset manual:")
        print(f"   https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset")
        print(f"2. Extract ke folder project (buat folder 'data')")
        print(f"3. Atau pakai mock data untuk testing")
        
        # offer to create mock data
        create_mock = input("\nCreate mock data for testing? (y/n): ").lower().strip()
        if create_mock == 'y':
            create_mock_dataset()
        
        return None
    
    print(f"\n🎉 DATASET FOUND!")
    print(f"📁 Path: {dataset_path}")
    
    # generate setup script dengan path yang benar
    generate_fixed_setup_script(dataset_path)
    
    return dataset_path

def create_mock_dataset():
    """buat mock dataset untuk testing"""
    print(f"\n📋 Creating mock dataset...")
    
    # buat folder data kalau belum ada
    data_folder = "data"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    # buat beberapa kategori mock
    categories = ['CHEF', 'ENGINEER', 'DESIGNER', 'HR', 'SALES']
    
    for category in categories:
        category_path = os.path.join(data_folder, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        # buat mock PDF files (kosong untuk testing)
        for i in range(5):  # 5 files per category
            mock_file = os.path.join(category_path, f"{category}_Resume_{i+1}.pdf")
            if not os.path.exists(mock_file):
                with open(mock_file, 'w') as f:
                    f.write(f"Mock PDF content for {category} Resume {i+1}")
    
    print(f"✅ Mock dataset created in: {os.path.abspath(data_folder)}")
    return os.path.abspath(data_folder)
