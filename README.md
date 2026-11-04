# DataFetch

Claude Code skills that research sources for a topic of the Eckernkamp-Kompass (SHIFT), check
each source for licence and data-protection issues, and turn the usable ones into downloads,
stakeholder maps and requirements.

## 1. The pipeline

```
project.md / topic
      │
      ▼
topic-research ───────────▶ suchprotokoll_<thema>.md, findings_<thema>.json
      │  (starts in a fresh subagent)
      ▼
source-compliance-check ──▶ licence and GDPR verdict per source and attachment,
      │                     rechtebericht_<thema>.md
      ▼
daten-download ───────────▶ data/raw/<thema>/, download_report_<thema>.md
stakeholder-analyse ──────▶ stakeholder_<thema>.md / .json
      │
      ▼
requirements-analyse ─────▶ requirements.md with fictional personas
```

| Skill | What it does |
|---|---|
| [`topic-research`](.claude/skills/topic-research/SKILL.md) | Exhaustive search for studies, interviews, datasets and grey literature; writes the search protocol and the findings file. |
| [`source-compliance-check`](.claude/skills/source-compliance-check/SKILL.md) | Licence check per use (N1 embedding, N2 showing passages, N3 reusing attachments), condensed to a release class `K2` / `K1` / `K0`, plus a separate GDPR check for personal data. |
| [`daten-download`](.claude/skills/daten-download/SKILL.md) | Downloads the sources and attachments that may be used, scans full texts for participant quotes. |
| [`stakeholder-analyse`](.claude/skills/stakeholder-analyse/SKILL.md) | Derives stakeholder groups, a power-interest matrix and gaps from the usable sources. |
| [`requirements-analyse`](.claude/skills/requirements-analyse/SKILL.md) | Turns `project.md` and the stakeholder map into requirements and fictional personas. |

Claude Code picks a skill up automatically from the request ("Recherche für den Kompass zu
ÖPNV", "Stakeholder ableiten", …), or you call it by name, e.g. `/topic-research`.

## 2. Which sources may be used

Licence and data protection are two independent verdicts. Every downstream skill combines them with
one rule, defined in [`findings-schema.md`, section 3.4](.claude/skills/topic-research/references/findings-schema.md)
and implemented once in [`nutzungsregel.py`](.claude/skills/daten-download/scripts/nutzungsregel.py):

| Release class | GDPR verdict | Result |
|---|---|---|
| `K1` or `K2` | `kein_personenbezug` | used |
| `K1` or `K2` | `zweifelhaft` or `ausstehend` (check not done yet) | waits for review |
| `K1` or `K2` | `personenbezogen` or `nicht_pruefbar` | blocked |
| `K0`, missing or unknown | any | blocked |
| listed in `meta.aussortiert` | any | blocked |

A source without a licence is `K0` even if a statutory exception would allow analysis. Each data
attachment is judged on its own verdicts. How a delivering RAG system has to enforce the classes
is described in [`docs/freigabeklassen-ausgabe.md`](docs/freigabeklassen-ausgabe.md).

## 3. Search tools

Scholarly databases are queried directly over their REST APIs (OpenAlex, Crossref, Semantic
Scholar, Zenodo, arXiv), so every query, page and hit count lands in the protocol. MCP servers,
configured in [`.mcp.json`](.mcp.json), cover the rest; all of them can be used for free:

| Server | Use | Key |
|---|---|---|
| `tavily` | grey literature with domain filter, mapping and crawling institution sites | `TAVILY_API_KEY` (free, 1,000 credits/month) |
| `exa`, `parallel` | additional web search indexes, semantic search for similar studies | none |
| `fetch` | reads a page verbatim as Markdown, respects robots.txt | none |
| `duckduckgo` | fallback web search | none |
| `paper-search` | BASE, CORE, OpenAIRE, DOAJ, Europe PMC | optional `OPENALEX_API_KEY`, `CORE_API_KEY` |

Details, fallbacks and which tool counts as evidence:
[`plattformen-und-apis.md`](.claude/skills/topic-research/references/plattformen-und-apis.md).

## 4. Setup (Windows)

Requirements: Python 3.10 or newer, Node.js (for `npx`), [uv](https://docs.astral.sh/uv/) (for `uvx`).

1. Set the keys as environment variables, never in files. Only the Tavily key is required.
   ```bash
   setx TAVILY_API_KEY "tvly-..."
   ```
   ```bash
   setx OPENALEX_API_KEY "..."
   ```
2. Quit and restart the Claude app (or terminal) completely, then approve the servers from
   `.mcp.json` when Claude Code asks.
3. Check the setup:
   ```bash
   python test_mcp_connections.py
   ```
   In a session, `/mcp` shows which servers are connected.

The download report needs `pypdf` (`pip install pypdf`); everything else uses the Python standard
library only.

## 5. Checking results

```bash
python .claude/skills/topic-research/scripts/validate_findings.py findings_<thema>.json --stage research
```
```bash
python .claude/skills/topic-research/scripts/validate_findings.py findings_<thema>.json
```
```bash
python .claude/skills/source-compliance-check/scripts/test_robots_parser.py
```

A complete, valid example of a findings file after both checks is
[`beispiel_findings.json`](.claude/skills/source-compliance-check/evals/beispiel_findings.json).
The evals for both research skills are in each skill's `evals/` folder.

## 6. Repository layout

```
.claude/skills/        the five skills
docs/                  notes for systems that consume the results
.mcp.json              MCP servers (no keys)
test_mcp_connections.py
data/, scratch/, Projekte/   local working data, not versioned
```
