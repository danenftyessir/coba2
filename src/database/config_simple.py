import psycopg2
import os

class DatabaseConfig:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'postgres', 
            'password': 'StimaSukses',
            'database': 'kaggle_resumes',
            'port': 5433
        }
    
    def get_connection(self):
        try:
            return psycopg2.connect(**self.config)
        except:
            return None
    
    def test_connection(self):
        conn = self.get_connection()
        if conn:
            conn.close()
            return True
        return False
