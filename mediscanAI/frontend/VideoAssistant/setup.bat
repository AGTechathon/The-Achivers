c:\Users\smutk\OneDrive\Documents\hackethon\prime-main\prime-main\training-studio-1.0.0\VideoAssistant\setup.bat@echo off
echo =====================================================
echo    Webcam Video Recorder - Windows Setup
echo =====================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python is installed. Proceeding with setup...

REM Create directories
echo Creating directories...
if not exist "templates" mkdir templates
if not exist "uploads" mkdir uploads
if not exist "static" mkdir static

REM Install Flask (avoiding NumPy issues)
echo Installing Flask...
pip install Flask==2.3.3 Werkzeug==2.3.7

REM Check if home.html exists
if exist "templates\home.html" (
    echo ✓ Found home.html in templates folder
) else (
    if exist "home.html" (
        echo Moving home.html to templates folder...
        move home.html templates\
    ) else (
        echo WARNING: home.html not found!
        echo Please place your home.html file in the templates folder
    )
)

echo.
echo =====================================================
echo Setup complete!
echo.
echo To start the server:
echo   python webcam.py
echo.
echo Then open your browser to:
echo   http://localhost:5000
echo =====================================================
pause