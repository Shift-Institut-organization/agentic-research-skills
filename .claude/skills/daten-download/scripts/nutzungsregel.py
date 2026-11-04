#!/usr/bin/env python3
"""
nutzungsregel.py — die gemeinsame Regel, ob eine Quelle oder ein Datenanhang genutzt
werden darf. Umsetzung von findings-schema.md, Abschnitt 3.4 (Skill topic-research).

Lizenz und Datenschutz sind zwei getrennte Urteile aus source-compliance-check. Erst
diese Regel verbindet sie:

    nutzen    freigabeklasse K1 oder K2  UND  datenschutz.befund == kein_personenbezug
    warten    freigabeklasse K1 oder K2  UND  datenschutz.befund zweifelhaft oder ausstehend
    gesperrt  alles Uebrige: K0, personenbezogen, nicht_pruefbar, fehlender oder
              unbekannter Block, Eintrag in meta.aussortiert

Die Richtung ist bewusst: Was die Regel nicht eindeutig freigibt, ist gesperrt.

Nur Standardbibliothek.
"""

import re

NUTZBARE_KLASSEN = {"K1_analyse_und_zitat", "K2_volltextwiedergabe"}


def norm_doi(raw):
    """DOI aus einer URL, kleingeschrieben, ohne Anker und Query."""
    m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", str(raw or ""))
    if not m:
        return None
    return m.group(0).split("#", 1)[0].split("?", 1)[0].lower().rstrip("./")


def aussortiert_schluessel(meta):
    """Alle Schluessel (DOI, URL, Titel), unter denen meta.aussortiert Quellen fuehrt."""
    keys = set()
    for e in (meta or {}).get("aussortiert") or []:
        if not isinstance(e, dict):
            continue
        url = str(e.get("doi_url") or "").strip()
        keys |= {norm_doi(url), url.rstrip("/").lower() or None, e.get("titel")}
    keys.discard(None)
    return keys


def quelle_schluessel(item):
    """Schluessel einer Quelle fuer den Abgleich mit meta.aussortiert."""
    return {norm_doi(item.get("doi_url")), item.get("titel")} - {None}


def anhang_schluessel(anhang):
    """Schluessel eines Datenanhangs fuer den Abgleich mit meta.aussortiert."""
    url = str(anhang.get("url") or "").strip()
    return {norm_doi(url), url.rstrip("/").lower() or None,
            anhang.get("titel_beschreibung")} - {None}


def nutzungsstatus(block, schluessel=frozenset(), aussortiert=frozenset()):
    """
    Wendet die Regel auf einen Eintrag oder einen Datenanhang an.

    block       das Objekt mit den Bloecken 'lizenz' und 'datenschutz'
    schluessel  Schluessel dieses Objekts (quelle_schluessel / anhang_schluessel)
    aussortiert Ergebnis von aussortiert_schluessel(meta)

    Rueckgabe: ("nutzen" | "warten" | "gesperrt", grund)
    """
    if schluessel & aussortiert:
        return "gesperrt", "steht in meta.aussortiert"

    liz = block.get("lizenz")
    ds = block.get("datenschutz")
    if not isinstance(liz, dict) or not liz:
        return "gesperrt", "kein lizenz-Block (Lizenzpruefung fehlt)"
    if not isinstance(ds, dict) or not ds:
        return "gesperrt", "kein datenschutz-Block (DSGVO-Pruefung fehlt)"

    klasse = liz.get("freigabeklasse")
    if klasse not in NUTZBARE_KLASSEN:
        grund = liz.get("k0_grund") or "freigabeklasse fehlt oder unbekannt"
        return "gesperrt", f"Lizenz: {klasse or 'keine Klasse'} ({grund})"

    befund = ds.get("befund")
    if ds.get("aussortiert") is True:
        return "gesperrt", f"Datenschutz: aussortiert ({befund})"
    if befund == "kein_personenbezug":
        return "nutzen", None
    if befund == "zweifelhaft":
        return "warten", "Datenschutz: zweifelhaft, Review steht aus"
    if befund == "ausstehend":
        return "warten", "Datenschutz: Pruefung steht noch aus"
    return "gesperrt", f"Datenschutz: {befund or 'kein Befund'}"


def compliance_geprueft(meta):
    """Ob source-compliance-check fuer die Datei abgeschlossen wurde."""
    meta = meta or {}
    return bool(meta.get("lizenz_geprueft")) and bool(meta.get("dsgvo_geprueft"))
