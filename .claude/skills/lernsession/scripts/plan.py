#!/usr/bin/env python3
"""Verteilt den offenen Stoff aller Kurse ab heute auf die Wochen bis zur Klausur.

Wird bei jedem Session-Start aufgerufen. Rechnet immer vom aktuellen Datum und
vom tatsächlichen Lernstand aus – verpasste Tage oder Wochen verteilen sich so
automatisch auf die verbleibende Zeit, ohne dass ein Plan „nachgeholt“ werden muss.

Datenquellen pro Kurs:
  _kurs/index.md       Themenlandkarte (Nr, Chunks, Status, ab)
  _kurs/kurs.md        Plan-Ziel bzw. Klausurtermin (erstes Datum JJJJ-MM-TT)
  _kurs/lernstand.json Karten; eine Karte <Nr>-<buchstabe> = ein gelernter Chunk
  _kurs/podcast/       Podcast-Folgen (Skill podcast-folge); <Datum>-hin-*.md = Stoff,
                       den der User auf dem Hinweg gehört hat → kommt abends zuerst dran,
                       nur noch Feynman/Übung (MIN_PRO_CHUNK_GEHOERT)

  plan.py [--minuten 60] [--kurs K ...] [--datum JJJJ-MM-TT]
"""
import argparse
import json
import math
import re
from datetime import date, timedelta
from pathlib import Path

import echtdatum

SEMESTER_START = date(2026, 10, 12)   # Montag der 1. Vorlesungswoche (Beispielwert)
VORLESUNGSENDE = date(2027, 2, 5)      # Standard-Ziel, wenn kein Termin bekannt
PUFFER_TAGE = 14                       # vor der Klausur: nur noch Klausurphase/Wiederholung
MIN_PRO_CHUNK = 5                      # gemessen 2026-10-29: 9 Chunks in ~46 min mit Feynman (2026-10-27: 2,5–5 min)
MIN_PRO_KARTE = 1.2                    # gemessen 2026-10-29: 22 Karten in ~26 min im Schnelldurchgang
REVIEWS_PRO_CHUNK = 6                  # Wiederholungen je Karte bis zum Plan-Ziel (Simulation 2026-10-27: 5-9)
MIN_MO_DO = 120                        # Lernzeit pro Abend Mo-Do
MIN_PORTION = 120                      # eine Wochenend-Portion (Sa/So)
PENDEL_TAGE = 0                        # Tage pro Woche mit Podcast auf dem Arbeitsweg (Skill podcast-folge)
MAX_CHUNKS_FOLGE = 8                   # höchstens so viele neue Chunks pro Hinweg-Folge (Skill podcast-folge)
MIN_PRO_CHUNK_GEHOERT = 2              # Session-Zeit für schon gehörten Chunk: Vorwissen-Check + Feynman
EFFEKTIV = 0.85                        # Anteil der Zeit, der wirklich zum Lernen taugt

# Persönliche Werte (Semesterdaten, Lernzeiten, Pendeltage) überschreiben die Standards oben,
# z. B. {"SEMESTER_START": "2026-10-12", "PENDEL_TAGE": 5}. Liegt lokal, nicht im Repo.
LOKAL = Path(__file__).resolve().parents[4] / "_system" / "plan-lokal.json"
if LOKAL.exists():
    for _k, _v in json.loads(LOKAL.read_text(encoding="utf-8")).items():
        if _k in globals():
            globals()[_k] = date.fromisoformat(_v) if isinstance(globals()[_k], date) else _v

KURSE = Path(__file__).resolve().parents[4] / "Kurse"
DATUM = re.compile(r"\d{4}-\d{2}-\d{2}")


def montag(d):
    return d - timedelta(days=d.weekday())


def themen_lesen(kurs):
    zeilen = (KURSE / kurs / "_kurs" / "index.md").read_text(encoding="utf-8").splitlines()
    kopf, themen = None, []
    for z in zeilen:
        if not z.startswith("|"):
            if kopf and themen:
                break
            continue
        zellen = [c.strip() for c in z.strip().strip("|").split("|")]
        if kopf is None:
            if "Nr" in zellen and "Chunks" in zellen:
                kopf = zellen
            continue
        if set(zellen[0]) <= set("-: "):
            continue
        t = dict(zip(kopf, zellen))
        status = t.get("Status", "").lower()
        if status.startswith("optional"):
            continue
        m = re.search(r"\d+", t.get("Chunks", ""))
        ab = DATUM.search(t.get("ab", ""))
        themen.append({
            "nr": t["Nr"], "titel": t.get("Thema", ""), "chunks": int(m.group()) if m else 0,
            "status": status, "datei": t.get("Datei", ""),
            "ab": date.fromisoformat(ab.group()) if ab else None,
        })
    return themen


