---
name: stakeholder-analyse
description: >
  Leitet aus einer geprüften findings_<thema>.json (topic-research, dann
  source-compliance-check) alle relevanten Stakeholder eines Themas ab. Nutzt nur Quellen,
  die nach der Rechteprüfung genutzt werden dürfen: keine Quellen mit Freigabeklasse K0,
  keine mit personenbezogenen oder nicht prüfbaren Daten, keine aussortierten. Kategorisiert,
  priorisiert und erstellt eine Stakeholder-Map mit Interessenkonflikten und
  Engagement-Empfehlungen. Trigger-Phrasen: "Stakeholder ableiten",
  "Stakeholder-Analyse", "Stakeholder-Map erstellen", "Wer sind die Stakeholder",
  "stakeholder mapping", "Interessengruppen analysieren".
---

# Skill: Stakeholder-Analyse aus Forschungsdaten

## Ziel
Aus einer geprüften **`findings_<thema>.json`** alle identifizierbaren Stakeholder
systematisch ableiten, kategorisieren und als priorisierte Stakeholder-Map ausgeben.

---

## Voraussetzung: Input-Datei

1. Prüfen, ob eine `findings_*.json` im Arbeitsverzeichnis existiert. Falls nicht: zuerst den
   Skill `topic-research` ausführen.
2. Prüfen, ob die Rechteprüfung abgeschlossen ist: `meta.lizenz_geprueft` und
   `meta.dsgvo_geprueft` gesetzt. Falls nicht: zuerst `source-compliance-check` ausführen.
   **Ohne Rechteprüfung keine Analyse**, auch nicht vorläufig.

**Lies die Datei vollständig** mit dem Read-Werkzeug. Schema:
`../topic-research/references/findings-schema.md` (einzige maßgebliche Schemabeschreibung).

---

## Nutzungsregel: Welche Quellen in die Analyse eingehen

Lizenz und Datenschutz sind zwei getrennte Urteile. In die Analyse geht eine Quelle nur ein,
wenn beide sie zulassen (`findings-schema.md`, Abschnitt 3.4):

| `lizenz.freigabeklasse` | `datenschutz.befund` | In der Analyse |
|---|---|---|
| `K1` oder `K2` | `kein_personenbezug` | ja |
| `K1` oder `K2` | `zweifelhaft` oder `ausstehend` | nein, bis das Review entschieden hat oder die Prüfung nachgeholt ist |
| `K1` oder `K2` | `personenbezogen` oder `nicht_pruefbar` | nein |
| `K0`, fehlend oder unbekannt | beliebig | nein |
| Quelle steht in `meta.aussortiert` | beliebig | nein |

Ausgeschlossene Quellen werden **gar nicht** ausgewertet, auch nicht ihre Metadaten,
Zielgruppen oder Institutionen. Sie erscheinen nur gezählt im Lagebild und mit ID in der
Liste der ausgeschlossenen Quellen, damit sichtbar bleibt, was fehlt.

Zusätzlich gilt für die Arbeit mit Inhalten:
- **Keine identifizierbaren Personen.** Stakeholder sind Gruppen und Organisationen, nie
  einzelne Befragte. Rollen, die eine einzelne Person erkennbar machen („die Leiterin des
  Tiefbauamts in X"), werden auf die Gruppe verallgemeinert („kommunale Verkehrsplanung").
- **Selbstauskünfte von Autorinnen und Autoren** (`datenschutz.autor_selbstauskunft`, etwa ein
  Positionality-Absatz) werden nicht ausgewertet.
- **Zitate aus `K1`-Quellen** nur kurz, als Beleg und mit Quellenangabe (§§ 51, 63 UrhG). Sonst
  in eigenen Worten wiedergeben.

---

## Workflow

### Phase 0: Datei einlesen, filtern & Lagebild erstellen

1. findings-Datei öffnen und alle Einträge lesen
2. Die Nutzungsregel auf jeden Eintrag anwenden und die nutzbaren Quellen bestimmen. Für eine
   große Datei die Regel per Skript anwenden statt von Hand:
   ```bash
   python -c "import json,sys; sys.path.insert(0,'.claude/skills/daten-download/scripts'); from nutzungsregel import *; d=json.load(open('findings_<thema>.json',encoding='utf-8')); a=aussortiert_schluessel(d['meta']); [print(f['id'], *nutzungsstatus(f, quelle_schluessel(f), a)) for f in d['findings']]"
   ```
