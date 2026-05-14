@echo off
REM ARP Assessment Platform - Run Locally (Windows)

echo.
echo 🚀 Starting ARP Assessment Platform locally...
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo ✅ Python found:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Create data and logs directories
if not exist "data\" mkdir data
if not exist "logs\" mkdir logs

REM Copy .env.example to .env if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating .env file...
    copy .env.example .env
)

REM Initialize database
echo 🗄️  Initializing database...
python -c "^
from src.backend.database import init_db, SessionLocal; ^
from src.backend.data_generator import generate_mock_data; ^
init_db(); ^
db = SessionLocal(); ^
generate_mock_data(db); ^
print('✅ Database initialized with mock data')"

echo.
echo 🎯 Starting services...
echo - Backend API: http://localhost:8000
echo - Dashboard: http://localhost:8501
echo.

REM Start backend in background
echo 🔧 Starting backend API...
start /B python -m src.backend.app

REM Wait a moment for backend to start
timeout /t 2 /nobreak

REM Start dashboard
echo 📊 Starting Streamlit dashboard...
streamlit run src/dashboard/app.py --server.port=8501

pause