def ziel_lesen(kurs):
    text = (KURSE / kurs / "_kurs" / "kurs.md").read_text(encoding="utf-8")
    for feld in ("Plan-Ziel", "Klausurtermin"):
        m = re.search(rf"\*\*{feld}:\*\*([^\n]*)", text)
        if m and DATUM.search(m.group(1)):
            return date.fromisoformat(DATUM.search(m.group(1)).group()), True
    return VORLESUNGSENDE, False


def karten_lesen(kurs):
    p = KURSE / kurs / "_kurs" / "lernstand.json"
    return json.loads(p.read_text(encoding="utf-8"))["karten"] if p.exists() else {}


def podcast_lesen(kurs, tag):
    """Chunk-IDs der Hinweg-Folge(n) des Tages und ob es eine Rückweg-Folge gibt."""
    ordner = KURSE / kurs / "_kurs" / "podcast"
    if not ordner.is_dir():
        return [], False
    ids = []
    for f in sorted(ordner.glob(f"{tag.isoformat()}-hin-*.md")):
        ids += re.findall(r"^# (\d{2}-[a-z])\b", f.read_text(encoding="utf-8"), re.M)
    return ids, any(ordner.glob(f"{tag.isoformat()}-rueck*.md"))


def kurs_planen(kurs, heute):
    themen, karten = themen_lesen(kurs), karten_lesen(kurs)
    klausur, bekannt = ziel_lesen(kurs)
    ende = klausur - timedelta(days=PUFFER_TAGE)
    if ende < heute + timedelta(days=7):
        ende = klausur - timedelta(days=1)
    woche0 = montag(heute)

    # offene Chunks je Thema, in Themenreihenfolge
    gelernt = {}
    diese_woche = 0
    for kid, k in karten.items():
        nr = kid.split("-")[0]
        gelernt[nr] = gelernt.get(nr, 0) + 1
        if k.get("erstellt", "") >= woche0.isoformat():
            diese_woche += 1
    offen = []  # (nr, buchstabe, verfügbar_ab, datei, titel, geschätzt)
    for t in themen:
        n_gelernt = t["chunks"] if t["status"].startswith("gelernt") else 0
        n_gelernt = max(n_gelernt, gelernt.get(t["nr"], 0))
        for i in range(n_gelernt, t["chunks"]):
            offen.append((t["nr"], chr(ord("a") + i), t["ab"] or heute, t["datei"], t["titel"],
                          t["status"].startswith("geplant")))

    # Wochen simulieren (ab Montag dieser Woche, damit das Wochensoll stabil bleibt)
    wochen = []
    w = woche0
    while w <= ende:
        wochen.append(w)
        w += timedelta(days=7)
    if not wochen:
        wochen = [woche0]
    rest = len(offen) + diese_woche
    queue = list(offen)
    soll = []
    for i, w in enumerate(wochen):
        sonntag = w + timedelta(days=6)
        quote = math.ceil(rest / (len(wochen) - i)) if rest else 0
        verfuegbar = [c for c in queue if c[2] <= sonntag]
        if i == 0:
            nehmen = max(0, quote - diese_woche)
            quote_gesamt = quote
        else:
            nehmen = quote
        genommen = verfuegbar[:nehmen]
        for c in genommen:
            queue.remove(c)
        geschafft = len(genommen) + (diese_woche if i == 0 else 0)
        soll.append((w, geschafft if i else quote_gesamt, len(genommen)))
        rest -= geschafft
    gehoert, rueck = podcast_lesen(kurs, heute)
    return {
        "gehoert": [c for c in offen if f"{c[0]}-{c[1]}" in gehoert and c[2] <= heute],
        "rueck": rueck,
        "kurs": kurs, "klausur": klausur, "bekannt": bekannt, "ende": ende, "wochen": soll,
        "offen": offen, "offen_jetzt": [c for c in offen if c[2] <= heute],
        "diese_woche_gelernt": diese_woche,
        "noch_diese_woche": soll[0][2] if soll else 0,
        "faellig": sorted(kid for kid, k in karten.items() if k["faellig"] <= heute.isoformat()),
        "faellig7": sum(k["faellig"] <= (heute + timedelta(days=7)).isoformat() for k in karten.values()),
        "pakete_fehlen": sorted({c[0] for c in offen if c[2] <= heute
                                 and not (KURSE / kurs / c[3]).exists()}),
    }


