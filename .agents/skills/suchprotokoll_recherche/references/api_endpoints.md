# API-Endpoints & Zugriffs-Dokumentation

Dieses Dokument enthält die programmatischen Zugriffspunkte und Paginierungsstrategien für alle im Skill genutzten Plattformen mit besonderem Fokus auf erschöpfende Recherche, qualitative Studien und Datenanhänge.

---

## 1. OpenAlex API (Interdisziplinär & Paginierbar)

**Basis-URL:** `https://api.openalex.org`

### Volltextsuche mit hoher Treffermenge (Paginierung)
```
GET https://api.openalex.org/works
  ?search=<QUERY>
  &filter=open_access.is_oa:true
  &per-page=50
  &page=1
  &mailto=research@example.com
```
*Für Folgeseiten `page=2`, `page=3` usw. inkrementieren bis Ergebnisse erschöpft sind oder Relevanz sinkt.*

### Gezielte Suche nach qualitativen Studien / Interviews
```
GET https://api.openalex.org/works
  ?search=<THEMA>+interview
  &filter=open_access.is_oa:true,publication_year:>2014
  &sort=relevance_score:desc
  &per-page=50
  &page=1
  &mailto=research@example.com
```

### Citation Snowballing mit OpenAlex API
```
# Vorwärts-Snowballing (Wer zitiert diese Seed-Studie?):
GET https://api.openalex.org/works?filter=cites:<OPENALEX_WORK_ID>&per-page=50&mailto=research@example.com

# Rückwärts-Snowballing (Welche Studien zitiert die Seed-Studie?):
1. GET https://api.openalex.org/works/<OPENALEX_WORK_ID>  -> Feld "referenced_works": ["W123...", "W456..."]
2. GET https://api.openalex.org/works?filter=openalex_id:W123|W456&per-page=50&mailto=research@example.com
```

### Nützliche Parameter
| Parameter | Bedeutung | Beispiel / Werte |
|-----------|-----------|------------------|
| `search` | Volltext- und Titelsuche | `search=bicycle+AND+interview` |
| `filter` | Felder filtern | `filter=open_access.is_oa:true,has_doi:true` |
| `sort` | Sortierung | `sort=relevance_score:desc` oder `sort=publication_date:desc` |
| `per-page` | Ergebnisse pro Seite (max 200) | `per-page=50` (Standard für umfassende Suche) |
| `page` | Seitennummer (1-basiert) | `page=2` |
| `cursor` | Cursor-Paginierung bei >10.000 Treffern | `cursor=*` |
| `mailto` | Polite Pool für schnellere Rate-Limits | `mailto=name@domain.com` |

**Docs:** https://docs.openalex.org/api-entities/works/search-works

---

## 2. Zenodo API (Preprints, Datensätze & Transkripte)

**Basis-URL:** `https://zenodo.org/api`

### Suche nach Publikationen & Preprints (mit Paginierung)
```
GET https://zenodo.org/api/records?q=<QUERY>&type=publication&access_right=open&size=50&page=1
```

### Gezielte Suche nach Datensätzen & Interviewtranskripten
```
GET https://zenodo.org/api/records?q=(<THEMA>)+AND+(interview+OR+qualitative+OR+transcript+OR+leitfaden)&type=dataset&access_right=open&size=50&page=1
```

### Dateianhänge eines Eintrags abrufen (für `daten_anhaenge`)
```
GET https://zenodo.org/api/records/<RECORD_ID>/files
```
*Liefert das JSON-Array `entries` mit `key` (Dateiname), `size` (Dateigröße) und `links.content` (direkter Download-Link für CSV, PDF-Anhänge, Transkript-Dateien).*

**Docs:** https://developers.zenodo.org/

---

## 3. QDR — Qualitative Data Repository (Syracuse University)

Das QDR basiert auf der Dataverse-Plattform und ist das weltweit führende Repositorium für **qualitative Forschungsdaten, Interviewtranskripte und Audio-/Textkorpora**.

**Basis-URL:** `https://dataverse.qdr.syr.edu/api`

### Suche nach qualitativen Datensätzen & Transkripten
```
GET https://dataverse.qdr.syr.edu/api/search
  ?q=<QUERY>
  &type=dataset
  &per_page=25
  &sort=date
  &order=desc
```

### Suche mit Interview-Schlüsselwörtern
```
GET https://dataverse.qdr.syr.edu/api/search
  ?q=<THEMA>+AND+(interview+OR+transcript+OR+"focus group")
  &type=dataset
  &per_page=25
```

**Websuche (Browser-Fallback):** `https://dataverse.qdr.syr.edu/dataverse/root?q=<QUERY>`

---

## 4. Harvard Dataverse API

**Basis-URL:** `https://dataverse.harvard.edu/api`

