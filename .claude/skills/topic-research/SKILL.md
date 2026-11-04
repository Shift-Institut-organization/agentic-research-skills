---
name: topic-research
description: >
  Erstellt ein strukturiertes, methodisch belastbares Suchprotokoll für ein Thema oder Projekt und
  sammelt erschöpfend qualitative Studien, Interviews, Datensätze und Graue Literatur aus
  Wissenschafts-Repositorien, Fachdatenbanken und Praxisportalen. Ergebnis sind zwei Dateien: ein
  menschenlesbares suchprotokoll_<thema>.md und eine maschinenlesbare findings_<thema>.json für die
  nachgelagerten Skills. Die Rechteprüfung der gefundenen Quellen (Lizenz und DSGVO) übernimmt
  anschließend der Skill source-compliance-check in einem frischen Subagenten.
  Nutze diesen Skill immer, wenn Quellen für ein Kompass-Thema gesucht oder gesammelt werden sollen,
  auch wenn der Auftrag nur beiläufig nach Quellen verlangt.
  Trigger-Phrasen: "Suchprotokoll erstellen", "Literaturrecherche", "qualitative Studien suchen",
  "Interviews suchen", "Daten sammeln", "Quellen für das Thema", "neues Thema einbetten",
  "search protocol", "systematic review", "Forschungsrecherche", "Recherche für den Kompass".
  Auch auslösen, wenn nur ein Thema genannt wird und erkennbar Quellen gebraucht werden, etwa
  "wir nehmen als nächstes ÖPNV" oder "was gibt es zu Akzeptanz von Lastenrad-Förderung".
  Nicht auslösen, wenn nur bereits vorliegende Quellen rechtlich geprüft werden sollen; dafür ist
  source-compliance-check zuständig.
---

# Skill: Themenrecherche und Suchprotokoll

## Ziel

Für ein gegebenes **Thema oder Projekt** ein vollständiges Suchprotokoll erstellen und **alle
relevanten Quellen erschöpfend** erfassen. Bevor die Quellen in den Kompass-Datenpool gelangen,
durchlaufen sie die Rechteprüfung im Skill `source-compliance-check` (Phase 6 dieses Ablaufs).

Der Skill erzeugt zwei Artefakte: `suchprotokoll_<thema>.md` (Dokumentation) und
`findings_<thema>.json` (Übergabe an die Folge-Skills).

## Leitprinzipien

1. **Kein künstlicher Abbruch.** Nicht nach 10 Treffern stoppen. Ziel ist möglichst vollständige
   Erfassung des Themas.
2. **Qualitative Interviews und Studien haben Vorrang im Zweifel.** Neben quantitativen Studien wird
   aktiv nach Erhebungen mit Interviews und Fokusgruppen gesucht, ebenso nach eigenständigen
   Transkripten und Leitfäden in Forschungsrepositorien. **Interviewdaten sind das wertvollste
   Material des Kompass und sollen erhalten bleiben**, nicht vorsorglich gemieden.
3. **Echte Datenanhänge, keine Pseudo-Anhänge.** Nur eigenständige Begleitdateien werden erfasst.
   Das Haupt-Paper ist **kein** Datenanhang und wird nie in `daten_anhaenge` dupliziert.
4. **Fachliche Auswahl und Rechteprüfung trennen.** Dieser Skill entscheidet, was fachlich trägt. Ob
   eine Quelle rechtlich genutzt werden darf, entscheidet ausschließlich `source-compliance-check`.
   Keine Quelle wird hier wegen vermuteter Lizenz- oder Datenschutzprobleme weggelassen.
5. **Nichts erfinden.** Keine Lizenzangabe, keine Fundstelle, keine Stichprobengröße, die nicht in der
   Quelle steht. Unbekanntes bleibt `null` beziehungsweise `unbekannt`.

---

## Pipeline

| Phase | Gegenstand | Ergebnis |
|---|---|---|
| 0 | Themen-Analyse und Plattform-Mapping | Archetyp, Plattformauswahl mit Begründung |
| 1 | Konzept-Strukturierung (Facetten A bis D) | Facettenliste |
| 2 | Suchbegriff-Thesaurus und Suchlogik | zweisprachiger Thesaurus, Boolesche Blöcke |
| 3 | Iterative Suche (A breit, B qualitativ, C Snowballing, D Praxis) | Roh-Treffer |
| 4 | Qualitäts- und Selektionskriterien | gefilterte Treffermenge |
| 5 | Findings erfassen | `findings_<thema>.json` (Rechercheteil) |
| 6 | Rechteprüfung übergeben | Subagent mit `source-compliance-check` |
| 7 | Protokoll schreiben und übergeben | `suchprotokoll_<thema>.md` + finales JSON |

