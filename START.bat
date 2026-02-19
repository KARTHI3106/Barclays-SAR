@echo off
echo ========================================
echo   AuditWatch - SAR Narrative Generator
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run SETUP.bat first.
    pause
    exit /b 1
)

REM Activate venv
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Ollama is running
echo [2/3] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama not detected!
    echo Please start Ollama in another terminal:
    echo    ollama serve
    echo.
    echo Press any key to continue anyway...
    pause >nul
)

REM Start Streamlit
echo [3/3] Starting AuditWatch...
echo.
echo ========================================
echo   App will open at: http://localhost:8501
echo   Press Ctrl+C to stop
echo ========================================
echo.

streamlit run src/ui/app.py

pause
