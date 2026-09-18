--- 
name: suchprotokoll_recherche
description: >
  Erstellt ein strukturiertes Suchprotokoll für ein gegebenes Thema oder Projekt.
  Sucht systematisch und erschöpfend nach qualitativen Studien, Interviews, Datensätzen
  und Grauer Literatur in öffentlichen Repositorien und themenspezifischen Plattformen.
  Speichert alle Fundstellen samt Datenanhängen als maschinenlesbare findings.json für die
  nachgelagerte Stakeholder-Analyse. Trigger-Phrasen: "Suchprotokoll erstellen",
  "Literaturrecherche", "qualitative Studien suchen", "search protocol",
  "systematic review", "Forschungsrecherche", "Daten sammeln", "Interviews suchen".
---

# Skill: Suchprotokoll & Datensammlung (suchprotokoll_recherche)

## Ziel
Für ein gegebenes **Thema oder Projekt** ein vollständiges, methodisch fundiertes
Suchprotokoll erstellen und **alle relevanten Quellen erschöpfend** als strukturierte
**`findings_<thema>.json`** im Arbeitsverzeichnis speichern.

**Wichtigste Leitprinzipien:**
1. **Kein künstlicher Abbruch:** Nicht nach 10 Treffern stoppen! Das Ziel ist eine möglichst vollständige Erfassung aller relevanten Quellen (Richtwert: **30–50+ validierte Einträge**, sofern das Thema dies hergibt).
2. **Besonderer Fokus auf qualitative Interviews & Studien:** Neben quantitativen/technischen Studien soll aktiv und gezielt nach qualitativen Erhebungen gesucht werden – sowohl nach Studien mit integrierten Interviews/Fokusgruppen als auch nach eigenständigen Interviewtranskripten und Leitfäden in Forschungsrepositorien.
3. **Erfassung von echten Datenanhängen & Begleitmaterialien:** Alle verfügbaren *eigenständigen* Anhänge (separate Transkripte, externe Leitfäden, ESM-Dateien, Datensätze in Repositorien) werden im JSON mit Typ und Link erfasst. **Wichtig:** Das Haupt-Paper bzw. Publikations-PDF selbst ist **kein** Datenanhang und darf niemals in `daten_anhaenge` dupliziert werden. Wenn keine separaten Begleitdateien existieren, bleibt `daten_anhaenge: []` strikt leer.

---

## Workflow

### Inkrementelles Phasen-Logging & Diagnose-Prinzip
> **Zentrales Transparenz-Gebot:** Der Agent dokumentiert Beobachtungen, Hindernisse und API-Verhalten **sofort nach jeder einzelnen Phase** (In-Situ).
> Nach Abschluss jeder Phase wird ein Eintrag in das Array `meta.phasen_log` geschrieben und die Zahlen in `meta.recherche_diagnose` aktualisiert.
> Dadurch wird verhindert, dass Fehlermeldungen, Rauschen oder Ausweichmanöver im Nachhinein geglättet oder vergessen werden.

---

### Phase 0: Themen-Analyse & Plattform-Mapping

#### 0.1 Bestimmung des Recherche-Archetyps
Analysiere die Aufgabenstellung bzw. `project.md` und ordne sie einem von **drei Recherche-Archetypen** zu:

1. **Archetyp 1: Infrastruktur- & Mobilitätsprojekt** (z. B. Radschnellweg, geschützte Radverkehrsanlagen, Fahrradparkhaus)
   - *Fokus:* Räumlich verortet, Verkehrs-/Bauplanung, Geodaten, lokale Akteure, technische Machbarkeit, Oberflächenqualität.
2. **Archetyp 2: Markt-, Problemfeld- & Strategierecherche (Themen-Recherche)** (z. B. Betriebliches E-Bike-Leasing, Akzeptanz von Lastenrad-Förderprogrammen, Sharing-Systeme)
   - *Fokus:* Nutzer-Schmerzpunkte, Zahlungsbereitschaft, Wechselbarrieren (*Switching Costs*), Verhaltensökonomie, Bedarfsanalysen, Flottenmanagement.
3. **Archetyp 3: Technologie- & Methodenevaluation** (z. B. IoT-Sensorik, Algorithmen, KI-Tools)
   - *Fokus:* Werkzeuge, Architekturen, Benchmarks, Software-Tools.