### Inkrementelles Phasen-Logging

Beobachtungen, Hindernisse und API-Verhalten werden **sofort nach jeder Phase** dokumentiert, nicht
nachträglich. Nach jeder Phase ein Eintrag in `meta.phasen_log`, Zahlen in `meta.recherche_diagnose`
aktualisieren. Nachträglich geschriebene Logs glätten genau die Reibung, derentwegen man sie führt.

### Werkzeuge

Zu Beginn feststellen, welche MCP-Server in der Sitzung verbunden sind (`mcp__tavily__*`,
`mcp__exa__*`, `mcp__parallel__*`, `mcp__fetch__*`, `mcp__duckduckgo__*`, `mcp__paper-search__*`), und
das im Log von Phase 0 vermerken. Fehlt einer oder ist sein freies Kontingent erschöpft, mit dem
Fallback weiterarbeiten, nicht abbrechen.

| Aufgabe | Bevorzugt | Fallback |
|---|---|---|
| OpenAlex, CrossRef, Semantic Scholar, Zenodo, arXiv | REST per Shell | – |
| BASE, CORE, OpenAIRE, DOAJ, Europe PMC | `mcp__paper-search__search_papers` mit `sources` | REST der jeweiligen Datenbank |
| Working Paper (SSRN) | Websuche mit `site:ssrn.com` | – |
| Graue Literatur | `mcp__tavily__tavily_search` mit `include_domains`, `tavily_map` | WebSearch mit `site:` und `filetype:pdf` |
| Breite Websuche | WebSearch, `mcp__exa__web_search_exa`, `mcp__parallel__web_search` | `mcp__duckduckgo__search` |
| Landing Page lesen | `mcp__fetch__fetch`, `mcp__tavily__tavily_extract` | `mcp__exa__web_fetch_exa` |
| PDF lesen | Datei per Shell laden, mit Read lesen | – |

Zwei Regeln, die das Protokoll belastbar halten:

- **Die wissenschaftlichen Datenbanken immer direkt über REST abfragen**, nicht über einen
  Such-MCP. Nur so stehen Query, Paginierung und Trefferzahl exakt im Protokoll. Ausnahme sind die
  Datenbanken ohne bequemen REST-Zugang, die `paper-search` abdeckt; dort je Datenbank eine eigene
  Abfrage loggen.
- **Jede Websuche mit Werkzeugname loggen.** Die Suchdienste haben verschiedene Indizes und liefern
  bei gleicher Query verschiedene Treffer.
- **WebFetch fasst zusammen und liefert keinen Originaltext.** Was als Beleg in die findings geht
  (Stichprobengröße, Data Availability Statement, Fundstellen in `pruefhinweise`), stammt aus
  `fetch`, `tavily_extract` oder der heruntergeladenen Datei. Auszüge aus Suchergebnissen sind kein
  Beleg. `tavily_research` und `mcp__parallel__web_decisions` nicht verwenden: Ihr Suchweg lässt sich
  nicht protokollieren.

Endpunkte, Parameter und Einrichtung: `references/plattformen-und-apis.md`.

---

## Phase 0: Themen-Analyse und Plattform-Mapping

### 0.1 Recherche-Archetyp bestimmen

Aufgabenstellung beziehungsweise `project.md` analysieren und einem Archetyp zuordnen. Die Archetypen
steuern die Plattformauswahl, nicht den Inhalt:

1. **Archetyp 1: Verortetes Infrastruktur- oder Vorhabenprojekt.** Räumlich gebunden, Planungs- und
   Baubezug, Geodaten, lokale Akteure, technische Machbarkeit.
2. **Archetyp 2: Markt-, Problemfeld- und Strategierecherche.** Nutzer-Schmerzpunkte,
   Zahlungsbereitschaft, Wechselbarrieren, Verhaltensökonomie, Bedarfsanalysen.
3. **Archetyp 3: Technologie- und Methodenevaluation.** Werkzeuge, Architekturen, Benchmarks.

Ein Thema kann zwei Archetypen bedienen. Dann beide Plattformsets abfragen und das im Header
begründen.

