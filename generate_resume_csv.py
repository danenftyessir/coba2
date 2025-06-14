#!/usr/bin/env python3
"""
Generate Resume.csv from PDF files in data directory
Creates a CSV file mapping resume IDs to categories based on file structure
"""

import os
import pandas as pd
from pathlib import Path

def generate_resume_csv():
    """Generate Resume.csv from PDF files in data directory"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, 'data')
    
    if not os.path.exists(data_path):
        print(f"❌ Data directory not found: {data_path}")
        return False
    
    print(f"📁 Scanning data directory: {data_path}")
    
    resumes = []
    
    # Scan all category directories
    for category_dir in os.listdir(data_path):
        category_path = os.path.join(data_path, category_dir)
        
        if os.path.isdir(category_path):
            print(f"📂 Processing category: {category_dir}")
            
            # Count PDF files in this category
            pdf_files = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
            
            for pdf_file in pdf_files:
                # Extract ID from filename (remove .pdf extension)
                resume_id = os.path.splitext(pdf_file)[0]
                
                resumes.append({
                    'ID': resume_id,
                    'Category': category_dir
                })
            
            print(f"   Found {len(pdf_files)} PDF files")
    
    if not resumes:
        print("❌ No PDF files found in data directory")
        return False
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(resumes)
    csv_path = os.path.join(base_path, 'Resume.csv')
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Created Resume.csv with {len(resumes)} entries")
    print(f"📄 File saved to: {csv_path}")
    
    # Show sample data
    print("\n📊 Sample data:")
    print(df.head(10))
    
    # Show category distribution
    print(f"\n📈 Category distribution:")
    category_counts = df['Category'].value_counts()
    for category, count in category_counts.items():
        print(f"   {category}: {count} files")
    
    return True

if __name__ == "__main__":
    print("=== Resume CSV Generator for ATS CV Search ===")
    if generate_resume_csv():
        print("🎉 Resume.csv generation completed successfully!")
    else:
        print("❌ Failed to generate Resume.csv")
