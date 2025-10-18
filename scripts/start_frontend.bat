@echo off
REM Start Frontend Server

REM Change to project root
cd /d "%~dp0\.."

echo Starting Aria Frontend...
cd frontend
call .venv\Scripts\activate
streamlit run app.py