3. Erstelle ein kurzes **Lagebild**:
   - Anzahl Quellen gesamt, davon genutzt, gesperrt und wartend auf Review
   - Verteilung nach `quelle_typ` (journal, dataset, report, …)
   - Häufigste `methodik`-Typen
   - Häufigste `laender_regionen`
   - Vollständigkeit: Felder mit fehlenden Werten identifizieren

---

### Phase 1: Rohe Stakeholder-Extraktion

Gehe **jeden genutzten Eintrag** in `findings` durch und extrahiere:

| findings-Feld | Was es liefert |
|---------------|---------------|
| `zielgruppen_genannt` | Direkte Stakeholder-Hinweise |
| `institutionen_genannt` | Organisationen, Behörden, NGOs |
| `autoren` | Forschungseinrichtungen (Affiliations aus DOI/Metadaten) |
| `abstract_kurzfassung` | Implizite Stakeholder im Kontext |
| `laender_regionen` | Geographische Stakeholder-Kontexte |
| `methodik` | Stakeholder-Typ-Hinweis (z. B. "qualitative_interviews" → es wurden echte Personen befragt) |

Erstelle eine **rohe Stakeholder-Liste** (unsortiert, mit Duplikaten):
```
[Quelle-ID] → [Stakeholder/Gruppe] → [Kontext/Beleg]
```

---

### Phase 2: Konsolidierung & Deduplizierung

Fasse semantisch gleiche Einträge zusammen:
- "Städte", "Kommunen", "Stadtverwaltung" → **Kommunale Behörden**
- "Radfahrende", "Cyclist", "Bicyclist" → **Radfahrende / Cyclist**
- "Ältere Menschen", "Elderly", "Senior citizens" → **Ältere Bevölkerung**

Ergebnis: **Konsolidierte Stakeholder-Liste** mit Häufigkeit (aus wie vielen
Quellen erwähnt) und Belegs-IDs.

---

### Phase 3: Kategorisierung nach Framework

Ordne jeden konsolidierten Stakeholder einer Kategorie zu:

```
PRIMÄR – Direkt betroffen / Endnutzer
  → Menschen/Gruppen, die das Thema direkt erfahren
  → Leistungserbringer, die direkt handeln
  → Beispiele: Radfahrende, Patient*innen, Schüler*innen

SEKUNDÄR – Institutionell / Entscheidend
  → Behörden & Politik (Regulierung, Finanzierung)
  → Forschung & Bildung (Wissensproduktion)
  → NGOs & Verbände (Interessenvertretung)
  → Finanziers & Fördergeber

TERTIÄR – Indirekt / Kontextuell
  → Wirtschaft & Industrie
  → Medien & Öffentlichkeit
  → Internationale Organisationen
  → Technologieanbieter / Plattformen
```

---

### Phase 4: Stakeholder-Mapping-Matrix

Erstelle eine vollständige Tabelle für jeden Stakeholder:

| # | Stakeholder | Kategorie | Interesse am Thema | Mögliche Konflikte | Belege (findings IDs) | Engagement-Empfehlung |
|---|-------------|-----------|-------------------|--------------------|-----------------------|-----------------------|

**Interesse am Thema:** Was will dieser Stakeholder erreichen/verhindern?
**Mögliche Konflikte:** Wo könnte dieser Stakeholder mit anderen kollidieren?
**Belege:** IDs aus findings.json, die diesen Stakeholder nennen
**Engagement-Empfehlung:** Interview, Fokusgruppe, Umfrage, Desk Research?

---

### Phase 5: Priorisierung (Power-Interest-Matrix)

Platziere jeden Stakeholder auf einer **Power-Interest-Matrix**:

```
         │  Hohes Interesse
         │
  Hohe   │  [SCHLÜSSEL-AKTEURE]     [HALTEN & INFORMIEREN]
  Macht  │   → aktiv einbinden        → regelmäßig updaten
         │
  ───────┼──────────────────────────────────────────────────
         │
  Geringe│  [BEOBACHTEN]            [INFORMIEREN]
  Macht  │   → im Auge behalten       → gelegentlich informieren
         │
                Geringes Interesse
```

Erstelle eine Tabelle mit Zuordnung und Begründung.

---

### Phase 6: Lückenanalyse

Identifiziere:
1. **Unterrepräsentierte Stakeholder:** Wer fehlt in den Quellen, ist aber
   offensichtlich relevant?
2. **Methodische Lücken:** Welche Stakeholder-Gruppen wurden in den Studien
   *nicht* befragt (obwohl sie sollten)?
