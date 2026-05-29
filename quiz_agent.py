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
    print("Bitte .env oeffnen und alle Werte eintragen.")
    sys.exit(1)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
QUIZ_URL          = os.getenv("QUIZ_URL")
QUIZ_USERNAME     = os.getenv("QUIZ_USERNAME")
QUIZ_PASSWORD     = os.getenv("QUIZ_PASSWORD")

from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig


async def main():
    input("Druecke ENTER um den Agenten zu starten...")

    llm = ChatAnthropic(
        model="claude-sonnet-4-5",
        anthropic_api_key=ANTHROPIC_API_KEY,
    )

    browser_config = BrowserConfig(
        headless=False,
        chrome_instance_path=r"C:\Users\flori\AppData\Local\ms-playwright\chromium-1223\chrome-win64\chrome.exe",
    )
    browser = Browser(config=browser_config)

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
        print(f"\nFEHLER beim Ausfuehren des Agenten: {e}")
        raise
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
