# findings_&lt;thema&gt;.json: Schema und Extraktionsregeln

Übergabeformat an die Folge-Skills (`stakeholder-analyse`, `daten-download`). Schema-Version 3.1.
Diese Datei ist die einzige maßgebliche Schemabeschreibung für alle Skills.

Zwei Skills schreiben in dieselbe Datei:

| Teil | Befüllt von |
|---|---|
| `meta` ohne die Rechtefelder, alle Felder je Eintrag außer `lizenz` und `datenschutz`, `pruefhinweise` | `topic-research` |
| `meta.projektpraemissen`, `meta.lizenz_geprueft`, `meta.dsgvo_geprueft`, `meta.aussortiert`, `meta.review_queue`, Blöcke `lizenz` und `datenschutz` je Eintrag und je Anhang | `source-compliance-check` |

## 1. Vollständiges Schema

```json
{
  "meta": {
    "thema": "string",
    "erstellungsdatum": "ISO-8601",
    "suchprotokoll_version": "3.1",
    "quellen_count": 0,
    "nutzungsarten": {
      "N1": "Volltext in RAG- oder Vektordatenbank einbetten",
      "N2": "Passagen oder Volltext an Nutzende ausliefern",
      "N3": "Datenanhänge weiterverwenden"
    },
    "projektpraemissen": {
      "rechtstraeger_status": "Forschungsorganisation i.S.d. § 60d UrhG",
      "nutzung_kommerziell": false,
      "quelle_der_einordnung": "Angabe des Projekts, 2026-10-20",
      "juristisch_geprueft": false
    },
    "lizenz_geprueft": "YYYY-MM-DD oder null",
    "dsgvo_geprueft": "YYYY-MM-DD oder null",
    "recherche_diagnose": {
      "treffer_roh_gesichtet": 180,
      "gefiltert_irrelevant": 135,
      "validiert_gespeichert": 45,
      "aussortiert_lizenz": 4,
      "review_queue_count": 11,
      "saettigungsgrund": "Keine neuen qualifizierten Treffer nach Paginierung bis Seite 4 und Zitationssuche"
    },
    "phasen_log": [
      {
        "phase": "0_themen_mapping | 1_2_facetten_thesaurus | 3A_breite_suche | 3B_qualitativer_boost | 3C_citation_snowballing | 3D_praxis_berichte | 4_qualitaets_selektion | 5_findings | 6_lizenzpruefung | 7_dsgvo_pruefung",
        "status": "ok | rauschen_hoch | daten_duenn | api_issue | friction | viele_zweifel | quellen_unerreichbar | nicht_einsehbar",
        "beobachtung": "Konkrete Beschreibung der Reibungspunkte und Ausweichmanöver"
      }
    ],
    "limitationen": ["Rechtsstand der Prüfdateien", "nicht erreichbare Quellen", "offene Rechtsfragen"],
    "aussortiert": [
      {
        "titel": "string",
        "doi_url": "string",
        "typ": "lizenz | datenschutz",
        "grund": "gesperrt für N1, N2 und N3: Rechtevorbehalt und kein rechtmäßiger Zugang",
        "nutzungsart": ["N1", "N2", "N3"],
        "_hinweis": "typ lizenz nur, wenn ALLE Nutzungsarten gesperrt sind; typ datenschutz bei jedem Personenbezug",
        "aussortiert_am": "YYYY-MM-DD"
      }
    ],
    "review_queue": [
      {
        "finding_id": "F-012",
        "typ": "lizenz | datenschutz",
        "dringlichkeit": "eskalation | hoch | normal",
        "frage": "Lizenzvermerk am Dokument widerspricht den DOI-Metadaten; Anfrage beim Herausgeber nötig",
        "entscheidung_noetig_von": "Rechtsprüfung SHIFT"
      }
    ]
  },
  "findings": [
    {
      "id": "F-001",
      "titel": "string",
      "autoren": ["string"],
      "jahr": 2024,
      "quelle_plattform": "OpenAlex | Zenodo | SSRN | TRID | QDR | GESIS | Difu | UBA | ADFC | GitHub | …",
      "quelle_typ": "journal_article | dataset | preprint | working_paper | municipal_report | verband_report | survey_report | market_study | ngo_report | policy_paper | guideline | whitepaper | report | software | thesis",
      "doi_url": "string",
      "open_access": true,
      "oa_status": "gold | green | hybrid | bronze | closed | unbekannt",
      "abstract_kurzfassung": "string, max. 300 Zeichen",
      "methodik": ["qualitative_interviews", "focus_groups", "thematic_analysis", "survey", "sensor_data", "review", "stakeholder_dialogue", "ethnography", "case_study"],
      "relevanz_begruendung": "1 bis 2 Sätze",
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

      "pruefhinweise": {
        "_hinweis": "Nur Fundstellen aus der Recherche, keine Bewertung. Die Rechteprüfung liest selbst nach.",
        "lizenzangabe_fundstelle": "string oder null",
        "anonymisierungserklaerung_fundstelle": "string oder null",
        "nutzungsbedingungen_url": "string oder null"
      },

      "daten_anhaenge": [
        {
          "typ": "interview_transkripte | interview_leitfaden | supplementary_pdf | codebook | survey_data | sensor_data | code_repository | appendix | sonstige",
          "titel_beschreibung": "Transkripte der 24 Leitfadeninterviews (Anhang S1)",
          "url": "https://doi.org/10.xxxx/supplementary-1",
          "format": "pdf | docx | csv | zip | txt | audio | html",
          "open_access": true,
          "lizenz": { },
          "datenschutz": { }
        }
      ],

      "lizenz": {
        "geprueft_am": "YYYY-MM-DD",
        "lizenz_bezeichnung": "string oder null",
        "lizenz_beleg_url": "string oder null",
        "lizenz_quelle": "api_feld | landing_page | lizenzdatei | nutzungsbedingungen | impressum | keine",
        "rechtmaessiger_zugang": true,
        "rechtevorbehalt": {
          "gefunden": false,
          "fundort": null,
          "geprueft": ["robots.txt", "agb", "tdmrep", "metadaten", "ai.robots.txt"]
        },
        "befund": {
          "N1": {"ergebnis": "frei | gestattet_schranke | zweifelhaft | gesperrt | nicht_pruefbar", "grundlage": "string oder null", "traegt_ohne_60d": true, "traegt_ohne_nc_praemisse": true},
          "N2": {"ergebnis": "…", "grundlage": null, "traegt_ohne_60d": false, "traegt_ohne_nc_praemisse": true},
          "N3": {"ergebnis": "…", "grundlage": null, "traegt_ohne_60d": false, "traegt_ohne_nc_praemisse": true}
        },
        "freigabeklasse": "K2_volltextwiedergabe | K1_analyse_und_zitat | K0_keine_freigabe",
        "k0_grund": "keine_lizenz_gefunden | nicht_pruefbar | kein_rechtmaessiger_zugang | n1_traegt_nicht | null (nur bei K1/K2)",
        "review_grund": "string oder null",
        "loeschpflicht_notiert": true
      },

      "datenschutz": {
        "geprueft_am": "YYYY-MM-DD",
        "pruefumfang": "volltext | stichprobe | anhang_separat | nicht_einsehbar",
        "stichprobe_beschreibung": "Umfang in Worten, nicht nur als Kategorie",
        "befund": "kein_personenbezug | personenbezogen | zweifelhaft | nicht_pruefbar | ausstehend",
        "grundlage": "vertrauensvermutung | red_flag | dreikriterientest | klassen_screening",
        "anonymisierungserklaerung": {
          "vorhanden": false,
          "fundstelle": null,
          "erklaerende_stelle": null,
          "stelle_einschlaegig": null
        },
        "red_flags_geprueft": ["R1","R2","R3","R4","R5","R6","R7","R8","R9"],
        "red_flags_gefunden": [
          {"flag": "R2", "fundstelle": "T4, T7", "beschreibung": "Straßennamen im Klartext"}
        ],
        "art9_kategorien": [],
        "art9_verschaerfter_massstab": false,
        "art10_betroffen": false,
        "dreikriterientest": {
          "no_record_isolation": {"P1": true, "P2": true, "P3": true},
          "no_linkage": {"P1": true, "P2": true, "P3": true},
          "no_inference": {"P1": true, "P2": true, "P3": true}
        },
        "review_grund": null,
        "aussortiert": false,
        "aussortierungsgrund": null,
        "autor_selbstauskunft": "Fundstelle eines Positionality-Absatzes oder null"
      }
    }
  ]
}
```

