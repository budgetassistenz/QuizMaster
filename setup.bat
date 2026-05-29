@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ================================================
echo    QuizMaster - Einmaliges Setup
echo ================================================
echo.

REM --- Schritt 1: virtuelle Umgebung erstellen ---
if exist "venv\Scripts\activate.bat" (
    echo [1/6] Virtuelle Umgebung existiert bereits - ok.
) else (
    echo [1/6] Erstelle virtuelle Umgebung...
    py -3.12 -m venv venv
    if errorlevel 1 python -m venv venv
    if errorlevel 1 (
        echo.
        echo FEHLER: Python wurde nicht gefunden. Bitte Python 3.12 installieren
        echo von https://www.python.org/downloads/ und Haken bei "Add to PATH" setzen.
        pause
        exit /b 1
    )
)

REM --- Schritt 2: Umgebung aktivieren ---
echo [2/6] Aktiviere Umgebung...
call venv\Scripts\activate.bat

REM --- Schritt 3: pip aktualisieren ---
echo [3/6] Aktualisiere pip...
python -m pip install --upgrade pip >nul

REM --- Schritt 4: alte/kollidierende Pakete entfernen ---
echo [4/6] Entferne alte LangChain-Pakete (verursachen Fehler)...
pip uninstall -y langchain-anthropic langchain-core langchain >nul 2>&1

REM --- Schritt 5: Pakete installieren ---
echo [5/6] Installiere benoetigte Pakete (kann ein paar Minuten dauern)...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo FEHLER bei der Installation. Pruefe deine Internetverbindung.
    pause
    exit /b 1
)

REM --- Schritt 6: Chromium-Browser installieren ---
echo [6/6] Installiere passenden Browser (Chromium)...
python -m playwright install chromium
if errorlevel 1 (
    echo.
    echo FEHLER beim Browser-Download. Pruefe deine Internetverbindung.
    pause
    exit /b 1
)

echo.
echo ================================================
echo    SETUP FERTIG!
echo ================================================
echo.
echo NAECHSTER SCHRITT:
echo   1. Kopiere die Datei ".env.example" zu ".env"
echo   2. Trage in ".env" deinen API-Schluessel und dein Passwort ein
echo   3. Starte dann das Quiz mit einem Doppelklick auf "start.bat"
echo.
pause
