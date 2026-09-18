---
name: daten_download
description: >
  Lädt Quellen aus einer findings.json (produziert vom suchprotokoll_recherche-Skill)
  lokal herunter. Filtert nach Open-Access-Status und Dateityp, speichert Dateien
  strukturiert im Repo unter data/raw/<thema>/, und aktualisiert die findings.json
  mit lokalen Pfaden und Download-Status. Trigger-Phrasen: "Daten herunterladen",
  "findings downloaden", "Quellen speichern", "PDFs herunterladen",
  "Datensätze herunterladen", "download findings".
---

# Skill: Daten-Download & Lokale Speicherung

## Ziel
Eine bestehende **`findings_<thema>.json`** einlesen und alle herunterladbaren
Quellen lokal im Repo speichern. Die findings.json wird danach mit lokalem Pfad
und Download-Status aktualisiert.

---

## Voraussetzungen prüfen

1. **findings.json vorhanden?**
   → Suche nach `findings_*.json` im Arbeitsverzeichnis.
   → Falls nicht: Benutzer auffordern, zuerst `suchprotokoll_recherche` auszuführen.

2. **Python vorhanden?** (für `update_findings.py`)
   → `python --version` ausführen.

---

## Workflow

### Phase 0: findings.json einlesen & Lagebild zeigen

Lies die findings.json und erstelle ein **Download-Lagebild**:

```
Gesamt:              <N> Einträge
Open Access (OA):    <N>  ← herunterladbar
Kein OA:             <N>  ← wird übersprungen
Bereits lokal:       <N>  ← wird übersprungen (Idempotenz)

Typen (herunterladbar):
  journal_article / preprint:  <N>  (nur wenn OA)
  dataset:                     <N>  (Zenodo, Dataverse)
  software:                    <N>  (GitHub)
  report / grey_literature:    <N>  (meist frei)
```

**Warte auf Bestätigung** des Benutzers bevor der Download startet.
Der Benutzer kann vorher noch Einträge mit `"download": false` manuell
in der findings.json markieren, um einzelne Quellen auszuschließen.

---

### Phase 1: Download & Vollautomatisierte Speicherung

Der gesamte Download-Workflow (inkl. Ordnererstellung, Bot-Bypass, Zenodo-Urllib-Streaming, Figshare-API, Idempotenz, Deduplikation und Dateibenennung) wird über das universelle Python-Skript ausgeführt:

```bash
python .agents/skills/daten_download/scripts/download_findings.py --findings "findings_<thema>.json"
```

Optionaler Trockenlauf (prüft Verfügbarkeit ohne Speicherung):
```bash
python .agents/skills/daten_download/scripts/download_findings.py --findings "findings_<thema>.json" --dry-run
```

#### Plattform-Strategien & Dateibenennung:
Alle heruntergeladenen Dateien werden streng nach folgendem Standard benannt:
`{Year}_{author}_{title}_{id}.{ext}`
Beispiel: `2021_Barnes_Towards-a-More-Comprehensive-Picture_F-017.pdf`

| Quelle | Zielordner | Download-Methode |
|--------|-----------|------------------|
| OA Journal-PDF / Preprint | `pdfs/` | Direkter Download; bei 403-Bot-Block (Elsevier/MDPI) → OpenAlex Repository-Fallback |
| arXiv | `pdfs/` | `https://arxiv.org/pdf/<id>.pdf` → gespeichert als `{Year}_{author}_{title}_{id}.pdf` |
| Figshare / Institutional Thesis | `pdfs/` | Figshare API (`api.figshare.com/v2/articles/<id>`) → Direkt-Download |
| Zenodo Dataset / Paper | `datasets/` / `pdfs/` | Zenodo API (`/api/records/<id>`) via native Python `urllib` (OpenSSL, kein Timeout) |
| GitHub Repo | `software/` | ZIP-Download + entpacken nach `software/{Year}_{author}_{title}_{id}/` |
| Harvard Dataverse | `datasets/` | Dataverse-API Dateiliste → Download nach `{Year}_{author}_{title}_{id}_{filename}` |
| Report / Grey Lit. | `reports/` | Direkter PDF-Download aus Metadaten/Websuche |

