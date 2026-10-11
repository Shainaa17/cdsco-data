# 💊 CDSCO Weekly Drug Intelligence Tracker

An automated end-to-end pharmaceutical intelligence platform designed to track, scrape, enrich, standardize, and visualize weekly drug approvals from the **Central Drugs Standard Control Organisation (CDSCO)**, Government of India.

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start / Installation](#-quick-start--installation)
- [Environment Variables (.env)](#-environment-variables-env)
- [Running the Project](#-running-the-project)
- [Database Schema](#-database-schema)
- [Deployment Options](#-deployment-options)
- [Troubleshooting](#-troubleshooting)

---

## 🌟 Overview

The CDSCO regularly publishes approvals for new chemical entities, fixed-dose combinations, biologicals, and medical formulations. However, these records are often scattered across government web portals and PDF circulars, frequently missing clinical composition, indications, or dosage details.

**CDSCO Weekly Drug Tracker** solves this by:
1. **Automated Ingestion**: Ingests approvals directly from the CDSCO online portal and official regulatory PDFs.
2. **AI Enrichment**: Utilizes Google Gemini (`gemini-2.5-flash`) combined with the Tavily Search API to research and fill missing compositions, dosages, and therapeutic indications, complete with verifiable web source citations.
3. **WHO ICD Mapping**: Automatically standardizes drug indications to WHO ICD-10/ICD-11 diagnostic classifications.
4. **Multi-Sheet Excel Reporting**: Generates formatted, color-coded executive Excel spreadsheets with clickable source links.
5. **Interactive Streamlit Dashboard**: Provides search, multi-faceted filtering, KPI analytics, and real-time synchronization.

---

## ✨ Key Features

- **Automated Web Scraping**: Headless Playwright browser automation navigating CDSCO approval tables.
- **Historical PDF Ingestion**: `pdfplumber`-powered parser extracting multi-page tabular data from legacy government circulars.
- **Deduplication Engine**: SHA-256 fingerprinting (`drug_name` + `manufacturer` + `approval_date`) prevents duplicate database insertions.
- **AI-Powered Data Enrichment**: Detects missing fields (`composition`, `dosage`, `indication`), searches validated medical databases using Tavily, and uses Google Gemini to extract exact values with strict grounding and zero hallucinations.
- **Diagnostic Code Normalization**: Tokenizes indication phrases and maps them to WHO ICD codes with hierarchy levels (e.g. Level 1 category to specific disease).
- **Executive Excel Reports**: Automated report creation with conditional formatting (red for missing, green for enriched), freeze panes, and active hyperlinks.
- **Streamlit Web UI**: Responsive local web application with instant KPI cards, advanced filters, and one-click CDSCO update triggers.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    subgraph Ingestion
        A[CDSCO Web Portal] -->|Playwright Scraper| P[HTML Parser / Cleaner]
        B[Official Approval PDFs] -->|pdfplumber| I[PDF Importer]
    end

    subgraph Storage & Deduplication
        P --> D[(PostgreSQL Database)]
        I --> D
        D ---|SHA-256 Hash Check| D
    end

    subgraph AI & Standards Enrichment
        D -->|Pending Approvals| S[Tavily Search API]
        S --> G[Google Gemini 2.5 Flash]
        G -->|Enriched Fields + URLs| D
        D -->|Unmapped Indications| M[WHO ICD Matcher]
        M --> D
    end

    subgraph Presentation
        D --> E[Excel Report Generator]
        D --> W[Streamlit Web Dashboard]
        E -->|cdsco_approvals.xlsx| W
    end
```

---

## 📂 Project Structure

```text
cdsco-weekly-tracker/
│
├── app/
│   ├── dashboard/
│   │   └── dashboard.py           # Streamlit web application & KPI dashboard
│   ├── database/
│   │   ├── db.py                  # PostgreSQL connection factory (URL or individual params)
│   │   ├── models.py              # DDL scripts and table creation
│   │   └── operations.py          # CRUD queries, hash deduplication, ICD operations
│   ├── enrichment/
│   │   ├── llm.py                 # Google Gemini prompt engineering & extraction
│   │   ├── pipeline.py            # Enrichment pipeline orchestrator
│   │   ├── search.py              # Tavily web search integration
│   │   └── citations.py           # Verification & citation utilities
│   ├── icd/
│   │   ├── code_matcher.py        # Indication term tokenizer and scoring
│   │   ├── pipeline.py            # WHO ICD extraction & PostgreSQL mapping
│   │   ├── search.py              # WHO ICD hierarchy retrieval
│   │   └── term_extractor.py      # Linguistic extraction of medical terms
│   ├── parser/
│   │   ├── cleaner.py             # Field normalization & whitespace cleanup
│   │   └── extractor.py           # BeautifulSoup / HTML table parsing
│   ├── pdf_import/
│   │   └── importer.py            # Multi-page PDF table reader & normalizer
│   ├── reports/
│   │   └── excel.py               # openpyxl multi-sheet formatted workbook generator
│   ├── scraper/
│   │   ├── browser.py             # Playwright browser lifecycle manager
│   │   ├── cdsco_scraper.py       # Scraper entry point
│   │   ├── navigator.py           # Navigation routines
│   │   └── selectors.py           # Web selectors
│   ├── utils/
│   │   ├── config.py              # Configuration constants
│   │   └── logger.py              # Logging handlers
│   └── main.py                    # Master CLI pipeline (Scrape -> Enrich -> Excel)
│
├── data/
│   ├── exports/                   # Output Excel reports (cdsco_approvals.xlsx)
│   └── pdfs/                      # Historical government PDF circulars
│
├── tests/                         # Unit tests
├── requirements.txt               # Python package dependencies
├── .env                           # Environment configuration & API keys
├── run_dashboard.bat              # One-click Windows starter script
├── SETUP_GUIDE_FOR_BEGINNERS.md   # Non-technical step-by-step setup guide
└── README.md                      # Technical documentation
```

---

## 🛠 Tech Stack

- **Language**: Python 3.10+
- **Database**: PostgreSQL (psycopg2-binary, SQLAlchemy)
- **Web Scraping**: Playwright, BeautifulSoup4, Requests
- **Document Processing**: pdfplumber, openpyxl, pandas
- **AI & Enrichment**: Google Gemini API (`google-genai`), Tavily Search API
- **Medical Ontologies**: WHO ICD API
- **User Interface**: Streamlit, Plotly Express

---

## 📋 Prerequisites

1. **Python**: Version 3.10 or higher ([python.org](https://www.python.org/downloads/))
2. **PostgreSQL**: A local PostgreSQL instance or a free cloud database (e.g., [Neon](https://neon.tech), [Supabase](https://supabase.com), [Render](https://render.com)).
3. **API Keys**:
   - [Google AI Studio](https://aistudio.google.com/) (`GEMINI_API_KEY`)
   - [Tavily AI](https://tavily.com/) (`TAVILY_API_KEY`)
   - *(Optional)* [WHO ICD API](https://icd.who.int/icdapi) (`WHO_ICD_CLIENT_ID`, `WHO_ICD_CLIENT_SECRET`)

---

## ⚙️ Environment Variables (.env)

Create or edit the `.env` file in the root directory:

```env
# Database Configuration (Option 1: Single URL - Recommended for Cloud)
DATABASE_URL=postgresql://username:password@localhost:5432/cdsco_tracker

# Database Configuration (Option 2: Individual variables)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cdsco_tracker
DB_USER=postgres
DB_PASSWORD=your_password_here

# AI & Search APIs
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# WHO ICD API Credentials (Optional)
WHO_ICD_CLIENT_ID=your_who_client_id
WHO_ICD_CLIENT_SECRET=your_who_client_secret
```

---

## 🚀 Quick Start / Installation

### 1. Clone or Extract the Repository
```bash
git clone https://github.com/Shainaa17/cdsco-data.git
cd cdsco-weekly-tracker
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Initialize the Database
Ensure your PostgreSQL database is running, then create the tables:
```bash
python test_db.py
```
*(You will see: `Database connected successfully.`)*

---

## 🏃 Running the Project

### 1. Launch the Web Dashboard
```bash
streamlit run app/dashboard/dashboard.py
```
Open your browser to: **`http://localhost:8501`**

### 2. Run the Full Pipeline (CLI)
Runs the complete sequence: Clears update flags → Scrapes CDSCO portal → Enriches missing data with Gemini + Tavily → Generates Excel report.
```bash
python -m app.main
```

### 3. Import Historical PDFs
Extract approvals from all PDFs stored in `data/pdfs/` and store them in the database:
```bash
python -m app.pdf_import.importer
```

### 4. Run WHO ICD Mapping Pipeline
Standardizes disease indications into official ICD-10/11 medical codes:
```bash
python -m app.icd.pipeline
```

---

## 🗄 Database Schema

The system uses two primary relational tables in PostgreSQL:

### `approvals`
| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique record identifier |
| `approval_hash` | TEXT UNIQUE | SHA-256 fingerprint for deduplication |
| `drug_name` | TEXT | Name of the approved drug formulation |
| `category` | TEXT | Drug category (New Drug, SND, FDC, etc.) |
| `approval_date` | TEXT | Date approved by CDSCO |
| `type` | TEXT | Formulation type (Tablet, Capsule, Bulk Drug, etc.) |
| `composition` | TEXT | Active pharmaceutical ingredients |
| `composition_source` | TEXT | Source URL validating composition |
| `dosage` | TEXT | Recommended dosage and strength |
| `dosage_source` | TEXT | Source URL validating dosage |
| `indication` | TEXT | Clinical indication / targeted disease |
| `indication_source` | TEXT | Source URL validating indication |
| `manufacturer` | TEXT | Pharmaceutical company / applicant |
| `needs_enrichment` | TEXT | `'Yes'` or `'No'` indicator |
| `missing_fields` | TEXT | Comma-separated list of missing attributes |
| `source` | TEXT | Origin (`CDSCO`, `CDSCO PDF`) |
| `source_url` | TEXT | Original PDF filename or web URL |
| `last_updated` | TEXT | Timestamp of last modification |
| `is_new` | BOOLEAN | Flag set for newly added approvals |

### `approval_icd_mappings`
| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique mapping ID |
| `approval_hash` | TEXT REFERENCES approvals | Foreign key linking to approval |
| `icd_search_term` | TEXT | Specific medical term extracted |
| `icd_code` | TEXT | WHO ICD diagnostic code |
| `icd_indication` | TEXT | Official ICD disease title |
| `level_1_indication` | TEXT | High-level disease category |

---

## 🚢 Deployment Options

A comprehensive step-by-step cloud deployment walkthrough is available in [DEPLOYMENT_GUIDE.md](file:///c:/Users/Shaina/OneDrive/Desktop/cdsco-weekly-tracker/DEPLOYMENT_GUIDE.md).

Recommended production architectures:
1. **Streamlit Community Cloud (Recommended & 100% Free)**:
   - Web App: Streamlit Community Cloud (connected to this GitHub repo).
   - Database: Free cloud PostgreSQL via [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com).
   - Automation: Scheduled weekly scraping via GitHub Actions ([`.github/workflows/weekly_tracker.yml`](file:///c:/Users/Shaina/OneDrive/Desktop/cdsco-weekly-tracker/.github/workflows/weekly_tracker.yml)).
2. **Containerized Web Service (Render.com / Railway)**:
   - Uses the included [Dockerfile](file:///c:/Users/Shaina/OneDrive/Desktop/cdsco-weekly-tracker/Dockerfile) with Playwright and Chromium pre-installed.
3. **Self-Hosted VPS (Docker Compose)**:
   - Launch PostgreSQL and the Streamlit app together using `docker compose up -d`.

---

## ❓ Troubleshooting

- **Database Connection Error (`could not connect to server`)**: Check that PostgreSQL is running and credentials in `.env` match your database settings.
- **Playwright Browser Missing (`Executable doesn't exist`)**: Run `playwright install chromium` in your activated environment.
- **Port 8501 Already in Use**: Launch on a custom port using:
  ```bash
  streamlit run app/dashboard/dashboard.py --server.port 8502
  ```
- **Gemini Quota / API Errors**: Verify your `GEMINI_API_KEY` at [Google AI Studio](https://aistudio.google.com/).
