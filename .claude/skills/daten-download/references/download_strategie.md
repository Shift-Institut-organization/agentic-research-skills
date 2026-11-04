# Download-Strategien pro Plattform

Dieses Dokument beschreibt die konkreten Download-Methoden für jede unterstützte
Plattform – inklusive URL-Schemas, API-Endpoints und Fallback-Strategien.

---

## Entscheidungsbaum: Was ist herunterladbar?

```
Eintrag in findings.json
        │
        ├─ download: false?  ──▶  ÜBERSPRINGEN (manuell gesetzt)
        │
        ├─ Nutzungsregel (nutzungsregel.py, findings-schema.md 3.4)
        │     K0, personenbezogen, nicht_pruefbar, aussortiert  ──▶  NIE LADEN (skipped_gesperrt)
        │     Datenschutz zweifelhaft oder ausstehend          ──▶  NICHT LADEN (skipped_review)
        │
        ├─ local_path gesetzt? ──▶  ÜBERSPRINGEN (bereits vorhanden, Idempotenz)
        │
        ├─ open_access: true  ──▶  HERUNTERLADEN
        │
        ├─ quelle_typ: "dataset"  ──▶  HERUNTERLADEN (Zenodo, Harvard Dataverse)
        │
        ├─ quelle_typ: "software"  ──▶  HERUNTERLADEN (GitHub ZIP)
        │
        └─ Sonst  ──▶  status: "skipped_no_oa", weiter
```

Jeder Datenanhang durchläuft die Nutzungsregel mit seinen eigenen `lizenz`- und
`datenschutz`-Blöcken, unabhängig vom Ergebnis der Quelle.

---

## 1. Open Access PDFs: andere Fundorte statt Umgehung (OpenAlex, Repositories)

**Wann:** `open_access: true` + `quelle_typ: "journal_article"` oder `"preprint"`

Viele Verlage (z. B. ScienceDirect/Elsevier, MDPI) lehnen automatisierte Abrufe ab (HTTP 403).
Diese Ablehnung wird **respektiert**: kein Browser-User-Agent, keine Ausweichwerkzeuge. Bei
Open-Access-Arbeiten liegt aber oft eine weitere, frei abrufbare Fassung in einem
Hochschulrepositorium, auf einem Preprint-Server oder in PubMed Central. Nur diese wird gesucht.

**Fallback über die OpenAlex API:**
1. DOI bei OpenAlex abfragen, mit Schlüssel aus `OPENALEX_API_KEY`, falls gesetzt:
   ```
   GET https://api.openalex.org/works/https://doi.org/<DOI>?api_key=<OPENALEX_API_KEY>
   User-Agent: DataFetch-daten-download/1.0 (Forschungsrecherche SHIFT)
   ```
2. Im Feld `locations` nach allen `pdf_url` filtern, die nicht auf die blockierte Verlagsdomain verweisen:
   - Universitäts-Repositorien (z. B. `pure.*`, `repository.*`, `orbi.*`, `ueaeprints.*`, `research.*`)
   - Europe PMC / PubMed Central (`ncbi.nlm.nih.gov/pmc/articles/PMC<ID>/pdf/`)
   - Figshare API (`api.figshare.com/v2/articles/<ID>`) für Master-/Doktorarbeiten
3. Über Pythons native `urllib.request` herunterladen.

---

## 2. Zenodo – Datasets & Publikationen (Schannel-sicher)

**Wann:** `quelle_plattform: "Zenodo"` oder `doi_url` enthält `zenodo`

**Wichtig für Windows:** Zenodo nicht über `curl.exe` oder PowerShell-WebRequests laden. Die Windows-Schannel-Zertifikatsprüfung (CRL/OCSP) führt dort zu 30-Sekunden-Timeouts. Python `urllib.request` nutzt OpenSSL und hat das Problem nicht. Die Zertifikatsprüfung abzuschalten (`--ssl-no-revoke`) ist keine Lösung.

**API-Workflow:**
1. Record-Metadaten abfragen:
   ```python
   import urllib.request, json
   url = f"https://zenodo.org/api/records/{record_id}"
   req = urllib.request.Request(url, headers={"User-Agent": "DataFetch-daten-download/1.0"})
   with urllib.request.urlopen(req, timeout=15) as resp:
       data = json.loads(resp.read().decode('utf-8'))
   ```
2. Dateiliste aus `data['files']` auslesen und streamen:
   ```python
   for f in data.get('files', []):
       dl_url = f['links'].get('content') or f['links'].get('self')
       # Download direkt via urllib in Zieldatei streamen
   ```

---

## 3. Dateibenennung & Standards

Alle heruntergeladenen Dateien erhalten strukturierte, lesbare Dateinamen:
```
{Jahr}_{Erstautor}_{TitelSlug}_{ID}.{ext}
```
- **Jahr:** z. B. `2021` (oder `ND` falls unbekannt)
- **Erstautor:** Nachname des 1. Autors bzw. Institutionsname bereinigt (z. B. `Barnes`, `UBA`, `Difu`, `Gemeente-Amsterdam`)
- **TitelSlug:** Bereinigter Kurztitel (max. 40 Zeichen, Bindestriche, keine Umlaute/Sonderzeichen)
- **ID:** Finding-ID (z. B. `F-017` bzw. `F-017_appendix_1`)
- **Beispiele:**
  - `2021_Barnes_Towards-a-More-Comprehensive-Picture_F-017.pdf`
  - `2020_UBA_Wirkungsanalyse-von-Massnahmen_F-002.pdf`
  - `2023_Gemeente-Amsterdam_Amsterdam-Bicycle-Flow-Counts_F-047.csv`

