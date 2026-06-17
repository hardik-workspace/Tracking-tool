@echo off
REM Build script for creating the executable
REM Run this file to build ActivityTracker.exe

echo.
echo ========================================
echo  Activity Tracker Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [1/4] Installing PyInstaller...
    pip install pyinstaller
) else (
    echo [1/4] PyInstaller already installed
)

echo.
echo [2/4] Checking other dependencies...
pip show pynput >nul 2>&1
if errorlevel 1 (
    echo ERROR: pynput not installed. Run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [2/4] All dependencies present

echo.
echo [3/4] Building executable...
echo This may take a minute...
echo.

REM Build using PyInstaller
pyinstaller --onefile --windowed ^
    --name "ActivityTracker" ^
    --distpath "./dist" ^
    --buildpath "./build" ^
    --specpath "." ^
    main.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [4/4] Build complete!
echo.
echo ========================================
echo  Build Successful!
echo ========================================
echo.
echo Executable location: dist\ActivityTracker.exe
echo.
echo To run the application:
echo   - Interactive mode: dist\ActivityTracker.exe --interactive
echo   - Background mode: dist\ActivityTracker.exe
echo.
echo To enable auto-start:
echo   - dist\ActivityTracker.exe --autostart
echo.

pause
