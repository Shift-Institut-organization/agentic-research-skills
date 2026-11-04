---
name: source-compliance-check
description: >
  Prüft recherchierte Quellen auf zwei Rechtsfragen, bevor sie in den Kompass-Datenpool gelangen:
  eine Lizenz- und Rechteprüfung (darf SHIFT die Quelle im Rahmen des Eckernkamp-Kompass nutzen?)
  und eine DSGVO-Personenbezugsprüfung (enthält die Quelle personenbezogene Daten?). Arbeitet auf
  einer findings_<thema>.json aus topic-research oder auf einer Liste von DOIs und URLs. Ergebnis
  sind je Quelle ein Lizenzbefund mit Freigabeklasse und ein Datenschutzbefund, die Listen der
  aussortierten Quellen und der Review-Queue sowie ein rechtebericht_<thema>.md.
  Nutze diesen Skill immer, wenn Quellen auf Lizenz, Urheberrecht, Nachnutzung, Text und Data
  Mining, Personenbezug oder Anonymisierung geprüft werden sollen, und immer im Anschluss an
  topic-research.
  Trigger-Phrasen: "Lizenzprüfung der Quellen", "DSGVO-Check der Quellen", "dürfen wir die Quelle
  nutzen", "dürfen wir das einbetten", "ist das anonymisiert", "Freigabeklasse",
  "können wir die in den Kompass übernehmen", "Rechteprüfung".
---

# Skill: Lizenz- und Datenschutzprüfung von Quellen

## Ziel

Jede Quelle **rechtlich freigeben oder aussortieren**, bevor sie in den Kompass-Datenpool gelangt.
Dazu je Quelle zwei getrennte Urteile:

- **Lizenzbefund** je Nutzungsart, verdichtet zu einer **Freigabeklasse** (`K2`, `K1`, `K0`)
- **Datenschutzbefund** (`kein_personenbezug`, `personenbezogen`, `zweifelhaft`, `nicht_pruefbar`)

## Eingabe

Zwei Fälle:

1. **`findings_<thema>.json` aus `topic-research`.** Der Normalfall. Die Datei wird in place um die
   Blöcke `lizenz` und `datenschutz` je Eintrag und je Datenanhang ergänzt, dazu
   `meta.aussortiert`, `meta.review_queue`, `meta.projektpraemissen`, `meta.lizenz_geprueft` und
   `meta.dsgvo_geprueft`. Rechercheteil nicht verändern.
