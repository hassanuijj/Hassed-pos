@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install pyinstaller
if not exist build\launcher.py exit /b 2
python -m PyInstaller --noconfirm --clean --onefile --name HassedPOS build\launcher.py
if errorlevel 1 exit /b 1
echo EXE created at dist\HassedPOS.exe
endlocal
