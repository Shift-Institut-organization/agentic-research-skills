# Datenformate & Agent-Lesestrategie

Dieses Dokument erklärt, **wie ein LLM-Agent** mit verschiedenen Datenformaten aus Wissenschaftsrepositorien umgeht, warum PDFs/CSVs problematisch sind und wie **qualitative Daten und Datenanhänge** effizient und strukturiert extrahiert werden.

---

## Das Kernproblem: Warum PDFs und CSVs schwierig sind

### PDFs
```
Problem:  PDFs sind für Menschen gemacht, nicht für Maschinen.
          Binärformat → Agent kann es nicht direkt lesen.
          Kein read_file() auf .pdf möglich.
          
Ausnahme: Wenn ein Tool (browser_subagent) die PDF-Seite im Browser öffnet
          und den sichtbaren Text extrahiert – aber das ist langsam und fehleranfällig.
          
Lösung:   NIEMALS auf die Haupt-PDF selbst verlassen. Stattdessen:
          1. Abstract aus API-Metadaten nehmen (immer vorhanden bei OpenAlex, PubMed)
          2. HTML-Landing-Page der DOI lesen (read_url_content auf doi.org/...)
          3. Semantic Scholar hat oft strukturierte Volltexte ohne PDF
          4. Begleitmaterialien (Supplementary PDFs / Leitfäden) gezielt verlinken
```

### CSVs & Datensätze
```
Problem:  CSVs können sehr groß sein (>100MB bei Sensordaten).
          Ohne Kontext sind Spaltennamen oft kryptisch.
          Ein Agent der eine 50.000-Zeilen CSV liest = Kontext-Overflow.
          
Lösung:   1. README / Codebook des Datensatzes lesen (fast immer vorhanden)
          2. Nur Metadaten aus Repositorium-API lesen (Beschreibung, Variablenliste)
          3. Bei Zenodo: /files-Endpoint liefert Dateiliste und direkte URLs
          4. view_file mit StartLine/EndLine = nur erste 20 Zeilen lesen (Header + Beispiel)
```

---

## Extraktion von Datenanhängen (`daten_anhaenge`)

Oft enthalten Studien wertvolle Primärdaten (Interview-Transkripte, Leitfäden, Zusatz-Tabellen) als **echte, eigenständige Begleitdateien** (Supplementary Material) oder in verknüpften Repositorien.

> [!WARNING]
> ### Wichtigste Unterscheidung: Hauptdokument vs. In-Text Anhang vs. Standalone Begleitdatei
> 
> | Kategorie | Was ist das? | Wohin gehört es in `findings.json`? |
> |-----------|--------------|--------------------------------------|
> | **Hauptpublikation** | Der reguläre Journal-Artikel, Konferenzbeitrag, Report oder die Dissertation als PDF/HTML. | `doi_url` (bzw. `open_access: true`). **NIEMALS** in `daten_anhaenge` eintragen! |
> | **In-Text Anhang** | Ein Fragenkatalog oder Leitfaden, der am Ende des Haupt-PDFs abgedruckt ist (z. B. "Appendix A, S. 12–15"). | In `qualitative_daten`: `"interview_leitfaden_verfuegbar": true`. **`daten_anhaenge: []` bleibt LEER!** Keine Pseudo-URLs mit `#appA` erfinden. |
> | **Standalone Begleitdatei** | Eine separate, eigenständige Datei zum Download (z. B. `mmc1.pdf`, `survey_raw.csv`, Zenodo-Files). | In `daten_anhaenge` mit direktem Download-Link und Typ aufnehmen. |

### Anti-Pattern vs. Best Practice