---

### Phase 2: Qualitativer PDF-Scan & Download-Report

Nach dem Download durchsucht das Skript `generate_download_report.py` alle lokal gesicherten PDFs automatisiert nach wörtlichen Zitaten, O-Tönen von Studienteilnehmern/Radfahrenden und qualitativen Befragungsabschnitten:

```bash
python .agents/skills/daten_download/scripts/generate_download_report.py --findings "findings_<thema>.json"
```

*(Hinweis: `download_findings.py` führt diesen Schritt standardmäßig automatisch am Ende des Downloads aus.)*

**Ergebnis:**
Erstellt `download_report_<thema>.md` mit:
- Download-Kennzahlen & Erfolgsquote
- Volltext-Übersichtstabelle inklusive Zitate-Nachweis (Ja/Nein, Seitenzahl)
- Allen extrahierten O-Tönen für die nachgelagerte Persona- und Stakeholder-Analyse

---

### Phase 3: Manuelle Einzelfall-Aktualisierung (Fallback)

Für manuelle Einzelfall-Downloads steht das Hilfsskript `update_findings.py` bereit:
```bash
python .agents/skills/daten_download/scripts/update_findings.py \
    --findings "findings_<thema>.json" \
    --id "<F-ID>" \
    --local-path "data/raw/<thema>/pdfs/{Year}_{author}_{title}_{id}.pdf" \
    --download-status "success"
```

---

## Output-Struktur

```
<arbeitsverzeichnis>/
├── findings_<thema>.json          ← aktualisiert (local_path, download_status)
├── download_report_<thema>.md     ← Qualitätsbericht mit extrahierten O-Tönen & Kennzahlen
└── data/
    └── raw/
        └── <thema>/
            ├── pdfs/              ← OA Artikel & Preprints ({Year}_{author}_{title}_{id}.pdf)
            ├── datasets/          ← CSV, JSON, ZIP von Zenodo etc.
            ├── reports/           ← Grey Literature & Berichte ({Year}_{author}_{title}_{id}.pdf)
            ├── transcripts/       ← Echte Datenanhänge ({Year}_{author}_{title}_{id}_{typ}_{nr}.pdf)
            └── software/          ← GitHub Repos ({Year}_{author}_{title}_{id}/)
```

---

## Neue Felder in findings.json nach Download

```json
{
  "id": "F-001",
  "...": "...",
  "download_status": "success | failed | skipped_no_oa | skipped_manual | skipped_existing",
  "download_timestamp": "2026-08-12T15:00:00Z",
  "local_path": "data/raw/<thema>/reports/2020_FGSV_Hinweise-zu-Radverkehrsanlagen_F-001.pdf",
  "local_path_type": "pdf | csv | zip | directory",
  "download_error": null
}
```

---

## Qualitätssicherung (Checkliste)

- [ ] Lagebild angezeigt und Benutzer hat bestätigt
- [ ] Ordnerstruktur und Downloads via Python ausgeführt
- [ ] Alle Dateien nach Standard `{Year}_{author}_{title}_{id}.{ext}` benannt
- [ ] Idempotenz gewahrt: bereits vorhandene Dateien nicht neu geladen
- [ ] findings.json mit `local_path` + `download_status` für alle Einträge aktualisiert
- [ ] `download_report_<thema>.md` generiert und alle heruntergeladenen PDFs auf Zitate/O-Töne geprüft

---

## Referenzen

- **Standard-Downloader-Script:** `scripts/download_findings.py` (Vollautomatisierter Pipeline-Download mit Bot-Bypass, Zenodo-Urllib-Streaming, Figshare-API, Idempotenz & Dateibenennung)
- **Qualitativer Report-Generator:** `scripts/generate_download_report.py` (Scannt alle gespeicherten PDFs nach wörtlichen Zitaten und erzeugt den Download-Report)
- Download-Strategien pro Plattform: `references/download_strategie.md`
- findings.json Schema: `../stakeholder_analyse/references/findings_schema.md`
- Inkrementelles Einzel-Update-Script: `scripts/update_findings.py`
