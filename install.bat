@echo off
cls

cd /d "%~dp0"

set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
set "PYTHON_INSTALLER=installer.exe"
set "INSTALL_DIR=%LocalAppData%\Programme\Python\Python311"
set "TEMP_DIR=%TEMP%"

:: Prüfen, ob Python installiert ist
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Python ist bereits installiert.
    set "PYTHON_FOUND=1"
    goto afterPythonCheck
)

echo [WARNUNG] Python wurde nicht gefunden.

:askInstall
set /p INSTALL_CONFIRM=Python installieren? (J/N):

if /i "%INSTALL_CONFIRM%"=="J" goto installPython
if /i "%INSTALL_CONFIRM%"=="N" (
    echo [ABBRUCH] Python-Installation wurde abgelehnt.
    exit /b 1
)

echo Bitte "J" oder "N" eingeben.
goto askInstall

:installPython
echo [INFO] Starte Installation...
echo [INFO] Python-Installer wird heruntergeladen...

powershell -ExecutionPolicy Bypass -Command ^
    "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TEMP_DIR%\%PYTHON_INSTALLER%' -UseBasicParsing"

if not exist "%TEMP_DIR%\%PYTHON_INSTALLER%" (
    echo [FEHLER] Der Python-Installer konnte nicht heruntergeladen werden.
    exit /b 1
)

echo [ERFOLG] Python-Installer wurde heruntergeladen: "%TEMP_DIR%\%PYTHON_INSTALLER%"

"%TEMP_DIR%\%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 TargetDir="%INSTALL_DIR%" Include_test=0

if %errorlevel% neq 0 (
    echo [FEHLER] Python-Installation fehlgeschlagen.
    exit /b 1
)

echo [ERFOLG] Python wurde erfolgreich installiert.

set "PATH=%PATH%;%INSTALL_DIR%;%INSTALL_DIR%\Scripts"
set "PYTHON_FOUND=1"

:afterPythonCheck

echo [INFO] Update pip...
py -m pip install --upgrade pip
echo [INFO] Starte Asploit...
py -m core.main