### 0.2 Vier Dimensionen der Themen-Analyse

1. **Disziplinen:** Fachgebiete des Themas.
2. **Geographischer Fokus:** global, europäisch, national (D-A-CH), lokal.
3. **Methodischer Typ:** qualitativ, quantitativ, Mixed Methods.
4. **Zielgruppen:** Betroffene, Entscheider, Nutzergruppen, Institutionen. Für den Kompass besonders
   die **indirekt Betroffenen**, die das System nicht selbst nutzen.

### 0.3 Plattform-Mapping

Plattformauswahl nach Archetyp und Themenfeld ableiten und **mit Begründung** im Protokoll-Header
dokumentieren. Vollständige Liste mit Endpunkten, Pagination-Parametern und Lizenzfeldern:
**`references/plattformen-und-apis.md`**.

Immer abzufragende Basis: OpenAlex, Zenodo, Semantic Scholar, CrossRef, dazu BASE und OpenAIRE über
`paper-search`, wenn der Server verbunden ist. Bei qualitativer Vertiefung zwingend ergänzt um QDR,
GESIS/SSOAR, ICPSR, Harvard Dataverse und OSF.

👉 Log: `phase: "0_themen_mapping"`, in `beobachtung` auch die verbundenen MCP-Server

---

## Phase 1: Konzept-Strukturierung (Faceted Search)

Vier Kern-Dimensionen als strukturierte Liste definieren:

- **Facette A, Hauptphänomen / System / Infrastruktur:** der Kernbegriff der Domäne.
- **Facette B, Kernmechanismus / Problembereich / Handlungsfeld:** was an dem Phänomen untersucht
  wird (Sicherheit, Komfort, Akzeptanz, Kosten, Zugang, Gerechtigkeit).
- **Facette C, Betroffene / Akteursgruppe / Kontext:** Nutzergruppen, Betroffene ohne Nutzung,
  Entscheider, Planerinnen, Verbände.
- **Facette D, methodischer und empirischer Filter:** qualitative Methoden und empirische
  Primärdaten.

Facette C ist für den Kompass die inhaltlich wichtigste, weil die *moral patients* dort sitzen. Wer
sie zu eng fasst, findet nur Nutzerforschung.

---

## Phase 2: Suchbegriff-Thesaurus und Suchlogik

### 2.1 Zweisprachiges Mapping

Mindestens **5 bis 8 Synonyme pro Facette**, deutsch und englisch, wo beides existiert. Lokale
Phänomene und Regelwerke brauchen die deutschen Termini, zu generalisierbaren Mechanismen liegt die
bessere Literatur international vor. Zwei ausgearbeitete Beispiel-Thesauri aus unterschiedlichen
Domänen: `references/plattformen-und-apis.md`, Abschnitt *Thesaurus-Muster*.

Zur Begriffserweiterung die Schlüsselwörter und Titel der ersten Treffer aus Phase 3A auswerten und
den Thesaurus nachziehen. Das ersetzt nicht die fachliche Auswahl, liefert aber Varianten, die man
selbst übersieht.

### 2.2 Boolesche Block-Aggregation

Nicht hunderte Einzelkombinationen durchprobieren, sondern Blöcke bilden: Synonyme innerhalb einer
Facette mit `OR` klammern, Facetten mit `AND` verbinden.

```
STUFE 1: Vollschnittmenge (präzise, oft 10 bis 25 Treffer)
  (A) AND (B) AND (C) AND (D)

STUFE 2: Relaxation bei geringer Ausbeute
  2a Akteursfokus:     (A) AND (C) AND (D)
  2b Mechanismusfokus: (A) AND (B) AND (D)

STUFE 3: Freitext für APIs ohne Boolesche Logik (z. B. Semantic Scholar)
  3 bis 5 fokussierte Kernphrasen aus den Top-Begriffen, paginiert
```

👉 Log: `phase: "1_2_facetten_thesaurus"`

---

## Phase 3: Iterative Suche, Snowballing und Praxis-Berichte

### 3A Breite Multi-Plattform-Suche

Optimierte Queries je Plattform ausführen. **Paginieren**, nicht bei Seite 1 stehen bleiben
(OpenAlex `per-page=50`, Zenodo `size=50`, Folgeseiten solange die Relevanz hält). Laufend
dokumentieren und über DOI und Titel deduplizieren.

