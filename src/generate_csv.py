#!/usr/bin/env python3
"""
Generate Resume CSV from PDF file structure
Creates a CSV file with ID and Category based on the PDF files in data directory
"""

import os
import pandas as pd
from pathlib import Path

def generate_resume_csv():
    """Generate Resume.csv from the PDF file structure"""
    print("🔄 Generating Resume.csv from PDF file structure...")
    
    # Base paths
    base_dir = Path(__file__).parent.parent  # Go up to project root
    data_dir = base_dir / "data"
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    # Collect all PDF files
    resumes = []
    total_files = 0
    
    for category_dir in data_dir.iterdir():
        if not category_dir.is_dir():
            continue
            
        category_name = category_dir.name
        print(f"📁 Processing category: {category_name}")
        
        pdf_files = list(category_dir.glob("*.pdf"))
        print(f"   Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            # Extract ID from filename (remove .pdf extension)
            resume_id = pdf_file.stem
            
            resumes.append({
                'ID': resume_id,
                'Category': category_name
            })
            total_files += 1
    
    if not resumes:
        print("❌ No PDF files found in data directory")
        return False
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(resumes)
    csv_path = base_dir / "Resume.csv"
    
    try:
        df.to_csv(csv_path, index=False)
        print(f"✅ Successfully created Resume.csv with {total_files} records")
        print(f"📍 Saved to: {csv_path}")
        
        # Show summary by category
        category_counts = df['Category'].value_counts()
        print("\n📊 Summary by category:")
        for category, count in category_counts.items():
            print(f"   {category}: {count} CVs")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create CSV file: {e}")
        return False

if __name__ == "__main__":
    print("=== ATS CV Search - Resume CSV Generator ===")
    if generate_resume_csv():
        print("\n🎉 Resume CSV generation completed successfully!")
        print("You can now run the data migration script.")
    else:
        print("\n❌ Resume CSV generation failed!")
