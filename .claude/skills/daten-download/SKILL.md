---
name: daten-download
description: >
  Lädt die Quellen und Datenanhänge einer findings_<thema>.json lokal herunter, die nach der
  Rechteprüfung genutzt werden dürfen. Voraussetzung ist ein abgeschlossener Lauf von
  topic-research und source-compliance-check. Quellen mit Freigabeklasse K0, mit
  personenbezogenen oder nicht prüfbaren Daten und aussortierte Quellen werden nie geladen,
  Quellen mit offenem Datenschutz-Review erst nach dem Review. Speichert unter
  data/raw/<thema>/ und trägt lokale Pfade und Download-Status in die findings-Datei ein.
  Trigger-Phrasen: "Daten herunterladen", "findings downloaden", "Quellen speichern",
  "PDFs herunterladen", "Datensätze herunterladen", "download findings".
---

# Skill: Daten-Download & Lokale Speicherung

## Ziel
Eine geprüfte **`findings_<thema>.json`** einlesen und alle Quellen und Datenanhänge lokal
speichern, die genutzt werden dürfen. Die Datei wird danach mit lokalem Pfad und
Download-Status aktualisiert.

---

## Voraussetzungen prüfen

1. **findings-Datei vorhanden?**
   → Suche nach `findings_*.json` im Arbeitsverzeichnis.
   → Falls nicht: zuerst den Skill `topic-research` ausführen.

2. **Rechteprüfung abgeschlossen?**
   → `meta.lizenz_geprueft` und `meta.dsgvo_geprueft` müssen gesetzt sein.
   → Falls nicht: zuerst `source-compliance-check` ausführen. Das Skript bricht sonst ab.

3. **Python vorhanden?** → `python --version`. Für den Bericht zusätzlich `pypdf`.

Schema der Datei: `../topic-research/references/findings-schema.md`. Diese Datei ist die
einzige maßgebliche Schemabeschreibung.

---

## Was geladen wird: die Nutzungsregel

Lizenz und Datenschutz sind zwei getrennte Urteile. Geladen wird nur, was beide zulassen
(`findings-schema.md`, Abschnitt 3.4):

| `lizenz.freigabeklasse` | `datenschutz.befund` | Download |
|---|---|---|
| `K1` oder `K2` | `kein_personenbezug` | laden |
| `K1` oder `K2` | `zweifelhaft` oder `ausstehend` | nicht laden, `skipped_review`, nach dem Review erneut ausführen |
| `K1` oder `K2` | `personenbezogen` oder `nicht_pruefbar` | nie laden, `skipped_gesperrt` |
| `K0`, fehlend oder unbekannt | beliebig | nie laden, `skipped_gesperrt` |
| Quelle steht in `meta.aussortiert` | beliebig | nie laden, `skipped_gesperrt` |

**Jeder Datenanhang wird mit seinen eigenen Blöcken beurteilt.** Ein CC-BY-Datensatz zu einem
Aufsatz ohne Lizenz darf geladen werden; ein Transkript-Anhang mit Personenbezug zu einem
freien Aufsatz nicht. Die Regel steht einmal in `scripts/nutzungsregel.py` und wird von allen
drei Skripten verwendet. Sie nicht im Skill-Ablauf nachbauen oder umgehen.

**Lokale Kopien gesperrter Quellen** aus früheren Läufen meldet das Skript am Ende und
verschiebt den Pfad nach `local_path_gesperrt`. Gelöscht wird nicht automatisch. Die Liste
dem Benutzer zeigen und das Löschen empfehlen, bei `personenbezogen` dringend.

---

## Workflow

### Phase 0: Lagebild zeigen

Die findings-Datei lesen und ein **Download-Lagebild** erstellen:

```
Gesamt:                     <N> Einträge
Nutzbar und Open Access:    <N>  ← wird geladen
Gesperrt (K0, Datenschutz): <N>  ← wird nie geladen
Wartet auf Review:          <N>  ← wird erst nach dem Review geladen
Kein Open Access:           <N>  ← wird übersprungen
Bereits lokal:              <N>  ← wird übersprungen (Idempotenz)
Anhänge nutzbar / gesperrt: <N> / <N>
```

Den Trockenlauf dafür verwenden, er zeigt die Entscheidung je Eintrag:

```bash
python .claude/skills/daten-download/scripts/download_findings.py --findings "findings_<thema>.json" --dry-run
```

**Auf Bestätigung warten**, bevor der Download startet. Einzelne Quellen lassen sich vorher
mit `"download": false` ausschließen. Freischalten lässt sich auf diesem Weg nichts: Eine
gesperrte Quelle wird erst nutzbar, wenn `source-compliance-check` ihren Befund ändert.

---

### Phase 1: Download

```bash
python .claude/skills/daten-download/scripts/download_findings.py --findings "findings_<thema>.json"
```

**Bot-Schutz wird nicht umgangen.** Das Skript meldet sich mit eigenem User-Agent. Lehnt ein
Verlag den Abruf ab, sucht es über OpenAlex nach anderen Open-Access-Fundorten
(Hochschulrepositorien, PubMed Central) und meldet sonst `failed`. Keine Browser-Tarnung,
kein Ausweichen auf andere Werkzeuge, um eine Sperre zu umgehen.

