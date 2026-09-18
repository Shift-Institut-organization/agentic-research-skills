# findings.json – Vollständiges Schema & Feldbeschreibung

Diese Datei wird vom `suchprotokoll_recherche`-Skill erzeugt und ist der
primäre Input für den `stakeholder_analyse`- sowie den `daten_download`-Skill.

---

## Toplevel-Struktur

```json
{
  "meta": { ... },
  "findings": [ ... ]
}
```

---

## `meta` Objekt

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `thema` | string | Name des Themas/Projekts (z. B. "Urban Cycling Infrastructure") |
| `erstellungsdatum` | string | ISO-8601 Datum/Zeit |
| `suchprotokoll_version` | string | Version des Suchprotokolls (z. B. `"2.0"`) |
| `quellen_count` | number | Anzahl Einträge in `findings` |
| `recherche_diagnose` | object | Kennzahlen: `treffer_roh_gesichtet`, `gefiltert_irrelevant`, `validiert_gespeichert`, `saettigungsgrund` |
| `phasen_log` | object[] | Inkrementelle Protokolleinträge pro Phase (`phase`, `status`, `beobachtung`) |

---

## `findings` Array – Pro Eintrag

### Pflichtfelder (müssen immer befüllt sein)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | string | Eindeutige ID, z. B. `"F-001"` |
| `titel` | string | Vollständiger Titel der Quelle |
| `autoren` | string[] | Liste der Autor*innen |
| `jahr` | number | Erscheinungsjahr |
| `quelle_plattform` | string | Woher? z. B. `"OpenAlex"`, `"Zenodo"`, `"QDR"`, `"GESIS"`, `"PubMed"` |
| `quelle_typ` | string | Typ der Quelle (siehe unten) |
| `doi_url` | string | DOI oder direkte URL zur Quelle |
| `abstract_kurzfassung` | string | Max. 300 Zeichen, vom Agent extrahiert |
| `relevanz_begruendung` | string | 1–2 Sätze: warum für das Thema relevant? |

### Optionale Felder & Fachmetadaten

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `open_access` | boolean | Ist die Quelle frei zugänglich? |
| `methodik` | string[] | Verwendete Methoden (Enum, siehe unten) |
| `facetten_treffer` | string[] | Welche Facetten wurden getroffen? z. B. `["A","B","C","D"]` |
| `schluesselwoerter` | string[] | Keywords der Quelle |
| `zielgruppen_genannt` | string[] | ⭐ Wichtig für Stakeholder-Analyse! |
| `institutionen_genannt` | string[] | ⭐ Wichtig für Stakeholder-Analyse! |
| `laender_regionen` | string[] | Geographischer Kontext |
| `rohdaten_verfuegbar` | boolean | Gibt es einen zugehörigen Datensatz oder Anhang? |
| `rohdaten_format` | string\|null | Format wenn ja: `"csv"`, `"json"`, `"zip"`, `"pdf_appendix"` |

### Qualitative Daten (`qualitative_daten`)
*Strukturiert qualitative Erhebungsmerkmale für Persona- und Stakeholder-Extraktion:*

| Unterfeld | Typ | Beschreibung |
|-----------|-----|-------------|
| `hat_interviews` | boolean | Wurden qualitative Interviews/Fokusgruppen geführt? |
| `interview_typ` | string | `semi_structured`, `expert`, `focus_group`, `narrative`, `user_study`, `none` |
| `stichprobengroesse` | number\|null | Anzahl befragter Personen / Teilnehmer (z. B. 24) |
| `transkripte_verfuegbar`| boolean | Liegen anonymisierte Transkripte als Datei/Anhang vor? |
| `interview_leitfaden_verfuegbar` | boolean | Liegt der Interviewleitfaden vor? |
| `zitate_im_text` | boolean | Enthält der Text/Abstract direkte O-Töne der Befragten? |

### Datenanhänge & Begleitmaterialien (`daten_anhaenge`)
*Array aller herunterladbaren Begleitdateien (für `daten_download`-Skill):*

```json
[
  {
    "typ": "interview_transkripte | interview_leitfaden | supplementary_pdf | codebook | survey_data | sensor_data | code_repository | appendix | sonstige",
    "titel_beschreibung": "string",
    "url": "string (direkter Download- oder Web-Link)",
    "format": "pdf | docx | csv | zip | txt | audio | html",
    "open_access": true
  }
]
```

---

## Enum-Werte

