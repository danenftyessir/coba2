#!/usr/bin/env python3
"""
PostgreSQL Data Migration Script for ATS CV Search
Migrates Resume.csv data to PostgreSQL database running in Docker
"""

import psycopg2
from psycopg2 import Error
import pandas as pd
import os
import sys
from pathlib import Path

# PostgreSQL Configuration for Docker (simplified)
POSTGRES_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'StimaSukses',
    'database': 'kaggle_resumes',
    'port': 5433
}

def create_connection():
    """Create connection to PostgreSQL server"""
    conn = None
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        print(f"✅ Successfully connected to PostgreSQL database '{POSTGRES_CONFIG['database']}'")
        return conn
    except Error as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        return None

def import_data_to_db(conn):
    """Import data from Resume.csv to PostgreSQL database"""
    try:
        # Find Resume.csv file - should be in project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent  # Go up from src to project root
        csv_path = project_root / "Resume.csv"
        data_dir = project_root / "data"
        
        if not csv_path.exists():
            print(f"❌ Resume.csv not found at: {csv_path}")
            print("Run the CSV generation script first: uv run generate_csv.py")
            return False
        
        print(f"📄 Reading Resume.csv from: {csv_path}")
        resumes_df = pd.read_csv(csv_path)
        cursor = conn.cursor()

        # Use ON CONFLICT for PostgreSQL (equivalent to INSERT IGNORE in MySQL)
        sql = '''
            INSERT INTO resumes (id, category, file_path, name, phone, birthdate, address)
            VALUES (%s, %s, %s, NULL, NULL, NULL, NULL)
            ON CONFLICT (id) DO NOTHING
        '''

        count = 0
        for index, row in resumes_df.iterrows():
            resume_id = str(row['ID'])
            category = row['Category']
            # Build file path relative to data directory
            file_path = str(data_dir / category / f"{resume_id}.pdf")

            cursor.execute(sql, (resume_id, category, file_path))
            count += 1
            
            if count % 100 == 0:
                print(f"   Processed {count} records...")

        conn.commit()
        print(f"✅ Successfully imported {count} records to PostgreSQL database.")
        
        # Check actual inserted count
        cursor.execute("SELECT COUNT(*) FROM resumes")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total records in database: {total_count}")
        
        # Show summary by category
        cursor.execute("SELECT category, COUNT(*) FROM resumes GROUP BY category ORDER BY COUNT(*) DESC")
        categories = cursor.fetchall()
        print(f"\n📋 Records by category:")
        for category, count in categories[:10]:  # Show top 10
            print(f"   {category}: {count}")
        if len(categories) > 10:
            print(f"   ... and {len(categories) - 10} more categories")

        return True

    except FileNotFoundError:
        print(f"❌ Error: Resume.csv file not found.")
        return False
    except Error as e:
        print(f"❌ Failed to import data: {e}")
        return False

def verify_data(conn):
    """Verify imported data and check file paths"""
    try:
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM resumes")
        total = cursor.fetchone()[0]
        print(f"\n🔍 Verification Results:")
        print(f"   Total records: {total}")
        
        # Check a few sample file paths
        cursor.execute("SELECT id, category, file_path FROM resumes LIMIT 5")
        samples = cursor.fetchall()
        print(f"\n📋 Sample records with file paths:")
        for sample in samples:
            resume_id, category, file_path = sample
            file_exists = "✅" if os.path.exists(file_path) else "❌"
            print(f"   {file_exists} {resume_id} ({category}): {file_path}")
            
    except Error as e:
        print(f"❌ Error verifying data: {e}")

def main():
    """Main function to run the migration process"""
    print("=== ATS CV Search - PostgreSQL Data Migration ===")
    print(f"🔗 Target: {POSTGRES_CONFIG['user']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}")
    
    # Check if PostgreSQL is running
    conn = create_connection()
    if not conn:
        print("\n💡 Make sure PostgreSQL is running:")
        print("   cd /home/nathangalung/documents/kuliah/sem6/stima/tubes/Tubes3_StimaSukses")
        print("   docker-compose up -d")
        print("   docker-compose ps")
        return
    
    try:
        if import_data_to_db(conn):
            verify_data(conn)
            print("\n🎉 Migration completed successfully!")
            print("The ATS application is now ready to use with PostgreSQL backend.")
        else:
            print("\n❌ Migration failed!")
        
    finally:
        conn.close()
        print("🔒 PostgreSQL connection closed.")

if __name__ == '__main__':
    main()
