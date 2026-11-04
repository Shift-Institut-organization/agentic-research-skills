#!/usr/bin/env python3
"""
generate_download_report.py
---------------------------
Erstellt einen umfassenden Download- und Qualitätsbericht für den Skill 'daten-download'.
Liest alle gespeicherten Volltexte (PDFs, Berichte) ein, durchsucht sie automatisiert
nach qualitativen O-Tönen und Teilnehmer-Zitaten und dokumentiert die Ergebnisse in
einem strukturierten Markdown-Bericht ('download_report_<thema>.md').

Verwendung:
  python generate_download_report.py [--findings findings.json] [--output report.md]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import pypdf
except ImportError:
    print("[!] FEHLER: 'pypdf' ist nicht installiert. Bitte mit 'pip install pypdf' installieren.")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nutzungsregel import aussortiert_schluessel, nutzungsstatus, quelle_schluessel  # noqa: E402

def find_workspace_root() -> Path:
    current = Path.cwd().resolve()
    for p in [current] + list(current.parents):
        if (p / ".claude").exists() or (p / ".git").exists():
            return p
    return current

WORKSPACE_ROOT = find_workspace_root()

# Regex-Muster für wörtliche Zitate von Studienteilnehmern / Nutzern (z. B. Radfahrenden)
QUOTE_PATTERNS = [
    re.compile(r'["“][^"”]{25,450}["”]\s*\([A-Za-z0-9\s,\-_]+\)', re.DOTALL),
    re.compile(r'\b(Participant|Respondent|Interviewee|Commuter|Cyclist|Bicyclist|User|Stakeholder)\s+([A-Z0-9]+|\([A-Za-z0-9\s]+\))[^.\n]{0,60}[:;]?\s*["“]([^"”]{20,450})["”]', re.IGNORECASE | re.DOTALL),
    re.compile(r'["“]([^"”]{30,450})["”]\s*[-–—]\s*(Participant|Respondent|Commuter|Cyclist|Bicyclist|User|Interviewee)', re.IGNORECASE | re.DOTALL),
    re.compile(r'„([^“]{25,450})“\s*\(([^)]+)\)', re.DOTALL),
    re.compile(r'\b(Ein Befragter|Ein Radfahrender|Eine Radfahrerin|Ein Pendler|Eine Teilnehmerin|Interviewte|Teilnehmer|Befragte|Nutzer)[^.\n]{0,60}[:;]?\s*„([^“]{20,450})“', re.IGNORECASE | re.DOTALL),
]

SECTION_KEYWORDS = [
    "interview findings", "participant comments", "free-text responses",
    "open-ended responses", "qualitative responses", "interview results",
    "qualitative ergebnisse", "befragungsergebnisse", "o-töne", "experteninterviews",
    "focus group findings", "cyclist feedback", "commuter feedback", "nutzerfeedback", "teilnehmerzitate"
]

def scan_pdf_for_quotes(pdf_path: Path, max_quotes: int = 8) -> dict:
    result = {
        "page_count": 0,
        "quotes": [],
        "sections": [],
        "has_quotes": False
    }

    if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
        return result

    try:
        reader = pypdf.PdfReader(str(pdf_path))
        result["page_count"] = len(reader.pages)
    except Exception as e:
        return result

    for page_idx, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            continue

        if not text:
            continue

        page_num = page_idx + 1
        text_lower = text.lower()

        # 1. Spezifische qualitative Abschnitte erkennen
        for kw in SECTION_KEYWORDS:
            if kw in text_lower:
                result["sections"].append((page_num, kw))

        # 2. Direkte Zitate erkennen
        for pat in QUOTE_PATTERNS:
            matches = pat.findall(text)
            for m in matches:
                quote_raw = m if isinstance(m, str) else " | ".join([x for x in m if x])
                quote_clean = " ".join(quote_raw.split())
                # Deduplizieren
                if not any(q[1] == quote_clean for q in result["quotes"]):
                    result["quotes"].append((page_num, quote_clean))
                if len(result["quotes"]) >= max_quotes:
                    break
            if len(result["quotes"]) >= max_quotes:
                break

    result["has_quotes"] = len(result["quotes"]) > 0 or len(result["sections"]) > 0
    return result

def clean_slug(text: str, max_len: int = 30) -> str:
    if not text:
        return "dokument"
    replacements = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue', 'ß': 'ss'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    words = text.strip().split()
    slug = "-".join(words)
    return slug[:max_len].rstrip("-") or "dokument"

def generate_report(findings_path: Path, output_path: Path = None, max_quotes_per_doc: int = 6) -> Path:
    with open(findings_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("meta", {})
    thema = meta.get("thema", "Recherche-Projekt")
    findings = data.get("findings", [])

    if not output_path:
        out_name = f"download_report_{clean_slug(thema)}.md"
        output_path = findings_path.parent / out_name

    # Statistiken
    total_findings = len(findings)
    downloaded_files = []
    skipped_no_oa = 0
    skipped_manual = 0
    failed_downloads = 0
    nicht_genutzt = 0
    aussortiert = aussortiert_schluessel(meta)

    print("=" * 65)
    print("DOWNLOAD-REPORT GENERIERUNG & QUALITATIVE ZITAT-ANALYSE")
    print(f"Thema:    {thema}")
    print(f"Findings: {findings_path.name}")
    print("=" * 65)

    # Scanne alle heruntergeladenen Dokumente
    doc_analyses = []
    scanned_count = 0

    for item in findings:
        fid = item.get("id", "F-???")
        titel = item.get("titel", "Ohne Titel")
        autoren = item.get("autoren", ["Unbekannt"])
        jahr = item.get("jahr", "ND")
        lp = item.get("local_path")
        status = item.get("download_status", "unknown")

        # Nur Quellen, die nach der Nutzungsregel genutzt werden dürfen. Das gilt auch
        # für Dateien, die aus einem früheren Lauf noch lokal liegen.
        if nutzungsstatus(item, quelle_schluessel(item), aussortiert)[0] != "nutzen":
            nicht_genutzt += 1
            continue

        if status == "skipped_no_oa":
            skipped_no_oa += 1
            continue
        elif status == "skipped_manual":
            skipped_manual += 1
            continue
        elif status == "failed":
            failed_downloads += 1
            continue

        if not lp:
            continue

        full_p = WORKSPACE_ROOT / lp
        if not full_p.exists():
            continue

        scanned_count += 1
        print(f"[{scanned_count}] Scanne: {full_p.name} ({full_p.stat().st_size / 1024:.1f} KB)...")

        scan_res = scan_pdf_for_quotes(full_p, max_quotes=max_quotes_per_doc)
        
        doc_analyses.append({
            "id": fid,
            "klasse": (item.get("lizenz") or {}).get("freigabeklasse", "")[:2],
            "title": titel,
            "author": autoren[0] if autoren else "Anon",
            "year": jahr,
            "local_path": lp,
            "file_name": full_p.name,
            "size_kb": full_p.stat().st_size / 1024,
            "page_count": scan_res["page_count"],
            "quotes": scan_res["quotes"],
            "sections": scan_res["sections"],
            "has_quotes": scan_res["has_quotes"]
        })

    docs_with_quotes = [d for d in doc_analyses if len(d["quotes"]) > 0]
    docs_with_sections = [d for d in doc_analyses if len(d["sections"]) > 0 and len(d["quotes"]) == 0]

    # Markdown Report aufbauen
    md = []
    md.append(f"# Download- & Zitat-Prüfbericht: {thema}\n")
    md.append(f"> **Erstellt am:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
    md.append(f"> **Quell-Datei:** `{findings_path.name}`  ")
    md.append(f"> **Speicherort Volltexte:** `data/raw/{clean_slug(thema)}/`\n")
    md.append("---\n")

    # 1. Executive Summary & Kennzahlen
    md.append("## 1. Download-Statistiken\n")
    md.append("| Kennzahl | Wert | Beschreibung |")
    md.append("|---|---|---|")
    md.append(f"| **Gesamte Findings** | {total_findings} | Erfasste Quellen im Suchprotokoll |")
    md.append(f"| **Erfolgreich lokal gesichert** | {len(doc_analyses)} | Volltexte & Reports lokal verfügbar |")
    md.append(f"| **Davon mit direkten O-Tönen/Zitaten** | **{len(docs_with_quotes)}** | **Enthalten wörtliche Aussagen von Studienteilnehmern/Nutzern (z. B. Radfahrenden)** |")
    md.append(f"| **Mit qualitativen Abschnitten** | {len(docs_with_sections)} | Enthalten qualitative Methodik-/Befragungsabschnitte |")
    md.append(f"| **Übersprungen (kein Open Access)** | {skipped_no_oa} | Paywall-Arbeiten (Metadaten & Abstract gesichert) |")
    md.append(f"| **Übersprungen (manuell)** | {skipped_manual} | Manuell durch `download: false` markiert |")
    md.append(f"| **Fehlgeschlagen (abgelehnt)** | {failed_downloads} | Konnten auch via Repositorien nicht geladen werden |")
    md.append(f"| **Nicht genutzt (Rechteprüfung)** | {nicht_genutzt} | K0, Personenbezug, nicht prüfbar, aussortiert oder Review offen; nicht gescannt |\n")
    md.append("---\n")

    # 2. Qualitative Übersichtstabelle
    md.append("## 2. Übersicht aller geprüften Volltexte\n")
    md.append("| ID | Klasse | Jahr | Erstautor | Kurztitel | Seiten | O-Töne? | Fundstellen | Lokale Datei |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for d in doc_analyses:
        q_status = "✅ Ja" if len(d["quotes"]) > 0 else ("🔍 Sektionen" if len(d["sections"]) > 0 else "Nein")
        q_summary = f"{len(d['quotes'])} Zitate" if d['quotes'] else (f"{len(d['sections'])} Abschnitte" if d['sections'] else "-")
        pages = f"{d['page_count']} S." if d['page_count'] > 0 else "-"
        md.append(f"| **{d['id']}** | {d['klasse']} | {d['year']} | {d['author']} | {d['title'][:38]}... | {pages} | {q_status} | {q_summary} | `{d['file_name']}` |")
    md.append("\n---\n")

    # 3. Extrahierte Zitate & O-Töne
    md.append("## 3. Extrahierte Teilnehmer-Zitate & O-Töne für Personas & Stakeholder\n")
    md.append("> Nur zur internen Auswertung. Aus K1-Quellen darf nach außen nur kurz und mit "
              "Quellenangabe zitiert werden (§§ 51, 63 UrhG). Personas werden aus den Aussagen "
              "abgeleitet und nicht mit echten Zitaten bestückt, die eine Person erkennbar machen.\n")
    if not docs_with_quotes:
        md.append("_In den geprüften Volltexten wurden keine wörtlichen Teilnehmer-Zitate nach dem Standard-Attributionsmuster gefunden._\n")
    else:
        for d in docs_with_quotes:
            md.append(f"### 📄 [{d['id']}] {d['year']} - {d['author']}: *{d['title']}*")
            md.append(f"- **Datei:** `[{d['file_name']}](file:///{WORKSPACE_ROOT.as_posix()}/{d['local_path']})` ({d['size_kb']:.1f} KB, {d['page_count']} Seiten)")
            md.append(f"- **Gefundene Zitate ({len(d['quotes'])}):**\n")
            for pno, q in d["quotes"]:
                md.append(f"> „{q}“  \n> — **Seite {pno}**\n")
            if d["sections"]:
                sec_list = ", ".join([f"S. {s[0]} ('{s[1]}')" for s in d["sections"][:4]])
                md.append(f"- **Erkannte qualitative Abschnitte:** {sec_list}\n")
            md.append("")

    if docs_with_sections:
        md.append("### 🔍 Dokumente mit qualitativen Abschnitten (Methodik / Befragung)")
        for d in docs_with_sections:
            sec_list = ", ".join([f"S. {s[0]} ('{s[1]}')" for s in d["sections"][:3]])
            md.append(f"- **[{d['id']}]** `{d['file_name']}`: {sec_list}")
        md.append("\n")

    # 4. Empfehlungen für Stakeholder-Analyse
    md.append("---\n")
    md.append("## 4. Empfehlungen für die Stakeholder-Analyse (`stakeholder-analyse`)\n")
    if docs_with_quotes:
        top_doc = docs_with_quotes[0]
        md.append(f"1. **Primärquelle für Personas:** Das Dokument **[{top_doc['id']}]** (`{top_doc['file_name']}`) bietet O-Töne von Nutzern, Radfahrenden und Betroffenen. Sie belegen Ziele und Pain Points der Personas; als Kern-Zitat einer Persona dienen sie nur sinngemäß, mit Beleg-ID.")
    md.append("2. **Praxisberichte & Kommunalrichtlinien:** Dokumente aus `reports/` (z. B. Difu, UBA, ACE) enthalten institutionelle Stakeholder-Anforderungen und organisatorische Reibungspunkte.")
    md.append("3. **Stichproben-Abgleich:** Die in `findings.json` gepflegten Stichprobengrößen (`qualitative_daten.stichprobengroesse`) bilden die empirische Grundlage für die quantitative Priorisierung in der Stakeholder-Map.\n")

    # Schreiben
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("\n" + "=" * 65)
    print(f"BERICHT ERFOLGREICH GENERIERT:")
    print(f"📄 Datei: {output_path}")
    print(f"📊 Geprüfte Volltexte: {len(doc_analyses)}")
    print(f"💬 Dokumente mit Zitaten: {len(docs_with_quotes)}")
    print("=" * 65)
    return output_path

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Erstellt einen Download- & Zitat-Prüfbericht für Volltexte.")
    parser.add_argument("--findings", "-f", type=str, help="Pfad zur findings_<thema>.json Datei")
    parser.add_argument("--output", "-o", type=str, help="Ausgabepfad für den Markdown-Bericht")
    parser.add_argument("--max-quotes", "-m", type=int, default=6, help="Maximale Zitate pro PDF (Standard: 6)")
    args = parser.parse_args()

    if args.findings:
        findings_path = Path(args.findings).resolve()
    else:
        cwd = Path.cwd()
        candidates = list(cwd.glob("findings*.json")) or list(cwd.glob("**/findings*.json"))
        if not candidates:
            print("[!] Keine findings.json gefunden. Bitte mit -f angeben.")
            sys.exit(1)
        findings_path = candidates[0].resolve()

    out_p = Path(args.output).resolve() if args.output else None
    generate_report(findings_path, output_path=out_p, max_quotes_per_doc=args.max_quotes)

if __name__ == "__main__":
    main()
