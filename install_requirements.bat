@echo off
setlocal enabledelayedexpansion
title AI & ML Adaptive Traffic Control System - Setup & Installation

echo ===============================================================================
echo     AI & ML Based Adaptive Traffic Control System - Installer
echo ===============================================================================
echo.

:: 1. Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.10, 3.11, or 3.12 from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] Detected Python %PY_VER%
echo.

:: 2. Upgrade pip
echo [2/5] Upgrading Python package manager (pip)...
python -m pip install --upgrade pip
echo.

:: 3. Install requirements
echo [3/5] Installing core dependencies from requirements.txt...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install some dependencies. Please check your internet connection or Python setup.
    pause
    exit /b 1
)
echo [OK] All dependencies successfully installed.
echo.

:: 4. Install local package in development/editable mode
echo [4/5] Installing project package in editable mode (traffic_ai)...
python -m pip install -e .
echo [OK] Project package registered.
echo.

:: 5. Verify SUMO Installation & SUMO_HOME
echo [5/5] Verifying SUMO (Simulation of Urban MObility)...
if defined SUMO_HOME (
    echo [OK] SUMO_HOME is set to: "%SUMO_HOME%"
) else (
    echo [INFO] SUMO_HOME is not set in environment variables. Scanning standard paths...
    if exist "C:\Program Files (x86)\Eclipse\Sumo" (
        set "SUMO_HOME=C:\Program Files (x86)\Eclipse\Sumo"
        setx SUMO_HOME "C:\Program Files (x86)\Eclipse\Sumo" >nul 2>&1
        echo [OK] Found SUMO at: C:\Program Files (x86)\Eclipse\Sumo
        echo [OK] Automatically configured SUMO_HOME for current and future sessions.
    ) else if exist "C:\Program Files\Eclipse\Sumo" (
        set "SUMO_HOME=C:\Program Files\Eclipse\Sumo"
        setx SUMO_HOME "C:\Program Files\Eclipse\Sumo" >nul 2>&1
        echo [OK] Found SUMO at: C:\Program Files\Eclipse\Sumo
        echo [OK] Automatically configured SUMO_HOME for current and future sessions.
    ) else (
        echo [WARNING] SUMO was not detected in standard directories.
        echo If Eclipse SUMO is not installed yet, please download and install it from:
        echo   https://eclipse.dev/sumo/
        echo Or via Windows Package Manager:
        echo   winget install Eclipse.SUMO
        echo Then set the SUMO_HOME system environment variable to your SUMO folder.
    )
)
echo.

:: Verification Smoke Run
echo ===============================================================================
echo Running System Verification Smoke Test...
echo ===============================================================================
python scripts\check_environment.py
echo.

echo ===============================================================================
echo Setup process finished!
echo To launch the Interactive Operations Dashboard, run:
echo   streamlit run app.py
echo ===============================================================================
echo.
pause
