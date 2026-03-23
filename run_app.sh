#!/bin/bash

# MSA Stock Analysis - Desktop Application Launcher (Mac/Linux)

echo "================================"
echo "MSA Stock Analysis - Desktop App"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $PYTHON_VERSION"

# Check if required packages are installed
python3 -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: PyQt5 not found. Installing dependencies..."
    echo ""
    
    if ! command -v pip3 &> /dev/null; then
        echo "ERROR: pip3 is not installed"
        echo "Please install pip: python3 -m ensurepip --upgrade"
        read -p "Press Enter to exit..."
        exit 1
    fi
    
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo ""
echo "Launching MSA Stock Analysis Desktop Application..."
echo ""

# Run the application
python3 desktop_app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Application failed to start"
    echo "Please check the error messages above"
    read -p "Press Enter to exit..."
fi

exit 0
