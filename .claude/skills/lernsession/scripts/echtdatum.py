"""Echtes heutiges Datum (Europe/Berlin).

Die Systemuhr der VM geht falsch und wird nicht synchronisiert (2026-10-29: über
einen Tag nach). Deshalb das Datum aus dem Date-Header eines Webservers holen;
nur wenn das scheitert, auf die Systemuhr zurückfallen (mit Warnung).
"""
import sys
import urllib.request
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

QUELLEN = ["https://www.google.com", "https://www.cloudflare.com"]


@lru_cache(maxsize=1)
def jetzt():
    for url in QUELLEN:
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=4) as r:
                return parsedate_to_datetime(r.headers["Date"]).astimezone(ZoneInfo("Europe/Berlin"))
        except Exception:
            continue
    print("Warnung: Internetzeit nicht erreichbar – Systemuhr wird benutzt (geht in der VM falsch).",
          file=sys.stderr)
    return datetime.now(ZoneInfo("Europe/Berlin"))


def heute() -> date:
    return jetzt().date()


if __name__ == "__main__":
    print(jetzt().strftime("%Y-%m-%d %H:%M"))
