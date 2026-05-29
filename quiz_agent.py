import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Pflichtfelder pruefen
PFLICHTFELDER = ["ANTHROPIC_API_KEY", "QUIZ_URL", "QUIZ_USERNAME", "QUIZ_PASSWORD"]
fehlende = [f for f in PFLICHTFELDER if not os.getenv(f)]
if fehlende:
    print(f"FEHLER: Folgende Variablen fehlen in der .env-Datei: {', '.join(fehlende)}")
    sys.exit(1)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
QUIZ_URL          = os.getenv("QUIZ_URL")
QUIZ_USERNAME     = os.getenv("QUIZ_USERNAME")
QUIZ_PASSWORD     = os.getenv("QUIZ_PASSWORD")

# WICHTIG: browser-use 0.12.x bringt einen EIGENEN ChatAnthropic-Wrapper mit,
# der bereits 'provider' und 'model_name' besitzt. Damit entfallen alle
# Pydantic-Hacks (object.__setattr__) UND der Patch in cloud_events.py.
# NICHT langchain_anthropic verwenden!
from browser_use import Agent, Browser, BrowserProfile, ChatAnthropic

# Modell-ID anpassen, falls Anthropic die Bezeichnung aendert.
MODELL = "claude-sonnet-4-5"

# Optionaler manueller Chromium-Pfad. Standardmaessig leer lassen, damit
# Playwright den selbst installierten Browser aufloest. Nur setzen, wenn die
# Datei wirklich existiert -> verhindert [WinError 2].
CHROMIUM_PFAD = os.getenv("CHROMIUM_PATH")  # z.B. ...\chrome-win64\chrome.exe


async def main():
    input("Druecke ENTER um den Agenten zu starten...")

    llm = ChatAnthropic(
        model=MODELL,
        api_key=ANTHROPIC_API_KEY,
    )

    profil_kwargs = {"headless": False}
    if CHROMIUM_PFAD and os.path.isfile(CHROMIUM_PFAD):
        profil_kwargs["executable_path"] = CHROMIUM_PFAD
    elif CHROMIUM_PFAD:
        print(f"WARNUNG: CHROMIUM_PATH existiert nicht, nutze Playwright-Standard: {CHROMIUM_PFAD}")

    browser_profile = BrowserProfile(**profil_kwargs)
    browser = Browser(browser_profile=browser_profile)

    aufgabe = f"""
Du bist ein Quiz-Assistent. Fuehre folgende Schritte genau aus:

1. Oeffne die Seite: {QUIZ_URL}
2. Melde dich an mit:
   - Benutzername: {QUIZ_USERNAME}
   - Passwort: {QUIZ_PASSWORD}
3. Starte das Quiz.
4. Beantworte jede Frage:
   a) Lies die Frage und alle Optionen vollstaendig.
   b) Bei Unsicherheit: neuer Tab, Google-Suche, zurueck zum Quiz.
   c) Beste Antwort waehlen und bestaetigen.
5. Quiz abschliessen und Ergebnis ausgeben.
"""

    try:
        agent = Agent(task=aufgabe, llm=llm, browser=browser)
        ergebnis = await agent.run()
        print("\n=== Quiz abgeschlossen ===")
        print(ergebnis)
    except Exception as e:
        print(f"\nFEHLER: {e}")
        raise
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