3. **Geographische Lücken:** Regionen ohne Quellen, aber mit thematischer Relevanz?

---

## Output-Format

**Zwei Dateien** im Arbeitsverzeichnis:

### 1. `stakeholder_<thema>.md` — Vollständige Stakeholder-Map

```
# Stakeholder-Analyse: "<Thema>"
*Basierend auf: findings_<thema>.json (<N> Quellen)*

## 0. Lagebild der Datenbasis
   [Übersicht über Quellen, Methoden, Geographien]
   [Genutzt / gesperrt / wartend auf Review, mit den IDs der nicht genutzten Quellen
    und dem Hinweis, dass sie nach der Nutzungsregel ausgeschlossen sind]

## 1. Rohe Stakeholder-Extraktion
   [Tabelle: Quelle → Stakeholder → Kontext]

## 2. Konsolidierte Stakeholder-Liste
   [Mit Häufigkeit und Quell-IDs]

## 3. Stakeholder-Kategorien
   [Primär / Sekundär / Tertiär mit Beschreibung]

## 4. Stakeholder-Mapping-Matrix
   [Vollständige Tabelle]

## 5. Power-Interest-Matrix
   [Tabelle + ASCII-Visualisierung]

## 6. Lückenanalyse & Empfehlungen
   [Fehlende Stakeholder + Methoden-Empfehlungen]

## 7. Priorisierte Top-10 Stakeholder für Interviews/Fokusgruppen
```

### 2. `stakeholder_<thema>.json` — Strukturierte Daten für Tools

```json
{
  "meta": {
    "thema": "string",
    "findings_basis": "findings_<thema>.json",
    "quellen_count": 0,
    "quellen_genutzt": 0,
    "quellen_ausgeschlossen": {
      "gesperrt": ["F-003"],
      "warten_auf_review": ["F-011"]
    },
    "nutzungsregel": "findings-schema.md, Abschnitt 3.4",
    "erstellungsdatum": "ISO-8601"
  },
  "stakeholder": [
    {
      "id": "SH-001",
      "name": "string",
      "kategorie": "primaer | sekundaer | tertiaer",
      "macht": "hoch | mittel | niedrig",
      "interesse": "hoch | mittel | niedrig",
      "prioritaet": "schluessel | halten_informieren | beobachten | informieren",
      "interesse_beschreibung": "string",
      "konfliktpotenzial": "string",
      "belege_finding_ids": ["string"],
      "haeufigkeit_in_quellen": 0,
      "engagement_empfehlung": "interview | fokusgruppe | umfrage | desk_research",
      "notizen": "string"
    }
  ],
  "luecken": {
    "fehlende_stakeholder": ["string"],
    "methodische_luecken": ["string"],
    "geographische_luecken": ["string"]
  }
}
```

---

## Qualitätssicherung (Checkliste)

- [ ] Rechteprüfung war abgeschlossen (`meta.lizenz_geprueft`, `meta.dsgvo_geprueft`)
- [ ] Nutzungsregel angewandt: keine Quelle mit `K0`, `personenbezogen`, `nicht_pruefbar`,
      `zweifelhaft`, `ausstehend` oder aus `meta.aussortiert` ausgewertet
- [ ] `belege_finding_ids` enthalten nur genutzte Quellen
- [ ] Keine einzelne Person identifizierbar, nur Gruppen und Organisationen
- [ ] Ausgeschlossene Quellen in Lagebild und `meta.quellen_ausgeschlossen` aufgeführt
- [ ] Alle genutzten Einträge wurden gelesen
- [ ] Rohe Extraktion deckt alle 4 relevanten Felder ab
- [ ] Konsolidierung: keine semantischen Duplikate mehr
- [ ] Mindestens 8 verschiedene Stakeholder-Typen identifiziert
- [ ] Power-Interest-Matrix vollständig befüllt
- [ ] Lückenanalyse enthält mind. 3 konkrete Empfehlungen
- [ ] stakeholder_<thema>.md gespeichert
- [ ] stakeholder_<thema>.json gespeichert

---

## Referenzen

- Schema und Nutzungsregel: `../topic-research/references/findings-schema.md` (Abschnitt 3.4)
- Nutzungsregel als Code: `../daten-download/scripts/nutzungsregel.py`
- Die Ergebnisdateien `stakeholder_<thema>.md` und `stakeholder_<thema>.json` sind der Input
  für den Skill `requirements-analyse`.
