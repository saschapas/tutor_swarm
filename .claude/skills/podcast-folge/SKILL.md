---
name: podcast-folge
description: Macht aus dem Lernstoff Podcast-Folgen (MP3, zwei Stimmen) für den Arbeitsweg – Hinweg-Folge mit dem neuen Stoff für die Abendsession, Rückweg-Folge als Abruf-Quiz mit Denkpausen. Verwenden, wenn der User „Podcast“, „Folge für morgen“, „was zum Hören“ o. ä. sagt.
argument-hint: "[Kurs] [JJJJ-MM-TT] [hin|rueck|beide]"
---

# Podcast-Folge

Der User hört auf dem Arbeitsweg (Dauer und Tage: `_system/profil.md`, lokal). Er hört morgens den neuen Stoff und vertieft ihn abends in der `/lernsession` (Feynman, Übungen). Hören ist die erste Begegnung mit dem Stoff, kein Lernen im Sinne der Karten. Deshalb legt diese Skill **keine Karten an und bewertet keine**.

Pfade relativ zur Projektwurzel (Ordner mit der `CLAUDE.md` des Lernordners).
- Python mit TTS: `PY=_system/venv-podcast/bin/python` (edge-tts + lameenc; ffmpeg ist nicht nötig)
- Vertonung: `$PY .claude/skills/podcast-folge/scripts/podcast.py <skript.md> [--tempo +5%]`
- Ablage: `Kurse/<Kurs>/_kurs/podcast/JJJJ-MM-TT-hin-NN-thema.md` bzw. `…-rueck.md` (+ gleichnamige `.mp3`). Datum = Tag, an dem gehört wird (Standard: morgen, wenn es nach 15 Uhr ist, sonst heute). Datum und Uhrzeit **nicht** mit `date` bestimmen (VM-Uhr geht falsch), sondern mit `python3 .claude/skills/lernsession/scripts/echtdatum.py`.

## Ablauf (ohne Rückfragen durchziehen)

1. **Was dran ist:** `python3 .claude/skills/lernsession/scripts/plan.py --minuten 60 --datum <Hördatum> [--kurs K]` → die vorgeschlagenen neuen Chunks sind der Stoff der Hinweg-Folge (das, was abends in der Session dran ist). **Hinweg = ein Kurs pro Tag** (eine Folge mit einem roten Faden statt Häppchen aus mehreren Fächern). Ohne Kursangabe rotieren: den Kurs mit dem größten Rückstand laut plan.py nehmen. Lief am Vortag schon derselbe Kurs, dann den nächsten. Welcher Kurs zuletzt dran war, zeigen die neuesten `*-hin-*`-Dateien in `Kurse/*/_kurs/podcast/`. **Rückweg = alle Kurse:** `lernstand.py faellig <Kurs> --bis <Hördatum>` für **jeden** Kurs. Die Rückweg-Datei liegt beim Kurs der Hinweg-Folge.
2. **Lesen:** nur die betreffenden Chunk-Abschnitte aus `themen/NN-*.md` (`grep -n '^## Chunk'`, dann `sed -n`). Fehlt ein Paket, zuerst `fachexperte-<kürzel>` beauftragen.
3. **Skripte schreiben** (Format unten). **Jede Folge dauert so lang wie der Weg** (laut `_system/profil.md`; Zahlen unten für 30 min). Gemessenes Tempo inklusive Sprecherwechsel: etwa 120 Wörter/min. Hinweg also **≈ 3400 Wörter + ~2 min Pausen**, Rückweg **≈ 2000 Wörter + ~12 min Pausen**. Reicht der Stoff des Plans nicht, kommen die nächsten Chunks laut Themenlandkarte dazu, höchstens ~8 neue Chunks pro Folge. Die restliche Zeit füllen mehr Beispiele, durchgesprochene Zahlenbeispiele und Querverbindungen zu früheren Themen. Nach dem Rendern die Länge prüfen (Ausgabe des Skripts bzw. MP3-Größe / 6000 = Sekunden). Weicht sie mehr als 3 min ab, Skript kürzen oder ergänzen und neu rendern. Bereits vertonte Zeilen kommen aus dem Cache.
4. **Vertonen:** beide Skripte im Hintergrund rendern (`run_in_background`, dauert ~2 min pro 10 min Audio, braucht Internet). Kurz prüfen: `file *.mp3`.
5. **Melden:** Pfade der MP3s, Länge, welche Chunks drin sind. Ein Satz Hinweis: Abends `/lernsession <Kurs>`, dann wird vertieft.

