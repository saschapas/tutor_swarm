---
name: klausurphase
description: Intensives Lernen über den gesamten Stoff eines Kurses in der Klausurenphase am Semesterende – Gesamtüberblick, Schwachstellen, Altklausuren, Probeklausuren. Verwenden, wenn der User in die Klausurvorbereitung geht oder die Klausur näher rückt. Wird verfeinert, sobald es soweit ist.
argument-hint: <Kurs>
effort: low
---

# Klausurphase (Grundgerüst – wird verfeinert)

Läuft im Hauptgespräch. Kurs-Skill `kurs-<kürzel>` laden. Die Lernsession-Regeln (Erklärstil, Feynman, Karten bewerten, **Tempo**) gelten weiter. Planung und Aufgabenerstellung (lernplaner, fachexperte) laufen vorab oder im Hintergrund, nie während der Interaktion.

## Beim ersten Aufruf für einen Kurs
1. Mit dem User klären und in `_kurs/kurs.md` unter „Klausurphase“ festhalten: Klausurtermin und -form, zugelassene Hilfsmittel, verfügbare Lernzeit pro Tag bis zur Klausur, parallele Klausuren in anderen Kursen.
2. `lernstand.py klausur <Kurs> <datum>` (deckelt alle Abstände auf die Restzeit).
3. Agent `lernplaner`: Plan bis zur Klausur über alle Kurse, die in dieser Phase geprüft werden – fällige Karten, Themen mit schwachen Karten, ungelernte Themen, Altklausur-Schwerpunkte.
4. Vorschlag mit dem User abstimmen; **dieses Skill-Dokument danach mit dem vereinbarten Vorgehen ergänzen.**

## Bausteine (Vorschlag)
- **Gesamtlandkarte:** Der User erklärt den Kurs als Ganzes aus dem Kopf (Feynman auf Kursebene); Lücken daraus werden zu Wiederholungs-Chunks.
- **Durchmischtes Üben (Interleaving):** Aufgaben aus verschiedenen Themen gemischt statt blockweise.
- **Altklausuren** unter Zeitdruck, danach Fehleranalyse und Rückführung auf Chunks.
- **Probeklausur** vom `fachexperte-<kürzel>` im Stil der Altklausuren.
- Schwache Karten (`lernstand.py status`) gezielt; fällige Karten weiter täglich.
