# 🚀 CDSCO Weekly Tracker - Cloud Deployment Guide

This guide walks you through deploying the **CDSCO Weekly Drug Intelligence Platform** to the cloud so anyone can access the dashboard online with zero server maintenance.

---

## 🏗 Architecture Overview

The system consists of two parts:
1. **Cloud PostgreSQL Database**: Stores approval records, hashes, enrichment data, and ICD mappings.
2. **Streamlit Web Dashboard**: Visualizes data, metrics, search filters, and allows on-demand Excel downloads.
3. *(Optional)* **Automated Scraper**: Runs on a schedule via GitHub Actions to keep data fresh.

```mermaid
flowchart LR
    A[Neon / Supabase Postgres] <--> B[Streamlit Community Cloud]
    C[GitHub Actions (Weekly Cron)] -->|Scrape & Enrich| A
```

---

## 🗄️ Step 1: Set Up a Free Cloud PostgreSQL Database (Takes 2 Mins)

Your local database (`localhost:5432`) cannot be reached by cloud servers. You need a free cloud PostgreSQL database.

### Recommended: Neon Serverless Postgres (100% Free)
1. Go to **[https://neon.tech](https://neon.tech)** and sign up for free (using GitHub or Google).
2. Click **Create Project**, name it `cdsco-db`, and select the region closest to you (e.g., `Singapore` or `Frankfurt`).
3. Under **Connection Details**, copy the connection string. It looks like:
   ```text
   postgresql://username:password@ep-xyz-123456.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
4. Save this string — this is your `DATABASE_URL`.

*(Alternative: You can also use [Supabase](https://supabase.com) or [Render PostgreSQL](https://render.com)).*

---

## ⚡ Step 2: Initialize Database Tables

Before launching the web app, initialize the required tables in your cloud database:

1. In your local `.env` file, temporarily set:
   ```env
   DATABASE_URL=postgresql://username:password@ep-xyz-123456.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
2. In your terminal, run:
   ```bash
   python test_db.py
   ```
   *Output: `Database connected successfully.`*

Both `approvals` and `approval_icd_mappings` tables are now created and ready in your cloud database!

---

## 🌐 Step 3: Deploy the Dashboard

Choose the deployment method that fits your needs best:

### Option A: Streamlit Community Cloud (Recommended — Free & 2 Clicks)

Streamlit Community Cloud is the fastest and official way to host Streamlit applications.

1. **Push your code to GitHub**:
   Ensure your latest code is committed and pushed to your repository (e.g., `https://github.com/Shainaa17/cdsco-data`).
   ```bash
   git add .
   git commit -m "Add cloud deployment configuration"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**:
   - Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.
   - Click **"Create app"** (or **"New app"**).
   - Select your repository: `Shainaa17/cdsco-data` (or your fork).
   - Set **Branch**: `main`.
   - Set **Main file path**: `app/dashboard/dashboard.py`.

3. **Configure Environment Secrets**:
   - Click **"Advanced settings..."** before deploying.
   - Under **Secrets**, paste your configuration in TOML format:
     ```toml
     DATABASE_URL = "postgresql://username:password@ep-xyz-123456.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
     GEMINI_API_KEY = "AIzaSy..."
     TAVILY_API_KEY = "tvly-..."
     WHO_ICD_CLIENT_ID = "your_client_id_optional"
     WHO_ICD_CLIENT_SECRET = "your_client_secret_optional"
     ```
   - Click **Save**.

4. **Click "Deploy!"**:
   Streamlit will build your app and give you a public URL (e.g., `https://cdsco-tracker.streamlit.app`).

---

### Option B: Render.com / Railway (Web Service via Docker)

If you prefer an all-in-one platform or want headless browser scraping running directly in the cloud container:

1. Push your repository to GitHub.
2. Go to **[Render.com](https://render.com)** and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Render will automatically detect the `Dockerfile`.
5. Set the **Instance Type** to Free or Starter.
6. Under **Environment Variables**, add:
   - `DATABASE_URL`
   - `GEMINI_API_KEY`
   - `TAVILY_API_KEY`
7. Click **Create Web Service**. Your app will build and be live with a `.onrender.com` URL.

---

### Option C: Self-Hosted Server / VPS (Docker Compose)

To host on your own Linux server (Ubuntu/Debian on AWS EC2, DigitalOcean, Hetzner, etc.):

1. Clone your repository onto the server:
   ```bash
   git clone https://github.com/Shainaa17/cdsco-data.git
   cd cdsco-data
   ```
2. Create your `.env` file with your credentials:
   ```bash
   nano .env
   ```
3. Run the complete stack (PostgreSQL + Streamlit + Scraper):
   ```bash
   docker compose up -d
   ```
4. Access the dashboard at `http://your-server-ip:8501`.

---

## ⏰ Step 4: Automated Scheduled Scraping (GitHub Actions)

A workflow file is already included at [`.github/workflows/weekly_tracker.yml`](file:///.github/workflows/weekly_tracker.yml).

To enable automated weekly scraping and AI enrichment:
1. Go to your GitHub repository -> **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret** and add:
   - `DATABASE_URL`
   - `GEMINI_API_KEY`
   - `TAVILY_API_KEY`
   - `WHO_ICD_CLIENT_ID` (optional)
   - `WHO_ICD_CLIENT_SECRET` (optional)
3. Every **Monday at 09:30 AM IST** (04:00 UTC), GitHub Actions will automatically:
   - Launch headless Chromium
   - Scrape newly published CDSCO approvals
   - Enrich missing fields using Google Gemini & Tavily
   - Map indications to WHO ICD codes
   - Update your cloud PostgreSQL database
4. You can also trigger a run manually anytime from the **Actions** tab by selecting **"CDSCO Weekly Tracker Cron"** -> **"Run workflow"**.

---

## ✅ Summary Checklist

| Task | Status | Notes |
|---|---|---|
| Create free Cloud PostgreSQL | 🔲 | Use Neon.tech or Supabase to get `DATABASE_URL` |
| Initialize tables | 🔲 | Run `python test_db.py` with `DATABASE_URL` |
| Push changes to GitHub | 🔲 | `git push origin main` |
| Deploy Streamlit Dashboard | 🔲 | Deploy on share.streamlit.io with `app/dashboard/dashboard.py` |
| Configure GitHub Actions Secrets | 🔲 | Enables 100% automated weekly data updates |
