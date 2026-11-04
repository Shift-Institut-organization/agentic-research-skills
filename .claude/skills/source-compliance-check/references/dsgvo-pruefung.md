# DSGVO-Personenbezugsprüfung (Phase 7)

Prüfprogramm für die Frage, ob eine recherchierte Quelle oder ein Datenanhang personenbezogene Daten
im Sinne der DSGVO enthält.

**Rechtsstand dieser Datei:** 2026-10-20.

> [!WARNING]
> **Zwei Vorbehalte zum Prüfmaßstab, die vor jeder Anwendung bekannt sein müssen.**
>
> 1. Der operative Kern, der Dreikriterientest, stammt aus den **EDPB Guidelines 02/2026 zur
>    Anonymisierung, Version 1.0, angenommen am 07.07.2026 für die öffentliche Konsultation**. Eine
>    finale Fassung stand bei Abfassung dieser Datei aus. **Die Randnummern können sich verschieben.**
>    Sie sind hier Orientierung, nicht zitierfähige Fundstelle für Dritte.
> 2. **Der Maßstab ist nicht juristisch gegengeprüft.** Er ist aus DSGVO, EuGH-Rechtsprechung und
>    den EDPB-Guidelines abgeleitet (Liste am Ende) und nutzbar, ersetzt aber keine
>    datenschutzrechtliche Beratung.

## Inhalt

