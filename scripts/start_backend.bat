@echo off
REM Start Backend Server

REM Change to project root
cd /d "%~dp0\.."

echo Starting Aria Backend...
cd backend
call .venv\Scripts\activate
python main.py
