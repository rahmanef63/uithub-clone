@echo off
TITLE Uithub Clone Launcher
CLS
ECHO ========================================================
ECHO 🚀 Launching Uithub Clone PRO...
ECHO ========================================================

REM Check if python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Python is not installed or not in PATH.
    ECHO Please install Python from https://python.org
    PAUSE
    EXIT /B
)

REM Check if virtual environment exists, if not create it
IF NOT EXIST ".venv" (
    ECHO [INFO] Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
CALL .venv\Scripts\activate

REM Install requirements if they exist (future proofing)
IF EXIST "requirements.txt" (
    pip install -r requirements.txt >nul 2>&1
)

REM Run the app
python main.py

PAUSE
