#!/usr/bin/env python3
"""Wiederholungskarten eines Kurses verwalten (<Kurs>/_kurs/lernstand.json).

Grundlage der Parameter: _system/lernwissenschaft.md
"""
import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import echtdatum

ERSTER_ABSTAND = 1
ZWEITER_ABSTAND = 3
START_LEICHTIGKEIT = 2.5
MIN_LEICHTIGKEIT = 1.3
KLAUSUR_ANTEIL = 0.15  # max. Abstand als Anteil der Resttage bis zur Klausur

KURSE = Path(__file__).resolve().parents[4] / "Kurse"


def pfad(kurs):
    return KURSE / kurs / "_kurs" / "lernstand.json"


def laden(kurs):
    p = pfad(kurs)
    if not (KURSE / kurs).is_dir():
        sys.exit(f"Kurs-Ordner nicht gefunden: {KURSE / kurs}")
    if not p.exists():
        return {"klausur": None, "karten": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def speichern(kurs, daten):
    p = pfad(kurs)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def heute():
    return echtdatum.heute()


def deckeln(abstand, klausur):
    """Abstand an den Klausurtermin anpassen (Cepeda et al. 2008)."""
    if not klausur:
        return abstand
    rest = (date.fromisoformat(klausur) - heute()).days
    if rest <= 1:
        return 1
    obergrenze = max(1, round(rest * KLAUSUR_ANTEIL))
    return max(1, min(abstand, obergrenze, rest - 1))


def cmd_neu(a):
    d = laden(a.kurs)
    if a.id in d["karten"]:
        sys.exit(f"Karte existiert schon: {a.id}")
    abstand = deckeln(ERSTER_ABSTAND, d["klausur"])
    d["karten"][a.id] = {
        "titel": a.titel,
        "quelle": a.quelle,
        "erstellt": heute().isoformat(),
        "abstand": abstand,
        "leichtigkeit": START_LEICHTIGKEIT,
        "wiederholungen": 0,
        "faellig": (heute() + timedelta(days=abstand)).isoformat(),
        "verlauf": [],
    }
    speichern(a.kurs, d)
    print(f"neu: {a.id} – fällig {d['karten'][a.id]['faellig']}")


def bewerten(d, karten_id, note):
    k = d["karten"].get(karten_id) or sys.exit(f"Unbekannte Karte: {karten_id}")
    ease = k["leichtigkeit"]
    if note == 0:
        abstand, ease, k["wiederholungen"] = ERSTER_ABSTAND, ease - 0.2, 0
    else:
        if k["wiederholungen"] == 0:
            basis = ZWEITER_ABSTAND if note >= 2 else ERSTER_ABSTAND
        else:
            basis = k["abstand"]
        if note == 1:
            abstand, ease = basis * 1.2, ease - 0.15
        elif note == 2:
            abstand = basis * (1 if k["wiederholungen"] == 0 else ease)
        else:
            abstand, ease = basis * (1.3 if k["wiederholungen"] == 0 else ease * 1.3), ease + 0.15
        k["wiederholungen"] += 1
    k["leichtigkeit"] = round(max(MIN_LEICHTIGKEIT, ease), 2)
    k["abstand"] = deckeln(max(1, round(abstand)), d["klausur"])
    k["faellig"] = (heute() + timedelta(days=k["abstand"])).isoformat()
    k["verlauf"].append({"datum": heute().isoformat(), "note": note})
    print(f"{karten_id}: Note {note} → nächster Termin {k['faellig']} (in {k['abstand']} Tagen)")


def cmd_bewerten(a):
    """Einzeln: <id> <note>. Mehrere auf einmal: <id>:<note> <id>:<note> ..."""
    if len(a.werte) == 2 and ":" not in a.werte[0]:
        paare = [(a.werte[0], a.werte[1])]
    else:
        paare = [w.rsplit(":", 1) for w in a.werte]
    d = laden(a.kurs)
    for karten_id, note in paare:
        if note not in {"0", "1", "2", "3"}:
            sys.exit(f"Note muss 0–3 sein: {karten_id}:{note}")
        bewerten(d, karten_id, int(note))
    speichern(a.kurs, d)


def cmd_faellig(a):
    d = laden(a.kurs)
    bis = a.bis or heute().isoformat()
    faellig = sorted(
        ((k["faellig"], i, k["titel"], k["quelle"]) for i, k in d["karten"].items() if k["faellig"] <= bis)
    )
    if not faellig:
        print(f"Keine Karten fällig bis {bis}.")
    for f, i, t, q in faellig:
        print(f"{f}  {i}  {t}  [{q}]")


def cmd_klausur(a):
    d = laden(a.kurs)
    date.fromisoformat(a.datum)
    d["klausur"] = a.datum
    for k in d["karten"].values():
        k["abstand"] = deckeln(k["abstand"], a.datum)
        neu = (heute() + timedelta(days=k["abstand"])).isoformat()
        k["faellig"] = min(k["faellig"], neu)
    speichern(a.kurs, d)
    print(f"Klausurtermin {a.datum} gesetzt, Abstände angepasst.")


def cmd_status(a):
    d = laden(a.kurs)
    karten = d["karten"].values()
    h = heute().isoformat()
    woche = (heute() + timedelta(days=7)).isoformat()
    print(f"Kurs: {a.kurs}")
    print(f"Klausur: {d['klausur'] or 'nicht gesetzt'}")
    print(f"Karten: {len(d['karten'])}, heute fällig: {sum(k['faellig'] <= h for k in karten)}, "
          f"in 7 Tagen fällig: {sum(k['faellig'] <= woche for k in karten)}")
    schwach = sorted((k["leichtigkeit"], i) for i, k in d["karten"].items() if k["leichtigkeit"] < 2.0)
    if schwach:
        print("Schwache Karten: " + ", ".join(i for _, i in schwach[:10]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    s = p.add_subparsers(dest="befehl", required=True)
    x = s.add_parser("neu"); x.add_argument("kurs"); x.add_argument("id"); x.add_argument("titel")
    x.add_argument("--quelle", default=""); x.set_defaults(f=cmd_neu)
    x = s.add_parser("bewerten"); x.add_argument("kurs"); x.add_argument("werte", nargs="+")
    x.set_defaults(f=cmd_bewerten)
    x = s.add_parser("faellig"); x.add_argument("kurs"); x.add_argument("--bis"); x.set_defaults(f=cmd_faellig)
    x = s.add_parser("klausur"); x.add_argument("kurs"); x.add_argument("datum"); x.set_defaults(f=cmd_klausur)
    x = s.add_parser("status"); x.add_argument("kurs"); x.set_defaults(f=cmd_status)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
