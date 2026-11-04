# topic-research

Themenrecherche für den Eckernkamp-Kompass, Version 3.1. Sucht erschöpfend nach Studien, Interviews,
Datensätzen und Grauer Literatur und schreibt `suchprotokoll_<thema>.md` und
`findings_<thema>.json`. Die rechtliche Prüfung der Quellen übernimmt danach
[`source-compliance-check`](../source-compliance-check/README.md) in einem frischen Subagenten.

## Inhalt

```
topic-research/
├── SKILL.md                         Pipeline Phase 0 bis 7
├── references/
│   ├── plattformen-und-apis.md      Plattformen, APIs, MCP-Tools, Fallbacks, Thesaurus-Muster
│   └── findings-schema.md           JSON-Schema für alle Skills (einzige maßgebliche Fassung)
├── scripts/
│   └── validate_findings.py         validiert findings.json, --stage research | compliance
└── evals/
    └── evals.json                   Eval 0: vollständiger Lauf
```

## Ablauf

| Phase | Inhalt |
|---|---|
| 0 bis 4 | Themen-Analyse, Facetten, Thesaurus, Suche (breit, qualitativ, Snowballing, Praxis), Selektion |
| 5 | Findings erfassen, mit `--stage research` validieren |
| 6 | Subagent mit `source-compliance-check` starten |
| 7 | Suchprotokoll schreiben, mit `--stage compliance` abschließend validieren |

## Validator

```bash
python .claude/skills/topic-research/scripts/validate_findings.py findings_thema.json --stage research
python .claude/skills/topic-research/scripts/validate_findings.py findings_thema.json   # Vorgabe: compliance
python .claude/skills/topic-research/scripts/validate_findings.py findings_thema.json --strict
```

Nur Python-Standardbibliothek, keine Installation.

## Änderungen gegenüber Version 2.0

- Rechteprüfung in eigenen Skill `source-compliance-check` ausgelagert
- Archetypen und Facetten domänenneutral formuliert, Radverkehrs-Thesaurus nur noch als eines von
  zwei Mustern
- Facette C auf die indirekt Betroffenen geschärft
- Deduplizierung Preprint gegen Publikation, Vorwärts- und Rückwärts-Snowballing mit konkreten
  Parametern
- Lizenzfelder je API dokumentiert, inklusive der `bronze`-Falle
- neues Feld `pruefhinweise` für Fundstellen, die der Rechteprüfung Suchzeit sparen

Die Vorgängerfassung 2.0 liegt im Git-Commit `06f5880`.
