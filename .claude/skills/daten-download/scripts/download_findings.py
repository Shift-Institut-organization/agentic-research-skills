#!/usr/bin/env python3
"""
download_findings.py
--------------------
Universeller, automatisierter Downloader für den Skill 'daten-download'.
Liest eine 'findings_<thema>.json' nach source-compliance-check ein und lädt die
Quellen und echten Datenanhänge, die genutzt werden dürfen, strukturiert in
'data/raw/<thema>/' herunter.

Was geladen wird, entscheidet allein nutzungsregel.py (findings-schema.md, 3.4):
  - Freigabeklasse K1 oder K2 UND Datenschutzbefund kein_personenbezug -> laden
  - Datenschutzbefund zweifelhaft -> nicht laden, wartet auf das Review
  - K0, personenbezogen, nicht_pruefbar, fehlende Blöcke, meta.aussortiert -> nicht laden
Jeder Datenanhang wird mit seinen eigenen Blöcken beurteilt, unabhängig von der Quelle.
Ohne abgeschlossene Rechteprüfung (meta.lizenz_geprueft und meta.dsgvo_geprueft)
bricht das Skript ab.

Unterstützt:
  - Universelle Pfad- & Themen-Erkennung (via CLI --findings oder Auto-Discovery)
  - Einheitliches Benennungsschema: {Jahr}_{Erstautor}_{TitelSlug}_{ID}.{ext}
  - Direkte Open-Access-Downloads (Springer, Reports, Zeitschriften)
  - Native Zenodo-Integration via urllib (OpenSSL, verhindert Schannel-Timeouts)
  - OpenAlex-Fallback auf andere Open-Access-Fundorte (Repositorien, PMC), wenn der
    Verlag den Abruf ablehnt. Bot-Schutz wird nicht umgangen: Das Skript meldet sich
    mit eigenem User-Agent und versucht keine Tarnung.
  - Figshare-API-Auflösung für institutionelle Preprints & Dissertationen
  - Intelligente Duplikaterkennung (kein redundanter Download von Haupt-Paper-URLs)
  - Idempotenz (bereits vorhandene Dateien werden übersprungen)
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nutzungsregel import (  # noqa: E402
    anhang_schluessel, aussortiert_schluessel, compliance_geprueft, nutzungsstatus,
    quelle_schluessel,
)

# Ehrlicher User-Agent: Blockt ein Verlag automatisierte Abrufe, wird das respektiert
# und als failed gemeldet, nicht mit einem Browser-User-Agent umgangen.
USER_AGENT = "DataFetch-daten-download/1.0 (Forschungsrecherche SHIFT)"

def find_workspace_root() -> Path:
    """Sucht das Wurzelverzeichnis des Repositories anhand von Marker-Dateien."""
    current = Path.cwd().resolve()
    for p in [current] + list(current.parents):
        if (p / ".claude").exists() or (p / ".git").exists():
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

def download_stream(url: str, dest_path: Path, timeout: int = 30) -> bool:
    """Lädt eine URL via Pythons native urllib herunter (OpenSSL-basiert)."""
    if not url or url.startswith("local://"):
        return False

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf,*/*;q=0.9"
    }
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
    return False

def warne_bei_lokaler_kopie(obj: dict, sammlung: list, label: str = None):
    """
    Merkt eine vorhandene lokale Datei einer gesperrten Quelle oder eines gesperrten
    Anhangs vor. Geloescht wird nicht automatisch: Das entscheidet ein Mensch, aber
    die Datei darf nicht unbemerkt im Datenpool bleiben.
    """
    lp = obj.get("local_path")
    if lp and (WORKSPACE_ROOT / lp).exists():
        sammlung.append(f"{label or obj.get('id', '?')}: {lp} ({obj.get('download_error')})")
        obj["local_path_gesperrt"] = lp
        obj["local_path"] = None


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
    if os.environ.get("OPENALEX_API_KEY"):
        api_url += f"?api_key={os.environ['OPENALEX_API_KEY']}"
    headers = {"User-Agent": USER_AGENT}
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

    # 1b. Ohne abgeschlossene Rechteprüfung wird nichts geladen
    meta = data.get("meta", {})
    if not compliance_geprueft(meta):
        print("[!] ABBRUCH: Die Rechteprüfung ist für diese Datei nicht abgeschlossen "
              "(meta.lizenz_geprueft oder meta.dsgvo_geprueft fehlt).")
        print("    Zuerst den Skill source-compliance-check ausführen. Ohne Lizenz- und "
              "Datenschutzbefund darf keine Quelle geladen werden.")
        sys.exit(1)
    aussortiert = aussortiert_schluessel(meta)

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
        "skipped_gesperrt": 0,
        "skipped_review": 0,
        "failed": 0,
        "attachments_downloaded": 0,
        "anhang_skipped_gesperrt": 0,
        "anhang_skipped_review": 0,
    }
    gesperrt_lokal = []  # lokale Kopien von Quellen, die nicht (mehr) genutzt werden dürfen

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

        # 1. Manuell ausgeschlossen (gilt auch für die Anhänge)
        if download_flag is False:
            print("  [-] Übersprungen (download: false)")
            item["download_status"] = "skipped_manual"
            stats["skipped_manual"] += 1
            continue

        # 2. Nutzungsregel: Lizenz und Datenschutz der Quelle selbst
        status, grund = nutzungsstatus(item, quelle_schluessel(item), aussortiert)
        download_url = doi_url
        if status != "nutzen":
            key = "skipped_review" if status == "warten" else "skipped_gesperrt"
            print(f"  [-] Nicht geladen ({grund})")
            item["download_status"] = key
            item["download_error"] = grund
            stats[key] += 1
            warne_bei_lokaler_kopie(item, gesperrt_lokal)

        # 3. Kein Open Access
        elif not is_oa and not ("dataset" in qtyp or "zenodo" in plat.lower()):
            print("  [-] Übersprungen (kein Open Access)")
            item["download_status"] = "skipped_no_oa"
            stats["skipped_no_oa"] += 1

        else:
            # 4. Zielordner bestimmen
            if "dataset" in qtyp or "zenodo" in plat.lower():
                cat = "dataset"
            elif "report" in qtyp or "guideline" in qtyp:
                cat = "report"
            elif "software" in qtyp:
                cat = "software"
            else:
                cat = "pdf"
            target_dir = subdirs[cat]

            if not download_url and anhaenge and anhaenge[0].get("url") and not anhaenge[0].get("url").startswith("local://"):
                download_url = anhaenge[0].get("url")

            # 5. Prüfen ob bereits lokal vorhanden (Idempotenz)
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
                    elif download_url and download_url.startswith("local://"):
                        print(f"  [-] Lokaler Verweis ({download_url})")
                        item["download_status"] = "skipped_local_reference"
                    else:
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
                                print("  [!] Direkter Download abgelehnt. Suche andere Open-Access-Fundorte über OpenAlex...")
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
                elif item.get("download_status") not in ("success", "skipped_local_reference"):
                    item["download_status"] = "failed"
                    item["download_error"] = ("Abruf vom Server abgelehnt oder kein frei "
                                              "zugänglicher Volltext gefunden")
                    stats["failed"] += 1
                    print("  [FAIL] Konnte Hauptdokument nicht herunterladen.")

        # 6. Echte Datenanhänge: jeder mit seinen eigenen Prüfblöcken
        haupt_lokal = item.get("local_path") if status == "nutzen" else None
        for idx, anhang in enumerate(anhaenge):
            a_typ = anhang.get("typ", "supplementary_pdf")
            a_url = anhang.get("url")
            a_format = anhang.get("format", "pdf").lower()
            a_titel = anhang.get("titel_beschreibung", "")

            a_status, a_grund = nutzungsstatus(anhang, anhang_schluessel(anhang), aussortiert)
            if a_status != "nutzen":
                key = "skipped_review" if a_status == "warten" else "skipped_gesperrt"
                print(f"    [-] Anhang '{a_typ}' nicht geladen ({a_grund})")
                anhang["download_status"] = key
                anhang["download_error"] = a_grund
                stats[f"anhang_{key}"] += 1
                warne_bei_lokaler_kopie(anhang, gesperrt_lokal, label=f"{fid} Anhang {idx + 1}")
                continue

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
                # Verweis auf das Hauptdokument nur, wenn dieses selbst genutzt werden darf
                if haupt_lokal:
                    anhang["local_path"] = haupt_lokal
                    anhang["download_status"] = "included_in_main_document"
                    print(f"    [+] Anhang '{a_typ}': Im Hauptdokument enthalten / verweist auf Hauptdokument ({haupt_lokal})")
                continue

            # Bereits lokal vorhanden
            if a_dest.exists() and a_dest.stat().st_size > 1000:
                anhang["local_path"] = a_rel
                anhang["download_status"] = "success"
                continue

            if args.dry_run:
                print(f"    [DRY-RUN] Anhang '{a_typ}' würde heruntergeladen werden.")
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
    print(f"⛔ Gesperrt (K0/Datenschutz):    {stats['skipped_gesperrt']} Quellen, "
          f"{stats['anhang_skipped_gesperrt']} Anhänge")
    print(f"⏳ Wartet auf Review:            {stats['skipped_review']} Quellen, "
          f"{stats['anhang_skipped_review']} Anhänge")
    print(f"❌ Nicht abrufbar (abgelehnt):   {stats['failed']}")
    print(f"📁 Zielordner:                   {base_dir}")
    print(f"📄 Aktualisierte Findings:       {findings_path}")
    print("=" * 65)

    if gesperrt_lokal:
        print("\n[!] ACHTUNG: Lokale Kopien von Quellen, die nicht genutzt werden dürfen.")
        print("    Sie stammen aus einem früheren Lauf. Bitte prüfen und löschen, bei")
        print("    Datenschutzbefund personenbezogen sofort:")
        for zeile in gesperrt_lokal:
            print(f"      - {zeile}")

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
