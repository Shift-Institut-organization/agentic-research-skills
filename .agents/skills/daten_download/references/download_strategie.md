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

---

## 1. Open Access PDFs & Bot-Blocker-Bypass (OpenAlex, Unpaywall, Repositories)

**Wann:** `open_access: true` + `quelle_typ: "journal_article"` oder `"preprint"`

Viele Verlage (z. B. ScienceDirect/Elsevier, MDPI) blockieren automatisierte HTTP-Anfragen via Cloudflare oder Akamai (HTTP 403 Forbidden). Da die Arbeiten jedoch Open Access sind, existieren legale, unblockierte Volltexte in universitären Repositories, Preprint-Servern und Archiven.

**Bypass-Strategie via OpenAlex API:**
1. DOI bei OpenAlex abfragen:
   ```
   GET https://api.openalex.org/works/https://doi.org/<DOI>
   User-Agent: DataFetch/1.0 (mailto:research@example.com)
   ```
2. Im Feld `locations` nach allen `pdf_url` filtern, die nicht auf die blockierte Verlagsdomain verweisen:
   - Universitäts-Repositorien (z. B. `pure.*`, `repository.*`, `orbi.*`, `ueaeprints.*`, `research.*`)
   - Europe PMC / PubMed Central (`ncbi.nlm.nih.gov/pmc/articles/PMC<ID>/pdf/`)
   - Figshare API (`api.figshare.com/v2/articles/<ID>`) für Master-/Doktorarbeiten
3. Über Pythons native `urllib.request` herunterladen.

---

## 2. Zenodo – Datasets & Publikationen (Schannel-sicher)

**Wann:** `quelle_plattform: "Zenodo"` oder `doi_url` enthält `zenodo`

**Wichtig für Windows:** Niemals Windows `curl.exe` ohne `--ssl-no-revoke` oder Standard-PowerShell-WebRequests gegen Zenodo ausführen, da die Windows-Schannel-Zertifikatsprüfung (CRL/OCSP) zu 30-Sekunden-Timeouts (HTTP 504 / Connection Timeout) führt. Stattdessen Python native `urllib.request` (nutzt OpenSSL und TLS 1.3) verwenden!

**API-Workflow:**
1. Record-Metadaten abfragen:
   ```python
   import urllib.request, json
   url = f"https://zenodo.org/api/records/{record_id}"
   req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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

req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
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
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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
python .agents/skills/daten_download/scripts/download_findings.py --findings "findings_<thema>.json"
```

### 2. Download- & Zitatbericht (Erkennung von O-Tönen in allen PDFs):
```python
python .agents/skills/daten_download/scripts/generate_download_report.py --findings "findings_<thema>.json"
```
