# Eval-Lauf 2026-10-30

Erster Lauf der Evals 1 bis 7 gegen den Stand von Commit `5bdbaed`. Jede Eval lief in einem
frischen Subagenten, der nur den Prompt und den Skill kannte (ohne Zugriff auf `evals/`). Eval 0
von `topic-research` (vollständiger Lauf) wurde nicht ausgeführt. Kein Baseline-Vergleich mit
v2.0.

## Ergebnis

| Eval | Name | Ergebnis | Abweichung vom Soll |
|---|---|---|---|
| 1 | lizenzcheck-gemischte-quellen | teilweise | ACM als K0 `nicht_pruefbar` statt `keine_lizenz_gefunden` (Landing Page HTTP 403); § 60d-Zweigleisigkeit für ACM nicht ausgewiesen. Cambridge K2, IGI (bronze) K0 und nicht frei, UBA nicht als § 5 behandelt: wie erwartet. |
| 2 | dsgvo-vertrauensvermutung-vs-redflag | teilweise | Datensatz 2 korrekt `personenbezogen` (R2, R3) und aussortiert. Datensatz 1 nicht vorsorglich aussortiert, aber `zweifelhaft` statt `kein_personenbezug`, weil ohne Material keine Stichprobe (V3) möglich war. |
| 3 | hard-fail-keine-lizenz-erfinden | bestanden | CC BY verweigert, K0 mit `keine_lizenz_gefunden`, Anfrage beim ADFC vorgeschlagen, keine Queue. |
| 4 | art9-verschaerft-schliesst-nicht-aus | bestanden | Kern erfüllt; R9 und das Feld `art9_verschaerfter_massstab` nicht ausdrücklich genannt. |
| 5 | nc-praemisse-greift-nd-bleibt | bestanden | – |
| 6 | freigabeklassen-k0-k1-k2-trennung | teilweise | Alle Klassen richtig (K2, K2, K1, K0), K1 gut erklärt. ACM aber `nicht_pruefbar` statt `keine_lizenz_gefunden` (wie Eval 1). |
| 7 | codebook-ist-keine-schluesselliste | bestanden | – |

## Befunde für den Skill

Nach Gewicht geordnet; mehrfach genannte zuerst.

1. **Validator und Eingabefall 2 (Fehler, aus Schritt 3).** `validate_findings.py` verlangt die
   Recherchephasen 0 bis 5 und `recherche_diagnose` auch dann, wenn nur eine DOI-Liste geprüft
   wird. Vier von sieben Läufen mussten Platzhalter erfinden. Gemeldet in Eval 1, 2, 3, 6.
2. **K0-Grund bei gesperrter Landing Page.** APIs melden keine Lizenz, Status `closed`, die
   Landing Page antwortet 403. Ob das `keine_lizenz_gefunden` oder `nicht_pruefbar` ist, regelt
   der Skill nicht. Beide Läufe mit ACM wählten `nicht_pruefbar`, Eval 1 sortierte die Quelle
   dadurch zusätzlich aus Datenschutzgründen aus. **Entschieden am 2026-11-04: HTTP 403 ergibt
   `nicht_pruefbar`.** Die Läufe lagen damit richtig; Evals 1 und 6 sind angepasst.
3. **Lizenz aus Nutzerangabe.** `lizenz_quelle` hat keinen Wert dafür, und es gibt kein Feld für
   „vorläufig, Beleg ausstehend". Die Läufe behalfen sich mit `keine` oder einem erfundenen Wert.
   Gemeldet in Eval 5, 6.
4. **Selbstauskünfte von Autorinnen und Autoren (Positionality).** Art.-9-Angaben des namentlich
   genannten Autors im Fließtext (Cambridge-Aufsatz) führen nach R1 + R9 wörtlich zu
   `personenbezogen`. Der Skill nimmt Autorendaten nur als bibliografische Angaben aus. Beide
   Läufe wählten `zweifelhaft`. Gemeldet in Eval 1, 6. **Entschieden am 2026-11-04: wird wie
   Autorendaten behandelt, keine Red Flag (`datenschutz.autor_selbstauskunft`).**
5. **User-Agent beim Laden per Shell.** Die Werkzeugtabelle sagt „per Shell laden", legt aber
   keinen User-Agent fest; ein Lauf versuchte einen Browser-User-Agent und wurde blockiert.
6. **Kleinere Lücken:**
   - Kein Datenschutzwert für „Prüfung ausstehend"; Datenschutz `nicht_pruefbar` ist nur für
     „nicht einmal der Abstract lesbar" definiert (Eval 1, 5, 6).
   - Ob jede ND-Quelle mit `N2: zweifelhaft` in die Review-Queue gehört (Eval 5).
   - CC BY-NC fehlt in der K2-Zeile von `lizenzpruefung.md` 6.1 (Eval 5).
   - Der § 60d-Dauerposten hat keinen Platz in der Queue, weil sie eine `finding_id` verlangt
     (Eval 3, 6).
   - Kein Vokabular für `art9_kategorien`; keine Regel für Supplements ohne eigene Lizenzangabe;
     nur ein `k0_grund`, wenn zwei zutreffen (Eval 1).
   - Kein Modus für konzeptionelle Fragen ohne konkrete Quelle (Eval 4, 7).
   - Die nicht veröffentlichte Schlüsselliste ist als Restrisiko benannt, aber nicht als Feld
     markiert, nach dem sich später filtern ließe (Eval 7).
