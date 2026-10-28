#!/usr/bin/env python3
"""Podcast-Skript (Markdown) in eine MP3 vertonen.

Aufruf (immer mit dem venv-Python, dort liegen edge-tts und lameenc):
  _system/venv-podcast/bin/python \
      podcast.py <skript.md> [--out <datei.mp3>] [--tempo +5%]

Skriptformat, eine Zeile pro Redebeitrag:
  A: Text von Stimme A (Erklärerin)
  B: Text von Stimme B (fragt nach)
  [PAUSE 8]        Stille in Sekunden (Denkpause bei Abruffragen)
Alles andere (Überschriften, Leerzeilen, Kommentare mit #) wird ignoriert.
Ohne --out landet die MP3 neben dem Skript (gleicher Name, .mp3).
"""
import argparse
import asyncio
import hashlib
import re
import sys
from pathlib import Path

import edge_tts
import lameenc

STIMMEN = {
    "A": "de-DE-SeraphinaMultilingualNeural",
    "B": "de-DE-FlorianMultilingualNeural",
}
CACHE = Path(__file__).resolve().parents[4] / "_system" / "podcast-cache"
RATE, PARALLEL = 24000, 6  # edge-tts liefert 24 kHz mono, 48 kbps


def stille(sek: float) -> bytes:
    enc = lameenc.Encoder()
    enc.set_bit_rate(48)
    enc.set_in_sample_rate(RATE)
    enc.set_channels(1)
    enc.set_quality(2)
    return enc.encode(b"\x00\x00" * int(RATE * sek)) + enc.flush()


def parse(text: str):
    teile = []
    for zeile in text.splitlines():
        zeile = zeile.strip()
        if m := re.fullmatch(r"\[PAUSE\s+(\d+(?:\.\d+)?)\]", zeile):
            teile.append(("pause", float(m.group(1))))
        elif m := re.fullmatch(r"([AB]):\s*(.+)", zeile):
            teile.append((m.group(1), m.group(2)))
    return teile


async def sprich(sem, sprecher, text, tempo):
    key = hashlib.sha1(f"{STIMMEN[sprecher]}|{tempo}|{text}".encode()).hexdigest()
    pfad = CACHE / f"{key}.mp3"
    if not pfad.exists():
        async with sem:
            for versuch in range(3):
                try:
                    await edge_tts.Communicate(text, STIMMEN[sprecher], rate=tempo).save(str(pfad))
                    break
                except Exception as e:  # Netzwerk-Aussetzer: kurz warten, neu versuchen
                    if versuch == 2:
                        raise
                    print(f"  Wiederholung ({e})", file=sys.stderr)
                    await asyncio.sleep(2)
    return pfad.read_bytes()


async def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skript", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--tempo", default="+0%", help="Sprechtempo, z. B. +10%% oder -5%%")
    a = ap.parse_args()

    teile = parse(a.skript.read_text(encoding="utf-8"))
    if not teile:
        sys.exit("Keine Zeilen im Format 'A: …', 'B: …' oder '[PAUSE n]' gefunden.")
    CACHE.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(PARALLEL)
    kurz, wechsel = stille(0.3), stille(0.4)  # knapp, damit es nach Gespräch klingt

    async def teil(t):
        return stille(t[1]) if t[0] == "pause" else await sprich(sem, t[0], t[1], a.tempo)

    audio = await asyncio.gather(*(teil(t) for t in teile))
    out = a.out or a.skript.with_suffix(".mp3")
    with open(out, "wb") as f:
        vorher = None
        for t, daten in zip(teile, audio):
            if vorher is not None and t[0] != "pause" and vorher != "pause":
                f.write(wechsel if t[0] != vorher else kurz)
            f.write(daten)
            vorher = t[0]
    woerter = sum(len(t[1].split()) for t in teile if t[0] != "pause")
    pausen = sum(t[1] for t in teile if t[0] == "pause")
    print(f"{out}  ({len(teile)} Teile, {woerter} Wörter ≈ {woerter / 120 + pausen / 60:.0f} min)")


if __name__ == "__main__":
    asyncio.run(main())
