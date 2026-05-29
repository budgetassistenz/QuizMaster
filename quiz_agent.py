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
try:
    from browser_use import Agent, Browser, BrowserProfile, ChatAnthropic
except ImportError as import_fehler:
    print("FEHLER: browser-use ist nicht (richtig) installiert.")
    print(f"Details: {import_fehler}")
    print("\nLOESUNG: Fuehre zuerst 'setup.bat' aus (Doppelklick).")
    sys.exit(1)

# Modell-ID anpassen, falls Anthropic die Bezeichnung aendert.
# Tipp: Fuer maximale Geschwindigkeit "claude-haiku-4-5" probieren (schneller,
# aber bei kniffligen Fragen evtl. ungenauer als Sonnet).
MODELL = "claude-sonnet-4-5"

# ----------------------------------------------------------------------------
#  GESCHWINDIGKEITS-EINSTELLUNGEN
# ----------------------------------------------------------------------------
# False = KEINE Screenshots, Agent arbeitet nur ueber den DOM/HTML.
#         -> Deutlich schneller und guenstiger. Empfohlen fuer Text-Quizze.
#         Nur auf True stellen, wenn der Agent visuelle Inhalte (Bilder) braucht.
USE_VISION = False

# True = "Flash-Modus": ueberspringt internes Nachdenken/Evaluieren.
#        Noch schneller, kann aber die Antwort-Qualitaet senken.
#        Bei falschen Antworten einfach wieder auf False stellen.
FLASH_MODE = False

# Mehrere Aktionen pro LLM-Aufruf erlauben -> weniger Hin und Her.
MAX_ACTIONS_PER_STEP = 4
# ----------------------------------------------------------------------------

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

    # Agent mit Geschwindigkeits-Optionen bauen. Manche Optionen existieren je
    # nach browser-use-Version nicht -> wir entfernen sie im Fehlerfall sauber,
    # statt das Programm abstuerzen zu lassen.
    agent_kwargs = {
        "task": aufgabe,
        "llm": llm,
        "browser": browser,
        "use_vision": USE_VISION,
        "flash_mode": FLASH_MODE,
        "max_actions_per_step": MAX_ACTIONS_PER_STEP,
    }
    while True:
        try:
            agent = Agent(**agent_kwargs)
            break
        except TypeError as e:
            # Unbekannten Parameter aus der Fehlermeldung entfernen und erneut versuchen.
            entfernt = False
            for option in ("max_actions_per_step", "flash_mode", "use_vision"):
                if option in str(e) and option in agent_kwargs:
                    print(f"Hinweis: '{option}' wird von dieser browser-use-Version nicht unterstuetzt - wird ignoriert.")
                    del agent_kwargs[option]
                    entfernt = True
                    break
            if not entfernt:
                raise

    try:
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
