#!/usr/bin/env python3
"""
PostgreSQL Data Migration Script for ATS CV Search
Migrates data from CSV to PostgreSQL database running in Docker
"""

import psycopg2
from psycopg2 import Error
import pandas as pd
import os
import sys

# PostgreSQL Configuration for Docker (Simplified Authentication)
POSTGRES_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'StimaSukses',
    'database': 'kaggle_resumes',
    'port': 5433
}

# Paths (updated for current project structure)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_PATH, 'Resume', 'Resume.csv') 
PDF_FOLDER_PATH = os.path.join(BASE_PATH, 'data')

def create_connection():
    """Create connection to PostgreSQL server"""
    conn = None
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        print(f"Successfully connected to PostgreSQL database '{POSTGRES_CONFIG['database']}'")
        return conn
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def check_and_create_table(conn):
    """Check if resumes table exists and create if needed"""
    try:
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'resumes'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Creating 'resumes' table...")
            cursor.execute('''
                CREATE TABLE resumes (
                    id VARCHAR(255) PRIMARY KEY,
                    category VARCHAR(255),
                    file_path TEXT,
                    name TEXT,
                    phone VARCHAR(50),
                    birthdate DATE,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute("CREATE INDEX idx_resumes_category ON resumes(category)")
            cursor.execute("CREATE INDEX idx_resumes_name ON resumes(name)")
            
            conn.commit()
            print("Table 'resumes' created successfully.")
        else:
            print("Table 'resumes' already exists.")
            
    except Error as e:
        print(f"Failed to create table: {e}")

def import_data_to_db(conn, csv_path, pdf_folder_path):
    """Import data from CSV to PostgreSQL database"""
    try:
        # Check if CSV file exists
        if not os.path.exists(csv_path):
            print(f"CSV file not found at: {csv_path}")
            print("Looking for Resume.csv in current directory...")
            
            # Try to find Resume.csv in current directory or parent directories
            current_dir = os.getcwd()
            possible_paths = [
                os.path.join(current_dir, 'Resume.csv'),
                os.path.join(current_dir, 'Resume', 'Resume.csv'),
                os.path.join(os.path.dirname(current_dir), 'Resume.csv'),
                os.path.join(os.path.dirname(current_dir), 'Resume', 'Resume.csv'),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    csv_path = path
                    print(f"Found CSV file at: {csv_path}")
                    break
            else:
                print("Resume.csv not found. Please ensure the file exists.")
                return
        
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
            file_path = os.path.join(pdf_folder_path, category, f"{resume_id}.pdf")

            cursor.execute(sql, (resume_id, category, file_path))
            count += 1

        conn.commit()
        print(f"Successfully imported {count} records to PostgreSQL database.")
        
        # Check actual inserted count
        cursor.execute("SELECT COUNT(*) FROM resumes")
        total_count = cursor.fetchone()[0]
        print(f"Total records in database: {total_count}")

    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_path}'.")
    except Error as e:
        print(f"Failed to import data: {e}")

def verify_data(conn):
    """Verify imported data"""
    try:
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM resumes")
        total = cursor.fetchone()[0]
        print(f"\nVerification Results:")
        print(f"Total records: {total}")
        
        # Count by category
        cursor.execute("SELECT category, COUNT(*) FROM resumes GROUP BY category ORDER BY category")
        categories = cursor.fetchall()
        print(f"Records by category:")
        for category, count in categories:
            print(f"  {category}: {count}")
        
        # Show sample records
        cursor.execute("SELECT id, category, file_path FROM resumes LIMIT 5")
        samples = cursor.fetchall()
        print(f"\nSample records:")
        for sample in samples:
            print(f"  {sample}")
            
    except Error as e:
        print(f"Error verifying data: {e}")

def main():
    """Main function to run the migration process"""
    print("=== PostgreSQL Data Migration for ATS CV Search ===")
    print(f"Target: {POSTGRES_CONFIG['user']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}")
    
    # Check if PostgreSQL is running
    conn = create_connection()
    if not conn:
        print("\nMake sure PostgreSQL is running:")
        print("  docker-compose up -d")
        print("  docker-compose ps")
        return
    
    try:
        check_and_create_table(conn)
        import_data_to_db(conn, CSV_PATH, PDF_FOLDER_PATH)
        verify_data(conn)
        
        print("\n✅ Migration completed successfully!")
        print("You can now run the ATS application with PostgreSQL backend.")
        
    finally:
        conn.close()
        print("PostgreSQL connection closed.")

if __name__ == '__main__':
    main()