#### Plattform-Strategien & Dateibenennung
Alle Dateien heißen `{Jahr}_{Erstautor}_{TitelSlug}_{ID}.{ext}`,
z. B. `2021_Barnes_Towards-a-More-Comprehensive-Picture_F-017.pdf`.

| Quelle | Zielordner | Download-Methode |
|--------|-----------|------------------|
| OA Journal-PDF / Preprint | `pdfs/` | Direkter Download; bei Ablehnung OpenAlex-Fallback auf andere OA-Fundorte |
| arXiv | `pdfs/` | `https://arxiv.org/pdf/<id>.pdf` |
| Figshare / Institutional Thesis | `pdfs/` | Figshare API (`api.figshare.com/v2/articles/<id>`) |
| Zenodo Dataset / Paper | `datasets/` / `pdfs/` | Zenodo API (`/api/records/<id>`) via `urllib` |
| GitHub Repo | `software/` | ZIP-Download |
| Harvard Dataverse | `datasets/` | Dataverse-API Dateiliste |
| Report / Grey Lit. | `reports/` | Direkter PDF-Download |

Details: `references/download_strategie.md`.

---

### Phase 2: Qualitativer PDF-Scan & Download-Report

`download_findings.py` erzeugt am Ende automatisch den Bericht. Einzeln:

```bash
python .claude/skills/daten-download/scripts/generate_download_report.py --findings "findings_<thema>.json"
```

Der Bericht `download_report_<thema>.md` enthält Kennzahlen, eine Übersicht der Volltexte mit
Freigabeklasse und die gefundenen O-Töne. Gescannt werden nur Quellen, die nach der
Nutzungsregel genutzt werden dürfen, auch wenn ältere Dateien noch lokal liegen.

Die O-Töne dienen der **internen Auswertung**. Aus `K1`-Quellen darf nach außen nur kurz und
mit Quellenangabe zitiert werden (§§ 51, 63 UrhG).

---

### Phase 3: Manuelle Einzelfall-Aktualisierung (Fallback)

```bash
python .claude/skills/daten-download/scripts/update_findings.py \
    --findings "findings_<thema>.json" \
    --id "<F-ID>" \
    --local-path "data/raw/<thema>/pdfs/{Year}_{author}_{title}_{id}.pdf" \
    --download-status "success"
```

Das Skript verweigert `success` und `--local-path` für Quellen, die nach der Nutzungsregel
nicht genutzt werden dürfen. Eine manuell geladene Datei einer gesperrten Quelle wird nicht
eingetragen, sondern gelöscht.

---

## Output-Struktur

```
<arbeitsverzeichnis>/
├── findings_<thema>.json          ← aktualisiert (local_path, download_status)
├── download_report_<thema>.md     ← Kennzahlen, Volltexte, O-Töne
└── data/
    └── raw/
        └── <thema>/
            ├── pdfs/
            ├── datasets/
            ├── reports/
            ├── transcripts/       ← nur Anhänge mit Datenschutzbefund kein_personenbezug
            └── software/
```

`data/raw/` gehört nicht ins Repository, wenn es urheberrechtlich geschützte Volltexte
enthält. Vor dem ersten Commit prüfen, ob `data/` in `.gitignore` steht.

---

## Neue Felder nach dem Download

Je Eintrag und je Anhang:

```json
{
  "download_status": "success | failed | skipped_no_oa | skipped_manual | skipped_existing | skipped_gesperrt | skipped_review | skipped_local_reference | included_in_main_document",
  "download_timestamp": "2026-08-12T15:00:00Z",
  "local_path": "data/raw/<thema>/reports/2020_FGSV_Hinweise-zu-Radverkehrsanlagen_F-001.pdf",
  "local_path_type": "pdf | csv | zip | directory",
  "local_path_gesperrt": "nur gesetzt, wenn eine frühere Kopie einer gesperrten Quelle gefunden wurde",
  "download_error": "Grund bei failed, skipped_gesperrt und skipped_review"
}
```

---

## Qualitätssicherung (Checkliste)

- [ ] Rechteprüfung abgeschlossen (`meta.lizenz_geprueft`, `meta.dsgvo_geprueft`)
- [ ] Lagebild aus dem Trockenlauf angezeigt und vom Benutzer bestätigt
- [ ] Keine Quelle oder kein Anhang mit `K0`, `personenbezogen`, `nicht_pruefbar` oder aus
      `meta.aussortiert` geladen
- [ ] Quellen mit Datenschutzbefund `zweifelhaft` oder `ausstehend` als `skipped_review` vermerkt
- [ ] Gemeldete lokale Kopien gesperrter Quellen dem Benutzer gezeigt
- [ ] Alle Dateien nach `{Year}_{author}_{title}_{id}.{ext}` benannt
- [ ] findings-Datei mit `local_path` und `download_status` für alle Einträge aktualisiert
- [ ] `download_report_<thema>.md` erzeugt

---

## Referenzen

- `scripts/nutzungsregel.py`: die gemeinsame Nutzungsregel
- `scripts/download_findings.py`: Download-Pipeline
- `scripts/generate_download_report.py`: Download- und Zitatbericht
- `scripts/update_findings.py`: manuelle Einzelaktualisierung
- `references/download_strategie.md`: Download-Strategien je Plattform
- `../topic-research/references/findings-schema.md`: Schema und Nutzungsregel (Abschnitt 3.4)
