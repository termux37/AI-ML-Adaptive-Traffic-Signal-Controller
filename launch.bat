@echo off
REM AI & ML Based Adaptive Traffic Control System - One-Click Project Launcher for Windows
TITLE AI & ML Based Adaptive Traffic Control System
cd /d "%~dp0"

echo ======================================================================
echo   AI & ML Based Adaptive Traffic Control System :: Master Launcher
echo ======================================================================
echo.

python launch.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Launch failed with code %ERRORLEVEL%.
    pause
)
