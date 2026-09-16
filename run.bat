@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
if not exist .venv (
  echo [ERROR] Please run setup.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
echo ex-video : lecture video -> transcript + slides + figures -> bundle.md
echo.
set /p SRC="Enter video file path OR Google Drive/URL link: "
if "%SRC%"=="" (
  echo No input given.
  pause
  exit /b 1
)
python -m exvideo "%SRC%" -o output
echo.
echo Done. Open the 'output' folder and use output\bundle.md
pause