#### 0.2 Vier Dimensionen der Themen-Analyse
1. **Disziplin(en):** Fachgebiete des Themas (z. B. Verkehrsplanung, Geographie, Human Factors, Public Health, Sensordatenverarbeitung, Informatik).
2. **Geographischer Fokus:** Global, europäisch, national (D-A-CH / Deutschland), lokal/regional.
3. **Methodischer Typ:** Qualitativ (Interviews, Fokusgruppen, qualitative Inhaltsanalyse, O-Töne), quantitativ (Surveys, Paneldaten, Sensordaten), Mixed Methods.
4. **Zielgruppen im Thema:** Betroffene, Entscheider (z. B. Radpendler, Alltagsradler, Verkehrsplaner, Kommunalverwaltung), Nutzergruppen, Institutionen.

#### 0.3 Plattform-Mapping nach Archetyp & Themenfeld
Leite daraus ab, **welche Plattformen** für dieses Thema relevant sind:

```
STANDARD (immer abfragen):
  - OpenAlex          — interdisziplinäre Wissenschaftsliteratur (REST API, paginierbar)
  - Zenodo            — Preprints, Datensätze, Graue Literatur, Transkripte (REST API)
  - Semantic Scholar  — KI-gestützte Literatursuche & Paper-Graphen

QUALITATIVE FORSCHUNG & INTERVIEW-REPOSITORIEN (Pflicht bei qualitativer Vertiefung):
  - QDR               — Qualitative Data Repository (qdr.syr.edu, spezialisiert auf Interviewdaten & Transkripte)
  - GESIS / SSOAR     — Archivierte Befragungen, qualitative Studien (DE-Fokus, ssoar.info)
  - ICPSR             — Quantitative + qualitative Sozialdaten (icpsr.umich.edu)
  - Harvard Dataverse — Offene Forschungsdaten & qualitative Anhänge (dataverse.harvard.edu)
  - OSF               — Open Science Framework (osf.io, Preprints & Projektanhänge)

MOBILITÄT, WIRTSCHAFTS- & VERHALTENSFORSCHUNG (Archetyp 2 / Markt- & Mobilitätsthemen):
  - TRID              — Transport Research International Documentation (trid.trb.org, weltweiter Standard für Verkehrsdaten)
  - SSOAR / GESIS     — empirische Sozial-, Mobilitäts- und Raumforschung im D-A-CH-Raum
  - EconStor / RePEc  — Open-Access-Arbeitspapiere zu Mikromobilität, Subventionsökonomie & Verkehrsmittelwahl
  - DLR / WVI         — Mobilitätsberichte, Pendlerbefragungen & Paneldaten

PRAXIS, KOMMUNEN, VERBÄNDE & NGOS (Graue Literatur):
  - Kommunal & Bund:  Difu, BBSR, UBA, BASt, Agora Verkehrswende, BMDV, Landesministerien
  - Verbände & NGOs:  ADFC (Fahrradklima-Test), VCD, Zukunft Fahrrad, European Cyclists' Federation (ECF)

NACH WEITEREN THEMENFELDERN:
  Ingenieurwesen / Technik:   IEEE Xplore, ACM Digital Library, arXiv (cs.HC, eess.SP)
  Medizin / Public Health:    PubMed / MEDLINE, Cochrane Library, WHO IRIS
  Stadtplanung / Mobilität:   TRID (trid.trb.org), EU Open Data Portal, GovData.de
  Software & Tools:           GitHub (topic:, language:), Hugging Face
```

Dokumentiere die Auswahl mit Begründung im Protokoll-Header.
👉 **Phasen-Log Eintrag:** `phase: "0_themen_mapping"`, `status: "ok" | "friction"`, `beobachtung: "..."`

---

### Phase 1: Konzept-Strukturierung (Faceted Search)

Definiere **4 universelle Kern-Dimensionen (Facetten A–D)** als strukturierte Liste:

- **Facette A – Hauptphänomen / Infrastruktur / System:** Kernbegriff der Domäne (z. B. `cycling network`, `bicycle infrastructure`, `Radverkehrsanlagen`, `bike sharing`, `cargo bike`).
- **Facette B – Kernmechanismus / Problembereich / Handlungsfeld:** 
  - *Sicherheit & Komfort:* `perceived safety`, `stress indicators`, `vibration comfort`, `surface roughness`, `separation quality`.
  - *Nutzung & Akzeptanz:* `route choice`, `modal shift`, `barrier-free`, `docking stations`, `fleet management`.
