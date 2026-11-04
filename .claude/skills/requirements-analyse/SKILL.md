---
name: requirements-analyse
description: >
  Erstellt aus einer Projektbeschreibung (project.md) und einer Stakeholder-Analyse
  (stakeholder_<thema>.json oder .md aus stakeholder-analyse) eine strukturierte
  requirements.md. Leitet funktionale/nicht-funktionale Anforderungen, Restriktionen und
  Evaluierungsfragen ab, identifiziert die 3 bis 5 wichtigsten Stakeholder und erstellt
  fiktive Personas. Belegt wird nur mit Quellen, die nach der Rechteprüfung genutzt werden
  dürfen; keine echten Personen und keine personenbezogenen Daten in den Personas.
  Trigger-Phrasen: "Requirements erstellen", "Anforderungen analysieren",
  "requirements.md generieren", "Personas aus Stakeholdern erstellen", "Projektanforderungen ableiten".
---

# Skill: Anforderungen & Persona-Analyse (requirements-analyse)

## Ziel
Aus einer **`project.md`** (Projektbeschreibung) und den Stakeholder-Daten
(**`stakeholder_<thema>.json`** oder **`stakeholder_<thema>.md`**) eine strukturierte,
vollständige und maschinenlesbare **`requirements.md`** erstellen. Die Anforderungsdatei verbindet
die fachlich-technischen Projektanforderungen mit ausgearbeiteten **Personas** der wichtigsten
Stakeholder.

---

## Voraussetzung & Inputs

Bevor die Analyse gestartet wird, prüfen ob folgende Dateien im Zielprojektordner existieren:
1. `project.md` – Projektbeschreibung, Zielsetzung, Rahmenbedingungen, Datenquellen
2. `stakeholder_<thema>.json` oder `stakeholder_<thema>.md` – Konsolidierte Stakeholder-Liste,
   Power-Interest-Matrix, Interessen & Belege

Falls Dateien fehlen: Den Benutzer darauf hinweisen, welche Datei fehlt bzw. zuerst den Skill
`stakeholder-analyse` ausführen.

**Stakeholder-Daten nur aus geprüften Quellen.** Die Stakeholder-Datei muss die Nutzungsregel
ausweisen (`meta.nutzungsregel` und `meta.quellen_ausgeschlossen` in der JSON-Fassung, Abschnitt 0
in der Markdown-Fassung). Fehlt das, stammt sie aus einer Fassung ohne Rechteprüfung: den Benutzer
darauf hinweisen und `stakeholder-analyse` neu ausführen lassen, statt mit ihr weiterzuarbeiten.

---

## Regeln für Belege und Personas

Diese Regeln gelten in allen Phasen. Sie setzen die Nutzungsregel aus
`../topic-research/references/findings-schema.md`, Abschnitt 3.4, für diesen Skill um.

1. **Nur genutzte Quellen als Beleg.** Jede `Beleg / Quelle`-Angabe in den Tabellen ist eine
   Finding-ID aus `belege_finding_ids` der Stakeholder-Datei oder eine Stelle in `project.md`.
   Wird zusätzlich die findings-Datei gelesen, gilt dort dieselbe Nutzungsregel: keine Quelle mit
   Freigabeklasse `K0`, mit Datenschutzbefund `personenbezogen`, `nicht_pruefbar` oder
   `zweifelhaft` oder `ausstehend` und keine aus `meta.aussortiert`.
