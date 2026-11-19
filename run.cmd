@echo off
setlocal
pushd "%~dp0" || exit /b 1

where python >nul 2>nul
if errorlevel 1 (
    echo Python is required. Install Python and add it to PATH, then run this file again.
    goto failed
)

python -B -c "import pygame" >nul 2>nul
if errorlevel 1 (
    python -m pip install -r requirements.txt
    if errorlevel 1 goto failed
)

python -B app.py
if errorlevel 1 goto failed
popd
exit /b 0

:failed
popd
pause
exit /b 1
