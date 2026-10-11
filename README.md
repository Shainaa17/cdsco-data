# 💊 CDSCO Weekly Drug Intelligence Tracker

An automated end-to-end pharmaceutical intelligence platform designed to track, scrape, enrich, standardize, and visualize weekly drug approvals from the **Central Drugs Standard Control Organisation (CDSCO)**, Government of India.

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Automated Weekly Scraper & Update Engine](#-automated-weekly-scraper--update-engine)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Environment Variables & Secrets Setup](#-environment-variables--secrets-setup)
  - [1. Local Environment (.env)](#1-local-environment-env)
  - [2. Streamlit Community Cloud Secrets](#2-streamlit-community-cloud-secrets)
  - [3. GitHub Actions Secrets](#3-github-actions-secrets)
- [Quick Start / Local Installation](#-quick-start--local-installation)
- [Running the Project](#-running-the-project)
- [Database Schema & Migrations](#-database-schema--migrations)
- [Cloud Deployment Options](#-cloud-deployment-options)
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
- **Streamlit Web UI**: Responsive web application with instant KPI cards, advanced filters, and one-click CDSCO update triggers.
- **Scheduled Cloud Automation**: Zero-maintenance weekly scraper executed via GitHub Actions and synced to a serverless Neon PostgreSQL database.

---

## 🏗 System Architecture

```mermaid
flowchart TD
    subgraph Ingestion
        A[CDSCO Web Portal] -->|Playwright Scraper| P[HTML Parser / Cleaner]
        B[Official Approval PDFs] -->|pdfplumber| I[PDF Importer]
    end

    subgraph Storage & Deduplication
        P --> D[(PostgreSQL Database - Neon / Local)]
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

    subgraph Automation & Presentation
        GH[GitHub Actions Cron - Weekly] -->|Triggers Pipeline| P
        D --> E[Excel Report Generator]
        D --> W[Streamlit Web Dashboard]
        E -->|cdsco_approvals.xlsx| W
    end
```

---

## 🔄 Automated Weekly Scraper & Update Engine

The platform includes two ways to keep data constantly updated:

### 1. Cloud-Scheduled Weekly Cron (GitHub Actions)
A pre-configured CI/CD workflow is available at [`.github/workflows/weekly_tracker.yml`](file:///.github/workflows/weekly_tracker.yml).
- **Schedule**: Automatically runs every **Monday at 04:00 UTC (09:30 AM IST)**.
- **On-Demand**: Can be triggered anytime from GitHub under **Actions** → **CDSCO Weekly Tracker Cron** → **Run workflow**.
- **What it does**: Spins up an Ubuntu runner, launches headless Chromium via Playwright, scrapes newly published CDSCO approvals, enriches missing clinical details via Gemini + Tavily, normalizes WHO ICD codes, and pushes newly tagged updates (`is_new = TRUE`) directly to your Neon cloud database.

### 2. Live In-Dashboard Update Trigger
Within the Streamlit web dashboard:
- Click the **"🔄 Update from CDSCO"** button at the bottom of the page.
- The pipeline clears previous update flags, scrapes new records, enriches them, updates the database, and refreshes the KPI cards automatically.

---

## 📂 Project Structure

```text
cdsco-weekly-tracker/
│
├── .github/
│   └── workflows/
│       └── weekly_tracker.yml     # Automated weekly scraper cron workflow
│
├── .streamlit/
│   └── config.toml                # Streamlit server and theme configuration
│
├── app/
│   ├── dashboard/
│   │   └── dashboard.py           # Streamlit web application & KPI dashboard
│   ├── database/
│   │   ├── db.py                  # PostgreSQL connection factory (URL or params)
│   │   ├── models.py              # DDL schema definition & auto-migrations
│   │   └── operations.py          # CRUD queries, hash deduplication, ICD operations
│   ├── enrichment/
│   │   ├── llm.py                 # Google Gemini prompt engineering & extraction
│   │   ├── pipeline.py            # AI enrichment pipeline orchestrator
│   │   ├── search.py              # Tavily web search integration
│   │   └── citations.py           # Verification & citation utilities
│   ├── icd/
│   │   ├── code_matcher.py        # Indication term tokenizer and scoring
│   │   ├── pipeline.py            # WHO ICD extraction & PostgreSQL mapping
│   │   ├── search.py              # WHO ICD hierarchy retrieval
│   │   └── term_extractor.py      # Clinical term extraction
│   ├── parser/
│   │   ├── cleaner.py             # Raw record normalization & cleaning
│   │   └── extractor.py           # BeautifulSoup HTML table parsing
│   ├── pdf_import/
│   │   └── importer.py            # PDF tabular extractor using pdfplumber
│   ├── reports/
│   │   └── excel.py               # openpyxl formatted spreadsheet generator
│   ├── scraper/
│   │   ├── browser.py             # Playwright browser lifecycle manager
│   │   ├── cdsco_scraper.py       # CDSCO portal table pagination & scraper
│   │   ├── navigator.py           # Page navigation & dropdown handlers
│   │   └── selectors.py           # CSS/XPath selectors
│   └── main.py                    # Complete end-to-end pipeline runner
│
├── data/
│   ├── exports/
│   │   └── cdsco_approvals.xlsx   # Generated Excel intelligence report
│   └── pdfs/                      # Directory for historical regulatory PDFs
│
├── DEPLOYMENT_GUIDE.md            # Detailed cloud deployment walkthrough
├── Dockerfile                     # Production container image with Playwright
├── docker-compose.yml             # Unified Docker Compose setup
├── requirements.txt               # Python package dependencies
├── run_dashboard.bat              # 1-click Windows starter batch script
├── test_db.py                     # Database connection & schema verification
└── README.md                      # Project documentation
```

---

## 🛠 Tech Stack

- **Frontend / Presentation**: Streamlit, Plotly Express, Pandas
- **Web Automation**: Playwright (Headless Chromium)
- **PDF Extraction**: `pdfplumber`
- **Database & Storage**: PostgreSQL (Local or Neon Serverless Postgres), `psycopg2-binary`
- **Generative AI & LLM**: Google Gemini API (`google-genai`, `gemini-2.5-flash`)
- **Search Engine API**: Tavily Search API (`tavily-python`)
- **Medical Standard**: WHO ICD-10 & ICD-11 API
- **Reporting**: `openpyxl` with custom formatting and hyperlinks
- **DevOps / CI/CD**: GitHub Actions, Docker, Streamlit Community Cloud

---

## 🔑 Environment Variables & Secrets Setup

The application uses these core environment variables:

| Variable | Description | Example / Source |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require` |
| `GEMINI_API_KEY` | Google Gemini API Key | Get from [Google AI Studio](https://aistudio.google.com/) |
| `TAVILY_API_KEY` | Tavily Web Search API Key | Get from [Tavily AI](https://tavily.com/) |
| `WHO_ICD_CLIENT_ID` | *(Optional)* WHO ICD API Client ID | [WHO ICD API](https://icd.who.int/icdapi) |
| `WHO_ICD_CLIENT_SECRET` | *(Optional)* WHO ICD API Client Secret | [WHO ICD API](https://icd.who.int/icdapi) |

---

### 1. Local Environment (`.env`)
For running on your computer, create or update a `.env` file in the root folder:

```env
# Cloud Database (e.g. Neon)
DATABASE_URL=postgresql://username:password@ep-xyz.aws.neon.tech/neondb?sslmode=require

# AI & Search APIs
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# WHO ICD API Credentials (Optional)
WHO_ICD_CLIENT_ID=your_who_client_id
WHO_ICD_CLIENT_SECRET=your_who_client_secret
```

---

### 2. Streamlit Community Cloud Secrets
*(Required for your live public dashboard app)*

1. Open your app on **[share.streamlit.io](https://share.streamlit.io)**.
2. In the bottom-right corner, click **"Manage app"**.
3. Click the **three vertical dots (`⋮`)** → **"Settings"**.
4. In the left sidebar of the modal, select **"Secrets"**.
5. Paste your variables in **TOML format** (keys and values in quotes):

```toml
DATABASE_URL = "postgresql://username:password@ep-xyz.aws.neon.tech/neondb?sslmode=require"
GEMINI_API_KEY = "your_gemini_api_key_here"
TAVILY_API_KEY = "your_tavily_api_key_here"
WHO_ICD_CLIENT_ID = "your_who_client_id_optional"
WHO_ICD_CLIENT_SECRET = "your_who_client_secret_optional"
```

6. Click **"Save"**. The dashboard will auto-restart and connect immediately.

---

### 3. GitHub Actions Secrets
*(Required for the automated weekly scraper cron)*

1. Go to your repository on **GitHub** (`https://github.com/Shainaa17/cdsco-data`).
2. Click **Settings** (top navigation tab).
3. In the left menu, go to **Secrets and variables** → **Actions**.
4. Scroll down to the **"Repository secrets"** section.
5. Click the green button **"New repository secret"**.
6. Add each variable separately:
   - Name: `DATABASE_URL` → Value: `postgresql://username:password@ep-xyz.aws.neon.tech/neondb?sslmode=require`
   - Name: `GEMINI_API_KEY` → Value: `your_gemini_api_key_here`
   - Name: `TAVILY_API_KEY` → Value: `your_tavily_api_key_here`
7. Click **"Add secret"** after each entry.

Now, your weekly scraper will authenticate securely without exposing keys in public code.

---

## 🚀 Quick Start / Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Shainaa17/cdsco-data.git
cd cdsco-weekly-tracker
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies & Playwright
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Initialize Database Tables
```bash
python test_db.py
```
*(Prints: `Database connected successfully.`)*

---

## 🏃 Running the Project

### 1. Launch the Dashboard
```bash
streamlit run app/dashboard/dashboard.py
```
Or simply double-click **`run_dashboard.bat`** on Windows. The app opens at `http://localhost:8501`.

### 2. Run the Full Scraping & Enrichment Pipeline Manually
```bash
python -m app.main
```

### 3. Import Historical PDFs
```bash
python -m app.pdf_import.importer
```

### 4. Run WHO ICD Standardization
```bash
python -m app.icd.pipeline
```

---

## 🗄 Database Schema & Migrations

The database includes automated migrations on startup (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`).

### `approvals` Table
| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique record ID |
| `approval_hash` | TEXT UNIQUE | SHA-256 fingerprint for deduplication |
| `drug_name` | TEXT | Name of approved formulation |
| `category` | TEXT | Category (New Drug, SND, FDC, Biological) |
| `approval_date` | TEXT | Date approved by CDSCO |
| `type` | TEXT | Formulation type (Tablet, Capsule, Injection, etc.) |
| `composition` | TEXT | Active pharmaceutical ingredients |
| `composition_source`| TEXT | Verified source citation URL |
| `dosage` | TEXT | Recommended dosage and strength |
| `dosage_source` | TEXT | Verified source citation URL |
| `indication` | TEXT | Clinical indication / targeted disease |
| `indication_source` | TEXT | Verified source citation URL |
| `manufacturer` | TEXT | Pharmaceutical company / applicant |
| `needs_enrichment` | TEXT | `'Yes'` or `'No'` indicator |
| `missing_fields` | TEXT | Missing attribute tags |
| `source` | TEXT | Data origin (`CDSCO`, `CDSCO PDF`) |
| `source_url` | TEXT | Original PDF file name or web URL |
| `last_updated` | TEXT | Timestamp of last modification |
| `is_new` | BOOLEAN | Set to `TRUE` for newly scraped records |
| `added_at` | TIMESTAMP | Record creation timestamp |

### `approval_icd_mappings` Table
| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Mapping record identifier |
| `approval_hash` | TEXT REFERENCES approvals | Foreign key linked to drug approval |
| `icd_search_term` | TEXT | Extracted clinical phrase |
| `icd_code` | TEXT | WHO ICD classification code (e.g., `1C62.0`) |
| `icd_indication` | TEXT | Official WHO medical disease title |
| `level_1_indication`| TEXT | Top-level disease classification hierarchy |

---

## 🚢 Cloud Deployment Options

For a step-by-step walkthrough, see [DEPLOYMENT_GUIDE.md](file:///c:/Users/Shaina/OneDrive/Desktop/cdsco-weekly-tracker/DEPLOYMENT_GUIDE.md).

- **Streamlit Community Cloud (Recommended & 100% Free)**:
  Directly link this repository, set the main path to `app/dashboard/dashboard.py`, and paste secrets in the dashboard settings.
- **Docker Container (Render.com / Railway / Fly.io)**:
  Uses the included [Dockerfile](file:///c:/Users/Shaina/OneDrive/Desktop/cdsco-weekly-tracker/Dockerfile) with Playwright and Chromium pre-installed.
- **Self-Hosted VPS (Docker Compose)**:
  Spin up PostgreSQL and the application together with one command:
  ```bash
  docker compose up -d
  ```

---

## ❓ Troubleshooting

- **UndefinedColumn or Schema Mismatches**: Running `python test_db.py` automatically migrates missing columns (`is_new`, `added_at`, `approval_icd_mappings`).
- **Streamlit Cloud ModuleNotFoundError**: Verify all required packages are present in `requirements.txt`.
- **Database Connection Error (`could not connect to server`)**: Check your `DATABASE_URL` string and ensure `?sslmode=require` is appended for cloud hosts like Neon.
- **Playwright Headless Missing**: Run `playwright install --with-deps chromium`.
