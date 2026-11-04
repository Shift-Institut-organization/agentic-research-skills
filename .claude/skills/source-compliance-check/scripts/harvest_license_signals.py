#!/usr/bin/env python3
"""
harvest_license_signals.py — sammelt maschinell auswertbare Lizenz- und TDM-Signale
für die Lizenzprüfung (Phase 6 des Skills source-compliance-check).

Das Skript nimmt dem Agenten den mechanischen Teil ab: Lizenzfelder aus OpenAlex und
CrossRef, robots.txt nach RFC 9309, W3C TDMRep. Es entscheidet NICHTS. Es liefert
Signale, die der Agent nach references/lizenzpruefung.md bewertet.

Zentrale Design-Entscheidung
----------------------------
Das Skript unterscheidet bei robots.txt strikt zwischen vier Zuständen:

    "kein_vorbehalt"          robots.txt abrufbar, kein TDM-Crawler würde für diese URL
                              abgewiesen
    "vorbehalt"               eine agentenspezifische Gruppe weist einen TDM-Crawler für
                              diese URL ab
    "vorbehalt_unspezifisch"  nur die "*"-Gruppe weist ab, keine Gruppe nennt einen
                              TDM-Crawler; ob das einen Vorbehalt trägt, ist manuell zu
                              bewerten
    "nicht_feststellbar"      robots.txt nicht abrufbar (403, 404, Timeout, Cloudflare)

Bei W3C TDMRep kommt "nicht_vorhanden" hinzu: alle drei Orte waren lesbar, keiner trägt
einen Eintrag. Nur HTTP 404 und 410 gelten als nicht vorhanden; 403, Timeout und
SSL-Fehler sind "nicht_feststellbar".

"nicht_feststellbar" darf niemals als "kein_vorbehalt" gewertet werden. Ein nicht
abrufbares Signal ist kein negatives Signal. Genau an dieser Stelle wird eine Prüfung
still zum Falschbefund.

Nutzung
-------
    python harvest_license_signals.py --doi 10.1234/abcd
    python harvest_license_signals.py --url https://example.org/paper
    python harvest_license_signals.py --batch dois.txt --json out.json
    python harvest_license_signals.py --from-findings findings_thema.json --json signals.json

Nur Standardbibliothek, keine Abhängigkeiten.
"""

import argparse
import html.parser
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "source-compliance-check/1.0"
TIMEOUT = 20

# User-Agents, deren Ausschluss in robots.txt als TDM-Rechtevorbehalt gilt.
# Grundlage: GPAI Code of Practice, Copyright Chapter, Measure 1.3 (RFC 9309).
TDM_AGENTS = [
    "GPTBot", "ClaudeBot", "anthropic-ai", "Claude-Web", "Google-Extended",
    "CCBot", "Bytespider", "PerplexityBot", "Applebot-Extended", "Amazonbot",
    "cohere-ai", "Diffbot", "FacebookBot", "Meta-ExternalAgent", "AI2Bot",
]

# Lizenz-URL-Fragmente, die eine eindeutige Einordnung erlauben.
LICENSE_HINTS = {
    "creativecommons.org/publicdomain/zero": "CC0",
    "creativecommons.org/publicdomain/mark": "Public Domain Mark",
    "creativecommons.org/licenses/by/": "CC BY",
    "creativecommons.org/licenses/by-sa/": "CC BY-SA",
    "creativecommons.org/licenses/by-nd/": "CC BY-ND",
    "creativecommons.org/licenses/by-nc/": "CC BY-NC",
    "creativecommons.org/licenses/by-nc-sa/": "CC BY-NC-SA",
    "creativecommons.org/licenses/by-nc-nd/": "CC BY-NC-ND",
    "govdata.de/dl-de/by-2-0": "dl-de/by-2-0",
    "opendatacommons.org": "ODC",
}