OpenAlex, CrossRef, Semantic Scholar und Zenodo per REST über die Shell abfragen, jede Query mit
Plattform, Suchstring, Seitenzahl und Trefferzahl im Log. Ergänzend arXiv per REST für Preprints,
`mcp__paper-search__search_papers` für BASE, CORE, OpenAIRE, DOAJ und Europe PMC (je Datenbank eine
Abfrage) und eine Websuche mit `site:ssrn.com` für Working Paper. Treffer anschließend mit
`mcp__fetch__fetch` auf der Landing Page nachlesen. Endpunkte: `references/plattformen-und-apis.md`,
Abschnitte 3 und 4.

Bei großen Titellisten aus mehreren Plattformen vor dem DOI-Abgleich auch über normalisierte Titel
abgleichen, weil Preprint und Publikation unterschiedliche DOI tragen.

**Deduplizieren mit Augenmaß.** Dieselbe Arbeit erscheint oft als SSRN-Working-Paper *und* als
Journal-Artikel. Die publizierte Fassung bevorzugen, die Preprint-Fassung aber vermerken, wenn sie
neuer ist oder frei zugänglich, während die publizierte hinter einer Schranke liegt. Für den Kompass
ist der frei zugängliche Volltext oft der einzige rechtlich nutzbare.

👉 Log: `phase: "3A_breite_suche"`, Status `ok | rauschen_hoch | api_issue`

### 3B Qualitativer Deep-Dive

**Auslöser:** Weniger als rund 30 Prozent der bisherigen Treffer enthalten Interviews, Fokusgruppen
oder Transkripte.

1. Gezielte Suchstrings: `"semi-structured interview"`, `"in-depth interview"`,
   `"qualitative interview"`, `"expert interview"`, `"interview guide"`, `"focus group"`. Deutsch bei
   D-A-CH-Themen: `"Leitfadeninterview"`, `"Experteninterview"`, `"Fokusgruppe"`,
   `"qualitative Befragung"`, `"Transkript"`.
2. Spezialrepositorien ansteuern: QDR, Zenodo mit `type=dataset` plus Keyword `interview`,
   GESIS/SSOAR, Harvard Dataverse, OSF.
3. Zwei Typen unterscheiden: Studien *mit integrierten* Interviews (O-Töne im Volltext) und
   *eigenständige* Interview-Datensätze (Transkripte, Audio, Leitfäden).

> [!TIP]
> Eigenständige Interview-Datensätze sind der ertragreichste Fund für den Kompass. Damit die
> Rechteprüfung sie zügig bearbeiten kann, schon beim Sammeln zwei Fundstellen in `pruefhinweise`
> notieren: wo die **Anonymisierungserklärung** steht (Methodenteil oder Data Availability Statement)
> und wo die **Nachnutzungsbedingungen des Repositoriums** stehen. Nur die Fundstellen, keine
> Bewertung: Die Prüfung liest selbst nach.
>
> Datensätze **ohne** Anonymisierungserklärung sind der Problemfall, nicht Transkripte als solche.
> Fehlt sie, lohnt die Suche nach der zugehörigen Publikation, die sie meist enthält.

👉 Log: `phase: "3B_qualitativer_boost"`, auch wenn der Auslöser nicht erreicht ist; dann mit dem
Anteil der Treffer mit Interviews in `beobachtung`. Der Validator verlangt den Eintrag, damit
„nicht nötig" von „vergessen" unterscheidbar bleibt.

### 3C Citation Snowballing

Zitationsnetzwerke der 2 bis 4 stärksten Seed-Studien verfolgen:

1. **Rückwärts:** zitierte Quellen über OpenAlex `referenced_works` beziehungsweise Semantic Scholar
   `/paper/DOI:<doi>/references`. Findet methodische Vorläufer.
2. **Vorwärts:** zitierende Arbeiten über OpenAlex `filter=cites:<OPENALEX_ID>&per-page=50`
   beziehungsweise Semantic Scholar `/paper/DOI:<doi>/citations`. Findet Folgestudien und
   Replikationen.
3. **Thematisch benachbart:** Semantic Scholar `/recommendations/v1/papers/forpaper/DOI:<doi>` liefert
   Arbeiten, die weder zitieren noch zitiert werden, aber denselben Gegenstand behandeln. Gerade bei
   interdisziplinären Themen findet das, was die Zitationskette verfehlt.
