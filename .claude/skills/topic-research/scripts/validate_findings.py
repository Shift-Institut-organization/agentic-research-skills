#!/usr/bin/env python3
"""
validate_findings.py — prueft findings_<thema>.json gegen das Schema aus
references/findings-schema.md.

Zweck: verhindern, dass ein Lauf als abgeschlossen gilt, dessen Uebergabedatei
unvollstaendig ist. Die Pruefung ist bewusst streng bei den Feldern, die die
Rechtschecks tragen, und nachsichtig bei allem anderen.

Besonders geprueft werden die Regeln, an denen Laeufe erfahrungsgemaess scheitern:
  1. daten_anhaenge enthaelt das Hauptdokument dupliziert
  2. Befunde stehen nur am Eintrag, nicht in meta.review_queue / meta.aussortiert
  3. lizenz- oder datenschutz-Block fehlt ganz, an der Quelle oder an einem Anhang
  4. Freigabeklasse passt nicht zu den Befunden, K0 ohne k0_grund, K1/K2 ohne Lizenz

Anhaenge werden mit denselben Regeln geprueft wie die Quelle selbst.

Zwei Stufen, weil zwei Skills nacheinander in dieselbe Datei schreiben:
  --stage research    nach topic-research: nur der Rechercheteil, Pruefbloecke duerfen fehlen
  --stage compliance  nach source-compliance-check (Vorgabe): alles

Nutzung
-------
    python validate_findings.py findings_thema.json --stage research
    python validate_findings.py findings_thema.json
    python validate_findings.py findings_thema.json --strict   # Warnungen zaehlen als Fehler

Exit-Code 0 = sauber, 1 = Fehler gefunden.
Nur Standardbibliothek.
"""

import argparse
import json
import re
import sys

PFLICHT_EINTRAG = [
    "id", "titel", "jahr", "quelle_plattform", "quelle_typ",
    "doi_url", "relevanz_begruendung", "qualitative_daten",
]

DS_PFLICHT = ["befund", "red_flags_geprueft", "stichprobe_beschreibung"]

QUAL_FELDER = [
    "hat_interviews", "interview_typ", "transkripte_verfuegbar",
    "interview_leitfaden_verfuegbar", "zitate_im_text",
]

LIZENZ_ERGEBNISSE = {"frei", "gestattet_schranke", "zweifelhaft", "gesperrt", "nicht_pruefbar"}
DS_BEFUNDE = {"kein_personenbezug", "personenbezogen", "zweifelhaft", "nicht_pruefbar",
              "ausstehend"}

FREIGABEKLASSEN = {"K2_volltextwiedergabe", "K1_analyse_und_zitat", "K0_keine_freigabe"}
K0_GRUENDE = {"keine_lizenz_gefunden", "nicht_pruefbar", "kein_rechtmaessiger_zugang",
              "n1_traegt_nicht"}

# Vermerke, die keine Lizenz sind und deshalb nicht in lizenz_bezeichnung gehoeren
KEINE_LIZENZ = re.compile(r"alle rechte|all rights|free to read|©|\(c\)|copyright", re.I)

RED_FLAGS = {"R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9"}

# Datenschutz-Befunde, die zur Aussortierung fuehren (Projektentscheidung 2026-10-20)
DS_AUSSORTIEREN = {"personenbezogen", "nicht_pruefbar"}
DS_BRAUCHT_QUEUE_NEU = {"zweifelhaft", "ausstehend"}

# Befunde, die zwingend einen Eintrag in review_queue erzeugen
LIZENZ_BRAUCHT_QUEUE = {"zweifelhaft", "nicht_pruefbar"}


PHASEN_PFLICHT = [
    "0_themen_mapping", "1_2_facetten_thesaurus", "3A_breite_suche",
    "3B_qualitativer_boost", "3C_citation_snowballing", "3D_praxis_berichte",
    "4_qualitaets_selektion", "5_findings",
]
PHASEN_PFLICHT_COMPLIANCE = ["6_lizenzpruefung", "7_dsgvo_pruefung"]


