#!/bin/bash
# Database initialization script for ATS CV Search PostgreSQL Docker container

echo "========================================"
echo "ATS CV Search Database Initialization"
echo "========================================"

# All setup is handled by the SQL script
# This ensures the database is properly configured with the simplified authentication

echo "Setting up database schema..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Ensure postgres user has all necessary permissions
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
    GRANT ALL ON SCHEMA public TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $POSTGRES_USER;

    -- Create additional indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_resumes_id ON resumes(id);
    CREATE INDEX IF NOT EXISTS idx_resumes_category_name ON resumes(category, name);
EOSQL

echo "Database initialization completed successfully!"
echo "Database ready for ATS CV Search application!"
