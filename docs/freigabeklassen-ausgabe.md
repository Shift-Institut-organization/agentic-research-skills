# Freigabeklassen: Anforderungen an das ausliefernde System

Hinweis an die Entwicklung. Diese Datei gehört **nicht** zu einem Skill: Die Recherche-Skills
vergeben die Freigabeklasse, durchsetzen muss sie das System, das den Korpus an Nutzende ausliefert
(RAG- bzw. Vektordatenbank mit Ausgabeinterface). Herkunft: `source-compliance-check`,
`references/lizenzpruefung.md`, Abschnitt 6.

## Die drei Klassen

Jede Quelle trägt nach der Lizenzprüfung genau eine Klasse im Feld `lizenz.freigabeklasse` der
`findings_<thema>.json`:

| Klasse | Bedeutung |
|---|---|
| `K2_volltextwiedergabe` | Chunking **und** Volltextwiedergabe zulässig |
| `K1_analyse_und_zitat` | Chunking zulässig, Wiedergabe **nur im Rahmen des Zitatrechts** (§ 51 UrhG) |
| `K0_keine_freigabe` | Weder Chunking noch Wiedergabe. **Vorgabewert**, wenn das Feld fehlt oder unbekannt ist. |

Die Freigabeklasse betrifft nur das Urheberrecht. Der Datenschutzbefund (`datenschutz.befund`) ist
ein eigenes Urteil. Das System verbindet beide mit einer Regel: Eine Quelle oder ein Datenanhang wird
nur ingestiert, wenn die Freigabeklasse `K1` oder `K2` ist **und** der Datenschutzbefund weder
`personenbezogen` noch `nicht_pruefbar` lautet. Bei `zweifelhaft` oder `ausstehend` wartet die Quelle, bis das Review
entschieden hat. Maßgeblich ist `references/findings-schema.md`, Abschnitt 3.4, im Skill
`topic-research`.

`K0` trägt einen `k0_grund`. Für die Auslieferung spielt er keine Rolle, er dient nur der späteren
Neubewertung.

## Warum das nötig ist

Ohne technische Durchsetzung lässt sich der frei lizenzierte Teil des Korpus nicht vom Rest trennen.
Dann gilt faktisch für den gesamten Korpus die strengere Klasse, und auch frei lizenzierte Quellen
dürften nur in Zitatlänge erscheinen.

## Sechs Anforderungen

1. **Freigabeklasse als Chunk-Metadatum führen.** Die Klasse wird auf Dokumentebene bestimmt und beim
   Ingest an jeden Chunk vererbt. Sie muss zur Retrieval-Zeit verfügbar sein, nicht erst beim
   Rendern, weil `K0` schon aus dem Retrieval herausfallen soll.
2. **`K0` hart filtern.** Chunks ohne Freigabeklasse oder mit `K0` werden weder abgerufen noch
   eingebettet. Der Filter gehört in die Retrieval-Query, nicht in die Darstellungsschicht.
3. **Ausgabe je Klasse unterschiedlich rendern.**
   - `K2`: längere zusammenhängende Passagen zulässig, Volltextanzeige und Download zulässig.
   - `K1`: Ausgabe als **gekennzeichnetes Zitat** mit harter Längenbegrenzung, kein Volltextzugriff,
     keine Schaltfläche „ganzes Dokument anzeigen".
4. **Chunk-Zusammenführung bei `K1` begrenzen.** Mehrere benachbarte Chunks derselben `K1`-Quelle
   dürfen nicht zu einer durchgehenden Passage zusammengesetzt werden. Technisch: Obergrenze für
   Anzahl und Gesamtlänge der Chunks **pro Quelle und Antwort**, nicht nur pro Chunk. Ohne diese
   Grenze rekonstruiert das System über mehrere Treffer hinweg genau das, was die Klasse verhindern
   soll. Das ist der am leichtesten übersehene Punkt.
5. **Quellenangabe erzwingen.** § 63 UrhG macht sie zur Wirksamkeitsvoraussetzung des Zitats: Fehlt
   sie, ist das Zitat unzulässig, auch wenn Umfang und Belegfunktion stimmen. Lässt sie sich nicht aus
   den Metadaten bilden, wird der Chunk nicht ausgegeben. Sie darf nicht hinter einer
   Aufklappfunktion verschwinden.
6. **Gemischte Antworten quellenweise behandeln.** Stützt sich eine Antwort auf `K1`- und
   `K2`-Quellen, gilt die Begrenzung **je Quelle**. Eine `K2`-Quelle in derselben Antwort erlaubt
   keine längere Wiedergabe der `K1`-Quelle.

## Was den Aufwand begrenzt

Die Klasse regelt die **Wiedergabe fremden Textes**, nicht die Zusammenfassung in eigenen Worten.
`K1`-Quellen dürfen inhaltlich voll ausgewertet werden, es darf nur nicht beliebig aus ihnen
abgeschrieben werden. Genau diese Trennung zeichnen die TDM-Schranken vor: Analyse ja, Weitergabe
nein.

## Umsetzungsstand

Offen. Blockiert die Auslieferung von Passagen an Nutzende.