- **Facette C – Betroffene / Akteursgruppe / Kontext:** 
  - *Nutzergruppen:* Radpendler, Alltagsradler, Senioren, Lastenradnutzende, vulnerable Verkehrsteilnehmer.
  - *Entscheider & Planer:* Kommunale Verkehrsplanung, Tiefbauamt, ADFC, Mobilitätsverbände.
- **Facette D – Methodischer & empirischer Filter:** Qualitative Methoden (Interviews, Fokusgruppen, Leitfäden, O-Töne) & empirische Primärdaten (Surveys, Ride-Along-Studien, Sensordaten).

---

### Phase 2: Suchbegriff-Thesaurus & Suchlogik

#### 2.1 Zweisprachiges Thesaurus-Mapping (DE / EN)
> **Zentrales Gebot bei themenspezifischer Recherche:** 
> Lokale Phänomene und Richtlinien (wie deutsche ERA-Regelwerke, Radwegeführung, ADFC-Klimatests) müssen im **deutschsprachigen Raum** mit Begriffen wie `Radweg`, `Radverkehrsanlage`, `Trennungsgüte`, `Radpendler` gesucht werden.
> Gleichzeitig existieren zu sicherheits- und fahrverhaltensökonomischen Kernmechanismen (z. B. `perceived cycling safety`, `route detour choice`, `vibration comfort`) hochqualitative **internationale Studien**, die mit englischen Fachtermini erschlossen werden müssen.

Erstelle eine Tabelle mit mind. **5–8 Synonymen/Varianten pro Facette** (zweisprachig wo relevant):

**Referenz-Thesaurus: Urbane Radinfrastruktur & Nutzersicherheit (The Bicycle Example):**
| Facette A (Infrastruktur / Radverkehr) | Facette B (Sicherheit / Schmerzpunkte) | Facette C (Zielgruppe / Akteure) | Facette D (Qualitativ / Empirisch) |
|---|---|---|---|
| `cycling network` / `Radnetz` | `perceived safety` / `subjektive Sicherheit` | `bicycle commuter*` / `Radpendler*` | `interview*` / `"semi-structured"` |
| `bicycle infrastructure` / `Radweg*` | `stress factor*` / `Stressbelastung` | `vulnerable road user*` / `VRU` | `"focus group*"` / `fokusgruppe*` |
| `protected bike lane*` / `Radschnellweg` | `separation quality` / `Trennungsgüte` | `cargo bike*` / `Lastenrad*` | `"in-depth interview*"` / `leitfaden` |
| `active mobility` / `Radverkehr` | `route choice` / `Routenwahl` | `elderly cyclist*` / `Senioren` | `Befragung*` / `survey*` / `O-Töne` |
| `velomobility` / `bike sharing` | `vibration comfort` / `Oberflächengüte` | `transport planner*` / `Verkehrsplaner` | `"qualitative analysis"` / `transkript` |

#### 2.2 Wie der Agent vollständige Abdeckung garantiert (Such- & Relaxationslogik)

> **Kein manuelles Durchprobieren von Einzelwörtern:** Der Agent führt nicht hunderte Einzelkombinationen aus, sondern nutzt **Boolesche Block-Aggregation**:
> 1. **Innerhalb einer Facette:** Alle Synonyme werden mit `OR` geklammert: `(Synonym1 OR Synonym2 OR ...)`
> 2. **Zwischen den Facetten:** Die Blöcke werden mit `AND` verbunden.

Um **vollständige Erschöpfung** zu garantieren, wendet der Agent eine **3-Stufen-Recherche** an:

```
STUFE 1: Vollschnittmenge (Sehr präzise, ca. 10–25 Treffer)
  Query: (Facette A) AND (Facette B) AND (Facette C) AND (Facette D)

STUFE 2: Relaxation bei geringer Ausbeute (Breiterer Fangbereich)
  Query 2a (Nutzer-/Akteursfokus): (Facette A) AND (Facette C) AND (Facette D)
  Query 2b (Mechanismus-/Problemfokus): (Facette A) AND (Facette B) AND (Facette D)

STUFE 3: Freitext- & Keyword-Suche (für APIs ohne komplexe Boolesche Logik wie Semantic Scholar)
  Query: 3–5 fokussierte Kernphrasen aus den Top-Begriffen paginiert abfragen:
  - "urban bicycle commuter perceived safety interview", "protected bike lane separation stress focus group", "cyclist route choice surface roughness qualitative study"
```

