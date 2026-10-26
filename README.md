# Lernordner – Lernassistent für Claude Code

Eine Agenten- und Skill-Struktur, mit der [Claude Code](https://claude.com/claude-code) als Lernassistent für Hochschulkurse arbeitet: Material sichten, Lücken finden und recherchieren, Stoff in kleine Chunks aufbereiten, interaktive Lernsessions (Feynman-Methode, Abrufübung) und verteilte Wiederholung mit Karten.

## Nutzung

1. Repo klonen und den Ordner in Claude Code öffnen (`claude` im Repo-Verzeichnis starten).
2. Einen Kursordner unter `Kurse/` anlegen und Material hineinlegen.
3. `/kurs-anlegen <Ordner>` – richtet den Kurs ein und erzeugt einen kursspezifischen Skill und Fachexperten-Agent.
4. `/material-update <Kurs>` bei neuem Material, `/lernsession <Kurs>` zum Lernen, `/klausurphase <Kurs>` vor der Prüfung.

Alle Regeln (Erklärstil, Lernmethode, Ordnerkonvention) stehen in `CLAUDE.md`, die lernwissenschaftliche Grundlage der Wiederholungsabstände in `_system/lernwissenschaft.md`.

## Aufbau

- `.claude/agents/` – `material-sichter`, `luecken-evaluator`, `recherche`, `lernplaner`
- `.claude/skills/` – `kurs-anlegen` (mit Vorlagen), `material-update`, `lernsession` (inkl. `lernstand.py`), `klausurphase`
- `Kurse/` – deine Kurse (per `.gitignore` vom Repo ausgeschlossen, ebenso die erzeugten `kurs-*`-Skills und `fachexperte-*`-Agents)

Sprache der Prompts: Deutsch.
