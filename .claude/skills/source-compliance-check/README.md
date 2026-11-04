# source-compliance-check

Lizenz- und Datenschutzprüfung für Quellen des Eckernkamp-Kompass, Version 3.1. Läuft im Anschluss an
[`topic-research`](../topic-research/README.md) in einem frischen Subagenten oder eigenständig auf
einer Liste von DOIs und URLs.

## Inhalt

```
source-compliance-check/
├── SKILL.md                            Phase 6 (Lizenz) und Phase 7 (DSGVO)
├── references/
│   ├── lizenzpruefung.md               Normenkette, Prämissen, Opt-out-Erkennung, Entscheidungsbaum
│   └── dsgvo-pruefung.md               Dreikriterientest, Vertrauensvermutung, Red Flags, Art. 9
├── scripts/
│   └── harvest_license_signals.py      sammelt Lizenzfelder, robots.txt und TDM-Signale
└── evals/
    ├── evals.json                      sieben Testfälle, noch nicht ausgeführt
    └── beispiel_findings.json          vollständig ausgefülltes Beispiel
```

Schema und Validator liegen in `topic-research`, weil beide Skills dieselbe Datei beschreiben.

## Die zwei Urteile je Quelle

**Lizenz.** Der Kompass tut mit einer Quelle dreierlei, und die drei Handlungen stehen auf
unterschiedlichen rechtlichen Füßen:

| | Handlung | Rechtliche Einordnung |
|---|---|---|
| `N1` | Volltext in die Vektordatenbank einbetten | Vervielfältigung. Kann von den TDM-Schranken (§ 44b, § 60d UrhG) getragen werden. |
| `N2` | Passagen an Nutzende ausliefern | Öffentliche Wiedergabe. **Von den TDM-Schranken nicht gedeckt.** |
| `N3` | Datenanhänge weiterverwenden | Zusätzlich Datenbankrechte, und immer Phase 7. |

Die drei Befunde werden zu einer **Freigabeklasse** verdichtet: `K2` (Volltext darf gezeigt werden),
`K1` (Analyse, Wiedergabe nur als Zitat), `K0` (keine Nutzung, Vorgabewert). Wie ein ausliefernder
Dienst die Klassen technisch durchsetzen muss, steht in `docs/freigabeklassen-ausgabe.md`.

**Datenschutz.** Quellen mit personenbezogenen Daten werden **aussortiert**, ohne Prüfung von
Rechtsgrundlagen. Maßstab ist aber die Identifizierbarkeit mit *vernünftigerweise anzuwendenden
Mitteln* (ErwGr. 26 DSGVO), nicht die theoretische Denkbarkeit:

- **Erklärten Anonymisierungen wird gefolgt**, wenn eine Erklärung vorliegt, die erklärende Stelle
  qualifiziert ist und die Stichprobe keine Red Flag findet.
- **Widerlegt wird nur durch konkrete Funde** (Red Flags R1 bis R9), nicht durch denkbare Szenarien.
- **Ein Codebook ist keine Schlüsselliste.**
- **Art. 9 schließt nicht aus, sondern verschärft.** Ein anonymes Transkript über Krankheitsverläufe
  enthält keine Gesundheitsdaten im Sinne der DSGVO.

## Skript

```bash
python .claude/skills/source-compliance-check/scripts/harvest_license_signals.py --from-findings findings_thema.json --json signale.json
python .claude/skills/source-compliance-check/scripts/harvest_license_signals.py --doi 10.1145/3145472
```

Nur Python-Standardbibliothek. Das Skript **entscheidet nichts**, es sammelt Signale. Es unterscheidet
strikt zwischen `kein_vorbehalt` (robots.txt abrufbar, nichts gefunden) und `nicht_feststellbar`
(robots.txt nicht abrufbar). Ein nicht abrufbares Signal ist kein negatives Signal.

## Projektprämissen

Stehen in `references/lizenzpruefung.md`, Abschnitt 1, und sind Angaben des Projekts, keine
Feststellungen des Skills:

1. **SHIFT ist Forschungsorganisation i.S.d. § 60d UrhG.** Steht für das Projekt fest. Befunde, die
   § 60d brauchen, tragen `traegt_ohne_60d: false`, weil der Forschungszweck offen bleibt.
2. **Der Kompass wird nicht kommerziell genutzt.** Damit ist die NC-Klausel erfüllt. Befunde, die
   darauf beruhen, tragen `traegt_ohne_nc_praemisse: false`.

Ändert sich eine Prämisse, lässt sich der betroffene Teil des Korpus über diese Felder gezielt
herausfiltern.

## Offene Punkte für die Rechtsprüfung

1. **Ist der produktive Kompass-Einsatz noch wissenschaftliche Forschung** im Sinne von Art. 3
   CDSM-RL? Entscheidet, ob § 60d greift. Der Prüfbericht weist deshalb zweigleisig aus, was auch
   allein über § 44b trägt.
2. **Bleibt die Nutzung nicht kommerziell?** Zu überwachen, ob der Kompass später entgeltlich
   bereitgestellt wird oder überwiegend einem gewerblichen Partner zugutekommt.
3. **Rechtsgrundlage für die bibliographischen Metadaten** (Autorennamen) einmal zentral klären.
4. **Selbstauskünfte von Autorinnen und Autoren** (Positionality) als nicht erfasst zu behandeln, ist
   eine Projektentscheidung vom 2026-11-04. Noch gegenzuprüfen.

## Grenzen

- **Phase 7 stellt Betroffenheit fest, nicht Zulässigkeit.** Offen bleibt allein die Tatsachenfrage,
  wenn sich der Personenbezug nicht sicher beurteilen lässt. Dann `zweifelhaft` und Review-Queue.
- **Der Prüfmaßstab ist nicht juristisch gegengeprüft.** Der Dreikriterientest stammt aus den EDPB
  Guidelines 02/2026 in der Konsultationsfassung; die Randnummern können sich verschieben.
- **Bewusstes Restrisiko:** Eine beim Forschenden verbliebene, nicht veröffentlichte Schlüsselliste
  führt nicht zur Aussortierung. Begründung und Gegenargument in `references/dsgvo-pruefung.md`,
  Abschnitte 7 und 13.1.

## Schnelltest

```bash
python .claude/skills/topic-research/scripts/validate_findings.py .claude/skills/source-compliance-check/evals/beispiel_findings.json
# erwartet: 0 Fehler, 0 Warnungen
```

Die Testfälle in `evals/evals.json` sind noch nicht ausgeführt. Härtetests: Nummer 3 (Agent soll sich
weigern, eine Lizenz zu erfinden), Nummer 4 (anonymisierte Studie mit Gesundheitsdaten bleibt drin),
Nummer 7 (Codebook ist kein Zuordnungsschlüssel).