1. [Schutzziel: was diese Prüfung leisten soll](#1-schutzziel-was-diese-prüfung-leisten-soll)
2. [Prüfgegenstand](#2-prüfgegenstand)
3. [Der Maßstab: reasonably likely means](#3-der-maßstab-reasonably-likely-means)
4. [Perspektivenprinzip](#4-perspektivenprinzip)
5. [Dreikriterientest](#5-dreikriterientest)
6. [Vertrauensvermutung bei erklärter Anonymisierung](#6-vertrauensvermutung-bei-erklärter-anonymisierung)
7. [Red-Flag-Katalog](#7-red-flag-katalog)
8. [Art. 9: Verschärfung, kein eigener Ausschlussgrund](#8-art-9-verschärfung-kein-eigener-ausschlussgrund)
9. [Screening nach Quellenklasse](#9-screening-nach-quellenklasse)
10. [Entscheidungsbaum](#10-entscheidungsbaum)
11. [Ausgabeformat](#11-ausgabeformat)
12. [Sorgfaltsdokumentation](#12-sorgfaltsdokumentation)
13. [Bekannte Lücken und Restrisiken](#13-bekannte-lücken-und-restrisiken)

---

## 1. Schutzziel: was diese Prüfung leisten soll

Diese Prüfung verfolgt ein klar umrissenes Ziel, und die Kenntnis dieses Ziels entscheidet über ihre
richtige Anwendung:

> **Der Kompass soll mit seinem Quellenkorpus nicht in den Anwendungsbereich der DSGVO fallen.**
> Erreicht wird das dadurch, dass keine personenbezogenen Daten in den Datenpool gelangen. Quellen,
> die solche Daten enthalten, werden aussortiert. Eine Abwägung von Rechtsgrundlagen findet nicht
> statt (Projektentscheidung vom 2026-10-20).

Daraus folgt zweierlei, und beides ist gleich wichtig:

**Erstens, warum ausgeschlossen statt abgewogen wird.** Wer keine personenbezogenen Daten verarbeitet,
braucht keine Rechtsgrundlage, keine Zweckbindung, keine Informationspflichten gegenüber Betroffenen,
kein Löschkonzept, keine Datenschutz-Folgenabschätzung und keinen Eintrag im Verzeichnis von
Verarbeitungstätigkeiten für diesen Verarbeitungsstrang. Der Verzicht auf einen Teil des Materials
erkauft den Verzicht auf den gesamten Apparat, der sonst daran hinge.

**Zweitens, warum die Prüfung nicht maximal streng sein darf.** Das Ziel ist Absicherung, nicht
Vorsicht um ihrer selbst willen. Eine Prüfung, die jede theoretisch denkbare Re-Identifizierung zum
Ausschlussgrund erhebt, sortiert praktisch jedes qualitative Material aus und zerstört damit genau den
Bestand, für den der Kompass gebaut ist. Sie wäre zudem **rechtlich falsch**: Art. 4 Nr. 1 DSGVO
i.V.m. ErwGr. 26 fragt nach Identifizierung mit *vernünftigerweise anzuwendenden Mitteln*, nicht nach
theoretischer Möglichkeit.

Der Prüfauftrag lautet deshalb:

> **Eine Prüfung, die dem Sorgfaltsmaßstab genügt und nicht fahrlässig ist. Erklärten
> Anonymisierungen von Interviewtranskripten wird so weit vertraut, wie das im Rahmen einer solchen
> Prüfung vertretbar ist. Interviewdaten sollen möglichst erhalten bleiben.**

Das ist kein Kompromiss zwischen Recht und Nutzen, sondern die zutreffende Anwendung des Maßstabs. Die
operative Umsetzung steht in Abschnitt 6 (Vertrauensvermutung) und Abschnitt 7 (Red-Flag-Katalog). Was
die Prüfung dokumentieren muss, damit sie dem Sorgfaltsmaßstab genügt, steht in Abschnitt 12.

---

## 2. Prüfgegenstand

### Nicht erfasst: bibliographische Metadaten

Autorennamen, Affiliationen, ORCID und Korrespondenzadressen **sind** personenbezogene Daten. Sie sind
es aber bei jeder wissenschaftlichen Quelle ausnahmslos. Würde die Prüfung sie erfassen, lautete jeder
Befund „personenbezogen", und der Korpus wäre leer. Ein Check, der immer dasselbe sagt, wird nach drei
Läufen ignoriert.

Die Verarbeitung bibliographischer Angaben wird daher **einmal zentral** auf eine Rechtsgrundlage
gestellt (Zitier- und Nachweiszweck) und ist nicht Gegenstand der Einzelfallprüfung. Einmal im
Protokoll vermerken, nicht je Quelle.

### Nicht erfasst: Selbstauskünfte von Autorinnen und Autoren

Vor allem qualitative Arbeiten enthalten oft einen Absatz zur eigenen Position (Positionality), in
dem die namentlich genannte Person Angaben über sich selbst macht, auch zu Art.-9-Kategorien wie
Herkunft, Religion oder sexueller Orientierung. Solche Angaben werden wie bibliographische Metadaten
behandelt. Sie lösen **keine Red Flag** aus, die Quelle bleibt nutzbar. Das Schutzziel dieser Prüfung
sind Personen, die nicht selbst entschieden haben, erkennbar zu sein; hier hat die Person es selbst
veröffentlicht.

Drei Grenzen:

- **Nur über sich selbst.** Was eine Autorin über Befragte, Kollegen oder andere Dritte schreibt,
  bleibt voll Gegenstand der Prüfung.
- **Dokumentieren.** Die Fundstelle steht in `datenschutz.autor_selbstauskunft`.
- **Nicht weiterverwenden.** Der Absatz fließt nicht in Stakeholder-Analysen oder Personas ein.

Die Angaben bleiben personenbezogene Daten. Die Regel ist eine Projektentscheidung vom 2026-11-04 und
noch nicht juristisch gegengeprüft.

### Erfasst: Personenbezug im Inhalt

Gegenstand sind Angaben über Personen **in** der Quelle:

| Fundort | Typische Erscheinungsform |
|---|---|
| Interviewtranskripte | Namen, Orte, Arbeitgeber, Familienverhältnisse, Krankheitsgeschichten |
| Fallbeschreibungen und Vignetten | reale Einzelfälle |
| Survey-Rohdaten | Merkmalskombinationen, offene Antwortfelder, Freitextkommentare |
| Schlüssellisten | Zuordnung von Pseudonym zu Klarnamen |
| Qualitative Zitate im Volltext | O-Töne mit Kontextangaben |
| Behörden- und Gerichtsdokumente | Beteiligte, Betroffene, Beschäftigte |
| Danksagungen und Interessenkonflikte | Dritte, Ansprechpartner |

Die letzte Zeile wird regelmäßig vergessen und ist bei Volltext-Einbettung einschlägig: Wer das ganze
PDF indexiert, indexiert auch die Danksagung. Sie ist allerdings ein Fall für die zentrale
Metadaten-Rechtsgrundlage, nicht für die Aussortierung der Quelle.

---

## 3. Der Maßstab: reasonably likely means

Normativer Anker: **Art. 4 Nr. 1 DSGVO i.V.m. ErwGr. 26.** Anonymität liegt vor, wenn die
Wahrscheinlichkeit einer Reidentifizierung mit vernünftigerweise anzuwendenden Mitteln nur
**unerheblich** („insignificant") ist. Siehe EuGH C-582/14 (Breyer) und C-413/23 P (EDPS/SRB).

**Das ist der entscheidende Satz dieser Datei**, weil er die Prüfung sowohl begrenzt als auch trägt:
Gefragt ist nicht, ob eine Identifizierung denkbar ist, sondern ob sie mit vertretbarem Aufwand
wahrscheinlich ist. Ein Transkript, aus dem Namen, Orte, Arbeitgeber und markante Einzelereignisse
entfernt wurden, ist nicht deshalb personenbezogen, weil sich jemand mit genügend Vorwissen und
genügend Aufwand theoretisch eine Zuordnung konstruieren könnte.

### Fünf objektive Faktoren (Rz. 29)

| Faktor | Inhalt | Praktische Lesart für Transkripte |
|---|---|---|
| a | Dateneigenschaften: Aggregationsgrad, Einzigartigkeit, Genauigkeit | Wie grob sind die verbliebenen Angaben? „Großstadt" statt Straßenname, „40 bis 50" statt Geburtsjahr |
| b | Kontext: bestehende Zugangsbeschränkungen | Offenes Repositorium oder Zugang auf Antrag |
| c | verfügbare Zusatzinformation | Gibt es eine öffentlich zugängliche Teilnehmerliste? |
| d | Aufwand: Zeit, Kosten, Arbeit | Wäre eine Zuordnung Recherchearbeit oder ein Blick? |
| e | Stand der Technik plus vorhersehbare Entwicklung | Periodische Neubewertung, kein „once anonymous, always anonymous" (Rz. 35) |

### Drei Regeln, die Fehlschlüsse abschneiden

| Regel | Rz. | Inhalt |
|---|---|---|
| **Motivationsverbot** | 31 | Die mangelnde *Motivation* eines Angreifers darf nicht als Faktor herangezogen werden. „Niemand hat ein Interesse daran" zählt nicht. |
| **Rechtliche Verbote: widerlegbar** | 32 bis 33 | Gesetzliche Re-Identifizierungsverbote sind als Barriere anzuerkennen (Breyer, C-582/14 Rz. 46), aber widerlegbar, wenn die Norm nicht wirksam durchgesetzt wird. |
| **Vertragliche Verbote: genügen nicht** | 34 | Ein Vertrag, der Re-Identifizierung untersagt, ersetzt keine technische oder faktische Maßnahme. |

Das Motivationsverbot (Rz. 31) begrenzt die Vertrauensvermutung des Abschnitts 6 nach unten: Die
Vermutung stützt sich auf die **Beschaffenheit der Daten**, nicht darauf, dass niemand nachsehen will.

---

## 4. Perspektivenprinzip

Anonymität ist keine objektive Eigenschaft eines Datensatzes, sondern perspektivabhängig: Dieselben
Daten können für die eine Stelle anonym und für eine andere personenbezogen sein (Rz. 6 bis 15). Für Auftragsverarbeiter gilt die Perspektive des Verantwortlichen,
eine funktionale Ausdehnung des Verarbeiterbegriffs (Rz. 15).

### Die drei Prüfperspektiven

| # | Perspektive | Prüffrage |
|---|---|---|
| P1 | **SHIFT als Verantwortlicher** beim Einlesen | Kann SHIFT mit den verfügbaren Mitteln identifizieren? |
| P2 | **Nutzende des Kompass** als Empfänger ausgelieferter Passagen | Kann eine Nutzerin aus einer Passage identifizieren? |
| P3 | **Potenzielle weitere Empfänger** (Chain of Means, Rz. 20 bis 21) | Begründet schon die mögliche Weitergabe Personenbezug? |

**Zu P2, mit der gebotenen Zurückhaltung.** Bei ortsbezogenen Beteiligungsverfahren sitzen Nutzende
mitunter im selben sozialen Raum wie die Befragten. Das ist ein **Faktor nach Rz. 29 lit. c**
(verfügbare Zusatzinformation), kein Automatismus. Ortskenntnis macht ein Transkript nur dann
zuordenbar, wenn im Text noch Angaben stehen, an die sie andocken kann. Sind Ort, Arbeitgeber und
markante Ereignisse entfernt, läuft auch lokales Vorwissen ins Leere.

Praktisch heißt das: P2 ist zu prüfen, wenn das Material **lokalisierbare Residuen** enthält (Red Flags
R2, R3, R4). Sie ist nicht als generelle Vermutung anzusetzen, Transkripte aus kommunalen Verfahren
seien zuordenbar.

### Chain of Means (Rz. 20 bis 21)

Übernahme aus EuGH C-319/22 (Scania) und C-413/23 P (EDPS/SRB): Erfasst ist auch die mittelbare
Identifizierung über Datenweitergaben. Flankierend EuGH C-604/22 (IAB Europe, ECLI:EU:C:2024:214,
07.03.2024): Maßgeblich ist die Identifizierung mit vertretbarem Aufwand, nicht aus der Sicht des
konkreten Datenhalters allein, sondern unter Einbeziehung der Mittel, die Dritte rechtmäßig
hinzufügen können.

Auch hier gilt der Zusatz „mit vertretbarem Aufwand". Die Kette ist erst geschlossen, wenn ein
realistischer Empfänger über reale Zusatzinformation verfügt, nicht schon dann, wenn ein Empfänger
denkbar ist.

---

## 5. Dreikriterientest

Der fachliche Standard hinter dem Red-Flag-Katalog. Personenbezug ist ausgeschlossen, wenn alle drei
Kriterien kumulativ erfüllt sind (EDPB Guidelines 02/2026, Kap. 3).

| Kriterium | Rz. | Prüffrage |
|---|---|---|
| **No Record Isolation** | 54 bis 57 | Lässt sich ein Datensatz über eine einzigartige Merkmalskombination herausgreifen? |
| **No Linkage** | 58 bis 65 | Lassen sich Datensätze derselben Person über Quellen hinweg verknüpfen? |
| **No Inference** | 66 bis 82 | Lässt sich eine spezifische und bedeutsame Aussage über eine Person ableiten? |

### Bedeutsamkeits-Trias zu No Inference (Rz. 66 bis 82)

Eine Inferenz ist nur bedeutsam, wenn sie **alle drei** Merkmale erfüllt: Sie beruht auf den
Ursprungsdaten und nicht auf Allgemeinwissen, sie kann Rechte oder Interessen berühren, und sie
unterscheidet die Person von anderen.

Beispiele: Aus „Grün ist eine beliebte Farbe" auf „Connor mag Grün" zu schließen verletzt das
Kriterium nicht. Trajektoriendaten, aus denen Wohn- und Arbeitsadresse hervorgehen, verletzen es.

Diese Trias hält die Prüfung operabel. Ohne sie landet jede Aussage über Menschen im Befund
„personenbezogen", weil sich zu jeder Angabe irgendeine Inferenz konstruieren lässt.

### Kontaminationsregel

Enthält ein Datensatz **teilweise** personenbezogene Einträge, ist er insgesamt als personenbezogen zu
behandeln, solange keine getrennte Verarbeitung erfolgt.

> Gestützt auf EuGH C-252/21 (Meta v. Bundeskartellamt), Rz. 89, in analoger Anwendung. Die
> Fundstelle ist nicht gegengeprüft. Nicht ungeprüft gegenüber Dritten zitieren.

**Getrennte Verarbeitung ist der Regelfall, nicht die Ausnahme.** Weil die Kontaminationsregel an die
fehlende Trennung anknüpft, greift sie nicht, wenn ein belasteter Anhang entfernt und der Rest
behalten wird. Genau so ist in Schritt 6 des Entscheidungsbaums zu verfahren: **Nicht die Quelle
aussortieren, sondern den Anhang.** Ein Aufsatz verliert seine Nutzbarkeit nicht dadurch, dass im
Supplement eine Teilnehmerliste liegt.

---

## 6. Vertrauensvermutung bei erklärter Anonymisierung

Der operative Kern der Entscheidung aus Abschnitt 1.

### 6.1 Die Vermutung

**Erklärt die Quelle, dass die Daten anonymisiert wurden, wird dem gefolgt, sofern keine Red Flag aus
Abschnitt 7 vorliegt.** Der Befund lautet dann `kein_personenbezug`.

Voraussetzung ist, dass alle drei Bedingungen erfüllt sind:

| # | Bedingung | Zu dokumentieren |
|---|---|---|
| V1 | **Erklärung vorhanden.** Die Quelle beschreibt die Anonymisierung, etwa im Methodenteil, im Data Availability Statement oder in der Datensatzbeschreibung. | Fundstelle |
| V2 | **Erklärende Stelle ist einschlägig qualifiziert.** Forschungseinrichtung, kuratiertes Repositorium (QDR, GESIS, ICPSR, Harvard Dataverse, OSF, Zenodo mit institutioneller Community), Behörde oder etablierter Verband. | Herausgeber |
| V3 | **Stichprobe zeigt keine Red Flag.** Umfang nach Abschnitt 12.1. | Umfang und Ergebnis |

Liegen V1 bis V3 vor, ist die Prüfung bestanden. Es ist **nicht** zusätzlich zu begründen, warum eine
Re-Identifizierung ausgeschlossen sei. Die Vermutung trägt.

### 6.2 Warum das trägt

Drei Gründe, die zusammen die Vermutung rechtfertigen und die in der Sorgfaltsdokumentation benannt
werden:

1. **Der Erklärende kennt die Rohdaten, der Prüfer nicht.** Wer anonymisiert hat, weiß, welche Angaben
   entfernt wurden. Ein nachgelagerter Prüfer sieht nur das Ergebnis. Die Erklärung ist damit die
   bessere Informationsquelle, nicht die schlechtere.
2. **Forschungsanonymisierung unterliegt eigener Kontrolle.** Ethikkommissionen,
   Datenschutzbeauftragte der Einrichtungen und die Kuratierung der Repositorien prüfen vorgelagert.
   Diese Kontrolle ist faktisch, nicht bloß vertraglich, und fällt daher nicht unter Rz. 34.
3. **Der Maßstab verlangt nicht mehr.** Nach Rz. 29 ist auf vernünftigerweise anzuwendende Mittel
   abzustellen. Eine fachgerecht durchgeführte Anonymisierung durch eine qualifizierte Stelle senkt
   die Re-Identifizierungswahrscheinlichkeit auf das Niveau, das ErwGr. 26 als unerheblich einstuft.

### 6.3 Was die Vermutung nicht deckt

- **Keine Erklärung, aber O-Töne mit Kontext** im Text: keine Vermutung, reguläre Prüfung nach
  Abschnitt 5.
- **Erklärung durch eine nicht einschlägige Stelle**, etwa ein Unternehmens-Whitepaper ohne
  Methodenangabe: keine Vermutung.
- **Red Flag vorhanden:** Die Vermutung ist widerlegt. Der konkrete Fund schlägt die abstrakte
  Erklärung. Das ist der Punkt, an dem die Prüfung nicht fahrlässig wird: Sie vertraut, aber sie sieht
  vorher nach.

> [!NOTE]
> Eine frühere Fassung dieser Datei verlangte, das Etikett „anonymisiert" grundsätzlich nicht zu
> übernehmen, und behandelte Transkripte als regelmäßig personenbezogen. Das war an diesem Prüfmaßstab
> gemessen zu streng und hätte den qualitativen Bestand des Kompass praktisch beseitigt. Maßgeblich
> ist die hier beschriebene Vermutung mit Red-Flag-Vorbehalt.

---

## 7. Red-Flag-Katalog

Das Arbeitsmittel der Prüfung. Gesucht wird nach **konkreten Funden im Text**, nicht nach denkbaren
Angriffsszenarien. Jede Red Flag widerlegt die Vertrauensvermutung und führt zum Befund
`personenbezogen`, damit zur Aussortierung.

| # | Red Flag | Warum |
|---|---|---|
| **R1** | **Klarnamen, Initialen mit Zusatzangabe, Namen kleiner Betriebe** | Direkte Identifizierung. Auch „Herr M. vom Planungsbüro K. in Würzburg". |
| **R2** | **Ortsangaben unterhalb der Gemeindeebene** | Straße, Quartier, Haltestelle, Schulname, Betriebsadresse. Der Anknüpfungspunkt, an dem lokales Vorwissen (P2) andockt. |
| **R3** | **In ihrer Organisation singuläre Funktionsbezeichnungen** | „Die Leiterin des Tiefbauamts in X" ist eine Person, keine Rolle. Gilt auch für kleine Vereine und Fachabteilungen. |
| **R4** | **Datierbare Einzelereignisse mit Öffentlichkeitsbezug** | „Nach dem Unfall an der Kreuzung im März" verknüpft mit Presseberichten. |
| **R5** | **Sehr kleine Grundgesamtheit plus mehrere Merkmale** | Richtwert: N unter 10 und zugleich drei oder mehr demografische Angaben je Person. |
| **R6** | **Zugängliche Schlüsselliste** | Veröffentlichte Zuordnung von Pseudonym zu Klarnamen oder Teilnehmerliste mit Namen. Abgrenzung unten. |
| **R7** | **Audio- oder Videoaufnahmen statt Text** | Stimme und Gesicht sind eigenständige Identifikatoren. |
| **R8** | **Feingranulare Geo- oder Bewegungsdaten** | Trajektorien, GPS-Tracks, Wegetagebücher mit Adressbezug. Typischer Fall einer Verletzung von No Inference (Abschnitt 5). |
| **R9** | **Art.-9-Angaben in Verbindung mit R1 bis R5** | Verschärfung, siehe Abschnitt 8. |

### Abgrenzung zu R6: Codebook ist nicht gleich Schlüsselliste

Ein häufiger und folgenreicher Fehlgriff:

| Artefakt | Inhalt | Bewertung |
|---|---|---|
| **Codebook** (Regelfall) | Variablendefinitionen, Kategoriensystem, Kodierregeln, Ausprägungen | **Keine Red Flag.** Enthält keine Personendaten. |
| **Schlüsselliste** | Zuordnung Pseudonym zu Klarnamen oder Kontaktdaten | **Red Flag R6**, sofern zugänglich. |
| **Nicht veröffentlichte Schlüsselliste beim Forschenden** | existiert, aber für niemanden abrufbar | Siehe unten. |

Das in der qualitativen Forschung übliche Codebook ist ein **Auswertungsinstrument**, keine
Zuordnungstabelle. Es als Schlüssel zu behandeln, würde praktisch jeden sorgfältig dokumentierten
qualitativen Datensatz aussortieren, und zwar gerade die am besten dokumentierten.

**Zur verbleibenden Schlüsselliste beim Forschenden.** Behält eine Forschungseinrichtung die
Zuordnungsliste intern, ohne sie zu veröffentlichen, ist sie für SHIFT und für Kompass-Nutzende nicht
mit vernünftigerweise anzuwendenden Mitteln erreichbar. Nach Rz. 29 lit. b und lit. c führt das zum
Befund `kein_personenbezug`, sofern keine andere Red Flag vorliegt.

> [!CAUTION]
> **Dies ist die rechtlich am stärksten umstrittene Einzelfestlegung dieser Datei.** Die Breyer-Linie
> behandelt Daten als personenbezogen, wenn die Zusatzinformation bei einem Dritten liegt und
> rechtmäßig erlangt werden kann. Gegen die Einordnung hier spricht also ein ernstzunehmendes
> Argument. Dafür spricht, dass Forschungseinrichtungen die Liste weder herausgeben dürfen noch
> herausgeben, womit sie faktisch und nicht nur vertraglich gesperrt ist, und dass Rz. 34 allein
> vertragliche Zusagen entwertet.
>
> Die Festlegung ist eine **bewusste Risikoentscheidung des Projekts** zugunsten des Erhalts von
> Interviewdaten. Sie steht als solche in Abschnitt 13.1 unter den Restrisiken, damit niemand sie für
> gesicherte Rechtslage hält.

---

## 8. Art. 9: Verschärfung, kein eigener Ausschlussgrund

> [!WARNING]
> **Den vollständigen Katalog nach dem Normtext von Art. 9 Abs. 1 DSGVO prüfen.** Verkürzte Listen
> lassen regelmäßig religiöse und weltanschauliche Überzeugungen sowie die Gewerkschaftszugehörigkeit
> weg.

Vollständig zu screenen: rassische und ethnische Herkunft · politische Meinungen · religiöse und
weltanschauliche Überzeugungen · Gewerkschaftszugehörigkeit · genetische Daten · biometrische Daten
zur eindeutigen Identifizierung · Gesundheitsdaten · Daten zum Sexualleben und zur sexuellen
Orientierung. Dazu Art. 10 (strafrechtliche Verurteilungen und Straftaten).

### Die entscheidende dogmatische Einordnung

**Art. 9 setzt personenbezogene Daten voraus.** Ein anonymes Transkript, in dem jemand über seine
Dialysetermine spricht, enthält **keine Gesundheitsdaten im Sinne der DSGVO**, weil es überhaupt keine
personenbezogenen Daten enthält. Die DSGVO ist auf anonyme Daten nicht anwendbar, und damit auch
Art. 9 nicht.

Daraus folgt für dieses Prüfprogramm:

- **Art.-9-Inhalte sind kein eigenständiger Aussortierungsgrund.** Wer das anders handhabte, verlöre
  genau die Quellen, die für den Kompass inhaltlich am wichtigsten sind: Interviews mit Menschen,
  deren Mobilität durch Krankheit, Behinderung, Alter oder Herkunft eingeschränkt ist. Das sind die
  *moral patients*, um derentwillen das Verfahren existiert.
- **Art.-9-Inhalte verschärfen den Prüfmaßstab.** Weil die Folgen einer Re-Identifizierung schwerer
  wiegen, ist die Anonymisierung strenger zu prüfen: größerer Stichprobenumfang (Abschnitt 12.1),
  Red Flag R9, und bei verbleibender Unsicherheit der Befund `zweifelhaft` statt
  `kein_personenbezug`.

**Kumulation bei tatsächlichem Personenbezug.** Liegt Personenbezug vor *und* sind Art.-9-Kategorien
betroffen, wird die Quelle aussortiert und die Kategorie in `art9_kategorien` dokumentiert. Die
Dokumentation ist wichtig, weil im Nachhinein belegbar sein muss, dass sensible Daten gerade **nicht**
in den Pool gelangt sind.

**Mittelbare Offenbarung reicht.** EuGH C-184/20 (Vyriausioji): Auch die mittelbare Offenbarung
sensibler Daten ist erfasst. Wer über seinen Arbeitsweg zur Dialyse spricht, offenbart
Gesundheitsdaten, ohne eine Diagnose zu nennen. Relevant für R9, sobald Personenbezug besteht.

**Öffentlich ist kein Freibrief.** EuGH C-446/21 (Schrems/Meta): Art. 9 Abs. 2 lit. e ist eng
auszulegen.

---

## 9. Screening nach Quellenklasse

Die Klasse der Quelle bestimmt den Prüfaufwand. Dieses Screening ersetzt die Prüfung nicht, es
dimensioniert sie.

| Klasse | Erwartung | Vorgehen |
|---|---|---|
| Journal-Artikel, quantitativ, aggregierte Statistik | Treffer unwahrscheinlich | Stichprobe: Methodenteil, Danksagung, Anhangsverzeichnis |
| Journal-Artikel mit qualitativen O-Tönen | Treffer möglich | Zitatpassagen samt Kontextangaben auf R1 bis R5 prüfen |
| **Interviewtranskripte mit Anonymisierungserklärung** | **Vermutung greift** | V1 bis V3 prüfen, Red-Flag-Stichprobe nach Abschnitt 12.1 |
| Interviewtranskripte **ohne** Erklärung | Treffer wahrscheinlich | Vollprüfung nach Abschnitt 5 |
| Survey-Mikrodaten | Treffer möglich | Merkmalskombinationen auf R5, Freitextfelder gesondert |
| Codebooks | in der Regel unbedenklich | auf Schlüssellisten-Charakter prüfen (R6), nicht pauschal als Schlüssel werten |
| Kommunal- und Behördenberichte | Treffer möglich | Fallbeschreibungen, Beteiligtenlisten, Anhörungsprotokolle |
| Verbands- und NGO-Berichte | Treffer möglich | Fallbeispiele und Porträts |
| Normtexte, Gesetze | Treffer unwahrscheinlich | kein Screening nötig |
| Gerichtsentscheidungen | Treffer möglich trotz Schwärzung | Beteiligte, Zeugen, Sachverhaltsdetails |
| Software, Code-Repositorien | Treffer möglich | Commit-Metadaten, Beispieldaten, Testfixtures |
| Audio, Video | **R7, immer** | aussortieren, sofern nicht nachweislich stimmverfremdet |

*Die Einordnung von Interviewtranskripten und Survey-Rohdaten ist eine Ableitung aus dem
Dreikriterientest, keine ausdrückliche Vorgabe der Quellen.*

---

## 10. Entscheidungsbaum

Je Quelle **und je Datenanhang** durchlaufen. Erste zutreffende Zeile gewinnt.

```
SCHRITT 0: Gegenstand eingrenzen
  nur bibliographische Metadaten betroffen
    → kein_personenbezug (außerhalb des Prüfgegenstands, Abschnitt 2)
  Selbstauskünfte der Autorin oder des Autors über sich selbst
    → ausklammern, in autor_selbstauskunft dokumentieren, Rest der Quelle weiter prüfen
  Material noch nicht beschafft, Beschaffung aber möglich
    → ausstehend, Review-Queue, Prüfung später nachholen
  sonst weiter

SCHRITT 1: Klassen-Screening (Abschnitt 9)
  Klasse "Treffer unwahrscheinlich", Stichprobe negativ
    → kein_personenbezug, Stichprobenumfang dokumentieren
  Klasse Audio/Video
    → personenbezogen (R7), AUSSORTIEREN
  sonst weiter

SCHRITT 2: Einsehbar?
  weder Volltext noch Abstract noch Methodenangaben abrufbar
    UND Klasse mit realistischem Risiko (Transkript, Mikrodaten, Fallbeschreibung)
      → nicht_pruefbar, AUSSORTIEREN
    UND Klasse ohne realistisches Risiko (quantitative Studie, Normtext, Review)
      → kein_personenbezug auf Klassengrundlage, Begründung dokumentieren
  sonst weiter

SCHRITT 3: Red-Flag-Pruefung (Abschnitt 7)
  eine oder mehrere Red Flags gefunden
    → personenbezogen, AUSSORTIEREN, gefundene Flags mit Fundstelle benennen
  sonst weiter

SCHRITT 4: Vertrauensvermutung (Abschnitt 6)
  V1 Erklärung vorhanden UND V2 Stelle einschlägig UND V3 Stichprobe ohne Flag
    → kein_personenbezug, Vermutung und Fundstelle dokumentieren, FERTIG
  sonst weiter

SCHRITT 5: Dreikriterientest je Perspektive P1, P2, P3 (Abschnitt 5)
  ein Kriterium für eine Perspektive verletzt
    → personenbezogen, AUSSORTIEREN, verletztes Kriterium und Perspektive benennen
  alle drei Kriterien für alle drei Perspektiven erfüllt
    → weiter zu Schritt 6
  nicht sicher beurteilbar
    → zweifelhaft, meta.review_queue (Tatsachenfrage, siehe unten)

SCHRITT 6: Kontaminationspruefung
  Anhang personenbezogen, Hauptquelle nicht
    → NUR den Anhang aussortieren, Hauptquelle bleibt (getrennte Verarbeitung)
  Hauptquelle selbst teilweise personenbezogen, keine Trennung möglich
    → personenbezogen für die ganze Quelle, AUSSORTIEREN
  sonst
    → kein_personenbezug

QUERSCHNITT:
  kein_personenbezug                     → bleibt im Korpus
  personenbezogen / nicht_pruefbar       → meta.aussortiert, typ "datenschutz"
  zweifelhaft                            → meta.review_queue
  ausstehend                             → meta.review_queue, Prüfung nachholen
```

### Was geprüft, aber nicht abgewogen wird

Die **Tatsachenfrage** „enthält diese Quelle personenbezogene Daten?" kann unklar bleiben. Dann lautet
der Befund `zweifelhaft` und die Quelle geht in die Review-Queue. Das ist **keine**
Rechtsgrundlagenprüfung, sondern die Feststellung des Sachverhalts, ohne die der Check nicht
entscheiden kann.

Abgeschafft ist allein die Nachfrage „wir haben hier zwar Personenbezug, aber vielleicht trägt eine
Rechtsgrundlage". Die wird nicht mehr gestellt.

---

## 11. Ausgabeformat

Je Eintrag und **zusätzlich je Datenanhang**:

**Beispiel 1: Transkript, Vertrauensvermutung greift.**

```json
"datenschutz": {
  "geprueft_am": "2026-10-20",
  "pruefumfang": "volltext",
  "stichprobe_beschreibung": "Methodenteil vollständig, je Transkript erste und letzte 500 Wörter, Volltextsuche nach Ortsangaben, Eigennamen und Organisationsbezeichnungen",
  "befund": "kein_personenbezug",
  "grundlage": "vertrauensvermutung",
  "anonymisierungserklaerung": {
    "vorhanden": true,
    "fundstelle": "Methodenteil S. 4 und Data Availability Statement",
    "erklaerende_stelle": "Universität X, Datensatz kuratiert über GESIS",
    "stelle_einschlaegig": true
  },
  "red_flags_geprueft": ["R1","R2","R3","R4","R5","R6","R7","R8","R9"],
  "red_flags_gefunden": [],
  "art9_kategorien": [],
  "art9_verschaerfter_massstab": false,
  "dreikriterientest": null,
  "aussortiert": false,
  "aussortierungsgrund": null
}
```

`dreikriterientest: null` ist hier korrekt: Greift die Vermutung, wird der Test nicht einzeln
durchgeführt. Dokumentiert werden Vermutungsgrundlage und Red-Flag-Prüfung.

**Beispiel 2: Transkript mit Residuen, Vermutung widerlegt.**

```json
"datenschutz": {
  "geprueft_am": "2026-10-20",
  "pruefumfang": "volltext",
  "stichprobe_beschreibung": "Volltext aller 12 Transkripte",
  "befund": "personenbezogen",
  "grundlage": "red_flag",
  "anonymisierungserklaerung": {
    "vorhanden": true,
    "fundstelle": "Datensatzbeschreibung",
    "erklaerende_stelle": "Universität Y",
    "stelle_einschlaegig": true
  },
  "red_flags_geprueft": ["R1","R2","R3","R4","R5","R6","R7","R8","R9"],
  "red_flags_gefunden": [
    {"flag": "R2", "fundstelle": "T4, T7, T9", "beschreibung": "Straßennamen und Haltestelle im Klartext"},
    {"flag": "R3", "fundstelle": "T2", "beschreibung": "Leiterin des Tiefbauamts der benannten Gemeinde"}
  ],
  "art9_kategorien": [],
  "art9_verschaerfter_massstab": false,
  "dreikriterientest": {
    "no_record_isolation": {"P1": false, "P2": false, "P3": false},
    "no_linkage": {"P1": true, "P2": false, "P3": false},
    "no_inference": {"P1": false, "P2": false, "P3": false}
  },
  "aussortiert": true,
  "aussortierungsgrund": "personenbezogen: R2 und R3. Die Anonymisierungserklärung ist durch konkrete Residuen widerlegt."
}
```

Der Vergleich beider Beispiele ist die eigentliche Dokumentation: Die Erklärung ist in beiden Fällen
vorhanden und die Stelle einschlägig. Den Unterschied macht allein, **was die Stichprobe gefunden
hat**. Das ist der Punkt, an dem die Prüfung nicht fahrlässig wird.

---

## 12. Sorgfaltsdokumentation

Die Vertrauensvermutung trägt nur, wenn die Prüfung, die sie begleitet, dem Sorgfaltsmaßstab genügt.
Vier Anforderungen, die zusammen belegen, dass nicht fahrlässig gehandelt wurde.

### 12.1 Stichprobenumfang

| Material | Mindestumfang |
|---|---|
| Transkriptsammlung, Regelfall | Methodenteil vollständig, je Transkript Anfang und Ende (je rund 500 Wörter), zusätzlich Volltextsuche nach Ortsangaben, Eigennamen und Organisationsbezeichnungen |
| Transkriptsammlung mit Art.-9-Inhalten | zusätzlich Volltext von mindestens einem Drittel der Transkripte, mindestens drei |
| Einzelnes Transkript | Volltext |
| Survey-Mikrodaten | Variablenliste vollständig, Freitextfelder vollständig, Häufigkeitsauszählung der demografischen Merkmale zur Beurteilung von R5 |
| Aufsatz mit O-Tönen | alle Zitatpassagen samt Kontextsatz |
| Quantitative Studie | Methodenteil, Danksagung, Anhangsverzeichnis |

Die Volltextsuche nach Ortsangaben und Eigennamen ist der wirksamste Einzelschritt. Sie ersetzt kein
Lesen, deckt aber R1 bis R3 zuverlässig ab und lässt sich maschinell durchführen.

### 12.2 Zu dokumentieren ist je Quelle

- der **Stichprobenumfang** in Worten, nicht nur als Kategorie
- die **Fundstelle der Anonymisierungserklärung** und die erklärende Stelle
- die **geprüften Red Flags** als vollständige Liste, auch wenn nichts gefunden wurde
- bei Funden: **Flag, Fundstelle, Beschreibung**
- der **Befund** und, bei Aussortierung, der Grund

Die vollständige Liste geprüfter Flags ist wichtiger, als sie aussieht: Sie unterscheidet „geprüft und
nichts gefunden" von „nicht geprüft". Nur Ersteres trägt die Vermutung.

### 12.3 Wiederholungsprüfung

Nach Rz. 35 gibt es kein „once anonymous, always anonymous". Der Korpus ist **jährlich** daraufhin zu
überprüfen, ob zwischenzeitlich Zusatzinformationen öffentlich wurden, die eine Zuordnung ermöglichen,
und ob sich der Stand der Technik verschoben hat. Das Datum der letzten Prüfung steht in
`meta.dsgvo_geprueft`.

### 12.4 Was die Dokumentation leisten soll

Sie soll gegenüber einer Aufsichtsbehörde belegen, dass SHIFT sich nicht auf eine pauschale Zusage
verlassen, sondern eine eigene, am Maßstab des ErwGr. 26 ausgerichtete Prüfung durchgeführt hat. Nicht
mehr, aber auch nicht weniger. Eine Prüfung ohne diese Dokumentation hat denselben Inhalt und denselben
Wert, aber sie ist nicht nachweisbar, und darauf kommt es im Streitfall an.

---

## 13. Bekannte Lücken und Restrisiken

### 13.1 Restrisiken der Projektentscheidung

Keine Mängel der Prüfung, sondern bewusst eingegangene Risiken. Sie gehören in den
Limitationen-Abschnitt des Protokolls:

| Risiko | Einordnung |
|---|---|
| **Nicht veröffentlichte Schlüsselliste** beim Forschenden führt nicht zur Aussortierung | Die stärkste Abweichung von der Breyer-Linie. Begründung und Gegenargument in Abschnitt 7. Bewusste Entscheidung zugunsten des Erhalts von Interviewdaten. |
| **Vertrauensvermutung** stützt sich auf die Qualifikation der erklärenden Stelle | Eine fehlerhafte Anonymisierung durch eine qualifizierte Stelle wird nur entdeckt, soweit die Stichprobe reicht. |
| **Stichprobe statt Vollprüfung** im Regelfall | Residuen außerhalb der Stichprobe werden nicht gefunden. Abgemildert durch die maschinelle Volltextsuche nach Orten und Eigennamen. |
| **Art. 9 ohne eigenen Ausschlussgrund** | Dogmatisch richtig, solange die Anonymität trägt. Fällt sie, war sensibles Material im Pool. Deshalb der verschärfte Stichprobenumfang. |

### 13.2 Offene Punkte des Prüfmaßstabs

| Lücke | Wirkung |
|---|---|
| EDPB Guidelines 02/2026 sind Version 1.0 in Konsultation | Randnummern können sich verschieben |
| Maßstab nicht juristisch gegengeprüft | Ableitung aus Normtext, Rechtsprechung und Guidelines, keine Beratung |
| Abgrenzung Pseudonymisierung / Anonymisierung nicht eigens ausgearbeitet | Trägt die Abgrenzung, von der die Aussortierung abhängt. Dringlichster Klärungspunkt. |
| Relativer Personenbezug (Breyer-Linie) nicht abschließend bewertet | Trägt die umstrittene Festlegung aus Abschnitt 7 |
| Stimmdaten als biometrisches Datum nicht ausgearbeitet | R7 beruht auf der Einordnung von Stimme als Identifikator |
| Keine quantitativen Schwellen (k-Anonymität, Differential Privacy) | R5 arbeitet mit einem Richtwert |
| Art. 89 DSGVO, § 27 BDSG nicht ausgearbeitet | Gegenstandslos, solange Rechtsgrundlagen nicht geprüft werden |

---

## Primärquellen

- DSGVO (Verordnung (EU) 2016/679), Art. 4 Nr. 1, Art. 9, Art. 10 und ErwGr. 26,
  https://eur-lex.europa.eu/eli/reg/2016/679/oj
- EDPB Guidelines 02/2026 zur Anonymisierung, Version 1.0 (Konsultationsfassung vom 07.07.2026)
- EuGH C-582/14 (Breyer), C-413/23 P (EDPS/SRB), C-319/22 (Scania), C-604/22 (IAB Europe),
  C-252/21 (Meta v. Bundeskartellamt), C-184/20 (Vyriausioji), C-446/21 (Schrems/Meta),
  abrufbar über https://curia.europa.eu
