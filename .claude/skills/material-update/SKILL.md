---
name: material-update
description: Verarbeitet neues Kursmaterial im Lernordner – sichten, ordnen, auf Lücken prüfen, Lücken mit bewerteten Quellen recherchieren, Themen-Notizen in Chunks und Wiederholungskarten anlegen. Verwenden, wenn neues Material in einem Kursordner liegt (z. B. in eingang/ oder lose im Kursordner) oder der User „neues Material“, „Material einpflegen“ o. ä. sagt.
argument-hint: <Kurs>
effort: medium
---

# Material-Update

Argument: Kursordner (`$ARGUMENTS`). Ohne Argument: alle Kurse nach neuem Material durchsuchen (Dateien in `eingang/` oder im Kurs-Wurzelordner, die nicht in `_kurs/index.md` stehen) und fragen, welcher.
Hat der Kurs noch kein `_kurs/`, zuerst `/kurs-anlegen`.

Lade den Kurs-Skill `kurs-<kürzel>` (Kürzel steht in `_kurs/kurs.md`), damit das Fachwissen mitläuft.

## Delegieren, nicht selbst lesen
Die schwere Lesearbeit machen die Agents (eigene Modelle/Effort in ihrer Frontmatter). Das Hauptgespräch liest das Material nicht selbst nach, sondern arbeitet mit deren Rückmeldungen. Jeder Auftrag nennt Kurs, konkrete Dateien (bei Fachexperten: Thema, Dateien und Seiten aus der Sichtung) und das erwartete Ergebnis. Regeln aus `CLAUDE.md`, „Sparsam arbeiten“.

## 1. Sichten
Agent `material-sichter` mit Kursordner und Liste der neuen Dateien. Bei vielen/großen Dateien mehrere Instanzen parallel, je eine Dateigruppe.

## 2. Ordnen – mit Bestätigung
Zeige dem User den Einsortier-Plan (Tabelle: Datei → Ziel-Pfad, Art, Themen) und die vorgeschlagenen Änderungen an der Themenlandkarte. **Erst nach seinem OK** verschieben (`mv`, nie löschen, nie überschreiben – bei Namenskonflikt Suffix anhängen). Dann `_kurs/index.md` aktualisieren (Material-Tabelle + Themenlandkarte). Die Themenlandkarte ist die Planungsgrundlage für `plan.py`: neue Themen mit Chunkzahl und Status `neu`; ersetzt neues Material eine `geplant`-Zeile, diese auf `neu` setzen und die geschätzte Chunkzahl (`~N`) durch die echte ersetzen; neu angekündigte Vorlesungen als `geplant` mit `ab`-Datum; Nicht-Prüfungsstoff `optional`. Nummern bestehender Themen nie ändern (Karten-IDs hängen daran). Fundstücke (Klausurtermin, Lernziele, Prüfungsform) in `kurs.md` übernehmen; neuer Klausurtermin → `lernstand.py klausur`.

## 3. Session-Pakete (Themen-Notizen)
Für jedes neue oder erweiterte Thema `themen/NN-kurzname.md` anlegen/ergänzen. Beauftrage dafür den Agent `fachexperte-<kürzel>`, mehrere Instanzen parallel (je ein Thema; kleine Themen desselben Foliensatzes bündeln, damit dasselbe PDF nicht mehrfach gelesen wird).

**Zweck:** Die Lernsession läuft mit niedrigem Denkaufwand und ohne Lesen zwischen den Antworten, damit der User nicht warten muss. Deshalb muss hier alles vorgedacht werden, was live gebraucht wird – fachlich geprüft, im Erklärstil, knapp.

```
# NN – Titel
Quellen: material/…:Seiten, ergaenzungen/…
Baut auf: NN, NN

## Chunk a – <eine Idee>          (Karten-ID: NN-a)
**Vorwissen-Check:** eine Frage
**Technisch:** präzise Erklärung mit Fachbegriffen/Formeln (≤ 120 Wörter)
**Einfach:** dasselbe ohne Jargon (≤ 80 Wörter)
**Alltag:** Beispiel, und wo es hinkt (≤ 60 Wörter)
**Glossar:** jeder vorkommende Begriff/jede Formel in 1–2 Sätzen (Formel: Symbole, Einheit, Mini-Zahlenbeispiel)
**Feynman-Kernpunkte:** 3–5 Punkte, die eine gute Rückerklärung enthalten muss; typische Fehlvorstellungen
**Abruffragen:** 2–3 Fragen für spätere Wiederholungen, mit Kurzantwort
**Material:** Datei:Seiten

## Chunk b – …

## Übungen
Je Chunk-Gruppe 3–6 Aufgaben (Wiedergabe / Anwendung / Transfer) mit Musterlösung Schritt für Schritt.
```

## 4. Lücken bewerten
Agent `luecken-evaluator`. Ergebnis in `_kurs/luecken.md` eintragen (neue IDs fortlaufend L001, L002, …).

## 5. Recherche
Für jede Lücke mit Priorität hoch/mittel einen Agent `recherche` (parallel, mehrere Instanzen; verwandte Lücken bündeln). Niedrige Lücken dem User auflisten und fragen, ob recherchiert werden soll. Danach Status in `luecken.md` setzen und die Ergänzung im passenden Themen-Chunk verlinken (bei Voraussetzungs-Lücken als eigener Chunk *vor* dem Thema).

## 6. Karten
**Keine** Karten für ungelernten Stoff anlegen – Karten entstehen in der Lernsession, wenn ein Chunk durchgenommen wurde. Im Index den Status der neuen Themen auf „neu“ setzen.

## 7. Bericht
Kurz: was einsortiert wurde, neue Themen/Chunks, Lücken (geschlossen/offen) mit den wichtigsten Quellen und ihrer Bewertung, Fehler oder Widersprüche im Material, geschätzte Lernzeit für den neuen Stoff. Wenn das Fachgebiet sich erweitert hat: Kurs-Skill und Fachexperten-Agent ergänzen (neue Teilgebiete, Hürden, Notation).