👉 **Phasen-Log Eintrag:** `phase: "1_2_facetten_thesaurus"`, `status: "ok"`, `beobachtung: "..."`

---

### Phase 3: Iterative Suche, Snowballing & Praxis-Berichte

Die Recherche erfolgt in vier systematischen Schritten:

#### Phase 3A: Breite Multi-Plattform-Suche (Erschöpfend & Paginiert)
1. Führe für jede ausgewählte Plattform optimierte Queries aus (via `read_url_content`, `search_web`, APIs oder `browser_subagent`).
2. **Paginierung nutzen:** Begrenze Abfragen nicht auf die erste Seite (z. B. bei OpenAlex `per-page=50`, bei Zenodo `size=50`, Folgeseiten mit `page=2` abrufen), solange Treffer hohe Relevanz aufweisen.
3. Dokumentiere Treffer laufend und dedupliziere über DOI / Titel.
👉 **Phasen-Log Eintrag:** `phase: "3A_breite_suche"`, `status: "ok" | "rauschen_hoch" | "api_issue"`, `beobachtung: "<Anzahl Roh-Treffer, Rauschanteil, Verhalten der APIs>"`

#### Phase 3B: Gezielter Qualitative & Interview Deep-Dive (Qualitative Harvest & Boost)
> **Qualitätscheck:** Wenn weniger als ca. 30 % der bisherigen Treffer qualitative Interviews, Fokusgruppen oder Transkripte enthalten, starte sofort eine **gezielte qualitative Nachrecherche**:

1. **Gezielte Interview-Suchstrings anwenden:**
   - `"semi-structured interview"` OR `"in-depth interview"` OR `"qualitative interview"` OR `"expert interview"` OR `"interview guide"` OR `"focus group"`
   - Deutsche Begriffe bei D-A-CH-Themen: `"Leitfadeninterview"` OR `"Experteninterview"` OR `"Fokusgruppe"` OR `"qualitative Befragung"` OR `"Transkript"`
2. **Spezifische Repositorien für qualitative Daten & Transkripte ansteuern:**
   - **QDR (Qualitative Data Repository):** Archivierte Interview-Projekte und Transkript-Dumps.
   - **Zenodo Datasets:** Suche mit `type=dataset` und Keyword `interview` / `qualitative`.
   - **GESIS / SSOAR:** Qualitative Sozial- und Mobilitätsstudien mit Interviewdaten.
   - **Harvard Dataverse & OSF:** Studien mit interviewbezogenen Codebooks / Transkript-Dateien.
3. **Zwei Typen qualitativer Fundstellen erfassen:**
   - *Studien mit integrierten Interviews* (mit O-Tönen im Volltext)
   - *Standalone Interview-Datensätze* (Transkripte, Audio-/Textdaten, Leitfäden in Repositorien).
👉 **Phasen-Log Eintrag:** `phase: "3B_qualitativer_boost"`, `status: "ok" | "daten_duenn"`, `beobachtung: "<Gefundene Transkripte, Repositorien-Verfügbarkeit>"`

#### Phase 3C: Citation Snowballing (Vorwärts- & Rückwärts-Recherche)
> **Ziel:** Vollständige Erschöpfung des Forschungsstandes durch Verfolgen von Zitationsnetzwerken der 2–4 stärksten identifizierten Seed-Studien.

1. **Rückwärts-Snowballing (Backward Search):**
   - Frage über OpenAlex (`referenced_works`) oder Semantic Scholar (`references`) die im Literaturverzeichnis der Seed-Studie zitierten Quellen ab.
   - Identifiziere methodische Vorläufer und zugrundeliegende qualitative Studien.
2. **Vorwärts-Snowballing (Forward Search):**
   - Frage über OpenAlex (`filter=cites:<OPENALEX_ID>&per-page=50`) oder Semantic Scholar (`citations`) neuere Arbeiten ab, die die Seed-Studie zitieren.
   - Findet neuere empirische Folgestudien, Replikationen und aktuelle Weiterentwicklungen.
👉 **Phasen-Log Eintrag:** `phase: "3C_citation_snowballing"`, `status: "ok"`, `beobachtung: "<Welche Seed-Studien, wie viele neue Arbeiten identifiziert>"`

