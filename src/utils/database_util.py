# src/utils/database_util.py
"""
Database utility for ATS CV Search with PostgreSQL Docker support
Provides simplified connection management with fallback capabilities
"""

import psycopg2
from psycopg2 import Error
import os
from typing import Optional

class DatabaseUtil:
    """Database utility with simplified PostgreSQL Docker authentication"""
    
    # PostgreSQL Docker configuration (simplified)
    POSTGRES_CONFIG = {
        'host': 'localhost',
        'user': 'postgres', 
        'password': 'StimaSukses',
        'database': 'kaggle_resumes',
        'port': 5433
    }
    
    def __init__(self):
        self.current_db_type = None
        self.current_config = None
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize database connection using PostgreSQL Docker"""
        if self.try_postgresql_connection():
            self.current_db_type = "PostgreSQL"
            self.current_config = self.POSTGRES_CONFIG.copy()
            print("✅ Using PostgreSQL database (Docker)")
            return
        
        # No database available
        print("❌ PostgreSQL Docker container is not available!")
        print("Please start the database container:")
        print("  ./start_postgres.sh")
        print("  or")
        print("  docker-compose up -d")
    
    def try_postgresql_connection(self):
        """Test PostgreSQL Docker connection"""
        try:
            print("🔄 Testing PostgreSQL Docker connection...")
            conn = psycopg2.connect(**self.POSTGRES_CONFIG)
            
            if conn and not conn.closed:
                conn.close()
                print("✅ PostgreSQL Docker connection successful")
                return True
                
        except Error as e:
            print(f"⚠️  PostgreSQL connection failed: {e}")
            print("💡 Make sure Docker PostgreSQL is running:")
            print("   docker-compose up -d")
            print("   docker-compose ps")
            return False
        
        return False
    
    def get_connection(self) -> Optional[psycopg2.extensions.connection]:
        """Get database connection"""
        if not self.current_config:
            raise Exception("No database connection available. Please check PostgreSQL Docker container.")
        
        try:
            conn = psycopg2.connect(**self.current_config)
            print(f"✅ Database connection successful ({self.current_db_type})")
            return conn
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            print("Please check:")
            print("1. PostgreSQL Docker container is running: docker-compose ps")
            print("2. Database 'kaggle_resumes' exists (should be auto-created)")
            print("3. Port 5432 is accessible")
            print("4. Check container logs: docker-compose logs postgres")
            print("5. Restart container: docker-compose restart postgres")
            
            raise Exception(f"Unable to connect to database: {e}")
    
    def close_connection(self, connection):
        """Close database connection"""
        if connection and not connection.closed:
            try:
                connection.close()
                print("✅ Database connection closed")
            except Error as e:
                print(f"❌ Error closing connection: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = self.get_connection()
            if conn and not conn.closed:
                # Test with a simple query
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                print(f"✅ Database connection test passed ({self.current_db_type})")
                print(f"PostgreSQL version: {version}")
                
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
                    print(f"📊 Table 'resumes' found with {count} records")
                else:
                    print("⚠️  Table 'resumes' not found. Run data migration:")
                    print("   uv run setup_postgres.py")
                
                cursor.close()
                conn.close()
                return True
            return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def get_current_database_type(self):
        """Get current database type"""
        return self.current_db_type
    
    def is_using_postgresql(self):
        """Check if using PostgreSQL"""
        return self.current_db_type == "PostgreSQL"

def main():
    """Test database connectivity"""
    print("Testing ATS CV Search Database Connection...")
    db_util = DatabaseUtil()
    
    if db_util.test_connection():
        print("🎉 Database is ready for ATS CV Search!")
        print(f"Using: {db_util.get_current_database_type()}")
    else:
        print("❌ Database connection failed. Please check setup.")
        print("\nTo fix:")
        print("1. Start PostgreSQL: ./start_postgres.sh")
        print("2. Run migration: uv run setup_postgres.py")
        print("3. Test again: uv run src/utils/database_util.py")

if __name__ == "__main__":
    main()
