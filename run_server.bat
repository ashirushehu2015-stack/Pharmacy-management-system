@echo off
echo Starting PharmCore System...
call venv\Scripts\activate
python manage.py runserver
pause