2. **Liste von DOIs oder URLs**, etwa „dürfen wir diese vier Quellen nutzen?". Dann zuerst eine
   minimale `findings_<thema>.json` nach dem Schema anlegen (Pflichtfelder des Rechercheteils, als
   `relevanz_begruendung` „vom Nutzer vorgegeben"), danach wie Fall 1 verfahren.

Die Felder unter `pruefhinweise` sind Fundstellen aus der Recherche, **keine Befunde**. Sie sparen
Suchzeit, ersetzen aber nie das eigene Nachlesen.

## Leitprinzipien

1. **Unabhängige Prüfung.** Wird der Skill aus `topic-research` aufgerufen, läuft er in einem
   frischen Subagenten ohne den Sammelkontext. Wer Quellen mühsam zusammengesucht hat, liest
   Lizenztexte als Bestätigung und nicht als Prüfung. Begründungen, warum eine Quelle wertvoll sei,
   spielen für die Prüfung keine Rolle.
2. **Keine Quelle ohne Rechtefreigabe.** Jede Quelle trägt am Ende eine **Freigabeklasse** und einen
   **Datenschutzbefund**. Fehlt eines von beiden, ist der Lauf nicht abgeschlossen.
3. **Personenbezug führt zum Ausschluss, nicht zur Abwägung.** Quellen mit personenbezogenen Daten
   werden ausnahmslos aussortiert, eine Prüfung etwaiger Rechtsgrundlagen findet nicht statt. Der
   Maßstab dafür ist aber die Identifizierbarkeit **mit vernünftigerweise anzuwendenden Mitteln**,
   nicht die theoretische Denkbarkeit. Erklärten Anonymisierungen wird vertraut, solange die
   Red-Flag-Prüfung nichts Gegenteiliges findet.
4. **Nichts erfinden, Zweifel offenlegen.** Eine erfundene Lizenzangabe ist schädlicher als gar keine
   Prüfung, weil sie ein Prüfsiegel trägt. Wo die Rechtslage unklar bleibt, lautet der Befund
   `zweifelhaft` und die Quelle geht in die Review-Queue, nicht durch.

> [!IMPORTANT]
> Erschöpfende Suche erzeugt Material, von dem ein Teil rechtlich nicht nutzbar ist. Diese Spannung
> wird nicht dadurch aufgelöst, dass die Prüfung milder ausfällt, wenn die Ausbeute sonst schrumpft.
> Ein kleinerer, sauber freigegebener Korpus ist für den Kompass mehr wert als ein großer mit
> Rechtsrisiko.
>
> Sie wird aber auch nicht dadurch aufgelöst, dass die Prüfung strenger ausfällt als der Maßstab
> verlangt. Eine Datenschutzprüfung, die jede theoretisch denkbare Re-Identifizierung zum
> Ausschlussgrund erhebt, beseitigt den qualitativen Bestand und ist zugleich rechtlich unzutreffend.
> Beide Fehlrichtungen kosten etwas, und die zweite fällt niemandem auf, weil ein leerer Korpus
> vorsichtig aussieht.

### Rechtsstand

Beide Prüfdateien tragen den Rechtsstand im Kopf und sind nicht juristisch gegengeprüft. Ist der dort
vermerkte Rechtsstand älter als sechs Monate, wird das im Rechtebericht als Limitation ausgewiesen.

### Werkzeuge: woher ein Beleg stammen darf

Ein Befund ist nur so gut wie der Text, auf dem er beruht. Deshalb ist festgelegt, welches Werkzeug
für welchen Beleg taugt:

| Beleg | Werkzeug | Nicht verwenden |
|---|---|---|
| API-Lizenzfelder, robots.txt, TDMRep | `scripts/harvest_license_signals.py` | – |
| Lizenzangabe auf der Landing Page, Nutzungsbedingungen, AGB, Impressum | `mcp__fetch__fetch` oder `mcp__tavily__tavily_extract` (Wortlaut) | WebFetch, Auszüge aus Suchergebnissen |
| Methodenteil, Data Availability Statement, Anonymisierungserklärung | `mcp__fetch__fetch` auf die Seite; PDFs per Shell nach `scratch/` laden und mit Read lesen | WebFetch |
| Transkripte, Datensätze, Anhänge für die Red-Flag-Stichprobe | Datei per Shell nach `scratch/` laden, mit Read lesen, Volltextsuche per Shell | MCP-Zusammenfassungen |

**WebFetch liefert keinen Originaltext**, sondern die Antwort eines kleinen Modells auf eine Frage
zur Seite. Ein Lizenzbefund oder eine Fundstelle darf darauf nie beruhen. Dasselbe gilt für die
Auszüge, die Exa, Parallel oder Tavily in Suchergebnissen liefern. Sind weder `fetch` noch Tavily
verbunden, die Seite per Shell laden und den Wortlaut selbst lesen. Gelingt das nicht, lautet der
Befund `nicht_pruefbar`.

**`fetch` beachtet robots.txt.** Verweigert der Server den Abruf, weil robots.txt automatisierte
Zugriffe ausschließt, ist das ein Signal für die Opt-out-Prüfung in Phase 6 und wird mit Wortlaut der
Fehlermeldung im Log vermerkt. Die Lizenz- und Nutzungsbedingungen dürfen dann mit `tavily_extract`
gelesen werden; Datensätze und Volltexte werden in diesem Fall nicht automatisiert geladen.

**Bot-Schutz nicht umgehen.** Blockt eine Seite automatisierte Zugriffe (Cloudflare-Challenge,
Login), wird das als Grund für `nicht_pruefbar` dokumentiert.

**Prüfkopien sind Daten mit möglichem Personenbezug.** Heruntergeladene Transkripte und Rohdaten nur
in `scratch/` ablegen (nicht versioniert) und löschen, sobald der Befund dokumentiert ist, bei
`personenbezogen` sofort.

Welche MCP-Server verbunden waren, steht im Log von Phase 6.

---

## Phase 6: Lizenz- und Rechteprüfung

**Zweck:** Feststellen, ob die jeweilige Lizenz die Nutzung der Quelle durch SHIFT zu gemeinnützigen
Zwecken im Rahmen des Eckernkamp-Kompass gestattet. Zweifelsfälle werden für die anschließende
Prüfung durch das Team markiert.

Vollständiges Prüfprogramm, Normenkette, Opt-out-Erkennung und Entscheidungsbaum:
**`references/lizenzpruefung.md`**. Hier nur das, was im Kopf bleiben muss.

### 6.1 Signale vorab sammeln

```bash
python scripts/harvest_license_signals.py --from-findings findings_<thema>.json --json signale.json
```

Das Skript sammelt Lizenzfelder aus OpenAlex und CrossRef, robots.txt und TDMRep. Es **entscheidet
nichts**. Ein nicht abrufbares Signal (`nicht_feststellbar`) ist kein negatives Signal und darf nie als
`kein_vorbehalt` gewertet werden.

Danach je Quelle die Landing Page und die Nutzungsbedingungen im Wortlaut lesen (`fetch` oder
`tavily_extract`). Das Skript sieht nur, was maschinenlesbar ist, AGB und Lizenzzeilen im Seitentext
nicht. Steht unter `pruefhinweise` eine Fundstelle, dort zuerst nachsehen.

### 6.2 Drei Nutzungsarten getrennt prüfen

Der Kompass tut mit einer Quelle dreierlei, und die drei Handlungen stehen auf **unterschiedlichen
rechtlichen Füßen**. Eine pauschale Freigabe „die Quelle dürfen wir nutzen" ist deshalb
bedeutungslos. Geprüft wird je Quelle **pro Nutzungsart**:

| Kürzel | Nutzungsart | Rechtliche Einordnung |
|---|---|---|
| `N1` | Volltext in RAG- oder Vektordatenbank einbetten | Vervielfältigung. Braucht Schranke oder Lizenz. |
| `N2` | Passagen oder Volltext an Nutzende ausliefern | Öffentliche Wiedergabe. **Von den TDM-Schranken nicht gedeckt.** |
| `N3` | Datenanhänge (Transkripte, Datensätze) weiterverwenden | Zusätzlich Datenbankrechte und Phase 7. |

> [!CAUTION]
> `N2` ist der kritische Pfad und der am leichtesten zu übersehende. Die TDM-Schranken erlauben die
> Vervielfältigung **zur Analyse** und verlangen Löschung, sobald der Analysezweck erfüllt ist. Sie
> erlauben nicht, die Quelle oder Teile davon an Dritte weiterzugeben. Eine Quelle kann für `N1`
> freigegeben und für `N2` gesperrt sein. Dieser Fall ist nicht die Ausnahme, sondern bei allen
> Rechte-vorbehaltenen Verlagsinhalten der Normalfall.

### 6.3 Projektprämissen

Die Prüfung beruht auf Annahmen über SHIFT, die der Skill **nicht selbst feststellen kann**. Sie
stehen als deklarierter Block in `references/lizenzpruefung.md`, Abschnitt *Projektprämissen*, werden
nach `meta.projektpraemissen` übernommen und im Rechtebericht ausgewiesen. Ändert sich eine Prämisse,
ändert sich der Befund.

| Prämisse | Wirkung | Ausgewiesen über |
|---|---|---|
| SHIFT ist **Forschungsorganisation i.S.d. § 60d UrhG** (Feststellung des Projekts, keine offene Frage) | Gegen § 60d wirkt kein Rechtevorbehalt. Offen bleibt nur, ob der produktive Einsatz noch wissenschaftlicher Forschungszweck ist. | `traegt_ohne_60d` |
| **Der Kompass wird nicht kommerziell genutzt** | Die NonCommercial-Klausel CC-lizenzierter Quellen ist erfüllt. NC-Quellen gehen nicht mehr allein wegen NC in die Review-Queue. | `traegt_ohne_nc_praemisse` |

Beide sind Angaben des Projekts, keine Feststellungen dieses Skills. Deshalb trägt jeder Befund, der
auf einer von ihnen beruht, das zugehörige Feld. Fällt eine Prämisse, lässt sich der betroffene Teil
des Korpus gezielt herausfiltern, statt alles neu zu prüfen.

Zwei Verwechslungen, die hier nahe liegen und teuer sind:

- **Nicht-kommerziell zu handeln macht niemanden zur Forschungsorganisation.** Die NC-Prämisse stützt
  die § 60d-Prämisse, ersetzt sie aber nicht. § 60d verlangt zusätzlich wissenschaftliche
  Forschungszwecke.
- **Mit der NC-Frage entfallen nicht ND und SA.** Ein Bearbeitungsverbot (`ND`) und eine
  Share-alike-Pflicht (`SA`) sind von der Kommerzialität unabhängig und betreffen weiterhin `N2`.

### 6.4 Befunde und Konsequenzen

| Befund | Bedeutung | Konsequenz |
|---|---|---|
| `frei` | Lizenz gestattet die Nutzungsart ausdrücklich (CC BY, CC0, Public Domain, amtliches Werk) | durchlassen |
| `gestattet_schranke` | Keine Lizenz, aber eine Schranke trägt. Schranke wird benannt. | durchlassen, Schranke dokumentieren |
| `zweifelhaft` | Lizenz unklar, mehrdeutig, oder Schranke nur möglicherweise einschlägig | **bleibt in findings, Flag plus Review-Queue** |
| `gesperrt` | Klarer Ausschluss für diese Nutzungsart | bleibt, wenn eine andere Nutzungsart noch trägt. Sonst nach `meta.aussortiert`. |
| `nicht_pruefbar` | Quelle, Landing Page oder Nutzungsbedingungen nicht erreichbar, auch bei HTTP 403 und wenn die APIs keine Lizenz melden | wie `zweifelhaft`, Grund aber gesondert vermerkt |

**Keine Lizenz gefunden ist nicht `nicht_pruefbar`.** War alles lesbar und es gibt schlicht keine
Lizenz (Verlags-Copyright, „free to read", „Alle Rechte vorbehalten", keine Angabe), werden die
Einzelbefunde normal gebildet, die Quelle erhält aber `K0_keine_freigabe` mit
`k0_grund: keine_lizenz_gefunden` (Abschnitt 6.6). Sie ist damit abschließend geprüft und gehört nicht
in die Review-Queue.

**Aussortiert wird erst, wenn die Quelle für keine Nutzungsart mehr trägt.** Eine Quelle, die für
`N1` frei und nur für `N2` gesperrt ist, bleibt im Korpus. Sie speist die Analyse, nur zitiert werden
darf aus ihr nicht.

Komplett gesperrte Quellen verschwinden nicht spurlos, sondern wandern mit Begründung nach
`meta.aussortiert`. Sonst findet die nächste Recherche sie erneut und prüft sie erneut.

### 6.5 Hard-Fail: Lizenzangaben werden nie erschlossen

Eine Lizenz wird **ausschließlich** aus einer belegbaren Quelle übernommen: Lizenzfeld der API,
Lizenzangabe auf der Landing Page, Lizenzdatei im Repositorium, Impressum oder Nutzungsbedingungen.

Niemals erschlossen wird eine Lizenz aus: Plattformzugehörigkeit („liegt auf Zenodo, also CC BY"),
Open-Access-Status („frei lesbar, also frei nutzbar"), Fachgebiet, Erscheinungsjahr oder Analogie zu
einer anderen Quelle desselben Herausgebers. Jede dieser Ableitungen ist ein Hard-Fail. Ist die
Lizenzangabe nicht erreichbar, lautet der Befund `nicht_pruefbar`; ist alles gelesen und es gibt keine
Lizenz, bleibt `lizenz_bezeichnung` leer und die Quelle erhält `K0` mit
`k0_grund: keine_lizenz_gefunden`.

Das gilt auch, wenn der Auftraggeber darauf drängt. Eine falsche Lizenzangabe fällt niemandem auf,
weil sie plausibel ist. Sie wird erst sichtbar, wenn jemand Rechte geltend macht. Stattdessen die
Anfrage beim Herausgeber als Handlungsvorschlag in die Review-Queue schreiben.

### 6.6 Freigabeklassen

Die drei Befunde je Nutzungsart werden zu einer **Freigabeklasse** verdichtet, die jede Quelle genau
einmal trägt und an alle ihre Chunks vererbt wird.

| Klasse | Bedeutung |
|---|---|
| `K2_volltextwiedergabe` | Chunking zulässig **und** Wiedergabe im Volltext zulässig. Typisch: CC0, CC BY, CC BY-SA, CC BY-NC, amtliches Werk, dl-de/by-2-0 |
| `K1_analyse_und_zitat` | Chunking zulässig, Wiedergabe **nur im Rahmen des Zitatrechts** (§ 51 UrhG). Typisch: CC BY-ND, CC BY-NC-ND |
| `K0_keine_freigabe` | Weder Chunking noch Wiedergabe. Quelle wird nicht indexiert. Typisch: keine Lizenz (Verlags-Copyright, „free to read", auch mit TDM-Rechtevorbehalt), nicht prüfbar, kein rechtmäßiger Zugang |

Ableitung: Zuerst `K0`, wenn keine Lizenz gefunden wurde, `N1` nicht trägt oder kein rechtmäßiger
Zugang besteht. Sonst `K2` wenn `N2 == frei`, `K1` wenn `N2` gesperrt, zweifelhaft oder nur über § 51
gestattet ist. Jedes `K0` trägt einen `k0_grund`: `keine_lizenz_gefunden`, `nicht_pruefbar`,
`kein_rechtmaessiger_zugang` oder `n1_traegt_nicht`. Einzelheiten: `references/lizenzpruefung.md`,
Abschnitt 6.

**Lizenz und Datenschutz bleiben zwei getrennte Urteile.** Ein Datenschutzbefund ändert die
Freigabeklasse nicht. Nachgelagerte Skills verbinden beide mit einer Regel: nutzbar nur bei `K1` oder
`K2` **und** Datenschutzbefund weder `personenbezogen` noch `nicht_pruefbar`; `zweifelhaft` wartet auf
das Review (`references/lizenzpruefung.md`, Abschnitt 6.3).

> [!IMPORTANT]
> **`K0` ist der Vorgabewert, nicht `K1`.** Fehlt das Feld oder trägt es einen unbekannten Wert, gilt
> die Quelle als nicht freigegeben. Ein abgebrochener Prüflauf oder ein nachträglich ergänzter
> Datensatz darf nie dazu führen, dass eine ungeprüfte Quelle als zitierfähig gilt.

Die Klasse regelt die **Wiedergabe fremden Textes**, nicht die Zusammenfassung in eigenen Worten.
`K1`-Quellen dürfen inhaltlich voll ausgewertet werden, es darf nur nicht beliebig aus ihnen
abgeschrieben werden.

### 6.7 Abbruchkriterien

- **Nutzungsarten nicht geklärt** → Prüfung nicht durchführbar. Erst `N1` bis `N3` für den konkreten
  Lauf bestätigen lassen, dann prüfen.
- **Keine Quelle erreichbar** (Netzsperre, API down) → Lauf als `nicht_pruefbar` kennzeichnen,
  `lizenz_geprueft:` **nicht** setzen. Einen Korpus als geprüft auszuweisen, der nicht geprüft werden
  konnte, ist schlechter als gar keine Prüfung.

👉 Log: `phase: "6_lizenzpruefung"`, Status `ok | viele_zweifel | quellen_unerreichbar`

---

## Phase 7: DSGVO-Personenbezugsprüfung

**Zweck:** Für jede Quelle und jeden Datenanhang feststellen, ob personenbezogene Daten i.S.d. DSGVO
enthalten sind. Quellen, die solche Daten enthalten, werden aussortiert.

Vollständiges Prüfprogramm mit Vertrauensvermutung, Red-Flag-Katalog, Dreikriterientest und
Entscheidungsbaum: **`references/dsgvo-pruefung.md`**.

### 7.1 Schutzziel

Der Kompass soll mit seinem Quellenkorpus **nicht in den Anwendungsbereich der DSGVO fallen**. Das
wird dadurch erreicht, dass keine personenbezogenen Daten in den Datenpool gelangen. Eine Abwägung
von Rechtsgrundlagen findet nicht statt: Wer keine personenbezogenen Daten verarbeitet, braucht
weder Rechtsgrundlage noch Zweckbindung, Informationspflichten, Löschkonzept oder
Datenschutz-Folgenabschätzung.

Daraus folgt zugleich die Grenze der Prüfung. Maßstab ist die Identifizierbarkeit **mit
vernünftigerweise anzuwendenden Mitteln** (Art. 4 Nr. 1 DSGVO i.V.m. ErwGr. 26), nicht die
theoretische Denkbarkeit.

### 7.2 Was geprüft wird und was nicht

**Nicht Gegenstand sind bibliographische Metadaten.** Autorennamen, Affiliationen und
Korrespondenzadressen sind personenbezogene Daten, aber bei *jeder* wissenschaftlichen Quelle. Würde
der Check sie erfassen, wäre jeder Befund „personenbezogen" und der Korpus leer. Ihre Verarbeitung
wird einmal zentral geklärt.

**Ebenfalls nicht Gegenstand sind Selbstauskünfte von Autorinnen und Autoren**, etwa ein
Positionality-Absatz mit Angaben zu Herkunft oder Religion. Sie lösen keine Red Flag aus. Die Fundstelle
kommt nach `datenschutz.autor_selbstauskunft`, und der Absatz fließt nicht in Stakeholder-Analysen oder
Personas ein. Das gilt nur für Angaben über die eigene Person, nicht über Dritte
(`references/dsgvo-pruefung.md`, Abschnitt 2).

Gegenstand ist der **Personenbezug im Inhalt**: Angaben über Befragte, Betroffene, Beschäftigte oder
namentlich behandelte Einzelpersonen in Volltexten, Transkripten, Rohdaten und Fallbeschreibungen.

### 7.3 Vertrauensvermutung bei erklärter Anonymisierung

Der Kern des Verfahrens. **Erklärt die Quelle, dass die Daten anonymisiert wurden, wird dem
gefolgt**, sofern drei Bedingungen erfüllt sind:

| | Bedingung |
|---|---|
| **V1** | Eine Anonymisierungserklärung ist vorhanden (Methodenteil, Data Availability Statement, Datensatzbeschreibung). Fundstelle dokumentieren. |
| **V2** | Die erklärende Stelle ist einschlägig qualifiziert: Forschungseinrichtung, kuratiertes Repositorium, Behörde, etablierter Verband. |
| **V3** | Die Stichprobe findet keine Red Flag (7.4). |

Dann lautet der Befund `kein_personenbezug`. Es ist **nicht** zusätzlich zu begründen, warum eine
Re-Identifizierung ausgeschlossen sei.

### 7.4 Red-Flag-Katalog

Die Vermutung wird durch **konkrete Funde im Text** widerlegt, nicht durch denkbare Szenarien. Jede
Red Flag führt zum Befund `personenbezogen`.

| | Red Flag |
|---|---|
| **R1** | Klarnamen, Initialen mit Zusatzangabe, Namen kleiner Betriebe |
| **R2** | Ortsangaben unterhalb der Gemeindeebene (Straße, Quartier, Haltestelle, Schule) |
| **R3** | In ihrer Organisation singuläre Funktionsbezeichnungen |
| **R4** | Datierbare Einzelereignisse mit Öffentlichkeitsbezug |
| **R5** | Sehr kleine Grundgesamtheit plus mehrere demografische Merkmale (Richtwert N unter 10) |
| **R6** | Zugängliche Schlüsselliste (Pseudonym zu Klarnamen) |
| **R7** | Audio- oder Videoaufnahmen statt Text |
| **R8** | Feingranulare Geo- oder Bewegungsdaten |
| **R9** | Art.-9-Angaben in Verbindung mit R1 bis R5 |

> [!IMPORTANT]
> **Ein Codebook ist keine Schlüsselliste.** Das in der qualitativen Forschung übliche Codebook
> enthält Variablendefinitionen und Kodierregeln, keine Zuordnung zu Klarnamen. Es als Schlüssel zu
> behandeln, sortiert ausgerechnet die am besten dokumentierten Datensätze aus. Nur eine tatsächlich
> **zugängliche** Zuordnungstabelle ist R6. Den Inhalt ansehen, nicht nach Dateinamen entscheiden.
> Zur nicht veröffentlichten Schlüsselliste beim Forschenden und ihrem Restrisiko:
> `references/dsgvo-pruefung.md`, Abschnitt 7.

### 7.5 Art. 9 verschärft, schließt aber nicht aus

**Art. 9 setzt personenbezogene Daten voraus.** Ein anonymes Transkript, in dem jemand über seine
Dialysetermine spricht, enthält keine Gesundheitsdaten im Sinne der DSGVO, weil es überhaupt keine
personenbezogenen Daten enthält.

Besondere Kategorien sind deshalb **kein eigener Aussortierungsgrund**. Andernfalls verlöre der
Kompass genau die Quellen, auf die es ihm ankommt: Interviews mit Menschen, deren Mobilität durch
Krankheit, Behinderung, Alter oder Herkunft eingeschränkt ist, also die *moral patients*.

Was Art. 9 bewirkt, ist eine **Verschärfung des Prüfmaßstabs**: größerer Stichprobenumfang, Red Flag
R9, und bei verbleibender Unsicherheit der Befund `zweifelhaft` statt `kein_personenbezug`.

### 7.6 Befunde und Konsequenzen

| Befund | Bedeutung | Konsequenz |
|---|---|---|
| `kein_personenbezug` | Vermutung greift oder Dreikriterientest bestanden | bleibt im Korpus |
| `personenbezogen` | Red Flag gefunden oder Kriterium verletzt | **nach `meta.aussortiert`**, typ `datenschutz` |
| `zweifelhaft` | Tatsachenfrage nicht sicher beurteilbar | **Review-Queue** |
| `nicht_pruefbar` | nichts einsehbar und Klasse mit realistischem Risiko | **nach `meta.aussortiert`** |
| `ausstehend` | Prüfung noch nicht gelaufen, das Material lässt sich aber beschaffen | **Review-Queue**, vorerst nicht nutzbar, nicht aussortiert |

**`ausstehend` ist kein Urteil über die Quelle.** Es heißt nur, dass noch niemand nachgesehen hat. Ist
das Material dagegen nicht erreichbar, lautet der Befund `nicht_pruefbar`. Der Lauf darf
`dsgvo_geprueft` trotzdem setzen, die betroffene Quelle bleibt einzeln gesperrt, bis der Befund
nachgetragen ist.

**Aussortiert wird, nicht abgewogen.** Was bleibt, ist allein die **Tatsachenfrage**, ob die Quelle
personenbezogene Daten enthält. Kann sie nicht beantwortet werden, lautet der Befund `zweifelhaft`
und geht in die Review-Queue.

**Bei Anhängen wird der Anhang aussortiert, nicht die Quelle.** Liegt im Supplement eine
Teilnehmerliste, verliert der Aufsatz dadurch nicht seine Nutzbarkeit.

### 7.7 Sorgfaltsdokumentation

Die Vermutung trägt nur, wenn die begleitende Prüfung nachweisbar ist. Je Quelle zu dokumentieren:
Stichprobenumfang in Worten, Fundstelle der Anonymisierungserklärung, erklärende Stelle, **die
vollständige Liste der geprüften Red Flags** (auch wenn nichts gefunden wurde), bei Funden Flag und
Fundstelle, sowie der Befund.

Die vollständige Liste geprüfter Flags unterscheidet „geprüft und nichts gefunden" von „nicht
geprüft". Nur Ersteres trägt die Vermutung. Mindestumfänge je Materialart:
`references/dsgvo-pruefung.md`, Abschnitt 12.

Die maschinelle Volltextsuche nach Ortsangaben, Eigennamen und Organisationsbezeichnungen (R1 bis R3)
läuft per Shell auf der heruntergeladenen Datei, nicht über ein MCP-Werkzeug. Nur so ist sie
vollständig und im Stichprobenumfang belegbar.

Es gibt kein „once anonymous, always anonymous": Der Korpus ist jährlich erneut zu bewerten.

### 7.8 Abbruchkriterien

- **Nichts einsehbar bei risikobehafteter Klasse** → `nicht_pruefbar`, aussortieren,
  `dsgvo_geprueft:` für diese Quelle nicht setzen.
- **Prüfperspektiven nicht geklärt** → erst klären. Eine Prüfung ohne Perspektive liefert kein
  Ergebnis, sondern ein Gefühl.

👉 Log: `phase: "7_dsgvo_pruefung"`, Status `ok | viele_treffer | nicht_einsehbar`

---

## Output

### `findings_<thema>.json`

Ergänzt nach dem Schema in `.claude/skills/topic-research/references/findings-schema.md`:
`lizenz`-Block mit `freigabeklasse` und `datenschutz`-Block je Eintrag und je Datenanhang,
`meta.aussortiert` (mit `typ` lizenz oder datenschutz), `meta.review_queue`,
`meta.projektpraemissen`, `meta.lizenz_geprueft`, `meta.dsgvo_geprueft` und die Phasen-Logs 6 und 7.

### `rechtebericht_<thema>.md`

1. **Projektprämissen** und Rechtsstand der Prüfdateien
2. **Lizenzbefunde** je Nutzungsart, **Verteilung der Freigabeklassen K2/K1/K0**, Aussortierte mit
   Begründung
3. **Datenschutzbefunde:** Zahl der Quellen mit greifender Vertrauensvermutung, gefundene Red Flags
   mit Fundstelle, Aussortierte, Sorgfaltsdokumentation (Stichprobenumfänge)
4. **Review-Queue** mit Dringlichkeit und wer entscheiden muss
5. **Limitationen und offene Rechtsfragen**, insbesondere die § 60d-Prämisse

### Validierung

```bash
python .claude/skills/topic-research/scripts/validate_findings.py findings_<thema>.json --stage compliance
```

---

## Qualitätssicherung

- [ ] **Jeder Eintrag trägt einen `lizenz`-Block mit Befund je Nutzungsart N1, N2, N3**
- [ ] **Jeder Eintrag trägt eine `freigabeklasse`** (`K2`, `K1` oder `K0`), Vorgabewert ist `K0`
- [ ] **Jeder Eintrag trägt einen `datenschutz`-Block mit Befund**
- [ ] **Keine Lizenz erschlossen statt belegt** (Hard-Fail-Regel 6.5 eingehalten)
- [ ] Abhängigkeit von den Projektprämissen in `traegt_ohne_60d` und `traegt_ohne_nc_praemisse`
- [ ] Bei greifender Vertrauensvermutung sind V1 bis V3 dokumentiert (Erklärung, Stelle, Stichprobe)
- [ ] **`red_flags_geprueft` ist vollständig befüllt**, auch wenn nichts gefunden wurde
- [ ] Stichprobenumfang je Quelle in Worten dokumentiert, nicht nur als Kategorie
- [ ] Aussortierte Quellen stehen mit Begründung und `typ` in `meta.aussortiert`
- [ ] Bei belastetem Anhang wurde der **Anhang** aussortiert, nicht die Quelle
- [ ] Zweifelsfälle stehen in `meta.review_queue`, nicht nur als Feld am Eintrag
- [ ] `meta.phasen_log` enthält die Phasen 6 und 7
- [ ] `validate_findings.py --stage compliance` läuft ohne Fehler durch
- [ ] `rechtebericht_<thema>.md` im Arbeitsverzeichnis gespeichert

---

## Referenzen

| Datei | Inhalt | Wann lesen |
|---|---|---|
| `references/lizenzpruefung.md` | Normenkette, Projektprämissen, Opt-out-Erkennung, Entscheidungsbaum, Lizenz-Schnelltabelle | Phase 6 |
| `references/dsgvo-pruefung.md` | Dreikriterientest, Perspektivenprüfung, Art.-9-Katalog, Entscheidungsbaum | Phase 7 |
| `scripts/harvest_license_signals.py` | Sammelt Lizenzfelder, robots.txt und TDM-Signale automatisiert | Phase 6, vorab |
| `evals/beispiel_findings.json` | Vollständig ausgefülltes Beispiel mit drei typischen Fällen | bei Unklarheit über das Format |
| `.claude/skills/topic-research/references/findings-schema.md` | JSON-Schema | Output |