## 2. Pflichtfelder

Ein Eintrag gilt als unvollständig, wenn eines dieser Felder fehlt oder `null` ist.

Nach `topic-research` (`--stage research`):
`id` · `titel` · `jahr` · `quelle_plattform` · `quelle_typ` · `doi_url` · `relevanz_begruendung` ·
`qualitative_daten` (vollständig, auch wenn überall `false`)

Zusätzlich nach `source-compliance-check` (`--stage compliance`):
`lizenz.befund.N1` · `lizenz.befund.N2` · `lizenz.befund.N3` · **`lizenz.freigabeklasse`** ·
`lizenz.k0_grund` (bei `K0`) · `datenschutz.befund` · **`datenschutz.red_flags_geprueft`** ·
`datenschutz.stichprobe_beschreibung`. Dasselbe gilt für die Blöcke jedes Datenanhangs.

`scripts/validate_findings.py` prüft genau das.

## 3. Die drei Regeln, an denen Läufe scheitern

### 3.1 `daten_anhaenge` enthält nur eigenständige Begleitdateien

**Niemals eintragen:**
- die DOI-URL der Quelle selbst
- das Open-Access-PDF des Hauptartikels (`open_access.oa_url` aus OpenAlex ist das **Hauptpaper**)
- Pseudo-URLs wie `https://doi.org/10.xxxx#appA`
- die Landing Page