#### Phase 3D: Praxis-, Kommunal-, Verbands- & NGO-Berichte (Graue Literatur)
> **Ziel:** Reale Stakeholder-Perspektiven, Richtlinien, Verbandsdaten und Problemstellungen aus der Praxis erfassen.

1. **Gezielte Portal- & Domain-Recherche** (via `search_web` mit Domain-Filtern und `filetype:pdf`):
   - **Kommunalforschung & Institute:** Difu, BBSR, UBA, BASt, Agora Verkehrswende, Wuppertal Institut.
   - **Verbände & Zivilgesellschaft:** ADFC, VCD, Zukunft Fahrrad, European Cyclists' Federation (ECF), VDV.
   - **Ministerien & Fachbehörden:** BMDV, Bundesamt für Logistik und Mobilität (BALM), Landesverkehrsministerien.
2. **Präzise Quellentypisierung:**
   - Als `quelle_typ` den konkreten Typ angeben: `"municipal_report"`, `"verband_report"`, `"survey_report"`, `"market_study"`, `"ngo_report"`, `"policy_paper"`, `"guideline"`, `"whitepaper"`, `"report"`.
   - Die konkrete herausgebende Organisation (z. B. `"ADFC"`, `"Difu"`, `"UBA"`, `"BASt"`, `"BBSR"`, `"Agora Verkehrswende"`) in `quelle_plattform` und `institutionen_genannt` eintragen.
👉 **Phasen-Log Eintrag:** `phase: "3D_praxis_berichte"`, `status: "ok"`, `beobachtung: "<Gefundene Praxis-Dokumente & Verbandsberichte>"`

---

### Phase 4: Qualitäts- und Selektionskriterien

Definiere explizite Kriterien:

**Einschlusskriterien (mindestens 4):**
- Methodische Eignung: Sowohl qualitative Erhebungen (Interviews, Fokusgruppen) als auch empirisch-quantitative Studien und fundierte Praxisberichte.
- Relevanz für Stakeholder/Nutzerperspektive oder technische Machbarkeit.
- Zeitraum (z. B. ab 2015 bzw. themenangepasst).
- Datenverfügbarkeit (Open Access, frei zugängliche Datensätze oder strukturierte Metadaten/Abstracts).

**Ausschlusskriterien (mindestens 3):**
- Rein spekulative Arbeiten ohne Methodik/Empirie/Praxisbasis.
- Reine Produktwerbung ohne Validierungsdaten.
- Nicht zum Projektkontext passende Disziplinen/Szenarien.

👉 **Phasen-Log Eintrag:** `phase: "4_qualitaets_selektion"`, `status: "ok"`, `beobachtung: "<Filter-Quote, verworfene Arbeiten mit Begründung>"`

---

### Phase 5: Findings erfassen & als JSON speichern

> **Metadaten direkt erfassen:** Für jeden qualifizierten Treffer wird sofort ein Eintrag in `findings_<thema>.json` erstellt.
> Neben den Standardfeldern müssen **qualitative Details**, **alle Datenanhänge** sowie die **Diagnose-Metadaten und das Phasen-Log** erfasst werden!

#### 5.1 findings_<thema>.json Schema

