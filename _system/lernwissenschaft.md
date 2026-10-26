# Wiederholungsabstände – wissenschaftliche Grundlage

Stand: 2026-10-17. Der Agent `lernplaner` darf diese Datei nach neuer Recherche aktualisieren; geänderte Parameter müssen dann auch in `lernstand.py` (Konstanten oben in der Datei) nachgezogen werden.

## Befunde

1. **Der optimale Abstand hängt davon ab, wie lange man etwas behalten muss.**
   Cepeda, Vul, Rohrer, Wixted & Pashler (2008), *Psychological Science* 19(11), 1095–1102, ca. 1 350 Teilnehmende, Abstände 0–105 Tage, Behaltensintervalle 7–350 Tage.
   Der beste Abstand zwischen zwei Lerndurchgängen liegt grob bei **10–20 % der Zeit bis zur Prüfung** (bei 1 Woche bis zur Prüfung eher 20–40 %, bei 1 Jahr eher 5–10 %). Beispiel: Klausur in 30 Tagen → Abstand von etwa 3–12 Tagen.
   Ein **zu kurzer Abstand schadet deutlich mehr als ein zu langer.**
   → Im Zweifel lieber etwas später wiederholen als zu früh.

2. **Wachsende oder gleiche Abstände – wichtiger ist die erste Wiederholung.**
   Karpicke & Roediger (2007): wachsende Abstände halfen nach 10 Minuten, gleiche Abstände waren nach 2 Tagen besser. Der Unterschied kam vor allem daher, wann die erste Abfrage stattfand: eine leicht verzögerte erste Abfrage verbessert das Langzeitbehalten.
   Kang, Lindsey, Mozer & Pashler (2014), *Psychonomic Bulletin & Review*: über 4 Wochen Training waren wachsende und gleiche Abstände beim Test nach 8 Wochen gleich gut, wachsende hielten aber die Trefferquote während des Trainings höher (motivierender, weniger Frust).
   → Erste Wiederholung **nicht am selben Tag**, sondern nach 1 Tag. Danach wachsende Abstände.

3. **Ziel-Abrufquote ~90 %.** Moderne Algorithmen (FSRS, Nachfolger von SM-2 in Anki) planen die Wiederholung so, dass man zum Zeitpunkt der Abfrage mit ~90 % Wahrscheinlichkeit noch richtig liegt. Höhere Ziele vervielfachen den Aufwand (97 % ≈ dreifache Anzahl Wiederholungen). Die Evidenz dafür kommt vor allem aus Auswertungen großer Anki-Datenmengen, nicht aus Laborstudien – solide als Faustregel, nicht als Naturgesetz.

## Parameter in `lernstand.py`

| Parameter | Wert | Grund |
| --- | --- | --- |
| Erste Wiederholung | +1 Tag | Befund 2 |
| Zweite Wiederholung (nach „gut“) | +3 Tage | übliche SM-2-Startwerte |
| Danach | Abstand × Leichtigkeit (Start 2,5) | wachsende Abstände |
| „vergessen“ (0) | zurück auf 1 Tag, Leichtigkeit −0,2 | |
| „schwer“ (1) | Abstand × 1,2, Leichtigkeit −0,15 | |
| „leicht“ (3) | Abstand × Leichtigkeit × 1,3, Leichtigkeit +0,15 | |
| Obergrenze bei bekanntem Klausurtermin | 15 % der Resttage bis zur Klausur | Befund 1 |
| Letzte Wiederholung | spätestens 1 Tag vor der Klausur | |

Abweichungen pro Kurs (z. B. Vokabeln vs. Herleitungen) werden in `<Kurs>/_kurs/kurs.md` festgehalten.

## Quellen

- Cepeda et al. 2008: https://www.evullab.org/pdf/CepedaVulRohrerWixtedPashler-PS-2008.pdf
- Karpicke & Roediger 2007: https://Www.Gwern.net/doc/psychology/spaced-repetition/2007-karpicke.pdf
- Kang et al. 2014: https://www.doi.org/10.3758/s13423-014-0636-z
- FSRS: https://github.com/open-spaced-repetition
