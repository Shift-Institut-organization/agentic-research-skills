# Lizenz- und Rechteprüfung (Phase 6)

Prüfprogramm für die Frage, ob die Lizenz einer recherchierten Quelle die Nutzung durch SHIFT zu
gemeinnützigen Zwecken im Rahmen des Eckernkamp-Kompass gestattet.

**Rechtsstand dieser Datei:** 2026-10-20. Der Prüfmaßstab ist aus den Normtexten und Lizenztexten
abgeleitet (Liste am Ende), aber **nicht juristisch gegengeprüft**. Wird diese Datei älter als sechs
Monate, im Protokoll als Limitation ausweisen.

## Inhalt

1. [Projektprämissen](#1-projektprämissen)
2. [Was überhaupt geprüft wird](#2-was-überhaupt-geprüft-wird)
3. [Normenkette](#3-normenkette)
4. [Opt-out-Erkennung](#4-opt-out-erkennung-rechtevorbehalt)
5. [Entscheidungsbaum](#5-entscheidungsbaum)
6. [Freigabeklassen für die Ausgabe](#6-freigabeklassen-für-die-ausgabe)
7. [Lizenz-Schnelltabelle](#7-lizenz-schnelltabelle)
8. [Quellenklassen mit Sonderregeln](#8-quellenklassen-mit-sonderregeln)
9. [Ausgabeformat](#9-ausgabeformat)
10. [Bekannte Lücken](#10-bekannte-lücken-dieser-prüfung)

---

## 1. Projektprämissen

Die Prüfung beruht auf Annahmen, die dieser Skill **nicht selbst feststellen kann**. Sie stehen hier
offen, damit ein Befund nachvollziehbar bleibt und bei geänderter Prämisse neu bewertet werden kann.

```yaml
nutzer: SHIFT (gemeinnützig, Kooperation mit THWS und Rockenstein)
zweck: Eckernkamp-Kompass, KI-gestützte Werte-Erhebung im Requirements Engineering

rechtstraeger_status: Forschungsorganisation i.S.d. § 60d UrhG
  quelle_der_einordnung: Feststellung des Projekts, 2026-11-04
  juristisch_geprueft: nein
  pruefung_durch_diesen_skill: nein

nutzung_kommerziell: nein
  bedeutung: Der Kompass wird nicht kommerziell genutzt. Die NonCommercial-Klausel
             CC-lizenzierter Quellen ist damit erfüllt.
  quelle_der_einordnung: Angabe des Projekts, 2026-10-20
  pruefung_durch_diesen_skill: nein
  reichweite: gilt für N1, N2 und N3 gleichermaßen

nutzungsarten:
  N1: Volltext in RAG- oder Vektordatenbank einbetten
  N2: Passagen oder Volltext an Nutzende ausliefern
  N3: Datenanhänge (Transkripte, Datensätze) weiterverwenden
```

> [!IMPORTANT]
> **SHIFT ist Forschungsorganisation.** Das steht für das Projekt fest und wird nicht je Lauf neu
> gefragt. Es gehört weder in die Review-Queue noch in den Prüfbericht als offene Frage.

**Offen bleibt der Zweck.** § 60d setzt nach Art. 3 CDSM-RL zusätzlich **wissenschaftliche
Forschungszwecke** voraus. Ob ein produktiv eingesetztes Beratungs- und Beteiligungswerkzeug diesen
Zweck noch erfüllt, ist eine eigene Rechtsfrage. Sie betrifft das ganze Projekt und keine einzelne
Quelle, steht deshalb unter `meta.limitationen` im Prüfbericht und nicht in der Review-Queue.

Deshalb bleibt die **zweigleisige Ausweisung**: Jeder Befund, der § 60d braucht, wird zusätzlich
danach bewertet, ob er auch **allein über § 44b UrhG** trägt (`traegt_ohne_60d`). Würde die Nutzung
als nicht-wissenschaftlich eingestuft, bliebe der § 44b-Teil des Korpus bestehen und nur der Rest
wäre neu zu bewerten.

### Zur Prämisse `nutzung_kommerziell: nein`

Das Projekt stellt fest, dass der Kompass nicht kommerziell genutzt wird. Die Prüfung legt das
zugrunde und behandelt die NonCommercial-Klausel damit als **erfüllt**. NC-lizenzierte Quellen gehen
nicht mehr allein wegen der NC-Klausel in die Review-Queue.

Dass diese Feststellung als **deklarierte Prämisse** geführt wird und nicht fest in die Prüflogik
eingebaut ist, hat denselben Grund wie bei § 60d: Sie ist eine Tatsachenaussage über das Projekt, die
sich ändern kann, während die bereits geprüften Quellen im Korpus liegen bleiben. Zwei Entwicklungen
ließen sie kippen:

- Der Kompass wird Kommunen oder Unternehmen **entgeltlich** zur Verfügung gestellt, auch wenn das
  Entgelt nur die Kosten deckt.
- Die Nutzung erfolgt überwiegend **zugunsten eines gewerblichen Kooperationspartners**.

Tritt eines davon ein, ist allein der NC-lizenzierte Teil des Korpus neu zu bewerten. Damit das ohne
vollständige Neurecherche möglich bleibt, trägt jeder Befund, der auf dieser Prämisse beruht, das
Feld `traegt_ohne_nc_praemisse`. Es ist dieselbe Vorsorge wie `traegt_ohne_60d`: Wer die Abhängigkeit
nicht mitschreibt, muss im Zweifel alles anfassen.

> Zu beachten bleibt: `nutzung_kommerziell: nein` und die Forschungsorganisations-Einordnung sind
> **zwei verschiedene Fragen**. Nicht-kommerziell zu handeln macht eine Einrichtung nicht zur
> Forschungsorganisation, und § 60d verlangt zusätzlich wissenschaftliche Forschungszwecke. Die
> NC-Prämisse stützt die § 60d-Prämisse also, ersetzt sie aber nicht.

---

## 2. Was überhaupt geprüft wird

Nicht jede Quelle wirft überhaupt eine Lizenzfrage auf. Vor der eigentlichen Prüfung zwei Filter:

**Kein Schutzgegenstand, keine Lizenzfrage.** Reine Metadaten (Titel, Autorennamen, Jahr, DOI,
Journalname) sind in aller Regel nicht schutzfähig. Wer nur Metadaten speichert, braucht keine
Schranke. Sobald **Abstract oder Volltext** gespeichert werden, ist die Schwelle überschritten, denn
der Abstract ist regelmäßig selbst ein schutzfähiger Text.

**Datenbankrechte gelten unabhängig vom Werkschutz.** Eine Sammlung nicht-schöpferischer Daten kann
über das Datenbankherstellerrecht geschützt sein, auch wenn kein einzelnes Element Werkqualität hat.
Relevant bei Datensätzen, Statistiksammlungen und Verbandsdatenbanken, also genau bei `N3`.

*Hinweis: Das Datenbankherstellerrecht (§§ 87a ff. UrhG) ist in dieser Prüfung nicht ausgearbeitet.
Entnahmen aus Datensätzen sind daher nicht abschließend beurteilbar und führen im Zweifel zu*
`zweifelhaft`.

---

## 3. Normenkette

### 3.1 Anknüpfung: Welche Handlung liegt vor?

| Nutzungsart | Betroffenes Recht |
|---|---|
| `N1` Einbetten in Vektor-DB | Vervielfältigung, § 16 UrhG |
| `N2` Ausliefern an Nutzende | Öffentliche Wiedergabe, § 15 Abs. 2, § 19a UrhG |
| `N3` Datenanhänge weiterverwenden | Vervielfältigung plus ggf. Datenbankherstellerrecht, §§ 87a ff. UrhG |

### 3.2 § 44b UrhG, Text und Data Mining

In Kraft seit 07.06.2021, Umsetzung von Art. 4 CDSM-RL.

| Absatz | Inhalt |
|---|---|
| Abs. 1 | Automatisierte Analyse digitaler Werke zur Gewinnung von Informationen über Muster, Trends und Korrelationen |
| Abs. 2 | Vervielfältigung **rechtmäßig zugänglicher** Werke zulässig, **Löschungspflicht**, sobald der TDM-Zweck erfüllt ist |
| Abs. 3 | Vorbehalt des Rechteinhabers, bei online veröffentlichten Inhalten nur in **maschinenlesbarer Form** wirksam (S. 2) |

Zwei Punkte, die in der Praxis falsch gelesen werden:

- **Rechtmäßig ist der *Zugang*, nicht die Zugänglichmachung.** Es kommt darauf an, ob der Nutzende
  rechtmäßig an das Werk gelangt ist, nicht ob der Anbieter es rechtmäßig eingestellt hat. Das
  schützt den gutgläubigen Entwickler.
- **§ 44b ist nicht auf kommerzielle Nutzung beschränkt.** Die Vorlagenorm Art. 4 CDSM-RL ist
  zweckoffen und begünstigt jede Person und jeden Zweck, auch kommerzielle. **Für die Prüfung heißt
  das: Gemeinnützigkeit ist bei § 44b kein Tatbestandsmerkmal.** § 44b trägt die SHIFT-Nutzung genauso
  wie eine kommerzielle. Der gGmbH-Status hilft hier weder noch schadet er.

### 3.3 § 60d UrhG, TDM für wissenschaftliche Forschung

§ 60d UrhG setzt die Forschungsausnahme des Art. 3 CDSM-RL um. Nach der Unionsvorlage gilt:

> Die Forschungsausnahme des Art. 3 ist **nicht abdingbar** (Art. 7 Abs. 1 CDSM-RL) und kennt
> **keinen Nutzungsvorbehalt**, ist aber auf **Forschungsorganisationen und Einrichtungen des
> Kulturerbes** sowie auf **wissenschaftliche Forschungszwecke** beschränkt.

Operativ folgt daraus:

| Frage | Antwort für die Prüfung |
|---|---|
| Wirkt ein Rechtevorbehalt gegen § 60d? | Nein. Das ist der entscheidende Unterschied zu § 44b. |
| Wer ist Forschungsorganisation? | § 60d Abs. 2 UrhG. SHIFT ist es laut Feststellung des Projekts (Abschnitt 1). |
| Deckt § 60d die Auslieferung an Nutzende (`N2`)? | Nein, siehe 3.4. Auch § 60d ist eine TDM-Schranke. |
| Ist § 60d vergütungsfrei? | Nicht geklärt. Offen lassen, Review-Queue. |

### 3.4 Die Grenze beider TDM-Schranken: `N2` ist nicht gedeckt

Dies ist der wichtigste Satz dieser Datei.

§ 44b und § 60d erlauben die **Vervielfältigung zum Zweck der automatisierten Analyse** und verlangen
die **Löschung, sobald dieser Zweck erfüllt ist** (§ 44b Abs. 2; Art. 4 Abs. 2 CDSM-RL: Aufbewahrung
„so lange, wie für die Zwecke des TDM notwendig"). Sie erlauben nicht, das Werk oder Teile davon
**an Dritte weiterzugeben**.

Liefert der Kompass Passagen, Zitate oder Volltextauszüge an Nutzende aus, ist das öffentliche
Wiedergabe und braucht eine **eigene** Grundlage:

1. eine **Lizenz**, die Weitergabe gestattet (CC BY, CC BY-SA, CC0, Public Domain), oder
2. **Gemeinfreiheit** (amtliche Werke, § 5 UrhG), oder
3. das **Zitatrecht** (§ 51 UrhG) in seinen engen Grenzen, oder
4. eine **individuell eingeholte Erlaubnis**.

Zum Zitatrecht (§ 51 UrhG): Großzitat nur zur Übernahme in ein selbständiges *wissenschaftliches*
Werk, Kleinzitat zur Belegfunktion, **Quellenangabe nach § 63 UrhG zwingend**. Ein RAG-System, das Passagen zur Beantwortung von Nutzerfragen ausgibt, ist
kein selbständiges wissenschaftliches Werk. Die Belegfunktion des Kleinzitats kann tragen, wenn die
Ausgabe sich **erkennbar auf die Quelle bezieht, in Umfang begrenzt ist und die Quelle nennt**. Das
ist eine Gestaltungsanforderung an das System, keine Eigenschaft der Quelle.

> [!CAUTION]
> Verwechsle nicht „Quelle ist Open Access" mit „Weitergabe erlaubt". Frei lesbar heißt frei lesbar.
> Viele Verlags-Open-Access-Angebote stehen unter „free to read", nicht unter einer
> Weiterverwendungslizenz. Für `N2` ist allein die **Lizenz** maßgeblich, nicht die Zugänglichkeit.

**Konsequenz für die Architektur, nicht nur für die Prüfung:** Wenn `N2` nur für den
lizenzfreigegebenen Teil des Korpus zulässig ist, muss der Kompass zwei Klassen von Quellen technisch
unterscheiden können: solche, aus denen zitiert werden darf, und solche, die nur die Analyse
speisen. Das leistet die Freigabeklasse (Abschnitt 6).

### 3.5 § 31 Abs. 5 UrhG, Zweckübertragungsregel

Die wichtigste Auslegungsregel bei unklaren Lizenztexten:

> Im Zweifel sind nur die für den Vertragszweck erforderlichen Rechte übertragen, im Zweifel zugunsten
> des Urhebers.

Das ist die dogmatische Grundlage dafür, dass `zweifelhaft` **nicht** als „wird schon gehen" behandelt
wird. Eine mehrdeutige Lizenz spricht im Rechtssinn gegen die weitergehende Nutzung, nicht dafür.

---

## 4. Opt-out-Erkennung (Rechtevorbehalt)

Ein Rechtevorbehalt nach § 44b Abs. 3 UrhG ist **kein aktives Verbotsrecht, sondern eine
Reservationstechnik**: Ohne wirksamen Vorbehalt gilt die Schranke, mit wirksamem Vorbehalt bleibt es
beim Regelverbot des § 15 UrhG. Rechtsfolge einer Verletzung: Ansprüche nach §§ 97 ff. UrhG.

**Nur relevant für § 44b.** Gegen § 60d/Art. 3 wirkt kein Vorbehalt.

### 4.1 Wo nachgesehen wird

Mindestens diese fünf Orte prüfen, in dieser Reihenfolge. `scripts/harvest_license_signals.py`
automatisiert die ersten drei.

| # | Ort | Was es bedeutet |
|---|---|---|
| 1 | `robots.txt` der Host-Domain, nach RFC 9309 | Einträge gegen `GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `anthropic-ai` gelten als wirksamer Vorbehalt. Baseline nach GPAI Code of Practice, Measure 1.3. |
| 2 | **Nutzungsbedingungen / AGB der Website** | ErwGr. 18 CDSM-RL nennt maschinenlesbare Mittel „einschließlich Metadaten und allgemeiner Geschäftsbedingungen einer Website". **AGB können den Vorbehalt tragen.** Prüfung darf sich nicht auf robots.txt beschränken. |
| 3 | **W3C TDMRep** | HTTP-Header oder `/.well-known/tdmrep.json`. |
| 4 | Metadaten der Datei | IPTC (Bilder), C2PA Content Credentials, XMP-Rechtefelder in PDFs. |
| 5 | `ai.robots.txt` (Konsortialliste, Cloudflare-Initiative) | Nicht zu verwechseln mit einer Datei namens `ai.txt`. Letztere ist kein etablierter Standard. |

**Technische Schutzmaßnahmen prüfen (Measure 1.2).** Paywalls, Subscription-Schranken und DRM sind
keine Vorbehalte, sondern lassen bereits den **rechtmäßigen Zugang** entfallen. Dann greift die
Schranke von vornherein nicht. Eine Quelle hinter einer Paywall, auf die nur über einen
Hochschulzugang zugegriffen wurde, ist für SHIFT nicht ohne Weiteres rechtmäßig zugänglich. Das ist
ein häufiger und leicht zu übersehender Fall: Der Zugang bestand, aber er bestand für die Hochschule,
nicht für SHIFT.

### 4.2 Ungeklärte Fragen, die als Zweifel zu führen sind

Rechtlich offen, also nicht eigenmächtig entscheiden:

- **Nachträglich erklärter Vorbehalt** und Rückzug bereits verarbeiteter Inhalte
- **Löschpflicht für bereits gelernte Repräsentationen** (Machine-Unlearning-Debatte)
- Reichweite des Vorbehalts auf **Modellgewichte**
- Verbindliche Festlegung auf ein konkretes maschinenlesbares Protokoll fehlt bislang, der
  EU-Multi-Stakeholder-Prozess läuft, „Ausgang ist offen"

Praxisbefund: Der Vorbehalt wird selten erklärt, weil Rechteinhaber fürchten, dass das Werk sonst in
Suchmaschinen nicht mehr angezeigt wird. Ein fehlender Vorbehalt ist
also der Normalfall und für sich genommen kein Grund zur Beunruhigung. Er ist aber auch kein Beleg
für eine Lizenz, siehe Hard-Fail-Regel.

---

## 5. Entscheidungsbaum

Je Quelle **und je Nutzungsart** durchlaufen. Erste zutreffende Zeile gewinnt.

```
SCHRITT 1: Schutzgegenstand?
  nur Metadaten gespeichert, kein Abstract, kein Volltext
    → frei (keine Lizenzfrage)
  sonst weiter

SCHRITT 2: Gemeinfrei?
  amtliches Werk (Gesetz, Verordnung, Entscheidung, amtlicher Erlass), § 5 UrhG
    → frei für N1, N2, N3
  Schutzfrist abgelaufen / Public Domain Mark / CC0
    → frei für N1, N2, N3
  sonst weiter
  ACHTUNG: Behördengutachten, Kommunalberichte und Ministeriumsbroschüren sind KEINE amtlichen
  Werke im Sinne des § 5. Amtlich ist der Normtext und die Entscheidung, nicht jede Publikation
  einer Behörde. Im Zweifel → zweifelhaft.

SCHRITT 3: Ausdrückliche Lizenz vorhanden und belegt?
  ja  → Lizenz-Schnelltabelle (Abschnitt 7) auswerten, Befund je Nutzungsart
  nein → weiter

SCHRITT 4: Rechtmäßiger Zugang?
  Paywall / DRM / Zugang nur über Dritt-Institution
    → gesperrt für N1, N2, N3 (Schranke greift nicht), Grund: kein rechtmäßiger Zugang
  sonst weiter

SCHRITT 5: Wirksamer Rechtevorbehalt? (nur § 44b-Pfad)
  maschinenlesbarer Vorbehalt gefunden (Abschnitt 4.1)
    → N1: gesperrt über § 44b.
         Trägt § 60d? Prämisse greift, Vorbehalt unwirksam → gestattet_schranke (§ 60d),
         aber ZWINGEND mit Vermerk "nur über § 60d, nicht über § 44b"
    → N2: gesperrt (TDM-Schranken decken N2 ohnehin nicht)
  kein Vorbehalt auffindbar
    → N1: gestattet_schranke (§ 44b, zusätzlich § 60d), Löschungspflicht nach Zweckerfüllung notieren
    → N2: weiter zu Schritt 6
    → N3: weiter zu Schritt 7

SCHRITT 6: N2: Trägt das Zitatrecht?
  Ausgabe erkennbar quellenbezogen, im Umfang begrenzt, Quelle genannt (§ 51, § 63 UrhG)
    → gestattet_schranke (§ 51), mit Auflage an die Systemgestaltung
  sonst
    → gesperrt für N2, Grund: keine Weitergabegrundlage

SCHRITT 7: N3: Datenanhänge
  Repositoriums-Nutzungsbedingungen prüfen (oft strenger als die Lizenz des Papers!)
  eigene Lizenz am Datensatz vorhanden → Schnelltabelle
  Datenbankherstellerrecht möglicherweise betroffen → zweifelhaft
  Nachnutzung ausdrücklich an Antrag/Registrierung gebunden (QDR, ICPSR, teils GESIS)
    → zweifelhaft, Grund: Nachnutzung antragspflichtig
  IMMER zusätzlich: Phase 7 (DSGVO) ist bei Datenanhängen nie entbehrlich

SCHRITT 8: nichts davon feststellbar (Quelle, Landing Page oder Nutzungsbedingungen nicht erreichbar)
    → nicht_pruefbar, Grund konkret benennen
  Das gilt auch, wenn die APIs keine Lizenz melden, die Landing Page aber den Abruf
  ablehnt (etwa HTTP 403): Was nicht gelesen werden konnte, ist nicht geprüft.
  Nicht verwechseln mit: alles gelesen, aber keine Lizenz gefunden. Das ist kein
  nicht_pruefbar, sondern ein geprüftes Ergebnis und führt in Schritt 9 zu K0
  mit k0_grund "keine_lizenz_gefunden".

SCHRITT 9: Freigabeklasse bilden (immer, als letzter Schritt)
  Die drei Befunde nach Abschnitt 6.2 zu einer Klasse verdichten:
    keine Nutzungslizenz gefunden                  → K0_keine_freigabe (keine_lizenz_gefunden)
    N1 traegt nicht oder kein rechtmäßiger Zugang  → K0_keine_freigabe
    N1 traegt UND N2 == frei                      → K2_volltextwiedergabe
    N1 traegt UND N2 gesperrt/zweifelhaft/§ 51    → K1_analyse_und_zitat
  Die Klasse ist das Feld, auf das die nachgelagerte Verarbeitung schaltet.
  Ohne sie ist der Befund für das RAG-System nicht auswertbar.
  Der Datenschutzbefund fließt NICHT in die Klasse ein (Abschnitt 6.3).
```

---

## 6. Freigabeklassen für die Ausgabe

Der Entscheidungsbaum liefert drei Befunde je Nutzungsart. Für die nachgelagerte Verarbeitung ist das
zu fein: Das RAG-System muss beim Ausliefern einer Antwort in **einem** Feld ablesen können, was es mit
einer Quelle tun darf. Die Befunde werden deshalb zu einer **Freigabeklasse** verdichtet, die jede
Quelle genau einmal trägt und an alle ihre Chunks vererbt wird.

### 6.1 Die drei Klassen

| Klasse | Bedeutung | Typische Lizenzlage |
|---|---|---|
| `K2_volltextwiedergabe` | Chunking und Embedding zulässig **und** Wiedergabe im Volltext zulässig | CC0, Public Domain Mark, CC BY, CC BY-SA, CC BY-NC, CC BY-NC-SA, amtliches Werk (§ 5 UrhG), dl-de/by-2-0 |
| `K1_analyse_und_zitat` | Chunking und Embedding zulässig, Wiedergabe **nur im Rahmen des Zitatrechts** (§ 51 UrhG) | CC BY-ND, CC BY-NC-ND |
| `K0_keine_freigabe` | Weder Chunking noch Wiedergabe. Quelle wird nicht indexiert. | keine Nutzungslizenz gefunden (Verlags-Copyright, „free to read", „Alle Rechte vorbehalten", keine Angabe, auch mit TDM-Rechtevorbehalt), Lizenz zweifelhaft oder nicht prüfbar, kein rechtmäßiger Zugang |

### 6.2 Ableitung aus den Befunden

```
K0_keine_freigabe, zuerst prüfen, mit k0_grund:
  keine_lizenz_gefunden        Landing Page und Nutzungsbedingungen gelesen, aber keine Lizenz,
                               die eine Nutzung einräumt (lizenz_bezeichnung == null)
  nicht_pruefbar               N1 == nicht_pruefbar: Quelle oder Lizenzangabe nicht erreichbar
  kein_rechtmaessiger_zugang   rechtmaessiger_zugang == false
  n1_traegt_nicht              N1 ∈ {zweifelhaft, gesperrt}

K2_volltextwiedergabe:
  N1 ∈ {frei, gestattet_schranke}  UND  N2 == frei

K1_analyse_und_zitat:
  N1 ∈ {frei, gestattet_schranke}  UND  N2 ∈ {gesperrt, zweifelhaft}
                                        oder N2 == gestattet_schranke mit Grundlage § 51 UrhG
```

**Keine Lizenz heißt K0, auch wenn eine Schranke `N1` tragen würde.** Für Verlagsinhalte ohne Lizenz
kann `N1` über § 44b oder § 60d `gestattet_schranke` sein, und der Befund wird so dokumentiert. Das
Projekt nutzt solche Quellen trotzdem nicht: Die Schranken hängen an Voraussetzungen (Forschungszweck,
Löschpflicht, kein Vorbehalt), die sich ändern können, und das Zitatrecht allein trägt keine
verlässliche Ausgabe. Die Einzelbefunde bleiben vollständig erhalten, damit sich der betroffene Teil
des Korpus bei einer späteren Entscheidung gezielt neu bewerten lässt.

**`keine_lizenz_gefunden` ist nicht `nicht_pruefbar`.** Ersteres ist ein Prüfergebnis: Alles war lesbar,
eine Lizenz gibt es nicht. Letzteres heißt, dass nicht nachgesehen werden konnte. Nur der zweite Fall
ist ein offener Vorgang für die Review-Queue; beim ersten lohnt allenfalls eine Anfrage beim
Herausgeber, die als Handlungsvorschlag in `review_grund` steht.

`lizenz_bezeichnung` trägt nur eine Lizenz, die eine Nutzung einräumt (CC-Lizenzen, dl-de, ODC,
Public Domain Mark) oder die Gemeinfreiheit nach § 5 UrhG. „Alle Rechte vorbehalten", „free to read"
oder ein Copyright-Vermerk sind keine Lizenz; das Feld bleibt dann `null`, der Wortlaut gehört in
`review_grund`.

> [!IMPORTANT]
> **`K0` ist der Vorgabewert, nicht `K1`.** Fehlt das Feld, ist es leer oder trägt es einen unbekannten
> Wert, behandelt das System die Quelle wie `K0` und liefert nichts aus. Diese Richtung ist nicht
> beliebig: Ein Fehler in der Pipeline, ein abgebrochener Prüflauf oder ein nachträglich ergänzter
> Datensatz darf nie dazu führen, dass eine ungeprüfte Quelle als zitierfähig gilt. Der Preis einer
> zu strengen Vorgabe ist eine fehlende Antwort, der Preis einer zu laxen ist eine Rechtsverletzung,
> die niemandem auffällt.

Dass `N2 == zweifelhaft` in `K1` landet und nicht in `K0`, hat einen eigenen Grund: Das Zitatrecht ist
eine **gesetzliche Schranke und wirkt unabhängig von der Lizenz**. Ein Bearbeitungsverbot (`ND`) hindert
das Kleinzitat nicht, weil ein Zitat keine Bearbeitung ist. Zweifel an der weitergehenden
Wiedergabebefugnis schlagen daher nicht auf die Zitatbefugnis durch.

### 6.3 Lizenz und Datenschutz sind zwei getrennte Urteile

Die Freigabeklasse beurteilt **nur** das Urheberrecht. Ein Datenschutzbefund ändert sie nicht: Eine
CC-BY-Quelle mit personenbezogenen Daten behält `K2`, und ihr `datenschutz`-Block weist sie als
aussortiert aus. Würde der Datenschutz in die Klasse einfließen, ließe sich nicht mehr erkennen, ob
eine Quelle wegen der Rechte oder wegen der Personen fehlt, und eine spätere Neubewertung müsste
beides anfassen.

Nachgelagerte Skills und das ausliefernde System verbinden die beiden Urteile mit **einer**
gemeinsamen Regel:

```
nutzbar     = freigabeklasse ∈ {K1, K2}
              UND datenschutz.befund ∉ {personenbezogen, nicht_pruefbar}
wartet      = nutzbar, aber datenschutz.befund == zweifelhaft  → erst nach Review
gesperrt    = alles Übrige
```

Die Regel gilt für jede Quelle und für jeden Datenanhang einzeln mit dessen eigenen Blöcken.

### 6.4 Was `K1` praktisch bedeutet

Das Zitatrecht trägt nicht jede Form der Ausgabe. Drei Voraussetzungen müssen gleichzeitig erfüllt
sein, und zwar durch die **Gestaltung des Systems**, nicht durch eine Eigenschaft der Quelle:

1. **Belegfunktion.** Das Zitat muss eine Aussage stützen und steht nicht für sich. Eine Ausgabe, die
   die Lektüre der Quelle ersetzt, ist kein Zitat mehr.
2. **Umfang begrenzt.** Kleinzitat heißt Ausschnitt, nicht Kapitel. Mehrere aneinandergereihte Chunks
   derselben Quelle können die Grenze gemeinsam überschreiten, auch wenn jeder einzelne sie hält.
3. **Quellenangabe.** § 63 UrhG verlangt sie zwingend. Sie ist **keine Höflichkeit, sondern
   Wirksamkeitsvoraussetzung der Schranke**: Fehlt die Quellenangabe, ist das Zitat unzulässig, auch
   wenn Umfang und Belegfunktion stimmen.

Wie ein nachgelagertes System die Klassen technisch durchsetzt, ist nicht Gegenstand dieser Prüfung.
Die Prüfung liefert die Klasse, die Durchsetzung liegt beim System, das den Korpus ausliefert.

---

## 7. Lizenz-Schnelltabelle

> Diese Tabelle ist eine Arbeitshilfe. Maßgeblich ist der **Lizenztext selbst**, der als Primärquelle
> unmittelbar zugänglich ist. Bei Unklarheit den Legal Code lesen, nicht
> die Kurzfassung des Deeds, und das Ergebnis im Prüfbericht mit der abgerufenen URL belegen.

| Lizenz | `N1` | `N2` | `N3` | Klasse | Anmerkung |
|---|---|---|---|---|---|
| CC0 / Public Domain Mark | frei | frei | frei | `K2` | unproblematisch |
| CC BY | frei | frei | frei | `K2` | Namensnennung technisch sicherstellen |
| CC BY-SA | frei | frei | frei | `K2` | Share-alike kann auf abgeleitete Ausgaben durchschlagen → Review |
| CC BY-ND | frei | **zweifelhaft** | frei | `K1` | Bearbeitungsverbot. Zusammenfassen oder Umformulieren einer Passage kann Bearbeitung sein. |
| CC BY-NC | frei | frei | frei | `K2` | NC durch Prämisse erfüllt, `traegt_ohne_nc_praemisse: false` |
| CC BY-NC-SA | frei | frei | frei | `K2` | NC erfüllt, Share-alike bleibt zu beachten → Review |
| CC BY-NC-ND | frei | **zweifelhaft** | frei | `K1` | NC erfüllt, aber **ND bleibt**. Der Zweifel bei `N2` folgt dem Bearbeitungsverbot, nicht der NC-Klausel. |
| Verlags-Copyright, „free to read" | § 44b/§ 60d-Pfad | **gesperrt** | n/a | `K0` | keine Lizenz: `k0_grund: keine_lizenz_gefunden`. Einzelbefunde trotzdem dokumentieren. |
| Verlags-Copyright mit TDM-Vorbehalt | nur § 60d-Pfad | **gesperrt** | n/a | `K0` | keine Lizenz: `k0_grund: keine_lizenz_gefunden`. Vorbehalt und Abhängigkeit von § 60d trotzdem ausweisen. |
| Repositoriums-Lizenz (Zenodo, OSF) | je nach Angabe | je nach Angabe | je nach Angabe | je nach Angabe | Lizenz steht am Record, nicht an der Plattform |
| „Alle Rechte vorbehalten" / keine Angabe | § 44b/§ 60d-Pfad | **gesperrt** | **zweifelhaft** | `K0` | fehlende Angabe ist keine Freigabe: `k0_grund: keine_lizenz_gefunden` |
| Datenlizenz Deutschland dl-de/by-2-0 | frei | frei | frei | `K2` | Namensnennung, bei Behördendaten häufig |
| Amtliches Werk (§ 5 UrhG) | frei | frei | frei | `K2` | nur Normtext und Entscheidung, nicht jede Behördenpublikation |
| Lizenzangabe nicht erreichbar, Zugang unklar | **nicht_pruefbar** | **nicht_pruefbar** | **nicht_pruefbar** | `K0` | `k0_grund: nicht_pruefbar`, Review-Queue |

**Zur NC-Klausel.** CC definiert `NonCommercial` als „not primarily intended for or directed towards
commercial advantage or monetary compensation". Das Projekt hat festgestellt, dass der Kompass nicht
kommerziell genutzt wird (Prämisse `nutzung_kommerziell: nein`, Abschnitt 1). Die Prüfung legt das
zugrunde: **Die NC-Klausel ist erfüllt, NC-lizenzierte Quellen sind für alle drei Nutzungsarten
nutzbar.**

Zwei Dinge bleiben trotzdem zu tun:

1. **Abhängigkeit mitschreiben.** Jeder Befund, der nur wegen dieser Prämisse trägt, erhält
   `traegt_ohne_nc_praemisse: false`. Ändert sich die Nutzung, lässt sich der betroffene Teil des
   Korpus gezielt herausfiltern, statt alles neu zu prüfen.
2. **NC nicht mit ND und SA verwechseln.** Bei `CC BY-NC-ND` entfällt mit der NC-Frage nicht das
   **Bearbeitungsverbot**, und bei `CC BY-NC-SA` nicht die **Share-alike-Pflicht**. Beide sind von der
   Kommerzialitätsfrage unabhängig und betreffen `N2`, weil das Zusammenfassen oder Umformulieren einer
   Passage eine Bearbeitung sein kann und eine Share-alike-Lizenz auf abgeleitete Ausgaben
   durchschlagen kann. Ein Befund „NC ist geklärt, also alles frei" wäre hier der nächstliegende
   Fehler.

---

## 8. Quellenklassen mit Sonderregeln

| Klasse | Sonderregel |
|---|---|
| **Amtliche Normtexte, Gerichtsentscheidungen** | § 5 UrhG, gemeinfrei. Freigabe für alle Nutzungsarten. Leitsätze eines Verlags sind nicht Teil der Entscheidung. |
| **Behörden- und Ministeriumsberichte (UBA, BASt, BBSR, Difu)** | Nicht automatisch § 5. Nutzungsbedingungen der Behörde prüfen, oft dl-de/by-2-0 oder eine eigene Lizenz. |
| **Verbands- und NGO-Berichte (ADFC, VCD, ECF)** | Regelmäßig vollgeschütztes Material ohne Lizenzangabe. Für `N2` praktisch immer `gesperrt`. Im Zweifel beim Herausgeber anfragen, das ist bei Verbänden oft erfolgreich und gehört in die Review-Queue als Handlungsvorschlag. |
| **Marktstudien, Whitepaper von Unternehmen** | Häufig ausdrückliches Weiterverbreitungsverbot. Immer die letzte Seite lesen. |
| **Preprints (arXiv, SSRN, OSF)** | Lizenz steht am Record und variiert stark. arXiv kennt mehrere Lizenzvarianten einschließlich „arXiv perpetual non-exclusive license", die **keine** Weiterverbreitung durch Dritte gestattet. Nie pauschal behandeln. |
| **Qualitative Datenrepositorien (QDR, ICPSR, GESIS)** | Nachnutzung regelmäßig antrags- oder vertragspflichtig, unabhängig von einer Lizenz. Immer `zweifelhaft` für `N3`, bis der Nutzungsvertrag geprüft ist. |
| **Interviewtranskripte jeder Herkunft** | Lizenzprüfung ersetzt nie Phase 7. Auch ein CC-BY-Transkript kann personenbezogene Daten enthalten, und die Lizenz des Urhebers kann die Einwilligung der Befragten nicht ersetzen. |

> Die letzte Zeile ist die wichtigste Verzahnung der beiden Checks. Eine Lizenz regelt das Verhältnis
> zum Urheber. Sie sagt nichts über das Verhältnis zu den Personen, über die gesprochen wird. Wer
> Phase 6 besteht, hat Phase 7 noch vor sich.

---

## 9. Ausgabeformat

Je Eintrag in `findings_<thema>.json`:

**Beispiel 1: NC-lizenzierte Quelle, durch die Prämisse getragen.**

```json
"lizenz": {
  "geprueft_am": "2026-10-20",
  "lizenz_bezeichnung": "CC BY-NC 4.0",
  "lizenz_beleg_url": "https://zenodo.org/records/1234567",
  "lizenz_quelle": "api_feld",
  "rechtmaessiger_zugang": true,
  "rechtevorbehalt": {
    "gefunden": false,
    "fundort": null,
    "geprueft": ["robots.txt", "agb", "tdmrep"]
  },
  "befund": {
    "N1": {"ergebnis": "frei", "grundlage": "CC BY-NC 4.0", "traegt_ohne_60d": true, "traegt_ohne_nc_praemisse": false},
    "N2": {"ergebnis": "frei", "grundlage": "CC BY-NC 4.0", "traegt_ohne_60d": true, "traegt_ohne_nc_praemisse": false},
    "N3": {"ergebnis": "frei", "grundlage": "CC BY-NC 4.0", "traegt_ohne_60d": true, "traegt_ohne_nc_praemisse": false}
  },
  "freigabeklasse": "K2_volltextwiedergabe",
  "k0_grund": null,
  "review_grund": null,
  "loeschpflicht_notiert": false
}
```

Zu lesen als: Die Quelle ist für alle drei Nutzungsarten frei, aber nur solange die Prämisse
`nutzung_kommerziell: nein` gilt. `traegt_ohne_60d: true` heißt hier, dass die Lizenz selbst trägt und
es auf die Schranke gar nicht ankommt. Eine Löschpflicht besteht nicht, weil die Nutzung nicht auf
§ 44b Abs. 2 gestützt ist.

**Beispiel 2: Verlagsinhalt ohne Lizenz, mit Rechtevorbehalt.**

```json
"lizenz": {
  "geprueft_am": "2026-10-20",
  "lizenz_bezeichnung": null,
  "lizenz_beleg_url": null,
  "lizenz_quelle": "keine",
  "rechtmaessiger_zugang": true,
  "rechtevorbehalt": {
    "gefunden": true,
    "fundort": "robots.txt: GPTBot, CCBot, Google-Extended jeweils Disallow /",
    "geprueft": ["robots.txt", "agb", "tdmrep"]
  },
  "befund": {
    "N1": {"ergebnis": "gestattet_schranke", "grundlage": "§ 60d UrhG (gegen Vorbehalt immun)", "traegt_ohne_60d": false, "traegt_ohne_nc_praemisse": true},
    "N2": {"ergebnis": "gesperrt", "grundlage": null, "traegt_ohne_60d": false, "traegt_ohne_nc_praemisse": true},
    "N3": {"ergebnis": "nicht_pruefbar", "grundlage": null, "traegt_ohne_60d": false, "traegt_ohne_nc_praemisse": true}
  },
  "freigabeklasse": "K0_keine_freigabe",
  "k0_grund": "keine_lizenz_gefunden",
  "review_grund": "Verlags-Copyright ohne Nutzungslizenz. N1 trüge nur über § 60d; das Projekt nutzt Quellen ohne Lizenz nicht. Möglich: Lizenzanfrage beim Verlag.",
  "loeschpflicht_notiert": true
}
```

Beispiel 2 zeigt, warum die Einzelbefunde trotz `K0` vollständig bleiben: Rechtlich trüge `N1` über
§ 60d, und der Rechtevorbehalt ist dokumentiert. Das Projekt nutzt die Quelle trotzdem nicht, weil
keine Lizenz vorliegt. Ändert sich diese Entscheidung, lassen sich alle Quellen mit
`k0_grund: keine_lizenz_gefunden` und `N1: gestattet_schranke` gezielt herausfiltern. Das RAG-System
liest ausschließlich `freigabeklasse`, nicht die drei Einzelbefunde.

Jeder `zweifelhaft`-, `gesperrt`- und `nicht_pruefbar`-Befund erzeugt **zusätzlich** einen Eintrag in
`meta.review_queue` beziehungsweise `meta.aussortiert`. Ausgenommen sind Befunde einer Quelle mit
`k0_grund: keine_lizenz_gefunden`: Sie ist abschließend geprüft, und es gibt nichts zu entscheiden. Ein Flag am Eintrag allein genügt nicht, weil
niemand 45 Einträge durchsieht, um die 6 Problemfälle zu finden.

**Auch ein `frei`-Befund mit `traegt_ohne_nc_praemisse: false` gehört nicht in die Review-Queue.** Er
ist kein offener Vorgang, sondern eine dokumentierte Abhängigkeit. Die Queue bliebe sonst voll mit
Einträgen, zu denen nichts zu entscheiden ist, und würde genau dadurch unbrauchbar.

---

## 10. Bekannte Lücken dieser Prüfung

Offen ausweisen, nicht kaschieren. Diese Punkte gehören in den Limitationen-Abschnitt des Protokolls:

| Lücke | Wirkung |
|---|---|
| Prüfmaßstab nicht juristisch gegengeprüft | Ableitung aus Norm- und Lizenztexten, keine anwaltliche Prüfung |
| Wissenschaftlicher Forschungszweck des produktiven Kompass-Einsatzes (§ 60d UrhG) nicht geklärt | Der gesamte Forschungspfad hängt daran; `traegt_ohne_60d` macht den betroffenen Teil filterbar |
| Gemeinnützigkeitsrecht (§§ 51 ff. AO) nicht ausgearbeitet | Die NC-Frage ist durch Projektprämisse entschieden. Kippt die Prämisse, fehlt die Beurteilungsgrundlage. |
| §§ 87a ff. UrhG nicht ausgearbeitet | Datensatz-Entnahmen nicht abschließend beurteilbar |
| Grenzen des Zitatrechts (§ 51 UrhG) nur grob umrissen | Umfangsgrenzen für `K1` nicht quantifiziert |
| Ob § 60d vergütungsfrei ist | offen |
| Post-hoc-Vorbehalt, Machine Unlearning, Modellgewichte | rechtlich ungeklärt |

Die § 60d-Prämisse ist die tragende Lücke. Den Hinweis darauf am Ende des Protokolls wiederholen.

---

## Primärquellen

- UrhG: §§ 5, 15, 16, 19a, 31, 44b, 51, 60d, 63, 87a ff., https://www.gesetze-im-internet.de/urhg/
- Richtlinie (EU) 2019/790 (CDSM-RL), Art. 3, 4, 7 und ErwGr. 18,
  https://eur-lex.europa.eu/eli/dir/2019/790/oj
- Creative-Commons-Lizenztexte (Legal Code), https://creativecommons.org/licenses/
- Datenlizenz Deutschland 2.0, https://www.govdata.de/dl-de/by-2-0
- RFC 9309 (Robots Exclusion Protocol), https://www.rfc-editor.org/rfc/rfc9309
- W3C TDM Reservation Protocol (TDMRep), https://www.w3.org/community/tdmrep/
- GPAI Code of Practice, Kapitel Copyright, Measures 1.2 und 1.3
