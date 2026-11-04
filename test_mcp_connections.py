#!/usr/bin/env python3
"""
test_mcp_connections.py
-----------------------
Prüft die Voraussetzungen der Recherche-Skills:
1. OpenAlex API (Wissenschaftsliteratur, mit OPENALEX_API_KEY falls gesetzt)
2. Zenodo API (Datensätze & Transkripte, ohne Schlüssel)
3. Tavily API-Key (für den MCP-Server "tavily" aus .mcp.json)
4. Exa- und Parallel-MCP (gehostet, ohne Schlüssel erreichbar?)
5. npx (startet den Tavily-Server lokal)
6. uvx (startet fetch, duckduckgo und paper-search lokal)

Die Schlüssel werden ausschließlich aus den Umgebungsvariablen TAVILY_API_KEY und
OPENALEX_API_KEY gelesen, nie aus Dateien.

Verwendung:
    python test_mcp_connections.py
"""

import json
import os
import shutil
import urllib.error
import urllib.parse
import urllib.request

UA = "DataFetchConnectionTest/1.0"


def test_openalex(api_key: str) -> tuple[bool, str]:
    url = "https://api.openalex.org/works?search=bicycle+infrastructure&per-page=1"
    if api_key:
        url += "&api_key=" + urllib.parse.quote(api_key)
    hinweis = "" if api_key else " (ohne OPENALEX_API_KEY: kleines Tagesbudget)"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            if results:
                title = results[0].get("title", "Kein Titel")
                return True, f"Erfolgreich! Gefunden: '{title[:50]}...'{hinweis}"
            return False, "Keine Treffer zurückgegeben."
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False, f"HTTP {e.code}: OPENALEX_API_KEY ungültig."
        if e.code == 429:
            return False, f"HTTP 429: Tagesbudget erschöpft{hinweis}."
        return False, f"HTTP Fehler {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Fehler: {e}"


def test_zenodo() -> tuple[bool, str]:
    url = "https://zenodo.org/api/records?q=cycling+dataset&size=1&type=dataset&access_right=open"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            hits = data.get("hits", {}).get("hits", [])
            if hits:
                title = hits[0].get("metadata", {}).get("title", "Kein Titel")
                return True, f"Erfolgreich! Gefunden: '{title[:50]}...'"
            return False, "Keine Datensätze gefunden."
    except Exception as e:
        return False, f"Fehler: {e}"


def test_tavily(api_key: str) -> tuple[bool, str]:
    if not api_key:
        return False, "Umgebungsvariable TAVILY_API_KEY ist nicht gesetzt."

    url = "https://api.tavily.com/search"
    payload = json.dumps({
        "query": "bicycle infrastructure safety",
        "search_depth": "basic",
        "max_results": 2
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": UA
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            if results:
                top_hit = results[0]
                return True, f"Erfolgreich! Top-Hit: '{top_hit.get('title', '')[:50]}...' ({top_hit.get('url', '')})"
            return True, "API erreichbar, aber keine Treffer."
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False, f"HTTP {e.code}: Ungültiger Tavily API-Key."
        return False, f"HTTP Fehler {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Fehler: {e}"


def test_hosted_mcp(url: str) -> tuple[bool, str]:
    """Schickt ein MCP-initialize an einen gehosteten Server und prüft die Antwort."""
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                   "clientInfo": {"name": "DataFetchConnectionTest", "version": "1.0"}}
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "User-Agent": UA
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if "serverInfo" in body:
                return True, "Erreichbar, ohne Schlüssel nutzbar."
            return False, "Antwort ohne serverInfo."
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return False, "HTTP 429: Rate-Limit ohne Schlüssel erreicht, später erneut versuchen."
        return False, f"HTTP Fehler {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Fehler: {e}"


def test_npx() -> tuple[bool, str]:
    path = shutil.which("npx")
    if path:
        return True, f"Gefunden: {path}"
    return False, "npx nicht gefunden. Node.js installieren, sonst startet der Tavily-Server nicht."


def test_uvx() -> tuple[bool, str]:
    path = shutil.which("uvx")
    if path:
        return True, f"Gefunden: {path}"
    return False, "uvx nicht gefunden. uv installieren (docs.astral.sh/uv), sonst starten fetch, duckduckgo und paper-search nicht."


def main():
    checks = [
        ("OpenAlex REST API (Wissenschaftsliteratur)", lambda: test_openalex(os.environ.get("OPENALEX_API_KEY", ""))),
        ("Zenodo REST API (Datensätze & Anhänge)", test_zenodo),
        ("Tavily API-Key (MCP-Server tavily)", lambda: test_tavily(os.environ.get("TAVILY_API_KEY", ""))),
        ("Exa (gehosteter MCP-Server exa)", lambda: test_hosted_mcp("https://mcp.exa.ai/mcp")),
        ("Parallel (gehosteter MCP-Server parallel)", lambda: test_hosted_mcp("https://mcp.parallel.ai/mcp")),
        ("npx (startet den Tavily-Server)", test_npx),
        ("uvx (startet fetch, duckduckgo, paper-search)", test_uvx),
    ]

    print("=" * 70)
    print("      DATAFETCH RECHERCHE & MCP VERBINDUNGSTEST")
    print("=" * 70)

    all_ok = True
    for i, (label, check) in enumerate(checks, 1):
        print(f"\n[{i}/{len(checks)}] Prüfe {label}...")
        ok, msg = check()
        all_ok = all_ok and ok
        status = "[PASS]" if ok else ("[WAIT]" if "nicht gesetzt" in msg else "[FAIL]")
        print(f"      Status: {status} -> {msg}")

    print("\n" + "=" * 70)
    if all_ok:
        print("  ERGEBNIS: ALLE VORAUSSETZUNGEN ERFÜLLT.")
        print("  In Claude Code mit /mcp prüfen, ob alle Server aus .mcp.json verbunden sind.")
    else:
        print("  HINWEIS: Schlüssel als Umgebungsvariablen setzen und Terminal/App neu starten:")
        print('           setx TAVILY_API_KEY "tvly-..."    (Windows, Pflicht)')
        print('           setx OPENALEX_API_KEY "..."       (Windows, empfohlen)')
        print("  Ohne MCP-Server arbeiten die Skills mit eingebauter Websuche weiter.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
