#!/usr/bin/env python3
"""
update_findings.py
------------------
Aktualisiert einen Eintrag in der findings.json nach einem Download.
Idempotent: bereits gesetzte Felder werden nicht überschrieben.

Verwendung:
    python update_findings.py \
        --findings findings_<thema>.json \
        --id F-001 \
        --local-path "data/raw/<thema>/pdfs/F-001.pdf" \
        --download-status success

    python update_findings.py \
        --findings findings_<thema>.json \
        --id F-002 \
        --download-status skipped_no_oa
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nutzungsregel import aussortiert_schluessel, nutzungsstatus, quelle_schluessel  # noqa: E402

VALID_STATUSES = {
    "success",
    "failed",
    "skipped_no_oa",
    "skipped_manual",
    "skipped_existing",
    "skipped_too_large",
    "skipped_gesperrt",
    "skipped_review",
}


def load_findings(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_findings(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_entry(data: dict, entry_id: str) -> dict | None:
    for entry in data.get("findings", []):
        if entry.get("id") == entry_id:
            return entry
    return None


def infer_type(local_path: str) -> str:
    ext = Path(local_path).suffix.lower()
    return {".pdf": "pdf", ".csv": "csv", ".zip": "zip", ".json": "json", ".txt": "txt"}.get(ext, "unknown")


def main():
    parser = argparse.ArgumentParser(description="findings.json nach Download aktualisieren.")
    parser.add_argument("--findings", required=True, help="Pfad zur findings.json")
    parser.add_argument("--id", required=True, dest="entry_id", help="Eintrags-ID (z. B. F-001)")
    parser.add_argument("--download-status", required=True, choices=list(VALID_STATUSES))
    parser.add_argument("--local-path", default=None, help="Lokaler Dateipfad")
    parser.add_argument("--local-path-type", default=None, help="Dateityp: pdf | csv | zip | directory")
    parser.add_argument("--error-message", default=None, help="Fehlermeldung bei Status 'failed'")
    args = parser.parse_args()

    findings_path = Path(args.findings)
    if not findings_path.exists():
        print(f"FEHLER: {findings_path} nicht gefunden.", file=sys.stderr)
        sys.exit(1)

    data = load_findings(findings_path)
    entry = find_entry(data, args.entry_id)
    if entry is None:
        print(f"FEHLER: ID '{args.entry_id}' nicht in findings.json gefunden.", file=sys.stderr)
        sys.exit(1)

    # Auch ein manueller Download unterliegt der Nutzungsregel.
    if args.download_status == "success" or args.local_path:
        status, grund = nutzungsstatus(entry, quelle_schluessel(entry),
                                       aussortiert_schluessel(data.get("meta")))
        if status != "nutzen":
            print(f"FEHLER: [{args.entry_id}] darf nicht genutzt werden ({grund}). "
                  "Kein lokaler Pfad gesetzt; eine bereits geladene Datei bitte löschen.",
                  file=sys.stderr)
            sys.exit(1)

    entry["download_status"] = args.download_status
    entry["download_timestamp"] = datetime.now(timezone.utc).isoformat()

    if args.local_path:
        entry["local_path"] = args.local_path.replace("\\", "/")
        entry["local_path_type"] = args.local_path_type or infer_type(args.local_path)

    entry["download_error"] = args.error_message or None

    if "meta" in data:
        data["meta"]["last_download"] = entry["download_timestamp"]

    save_findings(findings_path, data)
    print(f"[OK] [{args.entry_id}] -> {args.download_status}", end="")
    if args.local_path:
        print(f"  |  {args.local_path}", end="")
    print()


if __name__ == "__main__":
    main()
