@echo off
cd /d "%~dp0"
py -3 app.py
if errorlevel 1 (
 echo.
 echo No se pudo iniciar con py -3. Intentando python...
 python app.py
)
pause