def fetch_response(url, accept=None):
    """Holt eine URL. Gibt (text, headers, status) zurueck; status None heisst Erfolg."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if accept:
        req.add_header("Accept", accept)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            charset = r.headers.get_content_charset() or "utf-8"
            return r.read().decode(charset, errors="replace"), r.headers, None
    except urllib.error.HTTPError as e:
        return None, None, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return None, None, f"URLError {e.reason}"
    except Exception as e:  # Timeout, SSL, Decoding
        return None, None, f"{type(e).__name__}: {e}"


def fetch(url, accept=None):
    """Holt eine URL. Gibt (text, status) zurueck; status None heisst Erfolg."""
    text, _, err = fetch_response(url, accept)
    return text, err


def classify_license(raw):
    """
    Ordnet eine Lizenz-URL oder -Kennung einer bekannten Lizenz zu.

    Behandelt drei Schreibweisen, die in der Praxis nebeneinander vorkommen:
    volle Lizenz-URLs (CrossRef), SPDX-Kuerzel mit Version (Zenodo: 'cc-by-4.0')
    und versionslose Kuerzel (OpenAlex: 'cc-by'). Die versionslose Form ist bei
    OpenAlex der Normalfall und darf nicht als unklassifiziert durchfallen, sonst
    landet die haeufigste Lizenz ueberhaupt im Zweifelstopf.
    """
    if not raw:
        return None
    low = str(raw).strip().lower()

    for frag, name in LICENSE_HINTS.items():
        if frag in low:
            return name

    # Kuerzel normalisieren: Version abschneiden, Trennzeichen vereinheitlichen
    token = low.replace("_", "-").replace(" ", "-")
    token = re.sub(r"-?\d+(\.\d+)*$", "", token)      # '-4.0', '-1.0' entfernen
    token = re.sub(r"^(cc-?)", "cc-", token)

    spdx = {
        "cc-0": "CC0", "cc0": "CC0", "cc-zero": "CC0",
        "cc-publicdomain": "Public Domain Mark", "cc-pd": "Public Domain Mark",
        "cc-by": "CC BY",
        "cc-by-sa": "CC BY-SA",
        "cc-by-nd": "CC BY-ND",
        "cc-by-nc": "CC BY-NC",
        "cc-by-nc-sa": "CC BY-NC-SA",
        "cc-by-nc-nd": "CC BY-NC-ND",
    }
    if token in spdx:
        return spdx[token]
    if low in ("public-domain", "publicdomain", "pd"):
        return "Public Domain Mark"

    return f"unklassifiziert: {raw}"


# Resolver- und Aggregator-Hosts, deren robots.txt nichts ueber den Rechteinhaber aussagt.
RESOLVER_HOSTS = {
    "doi.org", "dx.doi.org", "www.doi.org", "hdl.handle.net",
    "api.openalex.org", "openalex.org", "api.crossref.org",
}


def resolve_final_url(url):
    """
    Folgt Weiterleitungen bis zur tatsaechlichen Inhaltsadresse.

    Unverzichtbar, weil OpenAlex als landing_page_url regelmaessig die
    doi.org-Adresse liefert. Eine robots.txt-Pruefung gegen doi.org prueft den
    Resolver, nicht den Verlag, und erzeugt einen Befund, der nach Pruefung
    aussieht und keine ist. Genau solche stillen Falschbefunde soll dieses
    Skript verhindern.

    Rueckgabe: (finale_url, hinweis_oder_None)
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower() not in RESOLVER_HOSTS:
        return url, None

    class _Catch(urllib.request.HTTPRedirectHandler):
        def __init__(self):
            self.last = None

        def redirect_request(self, req, fp, code, msg, headers, newurl):
            self.last = newurl
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    catcher = _Catch()
    opener = urllib.request.build_opener(catcher)
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with opener.open(req, timeout=TIMEOUT) as r:
            final = r.geturl()
    except urllib.error.HTTPError as e:
        final = catcher.last or getattr(e, "url", None)
    except Exception:
        final = catcher.last

    if not final:
        return url, ("DOI konnte nicht aufgeloest werden; robots.txt-Pruefung waere gegen "
                     "den Resolver gelaufen und wurde unterlassen.")
    if urllib.parse.urlparse(final).netloc.lower() in RESOLVER_HOSTS:
        return url, "Aufloesung endete erneut beim Resolver; Verlagshost nicht ermittelbar."
    return final, None


def url_path(parsed):
    """Pfad plus Query, wie RFC 9309 § 2.2.2 und TDMRep ihn vergleichen."""
    path = parsed.path or "/"
    return f"{path}?{parsed.query}" if parsed.query else path


def pattern_regex(pattern):
    """
    Uebersetzt ein robots.txt- oder TDMRep-Muster in einen regulaeren Ausdruck.

    '*' steht fuer beliebig viele Zeichen, ein '$' am Ende verankert das Muster am
    Pfadende (RFC 9309 § 2.2.3). Ohne '$' ist der Vergleich ein Praefixvergleich,
    deshalb wird der Ausdruck mit re.match und nicht mit re.fullmatch verwendet.
    """
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    rx = ".*".join(re.escape(part) for part in body.split("*"))
    return re.compile(rx + ("$" if anchored else ""))