2. **Personas sind fiktiv.** Eine Persona ist ein Typ, verdichtet aus mehreren Quellen, nie eine
   reale Person. Name, Alter und Lebensumstände werden erfunden und dürfen keiner befragten oder
   in einer Quelle beschriebenen Person entsprechen. Keine Kombination aus Ort, Funktion und
   Merkmalen, die eine echte Person erkennbar macht („Leiterin des Tiefbauamts in X").
3. **Keine personenbezogenen Daten aus den Quellen.** Weder Namen, Zitate noch Details von
   Befragten werden in eine Persona übernommen, auch nicht aus Quellen mit Befund
   `kein_personenbezug`, wenn sie dort einer Einzelperson zugeordnet sind. Das gilt auch für
   Selbstauskünfte von Autorinnen und Autoren (`datenschutz.autor_selbstauskunft`).
4. **Kern-Zitat in eigenen Worten.** Das Zitat einer Persona ist formuliert, nicht kopiert, und
   als sinngemäße Verdichtung gekennzeichnet, mit den Finding-IDs, auf denen es beruht. Ein
   wörtliches Zitat aus einer Quelle nur, wenn es kurz ist, aus einer `K1`- oder `K2`-Quelle
   stammt und mit Quellenangabe steht (§§ 51, 63 UrhG); dann gehört es in die Belege, nicht in
   den Mund der Persona.

---

## Workflow

### Phase 1: Input-Analyse & Datenaufnahme

1. Lies `project.md` vollständig ein.
2. Lies `stakeholder_<thema>.json` bzw. `stakeholder_<thema>.md` vollständig ein und prüfe den
   Nachweis der Nutzungsregel (siehe oben).
3. Extrahiere Kernfakten:
   - **Projektgegenstand & Standort**
   - **Zeitfenster & Takte** (z. B. Hauptverkehrszeiten, Betriebszeiten)
   - **Kosten & Budgetgrenzen** (z. B. Kilometersätze, jährliche Betriebskosten)
   - **Technische & Infrastrukturelle Restriktionen** (z. B. Trassierung, Busspur-Verfügbarkeit, Verkehrsfluss)
   - **Offene Kernfragen & Evaluierungsziele** (z. B. Potenzialanalyse, Umstiegswille, Stellplatzdimensionierung)

---

### Phase 2: Anforderungs-Kategorisierung

Gliedere die extrahierten Informationen in vier Hauptkategorien:

1. **Funktionale Anforderungen (FA):**
   - Was muss das System / die Infrastruktur konkret leisten? (z. B. Mindestbreiten für Lastenräder, sensorbasierte Gefahrenstellenerkennung, Anbindung an Radvorrangrouten, Ausleuchtung).
2. **Nicht-Funktionale Anforderungen & Qualitäten (NFA):**
   - Subjektive Sicherheit, Erschütterungsarmut / Fahrkomfort, Barrierefreiheit, Trennungsqualität zum Kfz-Verkehr, intuitive Verkehrsführung.
3. **Rahmenbedingungen & Restriktionen (RST):**
   - ERA-Regelwerke (Empfehlungen für Radverkehrsanlagen), bauliche Breitenrestriktionen im Straßenraum, Budgetdeckel, behördliche Abstimmungsprozesse.
4. **Zentrale Evaluierungsfragen & Forschungsbedarfe (EV):**
   - Verlagerungspotenzial (Modal Shift), subjektive Sicherheitsgewinne, Routenumwegeakzeptanz, Kosten-Nutzen-Verhältnis.

---

### Phase 3: Auswahl der Top 3–5 Stakeholder

1. Werte die Power-Interest-Matrix aus der Stakeholder-Analyse aus.
2. Identifiziere die **3 bis 5 einflussreichsten und kritischsten Stakeholder** (Typischerweise aus dem Quadranten *Schlüssel-Akteure / High Power - High Interest* sowie die primäre Endnutzer-Zielgruppe).
3. Stelle sicher, dass sowohl Entscheider/Aufgabenträger als auch operative Umsetzer und Endnutzer (Personen-Zielgruppen) vertreten sind.

---

### Phase 4: Persona-Entwicklung

Für jeden der 3–5 ausgewählten Stakeholder wird ein detailliertes Persona-Dossier erstellt.

**Format einer Persona:**
- **Name & Alter:** Erfundener, realistischer Name und repräsentatives Alter (Regel 2)
- **Rolle / Beruf:** Funktionsbezeichnung oder Nutzertypus, allgemein genug, dass keine reale Person gemeint sein kann (z. B. Alltags-Radpendler, Verkehrsplanerin einer Mittelstadt, Lastenrad-Gewerbetreibender)
- **Kern-Zitat:** Ein prägnanter Satz in eigenen Worten, der die Einstellung der Persona zum Projekt auf den Punkt bringt, mit Beleg-IDs (Regel 4)
- **Belege:** Finding-IDs genutzter Quellen, aus denen die Persona verdichtet ist
- **Hintergrund & Demografie:** Woher kommt die Person, tägliche Gewohnheiten, Mobilitätsverhalten
- **Ziele & Motivation:** Was will die Person erreichen? (z. B. stressfrei und sicher zur Arbeit radeln, Erschütterungen vermeiden, Radverkehrsanteil steigern)
- **Pain Points & Frustrationen:** Was befürchtet oder stört die Person? (z. B. zu enge Überholabstände von Kfz, schlechter Belag, fehlende physische Trennung)
- **Erwartungen & Anforderungen an das Projekt:** Konkrete Anforderungen, damit das Projekt für diese Persona ein Erfolg wird

---

### Phase 5: Generierung der `requirements.md`

Speichere die Ergebnisse strukturiert in einer `requirements.md` im Projektordner.

---

## Output-Schema für `requirements.md`

```markdown
# Anforderungsdokumentation & Persona-Analyse: "<Projektname>"

## 1. Projekt-Übersicht & Kontext
   [Kurze Zusammenfassung des Projekts, Standorts und der Ausgangslage]

## 2. Strukturierte Anforderungen
### 2.1 Funktionale Anforderungen (FA)
   | ID | Anforderung | Priorität | Beleg / Quelle |
### 2.2 Nicht-Funktionale Anforderungen (NFA)
   | ID | Anforderung | Priorität | Beleg / Quelle |
### 2.3 Rahmenbedingungen & Restriktionen (RST)
   | ID | Restriktion / Rahmenbedingung | Auswirkung | Quelle |
### 2.4 Zentrale Evaluierungsfragen & Forschungsbedarfe (EV)
   | ID | Fragestellung | Evaluierungsmethode | Quelle |

## 3. Identifizierte Top 3–5 Key Stakeholder
   [Übersichtstabelle der ausgewählten Stakeholder]

## 4. Persona-Dossiers
### Persona 1: [Name] – [Rolle]
   > Fiktive Persona, verdichtet aus F-..., F-... Keine reale Person.
   - **Demografie & Hintergrund:** ...
   - **Zitat (sinngemäß):** "..." (Belege: F-..., F-...)
   - **Ziele & Motivation:** ...
   - **Pain Points & Frustrationen:** ...
   - **Konkrete Projekt-Anforderungen:** ...

[... Personas 2 bis 5 ...]

## 5. Traceability-Matrix (Anforderungen vs. Personas)
   [Matrix: Welche Persona stellt/profitiert von welcher Anforderung]
```

---

## Qualitätssicherung (Checkliste)

- [ ] `project.md` und Stakeholder-Dateien wurden vollständig eingelesen
- [ ] Funktionale, Nicht-Funktionale Anforderungen & Restriktionen sind klar getrennt
- [ ] Mindestens 3 und maximal 5 Stakeholder wurden begründet ausgewählt
- [ ] Stakeholder-Datei weist die Nutzungsregel aus; alle Belege sind genutzte Quellen
- [ ] Jede Persona enthält Name, Alter, Rolle, Zitat, Hintergrund, Ziele, Pain Points, Anforderungen und Belege
- [ ] Personas sind als fiktiv gekennzeichnet; keine reale Person erkennbar, keine Namen, Zitate
      oder Details von Befragten übernommen
- [ ] Kern-Zitate in eigenen Worten; wörtliche Zitate nur kurz, aus K1/K2-Quellen, mit Quellenangabe
- [ ] Traceability-Matrix verbindet Personas mit den konkreten Systemanforderungen
- [ ] `requirements.md` wurde erfolgreich im Projektordner gespeichert
