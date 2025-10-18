@echo off
REM Startup script for Aria Chatbot - All Services
REM Starts Qdrant, Backend, and Frontend

REM Change to project root directory
cd /d "%~dp0\.."

echo ========================================
echo Aria Chatbot - Starting All Services
echo ========================================
echo.

REM Check if using Qdrant Cloud or Local
echo [1/3] Checking Qdrant configuration...
findstr /C:"cloud.qdrant.io" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Using Qdrant Cloud
) else (
    REM Check if local Qdrant is running
    curl -s http://localhost:6333/collections >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Local Qdrant is not running!
        echo Please start Qdrant first:
        echo   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
        pause
        exit /b 1
    )
    echo ✓ Local Qdrant is running
)
echo.

REM Start Backend
echo [2/3] Starting Backend (FastAPI)...
start "Aria Backend" cmd /k "cd /d "%~dp0..\backend" && .venv\Scripts\activate && python main.py"
echo ✓ Backend starting at http://localhost:8000

REM Wait for backend health to be ready (max ~20s)
setlocal EnableDelayedExpansion
set /a count=0
:wait_backend
set /a count+=1
for /f "usebackq delims=" %%H in (`curl.exe -s http://localhost:8000/health`) do set HEALTH=%%H
echo !HEALTH! | find /i "healthy" >nul 2>&1 && goto backend_ready
if !count! GEQ 20 (
    echo WARNING: Backend health not ready yet, continuing anyway...
    goto backend_ready
)
timeout /t 1 /nobreak >nul
goto wait_backend

:backend_ready
endlocal
echo.

REM Start Frontend
echo [3/3] Starting Frontend (Streamlit)...
start "Aria Frontend" cmd /k "cd /d "%~dp0..\frontend" && .venv\Scripts\activate && streamlit run app.py"
echo ✓ Frontend starting at http://localhost:8501
echo.

echo ========================================
echo All services are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Press any key to exit this window...
echo (The services will keep running in separate windows)
pause >nul