```json
{
  "meta": {
    "thema": "string",
    "erstellungsdatum": "ISO-8601",
    "suchprotokoll_version": "2.0",
    "quellen_count": 0,
    "recherche_diagnose": {
      "treffer_roh_gesichtet": 180,
      "gefiltert_irrelevant": 135,
      "validiert_gespeichert": 45,
      "saettigungsgrund": "Keine neuen qualifizierten Treffer nach Paginierung bis Seite 4 und Zitationssuche"
    },
    "phasen_log": [
      {
        "phase": "0_themen_mapping | 1_2_facetten_thesaurus | 3A_breite_suche | 3B_qualitativer_boost | 3C_citation_snowballing | 3D_praxis_berichte | 4_qualitaets_selektion",
        "status": "ok | rauschen_hoch | daten_duenn | api_issue | friction",
        "beobachtung": "Konkrete Beschreibung der Erfahrungen, Reibungspunkte und Ausweichmanöver in dieser Phase"
      }
    ]
  },
  "findings": [
    {
      "id": "F-001",
      "titel": "string",
      "autoren": ["string"],
      "jahr": 2024,
      "quelle_plattform": "OpenAlex | Zenodo | TRID | PubMed | QDR | GESIS | Difu | UBA | ADFC | GitHub | …",
      "quelle_typ": "journal_article | dataset | preprint | municipal_report | verband_report | survey_report | market_study | ngo_report | policy_paper | guideline | whitepaper | report | software | thesis",
      "doi_url": "string",
      "open_access": true,
      "abstract_kurzfassung": "string (max. 300 Zeichen, zusammengefasst)",
      "methodik": ["qualitative_interviews", "focus_groups", "thematic_analysis", "survey", "sensor_data", "review", "stakeholder_dialogue"],
      "relevanz_begruendung": "string (1–2 Sätze warum relevant)",
      "facetten_treffer": ["A", "B", "C", "D"],
      "schluesselwoerter": ["string"],
      "zielgruppen_genannt": ["string"],
      "institutionen_genannt": ["string"],
      "laender_regionen": ["string"],
      "rohdaten_verfuegbar": false,
      "rohdaten_format": null,
      "qualitative_daten": {
        "hat_interviews": true,
        "interview_typ": "semi_structured | expert | focus_group | narrative | user_study | none",
        "stichprobengroesse": 24,
        "transkripte_verfuegbar": true,
        "interview_leitfaden_verfuegbar": true,
        "zitate_im_text": true
      },
      "daten_anhaenge": [
        {
          "typ": "interview_transkripte | interview_leitfaden | supplementary_pdf | codebook | survey_data | sensor_data | code_repository | appendix | sonstige",
          "titel_beschreibung": "Transkripte der 24 Leitfadeninterviews (Anhang S1)",
          "url": "https://doi.org/10.xxxx/supplementary-1",
          "format": "pdf | docx | csv | zip | txt | audio | html",
          "open_access": true
        }
      ]
    }
  ]
}
```

> [!CAUTION]
> ### Strenge Regeln für `daten_anhaenge` (Keine Pseudo-Anhänge oder PDF-Duplikate!):
> 1. **Niemals das Hauptdokument / Volltext-PDF duplizieren:**
>    - Das reguläre Paper, der Zeitschriftenartikel, der Konferenzbeitrag oder der Kommunalbericht gehört **ausschließlich** in `doi_url` und wird über `open_access: true` erfasst.
>    - Es ist **STRENG VERBOTEN**, die URL des Hauptartikels oder dessen Open-Access-PDF nochmals als `supplementary_pdf` in `daten_anhaenge` einzutragen. Das führt zu 100% redundanten Downloads!
> 2. **`daten_anhaenge` ist ausschließlich für separate Begleitdateien:**
>    - Nur eintragen, wenn es eine *echte, eigenständige Begleitdatei* gibt (z. B. separate ESM-Dateien wie `mmc1.pdf`, `suppl_tab1.xlsx`, Zenodo-Dateien aus `/files`, separate Transkript-Dateien auf QDR/OSF).
> 3. **Keine In-Text Anhänge als Pseudo-URLs:**
>    - Wenn ein Interviewleitfaden, Fragebogen oder Anhang einfach auf den letzten Seiten des Hauptartikels abgedruckt ist (z. B. "Appendix A" auf Seite 14 des PDFs):
>      - Setze `qualitative_daten.interview_leitfaden_verfuegbar: true` (oder `transkripte_verfuegbar: true`).
>      - Erwähne in `relevanz_begruendung` oder `abstract_kurzfassung`: *"Fragebogen im Anhang des Volltexts abgedruckt"*.
>      - Trage **KEINE** Pseudo-URL (z. B. `https://doi.org/...#appA` oder die DOI-URL selbst) in `daten_anhaenge` ein!
> 4. **Default ist LEER (`[]`):**
>    - Wenn es keine separaten, herunterladbaren Begleitdateien gibt, muss `daten_anhaenge: []` strikt ein leeres Array sein!

#### 5.2 Wie der Agent Metadaten & Anhänge extrahiert

1. **Aus API-Antworten:**
   - OpenAlex: `abstract_inverted_index`, `open_access.oa_url`, `primary_location.landing_page_url`. (Achtung: `oa_url` ist das Hauptpaper, **kein** Anhang!).
   - Zenodo: `files`-Array liefert Dateinamen, Größen und direkte Download-URLs für Datensätze und Zusatzmaterialien.
