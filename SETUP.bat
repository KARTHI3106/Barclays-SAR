@echo off
echo ========================================
echo   AuditWatch - Setup Script
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo.

REM Create venv
echo [2/5] Creating virtual environment...
if exist "venv\" (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

REM Activate venv
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/5] Installing dependencies (this may take 3-5 minutes)...
pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Download spaCy model
echo [5/5] Downloading spaCy language model...
python -m spacy download en_core_web_sm
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Install Ollama from: https://ollama.ai/download
echo 2. Run: ollama pull llama3.1:8b
echo 3. Start Ollama: ollama serve (in a separate terminal)
echo 4. Run: START.bat (to start the app)
echo.
echo See SETUP.md for detailed instructions.
echo.
pause
