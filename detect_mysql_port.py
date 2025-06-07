import subprocess
import socket
import mysql.connector

def find_mysql_ports():
    """cari port mysql yang sedang listening"""
    print("🔍 Detecting MySQL ports...")
    
    possible_ports = []
    
    # method 1: netstat
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'LISTENING' in line and '127.0.0.1:' in line:
                # extract port
                parts = line.split()
                for part in parts:
                    if '127.0.0.1:' in part:
                        port = part.split(':')[-1]
                        if port.isdigit() and int(port) > 1000:
                            possible_ports.append(int(port))
        
        print(f"📋 Found listening ports: {sorted(set(possible_ports))}")
    except Exception as e:
        print(f"⚠️ netstat failed: {e}")
    
    # method 2: common mysql ports
    common_ports = [3306, 3307, 3308, 3309, 33060, 33061]
    
    mysql_ports = []
    
    for port in set(possible_ports + common_ports):
        if test_port_mysql(port):
            mysql_ports.append(port)
    
    return mysql_ports

def test_port_mysql(port):
    """test apakah port ini mysql"""
    try:
        # test socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is open")
            
            # test mysql connection
            try:
                config = {
                    'host': 'localhost',
                    'user': 'root',
                    'password': 'danen332',
                    'port': port,
                    'connection_timeout': 3
                }
                
                conn = mysql.connector.connect(**config)
                if conn.is_connected():
                    cursor = conn.cursor()
                    cursor.execute("SELECT VERSION()")
                    version = cursor.fetchone()[0]
                    cursor.close()
                    conn.close()
                    print(f"🎯 Port {port} is MySQL! Version: {version}")
                    return True
                    
            except mysql.connector.Error as e:
                print(f"⚠️ Port {port} not MySQL: {e}")
            except Exception as e:
                print(f"⚠️ Port {port} test failed: {e}")
        
        return False
        
    except Exception as e:
        return False

def update_database_config(correct_port):
    """update konfigurasi database dengan port yang benar"""
    config_content = f'''import mysql.connector
import os
from mysql.connector import Error
from typing import Optional
import time

class DatabaseConfig:
    """konfigurasi dan koneksi database dengan port yang benar"""
    
    def __init__(self):
        # config dengan port yang terdeteksi: {correct_port}
        self.config = {{
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'ats_cv_search'),
            'port': int(os.getenv('DB_PORT', '{correct_port}')),  # port yang benar
            'connection_timeout': 10,
            'autocommit': True,
            'raise_on_warnings': True
        }}
        self.connection = None
    
    def get_connection(self):
        """ambil koneksi database dengan port yang benar"""
        try:
            print(f"🔗 connecting to mysql://{{self.config['user']}}@{{self.config['host']}}:{{self.config['port']}}/{{self.config['database']}}")
            
            start_time = time.time()
            self.connection = mysql.connector.connect(**self.config)
            
            if self.connection and self.connection.is_connected():
                elapsed = time.time() - start_time
                print(f"✅ database connected in {{elapsed:.2f}}s")
                return self.connection
            else:
                raise Error("connection failed but no exception thrown")
            
        except mysql.connector.errors.DatabaseError as e:
            if "Unknown database" in str(e):
                print(f"⚠️ database '{{self.config['database']}}' not found, trying to create...")
                if self._create_database():
                    print("🔄 retrying connection...")
                    try:
                        self.connection = mysql.connector.connect(**self.config)
                        if self.connection and self.connection.is_connected():
                            print("✅ database created and connected")
                            return self.connection
                    except Exception as retry_e:
                        print(f"❌ retry connection failed: {{retry_e}}")
                        raise retry_e
                else:
                    raise e
            else:
                raise e
        
        except mysql.connector.errors.InterfaceError as e:
            print(f"❌ database interface error: {{e}}")
            print("💡 check if mysql server is running")
            raise e
        
        except mysql.connector.errors.ProgrammingError as e:
            print(f"❌ database programming error: {{e}}")
            print("💡 check database credentials")
            raise e
            
        except Exception as e:
            print(f"❌ unexpected database error: {{e}}")
            raise e
    
    def _create_database(self) -> bool:
        """buat database jika belum ada"""
        try:
            print(f"🔨 creating database '{{self.config['database']}}'...")
            
            temp_config = self.config.copy()
            temp_config.pop('database')
            
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            
            db_name = self.config['database']
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{{db_name}}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ database '{{db_name}}' created successfully")
            
            cursor.close()
            conn.close()
            return True
            
        except Error as e:
            print(f"❌ error creating database: {{e}}")
            return False
    
    def init_tables(self):
        """inisialisasi tabel database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            print("🔨 creating tables...")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applicant_profile (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    address TEXT,
                    linkedin_url VARCHAR(255),
                    date_of_birth DATE,
                    skills TEXT,
                    work_experience TEXT,
                    education_history TEXT,
                    summary_overview TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS application_detail (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    applicant_id INT NOT NULL,
                    cv_path VARCHAR(255) NOT NULL,
                    application_date DATE DEFAULT (CURDATE()),
                    job_position VARCHAR(255),
                    category VARCHAR(100),
                    raw_text LONGTEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (applicant_id) REFERENCES applicant_profile(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            conn.commit()
            cursor.close()
            print("✅ tables created successfully")
            
        except Error as e:
            print(f"❌ error creating tables: {{e}}")
            raise e
    
    def close_connection(self):
        """tutup koneksi database"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("✅ database connection closed")
        except Exception as e:
            print(f"⚠️ error closing connection: {{e}}")
'''
    
    # write ke file
    with open('src/database/config.py', 'w') as f:
        f.write(config_content)
    
    print(f"✅ Updated config.py with port {correct_port}")

def main():
    print("🎯 MySQL Port Detection")
    print("=" * 30)
    
    mysql_ports = find_mysql_ports()
    
    if mysql_ports:
        print(f"\n🎉 Found MySQL on ports: {mysql_ports}")
        
        # gunakan port pertama yang ditemukan
        correct_port = mysql_ports[0]
        print(f"🔧 Using port: {correct_port}")
        
        # update config
        update_database_config(correct_port)
        
        print(f"\n✅ Configuration updated!")
        print(f"💡 Now run: python main.py")
        
        return correct_port
    else:
        print("\n❌ No MySQL found on any port!")
        print("💡 Solutions:")
        print("   1. Start MySQL service")
        print("   2. Install MySQL/XAMPP")
        print("   3. Check if MySQL is running")
        return None

if __name__ == "__main__":
    main()
    input("\nPress Enter to continue...")