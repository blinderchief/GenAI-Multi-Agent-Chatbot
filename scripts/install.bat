@echo off
REM Installation script for Aria Chatbot
REM Sets up virtual environments and installs dependencies using uv

REM Change to project root directory
cd /d "%~dp0\.."

echo ========================================
echo Aria Chatbot - Installation Script
echo ========================================
echo.

REM Check Python version
echo [1/7] Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)
python --version
echo.

REM Check/Install uv
echo [2/7] Checking uv installation...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo uv not found. Installing uv...
    pip install uv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install uv
        pause
        exit /b 1
    )
    echo ✓ uv installed successfully
) else (
    uv --version
    echo ✓ uv is already installed
)
echo.

REM Create .env file if it doesn't exist
echo [3/7] Setting up environment file...
if not exist ".env" (
    copy ".env.example" ".env"
    echo ✓ Created .env file from .env.example
    echo IMPORTANT: Edit .env file and add your API keys!
) else (
    echo .env file already exists
)
echo.

REM Setup Backend
echo [4/7] Setting up Backend...
cd backend
if not exist ".venv" (
    echo Creating virtual environment with uv...
    uv venv
    echo ✓ Virtual environment created
) else (
    echo Virtual environment already exists
)

echo Installing backend dependencies with uv (fast!)...
call .venv\Scripts\activate
uv pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
call deactivate
echo ✓ Backend dependencies installed
cd ..
echo.

REM Setup Frontend
echo [5/7] Setting up Frontend...
cd frontend
if not exist ".venv" (
    echo Creating virtual environment with uv...
    uv venv
    echo ✓ Virtual environment created
) else (
    echo Virtual environment already exists
)

echo Installing frontend dependencies with uv (fast!)...
call .venv\Scripts\activate
uv pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
call deactivate
echo ✓ Frontend dependencies installed
cd ..
echo.

REM Install Playwright browsers
echo [6/7] Installing Playwright browsers...
cd backend
call .venv\Scripts\activate
python -m playwright install chromium
call deactivate
cd ..
echo ✓ Playwright browsers installed
echo.

REM Create necessary directories
echo [7/7] Creating directories...
if not exist "logs" mkdir logs
if not exist "data\seed" mkdir data\seed
if not exist "data\temp" mkdir data\temp
echo ✓ Directories created
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Start Qdrant (choose one):
echo    a. Docker: docker run -p 6333:6333 qdrant/qdrant
echo    b. Cloud: Sign up at https://cloud.qdrant.io/ and update .env
echo.
echo 2. Setup Qdrant collections:
echo    cd scripts
echo    python setup_qdrant.py
echo.
echo 3. Seed the knowledge base:
echo    python seed_data.py
echo.
echo 4. Start the application:
echo    run_all.bat
echo.
echo IMPORTANT: Don't forget to edit .env and add your API keys!
echo.
echo NOTE: This installation uses 'uv' for 10x faster package installation!
echo.
pause