❌ **ANTI-PATTERNS (Verboten!):**
```json
// FEHLER 1: Das Hauptpaper selbst als "Anhang" eintragen (erzeugt 100% Download-Duplikate!)
"daten_anhaenge": [
  {
    "typ": "supplementary_pdf",
    "titel_beschreibung": "Open Access Publikations-PDF: Towards a More Comprehensive Picture...",
    "url": "https://sciencedirect.com/.../main_article.pdf",
    "format": "pdf",
    "open_access": true
  }
]

// FEHLER 2: DOI mit Anchor für im Paper abgedruckte Anhänge als Pseudo-URL missbrauchen
"daten_anhaenge": [
  {
    "typ": "interview_leitfaden",
    "titel_beschreibung": "Appendix A: Semi-structured interview protocol",
    "url": "https://doi.org/10.1016/j.scs.2018.04.003#appA",
    "format": "pdf",
    "open_access": true
  }
]
```

✅ **BEST PRACTICES (Korrekt):**

**Fall A: Reines Paper ohne externe Begleitdateien (auch wenn es einen Anhang im Text hat):**
```json
{
  "id": "F-001",
  "titel": "Perceived safety and stress factors among urban bicycle commuters: A mixed-methods ride-along study",
  "doi_url": "https://doi.org/10.1016/j.trf.2023.05.012",
  "open_access": true,
  "qualitative_daten": {
    "hat_interviews": true,
    "interview_typ": "semi_structured",
    "interview_leitfaden_verfuegbar": true,
    "zitate_im_text": true
  },
  "daten_anhaenge": []   // <--- STRIKT LEER!
}
```

**Fall B: Echtes separates Supplementary Material / Repositorium-Dateien:**
```json
{
  "id": "F-002",
  "titel": "Urban Bicycle Surface Roughness and Cyclist Vibration Acceleration Dataset",
  "doi_url": "https://doi.org/10.5281/zenodo.10823456",
  "open_access": true,
  "daten_anhaenge": [
    {
      "typ": "sensor_data",
      "titel_beschreibung": "surface_roughness_3axis_accelerometer.csv",
      "url": "https://zenodo.org/api/records/10823456/files/surface_roughness_3axis_accelerometer.csv/content",
      "format": "csv",
      "open_access": true
    },
    {
      "typ": "interview_transkripte",
      "titel_beschreibung": "Electronic Supplementary Material (ESM): Anonymized ride-along interview transcripts",
      "url": "https://static-content.springer.com/esm/art%3A10.../MediaObjects/..._ESM1.pdf",
      "format": "pdf",
      "open_access": true
    }
  ]
}
```

### 1. Aus Zenodo / Dataverse API
```json
GET https://zenodo.org/api/records/<ID>/files
```
Die Antwort enthält ein Array von echten Zusatzdateien. Der Agent mappt jede Datei:
```json
{
  "typ": "interview_transkripte | codebook | survey_data | sensor_data",
  "titel_beschreibung": file["key"],
  "url": file["links"]["content"],
  "format": "csv | pdf | zip | txt",
  "open_access": true
}
```

### 2. Aus DOI Landing Pages (via `read_url_content`)
Auf den HTML-Seiten von Verlagen (Elsevier, Springer, Wiley, Nature, PLOS):
- Suche nach Abschnitten wie **"Supplementary material"**, **"Electronic supplementary material (ESM)"** oder **"Supporting information"**.
- Prüfe, ob es sich um **eigenständige Download-Links** handelt (z. B. auf Elsevier `mmc1.pdf`, Springer `_ESM.pdf`, Wiley `.docx` oder `.zip`).
- Nur solche eigenständigen Links gehören in `daten_anhaenge`.
- Fehlen solche Links, ist `daten_anhaenge: []` leer!

---

## Extraktion qualitativer Metadaten (`qualitative_daten`)

Der Agent prüft Abstract, Titel und Landing-Page-Text auf folgende Merkmale:

1. **`hat_interviews` (boolean):** Wurden Einzelinterviews, Experteninterviews oder Fokusgruppen durchgeführt?
2. **`interview_typ` (string):**
   - `"semi_structured"` (Leitfadeninterviews, semistrukturierte Befragungen)
   - `"expert"` (Experteninterviews mit Stakeholdern / Fachleuten)
   - `"focus_group"` (Gruppendiskussionen, Fokusgruppen)
   - `"narrative"` (Biografische / narrative Interviews)
   - `"user_study"` (Usability-Interviews, Think-Aloud-Protokolle)
   - `"none"` (Keine Interviews)
