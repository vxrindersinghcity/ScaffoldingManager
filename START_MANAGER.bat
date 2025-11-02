@echo off
title Scaffolding Business Manager
color 0A

echo ============================================================
echo       SCAFFOLDING BUSINESS MANAGER - Ultimate Edition
echo ============================================================
echo.
echo Starting application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Install required packages
echo Installing/Checking required packages...
pip install Flask Flask-CORS --quiet
if errorlevel 1 (
    echo [WARNING] Some packages may not have been installed correctly
)

echo.
echo ============================================================
echo Application is starting...
echo.
echo Your browser will open automatically in a few seconds
echo Database will be created in your home directory
echo.
echo IMPORTANT: Keep this window open while using the app
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Run the Python server
python scaffolding_manager.py

pause
