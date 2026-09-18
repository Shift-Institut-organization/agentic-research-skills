---
name: stakeholder_analyse
description: >
  Leitet aus einer findings.json-Datei (produziert vom suchprotokoll_recherche-Skill)
  alle relevanten Stakeholder eines Themas ab. Kategorisiert, priorisiert und
  erstellt eine vollständige Stakeholder-Map mit Interessenkonflikten und
  Engagement-Empfehlungen. Trigger-Phrasen: "Stakeholder ableiten",
  "Stakeholder-Analyse", "Stakeholder-Map erstellen", "Wer sind die Stakeholder",
  "stakeholder mapping", "Interessengruppen analysieren".
---

# Skill: Stakeholder-Analyse aus Forschungsdaten

## Ziel
Aus einer **`findings_<thema>.json`** (erstellt vom `suchprotokoll_recherche`-Skill)
alle identifizierbaren Stakeholder systematisch ableiten, kategorisieren und als
priorisierte Stakeholder-Map ausgeben.

---

## Voraussetzung: Input-Datei

Vor dem Start prüfen ob eine `findings_*.json` im Arbeitsverzeichnis existiert.
Falls nicht: Benutzer darauf hinweisen, zuerst den `suchprotokoll_recherche`-Skill
auszuführen.

**Lies die Datei vollständig** mit dem `view_file`-Tool.
Vollständige Feldbeschreibung des Schemas: `references/findings_schema.md`

---

## Workflow

### Phase 0: Datei einlesen & Lagebild erstellen

1. findings.json öffnen und alle Einträge lesen
2. Erstelle ein kurzes **Lagebild**:
   - Anzahl Quellen gesamt
   - Verteilung nach `quelle_typ` (journal, dataset, report, …)
   - Häufigste `methodik`-Typen
   - Häufigste `laender_regionen`
   - Vollständigkeit: Felder mit fehlenden Werten identifizieren

---

### Phase 1: Rohe Stakeholder-Extraktion

Gehe **jeden Eintrag** in `findings` durch und extrahiere:

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
    "erstellungsdatum": "ISO-8601"
  },
  "stakeholder": [
    {
      "id": "SH-001",
      "name": "string",
      "kategorie": "primaer | sekundaer" | "tertiaer",
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

- [ ] Alle findings.json-Einträge wurden gelesen
- [ ] Rohe Extraktion deckt alle 4 relevanten Felder ab
- [ ] Konsolidierung: keine semantischen Duplikate mehr
- [ ] Mindestens 8 verschiedene Stakeholder-Typen identifiziert
- [ ] Power-Interest-Matrix vollständig befüllt
- [ ] Lückenanalyse enthält mind. 3 konkrete Empfehlungen
- [ ] stakeholder_<thema>.md gespeichert
- [ ] stakeholder_<thema>.json gespeichert

---

## Referenzen

- findings.json Schema: `references/findings_schema.md`
- Stakeholder-Framework: `references/stakeholder_framework.md`