def parse_robots(text):
    """
    Zerlegt robots.txt in Gruppen nach RFC 9309 § 2.1 und § 2.2.1.

    Eine Gruppe sind eine oder mehrere User-agent-Zeilen plus die folgenden Regeln.
    Sie endet an der naechsten User-agent-Zeile, die auf mindestens eine Regel folgt.
    Allow ist ebenso eine Regel wie Disallow; fehlt das, verschmelzen benachbarte
    Gruppen und ein fremder Eintrag wird dem falschen Agenten zugerechnet.
    Regeln vor der ersten User-agent-Zeile gehoeren zu keiner Gruppe.

    Rueckgabe: Liste von {"agents": [token, ...], "rules": [(allow, muster), ...]},
    Tokens kleingeschrieben, '*' unveraendert.
    """
    groups, current = [], None
    for raw in text.lstrip("﻿").splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        if key == "user-agent":
            if current is None or current["rules"]:
                current = {"agents": [], "rules": []}
                groups.append(current)
            if val == "*":
                current["agents"].append("*")
            else:
                # Product-Token: Buchstaben, '_' und '-'; 'GPTBot/1.0' zaehlt als 'gptbot'
                m = re.match(r"[A-Za-z_-]+", val)
                if m:
                    current["agents"].append(m.group(0).lower())
        elif key in ("allow", "disallow") and current is not None:
            current["rules"].append((key == "allow", val))
    return groups


def select_rules(groups, agent):
    """
    Waehlt die Regeln fuer einen Agenten (RFC 9309 § 2.2.1).

    Alle Gruppen, die den Agenten nennen, werden gemergt. Die '*'-Gruppe gilt nur,
    wenn es keine solche Gruppe gibt. Rueckgabe: ("spezifisch" | "*" | None, regeln).
    """
    token = agent.lower()
    spezifisch = [g for g in groups if token in g["agents"]]
    if spezifisch:
        return "spezifisch", [r for g in spezifisch for r in g["rules"]]
    stern = [g for g in groups if "*" in g["agents"]]
    if stern:
        return "*", [r for g in stern for r in g["rules"]]
    return None, []


def is_allowed(rules, path):
    """
    Wertet Allow/Disallow fuer einen Pfad aus (RFC 9309 § 2.2.2).

    Der laengste passende Eintrag gewinnt, bei Gleichstand Allow. Kein Treffer,
    keine Regeln oder ein leeres Muster bedeuten: erlaubt.
    Rueckgabe: (erlaubt, entscheidendes_muster_oder_None).
    """
    best = None
    for allow, pattern in rules:
        if not pattern or not pattern_regex(pattern).match(path):
            continue
        cand = (len(pattern), allow)
        if best is None or cand > best[0]:
            best = (cand, pattern)
    if best is None:
        return True, None
    return best[0][1], best[1]


def check_robots(host_url):
    """
    Prueft robots.txt darauf, ob ein TDM-Crawler diese URL abrufen duerfte.

    Gefragt wird fuer jeden Agenten aus TDM_AGENTS, nicht fuer den eigenen User-Agent:
    Es geht darum, ob der Rechteinhaber einen Vorbehalt erklaert hat, nicht darum, ob
    dieses Skript gesperrt ist. Statusmodell im Modul-Docstring; 'nicht_feststellbar'
    darf nie zu 'kein_vorbehalt' kollabieren.
    """
    parsed = urllib.parse.urlparse(host_url)
    if not parsed.scheme or not parsed.netloc:
        return {"status": "nicht_feststellbar", "grund": "URL nicht parsebar", "agents": []}

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    text, err = fetch(robots_url)
    if text is None:
        return {
            "status": "nicht_feststellbar",
            "grund": f"robots.txt nicht abrufbar ({err})",
            "robots_url": robots_url,
            "agents": [],
        }

    groups = parse_robots(text)
    path = url_path(parsed)
    spezifisch_gesperrt, stern_gesperrt = [], []
    spezifisch_vorhanden = False
    for agent in TDM_AGENTS:
        art, rules = select_rules(groups, agent)
        if art == "spezifisch":
            spezifisch_vorhanden = True
        erlaubt, muster = is_allowed(rules, path)
        if erlaubt:
            continue
        eintrag = {"agent": agent, "gruppe": art, "regel": f"Disallow: {muster}"}
        (spezifisch_gesperrt if art == "spezifisch" else stern_gesperrt).append(eintrag)

    out = {"grund": None, "robots_url": robots_url, "pfad": path}
    if spezifisch_gesperrt:
        out.update(status="vorbehalt", agents=spezifisch_gesperrt)
    elif stern_gesperrt and not spezifisch_vorhanden:
        out.update(status="vorbehalt_unspezifisch", agents=stern_gesperrt)
    else:
        out.update(status="kein_vorbehalt", agents=[])
        if stern_gesperrt:
            # Einige TDM-Crawler haben eigene Gruppen und duerfen, die uebrigen fallen
            # auf eine sperrende '*'-Gruppe zurueck. Fuer die manuelle Pruefung festhalten.
            out["stern_gesperrt"] = stern_gesperrt
    return out


