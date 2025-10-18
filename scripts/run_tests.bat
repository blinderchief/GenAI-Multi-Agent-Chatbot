@echo off
REM Run tests for Aria Chatbot

REM Change to project root directory
cd /d "%~dp0\.."

echo ========================================
echo Aria Chatbot - Running Tests
echo ========================================
echo.

cd backend
call .venv\Scripts\activate

echo Running unit tests...
pytest tests/ -v -m "not integration"

echo.
echo ========================================
echo Test run complete!
echo ========================================
echo.

echo To run with coverage:
echo   pytest tests/ --cov=app --cov-report=html
echo.

call deactivate
pause
