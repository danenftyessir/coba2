# fix_resumes_seeder.py
import mysql.connector
import os
import random
from datetime import datetime, date

def get_connection():
    """get database connection"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='danen332',
            database='kaggle_resumes',
            port=3306
        )
        return conn
    except Exception as e:
        print(f"connection error: {e}")
        return None

def check_current_data():
    """check current data in resumes table"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # check total records
        cursor.execute("SELECT COUNT(*) FROM resumes")
        total = cursor.fetchone()[0]
        print(f"total records: {total}")
        
        # check null values
        cursor.execute("SELECT COUNT(*) FROM resumes WHERE name IS NULL")
        null_names = cursor.fetchone()[0]
        print(f"records with null name: {null_names}")
        
        # sample data
        cursor.execute("SELECT id, category, name, phone FROM resumes LIMIT 5")
        samples = cursor.fetchall()
        print("sample records:")
        for sample in samples:
            print(f"  {sample}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"check data error: {e}")

def update_resumes_with_sample_data():
    """update existing resumes records dengan sample data realistic"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # sample names berdasarkan kategori pekerjaan
        sample_data = {
            'ACCOUNTANT': [
                ('Sari Wulandari', '0812-3456-7890', '1995-03-15', 'Jl. Sudirman No. 123, Jakarta'),
                ('Budi Hartono', '0813-4567-8901', '1992-07-20', 'Jl. Thamrin No. 45, Jakarta'),
                ('Maya Kusuma', '0814-5678-9012', '1994-11-08', 'Jl. Gatot Subroto No. 67, Jakarta'),
            ],
            'CHEF': [
                ('Farhan Nugraha', '0815-6789-0123', '1990-05-12', 'Jl. Kemang No. 89, Jakarta'),
                ('Rina Anggraini', '0816-7890-1234', '1993-09-25', 'Jl. Senopati No. 34, Jakarta'),
                ('Yoga Permana', '0817-8901-2345', '1991-12-03', 'Jl. Blok M No. 56, Jakarta'),
            ],
            'ADVOCATE': [
                ('Aland Saputra', '0818-9012-3456', '1988-04-18', 'Jl. Kuningan No. 78, Jakarta'),
                ('Dewi Maharani', '0819-0123-4567', '1992-08-30', 'Jl. Rasuna Said No. 90, Jakarta'),
                ('Reza Fauzi', '0821-1234-5678', '1989-01-14', 'Jl. HR Rasuna No. 12, Jakarta'),
            ],
            'ARTS': [
                ('Ariel Pratama', '0822-2345-6789', '1995-06-22', 'Jl. Kemang Raya No. 123, Jakarta'),
                ('Lila Permata', '0823-3456-7890', '1993-10-17', 'Jl. Pondok Indah No. 45, Jakarta'),
                ('Eka Putri', '0824-4567-8901', '1994-02-28', 'Jl. Lebak Bulus No. 67, Jakarta'),
            ],
            'DIGITAL-MEDIA': [
                ('Rizki Ramadhan', '0825-5678-9012', '1996-07-11', 'Jl. Kelapa Gading No. 89, Jakarta'),
                ('Nina Kusuma', '0826-6789-0123', '1994-12-05', 'Jl. Puri Indah No. 34, Jakarta'),
                ('Denny Wijaya', '0827-7890-1234', '1992-03-19', 'Jl. Cilandak No. 56, Jakarta'),
            ]
        }
        
        # get all resumes grouped by category
        cursor.execute("SELECT id, category FROM resumes ORDER BY category, id")
        all_resumes = cursor.fetchall()
        
        print(f"updating {len(all_resumes)} resume records...")
        
        updated_count = 0
        for resume_id, category in all_resumes:
            # get sample data for this category
            if category in sample_data:
                names_for_category = sample_data[category]
                # cycle through sample data
                sample_index = updated_count % len(names_for_category)
                name, phone, birthdate, address = names_for_category[sample_index]
            else:
                # default data for categories not in sample
                name = f"Candidate {resume_id}"
                phone = f"081{random.randint(10000000, 99999999)}"
                birthdate = f"199{random.randint(0, 9)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                address = f"Jl. Example No. {random.randint(1, 100)}, Jakarta"
            
            # update record
            update_sql = """
                UPDATE resumes 
                SET name = %s, phone = %s, birthdate = %s, address = %s 
                WHERE id = %s
            """
            
            cursor.execute(update_sql, (name, phone, birthdate, address, resume_id))
            updated_count += 1
            
            if updated_count % 100 == 0:
                print(f"  updated {updated_count} records...")
        
        conn.commit()
        print(f"successfully updated {updated_count} resume records")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"update error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def verify_updated_data():
    """verify that data has been updated correctly"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # check updated records
        cursor.execute("SELECT COUNT(*) FROM resumes WHERE name IS NOT NULL")
        non_null_names = cursor.fetchone()[0]
        print(f"records with non-null name: {non_null_names}")
        
        # sample updated data
        cursor.execute("SELECT id, category, name, phone, birthdate, address FROM resumes LIMIT 10")
        samples = cursor.fetchall()
        print("sample updated records:")
        for sample in samples:
            print(f"  {sample[0]} | {sample[1]} | {sample[2]} | {sample[3]}")
        
        # check by category
        cursor.execute("SELECT category, COUNT(*) FROM resumes GROUP BY category ORDER BY category")
        categories = cursor.fetchall()
        print("records by category:")
        for cat, count in categories:
            print(f"  {cat}: {count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"verify error: {e}")

def main():
    """main function untuk fix resumes data"""
    print("FIX RESUMES SEEDER")
    print("=" * 40)
    
    print("\n1. checking current data...")
    check_current_data()
    
    print("\n2. updating resumes with sample data...")
    if update_resumes_with_sample_data():
        print("update successful!")
    else:
        print("update failed!")
        return
    
    print("\n3. verifying updated data...")
    verify_updated_data()
    
    print("\ndatabase seeding completed!")
    print("now you can run: python main.py")

if __name__ == "__main__":
    main()