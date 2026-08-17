@echo off
setlocal

cd /d "%~dp0"

py -3.8 -m venv .venv-win8
if errorlevel 1 goto :error

.venv-win8\Scripts\python -m pip install --upgrade pip
if errorlevel 1 goto :error

.venv-win8\Scripts\pip install -r requirements.txt -r requirements-build-windows.txt
if errorlevel 1 goto :error

.venv-win8\Scripts\pyinstaller --clean ses-sistemi.spec
if errorlevel 1 goto :error

echo.
echo Build tamamlandi:
echo dist\SesSistemi.exe
echo.
pause
exit /b 0

:error
echo.
echo Build basarisiz oldu.
echo.
pause
exit /b 1
