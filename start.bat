@echo off
setlocal
set PROJECT_ROOT=%~dp0
echo [ Aura AI ] Cleaning up old processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul

echo [ Aura AI ] Starting the system...

:: 1. Backend Setup
echo [ Backend ] Activating virtual environment and starting Django...
cd /d "%PROJECT_ROOT%backend"
if not exist venv (
    echo [ Backend ] Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [ Backend ] Installing dependencies...
pip install -r requirements.txt --quiet
start "Aura Backend" cmd /k "venv\Scripts\activate.bat && python manage.py runserver 8000"

:: 2. Celery Setup (Optional background memory)
echo [ Celery ] Starting task worker...
start "Aura Celery" cmd /k "venv\Scripts\activate.bat && celery -A mindcompanion worker --loglevel=info"

:: 3. Frontend Setup
echo [ Frontend ] Starting Vite...
cd /d "%PROJECT_ROOT%frontend"
if not exist node_modules (
    echo [ Frontend ] Installing dependencies...
    call npm install
)
start "Aura Frontend" cmd /k "npm run dev"

echo.
echo [ Success ] Aura is launching!
echo [ Info ] Backend: http://localhost:8000
echo [ Info ] Frontend: http://localhost:5173
echo.
pause
