# src/database/config.py
import mysql.connector
from mysql.connector import Error
import os
from typing import Optional

class DatabaseConfig:
    """konfigurasi database mysql dengan connection handling yang diperbaiki"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'danen332'),
            'database': os.getenv('DB_NAME', 'kaggle_resumes'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'connection_timeout': 10,
            'autocommit': True,
            'charset': 'utf8mb4',
            'use_unicode': True,
            'raise_on_warnings': False
        }
        print(f"database config: {self.config['user']}@{self.config['host']}:{self.config['port']}/{self.config['database']}")
    
    def get_connection(self) -> Optional[mysql.connector.MySQLConnection]:
        """buat koneksi ke database dengan connection handling yang diperbaiki"""
        try:
            print(f"connecting to mysql on port {self.config['port']}...")
            conn = mysql.connector.connect(**self.config)
            if conn.is_connected():
                print(f"database connection successful on port {self.config['port']}")
                return conn
        except mysql.connector.Error as e:
            if "Unknown database" in str(e):
                print(f"database '{self.config['database']}' not found")
                try:
                    # try to connect without database
                    temp_config = self.config.copy()
                    del temp_config['database']
                    temp_conn = mysql.connector.connect(**temp_config)
                    if temp_conn.is_connected():
                        temp_conn.close()
                        print("mysql server is running but database missing")
                        return None
                except:
                    pass
            print(f"mysql connection error: {e}")
        except Exception as e:
            print(f"connection error: {e}")
        return None
    
    def test_connection(self) -> bool:
        """test koneksi database dengan handling yang diperbaiki"""
        print("testing database connection...")
        
        conn = self.get_connection()
        if conn and conn.is_connected():
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                print(f"database connected successfully!")
                print(f"mysql version: {version}")
                
                # check if our database exists
                cursor.execute("SHOW DATABASES")
                databases = [db[0] for db in cursor.fetchall()]
                
                if self.config['database'] in databases:
                    print(f"database '{self.config['database']}' exists")
                else:
                    print(f"database '{self.config['database']}' not found")
                    print(f"run: python setup_database.py")
                
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"test query failed: {e}")
                if conn:
                    conn.close()
                return False
        else:
            print("database connection failed")
            self._print_troubleshooting_tips()
            return False
    
    def _print_troubleshooting_tips(self):
        """print helpful troubleshooting tips"""
        print("\ntroubleshooting tips:")
        print("1. start mysql service:")
        print("   - xampp control panel → start mysql")
        print("   - services.msc → start mysql service")
        print("   - cmd (admin): net start mysql")
        print("2. check mysql credentials:")
        print("   - default user: root")
        print("   - default password: (empty) or 'root'")
        print("3. common mysql ports:")
        print("   - 3306 (default)")
        print("   - 3307 (xampp alternative)")
        print("4. verify mysql installation:")
        print("   - mysql -u root -p")
        print("5. run auto-detection:")
        print("   - python detect_mysql_port.py")
    
    def initialize_database(self) -> bool:
        """initialize database tables jika belum ada"""
        print("initializing database...")
        
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # use database
            cursor.execute(f"USE {self.config['database']}")
            
            # check if resumes table exists
            cursor.execute("SHOW TABLES LIKE 'resumes'")
            if not cursor.fetchone():
                print("table 'resumes' not found")
                print("please run setup_database.py first")
                return False
            else:
                # count records
                cursor.execute("SELECT COUNT(*) FROM resumes")
                count = cursor.fetchone()[0]
                print(f"table 'resumes' found with {count} records")
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Error as e:
            print(f"database initialization error: {e}")
            return False

def test_config():
    """test database configuration"""
    print("testing database configuration...")
    config = DatabaseConfig()
    
    if config.test_connection():
        print("database configuration is working!")
        return True
    else:
        print("database configuration failed!")
        return False

if __name__ == "__main__":
    test_config()