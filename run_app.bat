@echo off
REM MSA Stock Analysis - Desktop Application Launcher (Windows)

echo ================================
echo MSA Stock Analysis - Desktop App
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: PyQt5 not found. Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Launching MSA Stock Analysis Desktop Application...
echo.

REM Run the application
python desktop_app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application failed to start
    echo Please check the error messages above
    pause
)

exit /b %errorlevel%
