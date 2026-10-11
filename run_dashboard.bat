@echo off
setlocal enabledelayedexpansion
title CDSCO Weekly Drug Intelligence Tracker

echo =======================================================
echo    CDSCO WEEKLY DRUG INTELLIGENCE TRACKER
echo =======================================================
echo.

cd /d "%~dp0"

:: 1. Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python is not found on your system PATH.
    echo.
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    echo IMPORTANT: Make sure to check the box: "Add python.exe to PATH"
    echo.
    pause
    exit /b 1
)

:: 2. Check or create virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [*] Setting up virtual environment for the first time...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [*] Installing required packages. This may take 2-3 minutes...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Failed to install requirements. Please check your internet connection.
        pause
        exit /b 1
    )
    echo [*] Installing browser drivers for scraper...
    .\.venv\Scripts\python.exe -m playwright install chromium
)

:: 3. Test Database Connection
echo [*] Checking database connection...
.\.venv\Scripts\python.exe test_db.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Warning: Could not connect to the database.
    echo Please check your database settings in the .env file.
    echo Press any key if you would like to start the dashboard anyway...
    pause
)

:: 4. Start the Streamlit Dashboard
echo.
echo =======================================================
echo  Starting CDSCO Weekly Dashboard...
echo  Opening browser at: http://localhost:8501
echo  Press Ctrl+C or close this window to stop the server.
echo =======================================================
echo.

.\.venv\Scripts\python.exe -m streamlit run app/dashboard/dashboard.py --server.port 8501

pause
