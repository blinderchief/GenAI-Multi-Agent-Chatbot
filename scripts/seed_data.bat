@echo off
REM Seed Qdrant Knowledge Base using backend virtual environment

REM Change to project root
cd /d "%~dp0\.."

echo ========================================
echo Seeding Qdrant Knowledge Base
echo ========================================
echo.

REM Activate backend virtual environment and run seed
cd backend
call .venv\Scripts\activate
cd ..
python scripts\seed_data.py
call deactivate

echo.
pause
