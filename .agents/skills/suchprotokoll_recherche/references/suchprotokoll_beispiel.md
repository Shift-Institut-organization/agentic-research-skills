# Suchprotokoll & Query-Leitfaden: Referenz-Beispiel (The Bicycle Example)

Dieses Dokument zeigt am durchgängigen Referenzbeispiel (Urbane Radverkehrsinfrastruktur & Sensorgestütztes Komfort-Mapping), wie die 4-Facetten-Methodik systematisch und erschöpfend angewendet wird:
- **Thema:** Urbane Radverkehrsinfrastruktur: Wahrgenommene Sicherheit, Erschütterungs-Mapping und Routenwahl
- **Fokus:** Mixed-Methods-Kombination aus qualitativen Pendler-Interviews und quantitativen Fahrbahn-Sensordaten

---

## 0. Strukturierung der 4 Facetten im Referenzbeispiel

| Dimension | Facetten-Ausprägung im Radverkehrs-Projekt |
|---|---|
| **Facette A (Entität / Phänomen)** | `cycling network`, `bicycle infrastructure`, `velomobility`, `active travel`, `Radnetz` |
| **Facette B (Mechanismus / Handlungsfeld)** | `perceived safety`, `stress factors`, `vibration comfort`, `surface roughness`, `separation quality` |
| **Facette C (Zielgruppe / Akteure)** | `bicycle commuters`, `vulnerable road users`, `cargo bike users`, `elderly cyclists` |
| **Facette D (Empirischer Filter)** | `semi-structured interview*`, `focus group*`, `ride-along`, `thematic analysis`, `O-Töne` |

---

## 1. Ausführliches Referenzbeispiel: Urbane Radinfrastruktur & Erschütterungs-Mapping

Empirische Studien und Datenanhänge zu sensorbasiertem Erschütterungs-Mapping und barrierefreiem Radverkehr:

### 1.1 Suchstrategie und Konzept-Strukturierung (Faceted Search)
- **Facette A – Hauptthema:** Radverkehr, Aktive Mobilität, Radinfrastruktur (`cycling`, `bicycle`, `active travel`, `velomobility`)
- **Facette B – Methode & Sensorik:** Erschütterungsmessung, Crowdsensing, GIS (`sensor*`, `vibration`, `crowdsensing`, `GIS`)
- **Facette C – Zielgruppen & Inklusion:** Vulnerable Gruppen, Senioren, Lastenräder, Barrierefreiheit (`accessibility`, `elderly`, `cargo bike`, `wheelchair`)
- **Facette D – Methodischer Filter:** Qualitative Erhebungen & Interviews (`interview*`, `"semi-structured"`, `"focus group*"`, `"thematic analysis"`)

**Kombinationslogik:**
- Vollabfrage (höchste Präzision): `(Facette A) AND (Facette B) AND (Facette C) AND (Facette D)`
- Relaxation (Nutzerfokus): `(Facette A) AND (Facette C) AND (Facette D)`
- Relaxation (Technikfokus): `(Facette A) AND (Facette B) AND (Facette D)`

---

## 2. Strukturierte Suchbegriffe (Thesaurus)

| Konzept A: Radverkehr / Mobilität | Konzept B: Digitale Sensorik & Erschütterung | Konzept C: Inklusion, Barrieren & Nutzertypen | Konzept D: Qualitativ & Empirisch (Interviews & Transkripte) |
| :--- | :--- | :--- | :--- |
| `cycling` | `crowdsensing` / `crowdsourced` | `accessibility` / `barrier-free` | `interview*` / `"semi-structured"` |
| `bicycle` / `biking` | `sensor*` (accelerometer, gyroscope) | `elderly` / `older adults` / `senior*` | `"focus group*"` / `fokusgruppe*` |
| `active mobility` / `active travel` | `vibration` / `roughness` / `shock` | `cargo bike*` / `cargobike*` | `"in-depth interview*"` / `leitfaden` |
| `cycling infrastructure` | `pavement condition` / `surface` | `wheelchair*` / `handbike*` | `"thematic analysis"` / `transkript*` |
| `velomobility` | `GIS` / `spatial analysis` | `vulnerable road users` / `VRU` | `experteninterview*` / `"user study"` |

---

## 3. Datenbank-spezifische Such-Queries (Search Strings)

### 3.1. Query für OpenAlex (Breite Suche mit Paginierung)
```text
https://api.openalex.org/works?search=(cycling+OR+bicycle)+AND+(vibration+OR+comfort+OR+pavement)+AND+(accessibility+OR+barrier)+AND+(interview+OR+qualitative)&filter=open_access.is_oa:true&per-page=50&page=1
```

### 3.2. Query für Zenodo (Datensätze & Preprints)
```text
(cycling OR bicycle) AND (comfort OR vibration OR accessibility) AND (interview OR qualitative OR survey)
```

### 3.3. Query für QDR / Harvard Dataverse (Qualitative Transkripte & Rohdaten)
```text
https://dataverse.qdr.syr.edu/api/search?q=cycling+AND+(interview+OR+transcript)&type=dataset&per_page=25
```