### `quelle_typ`
```
"journal_article"    — Peer-reviewed Zeitschriftenartikel
"conference_paper"   — Konferenzbeitrag
"preprint"           — Preprint (arXiv, Zenodo, SSRN)
"dataset"            — Rohdatensatz / Transkriptsammlung (Zenodo, QDR, Dataverse)
"municipal_report"   — Kommunalbericht / Städtisches Konzept (z. B. Difu, Stadt Münster)
"ngo_report"         — Verbandsbericht / Zivilgesellschaft (z. B. ADFC, VCD)
"policy_paper"       — Strategie- / Positionspapier (z. B. Agora Verkehrswende)
"guideline"          — Richtlinie / Technischer Leitfaden (z. B. FGSV, ERA)
"whitepaper"         — Think-Tank / Industry Whitepaper
"report"             — Allgemeiner technischer oder wissenschaftlicher Bericht
"thesis"             — Dissertation, Masterarbeit
"software"           — Code-Repository, Tool
"book_chapter"       — Buchkapitel
```

### `methodik`
```
"qualitative_interviews"   — Einzel-/Leitfadeninterviews
"focus_groups"             — Fokusgruppen / Gruppendiskussionen
"thematic_analysis"        — Qualitative Inhalts- / Themenanalyse
"survey"                   — Fragebogen, Online-Umfrage
"ethnography"              — Feldbeobachtung, Ethnographie
"case_study"               — Fallstudie
"systematic_review"        — Systematischer Review
"meta_analysis"            — Meta-Analyse
"sensor_data"              — Quantitative Sensormessungen
"gis_analysis"             — Räumliche Analyse
"experiment"               — Labor-/Feldexperiment
"mixed_methods"            — Kombination aus qualitativen und quantitativen Methoden
```

---

## Beispiel-Eintrag (vollständig)

```json
{
  "id": "F-001",
  "titel": "Bicyclist's perceived level of comfort in dense urban environments: A qualitative and empirical investigation",
  "autoren": ["Masoud Ghodrat Abadi", "David Hurwitz"],
  "jahr": 2018,
  "quelle_plattform": "OpenAlex",
  "quelle_typ": "journal_article",
  "doi_url": "https://doi.org/10.1016/j.scs.2018.04.003",
  "open_access": true,
  "abstract_kurzfassung": "Verknüpft objektive Straßenmerkmale mit subjektiv wahrgenommenem Fahrkomfort von Radfahrenden. N=24 semi-strukturierte Vor-Ort-Interviews identifizieren Kopfsteinpflaster und Kanten als Hauptursachen für subjektives Unbehagen.",
  "methodik": ["qualitative_interviews", "thematic_analysis", "sensor_data"],
  "relevanz_begruendung": "Liefert qualitative O-Töne und Erschütterungsbewertungen für die Persona-Entwicklung vulnerabler Radnutzer.",
  "facetten_treffer": ["A", "B", "C", "D"],
  "schluesselwoerter": ["cycling comfort", "qualitative interviews", "urban infrastructure"],
  "zielgruppen_genannt": ["Radfahrende", "Ältere Menschen", "Verkehrsplaner"],
  "institutionen_genannt": ["Oregon State University"],
  "laender_regionen": ["USA", "Oregon"],
  "rohdaten_verfuegbar": true,
  "rohdaten_format": "pdf_appendix",
  "qualitative_daten": {
    "hat_interviews": true,
    "interview_typ": "semi_structured",
    "stichprobengroesse": 24,
    "transkripte_verfuegbar": true,
    "interview_leitfaden_verfuegbar": true,
    "zitate_im_text": true
  },
  "daten_anhaenge": [
    {
      "typ": "interview_leitfaden",
      "titel_beschreibung": "Appendix A: Semi-structured interview protocol and route evaluation form",
      "url": "https://doi.org/10.1016/j.scs.2018.04.003#appA",
      "format": "pdf",
      "open_access": true
    },
    {
      "typ": "interview_transkripte",
      "titel_beschreibung": "Supplementary Material: Anonymized interview excerpts and category codes",
      "url": "https://doi.org/10.1016/j.scs.2018.04.003/mmc1.pdf",
      "format": "pdf",
      "open_access": true
    }
  ]
}
```

---

## Hinweise für Folge-Skills

### Für den `stakeholder_analyse`-Skill:
1. **`zielgruppen_genannt` & `institutionen_genannt`**: Direkte Akteure und Organisationen.
2. **`qualitative_daten`**: Wenn `hat_interviews: true` und `zitate_im_text: true`, lassen sich direkt repräsentative Originalaussagen (Pain Points, Wünsche) in die Stakeholder-Matrix und Persona-Zitate übernehmen.
3. **`qualitative_daten.stichprobengroesse`**: Zeigt empirische Belastbarkeit der Stakeholder-Gruppe.

### Für den `daten_download`-Skill:
1. Der Download-Skill liest **`daten_anhaenge`** und lädt Transkripte, Leitfäden und Datensätze gezielt in entsprechende Unterordner (`transcripts/`, `datasets/`, `pdfs/`).