4. **Ähnliche Studien im Web:** `mcp__exa__web_search_exa` mit Titel und Kernaussage einer Seed-Studie
   als Query. Exa sucht semantisch und findet auch Berichte und Graue Literatur, die in keinem
   Zitationsgraphen stehen.

👉 Log: `phase: "3C_citation_snowballing"`

### 3D Praxis-, Kommunal-, Verbands- und NGO-Berichte

Reale Stakeholder-Perspektiven, Richtlinien und Verbandsdaten erfassen. Institutslisten je
Themenfeld: `references/plattformen-und-apis.md`, Abschnitt 1. Vorgehen je Institution:

1. `mcp__tavily__tavily_map` auf die Publikationsseite, um zu sehen, wo die Berichte liegen
2. `mcp__tavily__tavily_search` mit `include_domains` auf diese Domain und den Facettenbegriffen
3. `mcp__tavily__tavily_extract` auf die Treffer, um Methodik und Herausgeber zu prüfen

Ohne Tavily oder bei erschöpftem Kontingent: WebSearch, `mcp__exa__web_search_exa` oder
`mcp__parallel__web_search` mit `site:<domain>` und `filetype:pdf`, Treffer mit `mcp__fetch__fetch`
lesen.

**Quellentypisierung präzise halten.** `quelle_typ` konkret angeben (`municipal_report`,
`verband_report`, `survey_report`, `market_study`, `ngo_report`, `policy_paper`, `guideline`,
`whitepaper`), herausgebende Organisation in `quelle_plattform` und `institutionen_genannt`. Die
Rechteprüfung behandelt diese Gruppe gesondert und braucht die genaue Typisierung.

👉 Log: `phase: "3D_praxis_berichte"`

---

## Phase 4: Qualitäts- und Selektionskriterien

**Einschluss (mindestens 4 explizit machen):** methodische Eignung (qualitativ, quantitativ oder
fundierter Praxisbericht), Relevanz für Stakeholder- oder Betroffenenperspektive, Zeitraum
(Richtwert ab 2015, themenangepasst), Datenverfügbarkeit.

**Ausschluss (mindestens 3):** rein spekulative Arbeiten ohne Methodik, Produktwerbung ohne
Validierungsdaten, fachfremde Szenarien.

Fachliche Selektion und Rechteprüfung **nicht vermischen.** Eine Quelle, die fachlich trägt, aber
rechtlich scheitern könnte, bleibt drin. Aussortiert wird sie erst in der Rechteprüfung, dort mit
Begründung. Nur so bleibt im Protokoll sichtbar, was der Rechtsrahmen gekostet hat.

👉 Log: `phase: "4_qualitaets_selektion"`

---

## Phase 5: Findings erfassen

Für jeden qualifizierten Treffer sofort einen Eintrag in `findings_<thema>.json` anlegen.
Vollständiges Schema, Feldsemantik und Extraktionsregeln je API:
**`references/findings-schema.md`**. Die Blöcke `lizenz` und `datenschutz` sowie `meta.aussortiert`
und `meta.review_queue` bleiben leer. Sie befüllt ausschließlich `source-compliance-check`.

Die beiden Regeln, an denen Läufe erfahrungsgemäß scheitern:

- **`daten_anhaenge` enthält ausschließlich eigenständige Begleitdateien.** Niemals die DOI-URL, das
  Open-Access-PDF des Hauptartikels oder eine Pseudo-URL wie `...#appA`. Ist der Leitfaden auf den
  letzten Seiten des Hauptdokuments abgedruckt, wird das über
  `qualitative_daten.interview_leitfaden_verfuegbar: true` erfasst und im Freitext erwähnt, nicht als
  Anhang. Default ist das leere Array.
- **`qualitative_daten` wird für jeden Eintrag gepflegt**, auch wenn die Antwort überall `false`
  lautet. Leere Felder sind später nicht von ungeprüften zu unterscheiden.

Danach validieren:

```bash
python scripts/validate_findings.py findings_<thema>.json --stage research
```

Das kostet Sekunden und verhindert, dass die Rechteprüfung auf einer kaputten Datei aufsetzt.

👉 Log: `phase: "5_findings"`

---

## Phase 6: Rechteprüfung übergeben

Die Rechteprüfung läuft in einem **frischen Subagenten ohne den Sammelkontext**. Das ist der Kern des
Verfahrens, keine Formalie: Wer 45 Quellen mühsam zusammengesucht hat, liest Lizenztexte als
Bestätigung und nicht als Prüfung.

