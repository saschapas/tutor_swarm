---
name: kurs-anlegen
description: Richtet einen neuen Kursordner im Lernordner ein – Ordnerstruktur, Stammdaten, erste Sichtung des Materials und einen kursspezifischen Skill (kurs-<kürzel>) plus Fachexperten-Agent (fachexperte-<kürzel>), die das Fachgebiet sehr gut kennen. Verwenden, wenn der User einen neuen Kurs/ein neues Fach anlegt oder ein Kursordner noch keinen _kurs/-Ordner hat.
argument-hint: <Kursordner>
---

# Kurs anlegen

Argument: Name des Kursordners in `Kurse/` (`$ARGUMENTS`). Fehlt es, liste die Ordner ohne `_kurs/` auf und frage.

## 1. Stammdaten erfragen

Frage den User in **einer** Nachricht (alles optional, „weiß ich noch nicht“ ist ok):
- Voller Kursname, Studiengang/Semester
- Klausurtermin und Prüfungsform (schriftlich, mündlich, Projekt, …)
- Wann/wie oft kommt neues Material (z. B. wöchentlich nach der Vorlesung am Dienstag)?
- Vorwissen in diesem Fach, bekannte Schwächen
- Besondere Wünsche an die Lernmethode für diesen Kurs

Leite ein kurzes Kürzel ab (kleinbuchstaben, ohne Umlaute, z. B. `ana1`, `bwl-rewe`) und bestätige es mit dem User.

## 2. Struktur anlegen

```
mkdir -p "Kurse/<Kurs>"/{_kurs/sessions,material/{vorlesung,uebung,loesung,literatur,klausur,organisatorisch,sonstiges},themen,ergaenzungen,eingang}
```
Lege `_kurs/kurs.md` aus `vorlagen/kurs.md` an (Werte einsetzen), dazu leere `index.md`, `luecken.md`, `quellen.md` mit den Überschriften aus den Vorlagen. Klausurtermin bekannt → `python3 .claude/skills/lernsession/scripts/lernstand.py klausur <Kurs> <datum>`.

## 3. Erstes Material verarbeiten

Liegt schon Material im Ordner, führe den Ablauf aus `.claude/skills/material-update/SKILL.md` aus (sichten → ordnen → Lücken → Recherche → Themen & Karten).

## 4. Kursspezifischen Skill und Agent erzeugen

**Existieren `kurs-<kürzel>` und `fachexperte-<kürzel>` schon**, nicht neu erzeugen: das Kürzel übernehmen, in Schritt 1 die dort schon bekannten Stammdaten nur noch bestätigen lassen und die Dateien mit den Erkenntnissen aus der Sichtung ergänzen.

Sonst:

Erst **nach** der Sichtung, damit sie das tatsächliche Fachgebiet kennen. Bestimme aus Material und Stammdaten: Fachgebiet und Teilgebiete, Standardliteratur des Fachs, typische Notation, typische Verständnishürden und Fehlvorstellungen, typische Aufgabentypen in Klausuren, sinnvolle Lernmethoden für dieses Fach (Rechnen üben, Herleitungen nachvollziehen, Definitionen auswendig, Fallanalysen, Programmieren, Vokabeln …).

- `.claude/skills/kurs-<kürzel>/SKILL.md` aus `vorlagen/kurs-skill.md`
- `.claude/agents/fachexperte-<kürzel>.md` aus `vorlagen/fachexperte.md`

Danach den Agent global verlinken, damit er auch außerhalb des Repos mit seinem Modell läuft: `ln -s "$PWD/.claude/agents/fachexperte-<kürzel>.md" ~/.claude/agents/`.

Fülle alle `{{…}}`-Felder konkret und fachlich gehaltvoll aus – kein generischer Text. Diese Dateien sind lebendig: Sie werden bei jedem Material-Update ergänzt, wenn neue Themen dazukommen.

## 5. Abschluss

Zeige dem User: Themenlandkarte, Lücken mit Status, wie viele Karten angelegt wurden, und wie er weitermacht (`/lernsession <Kurs>`; neues Material in `<Kurs>/eingang/` legen, dann `/material-update <Kurs>`).
