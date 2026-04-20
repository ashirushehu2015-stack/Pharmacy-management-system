@echo off
setlocal
set PORT=8000
echo ======================================================
echo   Starting Pharmacy Management System...
echo ======================================================
echo.

if not exist venv (
    echo [ERROR] Virtual environment not found. 
    echo Please run 'setup_desktop.bat' first.
    pause
    exit /b
)

:: Check for .env file
if not exist .env (
    echo [INFO] Creating default .env configuration...
    echo SECRET_KEY=django-insecure-desktop-mode-$(date /t) > .env
    echo DEBUG=False >> .env
    echo ALLOWED_HOSTS=localhost,127.0.0.1 >> .env
)

echo [1/2] Opening browser...
:: Small delay to wait for server to start. 
:: Browser often opens faster than the server can bind the port.
echo Waiting for server to initialize...
timeout /t 5 /nobreak > nul
start "" http://127.0.0.1:%PORT%

echo [2/2] Launching server on http://127.0.0.1:%PORT%
echo Press Ctrl+C to stop the system.
echo.

call venv\Scripts\activate

:: Verify waitress is installed
python -c "import waitress" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] 'waitress' not found in environment. 
    echo Please run 'setup_desktop.bat' again to install dependencies.
    pause
    exit /b
)

:: Use Waitress for production-ready performance on Windows
python -m waitress --port=%PORT% pharmacy_management_system.wsgi:application

pause
