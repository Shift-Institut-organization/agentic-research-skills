#!/usr/bin/env python3
"""
test_robots_parser.py — Testtabelle fuer check_robots() und check_tdmrep()
aus harvest_license_signals.py.

Zweck: Das Soll-Verhalten nach RFC 9309 festschreiben. Die Tabelle ist die
Spezifikation; rote Zeilen sind offene Punkte, keine Regressionen.

Kein Netz, keine Abhaengigkeiten. fetch() wird gestubbt.

    python test_robots_parser.py

Statusmodell (vier Werte, nicht drei):

    kein_vorbehalt          Regelwerk abrufbar, TDM-Crawler wuerde NICHT abgewiesen
    vorbehalt               agentenspezifische Gruppe weist ab -> Vorbehalt erklaert
    vorbehalt_unspezifisch  nur die "*"-Gruppe weist ab; ob das einen TDM-Vorbehalt
                            nach § 44b Abs. 3 UrhG traegt, ist offen -> manuelle Bewertung
    nicht_feststellbar      Regelwerk nicht abrufbar (403, Timeout, SSL, Cloudflare)
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "hls", os.path.join(HERE, "harvest_license_signals.py"))
hls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hls)

URL = "https://example.org/articles/12345"

# (Name, robots.txt, URL, erwarteter Status, RFC-Fundstelle)
ROBOTS_CASES = [
    ("leeres Disallow ist eine Erlaubnis, keine Sperre",
     "User-agent: GPTBot\nDisallow:\n",
     URL, "kein_vorbehalt", "§ 2.2.2 / ABNF empty-pattern"),

    ("Disallow auf fremdem Pfad trifft diese URL nicht",
     "User-agent: GPTBot\nDisallow: /admin/\n",
     URL, "kein_vorbehalt", "§ 2.2.2 Praefixvergleich"),

    ("nur die *-Gruppe sperrt -> eigener Status, keine Binaerentscheidung",
     "User-agent: *\nDisallow: /\n",
     URL, "vorbehalt_unspezifisch", "§ 2.2.1 Fallback-Gruppe"),

    ("Allow schlaegt laengeres Disallow nicht, aber deckt diese URL",
     "User-agent: GPTBot\nDisallow: /\nAllow: /articles/\n",
     URL, "kein_vorbehalt", "§ 2.2.2 most octets"),

    ("Allow-only-Block trennt Gruppen korrekt",
     "User-agent: GPTBot\nAllow: /\n\nUser-agent: BadBot\nDisallow: /\n",
     URL, "kein_vorbehalt", "§ 2.2.1 Gruppengrenze"),

    ("agentenspezifische Gruppe verdraengt die *-Gruppe",
     "User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n",
     URL, "kein_vorbehalt", "§ 2.2.1 spezifischer Treffer gewinnt"),

    ("Gruppe ohne Regeln erlaubt alles",
     "User-agent: GPTBot\n",
     URL, "kein_vorbehalt", "§ 2.1 leere Gruppe"),

    ("Wildcard greift nicht bei abweichender Endung",
     "User-agent: GPTBot\nDisallow: /*.pdf$\n",
     URL, "kein_vorbehalt", "§ 2.2.3 Sonderzeichen"),

    ("Wildcard greift bei passender Endung",
     "User-agent: GPTBot\nDisallow: /*.pdf$\n",
     "https://example.org/articles/12345.pdf", "vorbehalt", "§ 2.2.3 Sonderzeichen"),

    ("Product-Token wird case-insensitiv gematcht",
     "User-agent: gptbot\nDisallow: /\n",
     URL, "vorbehalt", "§ 2.2.1 case-insensitive"),

    ("mehrere Gruppen desselben Agenten werden gemergt",
     "User-agent: GPTBot\nDisallow: /foo\n\nUser-agent: GPTBot\nDisallow: /articles/\n",
     URL, "vorbehalt", "§ 2.2.1 Merge"),

    ("Kommentare am Zeilenende stoeren nicht",
     "User-agent: GPTBot   # KI-Crawler\nDisallow: /   # alles gesperrt\n",
     URL, "vorbehalt", "§ 2.2 EOL-Kommentar"),

    ("Kontrollfall: echter vollstaendiger Vorbehalt",
     "User-agent: GPTBot\nDisallow: /\n",
     URL, "vorbehalt", "-"),

    # Gegenproben zu den beiden Zeilen, die vor dem Umbau nur zufaellig gruen waren:
    # gleiche robots.txt, Pfad ausserhalb der Regel -> muss erlaubt sein.
    ("Gegenprobe Merge: gemergte Regeln treffen fremden Pfad nicht",
     "User-agent: GPTBot\nDisallow: /foo\n\nUser-agent: GPTBot\nDisallow: /articles/\n",
     "https://example.org/books/1", "kein_vorbehalt", "§ 2.2.1 Merge"),

    ("Gleichstand zwischen Allow und Disallow -> Allow gewinnt",
     "User-agent: GPTBot\nDisallow: /articles/\nAllow: /articles/\n",
     URL, "kein_vorbehalt", "§ 2.2.2 equivalent rules"),

    ("Query gehoert zum Pfad",
     "User-agent: GPTBot\nDisallow: /*?download=\n",
     URL + "?download=1", "vorbehalt", "§ 2.2.2 path + query"),

    ("*-Gruppe sperrt, nur ein fremder Agent hat eine eigene Gruppe",
     "User-agent: Googlebot\nAllow: /\n\nUser-agent: *\nDisallow: /\n",
     URL, "vorbehalt_unspezifisch", "§ 2.2.1 Fallback-Gruppe"),

    ("Regel vor der ersten User-agent-Zeile gehoert zu keiner Gruppe",
     "Disallow: /\nUser-agent: GPTBot\nAllow: /\n",
     URL, "kein_vorbehalt", "§ 2.1 Gruppenbeginn"),
]

# (Name, fetch_response-Rueckgabe (text, headers, err), erwarteter Ort -> Wert)
TDMREP_SEITE_CASES = [
    ("HTTP-Header tdm-reservation wird gelesen",
     ("<html></html>", {"tdm-reservation": "1", "tdm-policy": "https://example.org/p.json"}, None),
     {"header": 1}),
    ("HTML-Meta tdm-reservation wird gelesen",
     ('<html><head><meta content="1" name="TDM-Reservation"></head></html>', {}, None),
     {"meta": 1}),
    ("Header und Meta werden beide gelesen",
     ('<meta name="tdm-reservation" content="0">', {"tdm-reservation": "1"}, None),
     {"header": 1, "meta": 0}),
    ("Ungueltiger Wert ist Protokollfehler, kein Vorbehalt",
     ('<meta name="tdm-reservation" content="ja">', {}, None),
     {"meta": None}),
]

# (Name, tdmrep.json-Befund, Seitenbefund, erwarteter Gesamtstatus)
NV = {"status": "nicht_vorhanden"}
NF = {"status": "nicht_feststellbar", "grund": "HTTP 403"}
GELESEN = {"status": "gelesen"}
TDMREP_GESAMT_CASES = [
    ("nirgends ein Eintrag, alles lesbar", NV, GELESEN, "nicht_vorhanden"),
    ("Datei 403, Seite ohne Eintrag -> nicht feststellbar", NF, GELESEN, "nicht_feststellbar"),
    ("Datei ohne Eintrag, Seite nicht abrufbar -> nicht feststellbar", NV, NF, "nicht_feststellbar"),
    ("Header 1 schlaegt Datei 0",
     {"status": "kein_vorbehalt", "wert": 0}, {"status": "gelesen", "header": {"wert": 1, "roh": "1"}},
     "vorbehalt"),
    ("Meta 0 schlaegt Header 1 (spaeterer Ort ersetzt frueheren)", NV,
     {"status": "gelesen", "header": {"wert": 1, "roh": "1"}, "meta": {"wert": 0, "roh": "0"}},
     "kein_vorbehalt"),
    ("Datei 0, Seite nicht abrufbar -> 0 nicht belastbar",
     {"status": "kein_vorbehalt", "wert": 0}, NF, "nicht_feststellbar"),
    ("Datei 1, Seite nicht abrufbar -> Vorbehalt bleibt",
     {"status": "vorbehalt", "wert": 1}, NF, "vorbehalt"),
]

# (Name, fetch-Rueckgabe, erwarteter Status)
TDMREP_CASES = [
    ("404 heisst wirklich nicht vorhanden",
     (None, "HTTP 404"), "nicht_vorhanden"),
    ("403 ist nicht feststellbar, nicht abwesend",
     (None, "HTTP 403"), "nicht_feststellbar"),
    ("Timeout ist nicht feststellbar",
     (None, "TimeoutError: timed out"), "nicht_feststellbar"),
    ("tdm-reservation=1 ist ein Vorbehalt",
     ('[{"location": "/", "tdm-reservation": 1}]', None), "vorbehalt"),
    ("tdm-reservation=0 ist keiner",
     ('[{"location": "/", "tdm-reservation": 0}]', None), "kein_vorbehalt"),
    ("Regel fuer fremden Pfad gilt nicht",
     ('[{"location": "/images/*", "tdm-reservation": 1}]', None), "nicht_vorhanden"),
    ("erste passende Regel gilt",
     ('[{"location": "/x", "tdm-reservation": 0}, {"location": "/", "tdm-reservation": 1}]', None),
     "kein_vorbehalt"),
]


def run_seite():
    title = "W3C TDMRep: HTTP-Header und HTML-Meta"
    print(f"\n{title}\n" + "=" * len(title))
    passed = failed = 0
    for name, ret, soll in TDMREP_SEITE_CASES:
        hls.fetch_response = lambda u, accept=None, _r=ret: _r
        res = hls.check_tdmrep_seite("https://example.org/x")
        ist = {ort: res[ort]["wert"] for ort in ("header", "meta") if ort in res}
        ok = ist == soll
        passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
        print(f"[{'OK  ' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"   soll: {soll}\n   ist : {ist}")
    return passed, failed


def run_gesamt():
    title = "W3C TDMRep: Gesamtbefund aus drei Orten"
    print(f"\n{title}\n" + "=" * len(title))
    passed = failed = 0
    for name, datei, seite, soll in TDMREP_GESAMT_CASES:
        ist = hls.tdmrep_gesamt(datei, seite)["status"]
        ok = ist == soll
        passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
        print(f"[{'OK  ' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"   soll: {soll}\n   ist : {ist}")
    return passed, failed


def run(title, cases, fn):
    print(f"\n{title}\n" + "=" * len(title))
    passed = failed = 0
    for case in cases:
        if fn is hls.check_robots:
            name, body, url, soll, rfc = case
            hls.fetch = lambda u, accept=None, _b=body: (_b, None)
            ist = fn(url)["status"]
            extra = f"   RFC 9309 {rfc}"
        else:
            name, ret, soll = case
            hls.fetch = lambda u, accept=None, _r=ret: _r
            ist = fn("https://example.org/x")["status"]
            extra = ""
        ok = ist == soll
        passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
        print(f"[{'OK  ' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"   soll: {soll}\n   ist : {ist}{extra}")
    return passed, failed


def main():
    p1, f1 = run("robots.txt (RFC 9309)", ROBOTS_CASES, hls.check_robots)
    p2, f2 = run("W3C TDMRep: /.well-known/tdmrep.json", TDMREP_CASES, hls.check_tdmrep)
    p3, f3 = run_seite()
    p4, f4 = run_gesamt()
    passed, failed = p1 + p2 + p3 + p4, f1 + f2 + f3 + f4
    print(f"\n{passed} ok, {failed} offen")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
