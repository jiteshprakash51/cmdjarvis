@echo off
REM CMDJARVIS Launcher - Secure Command Executor
title CMDJARVIS
cd /d "%~dp0"

echo.
echo [*] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Download from: https://www.python.org/
    pause
    exit /b 1
)

echo [+] Python found. Installing dependencies...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [+] Starting JARVIS...
echo.
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo [!] JARVIS exited with error code %ERRORLEVEL%
)

pause
exit /b %ERRORLEVEL%