Den Subagenten (Agent-Werkzeug) mit folgendem Auftrag starten, und mit **nichts darüber hinaus**:

- Skill `source-compliance-check` auf `findings_<thema>.json` anwenden
- Pfad der Datei und Thema
- die Nutzungsarten `N1` bis `N3` aus `meta.nutzungsarten`

Nicht mitgeben: Relevanzbegründungen, Einschätzungen zur Wichtigkeit einzelner Quellen, Vermutungen
zur Rechtslage. Steht kein Subagent zur Verfügung, die Prüfung in einer neuen Sitzung ausführen
lassen und das im Protokoll als Limitation vermerken.

Der Subagent ergänzt die findings-Datei um die Prüfblöcke und schreibt `rechtebericht_<thema>.md`.
Erst danach geht es mit Phase 7 weiter.

---

## Phase 7: Output

### `suchprotokoll_<thema>.md`

0. Themen-Analyse und Plattform-Mapping, mit Begründung der Auswahl
1. Suchstrategie: Facetten und Kombinationslogik
2. Suchbegriff-Thesaurus
3. Plattformspezifische Queries und Snowballing-Pfade
4. Qualitäts- und Selektionskriterien
5. Fundstellen-Übersicht (Tabelle, mit Kennzeichnung von Interviews und Datenanhängen)
6. **Rechteprüfung:** Verweis auf `rechtebericht_<thema>.md` und dessen Kennzahlen (Verteilung der
   Freigabeklassen, Zahl der Aussortierten, Länge der Review-Queue). Keine eigene Bewertung.
7. Recherche-Log und Transparenzbericht: Phasen-Logs, Reibungsverluste, Rauschen, Limitationen
8. Nächste Schritte und offene Entscheidungen für das Team

### `findings_<thema>.json`

Vollständig befüllt nach `references/findings-schema.md`, mit `meta.recherche_diagnose` und
lückenlosem `meta.phasen_log`. Nach der Rechteprüfung abschließend validieren:

```bash
python scripts/validate_findings.py findings_<thema>.json --stage compliance
```

### Bibliographie auf Anforderung

Wird eine zitierfähige Liste gebraucht, BibTeX je DOI über den DOI-Resolver abrufen
(`Accept: application/x-bibtex`). Für SSRN-Working-Paper ohne DOI manuell als `@techreport`
aufbauen, Muster in `references/plattformen-und-apis.md`, Abschnitt 7.

---

## Qualitätssicherung

Vor Übergabe prüfen:

- [ ] Recherche erschöpfend (30+ Einträge beziehungsweise alle auffindbaren relevanten Quellen)
- [ ] Mindestens 3 Facetten in jeder Basis-Query kombiniert
- [ ] Phase 3B qualitativer Deep-Dive ausgeführt
- [ ] Phase 3C Snowballing auf Seed-Studien angewendet, vorwärts und rückwärts
- [ ] Phase 3D Praxis- und NGO-Quellen eingebunden
- [ ] `meta.phasen_log` für alle Phasen lückenlos
- [ ] `meta.recherche_diagnose` vollständig (Roh-Treffer, Rauschquote, Sättigungsgrund)
- [ ] `daten_anhaenge` enthält ausschließlich eigenständige Begleitdateien, sonst `[]`
- [ ] Im Haupttext abgedruckte Anhänge in `qualitative_daten` dokumentiert, nicht in `daten_anhaenge`
- [ ] `qualitative_daten` für jeden Eintrag gepflegt
- [ ] Rechteprüfung in frischem Subagenten durchgeführt, `rechtebericht_<thema>.md` liegt vor
- [ ] `validate_findings.py --stage compliance` läuft ohne Fehler durch
- [ ] Alle Dateien im Arbeitsverzeichnis gespeichert

---

## Referenzen

| Datei | Inhalt | Wann lesen |
|---|---|---|
| `references/plattformen-und-apis.md` | Plattformliste, API-Endpunkte, Pagination, MCP-Tools, Fallbacks, Thesaurus-Muster, BibTeX | Phase 0, 2, 3 |
| `references/findings-schema.md` | JSON-Schema, Feldsemantik, Extraktionsregeln je API | Phase 5 |
| `scripts/validate_findings.py` | Validiert findings.json gegen das Schema (`--stage research` oder `compliance`) | Phase 5, Phase 7 |
