#!/usr/bin/env python3
"""
download_findings.py
--------------------
Universeller, automatisierter Downloader für den 'daten_download'-Skill.
Liest eine beliebige 'findings_<thema>.json' ein und lädt alle Open-Access-Quellen
sowie echte Datenanhänge strukturiert in 'data/raw/<thema>/' herunter.

Unterstützt:
  - Universelle Pfad- & Themen-Erkennung (via CLI --findings oder Auto-Discovery)
  - Einheitliches Benennungsschema: {Jahr}_{Erstautor}_{TitelSlug}_{ID}.{ext}
  - Direkte Open-Access-Downloads (Springer, Reports, Zeitschriften)
  - Native Zenodo-Integration via urllib (OpenSSL, verhindert Schannel-Timeouts)
  - OpenAlex-Repository-Fallback bei HTTP 403 / Bot-Protection (Elsevier/MDPI)
  - Figshare-API-Auflösung für institutionelle Preprints & Dissertationen
  - Intelligente Duplikaterkennung (kein redundanter Download von Haupt-Paper-URLs)
  - Idempotenz (bereits vorhandene Dateien werden übersprungen)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

def find_workspace_root() -> Path:
    """Sucht das Wurzelverzeichnis des Repositories anhand von Marker-Dateien."""
    current = Path.cwd().resolve()
    for p in [current] + list(current.parents):
        if (p / ".agents").exists() or (p / ".git").exists():
            return p
    return current

WORKSPACE_ROOT = find_workspace_root()

def clean_slug(text: str, max_len: int = 40) -> str:
    """Wandelt einen Freitext in einen sauberen, dateisystemkompatiblen Slug um."""
    if not text:
        return "Dokument"
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue', 'ß': 'ss'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    words = text.strip().split()
    slug = "-".join(words)
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    return slug or "Dokument"

def clean_author(autoren: list, institutionen: list, default: str = "Autor") -> str:
    """Extrahiert einen prägnanten Nachnamen oder Institutionsnamen."""
    raw = None
    if autoren and len(autoren) > 0:
        raw = autoren[0]
    elif institutionen and len(institutionen) > 0:
        raw = institutionen[0]
    else:
        raw = default

    # Falls Kürzel in Klammern (z. B. "Allgemeiner Deutscher Fahrrad-Club (ADFC)")
    m = re.search(r'\(([A-Za-z0-9_-]+)\)', raw)
    if m:
        return m.group(1)

    parts = raw.strip().split()
    # Wenn Name = Vorname Nachname
    if len(parts) == 2 and not any(p.lower() in ["institut", "gesellschaft", "universitaet", "university", "gemeente", "club", "amt"] for p in parts):
        return clean_slug(parts[-1], max_len=20)
    
    return clean_slug(raw, max_len=20)

def generate_filename(item: dict, ext: str = ".pdf", suffix: str = "") -> str:
    """Erzeugt einen Dateinamen nach {Jahr}_{Erstautor}_{TitelSlug}_{ID}.{ext}."""
    fid = item.get("id")
    year = str(item.get("jahr") or "ND")
    author = clean_author(item.get("autoren", []), item.get("institutionen_genannt", []), item.get("quelle_plattform", "Anon"))
    title_slug = clean_slug(item.get("titel", "Ohne-Titel"), max_len=35)
    if suffix:
        clean_suf = re.sub(r'[^a-zA-Z0-9_-]', '', suffix)
        return f"{year}_{author}_{title_slug}_{fid}{clean_suf}{ext}"
    return f"{year}_{author}_{title_slug}_{fid}{ext}"

def _safe_delete(p: Path):
    if p.exists():
        for _ in range(3):
            try:
                p.unlink()
                break
            except OSError:
                time.sleep(0.2)

def download_stream(url: str, dest_path: Path, timeout: int = 30) -> bool:
    """Lädt eine URL via Pythons native urllib herunter (OpenSSL-basiert) mit curl-Fallback."""
    if not url or url.startswith("local://"):
        return False

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf,*/*;q=0.9"
    }
    # 1. Versuch: Python urllib (OpenSSL)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            if len(content) > 1000:
                if dest_path.suffix.lower() == ".pdf" and b"<html" in content[:250].lower():
                    return False
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_bytes(content)
                return True
    except Exception:
        pass

    # 2. Versuch: curl.exe in temporäre Datei
    import subprocess
    import uuid
    temp_file = dest_path.parent / f"_temp_{uuid.uuid4().hex[:8]}.bin"
    cmd = [
        "curl.exe", "-s", "-L",
        "--ssl-no-revoke",
        "-A", USER_AGENT,
        "--max-time", str(timeout),
        "-o", str(temp_file),
        url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and temp_file.exists():
            size = temp_file.stat().st_size
            if size > 1000:
                with open(temp_file, "rb") as f:
                    content = f.read()
                if dest_path.suffix.lower() == ".pdf" and b"<html" in content[:250].lower():
                    _safe_delete(temp_file)
                    return False
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_bytes(content)
                _safe_delete(temp_file)
                return True
            else:
                _safe_delete(temp_file)
    except Exception:
        _safe_delete(temp_file)
    return False

def resolve_figshare_pdf(url: str) -> str | None:
    """Extrahiert direkte Figshare-Download-URL aus Figshare/Institutional-Artikeln."""
    m = re.search(r'/(\d{7,10})(/|$)', url)
    if not m:
        return None
    article_id = m.group(1)
    api_url = f"https://api.figshare.com/v2/articles/{article_id}"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            files = data.get("files", [])
            if files and files[0].get("download_url"):
                return files[0]["download_url"]
    except Exception:
        pass
    return None

def resolve_openalex_pdf(doi: str) -> list[str]:
    """Sucht via OpenAlex nach alternativen Repository-PDF-Links (z.B. Uni-Repos, PMC)."""
    if not doi:
        return []
    clean_doi = doi.replace("https://doi.org/", "").strip()
    api_url = f"https://api.openalex.org/works/https://doi.org/{clean_doi}"
    headers = {"User-Agent": f"ShiftDataFetch/1.0 (mailto:shift@student.uni.de)"}
    candidates = []
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for loc in data.get("locations", []):
                pdf_url = loc.get("pdf_url")
                if pdf_url and "sciencedirect" not in pdf_url and "mdpi.com" not in pdf_url:
                    candidates.append(pdf_url)
    except Exception:
        pass
    return candidates

def download_zenodo_record(record_id: str, dest_dir: Path, item: dict) -> list[str]:
    """Lädt Dateien aus einem Zenodo Record nativ herunter."""
    url = f"https://zenodo.org/api/records/{record_id}"
    headers = {"User-Agent": USER_AGENT}
    saved_files = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            files = data.get("files", [])
            for f in files:
                key = f.get("key")
                content_url = f.get("links", {}).get("content") or f.get("links", {}).get("self")
                if not content_url:
                    continue
                file_ext = Path(key).suffix or ".dat"
                file_name = generate_filename(item, ext=file_ext, suffix=f"_{Path(key).stem}")
                file_dest = dest_dir / file_name
                if file_dest.exists() and file_dest.stat().st_size > 1000:
                    saved_files.append(file_dest.relative_to(WORKSPACE_ROOT).as_posix())
                    continue
                print(f"      Zenodo-Datei: {key} ({f.get('size')} Bytes)...")
                if download_stream(content_url, file_dest, timeout=60):
                    saved_files.append(file_dest.relative_to(WORKSPACE_ROOT).as_posix())
    except Exception as e:
        print(f"      [!] Zenodo API Fehler für Record {record_id}: {e}")
    return saved_files

def parse_args():
    parser = argparse.ArgumentParser(
        description="Lädt alle Open-Access-Quellen und Datenanhänge aus einer findings.json herunter."
    )
    parser.add_argument(
        "--findings", "-f",
        type=str,
        help="Pfad zur findings_<thema>.json Datei. Wenn weggelassen, wird im CWD gesucht."
    )
    parser.add_argument(
        "--dest-dir", "-d",
        type=str,
        help="Basisordner für Downloads (Standard: data/raw/<thema>/)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=30,
        help="Timeout in Sekunden für Downloads (Standard: 30)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Führt nur die Prüfung durch ohne Dateien herunterzuladen."
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Deaktiviert die automatische Erstellung des Download- & Zitatberichts nach dem Download."
    )
    return parser.parse_args()

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()

    # 1. Findings-Pfad auflösen
    if args.findings:
        findings_path = Path(args.findings).resolve()
    else:
        # Auto-Discovery im aktuellen Verzeichnis und Unterverzeichnissen
        cwd = Path.cwd()
        candidates = list(cwd.glob("findings*.json")) or list(cwd.glob("**/findings*.json"))
        if not candidates:
            print("[!] FEHLER: Keine 'findings*.json' gefunden. Bitte mit --findings angeben.")
            sys.exit(1)
        findings_path = candidates[0].resolve()

    if not findings_path.exists():
        print(f"[!] FEHLER: Datei {findings_path} nicht gefunden.")
        sys.exit(1)

    with open(findings_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Thema ermitteln
    meta_thema = data.get("meta", {}).get("thema", "")
    if not meta_thema:
        # Aus Dateinamen: findings_<thema>.json
        m = re.search(r'findings_?(.*)\.json', findings_path.name)
        meta_thema = m.group(1) if m else "unbekannt"
    thema_clean = clean_slug(meta_thema, max_len=30)

    # 3. Zielverzeichnisse aufbauen
    if args.dest_dir:
        base_dir = Path(args.dest_dir).resolve()
    else:
        base_dir = WORKSPACE_ROOT / "data" / "raw" / thema_clean

    subdirs = {
        "pdf": base_dir / "pdfs",
        "dataset": base_dir / "datasets",
        "report": base_dir / "reports",
        "transcript": base_dir / "transcripts",
        "software": base_dir / "software"
    }

    for d in subdirs.values():
        d.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("DATEN-DOWNLOAD SKILL: download_findings.py")
    print(f"📄 Findings-Datei: {findings_path.relative_to(WORKSPACE_ROOT) if findings_path.is_relative_to(WORKSPACE_ROOT) else findings_path}")
    print(f"🎯 Thema:          {meta_thema}")
    print(f"📁 Zielordner:     {base_dir.relative_to(WORKSPACE_ROOT) if base_dir.is_relative_to(WORKSPACE_ROOT) else base_dir}")
    print("=" * 65)

    findings = data.get("findings", [])
    stats = {
        "success": 0,
        "skipped_existing": 0,
        "skipped_no_oa": 0,
        "skipped_manual": 0,
        "failed": 0,
        "attachments_downloaded": 0
    }

    for item in findings:
        fid = item.get("id", "F-???")
        title = item.get("titel", "Ohne Titel")[:55]
        is_oa = item.get("open_access", False)
        download_flag = item.get("download", True)
        doi_url = item.get("doi_url", "")
        anhaenge = item.get("daten_anhaenge", [])
        qtyp = item.get("quelle_typ", "journal_article").lower()
        plat = item.get("quelle_plattform", "")

        print(f"\n[{fid}] {title}")

        # 1. Manuell ausgeschlossen
        if download_flag is False:
            print("  [-] Übersprungen (download: false)")
            item["download_status"] = "skipped_manual"
            stats["skipped_manual"] += 1
            continue

        # 2. Kein Open Access
        if not is_oa and not ("dataset" in qtyp or "zenodo" in plat.lower()):
            print("  [-] Übersprungen (kein Open Access)")
            item["download_status"] = "skipped_no_oa"
            stats["skipped_no_oa"] += 1
            continue

        # 3. Zielordner bestimmen
        if "dataset" in qtyp or "zenodo" in plat.lower():
            cat = "dataset"
        elif "report" in qtyp or "guideline" in qtyp:
            cat = "report"
        elif "software" in qtyp:
            cat = "software"
        else:
            cat = "pdf"
        target_dir = subdirs[cat]

        download_url = doi_url
        if not download_url and anhaenge and anhaenge[0].get("url") and not anhaenge[0].get("url").startswith("local://"):
            download_url = anhaenge[0].get("url")

        # 4. Prüfen ob bereits lokal vorhanden (Idempotenz)
        existing_local = item.get("local_path")
        if existing_local and (WORKSPACE_ROOT / existing_local).exists() and (WORKSPACE_ROOT / existing_local).stat().st_size > 1000:
            print(f"  [=] Bereits lokal vorhanden: {existing_local}")
            stats["skipped_existing"] += 1
            item["download_status"] = "success"
        elif args.dry_run:
            print("  [DRY-RUN] Würde heruntergeladen werden.")
        else:
            success = False
            dest_file = target_dir / generate_filename(item, ext=".pdf")
            try:
                # Fall A: Zenodo Record
                if "zenodo" in plat.lower() or "zenodo.org" in doi_url:
                    rec_match = re.search(r'zenodo\.(\d+)', doi_url)
                    if rec_match:
                        rec_id = rec_match.group(1)
                        print(f"  [↓] Lade Zenodo-Record {rec_id} via urllib...")
                        saved = download_zenodo_record(rec_id, target_dir, item)
                        if saved:
                            success = True
                            item["local_path"] = saved[0]
                            item["local_path_type"] = Path(saved[0]).suffix.lstrip(".")
                            stats["success"] += 1
                            print(f"  [OK] Zenodo gespeichert: {saved[0]}")
                else:
                    if download_url and download_url.startswith("local://"):
                        print(f"  [-] Lokaler Verweis ({download_url})")
                        item["download_status"] = "skipped_local_reference"
                        continue

                    # Fall B: Figshare / Institutional Preprints
                    if download_url and ("figshare" in download_url or "wgtn.ac.nz" in download_url):
                        fig_direct = resolve_figshare_pdf(download_url)
                        if fig_direct:
                            download_url = fig_direct

                    # Direkter Download
                    if download_url:
                        print(f"  [↓] Lade Hauptdatei von: {download_url[:65]}...")
                        if download_stream(download_url, dest_file, timeout=args.timeout):
                            success = True
                            rel = dest_file.relative_to(WORKSPACE_ROOT).as_posix()
                            item["local_path"] = rel
                            item["local_path_type"] = "pdf"
                            stats["success"] += 1
                            print(f"  [OK] Gespeichert: {rel} ({dest_file.stat().st_size / 1024:.1f} KB)")
                        else:
                            print("  [!] Direkter Download blockiert. Suche OpenAlex-Fallback...")
                            candidates = resolve_openalex_pdf(doi_url)
                            for cand in candidates:
                                print(f"    Versuche Fallback: {cand[:65]}...")
                                if download_stream(cand, dest_file, timeout=args.timeout):
                                    success = True
                                    rel = dest_file.relative_to(WORKSPACE_ROOT).as_posix()
                                    item["local_path"] = rel
                                    item["local_path_type"] = "pdf"
                                    stats["success"] += 1
                                    print(f"    [OK] Fallback erfolgreich: {rel} ({dest_file.stat().st_size / 1024:.1f} KB)")
                                    break
            except Exception as e:
                print(f"  [!] Fehler beim Download: {e}")

            if success:
                item["download_status"] = "success"
                item["download_error"] = None
                item["download_timestamp"] = datetime.now(timezone.utc).isoformat()
            else:
                if not item.get("download_status") == "success":
                    item["download_status"] = "failed"
                    item["download_error"] = "Blocked by publisher bot protection or no accessible open full text"
                    stats["failed"] += 1
                    print("  [FAIL] Konnte Hauptdokument nicht herunterladen.")

        # 5. Echte Datenanhänge & Begleitmaterialien verarbeiten
        for idx, anhang in enumerate(anhaenge):
            a_typ = anhang.get("typ", "supplementary_pdf")
            a_url = anhang.get("url")
            a_format = anhang.get("format", "pdf").lower()
            a_titel = anhang.get("titel_beschreibung", "")

            # Zielordner für Anhang
            if any(k in a_typ for k in ["interview", "transkript", "leitfaden"]):
                a_dir = subdirs["transcript"]
            elif any(k in a_typ for k in ["survey", "codebook", "dataset"]):
                a_dir = subdirs["dataset"]
            else:
                a_dir = subdirs["pdf"]

            a_filename = generate_filename(item, ext=f".{a_format}", suffix=f"_{a_typ}_{idx+1}")
            a_dest = a_dir / a_filename
            a_rel = a_dest.relative_to(WORKSPACE_ROOT).as_posix()

            # Duplikats- und In-Text-Prüfung
            is_dup_or_included = (
                not a_url
                or a_url == doi_url
                or a_url == item.get("doi")
                or "#app" in a_url
                or "Publikations-PDF" in a_titel
                or "Volltext" in a_titel
                or a_url == download_url
            )
            if is_dup_or_included:
                if item.get("local_path"):
                    anhang["local_path"] = item.get("local_path")
                    anhang["download_status"] = "included_in_main_document"
                    print(f"    [+] Anhang '{a_typ}': Im Hauptdokument enthalten / verweist auf Hauptdokument ({item.get('local_path')})")
                continue

            # Bereits lokal vorhanden
            if a_dest.exists() and a_dest.stat().st_size > 1000:
                anhang["local_path"] = a_rel
                anhang["download_status"] = "success"
                continue

            if args.dry_run:
                continue

            # Separater Download echter Begleitdateien
            if a_url and not a_url.startswith("local://") and a_url != download_url:
                print(f"    [↓] Lade echten Anhang '{a_typ}': {a_titel[:40]}...")
                if download_stream(a_url, a_dest, timeout=args.timeout):
                    anhang["local_path"] = a_rel
                    anhang["download_status"] = "success"
                    stats["attachments_downloaded"] += 1
                    print(f"    [OK] Anhang gespeichert: {a_rel}")
                else:
                    anhang["download_status"] = "failed"

    # Aktualisierte Findings speichern
    if not args.dry_run:
        with open(findings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 65)
    print("DOWNLOAD-ABSCHLUSSBERICHT")
    print("=" * 65)
    print(f"✅ Volltexte neu geladen:        {stats['success']}")
    print(f"✅ Volltexte bereits vorhanden:  {stats['skipped_existing']}")
    print(f"📎 Anhänge heruntergeladen:     {stats['attachments_downloaded']}")
    print(f"⚠️  Übersprungen (kein OA):      {stats['skipped_no_oa']}")
    print(f"⚠️  Übersprungen (manuell):      {stats['skipped_manual']}")
    print(f"❌ Nicht abrufbar (Paywall/Bot): {stats['failed']}")
    print(f"📁 Zielordner:                   {base_dir}")
    print(f"📄 Aktualisierte Findings:       {findings_path}")
    print("=" * 65)

    # Automatische Erstellung des Download- & Zitat-Berichts
    if not args.dry_run and not args.no_report:
        try:
            from generate_download_report import generate_report
            print("\n[INFO] Erstelle automatischen Download- & Zitatbericht...")
            report_file = generate_report(findings_path)
            print(f"📄 Download-Bericht erfolgreich generiert: {report_file}")
        except Exception as e:
            print(f"[!] Hinweis: Automatischer Download-Bericht konnte nicht erstellt werden: {e}")

if __name__ == "__main__":
    main()
