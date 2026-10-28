---
name: lernsession
description: Startet eine interaktive Lernsession für einen Kurs im Lernordner – fällige Wiederholungen, dann neuer Stoff in kleinen Chunks (technisch → einfach → Alltagsbeispiel, Feynman-Rückerklärung), dann Übungsaufgaben, am Ende Protokoll und Wiederholungskarten. Verwenden, wenn der User lernen, üben, wiederholen oder eine Session starten will.
argument-hint: <Kurs>
effort: low
---

# Lernsession

Läuft im Hauptgespräch (der User muss antworten können). Argument: Kurs (`$ARGUMENTS`) oder leer. **Ohne Argument ist das der Normalfall:** `plan.py` entscheidet, welche Kurse heute drankommen (Tagesplan über mehrere Kurse, nacheinander).

`S=python3 .claude/skills/lernsession/scripts/lernstand.py`
`P=python3 .claude/skills/lernsession/scripts/plan.py`

## Datum und Neuaufteilung (bei jedem Start)

Der User lernt unregelmäßig. Deshalb gibt es keinen festen Plan, der „nachgeholt“ werden muss: `plan.py` rechnet bei jedem Start vom **heutigen Datum** und vom **tatsächlichen Lernstand** (Karten = gelernte Chunks) aus und verteilt allen offenen Stoff – vorhandenen und laut Vorlesungsplan angekündigten – gleichmäßig auf die Wochen bis zum Ziel (Klausur − 14 Tage Puffer). Verpasste Tage verteilen sich so automatisch auf die restlichen Wochen.
- Die Ausgabe enthält: Wochensoll je Kurs, was diese Woche noch offen ist, fällige Karten, einen **Tagesvorschlag** (konkrete Karten- und Chunk-IDs für die angegebene Zeit) und fehlende Session-Pakete.
- Den Tagesvorschlag übernehmen. Abweichen nur, wenn der User etwas anderes will (z. B. „heute nur <Kurs>“ → `$P --kurs <kurs> --minuten N`).
- Liegt der User deutlich zurück (Wochensoll > ~1,5× des ursprünglichen Solls oder Wochenstunden unrealistisch), das **einmal kurz und sachlich** sagen und Prioritäten vorschlagen: Voraussetzungen für Kommendes und nahe Klausuren zuerst, optionale/Vorschau-Themen streichen.

## Tempo hat Vorrang

**Zeit im Blick behalten (User-Feedback 2026-10-27).** Beim Start die Uhrzeit festhalten (`date +%H:%M` im Vorbereitungsaufruf) und daraus ein Zeitbudget pro Chunk ableiten (verfügbare Minuten ÷ geplante Chunks). Pro Chunk höchstens **eine** Prüffrage plus bei Fehler eine Korrektur, dann weiter – nicht mehrfach zum selben Punkt nachfragen. Bei jedem Tool-Aufruf an Blockgrenzen die Uhrzeit mitnehmen und den Plan anpassen; dem User beim Kurswechsel kurz sagen, wie viel Zeit noch bleibt und was davon noch drankommt. Lieber weniger Chunks sauber abschließen als einen Chunk zerfragen.
**Einmal nachfragen, dann weiter:** Sitzt die Antwort nach einer Korrektur und einer Rückfrage noch nicht, nicht weiterbohren. Stattdessen: Karte beim Speichern mit Note 0–1 anlegen bzw. bewerten (kommt so früher und öfter wieder) und den Punkt im Protokoll unter „Hürden“ sowie in `kurs.md` → „Notizen aus Sessions“ als Schwachstelle festhalten, damit spätere Sessions ihn gezielt und intensiver wiederholen.

Der Lernfluss darf nicht stocken. Die Denk- und Lesearbeit ist beim Material-Update schon passiert (Session-Pakete in `themen/`); live wird nur noch vorgetragen, gefragt und geprüft.

- **Nach jeder Antwort des Users sofort antworten – ohne Tool-Aufruf.** Tool-Aufrufe nur an festen Stellen: Vorbereitung (einmal), Karten speichern (am Ende eines Blocks), Abschluss.
- **Kein Lesen während der Interaktion.** Alles Nötige wird in der Vorbereitung auf einmal geladen. Fehlt für einen Chunk das Session-Paket, den Chunk aus dem Material erklären, aber das Lesen dafür einmalig *vor* dem Chunk erledigen, nicht zwischen den Antworten.
- **Kurze Nachrichten.** Eine Stufe der Erklärung, eine Frage, eine Rückmeldung pro Nachricht. Richtwert: ≤ 150 Wörter. Lieber drei schnelle Wechsel als eine lange Nachricht.
- **Keine Subagents im Vordergrund.** Der `fachexperte-<kürzel>` läuft nur im Hintergrund (`run_in_background`), z. B. um Übungen vorzubereiten, während die Chunks laufen.
- Rückmeldung auf User-Antworten: direkt mit dem Inhalt anfangen („Richtig – …“, „Fast: …“), keine Vorrede.
- Noten merken statt sofort speichern; gesammelt speichern (siehe unten).