2. **Aus DOI Landing Pages (`read_url_content`):**
   - Suche nach Sektionen wie *Supplementary Materials*, *Electronic Supplementary Material (ESM)*, *Supporting Information*.
   - Extrahiere **nur Links zu echten, separaten Begleitdateien** (z. B. `mmc1.pdf`, `.xlsx`, `.zip`) in `daten_anhaenge`.
   - Ignoriere Links, die lediglich das Haupt-PDF oder den Artikel selbst darstellen.
3. **Aus Abstract / Volltext-Hinweisen:**
   - Prüfe, ob Stichprobengröße (z. B. "N=18 interviews", "4 focus groups with 32 participants") genannt wird und trage sie in `qualitative_daten.stichprobengroesse` ein.
   - Prüfe, ob qualitative Zitate/O-Töne in der Studie vorhanden sind (`zitate_im_text: true`).
   - Wenn der Leitfaden im Text abgedruckt ist: `qualitative_daten.interview_leitfaden_verfuegbar: true`, aber `daten_anhaenge: []`!

Mehr Details: `references/datenformate_agent.md`

---

## Output-Format

**Zwei Dateien** im Arbeitsverzeichnis:

### 1. `suchprotokoll_<thema>.md` — Menschenlesbare Dokumentation
Enthält den vollständigen Recherchebericht:
- 0. Themen-Analyse & Plattform-Mapping (inkl. qualitativer Repositorien & Grey Lit)
- 1. Suchstrategie (Strukturierte Facetten-Liste & Kombinationslogik)
- 2. Suchbegriff-Thesaurus (inkl. qualitativer Interviewbegriffe)
- 3. Datenbank-spezifische Queries & Snowballing-Pfade
- 4. Qualitäts- und Selektionskriterien
- 5. Zusammenfassung der Fundstellen (Übersichtstabelle inkl. Kennzeichnung von Interviews & Datenanhängen)
- 6. Recherche-Log & Transparenzbericht (Zusammenfassung der Phasen-Logs, Reibungsverluste, Rauschen, Limitationen)
- 7. Nächste Schritte (Übergabe an `stakeholder_analyse` und `daten_download`)

### 2. `findings_<thema>.json` — Maschinenlesbare Daten für Folge-Skills
Vollständig befülltes JSON gemäß Schema 5.1 mit **allen gefundenen Quellen**, `recherche_diagnose` und vollständigem `phasen_log`.

---

## Qualitätssicherung (Checkliste)

- [ ] Recherche erschöpfend durchgeführt (mind. 30+ Einträge bzw. alle auffindbaren relevanten Quellen)
- [ ] Mindestens 3 Facetten in jeder Basis-Query kombiniert
- [ ] Phase 3B Qualitative Deep-Dive ausgeführt: Gezielt nach qualitativen Interviews, Fokusgruppen und Transkripten gesucht
- [ ] Phase 3C Snowballing auf Seed-Studien angewendet
- [ ] Phase 3D Praxis- und NGO-Quellen eingebunden
- [ ] Inkrementelles Phasen-Log (`meta.phasen_log`) für alle Phasen lückenlos befüllt
- [ ] `meta.recherche_diagnose` (Roh-Treffer, Rauschquote, Sättigungsgrund) vollständig ausgefüllt
- [ ] `daten_anhaenge` enthält AUSSCHLIESSLICH separate Begleitdateien (keine Duplikate der Haupt-PDF/DOI, kein '#appA' auf Hauptseiten). Wenn keine separaten Begleitdateien existieren: `daten_anhaenge: []`
- [ ] Im Haupttext abgedruckte Anhänge (z. B. Fragenkatalog am Textende) sind in `qualitative_daten` (`interview_leitfaden_verfuegbar: true`) dokumentiert, NICHT in `daten_anhaenge`
- [ ] `qualitative_daten` (Interview-Typ, Stichprobengröße, O-Töne) für jeden Eintrag gepflegt
- [ ] findings.json ist valides JSON und enthält alle Pflichtfelder
- [ ] `suchprotokoll_<thema>.md` im Arbeitsverzeichnis gespeichert

---

## Referenzen

- Beispiel-Suchprotokoll: `references/suchprotokoll_beispiel.md`
- API-Endpoints aller Plattformen: `references/api_endpoints.md`
- Datenformate & Agent-Lesestrategie: `references/datenformate_agent.md`


