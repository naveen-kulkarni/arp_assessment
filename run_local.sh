#!/bin/bash

# ARP Assessment Platform - Run Locally

echo "🚀 Starting ARP Assessment Platform locally..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create data and logs directories
mkdir -p data logs

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
from src.backend.database import init_db, SessionLocal
from src.backend.data_generator import generate_mock_data

init_db()
db = SessionLocal()
generate_mock_data(db)
print('✅ Database initialized with mock data')
"

echo ""
echo "🎯 Starting services..."
echo "- Backend API: http://localhost:8000"
echo "- Dashboard: http://localhost:8501"
echo ""

# Start backend in background
echo "🔧 Starting backend API..."
python3 -m src.backend.app &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start dashboard
echo "📊 Starting Streamlit dashboard..."
streamlit run src/dashboard/app.py --server.port=8501

# Cleanup
trap "kill $BACKEND_PID" EXIT
