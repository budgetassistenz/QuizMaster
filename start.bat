@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM --- Pruefen ob Setup gelaufen ist ---
if not exist "venv\Scripts\activate.bat" (
    echo FEHLER: Setup wurde noch nicht ausgefuehrt.
    echo Bitte zuerst "setup.bat" per Doppelklick starten.
    pause
    exit /b 1
)

REM --- Pruefen ob .env existiert ---
if not exist ".env" (
    echo FEHLER: Die Datei ".env" fehlt im Ordner:
    echo    %cd%
    echo.
    echo Bitte ".env.example" nach ".env" kopieren und ausfuellen.
    pause
    exit /b 1
)

echo Starte QuizMaster...
echo.
call venv\Scripts\activate.bat
python quiz_agent.py

echo.
echo === Programm beendet ===
pause