TDM_NICHT_VORHANDEN = {"HTTP 404", "HTTP 410"}


def tdm_wert(raw):
    """tdm-reservation als 0 oder 1; jeder andere Wert ist ein Protokollfehler (None)."""
    s = str(raw).strip()
    return int(s) if s in ("0", "1") else None


def check_tdmrep(host_url):
    """
    Prueft W3C TDMRep unter /.well-known/tdmrep.json fuer den Pfad dieser URL.

    Die erste Regel, deren location auf den Pfad passt, gilt (TDMRep § 3.2).
    Nur 404 und 410 heissen 'nicht_vorhanden'; 403, Timeout und SSL-Fehler sagen
    nichts ueber das Fehlen der Datei und ergeben 'nicht_feststellbar'.
    """
    parsed = urllib.parse.urlparse(host_url)
    if not parsed.scheme or not parsed.netloc:
        return {"status": "nicht_feststellbar", "grund": "URL nicht parsebar"}
    url = f"{parsed.scheme}://{parsed.netloc}/.well-known/tdmrep.json"
    text, err = fetch(url, accept="application/json")
    if text is None:
        if err in TDM_NICHT_VORHANDEN:
            return {"status": "nicht_vorhanden", "grund": err, "tdmrep_url": url}
        return {"status": "nicht_feststellbar", "grund": f"tdmrep.json nicht abrufbar ({err})",
                "tdmrep_url": url}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"status": "nicht_feststellbar", "grund": "kein valides JSON", "tdmrep_url": url}

    path = url_path(parsed)
    entries = data if isinstance(data, list) else [data]
    regel = next((e for e in entries
                  if isinstance(e, dict) and isinstance(e.get("location"), str)
                  and pattern_regex(e["location"]).match(path)), None)
    if regel is None:
        return {"status": "nicht_vorhanden", "grund": "keine Regel fuer diesen Pfad",
                "tdmrep_url": url, "raw": data}
    wert = tdm_wert(regel.get("tdm-reservation"))
    if wert is None:
        return {"status": "nicht_feststellbar",
                "grund": f"Protokollfehler: tdm-reservation={regel.get('tdm-reservation')!r}",
                "tdmrep_url": url, "raw": data}
    return {
        "status": "vorbehalt" if wert == 1 else "kein_vorbehalt",
        "wert": wert,
        "policy": regel.get("tdm-policy"),
        "tdmrep_url": url,
        "raw": data,
    }


class _TdmMeta(html.parser.HTMLParser):
    """Sammelt <meta name="tdm-reservation"> und <meta name="tdm-policy">."""

    def __init__(self):
        super().__init__()
        self.werte = {}

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        a = {k.lower(): (v or "") for k, v in attrs}
        name = a.get("name", "").strip().lower()
        if name in ("tdm-reservation", "tdm-policy") and name not in self.werte:
            self.werte[name] = a.get("content", "").strip()


