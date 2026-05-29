# QuizMaster – Schritt-für-Schritt-Anleitung (idiotensicher)

Diese Anleitung bringt das Quiz-Skript auf deinem Windows-Rechner zum Laufen.
Folge den Schritten **genau in dieser Reihenfolge**. Du musst nur kopieren,
einfügen und Enter drücken.

---

## Was du EINMALIG vorbereiten musst

### Schritt 1 – Projekt-Dateien holen

Öffne die **PowerShell** (Windows-Taste drücken, `powershell` tippen, Enter).
Kopiere folgenden Block komplett hinein und drücke Enter:

```powershell
cd C:\Users\flori
git clone https://github.com/budgetassistenz/QuizMaster.git quiz-agent
cd quiz-agent
git checkout claude/ecstatic-pascal-7XOGx
```

> Falls du den Ordner `quiz-agent` schon hast und nur die neuen Dateien willst:
> ```powershell
> cd C:\Users\flori\quiz-agent
> git fetch origin claude/ecstatic-pascal-7XOGx
> git checkout claude/ecstatic-pascal-7XOGx
> git pull origin claude/ecstatic-pascal-7XOGx
> ```

---

### Schritt 2 – Setup ausführen (installiert alles automatisch)

Öffne den Ordner `C:\Users\flori\quiz-agent` im Windows-Explorer und mache
einen **Doppelklick auf `setup.bat`**.

Das Skript erledigt automatisch:
- virtuelle Umgebung (venv) erstellen
- alte, fehlerhafte LangChain-Pakete entfernen
- `browser-use` + Abhängigkeiten installieren
- den richtigen Chromium-Browser herunterladen

➡️ **Warte, bis "SETUP FERTIG!" erscheint.** Das kann ein paar Minuten dauern.

---

### Schritt 3 – Zugangsdaten eintragen (.env-Datei)

1. Mache im Ordner eine **Kopie von `.env.example`**.
2. Benenne die Kopie um in **`.env`** (nur Punkt + env, ohne `.example`).
3. Öffne `.env` mit dem Editor (Rechtsklick → Öffnen mit → Editor).
4. Trage deine echten Daten ein:

```
ANTHROPIC_API_KEY=sk-ant-DEIN-ECHTER-SCHLUESSEL
QUIZ_URL=https://usp-partner-ag.reteach.io/invitation?invitationToken=DEIN-TOKEN
QUIZ_USERNAME=florianobfeuillet@gmail.com
QUIZ_PASSWORD=DEIN-PASSWORT
```

5. Speichern (Strg + S) und schließen.

> **Wichtig:** Die Datei muss exakt `.env` heißen und im Ordner
> `C:\Users\flori\quiz-agent\` liegen – **nicht** `quiz-agent.env`.

---

## Bei jedem Mal: Quiz starten

Doppelklick auf **`start.bat`**.

Es öffnet sich ein Fenster, in dem steht:
`Druecke ENTER um den Agenten zu starten...`

➡️ **Enter drücken.** Der Browser öffnet sich und der Agent beantwortet das Quiz.

---

## Wenn etwas schiefgeht

| Meldung | Lösung |
|---|---|
| `Python wurde nicht gefunden` | Python 3.12 installieren von python.org, Haken bei **"Add to PATH"** setzen, dann `setup.bat` erneut. |
| `Die Datei ".env" fehlt` | Schritt 3 nachholen (Kopie von `.env.example` als `.env`). |
| `browser-use ist nicht installiert` | `setup.bat` erneut ausführen. |
| `has no attribute 'provider'` / `'model_name'` | Du nutzt noch alten Code. Schritt 1 (`git pull`) + `setup.bat` wiederholen. |
| `[WinError 2] ... Datei nicht finden` | `CHROMIUM_PATH` in `.env` löschen/auskommentieren und `python -m playwright install chromium` laufen lassen (steckt schon in `setup.bat`). |
| Modell-ID abgelehnt | In `quiz_agent.py` die Zeile `MODELL = "claude-sonnet-4-5"` auf die aktuelle Anthropic-Modell-ID anpassen. |

---

## Warum es vorher nicht ging (kurz)

Der alte Code benutzte `langchain_anthropic` mit Bastel-Workarounds
(`object.__setattr__`, Patch in `cloud_events.py`). `browser-use` bringt aber
seinen **eigenen** `ChatAnthropic` mit, der alles Nötige (`provider`,
`model_name`) schon eingebaut hat. Der neue Code nutzt diesen – dadurch
verschwinden alle Attribut-Fehler **und** der manuelle Patch wird überflüssig.
Der `WinError 2` kam von einem fest verdrahteten, nicht passenden Chromium-Pfad;
jetzt findet Playwright den Browser selbst.
