---
name: requirements_analyse
description: >
  Erstellt aus einer Projektbeschreibung (project.md) und einer Stakeholder-Analyse
  (stakeholder.json oder stakeholder.md) eine strukturierte requirements.md.
  Leitet funktionale/nicht-funktionale Anforderungen, Restriktionen und Evaluierungsfragen
  ab, identifiziert die 3 bis 5 wichtigsten Stakeholder und erstellt prägnante Personas.
  Trigger-Phrasen: "Requirements erstellen", "Anforderungen analysieren",
  "requirements.md generieren", "Personas aus Stakeholdern erstellen", "Projektanforderungen ableiten".
---

# Skill: Anforderungen & Persona-Analyse (requirements_analyse)

## Ziel
Aus einer **`project.md`** (Projektbeschreibung) und vorhandenen Stakeholder-Daten (**`stakeholder.json`** oder **`stakeholder.md`**) eine strukturierte, vollständige und maschinenlesbare **`requirements.md`** erstellen. Die Anforderungsdatei verbindet die fachlich-technischen Projektanforderungen mit konkret ausgearbeiteten **Personas** der wichtigsten Stakeholder.

---

## Voraussetzung & Inputs

Bevor die Analyse gestartet wird, prüfen ob folgende Dateien im Zielprojektordner existieren:
1. `project.md` – Projektbeschreibung, Zielsetzung, Rahmenbedingungen, Datenquellen
2. `stakeholder.json` oder `stakeholder.md` – Konsolidierte Stakeholder-Liste, Power-Interest-Matrix, Interessen & Belege

Falls Dateien fehlen: Den Benutzer darauf hinweisen, welche Datei fehlt bzw. zuerst den `stakeholder_analyse`-Skill auszuführen.

---

## Workflow

### Phase 1: Input-Analyse & Datenaufnahme

1. Lies `project.md` vollständig ein.
2. Lies `stakeholder.json` bzw. `stakeholder.md` vollständig ein.
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
- **Name & Alter:** Realistischer Name und repräsentatives Alter
- **Rolle / Beruf:** Genaue Funktionsbezeichnung oder Nutzertypus (z. B. Alltags-Radpendler, Verkehrsplanerin Tiefbauamt, Lastenrad-Gewerbetreibender)
- **Kern-Zitat:** Ein prägnanter Satz, der die Einstellung der Persona zum Projekt auf den Punkt bringt
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
   - **Demografie & Hintergrund:** ...
   - **Zitat:** "..."
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
- [ ] Jede Persona enthält Name, Alter, Rolle, Zitat, Hintergrund, Ziele, Pain Points und Anforderungen
- [ ] Traceability-Matrix verbindet Personas mit den konkreten Systemanforderungen
- [ ] `requirements.md` wurde erfolgreich im Projektordner gespeichert
