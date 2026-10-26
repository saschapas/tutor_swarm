# 🐝 tutor_swarm

**Ein Team aus KI-Agenten für [Claude Code](https://claude.com/claude-code), das aus deinem Kursmaterial einen persönlichen Tutor macht.**

Du legst Folien, Skripte und Übungsblätter in einen Ordner. Die Agents sortieren das Material, suchen Lücken, recherchieren fehlende Grundlagen mit bewerteten Quellen und bereiten alles in kleine Lerneinheiten auf. Danach lernst du im Gespräch: Erklärungen, Rückfragen, Übungsaufgaben und Wiederholungen im richtigen Abstand.

*English version below ↓*

---

## ✨ Was es kann

- **Material verstehen:** Folien, PDFs und Übungsblätter sichten, nach Themen ordnen und eine Themenlandkarte anlegen (was baut worauf auf).
- **Lücken finden und schließen:** fehlende Grundlagen, Sprünge in Herleitungen und unerklärte Formeln erkennen. Danach gezielt recherchieren, mit Quellenbewertung (Lehrbücher und Peer-Review vor Wikipedia).
- **Erklären in drei Stufen:** jedes Konzept erst *technisch*, dann *mit einfachen Worten*, dann als *Alltagsbeispiel*. Jedes Symbol in einer Formel wird benannt und an einem Zahlenbeispiel durchgerechnet.
- **Lernen nach der Feynman-Methode:** Nach jedem Chunk erklärst du das Konzept selbst. Der Tutor sagt dir genau, was fehlt.
- **Verteilte Wiederholung:** Gelerntes wird zu Karten, die in wachsenden Abständen wiederkommen. Die Abstände richten sich nach dem Klausurtermin, die lernwissenschaftliche Grundlage steht in `_system/lernwissenschaft.md`.
- **Pro Kurs ein Fachexperte:** Beim Anlegen eines Kurses entstehen ein eigener Skill und ein eigener Agent, die das jeweilige Fach sehr gut kennen (Notation, typische Hürden, Klausuraufgaben).

## 🚀 Schnellstart

```bash
git clone https://github.com/saschapas/tutor_swarm.git
cd tutor_swarm
mkdir -p Kurse/mein_kurs && cp ~/Downloads/folien*.pdf Kurse/mein_kurs/
claude
```

Dann in Claude Code:

| Befehl | Was passiert |
| --- | --- |
| `/kurs-anlegen mein_kurs` | Kurs einrichten, erstes Material sichten, Fachexperten-Skill und -Agent erzeugen |
| `/material-update mein_kurs` | Neues Material einpflegen: sichten → ordnen → Lücken → Recherche → Lerneinheiten und Karten |
| `/lernsession mein_kurs` | Interaktiv lernen: erst fällige Wiederholungen, dann neuer Stoff, dann Übungsaufgaben |
| `/klausurphase mein_kurs` | Intensive Vorbereitung über den gesamten Stoff |

**Voraussetzungen:** Claude Code und Python 3 (für das Wiederholungs-Skript). Optional: `pdftotext` (poppler-utils) zum Lesen von PDFs.

## 🧩 Aufbau

```
CLAUDE.md                      Spielregeln: Erklärstil, Lernmethode, Ordnerkonvention
_system/lernwissenschaft.md    Wiederholungsabstände und ihre Studienlage
.claude/
  agents/
    material-sichter.md        erkennt Art und Themen jeder Datei, schlägt eine Ordnung vor
    luecken-evaluator.md       bewertet, was im Material fehlt, priorisiert
    recherche.md               schließt Lücken mit bewerteten Quellen
    lernplaner.md              verteilt Stoff und Wiederholungen auf die Zeit bis zur Klausur
  skills/
    kurs-anlegen/              Einrichtung + Vorlagen für Kurs-Skill und Fachexperten-Agent
    material-update/           die Aufbereitungs-Pipeline
    lernsession/               die Live-Lernsession + scripts/lernstand.py (Karten)
    klausurphase/              Klausurvorbereitung
Kurse/                         deine Kurse – lokal, per .gitignore nie im Repo
```

Jeder Kurs bekommt diese Struktur:

```
Kurse/<kurs>/
  _kurs/        Stammdaten, Themenlandkarte, Lücken, Quellen, Lernstand, Session-Protokolle
  material/     Originalmaterial, sortiert
  themen/       aufbereitete Lerneinheiten (Chunks)
  ergaenzungen/ recherchierte Ergänzungen mit Quellenangabe
  eingang/      hier neues Material ablegen
```

## ⚙️ Wie es zusammenarbeitet

**Aufbereiten ohne Zeitdruck:** Beim Material-Update arbeiten die Agents im Hintergrund. Sie lesen, prüfen, recherchieren und schreiben fertige Session-Pakete.

**Lernen in Echtzeit:** Die Lernsession läuft im Hauptgespräch, denn nur dort kannst du antworten. Sie greift nur auf die vorbereiteten Pakete zu. So kommen die Antworten schnell und der Lernfluss stockt nicht. Die Lern-Skills laufen mit `effort: low` und antworten ohne Tool-Aufrufe zwischen deinen Antworten. Die automatischen Antwortvorschläge von Claude Code sind in `.claude/settings.json` abgeschaltet, damit du selbst formulierst – das ist der Kern der Abrufübung.

```
 Material ──▶ material-sichter ──▶ luecken-evaluator ──▶ recherche (×n, parallel)
                                                              │
                                                              ▼
 Du ◀──▶ /lernsession ◀── themen/ + lernstand.json ◀── fachexperte-<kurs>
                 ▲
             lernplaner
```

## 🐝 Ist das wirklich ein „Swarm“?

Ehrlich gesagt: im strengen Sinn nicht. Der Name ist eher augenzwinkernd gemeint.

Ein **Schwarm** im Sinne der Schwarmintelligenz besteht aus vielen gleichartigen Agenten ohne zentrale Steuerung. Sie interagieren nur lokal miteinander, und das Gesamtverhalten entsteht von selbst (*Emergenz*), so wie bei Ameisen, die über Duftspuren den kürzesten Weg finden.

Dieses Projekt ist ein **Multi-Agent-System nach dem Orchestrator-Worker-Muster**. Ein zentraler Ablauf (Skill bzw. Hauptgespräch) ruft wenige, spezialisierte Agents in fester Reihenfolge auf. Die Agents reden nicht miteinander, und das Ergebnis ist geplant, nicht emergent. Am schwärmigsten ist noch die Recherche: Mehrere Instanzen laufen parallel, eine pro Lücke. Fachlich heißt das *Fan-out/Fan-in*.

Im LLM-Umfeld wird „Swarm“ allerdings oft locker für „mehrere zusammenarbeitende Agents“ benutzt. In diesem Sinne passt der Name.

## 🔒 Privatsphäre

Deine Kurse, Notizen und dein Lernstand liegen nur lokal in `Kurse/`. Die `.gitignore` schließt sie aus, ebenso die erzeugten kursspezifischen Skills (`kurs-*`) und Agents (`fachexperte-*`), denn darin stehen Kursnamen und Dozierende.

## 🛠️ Anpassen

- **Sprache:** Die Prompts sind auf Deutsch. Englisches Material funktioniert, erklärt wird auf Deutsch mit den englischen Fachbegriffen. Für eine andere Sprache passt du `CLAUDE.md` an.
- **Erklärstil und Methode:** stehen zentral in `CLAUDE.md`. Kursspezifische Abweichungen kommen in `Kurse/<kurs>/_kurs/kurs.md` unter „Methoden“.
- **Wiederholungsabstände:** Konstanten oben in `lernstand.py`. Bitte zusammen mit `_system/lernwissenschaft.md` ändern.

---
---

# 🐝 tutor_swarm (English)

**A team of AI agents for [Claude Code](https://claude.com/claude-code) that turns your course material into a personal tutor.**

Drop slides, lecture notes and problem sheets into a folder. The agents sort the material, find gaps, research missing foundations using rated sources, and break everything down into small learning units. Then you learn through conversation: explanations, questions, exercises, and reviews at the right intervals.

> **Note:** All prompts and the tutor's output are in **German**. English course material works fine, and English technical terms are always given alongside. To use another language, adapt `CLAUDE.md`.

## ✨ Features

- **Understands your material:** reviews slides, PDFs and exercise sheets, groups them by topic, and builds a topic map showing which topic builds on which.
- **Finds and fills gaps:** spots missing prerequisites, jumps in derivations and unexplained formulas, then researches them and rates every source (textbooks and peer-reviewed work rank above Wikipedia).
- **Three-level explanations:** every concept is explained *technically*, then *in plain words*, then with an *everyday analogy*. Every symbol in a formula is named and worked through with a small numeric example.
- **Feynman technique:** after each chunk you explain the concept back in your own words. The tutor points out exactly what's missing.
- **Spaced repetition:** what you've learned becomes cards that come back at growing intervals, tuned to your exam date. The research behind the intervals is summarized in `_system/lernwissenschaft.md`.
- **A subject expert per course:** setting up a course generates a dedicated skill and agent that know the field well, including its notation, typical pitfalls and exam task types.

## 🚀 Quick start

```bash
git clone https://github.com/saschapas/tutor_swarm.git
cd tutor_swarm
mkdir -p Kurse/my_course && cp ~/Downloads/slides*.pdf Kurse/my_course/
claude
```

Then, inside Claude Code:

| Command | What it does |
| --- | --- |
| `/kurs-anlegen my_course` | Set up the course, review the first material, generate the subject-expert skill and agent |
| `/material-update my_course` | Process new material: review → sort → gaps → research → learning units and cards |
| `/lernsession my_course` | Interactive study session: due reviews first, then new material, then exercises |
| `/klausurphase my_course` | Intensive exam preparation across all material |

**Requirements:** Claude Code and Python 3 (for the repetition script). Optional: `pdftotext` (poppler-utils) for reading PDFs.

## 🧩 Structure

| Path | Purpose |
| --- | --- |
| `CLAUDE.md` | Ground rules: explanation style, learning method, folder conventions |
| `_system/lernwissenschaft.md` | Spaced-repetition intervals and the evidence behind them |
| `.claude/agents/material-sichter.md` | *Material reviewer*: identifies the type and topics of each file |
| `.claude/agents/luecken-evaluator.md` | *Gap evaluator*: rates what's missing and prioritizes it |
| `.claude/agents/recherche.md` | *Researcher*: fills gaps using rated sources |
| `.claude/agents/lernplaner.md` | *Study planner*: schedules new material and reviews up to the exam |
| `.claude/skills/kurs-anlegen/` | Course setup + templates for the course skill and expert agent |
| `.claude/skills/material-update/` | The processing pipeline |
| `.claude/skills/lernsession/` | The live study session + `scripts/lernstand.py` (cards) |
| `.claude/skills/klausurphase/` | Exam preparation |
| `Kurse/` | Your courses. Local only, never committed (see `.gitignore`) |

## ⚙️ How it works

**Preparation with no time pressure:** during a material update, the agents work in the background. They read, check, research, and write ready-made session packages.

**Learning in real time:** the study session runs in the main conversation, because that's the only place where you can reply. It only uses the prepared packages, so responses are fast and your flow isn't interrupted. The study skills run at `effort: low` and make no tool calls between your answers. Claude Code's automatic prompt suggestions are switched off in `.claude/settings.json`, so you phrase every answer yourself – that's the whole point of retrieval practice.

## 🐝 Is it really a "swarm"?

Honestly, not in the strict sense. The name is meant with a wink.

In swarm intelligence, a **swarm** is many similar agents with no central control. They interact only locally, and the overall behavior *emerges* on its own, like ants finding the shortest path by following pheromone trails.

This project is a **multi-agent system using the orchestrator–worker pattern**. A central workflow (a skill, or the main conversation) calls a few specialized agents in a fixed order. The agents don't talk to each other, and the outcome is planned, not emergent. The research step comes closest to swarm behavior: several instances run in parallel, one per gap. Technically, that's *fan-out/fan-in*.

That said, in the LLM world "swarm" is often used loosely for "several cooperating agents", and in that sense the name fits.

## 🔒 Privacy

Your courses, notes and learning progress stay local in `Kurse/`. The `.gitignore` excludes them, as well as the generated course-specific skills (`kurs-*`) and agents (`fachexperte-*`), because those contain course and instructor names.

## 🛠️ Customizing

- **Explanation style and method** are defined centrally in `CLAUDE.md`. Course-specific overrides go in `Kurse/<course>/_kurs/kurs.md` under "Methoden".
- **Review intervals** are the constants at the top of `lernstand.py`. Change them together with `_system/lernwissenschaft.md`.
