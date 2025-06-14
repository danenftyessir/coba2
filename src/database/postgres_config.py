# src/database/postgres_config.py
import psycopg2
from psycopg2 import Error
import os
from typing import Optional

class PostgreSQLConfig:
    """PostgreSQL database configuration with simplified Docker authentication"""
    
    def __init__(self):
        # Simplified configuration using Docker defaults
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'StimaSukses'),
            'database': os.getenv('DB_NAME', 'kaggle_resumes'),
            'port': int(os.getenv('DB_PORT', '5433')),  # Using Docker port 5433
        }
        print(f"PostgreSQL config: {self.config['user']}@{self.config['host']}:{self.config['port']}/{self.config['database']}")
        print(f"Using simplified Docker authentication (password: StimaSukses)")
    
    def get_connection(self) -> Optional[psycopg2.extensions.connection]:
        """Create connection to PostgreSQL database"""
        try:
            print(f"Connecting to PostgreSQL on port {self.config['port']}...")
            conn = psycopg2.connect(**self.config)
            print(f"PostgreSQL connection successful on port {self.config['port']}")
            return conn
        except psycopg2.Error as e:
            if "does not exist" in str(e):
                print(f"Database '{self.config['database']}' not found")
                try:
                    # Try to connect without database
                    temp_config = self.config.copy()
                    temp_config['database'] = 'postgres'  # Default PostgreSQL database
                    temp_conn = psycopg2.connect(**temp_config)
                    temp_conn.close()
                    print("PostgreSQL server is running but target database missing")
                    return None
                except:
                    pass
            print(f"PostgreSQL connection error: {e}")
        except Exception as e:
            print(f"Connection error: {e}")
        return None
    
    def test_connection(self) -> bool:
        """Test PostgreSQL database connection"""
        print("Testing PostgreSQL database connection...")
        
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                print(f"Database connected successfully!")
                print(f"PostgreSQL version: {version}")
                
                # Check if our database exists
                cursor.execute("SELECT datname FROM pg_database WHERE datname = %s", (self.config['database'],))
                db_exists = cursor.fetchone()
                
                if db_exists:
                    print(f"Database '{self.config['database']}' exists")
                    
                    # Check if resumes table exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'resumes'
                        )
                    """)
                    table_exists = cursor.fetchone()[0]
                    
                    if table_exists:
                        cursor.execute("SELECT COUNT(*) FROM resumes")
                        count = cursor.fetchone()[0]
                        print(f"Table 'resumes' found with {count} records")
                    else:
                        print("Table 'resumes' not found")
                else:
                    print(f"Database '{self.config['database']}' not found")
                    print("Run: docker-compose up -d")
                
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"Test query failed: {e}")
                if conn:
                    conn.close()
                return False
        else:
            print("PostgreSQL connection failed")
            self._print_troubleshooting_tips()
            return False
    
    def _print_troubleshooting_tips(self):
        """Print helpful troubleshooting tips for PostgreSQL"""
        print("\nTroubleshooting tips:")
        print("1. Start PostgreSQL with Docker:")
        print("   - docker-compose up -d")
        print("   - docker-compose ps (check status)")
        print("2. Check PostgreSQL container logs:")
        print("   - docker-compose logs postgres")
        print("3. Verify container is running:")
        print("   - docker ps | grep postgres")
        print("4. Test connection manually:")
        print("   - docker exec -it ats_postgres psql -U postgres -d kaggle_resumes")
        print("5. Common PostgreSQL ports:")
        print("   - 5433 (Docker mapped port)")
        print("6. Reset database:")
        print("   - docker-compose down -v && docker-compose up -d")
    
    def initialize_database(self) -> bool:
        """Initialize database tables if they don't exist"""
        print("Initializing PostgreSQL database...")
        
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Check if resumes table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'resumes'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print("Table 'resumes' not found")
                print("Tables should be created automatically by Docker init scripts")
                return False
            else:
                # Count records
                cursor.execute("SELECT COUNT(*) FROM resumes")
                count = cursor.fetchone()[0]
                print(f"Table 'resumes' found with {count} records")
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Error as e:
            print(f"Database initialization error: {e}")
            if conn:
                conn.close()
            return False

def test_config():
    """Test PostgreSQL database configuration"""
    print("Testing PostgreSQL database configuration...")
    config = PostgreSQLConfig()
    
    if config.test_connection():
        print("PostgreSQL database configuration is working!")
        return True
    else:
        print("PostgreSQL database configuration failed!")
        return False

if __name__ == "__main__":
    test_config()
