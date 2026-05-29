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

# ----------------------------------------------------------------------------
#  EIN SCHALTER FUER ALLES
# ----------------------------------------------------------------------------
#   True  = SCHNELL & GUENSTIG (Haiku + Flash, ohne Vision).
#           minimale Tokens, hohes Tempo. ABER: Im Test hat der Agent den Kurs
#           NICHT wirklich bearbeitet, sondern den Abschluss nur erfunden.
#           Nur fuer triviale Klick-Kurse und nur, wenn du das Ergebnis selbst
#           im Dashboard nachpruefst.
#
#   False = ZUVERLAESSIG (Sonnet + Vision, ohne Flash).  <-- EMPFOHLEN
#           Langsamer und teurer, aber der Agent arbeitet jede Lektion wirklich
#           durch und erfindet nichts. Das willst du, wenn der Agent den Kurs
#           tatsaechlich selbst machen soll.
SPEED_MODE = False
# ----------------------------------------------------------------------------

if SPEED_MODE:
    MODELL = "claude-haiku-4-5-20251001"
    USE_VISION = False
    FLASH_MODE = True
else:
    MODELL = "claude-sonnet-4-5"
    USE_VISION = True
    FLASH_MODE = False

# Mehrere Aktionen pro LLM-Aufruf -> weniger Hin und Her.
MAX_ACTIONS_PER_STEP = 4
# Anzahl vergangener Schritte im Kontext. None = voller Verlauf, sonst > 5.
MAX_HISTORY_ITEMS = 10
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
Du bist ein gewissenhafter E-Learning-Assistent fuer eine reteach-Kursseite.
WICHTIG: Erfinde NICHTS. Melde nur, was du wirklich auf dem Bildschirm siehst.

1. Oeffne die Seite: {QUIZ_URL}
2. Falls ein Login verlangt wird, melde dich an mit Benutzername
   {QUIZ_USERNAME} und Passwort {QUIZ_PASSWORD}. Bist du bereits angemeldet,
   fahre einfach fort.
3. Oeffne den Kurs und arbeite ALLE Lektionen der Reihe nach durch
   (nicht nur die erste Seite!).
4. Auf jeder Seite:
   a) Lies den gesamten Inhalt aufmerksam.
   b) Erscheint eine Frage mit Auswahlmoeglichkeiten, waehle die richtige
      Antwort anhand des Lektionsinhalts aus und bestaetige sie.
   c) Klicke danach auf "Weiter", um zur naechsten Seite zu gelangen.
5. Wiederhole Schritt 4, bis der Kurs vollstaendig abgeschlossen ist.
6. Lies am Ende das tatsaechlich angezeigte Ergebnis (z. B. die Prozentzahl)
   direkt vom Bildschirm ab und gib es woertlich aus. Behaupte NIEMALS einen
   Abschluss oder ein Ergebnis, das du nicht wirklich gesehen hast. Wenn du
   stecken bleibst, beschreibe genau, was auf dem Bildschirm zu sehen ist.
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
        "max_history_items": MAX_HISTORY_ITEMS,
    }
    while True:
        try:
            agent = Agent(**agent_kwargs)
            break
        except TypeError as e:
            # Unbekannten Parameter aus der Fehlermeldung entfernen und erneut versuchen.
            entfernt = False
            for option in ("max_history_items", "max_actions_per_step", "flash_mode", "use_vision"):
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