3. **`stichprobengroesse` (number | null):** Anzahl der befragten Personen / Interviewpartner (z. B. aus "N=23", "23 semistrukturierte Interviews", "4 Fokusgruppen mit je 6 Teilnehmern" → 24).
4. **`transkripte_verfuegbar` (boolean):** Liegen Transkripte als Anhang oder in einem Repositorium vor?
5. **`interview_leitfaden_verfuegbar` (boolean):** Ist der Fragenkatalog / Leitfaden einsehbar?
6. **`zitate_im_text` (boolean):** Werden wörtliche Zitate (O-Töne) im Text/Abstract erwähnt bzw. dargestellt?

---

## Strategie pro Plattform

### OpenAlex (Beste Quelle für bibliografische Metadaten)

API liefert **strukturiertes JSON**:
```json
{
  "title": "...",
  "abstract_inverted_index": { ... },
  "authorships": [{"author": {"display_name": "..."}, "institutions": [...]}],
  "open_access": {"is_oa": true, "oa_url": "..."},
  "concepts": [{"display_name": "accessibility", "score": 0.87}],
  "keywords": [...],
  "publication_year": 2023
}
```

**Abstract rekonstruieren** aus `abstract_inverted_index`:
```python
words = [""] * (max_position + 1)
for word, positions in inverted.items():
    for pos in positions:
        words[pos] = word
abstract = " ".join(words)
```

---

### Zenodo (Preprints, Datensätze & Transkripte)

- API-Metadaten (`GET /api/records/<ID>`) liefern `description` und `resource_type`.
- API-Files (`GET /api/records/<ID>/files`) liefert alle Dateianhänge für `daten_anhaenge`.

---

### QDR & Harvard Dataverse (Qualitative Datensätze & Codebooks)

- Suche liefert Dataset-Persistent-IDs (DOIs).
- Dateiliste über `/api/datasets/:persistentId/versions/:latest/files` abrufen.
- Codebooks, Leitfäden und Transkript-Dateien direkt als Einträge in `daten_anhaenge` aufnehmen.

---

## Das "Goldene Prinzip" für Agenten

```
┌─────────────────────────────────────────────────────────┐
│                LESEREIHENFOLGE FÜR AGENTEN              │
│                                                         │
│  1. API-Metadaten (JSON)          ← immer zuerst        │
│     title, abstract, authors,                           │
│     keywords, institutions, files-List                  │
│                                                         │
│  2. Landing Page (HTML)           ← für Anhänge/O-Töne  │
│     read_url_content(doi_url)                           │
│     → Dublin Core, OpenGraph Meta-Tags                  │
│     → Supplementary Materials Links                     │
│     → Abstract & Methodik-Abschnitt                     │
│                                                         │
│  3. README / Codebook (Text/MD)   ← für Datensätze      │
│     raw GitHub URL oder Repositorium-Dateiliste         │
│                                                         │
│  4. Erste Zeilen (CSV)            ← nur bei Bedarf      │
│     view_file(StartLine=1, EndLine=20)                  │
│     → Header + 5 Beispielzeilen                         │
│                                                         │
│  ❌ NIEMALS: Ganze PDFs unstrukturiert einlesen         │
│  ❌ NIEMALS: Große Datensätze komplett laden           │
└─────────────────────────────────────────────────────────┘
```

---

## Warum findings.json mit Anhängen die Lösung ist

Der `suchprotokoll_recherche`-Skill extrahiert Metadaten, qualitative Dimensionen und Links zu allen Anhängen direkt in die strukturierte `findings.json`.

```
suchprotokoll_recherche
        │
        ├─ Extrahiert: Metadaten, Zitate, Interview-Details, Anhänge-URLs
        │
        ▼
 findings_<thema>.json
        │
        ├────────────────────────────────┐
        ▼                                ▼
stakeholder_analyse               daten_download
- Liest Zitate & Interviews      - Lädt PDFs UND Anhänge
- Baut fundierte Personas        - Speichert Transkripte &
- Erkennt echte O-Töne             Datensätze strukturiert
```