**Nur eintragen**, wenn eine echte eigenständige Datei existiert: separate ESM-Dateien (`mmc1.pdf`,
`suppl_tab1.xlsx`), Dateien aus dem Zenodo-`files`-Array außer dem Haupt-PDF, Transkriptdateien auf
QDR oder OSF.

**Im Haupttext abgedruckte Anhänge** (Leitfaden auf den letzten Seiten des PDF) werden über
`qualitative_daten.interview_leitfaden_verfuegbar: true` erfasst und in `relevanz_begruendung`
erwähnt, nicht als Anhang. Sonst lädt der Folge-Skill dasselbe PDF ein zweites Mal herunter.

**Default ist das leere Array.** Gibt es nichts, steht dort `[]`, nicht ein Platzhalter.

### 3.2 Anhänge tragen eigene Prüfblöcke

Ein Datenanhang kann anders lizenziert sein als die Quelle und enthält regelmäßig andere Daten.
Deshalb trägt jeder Anhang eigene `lizenz`- und `datenschutz`-Blöcke. Ein Transkript-Anhang zu einem
CC-BY-Artikel ist nicht automatisch CC BY und fast nie personenbezugsfrei.

### 3.3 Befunde stehen doppelt, aber nicht jeder Befund gehört in dieselbe Liste

Ein Flag tief im Eintrag wird nicht gefunden. Die Queue ist das, was ein Mensch tatsächlich öffnet.
Welcher Befund wohin gehört, folgt aber einer Unterscheidung:

| Befund | Zusätzlich wohin | Begründung |
|---|---|---|
| Lizenz `zweifelhaft`, `nicht_pruefbar` | `meta.review_queue` | offener Vorgang, jemand muss entscheiden |
| `K0` mit `k0_grund: keine_lizenz_gefunden` | nirgends zusätzlich | abschließend geprüft, nichts zu entscheiden |
| Datenschutz `personenbezogen` | `meta.aussortiert`, `typ: datenschutz` | keine Abwägung vorgesehen |
| Datenschutz `nicht_pruefbar` bei risikobehafteter Klasse | `meta.aussortiert`, `typ: datenschutz` | Personenbezug nicht ausschließbar |
| Datenschutz `zweifelhaft` | `meta.review_queue` | Tatsachenfrage offen, keine Rechtsgrundlagenfrage |
| Datenschutz `ausstehend` | `meta.review_queue` | Prüfung noch nicht gelaufen, muss nachgeholt werden |
| `gesperrt` für **alle** Nutzungsarten | `meta.aussortiert`, `typ: lizenz` | Quelle ist unbrauchbar |
| `gesperrt` für **einzelne** Nutzungsart | nirgends zusätzlich | geschlossenes Ergebnis, kein offener Vorgang |
| `frei` mit `traegt_ohne_nc_praemisse: false` | nirgends zusätzlich | dokumentierte Abhängigkeit, nichts zu entscheiden |

Die beiden letzten Zeilen sind wichtig: Eine Queue, die auch Einträge führt, zu denen nichts zu
entscheiden ist, wird nicht gelesen. Eine Quelle, die für `N1` frei und nur für `N2` gesperrt ist,
bleibt im Korpus und wird nicht aussortiert. Sie speist die Analyse, nur zitiert werden darf aus ihr
nicht.

### 3.4 Wann eine Quelle genutzt werden darf

Lizenz und Datenschutz sind zwei getrennte Urteile; keines verändert das andere. Folge-Skills
(`daten-download`, `stakeholder-analyse`) und das ausliefernde System verbinden sie mit genau dieser
Regel, für jede Quelle und jeden Datenanhang mit dessen eigenen Blöcken:

| `lizenz.freigabeklasse` | `datenschutz.befund` | Ergebnis |
|---|---|---|
| `K1` oder `K2` | `kein_personenbezug` | nutzen |
| `K1` oder `K2` | `zweifelhaft` oder `ausstehend` | warten, bis das Review entschieden oder die Prüfung nachgeholt ist |
| `K1` oder `K2` | `personenbezogen` oder `nicht_pruefbar` | nicht nutzen |
| `K0`, fehlend oder unbekannt | beliebig | nicht nutzen |

Fehlt einer der beiden Blöcke, gilt die Quelle als nicht nutzbar.

## 4. Extraktionsregeln je API

### OpenAlex
- Abstract aus `abstract_inverted_index` rekonstruieren
- `primary_location.landing_page_url` für die Landing Page
- `open_access.oa_url` ist das **Hauptpaper**, kein Anhang
- `primary_location.license` für die Rechteprüfung. `null` heißt keine Angabe, nicht „frei".
- `referenced_works` für Rückwärts-Snowballing, `filter=cites:<ID>` für Vorwärts

### Zenodo
- `files`-Array liefert Dateinamen, Größen und direkte Download-URLs
- `metadata.license.id` als SPDX-Kürzel, zuverlässigste Lizenzquelle überhaupt
- `metadata.resource_type.type` für `quelle_typ`

### CrossRef
- `license[]` kann mehrere Einträge führen. Der mit `content-version: "tdm"` ist für `N1` der
  einschlägige und wird vorrangig ausgewertet.

### Landing Pages (`fetch`)
- Abschnitte *Supplementary Materials*, *Electronic Supplementary Material*, *Supporting Information*,
  *Data Availability Statement* auswerten
- Nur Links zu echten separaten Dateien übernehmen
- Lizenzangabe und Nutzungsbedingungen mitlesen, und die Fundstelle in `pruefhinweise` notieren

### Abstract und Volltext
- Stichprobengröße suchen („N=18 interviews", „4 focus groups with 32 participants") →
  `qualitative_daten.stichprobengroesse`
- O-Töne im Text → `zitate_im_text: true`
- *Data Availability Statement* ist der ergiebigste Einzelabschnitt für beide Rechtschecks zugleich: Er
  nennt Lizenz, Repositorium und oft die Einwilligungslage der Befragten.