def check_tdmrep_seite(url):
    """
    Prueft die beiden TDMRep-Orte auf der Seite selbst: die Response-Header
    tdm-reservation/tdm-policy und die gleichnamigen HTML-<meta>-Elemente.
    """
    text, headers, err = fetch_response(url, accept="text/html")
    if text is None:
        return {"status": "nicht_feststellbar", "grund": f"Seite nicht abrufbar ({err})"}

    orte = {}
    if headers is not None and headers.get("tdm-reservation") is not None:
        orte["header"] = {"roh": headers.get("tdm-reservation"),
                          "policy": headers.get("tdm-policy")}
    parser = _TdmMeta()
    try:
        parser.feed(text)
    except Exception:
        pass
    if "tdm-reservation" in parser.werte:
        orte["meta"] = {"roh": parser.werte["tdm-reservation"],
                        "policy": parser.werte.get("tdm-policy")}
    for ort in orte.values():
        ort["wert"] = tdm_wert(ort["roh"])
    return {"status": "gelesen", "url": url, **orte}


def tdmrep_gesamt(datei, seite):
    """
    Verbindet die drei TDMRep-Orte zu einem Befund.

    Reihenfolge nach TDMRep § 3: tdmrep.json, dann HTTP-Header, dann HTML-Meta. Ein
    spaeterer Ort ersetzt einen frueheren, ein fehlender setzt nichts zurueck. War ein
    Ort nicht lesbar, ist ein Wert 0 oder 'kein Eintrag' nicht belastbar: Der nicht
    gelesene Ort koennte einen Vorbehalt tragen.
    """
    wert, quelle, policy, luecken = None, None, None, []
    if datei.get("status") in ("vorbehalt", "kein_vorbehalt"):
        wert, quelle, policy = datei["wert"], "tdmrep.json", datei.get("policy")
    elif datei.get("status") == "nicht_feststellbar":
        luecken.append(f"tdmrep.json: {datei.get('grund')}")

    if seite.get("status") == "nicht_feststellbar":
        luecken.append(f"Header und Meta: {seite.get('grund')}")
    for ort in ("header", "meta"):
        eintrag = seite.get(ort)
        if not eintrag:
            continue
        if eintrag["wert"] is None:
            luecken.append(f"{ort}: Protokollfehler, tdm-reservation={eintrag['roh']!r}")
            continue
        wert, quelle, policy = eintrag["wert"], ort, eintrag.get("policy")

    out = {"datei": datei, "seite": seite, "quelle": quelle, "policy": policy,
           "luecken": luecken}
    if wert == 1:
        out["status"] = "vorbehalt"
    elif luecken:
        out["status"] = "nicht_feststellbar"
        out["grund"] = "; ".join(luecken)
    elif wert == 0:
        out["status"] = "kein_vorbehalt"
    else:
        out["status"] = "nicht_vorhanden"
    return out


def query_openalex(doi):
    url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
    text, err = fetch(url)
    if text is None:
        return {"erreichbar": False, "grund": err}
    try:
        w = json.loads(text)
    except json.JSONDecodeError:
        return {"erreichbar": False, "grund": "kein valides JSON"}
    prim = w.get("primary_location") or {}
    best = w.get("best_oa_location") or {}
    oa = w.get("open_access") or {}
    return {
        "erreichbar": True,
        "titel": w.get("title"),
        "jahr": w.get("publication_year"),
        "landing_page": prim.get("landing_page_url"),
        "license_raw": prim.get("license") or best.get("license"),
        "license_klassifiziert": classify_license(prim.get("license") or best.get("license")),
        "oa_status": oa.get("oa_status"),
        "oa_url": oa.get("oa_url"),
    }


def query_crossref(doi):
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    text, err = fetch(url)
    if text is None:
        return {"erreichbar": False, "grund": err}
    try:
        msg = json.loads(text).get("message", {})
    except json.JSONDecodeError:
        return {"erreichbar": False, "grund": "kein valides JSON"}
    lics = []
    for l in msg.get("license", []) or []:
        lics.append({
            "url": l.get("URL"),
            "content_version": l.get("content-version"),
            "klassifiziert": classify_license(l.get("URL")),
        })
    # Der tdm-Eintrag ist fuer N1 der einschlaegige.
    tdm = [l for l in lics if l.get("content_version") == "tdm"]
    return {
        "erreichbar": True,
        "titel": (msg.get("title") or [None])[0],
        "verlag": msg.get("publisher"),
        "lizenzen": lics,
        "tdm_lizenz": tdm[0] if tdm else None,
    }


