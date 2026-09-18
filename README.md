# Research Skill

## 1. Technologies & APIs Used

The research skill ([`suchprotokoll_recherche`](.agents/skills/suchprotokoll_recherche/SKILL.md)) uses python scripts to interact with structured REST APIs, and targeted web extraction:

| Technology / Interface | Purpose | Endpoints & Mechanisms |
|---|---|---|
| **OpenAlex REST API** | Interdisciplinary academic literature, metadata, citation networks | `https://api.openalex.org/works?filter=...` with pagination (`per-page=50`, `page=N`). Returns DOIs, abstracts, open-access status, references, and citation counts. |
| **Zenodo REST API** | Open science datasets, interview transcripts, code, and preprints | `https://zenodo.org/api/records?q=...&type=dataset` via native HTTP requests. Returns file lists, direct download links, and deposit metadata. |
| **Semantic Scholar API** | AI-indexed paper graphs and citation paths | Graph search and reference traversal endpoints for forward/backward snowballing. |
| **Specialized Repositories** | Qualitative and domain-specific data | **QDR** (Qualitative Data Repository) for transcripts, **GESIS/SSOAR** for empirical social and mobility studies, **EconStor** for economics and governance papers. |
| **DOM Scraping (`read_url_content`)** | DOI landing page parsing & Electronic Supplementary Material (ESM) extraction | Fetches publisher landing pages (ScienceDirect, SpringerLink, Wiley) to locate standalone supplementary attachments (`.xlsx`, `.csv`, interview guide PDFs). |
| **Targeted Search (`search_web`)** | Grey literature & institutional reports | Domain-restricted queries (`site:oecd.org`, `site:difu.de`, `filetype:pdf`) targeting public guidelines, agency surveys, and institutional reports. |

---

## 2. From `project.md` to `findings_<thema>.json`: Step-by-Step

### Step 1: Project Parsing & Archetype Mapping
The agent reads `project.md` and maps the project into one of three archetypes:
1. **Spatial & Infrastructure:** Queries OpenAlex, Zenodo, public research portals.
2. **Market, Organizational & Problem Fields:** Queries EconStor, SSOAR/GESIS, specialized survey databases.
3. **Technology & Methods:** Queries IEEE Xplore, ACM, arXiv.

### Step 2: 4-Facet Search Construction & Bilingual Thesaurus
The search scope is broken down into four boolean facets, each populated with 5–8 synonyms in English and German (e.g., for urban cycling safety):
- **Facet A (Phenomenon / Infrastructure):** Core subject (e.g., `cycling network`, `bicycle infrastructure`, `Radverkehrsanlagen`).
- **Facet B (Mechanism / Pain Point):** Operational factors or safety mechanisms (e.g., `perceived safety`, `route choice`, `vibration comfort`, `Trennungsgüte`).
- **Facet C (Actors / Context):** Affected individuals or decision-makers (e.g., `urban commuters`, `cyclists`, `Radfahrende`, `vulnerable road users`).
- **Facet D (Empirical / Methodological Filter):** Empirical data constraint (e.g., `semi-structured interview`, `sensor data`, `focus group`, `survey`, `Leitfadeninterview`).

### Step 3: 3-Tier Query Execution
The agent queries the APIs using boolean aggregation (`OR` within facets, `AND` between facets):
1. **Tier 1 (Full Intersection):** `(Facet A) AND (Facet B) AND (Facet C) AND (Facet D)` for high-precision seed studies.
2. **Tier 2 (Conjunction Relaxation):** If results are scarce, queries are relaxed to `(A) AND (C) AND (D)` or `(A) AND (B) AND (D)`.
3. **Tier 3 (Free-Text Keywords):** Formatted keyword strings for APIs without full boolean syntax (e.g., Semantic Scholar).
- **Pagination:** Calls loop across pages (e.g., `page=1`, `page=2` up to saturation) rather than stopping at the top 10 results.

### Step 4: Qualitative Boost & Citation Snowballing
- **Qualitative Harvest:** If fewer than 30% of hits include empirical user studies, targeted queries are launched against **QDR**, **Zenodo Datasets**, and **GESIS** specifically for interview transcripts and study guides.
- **Backward Snowballing:** Extracts cited papers from seed studies via OpenAlex `referenced_works`.
- **Forward Snowballing:** Fetches newer papers citing the seed studies via OpenAlex `cites:<ID>`.

### Step 5: Quality Gate, Attachment Validation & Output Generation
- **Deduplication:** Merges duplicates via DOI and normalized title strings.
- **Strict Attachment Rule:** The publication PDF URL is placed in `doi_url`. The `daten_anhaenge` array is strictly reserved for independent companion files (transcripts, CSV datasets, supplementary codebooks). In-text appendices are documented in `qualitative_daten.interview_leitfaden_verfuegbar: true` without duplicating links.
- **In-Situ Diagnostic Logging:** Telemetry is written directly to `meta.phasen_log` and `meta.recherche_diagnose` (raw hits sighted, filtered count, saturation reason).
- **Emitted Files:**
  - `findings_<thema>.json`: Machine-readable dataset.
  - `suchprotokoll_<thema>.md`: Human-readable protocol and search log.

---

## 3. Sample Dataset

A public demonstration dataset with two validated entries is available in [**`sample_findings.json`**](sample_findings.json):
- **`meta`**: Contains search metadata, diagnostic metrics (`treffer_roh_gesichtet`, `gefiltert_irrelevant`, `validiert_gespeichert`), and phase progression logs (`meta.phasen_log`).
- **Entry `F-001` (Academic Journal Paper):** OpenAlex hit with mixed-methods data (N=28 ride-along interviews + GPS tracking) and a linked ESM interview guide.
- **Entry `F-002` (Open Dataset & Grey Literature):** Zenodo hit with raw 3-axis accelerometer sensor data (CSV) and survey evaluation across urban corridors.

---

## 4. Downstream Skills (Brief Summary)

The `findings_<thema>.json` file serves as the input contract for the remaining skills in the repository:

1. [**`daten_download`**](.agents/skills/daten_download/SKILL.md): Automates the local download of open-access PDFs, datasets, and attachments into `data/raw/<thema>/` and scans full-texts for direct participant quotes (*O-Töne*).
2. [**`stakeholder_analyse`**](.agents/skills/stakeholder_analyse/SKILL.md): Ingests the findings JSON, extracts mentioned user groups and institutions, and generates a Power-Interest Matrix (`stakeholder.json` / `stakeholder.md`).
3. [**`requirements_analyse`**](.agents/skills/requirements_analyse/SKILL.md): Synthesizes `project.md`, stakeholder data, and empirical quotes into formal functional/non-functional requirements and personas (`requirements.md`).
