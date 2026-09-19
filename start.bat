@echo off
title Strata Services
echo Starting Strata AI...
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo [WARNING] Virtual environment not found at .venv\Scripts\activate.bat
)
python start_all.py
pause