def harvest(doi=None, url=None):
    out = {"doi": doi, "url": url, "abgefragt_am": time.strftime("%Y-%m-%d %H:%M:%S")}

    if doi:
        out["openalex"] = query_openalex(doi)
        out["crossref"] = query_crossref(doi)
        if not url:
            url = (out["openalex"].get("landing_page")
                   if out["openalex"].get("erreichbar") else None)
            out["url"] = url

    if url:
        final_url, aufloesung_hinweis = resolve_final_url(url)
        out["url_aufgeloest"] = final_url
        if final_url != url:
            out["aufloesung"] = f"{url} -> {final_url}"
        if aufloesung_hinweis:
            out["robots"] = {"status": "nicht_feststellbar", "grund": aufloesung_hinweis}
            out["tdmrep"] = {"status": "nicht_feststellbar", "grund": aufloesung_hinweis}
        else:
            out["robots"] = check_robots(final_url)
            out["tdmrep"] = tdmrep_gesamt(check_tdmrep(final_url), check_tdmrep_seite(final_url))
    else:
        out["robots"] = {"status": "nicht_feststellbar", "grund": "keine URL ermittelbar"}
        out["tdmrep"] = {"status": "nicht_feststellbar", "grund": "keine URL ermittelbar"}

    out["hinweise"] = build_hints(out)
    return out


def build_hints(sig):
    """
    Formuliert die Signale als Hinweise fuer den Agenten.
    Bewertet NICHT. Jeder Hinweis benennt, was noch zu pruefen bleibt.
    """
    hints = []
    oa = sig.get("openalex", {})
    cr = sig.get("crossref", {})

    lic = oa.get("license_klassifiziert")
    if lic and not lic.startswith("unklassifiziert"):
        hints.append(f"OpenAlex meldet Lizenz: {lic}. Gegen die Landing Page verifizieren.")
    elif oa.get("erreichbar") and not oa.get("license_raw"):
        hints.append(
            "OpenAlex meldet KEINE Lizenz (null). Das ist keine Freigabe. Landing Page und "
            "Nutzungsbedingungen lesen: Steht dort keine Lizenz, K0 mit k0_grund "
            "keine_lizenz_gefunden; sind sie nicht erreichbar, nicht_pruefbar."
        )

    if oa.get("oa_status") == "bronze":
        hints.append(
            "oa_status=bronze: frei lesbar, aber ohne Weiterverwendungslizenz. "
            "Ohne Lizenz auf der Landing Page: K0 mit k0_grund keine_lizenz_gefunden."
        )
    elif oa.get("oa_status") == "closed":
        hints.append(
            "oa_status=closed: Zugang pruefen. Falls nur ueber Hochschulzugang erreichbar, "
            "ist der rechtmaessige Zugang fuer SHIFT fraglich (Schranke greift dann nicht)."
        )

    if cr.get("tdm_lizenz"):
        hints.append(
            f"CrossRef fuehrt eine eigene TDM-Lizenz: {cr['tdm_lizenz'].get('url')}. "
            "Fuer N1 vorrangig auswerten."
        )

    rb = sig.get("robots", {})
    if rb.get("status") == "vorbehalt":
        agents = ", ".join(a["agent"] for a in rb.get("agents", []))
        hints.append(
            f"robots.txt sperrt TDM-Agenten ({agents}). Wirksamer Rechtevorbehalt gegen § 44b. "
            "N1 nur ueber den § 60d-Pfad, gegen den kein Vorbehalt wirkt. Zweigleisig ausweisen."
        )
    elif rb.get("status") == "vorbehalt_unspezifisch":
        hints.append(
            f"robots.txt sperrt diese URL nur ueber die '*'-Gruppe ({rb['agents'][0]['regel']}); "
            "keine Gruppe nennt einen TDM-Crawler. Ob eine pauschale Bot-Sperre einen "
            "Rechtevorbehalt nach § 44b Abs. 3 UrhG traegt, ist nicht automatisch entscheidbar. "
            "MANUELL BEWERTEN, nicht als kein_vorbehalt werten."
        )
    elif rb.get("status") == "nicht_feststellbar":
        hints.append(
            f"robots.txt NICHT ABRUFBAR ({rb.get('grund')}). Das ist kein Beleg fuer das Fehlen "
            "eines Vorbehalts. AGB und Nutzungsbedingungen manuell pruefen."
        )
    elif rb.get("status") == "kein_vorbehalt":
        hints.append(
            "robots.txt abrufbar, kein TDM-Vorbehalt. AGB/Nutzungsbedingungen bleiben zu pruefen "
            "(ErwGr. 18 CDSM-RL: AGB koennen den Vorbehalt tragen)."
        )
        if rb.get("stern_gesperrt"):
            gesperrt = ", ".join(a["agent"] for a in rb["stern_gesperrt"])
            hints.append(
                "Einige TDM-Crawler haben eigene, erlaubende Gruppen; die uebrigen fallen auf eine "
                f"sperrende '*'-Gruppe zurueck ({gesperrt}). Manuell bewerten."
            )

    td = sig.get("tdmrep", {})
    if td.get("status") == "vorbehalt":
        policy = f" Policy: {td['policy']}." if td.get("policy") else ""
        hints.append(f"W3C TDMRep erklaert einen Vorbehalt (tdm-reservation=1, Ort: "
                     f"{td.get('quelle') or 'tdmrep.json'}).{policy}")
    elif td.get("status") == "kein_vorbehalt":
        hints.append(f"W3C TDMRep erklaert ausdruecklich keinen Vorbehalt (tdm-reservation=0, "
                     f"Ort: {td.get('quelle')}). AGB bleiben zu pruefen.")
    elif td.get("status") == "nicht_vorhanden":
        hints.append("W3C TDMRep: an keinem der drei Orte (tdmrep.json, HTTP-Header, HTML-Meta) "
                     "ein Eintrag.")
    elif td.get("status") == "nicht_feststellbar":
        hints.append(
            f"W3C TDMRep NICHT FESTSTELLBAR ({td.get('grund')}). Das ist kein Beleg fuer das "
            "Fehlen eines Vorbehalts. Nutzungsbedingungen manuell pruefen."
        )

    hints.append(
        "Immer noch manuell zu pruefen: Nutzungsbedingungen/AGB, Lizenzangabe auf der Landing Page, "
        "bei Datensaetzen die Nachnutzungsbedingungen des Repositoriums."
    )
    return hints