def tagesvorschlag(plaene, minuten, heute):
    """Erst alle fälligen Karten, dann heute als Podcast gehörte Chunks (kurz, nur Feynman),
    dann weitere Chunks nach Dringlichkeit (Rest-Wochensoll / Resttage der Woche)."""
    vorschlag = []
    karten = sum(len(p["faellig"]) for p in plaene)
    min_karten = round(min(minuten, karten * MIN_PRO_KARTE))
    budget = minuten - min_karten
    resttage = 7 - heute.weekday()
    bedarf = {p["kurs"]: p["noch_diese_woche"] for p in plaene}
    naechste = {p["kurs"]: list(p["offen_jetzt"]) for p in plaene}
    zuteilung = {p["kurs"]: [] for p in plaene}
    for p in plaene:
        for c in p["gehoert"]:
            if budget < MIN_PRO_CHUNK_GEHOERT:
                break
            zuteilung[p["kurs"]].append(c)
            naechste[p["kurs"]].remove(c)
            bedarf[p["kurs"]] -= 1
            budget -= MIN_PRO_CHUNK_GEHOERT
    n_chunks = max(0, budget // MIN_PRO_CHUNK)
    nahe = {p["kurs"]: (p["klausur"] - heute).days for p in plaene}
    for _ in range(n_chunks):
        kandidaten = [k for k in naechste if naechste[k]]
        if not kandidaten:
            break
        # Dringlichkeit: offenes Wochensoll pro Resttag; bei Gleichstand die nähere Klausur
        k = max(kandidaten, key=lambda k: (bedarf[k] / resttage, -nahe[k]))
        zuteilung[k].append(naechste[k].pop(0))
        bedarf[k] -= 1
    for p in plaene:
        if p["faellig"] or zuteilung[p["kurs"]]:
            vorschlag.append((p, zuteilung[p["kurs"]]))
    return vorschlag, karten, min_karten


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--minuten", type=int, default=60)
    ap.add_argument("--kurs", nargs="*")
    ap.add_argument("--portionen", type=int, default=1, help="Wochenend-Portionen (je 2 h) pro Woche, Standard 1")
    ap.add_argument("--pendeltage", type=int, default=PENDEL_TAGE,
                    help=f"Tage pro Woche mit Podcast auf dem Arbeitsweg, Standard {PENDEL_TAGE}")
    ap.add_argument("--datum", help="zum Testen: so tun, als wäre heute dieses Datum")
    a = ap.parse_args()
    heute = date.fromisoformat(a.datum) if a.datum else echtdatum.heute()
    kurse = a.kurs or sorted(p.name for p in KURSE.iterdir()
                             if (p / "_kurs" / "index.md").exists() and not p.name.startswith("_"))
    plaene = [kurs_planen(k, heute) for k in kurse]

    tage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    sw = (montag(heute) - SEMESTER_START).days // 7 + 1
    print(f"Heute: {tage[heute.weekday()]} {heute} · Semesterwoche {sw} · Vorlesungsende {VORLESUNGSENDE}\n")
    print(f"{'Kurs':<24}{'Ziel':<13}{'Wo.':>4}{'offen':>7}{'davon da':>9}{'Soll/Wo':>8}"
          f"{'Woche noch':>11}{'fällig':>8}{'7 Tage':>7}")
    for p in plaene:
        wochen_rest = max(1, len(p["wochen"]))
        soll_wo = math.ceil((len(p["offen"]) + p["diese_woche_gelernt"]) / wochen_rest)
        ziel = f"{p['ende']}" + ("" if p["bekannt"] else "*")
        print(f"{p['kurs']:<24}{ziel:<13}{len(p['wochen']):>4}{len(p['offen']):>7}{len(p['offen_jetzt']):>9}"
              f"{soll_wo:>8}{p['noch_diese_woche']:>11}{len(p['faellig']):>8}{p['faellig7']:>7}")
    print(f"Ziel = Klausur − {PUFFER_TAGE} Tage Puffer; * = kein Klausurtermin bekannt, Vorlesungsende angenommen.")
    gesamt = sum(p["noch_diese_woche"] for p in plaene)
    print(f"Diese Woche noch gesamt: {gesamt} Chunks ≈ {gesamt * MIN_PRO_CHUNK / 60:.1f} h "
          f"(+ Wiederholungen).\n")

    kap = (4 * MIN_MO_DO + a.portionen * MIN_PORTION) * EFFEKTIV
    pro_chunk = MIN_PRO_CHUNK + REVIEWS_PRO_CHUNK * MIN_PRO_KARTE
    pro_gehoert = MIN_PRO_CHUNK_GEHOERT + REVIEWS_PRO_CHUNK * MIN_PRO_KARTE
    soll_gesamt = sum(math.ceil((len(p["offen"]) + p["diese_woche_gelernt"]) / max(1, len(p["wochen"])))
                      for p in plaene)
    # Pendeln: bis zu MAX_CHUNKS_FOLGE Chunks pro Hinweg-Folge sind abends schon bekannt und kosten weniger
    vorgehoert = a.pendeltage * MAX_CHUNKS_FOLGE
    passt = min(vorgehoert, kap / pro_gehoert)
    passt += max(0, kap - passt * pro_gehoert) / pro_chunk
    print(f"Kapazität ({a.portionen} Wochenend-Portion/en, {a.pendeltage} Pendeltage): {kap:.0f} min/Woche Session "
          f"+ {a.pendeltage * 60} min Podcast ≈ {passt:.0f} Chunks/Woche inkl. Wiederholungen "
          f"(gehört {pro_gehoert:.0f}, sonst {pro_chunk:.0f} min/Chunk); Soll {soll_gesamt}/Woche → Deckung "
          f"{100 * passt / max(1, soll_gesamt):.0f} %{'  – ZU VIEL, priorisieren!' if passt < soll_gesamt else ''}\n")

    vorschlag, karten, min_karten = tagesvorschlag(plaene, a.minuten, heute)
    print(f"Vorschlag für heute ({a.minuten} min):")
    if karten:
        print(f"  Wiederholungen: {karten} Karten (~{min_karten} min) – zuerst, überfällige zuerst")
    for p, chunks in vorschlag:
        teile = []
        if p["faellig"]:
            teile.append(f"{len(p['faellig'])} Karten: {' '.join(p['faellig'][:12])}")
        if chunks:
            ids = " ".join(f"{c[0]}-{c[1]}" + ("*" if c in p["gehoert"] else "") for c in chunks)
            teile.append(f"neu: {ids}")
        print(f"  {p['kurs']}: " + " · ".join(teile))
    if not vorschlag:
        print("  Nichts fällig und kein verfügbarer neuer Stoff.")
    pod = [p for p in plaene if p["gehoert"] or p["rueck"]]
    if pod:
        print("  * = heute als Podcast gehört (Hinweg) → nach dem Vorwissen-Check direkt Feynman, nur Lücken erklären")
        for p in pod:
            teile = []
            if p["gehoert"]:
                teile.append("Hinweg " + " ".join(f"{c[0]}-{c[1]}" for c in p["gehoert"]))
            if p["rueck"]:
                teile.append("Rückweg-Quiz gehört → Wiederholungen dieses Kurses im Schnelldurchgang")
            print(f"  Podcast {p['kurs']}: " + " · ".join(teile))

    fehlen = [(p["kurs"], p["pakete_fehlen"]) for p in plaene if p["pakete_fehlen"]]
    if fehlen:
        print("\nSession-Pakete fehlen (Themen mit Material, aber ohne themen/-Datei):")
        for k, nrs in fehlen:
            print(f"  {k}: {', '.join(nrs)}")

    # Wochenübersicht für die nächsten Wochen
    n = 6
    print(f"\nChunks pro Woche (nächste {n} Wochen, inkl. angekündigtem Stoff):")
    alle = sorted({w for p in plaene for w, _, _ in p["wochen"]})[:n]
    print(f"{'':<24}" + "".join(f"{w.strftime('%d.%m.'):>8}" for w in alle))
    for p in plaene:
        d = {w: s for w, s, _ in p["wochen"]}
        print(f"{p['kurs']:<24}" + "".join(f"{d.get(w, '–'):>8}" for w in alle))


if __name__ == "__main__":
    main()
