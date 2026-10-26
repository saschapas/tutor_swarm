---
name: lernsession
description: Startet eine interaktive Lernsession für einen Kurs im Lernordner – fällige Wiederholungen, dann neuer Stoff in kleinen Chunks (technisch → einfach → Alltagsbeispiel, Feynman-Rückerklärung), dann Übungsaufgaben, am Ende Protokoll und Wiederholungskarten. Verwenden, wenn der User lernen, üben, wiederholen oder eine Session starten will.
argument-hint: <Kurs>
effort: low
---

# Lernsession

Läuft im Hauptgespräch (der User muss antworten können). Argument: Kurs (`$ARGUMENTS`); ohne Argument die Kurse mit fälligen Karten zeigen (`lernstand.py status` je Kurs, in **einem** Bash-Aufruf) und fragen.

`S=python3 .claude/skills/lernsession/scripts/lernstand.py`

## Tempo hat Vorrang

Der Lernfluss darf nicht stocken. Die Denk- und Lesearbeit ist beim Material-Update schon passiert (Session-Pakete in `themen/`); live wird nur noch vorgetragen, gefragt und geprüft.

- **Nach jeder Antwort des Users sofort antworten – ohne Tool-Aufruf.** Tool-Aufrufe nur an festen Stellen: Vorbereitung (einmal), Karten speichern (am Ende eines Blocks), Abschluss.
- **Kein Lesen während der Interaktion.** Alles Nötige wird in der Vorbereitung auf einmal geladen. Fehlt für einen Chunk das Session-Paket, den Chunk aus dem Material erklären, aber das Lesen dafür einmalig *vor* dem Chunk erledigen, nicht zwischen den Antworten.
- **Kurze Nachrichten.** Eine Stufe der Erklärung, eine Frage, eine Rückmeldung pro Nachricht. Richtwert: ≤ 150 Wörter. Lieber drei schnelle Wechsel als eine lange Nachricht.
- **Keine Subagents im Vordergrund.** Der `fachexperte-<kürzel>` läuft nur im Hintergrund (`run_in_background`), z. B. um Übungen vorzubereiten, während die Chunks laufen.
- Rückmeldung auf User-Antworten: direkt mit dem Inhalt anfangen („Richtig – …“, „Fast: …“), keine Vorrede.
- Noten merken statt sofort speichern; gesammelt speichern (siehe unten).

## 0. Vorbereitung (ein einziger Durchgang, ohne Ausgabe)
In **einer Antwort parallel**:
- Kurs-Skill `kurs-<kürzel>` laden (Kürzel in `<Kurs>/_kurs/kurs.md`). Dessen Methoden gehen den allgemeinen vor.
- Lesen: `_kurs/kurs.md`, `_kurs/index.md`, letztes Protokoll in `_kurs/sessions/`.
- Bash: `$S faellig <Kurs>; $S status <Kurs>; ls <Kurs>/eingang`.
Dann die Session-Pakete (`themen/NN-*.md`) der fälligen Karten und der nächsten 2–3 neuen Chunks in **einem** parallelen Schub lesen.
Fehlen Pakete für die nächsten Chunks: `fachexperte-<kürzel>` im Hintergrund beauftragen, sie zu schreiben, und mit Wiederholungen bzw. vorhandenen Paketen beginnen.

## 1. Einstieg – fragen
Eine kurze Nachricht:
- **Wie viel Zeit bleibt, bis neuer Stoff eingepflegt wird?** (Tage)
- Wie viel Zeit hast du jetzt?
- Klausurtermin bestätigen bzw. erfragen (→ `$S klausur`).
- Liegt ungesichtetes Material in `eingang/`: kurz erwähnen, `/material-update` nach der Session anbieten.
Direkt nach der Antwort einen Plan in 2–3 Zeilen nennen und loslegen (keine Rückfrage, außer der Plan ist strittig). Regeln: Wiederholung vor Neuem. Neuer Stoff nur so viel, dass bis zum nächsten neuen Stoff jeder neue Chunk mindestens einmal nach ≥ 1 Tag wiederholt werden kann. Ist viel offen und wenig Zeit: Voraussetzungen für das Kommende zuerst, das offen sagen.
Übungen für den heutigen Stoff jetzt schon im Hintergrund beim `fachexperte-<kürzel>` in Auftrag geben, falls das Paket keine hat.

## 2. Wiederholung (Abrufübung)
Pro fälliger Karte die Abruffrage aus dem Paket stellen – **nicht** den Inhalt vorlesen. Antwort kurz bewerten (Note 0 vergessen · 1 mit Mühe · 2 richtig · 3 mühelos), Note im Kopf behalten, nächste Frage in derselben Nachricht.
Bei 0 oder 1: knappe Neu-Erklärung aus dem Paket, Feynman-Rückerklärung verlangen.
Am Ende des Blocks **ein** Aufruf: `$S bewerten <Kurs> id:note id:note …`.

## 3. Neuer Stoff – Chunk für Chunk
Reihenfolge aus `index.md`. Pro Chunk, jeweils als eigene kurze Nachricht und auf den User wartend, wo eine Frage gestellt wird:
1. **Vorwissen-Check** (eine Frage aus dem Paket). Sitzt es nicht: zuerst die Voraussetzung.
2. **Technisch** – präzise, Fachbegriffe, Formeln.
3. **Einfach** – ohne Jargon.
4. **Alltagsbeispiel** – wenn möglich; sagen, wo es hinkt.
   Stufen 2–4 dürfen in eine Nachricht, wenn sie zusammen kurz bleiben. Jeder Begriff/jede Formel, die vorkommt, wird erklärt (Glossar im Paket).
5. **Feynman:** „Erklär's mir, als wäre ich 12.“ Gegen die Kernpunkte im Paket prüfen: was fehlt, was falsch, wo Jargon statt Erklärung. Genau dort nachbessern, erneut erklären lassen, bis es sitzt.
Die Karten-IDs der fertigen Chunks merken. Nach jedem Chunk kurz: weiter oder Pause?
Am Ende des Blocks (oder vor einer Pause) **ein** Bash-Aufruf mit allen neuen Karten: `$S neu <Kurs> <id> "<Titel>" --quelle … && $S neu …`.

## 4. Übungsaufgaben
Aus dem Paket bzw. vom Hintergrund-Agenten. Steigend Wiedergabe → Anwendung → Transfer. Lösung erst nach eigenem Versuch; Fehler kurz und genau benennen (Rechenfehler / Konzeptfehler / Notation) und auf den Chunk zurückführen. Lösungen gegen die Musterlösung im Paket prüfen statt neu zu rechnen.

## 5. Abschluss (ein Schub paralleler Aufrufe)
- Noch nicht gespeicherte Noten/Karten speichern.
- Protokoll `_kurs/sessions/JJJJ-MM-TT.md` (bei mehreren am Tag `-2` …): Dauer, Wiederholungen mit Noten, neue Chunks, Übungen und Ergebnisse, Hürden, offene Fragen, nächste Schritte.
- `index.md`: Status der Themen (in Arbeit / gelernt).
- Bewährte/gescheiterte Methoden in `kurs.md`; wiederkehrende fachliche Hürden in den Kurs-Skill.
- Dem User in 2–3 Zeilen: wann die nächsten Karten fällig sind, was als Nächstes drankommt.

## Ton
Geduldig, direkt, ermutigend ohne leeres Lob. Fehler sind Information. Eine Frage pro Nachricht, außer beim Einstieg.
