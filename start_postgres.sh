#!/bin/bash

# PostgreSQL Docker Setup Script for ATS CV Search
# This script sets up PostgreSQL in Docker and prepares the environment

echo "=== ATS CV Search PostgreSQL Setup ==="

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker."
    exit 1
fi

echo "✅ Docker is available"

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available"
    exit 1
fi

echo "✅ Docker Compose is available"

# Stop existing containers if running
echo "🔄 Stopping existing containers..."
$COMPOSE_CMD down

# Start PostgreSQL container
echo "🚀 Starting PostgreSQL container..."
$COMPOSE_CMD up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec ats_postgres pg_isready -U postgres -d kaggle_resumes &> /dev/null; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start after 30 seconds"
        echo "Check logs with: $COMPOSE_CMD logs postgres"
        exit 1
    fi
    
    echo "   Attempt $i/30..."
    sleep 1
done

# Check container status
echo "📊 Container status:"
$COMPOSE_CMD ps

# Show connection info
echo ""
echo "🔗 PostgreSQL Connection Info:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: kaggle_resumes"
echo "   Username: postgres"
echo "   Password: StimaSukses"

# Install Python dependencies if needed
if [ -f "requirements.txt" ]; then
    echo ""
    echo "📦 Installing Python dependencies with uv..."
    if command -v uv &> /dev/null; then
        echo "Using uv package manager..."
        uv pip install psycopg2-binary pandas
        echo "✅ Dependencies installed with uv"
    else
        echo "❌ uv not found. Please install uv first:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "   source ~/.bashrc"
        echo ""
        echo "Or install dependencies manually:"
        echo "   pip install psycopg2-binary pandas"
    fi
fi

echo ""
echo "🎉 PostgreSQL setup completed!"
echo ""
echo "Next steps:"
echo "1. Run data migration: uv run setup_postgres.py"
echo "2. Test connection: uv run src/database/postgres_config.py"
echo "3. Start application: uv run src/main.py"
echo ""
echo "Useful commands:"
echo "   🔍 Check logs: $COMPOSE_CMD logs postgres"
echo "   🗄️  Connect to DB: docker exec -it ats_postgres psql -U postgres -d kaggle_resumes"
echo "   🛑 Stop: $COMPOSE_CMD down"
echo "   🔄 Restart: $COMPOSE_CMD restart postgres"