class Report:
    def __init__(self):
        self.errors, self.warnings, self.notes = [], [], []

    def err(self, where, msg):
        self.errors.append(f"[FEHLER]  {where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"[WARNUNG] {where}: {msg}")

    def note(self, msg):
        self.notes.append(f"[HINWEIS] {msg}")


def norm_doi(raw):
    """
    Normalisiert eine DOI aus einer URL.

    Fragment und Query werden abgeschnitten, damit eine Pseudo-URL wie
    '.../10.1234/abcd#appA' dieselbe DOI ergibt wie das Hauptdokument. Genau diese
    Faelle sind der Grund fuer die Pruefung: ein im Haupttext abgedruckter Anhang,
    der mit einem Anker als eigenstaendige Datei ausgegeben wird.
    """
    if not raw:
        return None
    m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", str(raw))
    if not m:
        return None
    doi = m.group(0)
    doi = doi.split("#", 1)[0].split("?", 1)[0]
    return doi.lower().rstrip(".").rstrip("/")


def anhang_keys(a):
    """Schluessel, unter denen ein aussortierter Anhang in meta.aussortiert stehen kann."""
    url = str(a.get("url") or "").strip()
    return {norm_doi(url), url.rstrip("/").lower() or None, a.get("titel_beschreibung")} - {None}


def check_anhaenge(fnd, rep, ctx):
    """
    Regel 1: Hauptdokument darf nicht als Anhang dupliziert sein.
    Regel 3: In der Stufe compliance (ctx gesetzt) traegt jeder Anhang eigene, vollstaendige
    lizenz- und datenschutz-Bloecke, die nach denselben Regeln geprueft werden wie die Quelle.
    """
    fid = fnd.get("id", "?")
    anh = fnd.get("daten_anhaenge")
    if anh is None:
        rep.warn(fid, "daten_anhaenge fehlt. Default ist [], nicht Weglassen.")
        return
    if not isinstance(anh, list):
        rep.err(fid, "daten_anhaenge muss eine Liste sein.")
        return

    haupt = {norm_doi(fnd.get("doi_url"))} - {None}
    haupt_urls = {str(fnd.get("doi_url", "")).rstrip("/").lower()} - {""}

    for i, a in enumerate(anh):
        if not isinstance(a, dict):
            rep.err(fid, f"daten_anhaenge[{i}] ist kein Objekt.")
            continue
        url = str(a.get("url") or "").strip()
        if not url:
            rep.err(fid, f"daten_anhaenge[{i}] hat keine url.")
            continue
        low = url.rstrip("/").lower()

        # Reihenfolge ist bewusst: der Anker-Fall ist der spezifischere und soll die
        # praezisere Meldung erzeugen, statt zusaetzlich als Dublette gemeldet zu werden.
        if "#" in url and norm_doi(url) and norm_doi(url) in haupt:
            rep.err(fid, f"daten_anhaenge[{i}] ist eine Pseudo-URL mit Anker ({url}). "
                         "Im Haupttext abgedruckte Anhaenge gehoeren nach qualitative_daten "
                         "(interview_leitfaden_verfuegbar), nicht in daten_anhaenge.")
        elif norm_doi(url) and norm_doi(url) in haupt:
            rep.err(fid, f"daten_anhaenge[{i}] dupliziert die Haupt-DOI ({url}). "
                         "Das Hauptdokument ist kein Datenanhang.")
        elif low in haupt_urls:
            rep.err(fid, f"daten_anhaenge[{i}] dupliziert doi_url ({url}).")
        if not a.get("typ"):
            rep.warn(fid, f"daten_anhaenge[{i}] hat keinen typ.")

        # Anhaenge brauchen eigene Pruefbloecke, geprueft wie die der Quelle
        if ctx is None:
            continue
        where = f"{fid}.daten_anhaenge[{i}]"
        keys = anhang_keys(a)
        if not isinstance(a.get("lizenz"), dict) or not a["lizenz"]:
            rep.err(where, "lizenz-Block fehlt oder ist leer. Anhaenge koennen abweichend "
                           "lizenziert sein und werden einzeln geprueft.")
        else:
            check_lizenz(a["lizenz"], where, fid, keys, rep, ctx)
        if not isinstance(a.get("datenschutz"), dict) or not a["datenschutz"]:
            rep.err(where, "datenschutz-Block fehlt oder ist leer. Bei Transkripten und "
                           "Rohdaten ist das nie entbehrlich.")
        else:
            check_datenschutz(a["datenschutz"], where, fid, keys, rep, ctx)


def check_lizenz(liz, fid, queue_id, keys, rep, ctx):
    """
    Prueft einen lizenz-Block, an der Quelle oder an einem Anhang.

    fid ist die Fundstelle fuer Meldungen, queue_id die id, unter der die Quelle in
    meta.review_queue steht, keys die Schluessel fuer meta.aussortiert.
    """
    queue_ids, aussortiert_keys, praemissen = (ctx["queue_ids"], ctx["aussortiert_keys"],
                                               ctx["praemissen"])
    if not isinstance(liz, dict):
        rep.err(fid, "lizenz-Block fehlt. Phase 6 nicht durchgefuehrt.")
        return
    bef = liz.get("befund")
    if not isinstance(bef, dict):
        rep.err(fid, "lizenz.befund fehlt.")
        return

    for art in ("N1", "N2", "N3"):
        b = bef.get(art)
        if not isinstance(b, dict):
            rep.err(fid, f"lizenz.befund.{art} fehlt. Jede Nutzungsart wird einzeln beurteilt.")
            continue
        erg = b.get("ergebnis")
        if erg not in LIZENZ_ERGEBNISSE:
            rep.err(fid, f"lizenz.befund.{art}.ergebnis ungueltig: {erg!r}")
            continue
        if erg == "gestattet_schranke" and not b.get("grundlage"):
            rep.err(fid, f"{art}: gestattet_schranke ohne benannte Schranke. "
                         "Die Grundlage ist der ganze Punkt des Befunds.")
        # Ausnahme: Eine Quelle ohne Lizenz ist abschliessend geprueft (K0, keine_lizenz_gefunden).
        # Ihre Einzelbefunde sind dokumentiert, aber kein offener Vorgang.
        if (erg in LIZENZ_BRAUCHT_QUEUE and queue_id not in queue_ids
                and liz.get("k0_grund") != "keine_lizenz_gefunden"):
            rep.err(fid, f"{art}: Befund {erg} ohne Eintrag in meta.review_queue. "
                         "Ein Flag am Eintrag allein wird nicht gefunden.")
        # Zweigleisigkeit: Abhaengigkeit von den Projektpraemissen muss ausgewiesen sein.
        # Ohne diese Felder laesst sich bei geaenderter Praemisse nicht feststellen, welcher
        # Teil des Korpus neu zu bewerten ist, und es muss alles angefasst werden.
        if erg in ("frei", "gestattet_schranke"):
            if "traegt_ohne_60d" not in b:
                rep.warn(fid, f"{art}: traegt_ohne_60d fehlt. Die Zweigleisigkeit ist die "
                              "Absicherung gegen das Wegfallen der § 60d-Praemisse.")
            if "traegt_ohne_nc_praemisse" not in b:
                rep.warn(fid, f"{art}: traegt_ohne_nc_praemisse fehlt. Bei NC-Lizenzen traegt "
                              "der Befund nur, solange die Nutzung nicht kommerziell ist.")

        # Eine Praemisse, auf die sich ein Befund stuetzt, muss auch deklariert sein.
        if b.get("traegt_ohne_nc_praemisse") is False and praemissen.get("nutzung_kommerziell") is not False:
            rep.err(fid, f"{art}: Befund stuetzt sich auf die NC-Praemisse "
                         "(traegt_ohne_nc_praemisse=false), aber meta.projektpraemissen fuehrt "
                         "nutzung_kommerziell nicht als false. Ein Befund darf sich nicht auf eine "
                         "Praemisse stuetzen, die nirgends erklaert ist.")
        if b.get("traegt_ohne_60d") is False and not praemissen.get("rechtstraeger_status"):
            rep.err(fid, f"{art}: Befund stuetzt sich auf § 60d (traegt_ohne_60d=false), aber "
                         "meta.projektpraemissen fuehrt keinen rechtstraeger_status.")

        # NC-Lizenz und zugleich Befund 'zweifelhaft' mit NC-Begruendung ist seit der
        # Praemisse ein Widerspruch. Der Zweifel muss dann aus ND oder SA kommen, nicht aus NC.
        lizname = str(liz.get("lizenz_bezeichnung") or "").upper()
        if erg == "zweifelhaft" and "NC" in lizname and "ND" not in lizname and "SA" not in lizname:
            grund = str(liz.get("review_grund") or "").lower()
            if "nc" in grund or "kommerz" in grund or "commercial" in grund:
                rep.err(fid, f"{art}: Befund zweifelhaft mit NC-Begruendung, obwohl die Praemisse "
                             "nutzung_kommerziell=false die NC-Klausel erfuellt. Entweder ist der "
                             "Grund ein anderer (ND, SA, Zugang) oder der Befund ist veraltet.")

    # Aussortierung erst, wenn die Quelle fuer KEINE Nutzungsart mehr traegt.
    # Eine Quelle, die fuer N1 frei und nur fuer N2 gesperrt ist, bleibt zu Recht im Korpus:
    # sie speist die Analyse, nur zitiert werden darf aus ihr nicht. Das ist der Normalfall
    # bei rechtevorbehaltenen Verlagsinhalten und kein Aussortierungsgrund.
    ergebnisse = [bef.get(a, {}).get("ergebnis") for a in ("N1", "N2", "N3")
                  if isinstance(bef.get(a), dict)]
    if ergebnisse and all(e == "gesperrt" for e in ergebnisse):
        if not keys & aussortiert_keys:
            rep.err(fid, "Fuer alle Nutzungsarten gesperrt, aber die Quelle steht nicht in "
                         "meta.aussortiert. Komplett gesperrte Quellen gehoeren mit Begruendung "
                         "dorthin, sonst werden sie bei der naechsten Recherche erneut gefunden "
                         "und erneut geprueft.")
    elif "gesperrt" in ergebnisse and not liz.get("review_grund"):
        gesperrte = [a for a in ("N1", "N2", "N3")
                     if isinstance(bef.get(a), dict) and bef[a].get("ergebnis") == "gesperrt"]
        rep.warn(fid, f"Gesperrt fuer {', '.join(gesperrte)}, aber kein review_grund vermerkt. "
                      "Die nachgelagerte Verarbeitung muss erkennen koennen, warum diese Quelle "
                      "nur eingeschraenkt nutzbar ist.")

    # Hard-Fail-Regel: Lizenz muss belegt sein
    if liz.get("lizenz_bezeichnung") and not liz.get("lizenz_beleg_url"):
        rep.err(fid, f"Lizenz {liz['lizenz_bezeichnung']!r} angegeben, aber keine "
                     "lizenz_beleg_url. Lizenzen werden belegt, nicht erschlossen.")
    if liz.get("lizenz_bezeichnung") and liz.get("lizenz_quelle") in (None, "keine"):
        rep.err(fid, "Lizenz angegeben, aber lizenz_quelle fehlt oder ist 'keine'.")
    if liz.get("lizenz_bezeichnung") and KEINE_LIZENZ.search(str(liz["lizenz_bezeichnung"])):
        rep.err(fid, f"lizenz_bezeichnung {liz['lizenz_bezeichnung']!r} ist keine Lizenz, sondern "
                     "ein Rechtevermerk. Das Feld bleibt null, die Quelle erhaelt K0 mit "
                     "k0_grund keine_lizenz_gefunden.")

    # Freigabeklasse: das Feld, auf das die Ausgabe schaltet.
    fk = liz.get("freigabeklasse")
    k0_grund = liz.get("k0_grund")
    if fk is None:
        rep.err(fid, "freigabeklasse fehlt. Ohne sie kann das RAG-System nicht entscheiden, "
                     "ob aus der Quelle zitiert werden darf. Vorgabewert ist K0_keine_freigabe.")
    elif fk not in FREIGABEKLASSEN:
        rep.err(fid, f"freigabeklasse ungueltig: {fk!r}. Zulaessig: "
                     f"{', '.join(sorted(FREIGABEKLASSEN))}")
    else:
        # Konsistenz mit den Einzelbefunden
        n1 = bef.get("N1", {}).get("ergebnis") if isinstance(bef.get("N1"), dict) else None
        n2 = bef.get("N2", {}).get("ergebnis") if isinstance(bef.get("N2"), dict) else None
        n1_traegt = n1 in ("frei", "gestattet_schranke")
        if fk == "K2_volltextwiedergabe" and not (n1_traegt and n2 == "frei"):
            rep.err(fid, f"freigabeklasse K2 erfordert N1 frei/gestattet_schranke und N2 frei, "
                         f"vorliegend N1={n1!r}, N2={n2!r}. K2 erlaubt Volltextwiedergabe; "
                         "eine zu grosszuegige Klasse ist der folgenschwerste Fehler dieser Datei.")
        if fk == "K1_analyse_und_zitat" and not n1_traegt:
            rep.err(fid, f"freigabeklasse K1 erfordert, dass N1 traegt, vorliegend N1={n1!r}. "
                         "Ohne Chunking-Befugnis gibt es nichts zu zitieren.")
        if fk != "K0_keine_freigabe":
            if not liz.get("lizenz_bezeichnung"):
                rep.err(fid, f"{fk} ohne lizenz_bezeichnung. Ohne gefundene Lizenz ist die Klasse "
                             "K0 mit k0_grund keine_lizenz_gefunden, auch wenn eine Schranke N1 "
                             "tragen wuerde.")
            if liz.get("rechtmaessiger_zugang") is False:
                rep.err(fid, f"{fk} trotz rechtmaessiger_zugang=false.")
            if k0_grund is not None:
                rep.err(fid, f"k0_grund {k0_grund!r} gesetzt, aber freigabeklasse ist {fk}.")
        elif k0_grund is None:
            rep.err(fid, "K0 ohne k0_grund. Zulaessig: " + ", ".join(sorted(K0_GRUENDE)) + ".")
        elif k0_grund not in K0_GRUENDE:
            zusatz = (" Lizenz und Datenschutz sind getrennte Urteile; der Datenschutzbefund "
                      "aendert die Freigabeklasse nicht." if "datenschutz" in str(k0_grund) else "")
            rep.err(fid, f"k0_grund ungueltig: {k0_grund!r}. Zulaessig: "
                         f"{', '.join(sorted(K0_GRUENDE))}.{zusatz}")
        elif k0_grund == "keine_lizenz_gefunden" and liz.get("lizenz_bezeichnung"):
            rep.err(fid, f"k0_grund keine_lizenz_gefunden, aber lizenz_bezeichnung ist "
                         f"{liz['lizenz_bezeichnung']!r}.")
        elif k0_grund == "nicht_pruefbar" and n1 != "nicht_pruefbar":
            rep.warn(fid, f"k0_grund nicht_pruefbar, aber N1={n1!r}. War die Quelle lesbar und es "
                          "gibt keine Lizenz, lautet der Grund keine_lizenz_gefunden.")
        elif k0_grund == "kein_rechtmaessiger_zugang" and liz.get("rechtmaessiger_zugang") is not False:
            rep.err(fid, "k0_grund kein_rechtmaessiger_zugang, aber rechtmaessiger_zugang ist "
                         "nicht false.")
        elif k0_grund == "n1_traegt_nicht" and n1_traegt:
            rep.err(fid, f"k0_grund n1_traegt_nicht, aber N1={n1!r} traegt.")

    rv = liz.get("rechtevorbehalt")
    if isinstance(rv, dict):
        if rv.get("gefunden") and not rv.get("fundort"):
            rep.err(fid, "Rechtevorbehalt gefunden, aber kein fundort benannt.")
        if not rv.get("geprueft"):
            rep.warn(fid, "rechtevorbehalt.geprueft ist leer. Es muss dokumentiert sein, "
                          "wo nachgesehen wurde, sonst ist 'nicht gefunden' bedeutungslos.")
    else:
        rep.warn(fid, "lizenz.rechtevorbehalt fehlt.")


def check_datenschutz(ds, fid, queue_id, keys, rep, ctx):
    """
    Prueft einen datenschutz-Block, an der Quelle oder an einem Anhang. Parameter wie
    bei check_lizenz.

    Leitidee: Seit der Projektentscheidung vom 2026-10-20 wird Personenbezug nicht
    abgewogen, sondern fuehrt zur Aussortierung. Zugleich gilt die Vertrauensvermutung
    fuer erklaerte Anonymisierungen. Der Validator prueft deshalb vor allem, ob die
    Vermutung sauber belegt ist, denn genau daran haengt, ob die Pruefung dem
    Sorgfaltsmassstab genuegt.
    """
    queue_ids, aussortiert_keys = ctx["queue_ids"], ctx["aussortiert_keys"]
    if not isinstance(ds, dict):
        rep.err(fid, "datenschutz-Block fehlt. Phase 7 nicht durchgefuehrt.")
        return

    bef = ds.get("befund")
    if bef not in DS_BEFUNDE:
        rep.err(fid, f"datenschutz.befund ungueltig: {bef!r}. Zulaessig: "
                     f"{', '.join(sorted(DS_BEFUNDE))}. Die Werte 'pseudonymisiert' und "
                     "'besondere_kategorie' sind entfallen: pseudonyme Daten sind "
                     "personenbezogen, und Art. 9 ist kein eigener Ausschlussgrund mehr.")
        return

    # Noch nicht geprueft: Es gibt nichts zu belegen, aber einen offenen Vorgang.
    if bef == "ausstehend":
        if queue_id not in queue_ids:
            rep.err(fid, "Befund ausstehend ohne Eintrag in meta.review_queue. Die Pruefung "
                         "muss nachgeholt werden, und jemand muss das sehen.")
        return

    # --- Sorgfaltsdokumentation: ohne sie traegt kein Befund ---
    flags_geprueft = ds.get("red_flags_geprueft")
    if not flags_geprueft:
        rep.err(fid, "red_flags_geprueft ist leer. Die Liste unterscheidet 'geprueft und nichts "
                     "gefunden' von 'nicht geprueft'. Nur Ersteres traegt die Vertrauensvermutung.")
    elif not isinstance(flags_geprueft, list):
        rep.err(fid, "red_flags_geprueft muss eine Liste sein.")
    else:
        unbekannt = set(flags_geprueft) - RED_FLAGS
        if unbekannt:
            rep.err(fid, f"red_flags_geprueft enthaelt unbekannte Kennungen: "
                         f"{', '.join(sorted(unbekannt))}")
        fehlend = RED_FLAGS - set(flags_geprueft)
        if fehlend and bef == "kein_personenbezug":
            rep.warn(fid, f"red_flags_geprueft unvollstaendig, nicht geprueft: "
                          f"{', '.join(sorted(fehlend))}. Bei Befund kein_personenbezug sollten "
                          "alle neun Flags geprueft sein.")

    if not ds.get("stichprobe_beschreibung") and ds.get("pruefumfang") != "nicht_einsehbar":
        rep.err(fid, "stichprobe_beschreibung fehlt. Der Umfang ist in Worten zu dokumentieren, "
                     "nicht nur als Kategorie; er ist der Kern des Sorgfaltsnachweises.")

    # --- Red Flags: Funde muessen Fundstellen tragen ---
    gefunden = ds.get("red_flags_gefunden") or []
    if not isinstance(gefunden, list):
        rep.err(fid, "red_flags_gefunden muss eine Liste sein.")
        gefunden = []
    for i, g in enumerate(gefunden):
        if not isinstance(g, dict):
            rep.err(fid, f"red_flags_gefunden[{i}] ist kein Objekt.")
            continue
        if g.get("flag") not in RED_FLAGS:
            rep.err(fid, f"red_flags_gefunden[{i}].flag ungueltig: {g.get('flag')!r}")
        if not g.get("fundstelle"):
            rep.err(fid, f"red_flags_gefunden[{i}] ohne fundstelle. Ein Fund ohne Fundstelle "
                         "ist nicht nachpruefbar und widerlegt die Vermutung nicht nachvollziehbar.")

    # --- Konsistenz Befund und Funde ---
    if gefunden and bef == "kein_personenbezug":
        flags = ", ".join(str(g.get("flag")) for g in gefunden if isinstance(g, dict))
        rep.err(fid, f"Red Flags gefunden ({flags}), aber Befund kein_personenbezug. "
                     "Ein konkreter Fund schlaegt die Anonymisierungserklaerung.")
    if bef == "personenbezogen" and not gefunden and not ds.get("dreikriterientest"):
        rep.err(fid, "Befund personenbezogen ohne Red Flag und ohne Dreikriterientest. "
                     "Der Befund muss zeigen, woran es scheitert.")

    # --- Vertrauensvermutung: V1 bis V3 muessen belegt sein ---
    grundlage = ds.get("grundlage")
    if grundlage == "vertrauensvermutung":
        ae = ds.get("anonymisierungserklaerung") or {}
        if not ae.get("vorhanden"):
            rep.err(fid, "grundlage vertrauensvermutung, aber anonymisierungserklaerung.vorhanden "
                         "ist nicht gesetzt (V1 nicht erfuellt).")
        if not ae.get("fundstelle"):
            rep.err(fid, "Vertrauensvermutung ohne Fundstelle der Anonymisierungserklaerung (V1). "
                         "Die Fundstelle ist der Beleg dafuer, dass die Erklaerung geprueft wurde.")
        if not ae.get("erklaerende_stelle"):
            rep.err(fid, "Vertrauensvermutung ohne erklaerende_stelle (V2).")
        if ae.get("stelle_einschlaegig") is not True:
            rep.err(fid, "Vertrauensvermutung, aber stelle_einschlaegig ist nicht true (V2). "
                         "Die Vermutung stuetzt sich auf die Qualifikation der erklaerenden Stelle.")
        if bef != "kein_personenbezug":
            rep.err(fid, f"grundlage vertrauensvermutung, aber Befund {bef!r}. Die Vermutung "
                         "fuehrt zu kein_personenbezug oder sie greift nicht.")
    elif grundlage is None and bef == "kein_personenbezug":
        rep.warn(fid, "Befund kein_personenbezug ohne Angabe der grundlage "
                      "(vertrauensvermutung, dreikriterientest oder klassen_screening).")

    # --- Art. 9: kein Ausschlussgrund, aber Massstabsverschaerfung ---
    if ds.get("art9_kategorien") and not ds.get("art9_verschaerfter_massstab"):
        rep.warn(fid, "art9_kategorien benannt, aber art9_verschaerfter_massstab nicht gesetzt. "
                      "Art. 9 schliesst nicht aus, verschaerft aber den Stichprobenumfang.")

    # --- Aussortierung: Konsequenz der Projektentscheidung ---
    aussortiert = ds.get("aussortiert")
    if bef in DS_AUSSORTIEREN:
        if aussortiert is not True:
            rep.err(fid, f"Befund {bef} ohne aussortiert=true. Personenbezug fuehrt zur "
                         "Aussortierung, eine Rechtsgrundlagenpruefung ist nicht vorgesehen.")
        if not ds.get("aussortierungsgrund"):
            rep.err(fid, f"Befund {bef} ohne aussortierungsgrund.")
        if not keys & aussortiert_keys:
            rep.err(fid, f"Befund {bef}, aber die Quelle steht nicht in meta.aussortiert. "
                         "Sonst wird sie bei der naechsten Recherche erneut gefunden.")
    else:
        if aussortiert is True:
            rep.warn(fid, f"aussortiert=true bei Befund {bef}. Zulaessig, sollte aber im "
                          "aussortierungsgrund erklaert sein.")

    if bef in DS_BRAUCHT_QUEUE_NEU and queue_id not in queue_ids:
        rep.err(fid, f"Befund {bef} ohne Eintrag in meta.review_queue. Die Tatsachenfrage ist "
                     "offen und jemand muss sie beantworten.")

    # --- Dreikriterientest: wenn durchgefuehrt, dann vollstaendig ---
    dkt = ds.get("dreikriterientest")
    if isinstance(dkt, dict):
        for krit in ("no_record_isolation", "no_linkage", "no_inference"):
            k = dkt.get(krit)
            if not isinstance(k, dict):
                rep.warn(fid, f"dreikriterientest.{krit} fehlt.")
            elif not all(pp in k for pp in ("P1", "P2", "P3")):
                rep.warn(fid, f"dreikriterientest.{krit}: nicht alle drei Perspektiven "
                              "P1, P2, P3 beurteilt.")


def check_meta(meta, rep, n_findings, compliance):
    if not isinstance(meta, dict):
        rep.err("meta", "meta fehlt oder ist kein Objekt.")
        return
    for f in ("thema", "erstellungsdatum", "suchprotokoll_version"):
        if not meta.get(f):
            rep.err("meta", f"{f} fehlt.")

    diag = meta.get("recherche_diagnose")
    if not isinstance(diag, dict):
        rep.err("meta", "recherche_diagnose fehlt.")
    else:
        for f in ("treffer_roh_gesichtet", "validiert_gespeichert", "saettigungsgrund"):
            if diag.get(f) in (None, "", 0):
                rep.warn("meta.recherche_diagnose", f"{f} fehlt oder ist 0.")

    log = meta.get("phasen_log")
    if not isinstance(log, list) or not log:
        rep.err("meta", "phasen_log fehlt oder ist leer.")
    else:
        gesehen = {e.get("phase") for e in log if isinstance(e, dict)}
        pflicht = PHASEN_PFLICHT + (PHASEN_PFLICHT_COMPLIANCE if compliance else [])
        for p in pflicht:
            if p not in gesehen:
                rep.err("meta.phasen_log", f"Phase {p} fehlt im Log.")
        for e in log:
            if isinstance(e, dict) and not e.get("beobachtung"):
                rep.warn("meta.phasen_log", f"Phase {e.get('phase')} ohne beobachtung.")

    # Pruefsiegel duerfen nicht gesetzt sein, wenn Befunde fehlen
    if meta.get("lizenz_geprueft") and not meta.get("projektpraemissen"):
        rep.warn("meta", "lizenz_geprueft gesetzt, aber projektpraemissen fehlen. "
                         "Der Befund ist ohne die Praemissen nicht nachvollziehbar.")

    if n_findings < 30:
        rep.note(f"Nur {n_findings} Eintraege. Richtwert des Skills sind 30 bis 50+. "
                 "Falls das Thema nicht mehr hergibt, Saettigungsgrund dokumentieren.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datei")
    ap.add_argument("--stage", choices=["research", "compliance"], default="compliance",
                    help="research: nur Rechercheteil pruefen; compliance: alles (Vorgabe)")
    ap.add_argument("--strict", action="store_true", help="Warnungen zaehlen als Fehler")
    args = ap.parse_args()
    compliance = args.stage == "compliance"

    rep = Report()
    try:
        with open(args.datei, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[FEHLER] Datei nicht gefunden: {args.datei}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[FEHLER] Kein valides JSON: Zeile {e.lineno}, Spalte {e.colno}: {e.msg}")
        sys.exit(1)

    meta = data.get("meta", {})
    findings = data.get("findings", [])
    if not isinstance(findings, list):
        print("[FEHLER] findings muss eine Liste sein.")
        sys.exit(1)

    praemissen = meta.get("projektpraemissen") or {}
    queue_ids = {e.get("finding_id") for e in (meta.get("review_queue") or [])
                 if isinstance(e, dict)}
    aussortiert_keys = set()
    for e in (meta.get("aussortiert") or []):
        if isinstance(e, dict):
            url = str(e.get("doi_url") or "").strip()
            aussortiert_keys.add(norm_doi(url))
            aussortiert_keys.add(url.rstrip("/").lower() or None)
            aussortiert_keys.add(e.get("titel"))
    aussortiert_keys.discard(None)
    ctx = {"queue_ids": queue_ids, "aussortiert_keys": aussortiert_keys,
           "praemissen": praemissen} if compliance else None

    check_meta(meta, rep, len(findings), compliance)

    ids = set()
    for fnd in findings:
        if not isinstance(fnd, dict):
            rep.err("findings", "Eintrag ist kein Objekt.")
            continue
        fid = fnd.get("id", "?")
        if fid in ids:
            rep.err(fid, "doppelte id.")
        ids.add(fid)

        for f in PFLICHT_EINTRAG:
            if fnd.get(f) in (None, ""):
                rep.err(fid, f"Pflichtfeld {f} fehlt.")

        qd = fnd.get("qualitative_daten")
        if isinstance(qd, dict):
            for f in QUAL_FELDER:
                if f not in qd:
                    rep.warn(fid, f"qualitative_daten.{f} fehlt. Leere Felder sind spaeter "
                                  "nicht von ungeprueften zu unterscheiden.")
        elif qd is not None:
            rep.err(fid, "qualitative_daten muss ein Objekt sein.")

        check_anhaenge(fnd, rep, ctx)
        if compliance:
            keys = {norm_doi(fnd.get("doi_url")), fnd.get("titel")} - {None}
            check_lizenz(fnd.get("lizenz"), fid, fid, keys, rep, ctx)
            check_datenschutz(fnd.get("datenschutz"), fid, fid, keys, rep, ctx)

    # Verwaiste Queue-Eintraege
    for qid in queue_ids:
        if qid and qid not in ids:
            rep.warn("meta.review_queue", f"Eintrag verweist auf unbekannte id {qid}.")

    print("=" * 72)
    print(f"Validierung: {args.datei} (Stufe {args.stage})")
    print(f"{len(findings)} Eintraege, {len(queue_ids)} in der Review-Queue, "
          f"{len(meta.get('aussortiert') or [])} aussortiert")
    print("=" * 72)
    for line in rep.errors:
        print(line)
    for line in rep.warnings:
        print(line)
    for line in rep.notes:
        print(line)
    if not (rep.errors or rep.warnings or rep.notes):
        print("Keine Beanstandungen.")
    print("-" * 72)
    print(f"{len(rep.errors)} Fehler, {len(rep.warnings)} Warnungen, {len(rep.notes)} Hinweise")

    fail = bool(rep.errors) or (args.strict and bool(rep.warnings))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