### 3.4. Query für IEEE Xplore (Technik & Usability)
```sql
("Document Title":cycling OR "Document Title":bicycle) 
AND ("Abstract":sensor* OR "Abstract":crowdsens* OR "Abstract":vibration) 
AND ("Abstract":interview* OR "Abstract":qualitative OR "Abstract":survey OR "Abstract":usability)
```

---

## 4. Qualitäts- und Selektionskriterien

### Einschlusskriterien
1. **Methodik:** Sowohl qualitative Erhebungen (semi-strukturierte Interviews, Fokusgruppen, "Think-Aloud"-Fahrten) als auch quantitative Sensorstudien.
2. **Daten-Artefakte & Begleitmaterialien:** Studien mit zugänglichen Interviewleitfäden, anonymisierten Transkripten, Codebooks oder Rohdaten-Dumps.
3. **Inhaltlicher Fokus:** Einfluss von Fahrbahnbeschaffenheit auf das Fahrverhalten und Komfort vulnerabler Gruppen.
4. **Vollständigkeit:** Zugängliche Metadaten/Abstracts, Open-Access bevorzugt.

### Ausschlusskriterien
1. Reine Simulationen ohne Probanden oder reale Messfahrten.
2. Ausschließlich Kraftfahrzeugverkehr (MIV / PKW).
3. Fehlende Validität / kommerzielle Werbebroschüren.

---

## 5. Beispiel-Auszug `findings_urban_cycling.json`

```json
{
  "meta": {
    "thema": "Urban Cycling Infrastructure: Vibration Mapping & Perceived Safety",
    "erstellungsdatum": "2026-08-26T11:00:00Z",
    "suchprotokoll_version": "2.0",
    "quellen_count": 42,
    "recherche_diagnose": {
      "treffer_roh_gesichtet": 165,
      "gefiltert_irrelevant": 123,
      "validiert_gespeichert": 42,
      "saettigungsgrund": "Sättigung erreicht: Nach Paginierung bis Seite 4 und Vorwärts-Zitationssuche keine neuen relevanten Treffer mehr."
    },
    "phasen_log": [
      {
        "phase": "0_themen_mapping",
        "status": "ok",
        "beobachtung": "Plattformen OpenAlex, Zenodo, QDR und ADFC-Fachportal als primäre Quellen ausgewählt."
      },
      {
        "phase": "1_2_facetten_thesaurus",
        "status": "ok",
        "beobachtung": "4 Kernfacetten mit 24 Begriffen (inkl. Leitfadeninterview & Vibrationssensorik) definiert."
      },
      {
        "phase": "3A_breite_suche",
        "status": "rauschen_hoch",
        "beobachtung": "OpenAlex lieferte 110 Treffer, ca. 60 % befassten sich mit PKW-Fahrbahnen; Rauschfilter auf 'cycling/bicycle' verschärft."
      },
      {
        "phase": "3B_qualitativer_boost",
        "status": "ok",
        "beobachtung": "QDR und Zenodo brachten 6 relevante Interview-Datensätze und Leitfäden zu barrierefreier Mobilität."
      },
      {
        "phase": "3C_citation_snowballing",
        "status": "sehr_erfolgreich",
        "beobachtung": "Seed-Studie F-001 lieferte über Vorwärts-Zitationen 9 neuere Studien aus 2021–2024."
      },
      {
        "phase": "3D_praxis_berichte",
        "status": "ok",
        "beobachtung": "ADFC-Fahrradklima-Test und Difu-Kommunalstudie erfolgreich als Praxisquellen eingebunden."
      },
      {
        "phase": "4_qualitaets_selektion",
        "status": "ok",
        "beobachtung": "42 Quellen erfüllten alle Qualitätskriterien und wurden strukturiert mit Datenanhängen gespeichert."
      }
    ]
  },
  "findings": [
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
          "typ": "interview_transkripte",
          "titel_beschreibung": "Electronic Supplementary Material (ESM 1): Anonymized interview excerpts and category codes",
          "url": "https://ars.els-cdn.com/content/image/1-s2.0-S221067071830421X-mmc1.pdf",
          "format": "pdf",
          "open_access": true
        }
      ]
    }
  ]
}
```

---

## 6. Recherche-Log & Transparenzbericht

### 6.1 Aufgetretene Reibungspunkte & Rauschen
- **Rauschen in Phase 3A:** Breites Schlagwort "vibration" führte zu starkem Rauschen mit PKW- und Gleisbau-Papern; Einengung auf `cycling/bicycle` löste das Problem.
- **Datenverfügbarkeit in Phase 3B:** Standalone-Transkripte speziell zu Lastenrädern sind international kaum öffentlich archiviert; Fokusgruppen-Transkripte zu Senior*innen und Barrierefreiheit waren hingegen auf Zenodo gut verfügbar.

### 6.2 Erfolgreiche Ausweichstrategien & Hebel
- **Snowballing:** Das Vorwärts-Snowballing ausgehend von Studie F-001 brachte den höchsten Zuwachs an aktuellen empirischen Studien (9 Volltreffer).
- **Praxisquellen:** Der ADFC-Fahrradklima-Test lieferte die notwendige deutschlandspezifische Nutzerperspektive.

### 6.3 Limitationen & Sättigung
- Sättigung nach 4 Paginierungsseiten und Abschluss der Zitationsanalyse erreicht. Gesamtfundus: 42 validierte Quellen.



