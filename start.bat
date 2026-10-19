@echo off
REM ============================================================
REM   BloodLink - Blood Donor Finder System
REM   One-click setup and run (Windows)
REM
REM   - First time: creates the environment, installs everything,
REM     sets up the database and loads demo data.
REM   - After that: detects the existing environment and launches
REM     the app directly.
REM
REM   Just double-click this file.
REM ============================================================
title BloodLink - Blood Donor Finder
cd /d "%~dp0"

echo.
echo ==========================================================
echo    BloodLink - Blood Donor Finder System
echo ==========================================================
echo.

REM ---- 1. Find Python (prefer the 'py' launcher, else 'python') ----
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
    python --version >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo [ERROR] Python is not installed or not on PATH.
    echo         Install Python 3 from https://www.python.org/downloads/
    echo         and tick "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo [OK] Using Python: %PY%

REM ---- 2. Detect the virtual environment; create it only if missing ----
set "NEED_INSTALL="
if not exist "venv\Scripts\activate.bat" (
    echo.
    echo [SETUP] No environment found. Creating virtual environment...
    %PY% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        pause
        exit /b 1
    )
    set "NEED_INSTALL=1"
) else (
    echo [OK] Existing environment detected.
)

REM ---- 3. Activate the virtual environment ----
call "venv\Scripts\activate.bat"

REM ---- 4. Verify dependencies are actually installed (handles a half-set-up env) ----
python -c "import django" >nul 2>&1
if errorlevel 1 set "NEED_INSTALL=1"

REM ---- 5. Install dependencies only when needed ----
if defined NEED_INSTALL (
    echo.
    echo [SETUP] Installing dependencies ^(this can take a minute^)...
    python -m pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies already installed.
)

REM ---- 6. Apply database migrations (safe to run every time) ----
echo.
echo [DB] Applying migrations...
python manage.py migrate

REM ---- 7. Load demo data only if there is no database yet ----
if not exist "db.sqlite3" (
    echo.
    echo [DB] Loading demo data ^(badges, donors, hospitals, organizations^)...
    python manage.py seed
) else if defined NEED_INSTALL (
    echo.
    echo [DB] Loading demo data ^(badges, donors, hospitals, organizations^)...
    python manage.py seed
)

REM ---- 8. Launch the server and open the browser ----
echo.
echo ==========================================================
echo   BloodLink is starting...
echo   Open your browser at:  http://127.0.0.1:8000
echo.
echo   Demo logins:
echo     Admin        ^-^>  admin / admin12345
echo     Hospital     ^-^>  hospital1 / hospital12345
echo     Organization ^-^>  org1 / org12345
echo     Donor        ^-^>  donor1 / donor12345
echo.
echo   Press CTRL+C in this window to stop the server.
echo ==========================================================
echo.

REM Open the browser a few seconds after the server starts (runs in background)
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:8000'"

python manage.py runserver

echo.
echo Server stopped.
pause