## 0. Einstieg – eine Frage
Sofort, ohne Tool-Aufruf: **„Wie viel Zeit hast du heute?“** (Mit Argument zusätzlich nichts weiter fragen; Klausurtermine stehen in `kurs.md` und werden nicht jedes Mal bestätigt.)

## 1. Vorbereitung (ein einziger Durchgang)
Nach der Antwort in **einer Antwort parallel**:
- Bash: `$P --minuten <N> [--kurs <Kurs>]; ls Kurse/*/eingang` (ein Aufruf).
- Für die Kurse im Tagesvorschlag: Kurs-Skill `kurs-<kürzel>` laden (Methoden gehen den allgemeinen vor), `_kurs/kurs.md` und letztes Protokoll in `_kurs/sessions/` lesen.
Dann die Session-Pakete (`themen/NN-*.md`) der fälligen Karten und der vorgeschlagenen Chunks in **einem** parallelen Schub lesen – bei fälligen Karten nur deren Chunk-Abschnitt (`grep -n '^## Chunk'`, dann `sed -n`), nicht das ganze Paket.
Danach **pro Kurs eine Formelsammlung** als HTML schreiben: `Kurse/<Kurs>/_kurs/formelsammlungen/JJJJ-MM-TT.html` (bei mehreren Sessions am Tag `-2` …). Inhalt: alle Formeln, Regeln und Merktabellen der heutigen Chunks und fälligen Karten, gegliedert nach Karten-ID (Anker `#<kürzel>-<karte>` o. ä.), mit Mini-Beispielen und typischen Fehlern. Formeln in LaTeX, gerendert mit MathJax 3 (`tex-svg`, cdnjs), helles und dunkles Farbschema. **Kein Claude-Artifact**, nur die lokale Datei. Vorlage: Kopf und CSS der letzten vorhandenen Datei im Ordner (nur bis `</style>` lesen, z. B. `sed '/<\/style>/q'`). Im Chat bei Formeln auf die Karten-ID in der Formelsammlung verweisen; im Chat selbst Formeln schlicht im Stil Σ_{i=1}^{3} i, x_i², ∂f/∂μ schreiben (Unicode-Symbole plus _{} und ^{}, keine Backticks, kein \sum), Wunsch des Users. Dem User zu Beginn den Pfad nennen.
Fehlen Pakete für vorgeschlagene Chunks: `fachexperte-<kürzel>` im Hintergrund beauftragen, sie zu schreiben, und mit Wiederholungen bzw. vorhandenen Paketen beginnen.
Dann **eine** kurze Nachricht: Datum/Semesterwoche, der Tagesplan in 2–3 Zeilen (welche Kurse, wie viele Wiederholungen, welche Chunks), ggf. Hinweis auf Rückstand oder auf Material in `eingang/` (`/material-update` nach der Session anbieten) – und direkt mit der ersten Frage loslegen.
Übungen für den heutigen Stoff im Hintergrund beim `fachexperte-<kürzel>` in Auftrag geben, falls das Paket keine hat.
Mehrere Kurse am Tag: Kurs für Kurs abarbeiten (Wiederholungen aller Kurse zuerst, dann neuer Stoff), beim Kurswechsel Kurs-Skill wechseln und Karten des alten Kurses speichern.

## 2. Wiederholung (Abrufübung)
**Schnelldurchgang (User-Wunsch 2026-10-29):** Wiederholungen kurz halten, damit mehr Zeit für neuen Stoff bleibt – pro Kurs alle fälligen Karten in **einer** Nachricht als Kurzfragen (a, b, c …), User antwortet stichwortartig. Danach eine Nachricht mit allen Korrekturen + Merkhilfen und höchstens einer Kontrollfrage, dann nächster Kurs. Lieber öfter kurz wiederholen als selten lang.
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
**Schon als Podcast gehört?** `plan.py` erkennt die Hinweg-Folgen des Tages selbst und markiert deren Chunks im Tagesvorschlag mit * (sie stehen vorn); „Rückweg-Quiz gehört“ heißt: Wiederholungen dieses Kurses im Schnelldurchgang. Sonst gilt: Wenn es in `_kurs/podcast/` eine Hinweg-Folge von heute zu dem Chunk gibt (`ls Kurse/<Kurs>/_kurs/podcast/<heute>-hin-*` im Vorbereitungs-Schub), dann einmal fragen, ob der User sie gehört hat. Falls ja: die Stufen 2–4 weglassen, nach dem Vorwissen-Check direkt zu Feynman gehen und nur bei Lücken erklären. Das Hören zählt als erste Begegnung mit dem Stoff, die Session ist die Vertiefung. Karten entstehen trotzdem erst hier.
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