### Suche nach Datensätzen & Anhängen
```
GET https://dataverse.harvard.edu/api/search
  ?q=<QUERY>
  &type=dataset
  &per_page=50
  &start=0
  &sort=date
  &order=desc
```

### Dateianhänge eines Datensatzes abrufen
```
GET https://dataverse.harvard.edu/api/datasets/:persistentId/versions/:latest/files?persistentId=<DOI>
```

**Docs:** https://guides.dataverse.org/en/latest/api/search.html

---

## 5. GESIS & SSOAR (DE / Sozialdaten & Qualitative Studien)

### SSOAR (Social Science Open Access Repository)
```
https://www.ssoar.info/ssoar/discover?query=<THEMA>+interview&filtertype=type&filter_relational_operator=equals&filter=article
```

### GESIS Datenarchiv (Forschungsdaten & Befragungen)
```
https://search.gesis.org/research_data?q=<THEMA>+AND+(interview+OR+befragung)&lang=de
```

*Hinweis:* Bei GESIS und SSOAR Abfragen via `read_url_content` oder `search_web` auf die Suchergebnisseite ausführen.

---

## 6. OSF (Open Science Framework)

**Basis-URL:** `https://api.osf.io/v2`

### Projektsuche nach Vorabregistrierungen & Datenanhängen
```
GET https://api.osf.io/v2/nodes/?filter[title]=<THEMA>&filter[description]=interview&page[size]=25
```

**Websuche:** `https://osf.io/search/?q=<THEMA>+interview`

---

## 7. PubMed / NCBI API (Entrez)

**Basis-URL:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

### Qualitative Studien & Interviews in PubMed
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
  ?db=pubmed
  &term=(<THEMA>[tiab])+AND+(interview*[tiab]+OR+"qualitative study"[tiab]+OR+"focus group*"[tiab])
  &retmax=100
  &retmode=json
```

### Metadaten abrufen (EFetch)
```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
  ?db=pubmed
  &id=<PMID1>,<PMID2>,<PMID3>
  &retmode=xml
```

**Docs:** https://www.ncbi.nlm.nih.gov/books/NBK25499/

---

## 8. Semantic Scholar API

**Basis-URL:** `https://api.semanticscholar.org/graph/v1`

### Papersuche mit hoher Trefferzahl
```
GET https://api.semanticscholar.org/graph/v1/paper/search
  ?query=<QUERY>
  &fields=title,authors,year,abstract,isOpenAccess,openAccessPdf,externalIds,citationCount
  &limit=50
  &offset=0
```

### Citation Snowballing mit Semantic Scholar
```
# Referenzen & Zitationen einer Paper-ID abrufen:
GET https://api.semanticscholar.org/graph/v1/paper/<PAPER_ID>?fields=references.title,references.abstract,references.isOpenAccess,citations.title,citations.abstract,citations.isOpenAccess&limit=50
```

**Docs:** https://api.semanticscholar.org/api-docs/

---

## 9. GitHub Search API (Tools, Repos & Transkript-Korpora)

**REST-API:** `https://api.github.com/search`

### Repository-Suche
```
GET https://api.github.com/search/repositories
  ?q=<THEMA>+qualitative+data+in:readme
  &sort=stars
  &order=desc
  &per_page=30
```

---

## 10. arXiv API

**Basis-URL:** `https://export.arxiv.org/api/query`

```
GET https://export.arxiv.org/api/query
  ?search_query=all:<KEYWORD>+AND+(cat:cs.HC+OR+cat:cs.CY)
  &max_results=50
  &sortBy=relevance
```

---

## 11. Zivilgesellschafts-, NPO- & Wirtschafts-Repositorien

### A. SSOAR / GESIS (Social Science Open Access Repository)
Zentrales europäisches Fachportal für empirische Sozialwissenschaften, qualitative Studien und Vereinsforschung.

**Web- & OAI-PMH-Suche:**
```
https://www.ssoar.info/ssoar/discover?query=<THEMA>+AND+(Verein+OR+Ehrenamt+OR+NPO)
```
*Gezielte Zitations- & Volltextsuche:*
- `site:ssoar.info ("Verein" OR "Sportverein" OR "Ehrenamt") ("Finanzen" OR "Konto" OR "Befragung") filetype:pdf`

---

### B. EconStor (ZBW – Leibniz-Informationszentrum Wirtschaft)
Über 250.000 wirtschaftswissenschaftliche Open-Access-Volltexte, Arbeitspapiere und Preprints (u. a. DIW, ZEW, DLR, Universitäten).