def extract_dois_from_findings(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    items = []
    for fnd in data.get("findings", []):
        raw = fnd.get("doi_url") or ""
        m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", raw)
        items.append({
            "id": fnd.get("id"),
            "doi": m.group(0) if m else None,
            "url": raw if not m else None,
        })
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--doi")
    g.add_argument("--url")
    g.add_argument("--batch", help="Textdatei, eine DOI oder URL pro Zeile")
    g.add_argument("--from-findings", help="findings_<thema>.json, DOIs werden extrahiert")
    ap.add_argument("--json", help="Ergebnis zusaetzlich als JSON hierhin schreiben")
    ap.add_argument("--delay", type=float, default=1.0, help="Pause zwischen Abfragen in Sekunden")
    args = ap.parse_args()

    targets = []
    if args.doi:
        targets = [{"doi": args.doi, "url": None}]
    elif args.url:
        targets = [{"doi": None, "url": args.url}]
    elif args.batch:
        with open(args.batch, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = re.search(r"10\.\d{4,9}/[^\s]+", line)
                targets.append({"doi": m.group(0) if m else None,
                                "url": None if m else line})
    else:
        targets = extract_dois_from_findings(args.from_findings)

    results = []
    for i, t in enumerate(targets, 1):
        if not t.get("doi") and not t.get("url"):
            results.append({**t, "fehler": "weder DOI noch URL"})
            continue
        print(f"[{i}/{len(targets)}] {t.get('doi') or t.get('url')}", file=sys.stderr)
        r = harvest(doi=t.get("doi"), url=t.get("url"))
        if t.get("id"):
            r["finding_id"] = t["id"]
        results.append(r)
        if i < len(targets):
            time.sleep(args.delay)

    payload = {"signale": results, "anzahl": len(results)}
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n{len(results)} Datensaetze nach {args.json} geschrieben.", file=sys.stderr)
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    # Kurzuebersicht auf stderr, damit sie nicht die JSON-Ausgabe verschmutzt
    def zaehle(signal, status):
        return sum(1 for r in results if r.get(signal, {}).get("status") == status)
    print(f"\nZusammenfassung: {zaehle('robots', 'vorbehalt')} mit Rechtevorbehalt, "
          f"{zaehle('robots', 'vorbehalt_unspezifisch')} nur mit '*'-Sperre, "
          f"{zaehle('robots', 'nicht_feststellbar')} mit nicht feststellbarem robots.txt, "
          f"{zaehle('tdmrep', 'nicht_feststellbar')} mit nicht feststellbarem TDMRep "
          "(alle manuell pruefen!)", file=sys.stderr)


if __name__ == "__main__":
    main()
