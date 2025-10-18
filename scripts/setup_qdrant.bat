@echo off
REM Setup Qdrant Collections using backend virtual environment

REM Change to project root
cd /d "%~dp0\.."

echo ========================================
echo Setting up Qdrant Collections
echo ========================================
echo.

REM Activate backend virtual environment and run setup
cd backend
call .venv\Scripts\activate
cd ..
python scripts\setup_qdrant.py
call deactivate

echo.
pause
