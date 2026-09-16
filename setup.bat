@echo off
setlocal
cd /d "%~dp0"
echo ================================
echo   ex-video - first-time setup
echo ================================
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python is not installed.
  echo Please install Python 3.10+ from https://www.python.org/downloads/ and run again.
  pause
  exit /b 1
)
if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
echo Installing packages ... (first time can take several minutes)
pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Package install failed. Check your internet connection.
  pause
  exit /b 1
)
echo.
echo Setup complete. Now double-click run.bat to use the program.
pause