## Talk-Format (gilt für beide Folgen)
Wunsch des Users: Es soll klingen wie **zwei Leute, die sich unterhalten**, nicht wie Vorlesung mit Fragesteller. Unterhaltsam, aber fachlich exakt.
- **Feste Hosts:** **Jana** (A, Stimme Seraphina) hat den Stoff vorbereitet. Sie ist trocken-witzig und liebt schräge Beispiele. **Tim** (B, Stimme Florian) teilt den fachlichen Hintergrund des Users (`_system/profil.md`), ist neugierig und skeptisch. Er bringt eigene Vergleiche aus seinem Fach und dem Alltag ein. Die beiden reden sich mit Namen an, duzen sich und den Hörer.
- **Gespräch statt Abfrage:** Beide tragen Inhalt bei. Tim stellt eigene Vermutungen auf, liegt dabei auch mal daneben, und Jana korrigiert ihn. Genau dort landen die typischen Fehlvorstellungen aus dem Paket. Sie unterbrechen sich („Moment, Moment…“), reagieren („Ach krass“, „Okay, das ist fies“), widersprechen sich und lachen über eigene Beispiele. Running Gags und Rückbezüge auf frühere Folgen oder Themen sind erwünscht.
- **Der Lernaufbau bleibt darunter:** Jeder Chunk läuft technisch → einfach → Alltagsbeispiel + wo es hinkt → Falle. Er klingt aber nicht wie eine Gliederung, die Übergänge kommen aus dem Gespräch („Wie würdest du das deiner Oma erklären?“). Fachbegriffe englisch, wie in Material und Klausur.
- **Hörer einbeziehen:** Vor kniffligen Stellen wendet sich jemand an den Hörer („Überleg mal kurz mit, …“, `[PAUSE 5–10]`), erst danach antworten die Hosts.
- Tempo: viele kurze Beiträge, auch Einwortreaktionen als eigene Zeile („B: Echt?“). Lange Monologe vermeiden, höchstens ~5 Sätze am Stück.

## Hinweg-Folge (neuer Stoff)
- Pro Chunk der **Erklärstil aus CLAUDE.md**: Vorwissen-Frage mit `[PAUSE 5]` → technisch (Fachbegriffe englisch mitnennen) → einfach → Alltagsbeispiel + wo es hinkt → typische Fehlvorstellung. Alle Inhalte nur aus dem Paket; was dort als extern markiert ist, auch so ansagen.
- Einstieg: worum es geht und warum (Motivation, Einordnung in die Themenlandkarte). Schluss: Zusammenfassung in 4–6 Punkten, dann 4–6 Abruffragen aus dem Paket mit `[PAUSE 7]` bis `[PAUSE 10]`, die letzte eine Transferfrage „zum Weiterdenken für den Tag“.

## Rückweg-Folge (Abruf-Quiz)
- Ziel: Abrufübung, nicht Wiederhören. Format **Quizshow**: Jana stellt die Fragen und zählt Punkte, Tim spielt mit. Nach jeder Frage kommt die Ansage „…und du?“ und `[PAUSE 8–12]` für den Hörer. Erst danach antwortet Tim (1–3 Sätze). Ab und zu liegt Tim daneben, dann fragt Jana zurück und der Hörer soll den Fehler finden (`[PAUSE]`), das ist starke Abrufübung. Spielstand und kleine Frotzeleien halten es locker.
- Inhalt gemischt (interleaving): ~60 % Fragen zum Stoff der Hinweg-Folge desselben Tages (andere Formulierung als dort, mehr „warum“ und „was wäre, wenn“), ~40 % fällige Karten bis zum Hördatum **aus allen Kursen** (Abruffragen aus deren Chunks, kursweise in eigenen Runden, die Jana ansagt: „Runde <Kurs>!“). Sind zu viele Karten fällig, haben die überfälligsten Vorrang. Damit 30 min sinnvoll gefüllt sind, mischen: ~25 kurze Fragen, 2–3 Kopfrechen-Aufgaben (z. B. einen Schritt einer Formel mit runden Zahlen), 3–4 **Feynman-laut-Aufträge** („Erklär laut, als wäre ich zwölf: …“, `[PAUSE 40]`, danach die Kernpunkte aus dem Paket als Checkliste). Reichen heutiger Stoff und fällige Karten nicht, kommen ältere, bald fällige Karten dazu. Schluss: „Was davon war wackelig? Merk es dir für die Session heute Abend.“

## Audio-Regeln für Skripte
- Format: eine Zeile pro Beitrag `A: …` / `B: …`, Pausen `[PAUSE n]`. Zeilen mit `#` sind Gliederung und werden nicht gesprochen. Kopf: Titel, Quelle (Paket + Folien), Stimmen (A = Jana, B = Tim).
- Kurze Sätze, gesprochene Sprache, ein Beitrag höchstens ~6 Sätze, dann kommt die andere Stimme.
- **Keine Symbole, kein Code, keine Tabellen.** Formeln ausformulieren („Sigma von x ist die Wurzel aus …“), jedes Symbol beim Namen nennen, Zahlenbeispiele mit runden Zahlen. Abkürzungen beim ersten Mal ausschreiben. Prozent, Brüche und Zehnerpotenzen in Worten.
- Wo Material nur visuell funktioniert (Diagramm, Herleitung über viele Zeilen): Kernidee in Worten, dann „schau dir heute Abend in der Formelsammlung die Herleitung an“.
- Nach dem Schreiben einmal die eigenen Zeilen auf Symbole (`grep -nE '[=∑√^_|<>]'`) prüfen.
