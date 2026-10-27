@echo off
chcp 65001 >nul
title Online4Tech Bridge Setup
py -m pip install --user paramiko
if errorlevel 1 (
 echo تعذر التثبيت. تأكد من تثبيت Python 3.10 أو أحدث.
 pause
 exit /b 1
)
echo تم التثبيت. شغّل start.bat بعد ذلك.
pause
