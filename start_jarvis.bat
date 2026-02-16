@echo off
setlocal EnableDelayedExpansion
title JARVIS - Windows AI CMD Assistant
color 0A

:: ==================================================
:: AUTO ELEVATE TO ADMIN
:: ==================================================
net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

:: ==================================================
:: GET FULL ABSOLUTE PATH OF THIS BAT FILE
:: ==================================================
set "BASE_DIR=%~dp0"
for %%i in ("%BASE_DIR%.") do set "BASE_DIR=%%~fi"

:: Move into project directory safely
cd /d "%BASE_DIR%"

echo ==========================================
echo        JARVIS - Smart Auto Launcher
echo ==========================================
echo.

:: ==================================================
:: STEP 1 - CHECK PYTHON
:: ==================================================
where python >nul 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [*] Python not found. Installing latest version...

    set "PYTHON_URL=https://www.python.org/ftp/python/3.14.2/python-3.14.2-amd64.exe"
    set "PYTHON_INSTALLER=%TEMP%\python_installer.exe"

    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"

    if not exist "%PYTHON_INSTALLER%" (
        echo [ERROR] Download failed.
        timeout /t 5 >nul
        exit /b 1
    )

    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%PYTHON_INSTALLER%"
)

:: Re-check python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python installation failed.
    timeout /t 5 >nul
    exit /b 1
)

:: ==================================================
:: STEP 2 - INSTALL DEPENDENCIES
:: ==================================================
if exist "%BASE_DIR%\requirements.txt" (
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r "%BASE_DIR%\requirements.txt" >nul 2>&1
)

:: ==================================================
:: STEP 3 - FIND AND RUN main.py (PATH SAFE)
:: ==================================================
set "MAIN_FILE=%BASE_DIR%\main.py"

if exist "%MAIN_FILE%" (
    cls
    echo ==========================================
    echo           Launching JARVIS...
    echo ==========================================
    echo.
    python "%MAIN_FILE%"
) else (
    echo [ERROR] main.py not found at:
    echo %MAIN_FILE%
    timeout /t 5 >nul
)

endlocal
exit
