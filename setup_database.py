import mysql.connector
from mysql.connector import Error
import pandas as pd
import os

# --- Konfigurasi ---
# GANTI DENGAN DETAIL KONEKSI MYSQL ANDA
MYSQL_CONFIG = {
    'host': 'localhost',        # atau alamat IP server MySQL Anda
    'user': 'root',             # username MySQL Anda
    'password': 'danen332', # password MySQL Anda
    'database': 'kaggle_resumes' # Nama database yang Anda buat di Langkah 1
}

# Path ke file dan folder dataset
BASE_PATH = r'C:\Users\DANENDRA\OneDrive\Documents\ITB\SEMESTER 4\IF2211 Strategi Algoritma\coba2'
CSV_PATH = os.path.join(BASE_PATH, 'Resume', 'Resume.csv')
PDF_FOLDER_PATH = os.path.join(BASE_PATH, 'data')


def create_connection():
    """Membuat koneksi ke server MySQL."""
    conn = None
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            print(f"Berhasil terhubung ke database MySQL '{MYSQL_CONFIG['database']}'")
        return conn
    except Error as e:
        print(f"Error saat koneksi ke MySQL: {e}")
        return None

def create_table(conn):
    """Membuat tabel 'resumes' di MySQL jika belum ada."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id VARCHAR(255) PRIMARY KEY,
                category VARCHAR(255),
                file_path TEXT,
                name TEXT,
                phone VARCHAR(50),
                birthdate DATE,
                address TEXT
            )
        ''')
        print("Tabel 'resumes' berhasil dibuat atau sudah ada.")
    except Error as e:
        print(f"Gagal membuat tabel: {e}")

def import_data_to_db(conn, csv_path, pdf_folder_path):
    """Membaca data CSV dan memasukkannya ke database MySQL."""
    try:
        resumes_df = pd.read_csv(csv_path)
        cursor = conn.cursor()

        sql = '''
            INSERT IGNORE INTO resumes (id, category, file_path, name, phone, birthdate, address)
            VALUES (%s, %s, %s, NULL, NULL, NULL, NULL)
        '''

        count = 0
        for index, row in resumes_df.iterrows():
            resume_id = str(row['ID'])
            category = row['Category']
            file_path = os.path.join(pdf_folder_path, category, f"{resume_id}.pdf")

            # Menggunakan IGNORE agar tidak error jika ID sudah ada
            cursor.execute(sql, (resume_id, category, file_path))
            count += 1

        conn.commit()
        print(f"{cursor.rowcount} data berhasil diimpor ke database.")

    except FileNotFoundError:
        print(f"Error: File CSV tidak ditemukan di '{csv_path}'.")
    except Error as e:
        print(f"Gagal memasukkan data: {e}")

def main():
    """Fungsi utama untuk menjalankan proses."""
    conn = create_connection()
    if conn:
        create_table(conn)
        import_data_to_db(conn, CSV_PATH, PDF_FOLDER_PATH)
        conn.close()
        print("Koneksi ke MySQL ditutup.")

if __name__ == '__main__':
    main()