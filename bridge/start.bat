@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 is required. Install it from https://www.python.org/downloads/windows/
    echo During setup, enable "Add Python to PATH".
    pause
    exit /b 1
  )
  set "PY=python"
)
%PY% -m pip install --user --upgrade paramiko
if errorlevel 1 (
  echo Could not install Paramiko. Check your internet connection and try again.
  pause
  exit /b 1
)
%PY% bridge.py
pause
