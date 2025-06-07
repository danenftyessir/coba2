# src/database/config.py
import mysql.connector
from mysql.connector import Error

class DatabaseConfig:
    """konfigurasi database mysql"""
    
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'danen332',
            'database': 'kaggle_resumes',
            'port': 3306
        }
    
    def get_connection(self):
        """buat koneksi ke database"""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            print(f"error koneksi database: {e}")
            return None
    
    def test_connection(self):
        """test koneksi database"""
        conn = self.get_connection()
        if conn and conn.is_connected():
            conn.close()
            return True
        return False