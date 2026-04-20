@echo off
setlocal
echo ======================================================
echo   Pharmacy Management System - Desktop Setup
echo ======================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! 
    echo Please install Python 3.12 or newer from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b
)

:: Create Virtual Environment
echo [1/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
)

:: Activate and install requirements
echo [2/4] Installing dependencies...
call venv\Scripts\activate
pip install -U pip
:: Priority install for core web deps
pip install django waitress whitenoise python-dotenv dj-database-url
pip install -r requirements.txt

:: Database setup
echo [3/4] Preparing database...
python manage.py migrate

:: Admin user check
echo [4/4] Finalizing setup...
echo.
echo Would you like to create an Administrator account now? (Y/N)
set /p create_admin=
if /i "%create_admin%"=="Y" (
    echo Enter the details for your new administrator account:
    python manage.py createsuperuser
)

echo.
echo ======================================================
echo   SETUP COMPLETE!
echo   You can now use 'run_pharmacy.bat' to start the app.
echo ======================================================
pause
