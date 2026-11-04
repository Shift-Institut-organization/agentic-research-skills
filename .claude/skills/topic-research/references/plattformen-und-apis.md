# Plattformen, APIs und Suchwerkzeuge

Nachschlagewerk für die Phasen 0, 2 und 3. Enthält Plattform-Mapping, MCP-Tools, direkte
API-Fallbacks, Thesaurus-Muster, BibTeX-Export und Fehlerbehandlung.

## Inhalt

1. [Plattform-Mapping nach Archetyp](#1-plattform-mapping-nach-archetyp)
2. [Quellenwahl: welche Plattform wofür](#2-quellenwahl-welche-plattform-wofür)
3. [MCP-Tools](#3-mcp-tools)
4. [REST-APIs per Shell](#4-rest-apis-per-shell)
5. [Lizenzfelder je API](#5-lizenzfelder-je-api)
6. [Thesaurus-Muster](#6-thesaurus-muster)
7. [BibTeX-Export](#7-bibtex-export)
8. [Fehlerbehandlung](#8-fehlerbehandlung)
9. [Bekannte Grenzen](#9-bekannte-grenzen)

---

## 1. Plattform-Mapping nach Archetyp

```
STANDARD (immer abfragen):
  OpenAlex          interdisziplinäre Wissenschaftsliteratur, REST, paginierbar
  Zenodo            Preprints, Datensätze, Graue Literatur, Transkripte, REST
  Semantic Scholar  KI-gestützte Suche, Paper-Graphen, Related Papers
  CrossRef          DOI-Auflösung, Verlagsmetadaten, exakte Bibliographie

QUALITATIVE FORSCHUNG UND INTERVIEW-REPOSITORIEN (Pflicht bei qualitativer Vertiefung):
  QDR               Qualitative Data Repository, qdr.syr.edu, spezialisiert auf Transkripte
  GESIS / SSOAR     archivierte Befragungen, qualitative Studien, DE-Fokus, ssoar.info
  ICPSR             quantitative und qualitative Sozialdaten, icpsr.umich.edu
  Harvard Dataverse offene Forschungsdaten und qualitative Anhänge
  OSF               Open Science Framework, Preprints und Projektanhänge

WORKING PAPER UND PREPRINTS:
  SSRN              Rechts-, Wirtschafts- und Sozialwissenschaft, oft Monate vor Publikation
  arXiv             cs.HC, cs.CY, eess.SP, stat.AP
  EconStor / RePEc  Open-Access-Arbeitspapiere Wirtschaft

PRAXIS, KOMMUNEN, VERBÄNDE, NGOS (Graue Literatur):
  Bund und Kommunen Difu, BBSR, UBA, BASt, BMDV, Landesministerien, GovData.de
  Verbände und NGOs je nach Themenfeld, siehe unten
  EU                EU Open Data Portal, EUR-Lex, Eurostat

NACH THEMENFELD:
  Mobilität und Verkehr     TRID (trid.trb.org), Agora Verkehrswende, DLR, VDV, ADFC, VCD, ECF
  Ingenieurwesen, Technik   IEEE Xplore, ACM Digital Library, arXiv
  Medizin, Public Health    PubMed/MEDLINE, Cochrane Library, WHO IRIS
  Stadt- und Raumplanung    BBSR, Difu, EU Open Data Portal
  Software und Tools        GitHub (topic:, language:), Hugging Face
  Beteiligung und Demokratie  FES, Bertelsmann Stiftung, OECD, Partizipationsportale der Länder
```

Die Auswahl **mit Begründung** im Protokoll-Header dokumentieren. Ein Mapping ohne Begründung lässt
sich später nicht prüfen und beim nächsten Thema nicht wiederverwenden.

---

## 2. Quellenwahl: welche Plattform wofür

| Quelle | Stärke | Zugang |
|---|---|---|
| **OpenAlex** | publizierte Artikel, Zitationszahlen, breite Abdeckung über 100.000 Venues | REST per Shell |
| **CrossRef** | DOI-Auflösung, exakte Verlagsmetadaten, Lizenzfelder | REST per Shell |
| **Semantic Scholar** | thematisch verwandte Arbeiten, Zitationsnetzwerke | REST per Shell |
| **Zenodo** | Datensätze, Anhänge, `files`-Array mit direkten Download-URLs | REST per Shell |
| **arXiv** | Informatik, ML, NLP, quantitative Preprints | arXiv-API per Shell, ergänzend `mcp__paper-search__search_papers` |
| **BASE, CORE, OpenAIRE, DOAJ, Europe PMC** | europäische Hochschulrepositorien, Open-Access-Volltexte, Projektberichte aus EU-Förderung | `mcp__paper-search__search_papers` mit `sources` |
| **SSRN** | Working Paper, Vorveröffentlichungen, juristische und ökonomische Diskussion | Websuche mit `site:ssrn.com` (keine öffentliche API) |
| **Web** | Behördenseiten, Verbandsberichte, Graue Literatur | `mcp__tavily__tavily_search` mit Domain-Filter, dazu Exa, Parallel und WebSearch |

**Arbeitsteilung in einem Satz:** Die wissenschaftlichen Datenbanken werden direkt über ihre REST-APIs
abgefragt, weil nur so Query, Paginierung und Trefferzahl exakt im Protokoll stehen. MCP-Server
decken ab, was keine brauchbare API hat oder sich per Shell nur mühsam abfragen lässt: weitere
Repositorien, Graue Literatur und das Lesen von Seiten und PDFs.

---

## 3. MCP-Tools

Die Server sind projektweit in `.mcp.json` im Repository-Wurzelverzeichnis konfiguriert. In Claude Code
heißen ihre Werkzeuge `mcp__<server>__<tool>`. Vor dem ersten Einsatz prüfen, welche tatsächlich
verbunden sind, und den Stand in `meta.phasen_log` (Phase 0) vermerken.

Alle Server sind ohne Bezahlung nutzbar. Die freien Kontingente der Suchdienste sind aber begrenzt und
ändern sich. Deshalb sind die Websuchen auf mehrere Anbieter mit **eigenem Index** verteilt: Fällt einer
wegen Kontingent oder Rate-Limit aus, mit dem nächsten weiterarbeiten und den Wechsel im Log vermerken.

| Server | Kosten | Schlüssel |
|---|---|---|
| `tavily` | 1.000 Credits im Monat | `TAVILY_API_KEY`, kostenlos bei tavily.com |
| `exa` | ohne Schlüssel mit niedrigem Rate-Limit | keiner |
| `parallel` | ohne Schlüssel mit niedrigem Rate-Limit | keiner |
| `fetch` | lokal, unbegrenzt | keiner |
| `duckduckgo` | lokal, ohne festes Kontingent | keiner |
| `paper-search` | lokal, Limits der jeweiligen Datenbank | optional `OPENALEX_API_KEY`, `CORE_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY` |

### Werkzeugwahl je Aufgabe

| Aufgabe | Bevorzugt | Fallback |
|---|---|---|
| Publizierte Literatur, Snowballing | REST per Shell (Abschnitt 4) | – |
| Weitere Repositorien (BASE, CORE, OpenAIRE, DOAJ, Europe PMC) | `mcp__paper-search__search_papers` | REST der jeweiligen Datenbank |
| Preprints | arXiv-API per Shell | `mcp__paper-search__search_papers` |
| Working Paper (SSRN) | Websuche mit `site:ssrn.com` | – |
| Graue Literatur mit Domain-Filter | `mcp__tavily__tavily_search` (`include_domains`) | WebSearch mit `site:` |
| Graue Literatur, breite Suche | WebSearch, `mcp__exa__web_search_exa`, `mcp__parallel__web_search` | `mcp__duckduckgo__search` |
| Ähnliche Studien zu einer bekannten Quelle | `mcp__exa__web_search_exa` mit Titel und Kernaussage als Query | Semantic Scholar Recommendations |
| Institutsseite systematisch erschließen | `mcp__tavily__tavily_map`, dann `tavily_crawl` | WebSearch mit `site:` und `filetype:pdf` |
| Landing Page **wörtlich** lesen | `mcp__fetch__fetch`, `mcp__tavily__tavily_extract` | `mcp__exa__web_fetch_exa`, `mcp__parallel__web_fetch` mit `full_content` |
| PDF lesen, Tabellen und Abbildungen | Datei per Shell nach `scratch/` laden, mit Read lesen | Jina Reader ohne Schlüssel: `curl -s https://r.jina.ai/<URL>` (20 Anfragen je Minute) |
| Titel deduplizieren | DOI- und Titelabgleich per Skript | – |

> [!IMPORTANT]
> **WebFetch fasst Seiten über ein kleines Modell zusammen, es liefert keinen Originaltext.** Zur
> Orientierung taugt es, als Beleg nicht. Lizenzangaben, Nutzungsbedingungen, Data Availability
> Statements und Stichprobengrößen nur aus `fetch`, `tavily_extract` oder der heruntergeladenen
> Datei übernehmen. Die Suchwerkzeuge von Exa und Parallel liefern **Auszüge**, keinen Volltext;
> auch sie sind kein Beleg.

**Nicht verwenden:** `tavily_research` und `mcp__parallel__web_decisions`. Beide recherchieren
selbständig über mehrere Schritte und liefern ein Ergebnis, dessen Suchweg sich nicht protokollieren
lässt. Für ein Suchprotokoll ist das wertlos.

**Protokollpflicht für jede Websuche:** Werkzeug, Query, Filter und Trefferzahl ins Log. Die Anbieter
liefern bei gleicher Query unterschiedliche Treffer; ohne Werkzeugangabe ist die Suche nicht
nachvollziehbar.

### Tavily (Graue Literatur, Seiten erschließen)

| Tool | Zweck | Wichtige Parameter |
|---|---|---|
| `tavily_search` | Websuche | `include_domains`, `exclude_domains`, `search_depth`, `include_raw_content` |
| `tavily_extract` | Seiteninhalt im Wortlaut | `urls`, `extract_depth`, `format` |
| `tavily_map` | Seitenstruktur einer Domain auflisten | `url`, `max_depth` |
| `tavily_crawl` | mehrere verlinkte Seiten einer Domain lesen | `url`, `max_depth` |

**Arbeitsmuster für Phase 3D:** erst `tavily_map` auf die Publikationsseite einer Institution, um zu
sehen, wo die Berichte liegen, dann `tavily_search` mit `include_domains` auf diese Domain, dann
`tavily_extract` auf die Treffer. Das Kontingent reicht für einige hundert Suchen im Monat; `tavily_crawl`
und `search_depth: "advanced"` verbrauchen mehrere Credits je Aufruf und nur gezielt einsetzen.

### Exa und Parallel (zusätzliche Suchindizes)

| Tool | Zweck | Wichtige Parameter |
|---|---|---|
| `mcp__exa__web_search_exa` | semantische Websuche, findet inhaltlich ähnliche Seiten auch ohne gleiche Stichworte | `query`, `numResults` |
| `mcp__exa__web_fetch_exa` | Seite als Markdown | `urls`, `maxCharacters` |
| `mcp__parallel__web_search` | Websuche mit Auszügen | `objective`, `search_queries` |
| `mcp__parallel__web_fetch` | Seiten als Markdown, mit `full_content: true` vollständig | `urls`, `full_content` |

Beide laufen ohne Schlüssel mit niedrigem, nicht veröffentlichtem Rate-Limit. Bei Fehlermeldungen zum
Limit auf einen anderen Suchdienst wechseln. Ein kostenloses Konto bei exa.ai oder parallel.ai hebt die
Grenze; der Schlüssel wird dann für Exa als Header `x-api-key` eingetragen, nur in der persönlichen
Konfiguration (`claude mcp add -s user`), nie in `.mcp.json`.

### Fetch (Seiten wörtlich lesen)

`mcp__fetch__fetch` ist der offizielle Referenzserver des MCP-Projekts. Er lädt eine Seite lokal und
wandelt sie ohne Zusammenfassung in Markdown um. Parameter: `url`, `max_length` (Standard 5.000 Zeichen),
`start_index` zum Weiterlesen langer Seiten, `raw` für unverändertes HTML.

Der Server **beachtet robots.txt** und verweigert den Abruf, wenn die Seite automatisierte Zugriffe
ausschließt oder robots.txt nicht erreichbar ist. Das ist gewollt und wird nicht abgeschaltet. Eine
Verweigerung ist selbst ein Befund für die Rechteprüfung; dann mit `tavily_extract` oder dem Download
per Shell weiterarbeiten und den Grund im Log vermerken.

### DuckDuckGo (Reserve)

`mcp__duckduckgo__search` (`query`, `max_results`) und `mcp__duckduckgo__fetch_content` (`url`). Der
Server liest die DuckDuckGo-Webseite aus, nicht eine offizielle API. Bei Bot-Schutz kommen leere
Ergebnisse zurück. Nur als Reserve, wenn die anderen Suchdienste ausgeschöpft sind, und eine leere
Antwort nicht als „keine Treffer" protokollieren.

### paper-search (weitere wissenschaftliche Datenbanken)

`mcp__paper-search__search_papers` durchsucht mehrere Datenbanken in einem Aufruf, gesteuert über den
Parameter `sources`. Für dieses Projekt wichtig sind die Quellen, für die das Repository sonst keinen
Zugang hat: BASE, CORE, OpenAIRE, DOAJ und Europe PMC. Die vollständige Liste der Einzelwerkzeuge zeigt
`/mcp` in der Sitzung.

- Je Datenbank eine eigene Abfrage, damit Trefferzahl und Quelle im Log getrennt stehen.
- Die Trefferliste ist **kein Lizenzbeleg**. Lizenzfelder kommen weiter aus OpenAlex, CrossRef oder der
  Landing Page (Abschnitt 5).
- Ohne `CORE_API_KEY` ist CORE stark gedrosselt; ein Schlüssel ist bei core.ac.uk kostenlos.
- Der Server läuft unter Python 3.12, das `uvx` beim ersten Start selbst herunterlädt. Die
  installierte Python-Version des Rechners spielt keine Rolle.

### Einrichtung

Tavily läuft lokal über `npx` und braucht Node.js. `fetch`, `duckduckgo` und `paper-search` laufen über
`uvx` und brauchen [uv](https://docs.astral.sh/uv/). Beim ersten Start im Projekt fragt Claude Code, ob
die Server aus `.mcp.json` verwendet werden dürfen. Kontrolle im Terminal mit `claude mcp list`, in
der Sitzung mit `/mcp`. Vorab prüft `python test_mcp_connections.py` Schlüssel, Endpunkte und
Programme.


## 4. REST-APIs per Shell

### OpenAlex (kostenloser Schlüssel empfohlen)

Seit Februar 2026 rechnet OpenAlex nach einem täglichen Budget ab. Ohne Schlüssel ist es klein, mit
einem kostenlosen Schlüssel von openalex.org zehnmal so groß. Einzelabrufe per DOI oder OpenAlex-ID
(`/works/doi:...`) sind unbegrenzt frei; Suche, Filter und Listen zehren vom Budget. Der Schlüssel geht
als Query-Parameter `api_key` mit und kommt aus der Umgebungsvariable `OPENALEX_API_KEY`. In Logs und
im Suchprotokoll die URL **ohne** diesen Parameter vermerken.

```bash
curl -s "https://api.openalex.org/works?search=QUERY&per-page=50&api_key=$OPENALEX_API_KEY" \
| python -c "
import sys, json
for w in json.load(sys.stdin).get('results', []):
    lic = (w.get('primary_location') or {}).get('license') or w.get('open_access', {}).get('oa_status')
    print(f\"{w.get('title','?')} ({w.get('publication_year','?')}) | {w.get('doi','-')} | Lizenz: {lic or 'KEINE ANGABE'}\")
"
```

Pagination über `page=2`, `page=3` oder per Cursor `cursor=*`. Vorwärts-Snowballing:
`https://api.openalex.org/works?filter=cites:W1234567890&per-page=50`.

### CrossRef (kein Schlüssel nötig)

```bash
curl -s "https://api.crossref.org/works?query=QUERY&rows=50" \
| python -c "
import sys, json
for it in json.load(sys.stdin).get('message', {}).get('items', []):
    lic = [l.get('URL') for l in it.get('license', [])] or ['KEINE ANGABE']
    print(f\"{it.get('title',['?'])[0]} | {it.get('DOI','-')} | Lizenz: {', '.join(lic)}\")
"
```

### Zenodo (Datensätze und echte Anhänge)

```bash
curl -s "https://zenodo.org/api/records?q=QUERY&size=50&type=dataset" \
| python -c "
import sys, json
for r in json.load(sys.stdin).get('hits', {}).get('hits', []):
    md = r.get('metadata', {})
    lic = (md.get('license') or {}).get('id', 'KEINE ANGABE')
    print(f\"{md.get('title','?')} | {r.get('doi','-')} | Lizenz: {lic}\")
    for f in r.get('files', []):
        print(f\"    Anhang: {f.get('key')} ({f.get('size')} B) -> {f.get('links',{}).get('self')}\")
"
```

Das `files`-Array ist die verlässlichste Quelle für **echte** Datenanhänge, weil es nur eigenständige
Dateien listet. Das Haupt-PDF steht dort allerdings ebenfalls drin und gehört **nicht** in
`daten_anhaenge`.

### Semantic Scholar (Snowballing und verwandte Arbeiten)

```bash
# Rückwärts (zitierte) und vorwärts (zitierende Arbeiten), paginiert über offset
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.xxxx/yyyy/references?fields=title,year,externalIds&limit=100"
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.xxxx/yyyy/citations?fields=title,year,externalIds&limit=100"

# Thematisch verwandt, ohne Zitationsbeziehung
curl -s "https://api.semanticscholar.org/recommendations/v1/papers/forpaper/DOI:10.xxxx/yyyy?fields=title,year,externalIds&limit=50"
```

Ohne Schlüssel gelten niedrige Rate-Limits. Bei HTTP 429 Pausen einlegen. Ein optionaler Schlüssel
wird als Header `x-api-key` mitgegeben, Wert aus der Umgebungsvariable `SEMANTIC_SCHOLAR_API_KEY`.

### arXiv

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:QUERY&start=0&max_results=50"
```

Liefert Atom-XML. Die Lizenz steht nicht in der Antwort, sondern auf der Abstract-Seite.

### SSRN

Eine öffentliche API gibt es nicht. Suche über WebSearch, `mcp__exa__web_search_exa` oder
`mcp__tavily__tavily_search` mit `site:ssrn.com` beziehungsweise `include_domains: ["ssrn.com"]`, dann die
Abstract-Seite mit `mcp__fetch__fetch` oder `tavily_extract` lesen. SSRN blockiert automatisierte
Zugriffe häufig; eine Verweigerung im Log vermerken und die Quelle nicht als einzigen Pfad einplanen.

---

## 5. Lizenzfelder je API

Direkt für die Rechteprüfung relevant. `source-compliance-check/scripts/harvest_license_signals.py` liest diese
Felder automatisiert.

| API | Feldpfad | Hinweis |
|---|---|---|
| OpenAlex | `primary_location.license`, `best_oa_location.license` | oft `null`. `null` heißt **keine Angabe**, nicht „frei". |
| OpenAlex | `open_access.oa_status` (`gold`, `green`, `hybrid`, `bronze`, `closed`) | **`bronze` ist die Falle:** frei lesbar, aber ohne Lizenz. |
| CrossRef | `license[].URL` plus `license[].content-version` | mehrere Einträge möglich (`vor-vm`, `am`, `tdm`). Der `tdm`-Eintrag ist für `N1` der einschlägige. |
| Zenodo | `metadata.license.id` | SPDX-Kürzel, zuverlässig |
| Semantic Scholar | `openAccessPdf.license` | oft leer |
| arXiv | Lizenzangabe am Record, nicht in der API-Kernantwort | manuell prüfen, mehrere Varianten im Umlauf |

> `oa_status: bronze` bedeutet: Der Verlag stellt frei lesbar, ohne eine Weiterverwendungslizenz zu
> erteilen. Für `N1` kann die TDM-Schranke tragen, für `N2` ist der Befund regelmäßig `gesperrt`. Das
> ist genau der Fall, den eine schnelle Prüfung als „Open Access, also frei" durchwinkt.

---

## 6. Thesaurus-Muster

Zwei ausgearbeitete Beispiele aus unterschiedlichen Domänen. Sie zeigen das **Muster**, nicht den
Inhalt. Für ein neues Thema wird der Thesaurus neu gebaut, nicht angepasst.

### Muster A: Urbane Radinfrastruktur und Nutzersicherheit

| Facette A (System) | Facette B (Mechanismus) | Facette C (Akteure) | Facette D (Methode) |
|---|---|---|---|
| `cycling network` / `Radnetz` | `perceived safety` / `subjektive Sicherheit` | `bicycle commuter*` / `Radpendler*` | `interview*` / `"semi-structured"` |
| `bicycle infrastructure` / `Radweg*` | `stress factor*` / `Stressbelastung` | `vulnerable road user*` / `VRU` | `"focus group*"` / `Fokusgruppe*` |
| `protected bike lane*` / `Radschnellweg` | `separation quality` / `Trennungsgüte` | `cargo bike*` / `Lastenrad*` | `"in-depth interview"` / `Leitfaden` |
| `active mobility` / `Radverkehr` | `route choice` / `Routenwahl` | `elderly cyclist*` / `Senioren` | `survey*` / `Befragung*` |
| `velomobility` / `bike sharing` | `vibration comfort` / `Oberflächengüte` | `transport planner*` / `Verkehrsplaner` | `"qualitative analysis"` / `Transkript` |

### Muster B: Werte-Erhebung in der Softwareentwicklung

| Facette A (System) | Facette B (Mechanismus) | Facette C (Akteure) | Facette D (Methode) |
|---|---|---|---|
| `requirements engineering` / `Anforderungserhebung` | `value elicitation` / `Werterhebung` | `indirect stakeholder*` / `indirekt Betroffene` | `interview*` / `Experteninterview` |
| `value sensitive design` / `VSD` | `value conflict*` / `Wertekonflikt` | `moral patient*` | `"focus group*"` / `Fokusgruppe*` |
| `participatory design` / `partizipative Gestaltung` | `deliberation` / `Deliberation` | `citizen*` / `Bürger*` | `"deliberative poll*"` |
| `algorithmic system*` / `algorithmische Systeme` | `legitimacy` / `Legitimität` | `affected communit*` / `Betroffenengruppe` | `"case study"` / `Fallstudie` |
| `sociotechnical system*` | `accountability` / `Verantwortung` | `software team*` / `Entwicklungsteam` | `ethnograph*` / `teilnehmende Beobachtung` |

**Was beide Muster gemeinsam haben** und was beim Neubau zu reproduzieren ist: Facette D trägt immer
sowohl Methodenbegriffe (`interview`) als auch Artefaktbegriffe (`Transkript`, `Leitfaden`). Nur die
Artefaktbegriffe finden eigenständige Datensätze in Repositorien, nur die Methodenbegriffe finden
Studien mit integrierten Erhebungen.

---

## 7. BibTeX-Export

Für Arbeiten mit DOI per Content Negotiation beim DOI-Resolver:

```bash
curl -sL -H "Accept: application/x-bibtex" "https://doi.org/10.xxxx/yyyy"
```

Für SSRN-Paper ohne DOI manuell:

```bibtex
@techreport{AutorJahr,
  author      = {Nachname, Vorname and Nachname2, Vorname2},
  title       = {Titel der Arbeit},
  year        = {2026},
  type        = {Working Paper},
  institution = {SSRN},
  url         = {https://ssrn.com/abstract=XXXXXXX},
  note        = {SSRN Working Paper}
}
```

Für Datensätze:

```bibtex
@misc{AutorJahrData,
  author       = {Nachname, Vorname},
  title        = {Titel des Datensatzes},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.XXXXXXX},
  note         = {Datensatz. Lizenz: CC BY 4.0}
}
```

Die Lizenz gehört in `note`, nicht nur in die findings.json. Wer die Bibliographie weitergibt, gibt
sonst die Rechtelage nicht mit weiter.

Besteht eine Zotero-Anbindung, Treffer dort ablegen statt BibTeX-Dateien zu pflegen.

---

## 8. Fehlerbehandlung

| Fehler | Ursache | Abhilfe |
|---|---|---|
| MCP-Werkzeug fehlt in der Sitzung | Server nicht freigegeben oder Schlüssel nicht gesetzt | `/mcp` bzw. `claude mcp list`; Umgebungsvariable prüfen, App neu starten |
| Tavily meldet 401 | `TAVILY_API_KEY` nicht gesetzt oder App nach `setx` nicht neu gestartet | Variable setzen, App vollständig beenden und neu starten |
| Exa oder Parallel melden Rate-Limit | Kontingent ohne Schlüssel erschöpft | auf einen anderen Suchdienst wechseln und den Wechsel im Log vermerken |
| `fetch` verweigert den Abruf | robots.txt schließt automatisierte Zugriffe aus oder ist nicht erreichbar | nicht umgehen; Befund für die Rechteprüfung, Seite mit `tavily_extract` oder per Download lesen und den Grund vermerken |
| `duckduckgo` liefert keine Treffer | Bot-Schutz von DuckDuckGo | nicht als „keine Treffer" werten, anderen Suchdienst nutzen |
| `paper-search` startet nicht | `uv` fehlt oder der erste Start lädt noch Python 3.12 | `uv` installieren; beim ersten Start ein bis zwei Minuten warten, dann `/mcp` erneut prüfen |
| Tavily startet unter Windows nicht | `npx` wird ohne Shell nicht gefunden | in `.mcp.json` `"command": "cmd"` und `"args": ["/c", "npx", "-y", "tavily-mcp@0.2.22"]` |
| MCP-Ausgabe abgeschnitten | Ausgabe über 25.000 Tokens | weniger URLs je Aufruf; bei `fetch` mit `start_index` abschnittsweise weiterlesen |
| Rate-Limit OpenAlex / CrossRef | zu viele Anfragen in kurzer Zeit, bei OpenAlex Tagesbudget erschöpft | Pausen einlegen, Seitengröße beibehalten statt mehr Einzelabfragen; für OpenAlex `OPENALEX_API_KEY` setzen |
| Rate-Limit Semantic Scholar | kein Schlüssel | Pausen einlegen, optional `SEMANTIC_SCHOLAR_API_KEY` als Header `x-api-key` |
| SSRN-Suche leer | Query zu eng | Begriffe weiten, Synonyme aus dem Thesaurus einsetzen |
| Zenodo liefert Haupt-PDF im `files`-Array | Normalverhalten | Haupt-PDF **nicht** nach `daten_anhaenge` übernehmen |
| `license: null` bei OpenAlex | Verlag meldet keine Lizenz | Befund `nicht_pruefbar`, **nicht** als „frei" werten |
| robots.txt nicht abrufbar (403, 404) | Host blockt oder führt keine | als „nicht feststellbar" dokumentieren, nicht als „kein Vorbehalt" |
| Landing Page hinter Cloudflare-Challenge | Bot-Schutz | `fetch` oder `tavily_extract` versuchen, sonst `nicht_pruefbar`. Bot-Schutz nicht umgehen. |

Die letzten drei Zeilen sind die Stellen, an denen eine Prüfung still zu einem Falschbefund wird: Ein
nicht abrufbares Signal ist kein negatives Signal.

---

## 9. Bekannte Grenzen

- **SSRN-Volltexte** liegen oft hinter einer Download-Schranke. `fetch` und `tavily_extract` erreichen die Abstract-Seite,
  nicht immer das PDF. Für die Rechteprüfung bedeutet eine Download-Schranke zugleich eine Frage nach dem
  rechtmäßigen Zugang.
- **OpenAlex-Abdeckung** ist stark bei STEM und großen sozialwissenschaftlichen Journals, schwächer bei
  regionalen Fachzeitschriften und sehr neuen Veröffentlichungen (Indexierungsverzug von Tagen bis
  Wochen).
- **Semantic Scholar** ist exzellent für Informatik-Zitationsnetze, dünn für Rechtswissenschaft. Dort
  OpenAlex-Zitationen als primär behandeln.
- **Graue Literatur ist nicht indexiert.** Kommunal- und Verbandsberichte finden sich nur über gezielte
  Domain-Suchen mit `filetype:pdf`. Ein Suchprotokoll, das Phase 3D auslässt, findet die
  Praxisperspektive strukturell nicht.
- **Qualitative Repositorien sind schlecht durchsuchbar.** QDR und ICPSR haben eigene Suchlogiken und
  erfordern häufig manuelles Browsen der Collections. Zeitbudget einplanen.
