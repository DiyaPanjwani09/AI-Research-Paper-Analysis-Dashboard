#!/bin/bash
# AI-powered Research Paper Intelligence Engine - Setup Script

set -e

echo "=========================================="
echo "AI-powered Research Paper Intelligence Engine Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is required but not installed."
    exit 1
fi

echo "Step 1: Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
pip install --upgrade pip
pip install -r ../requirements.txt

# Create necessary directories
mkdir -p uploads vector_db datasets/processed

echo "Step 2: Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

echo "Step 3: Setting up database..."
cd ..

# Check if PostgreSQL is running
if command -v psql &> /dev/null; then
    echo "Please ensure PostgreSQL is running and create the database:"
    echo "  createdb research_db"
    echo "  psql -c \"CREATE USER user WITH PASSWORD 'password';\""
    echo "  psql -c \"GRANT ALL PRIVILEGES ON DATABASE research_db TO user;\""
else
    echo "PostgreSQL is not installed. Please install it or use Docker."
fi

echo "Step 4: Preprocessing datasets..."
cd datasets
python preprocessing.py

echo "Step 5: Initializing vector database..."
cd ../backend
python -c "from utils.vector_db import vector_db; vector_db.initialize_with_arxiv('../datasets/processed/arxiv_processed.csv')"

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the backend:"
echo "  cd backend && python main.py"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm start"
echo ""
echo "Or use Docker:"
echo "  docker-compose up --build"