---

## 4. GitHub Repositories (Python)

**Wann:** `quelle_typ: "software"` oder `quelle_plattform: "GitHub"`

```python
import urllib.request, zipfile, io
from pathlib import Path

repo_url = "https://github.com/owner/repo/archive/refs/heads/main.zip"
dest_dir = Path("data/raw/<thema>/software") / f"{year}_{author}_{title_slug}_{id}"

# ZIP direkt im Speicher laden und entpacken
with urllib.request.urlopen(repo_url) as resp:
    with zipfile.ZipFile(io.BytesIO(resp.read())) as z:
        z.extractall(dest_dir)
```

---

## 5. arXiv Preprints (Python)

**Wann:** `quelle_plattform: "arXiv"`

```python
import urllib.request
from pathlib import Path

arxiv_id = "2301.12345"
pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
dest_file = Path("data/raw/<thema>/pdfs") / f"{year}_{author}_{title_slug}_{id}.pdf"

req = urllib.request.Request(pdf_url, headers={"User-Agent": "DataFetch-daten-download/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    dest_file.write_bytes(resp.read())
```

---

## 6. Harvard Dataverse & Repositorien (Python)

**Wann:** `quelle_plattform: "Harvard Dataverse"`

```python
import urllib.request, json
from pathlib import Path

pid = "doi:10.7910/DVN/XXXXX"
api_url = f"https://dataverse.harvard.edu/api/datasets/:persistentId/versions/:latest/files?persistentId={pid}"

with urllib.request.urlopen(api_url) as resp:
    files_data = json.loads(resp.read().decode('utf-8'))

for idx, f in enumerate(files_data.get("data", [])):
    file_id = f["dataFile"]["id"]
    filename = f["dataFile"]["filename"]
    ext = Path(filename).suffix
    dest_file = Path("data/raw/<thema>/datasets") / f"{year}_{author}_{title_slug}_{id}_{filename}"
    dl_url = f"https://dataverse.harvard.edu/api/access/datafile/{file_id}"
    with urllib.request.urlopen(dl_url) as r:
        dest_file.write_bytes(r.read())
```

---

## 7. Datenanhänge & Begleitmaterialien (`daten_anhaenge`)

Wenn ein Eintrag in `findings.json` ein Array `daten_anhaenge` enthält, werden ausschließlich **echte, eigenständige Begleitdateien** heruntergeladen. 

> [!NOTE]
> Falls ein Anhang dieselbe URL wie die Publikation hat (`anhang.url == entry.doi_url`) oder der Anhang lediglich im Volltext abgedruckt ist, wird kein separater Download ausgeführt, sondern auf das Hauptdokument verwiesen.

| Anhang-Typ | Zielordner | Namenskonvention |
|------------|------------|------------------|
| `interview_transkripte` | `transcripts/` | `{Year}_{author}_{title}_{ID}_transkript_<nr>.<ext>` |
| `interview_leitfaden` | `transcripts/` | `{Year}_{author}_{title}_{ID}_leitfaden.<ext>` |
| `codebook` / `survey_data` | `datasets/` | `{Year}_{author}_{title}_{ID}_codebook.<ext>` |
| `supplementary_pdf` / `appendix` | `pdfs/` | `{Year}_{author}_{title}_{ID}_appendix_<nr>.pdf` |

**Python Download-Loop für Anhänge (in `download_findings.py` integriert):**
```python
for idx, anhang in enumerate(entry.get("daten_anhaenge", [])):
    # Duplikatsprüfung: Nicht laden wenn URL mit Hauptdokument identisch ist
    if anhang.get("url") == entry.get("doi_url") or "#app" in anhang.get("url", ""):
        anhang["download_status"] = "included_in_main_document"
        continue
        
    ext = Path(anhang.get("url", "")).suffix.split("?")[0] or f".{anhang.get('format', 'pdf')}"
    folder = "transcripts" if "interview" in anhang.get("typ", "") else "datasets"
    filename = f"{year}_{author}_{title_slug}_{id}_{anhang['typ']}_{idx+1}{ext}"
    dest = Path("data/raw/<thema>") / folder / filename
    download_stream(anhang["url"], dest)
```

---

## 8. Fehlerbehandlung & Retry (Python)

```python
import time, urllib.request
from pathlib import Path

def download_with_retry(url: str, dest_path: Path, max_retries: int = 3, timeout: int = 30) -> bool:
    delay = 2
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DataFetch-daten-download/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = resp.read()
                if len(content) > 1000:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    dest_path.write_bytes(content)
                    return True
        except Exception as e:
            print(f"Versuch {attempt + 1} fehlgeschlagen: {e}")
            time.sleep(delay)
            delay *= 2
    return False
```

---

## 9. Automatisierte Gesamtausführung & Zitatbericht

Die gesamte Pipeline (Plattform-Erkennung, Zenodo-Urllib-Streaming, OpenAlex-Fallback, Figshare-API, Dateibenennung nach `{Year}_{author}_{title}_{id}.{ext}` und anschließender Zitatbericht) ist in zwei universellen Python-Skripten gebündelt:

### 1. Download-Pipeline:
```python
python .claude/skills/daten-download/scripts/download_findings.py --findings "findings_<thema>.json"
```

### 2. Download- & Zitatbericht (Erkennung von O-Tönen in allen PDFs):
```python
python .claude/skills/daten-download/scripts/generate_download_report.py --findings "findings_<thema>.json"
```
