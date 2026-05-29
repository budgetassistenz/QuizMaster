"""
quiz_agent.py – Automatischer Quiz-Agent mit browser-use + Claude
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Umgebungsvariablen aus .env laden
load_dotenv()

# --- Pflichtfelder prüfen ---
PFLICHTFELDER = ["ANTHROPIC_API_KEY", "QUIZ_URL", "QUIZ_USERNAME", "QUIZ_PASSWORD"]
fehlende = [f for f in PFLICHTFELDER if not os.getenv(f)]
if fehlende:
    print(f"FEHLER: Folgende Variablen fehlen in der .env-Datei: {', '.join(fehlende)}")
    print("Bitte .env öffnen und alle Werte eintragen.")
    sys.exit(1)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
QUIZ_URL          = os.getenv("QUIZ_URL")
QUIZ_USERNAME     = os.getenv("QUIZ_USERNAME")
QUIZ_PASSWORD     = os.getenv("QUIZ_PASSWORD")

# Brave Browser Pfad auf Windows
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserProfile


async def main():
    # --- LLM initialisieren ---
    llm = ChatAnthropic(
        model="claude-sonnet-4-5",
        anthropic_api_key=ANTHROPIC_API_KEY,
    )

    # --- Browser konfigurieren (sichtbar, Brave) ---
    browser_profile = BrowserProfile(
        headless=False,
        executable_path=BRAVE_PATH,
    )
    browser = Browser(browser_profile=browser_profile)

    # --- Aufgabe für den Agenten ---
    aufgabe = f"""
Du bist ein Quiz-Assistent. Führe folgende Schritte genau aus:

1. Öffne die Seite: {QUIZ_URL}
2. Melde dich an mit:
   - Benutzername: {QUIZ_USERNAME}
   - Passwort: {QUIZ_PASSWORD}
3. Starte das Quiz (suche nach einem Button wie "Quiz starten", "Start", "Begin").
4. Beantworte jede Frage so:
   a) Lies die Frage und alle Antwortoptionen vollständig.
   b) Wenn du dir nicht sicher bist: Öffne einen neuen Tab, suche kurz bei
      Google nach der Frage, schließe den Tab wieder und kehre zum Quiz zurück.
   c) Wähle die beste Antwort und bestätige sie (Klick auf "Weiter",
      "Nächste Frage", "Submit" o. Ä.).
5. Schließe das Quiz ab.
6. Lies das Ergebnis (Punktzahl / Auswertung) und gib es aus.

Wichtig: Bleibe geduldig bei Ladezeiten. Falls ein Schritt fehlschlägt,
beschreibe kurz das Problem.
"""

    # --- Agent starten ---
    try:
        agent = Agent(
            task=aufgabe,
            llm=llm,
            browser=browser,
        )
        ergebnis = await agent.run()
        print("\n=== Quiz abgeschlossen ===")
        print(ergebnis)
    except Exception as e:
        print(f"\nFEHLER beim Ausführen des Agenten: {e}")
        print("Bitte prüfe deine .env-Werte und ob der Browser korrekt installiert ist.")
        raise
    finally:
        # Browser sauber schließen
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