**REST- / Discovery-Endpoint:**
```
https://www.econstor.eu/discover?query=<QUERY>&filtertype=type&filter_relational_operator=equals&filter=Working+Paper
```
*Gezielte Suche zu Mikromobilität, Radverkehrsförderung und Verkehrsmittelwahl:*
- `site:econstor.eu ("bike sharing" OR "cycling infrastructure") ("modal choice" OR "subsidies" OR "route choice") filetype:pdf`
- `site:econstor.eu ("active travel" OR "Radverkehr") ("Infrastruktur" OR "perceived safety") filetype:pdf`

---

### C. TRID — Transport Research International Documentation
Weltweit größte verkehrswissenschaftliche Datenbank (über 1,4 Mio. Datensätze von TRB, OECD/ITF, BASt):
- Web-Recherche nach Berichten und Open-Access-Studien:
  `https://trid.trb.org/`
  `site:trid.trb.org "cycling safety" (interview OR "sensor data" OR "perceived comfort")`

---

### D. BASt (Bundesanstalt für Straßenwesen) & DLR Institut für Verkehrsforschung
Verkehrsstatistiken, Sicherheitsuntersuchungen und empirische Nutzerstudien im Radverkehr:
- Suchmuster:
  `site:bast.de "Radverkehr" ("Verkehrssicherheit" OR "Infrastruktur") filetype:pdf`
  `site:dlr.de/vf "Mobilität in Deutschland" OR "Radverkehr" filetype:pdf`

---

## 12. Praxis-, NGO- & Kommunal-Portale (Graue Literatur)

Für Praxisberichte, Bürgerbeteiligungen und institutionelle Stakeholder-Positionspapiere:

| Organisation / Institut | Fokus & Relevanz | Suchmuster (search_web / URL) |
|-------------------------|------------------|-------------------------------|
| **Difu** (difu.de) | Deutsches Institut für Urbanistik (Kommunalleitfäden, Radverkehrsplanung) | `site:difu.de <THEMA> (interview OR leitfaden OR bericht)` |
| **BBSR** (bbsr.bund.de) | Bundesinstitut für Bau-, Stadt- und Raumforschung (Smart Cities, Mobilität) | `site:bbsr.bund.de <THEMA> filetype:pdf` |
| **UBA** (umweltbundesamt.de) | Umweltbundesamt (Verkehrswende, Radverkehrspotenziale) | `site:umweltbundesamt.de <THEMA> publikationen` |
| **BASt** (bast.de) | Bundesanstalt für Straßenwesen (Sicherheitsstudien & Regelwerke) | `site:bast.de <THEMA> filetype:pdf` |
| **Agora Verkehrswende** | Think-Tank für nachhaltige Mobilität | `site:agora-verkehrswende.de <THEMA> filetype:pdf` |
| **ADFC / VCD** | Radfahrer-Interessenverbände (Fahrradklima-Test, Umfragedaten) | `site:adfc.de (<THEMA> OR fahrradklima-test) filetype:pdf` |
| **VDV** (vdv.de) | Verband Deutscher Verkehrsunternehmen (Intermodalität, B+R) | `site:vdv.de <THEMA> positionspapier` |
| **GovData / Open Data** | Offene Verkehrs- und Zähldaten (govdata.de, data.europa.eu) | `https://www.govdata.de/web/guest/suchen/-/search/?q=<THEMA>` |

---

## Best Practices für maximale Ausbeute & Anhänge

1. **Paginierung ausschöpfen:** Immer `page=1`, `page=2` (bzw. `offset=50`) abfragen, bis keine neuen qualifizierten Treffer mehr gefunden werden.
2. **Polite Pool bei OpenAlex:** `mailto=` anhängen für 10x schnellere Raten und stabile Verbindungen.
3. **Zweisprachig suchen (DE & EN):** Spezifische Richtlinienbegriffe im D-A-CH-Raum Deutsch suchen (`Radverkehrsanlage`, `Trennungsgüte`, `Radpendler`), empirische und kognitive Wirkungsmechanismen international Englisch (`perceived safety`, `stress indicators`, `vibration comfort`).
4. **Snowballing anwenden:** Aus den besten 2–3 Treffern Zitationen und Referenzen abrufen – liefert oft die wertvollsten qualitativen Vorläuferstudien.
5. **Verbands- & Praxisberichte einbinden:** Über Difu, ADFC, UBA und BASt reale Stakeholder- und Betreiberperspektiven ergänzen.
6. **Dateianhänge erfassen (Keine Haupt-Paper-Duplikate!):** Bei Zenodo und Dataverse die Endpoints `/files` aufrufen, um alle begleitenden Dokumente (Transkript-Dateien, Datensätze, Codebooks) direkt in `daten_anhaenge` aufzunehmen. **Wichtig:** Die Hauptpublikation selbst (z. B. aus OpenAlex `oa_url` oder DOI) gehört in `doi_url` und `open_access: true`, **NIEMALS** in `daten_anhaenge`! Wenn keine separaten Begleitdateien existieren, bleibt `daten_anhaenge: []` strikt leer.


