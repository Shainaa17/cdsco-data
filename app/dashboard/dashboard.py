import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px

from app.database.operations import (
    fetch_all_records,
    fetch_icd_mappings_for_excel
)
from app.database.models import create_tables
from app.main import main as update_pipeline

st.set_page_config(
    page_title="CDSCO Weekly Drug Tracker",
    page_icon="💊",
    layout="wide"
)

DEFAULT_COLUMNS = [
    "category", "drug_name", "approval_date", "type", "composition",
    "dosage", "indication", "manufacturer", "needs_enrichment",
    "missing_fields", "source", "source_url", "last_updated",
    "composition_source", "dosage_source", "indication_source",
    "is_new"
]


def load_data():
    try:
        create_tables()
    except Exception as e:
        print(f"Schema check notice: {e}")
    try:
        records = fetch_all_records()
        if not records:
            return pd.DataFrame(columns=DEFAULT_COLUMNS)
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame(columns=DEFAULT_COLUMNS)


df = load_data()

st.title("💊 CDSCO Weekly Drug Intelligence Dashboard")
st.caption("Automated CDSCO Drug Approval Monitoring & AI Enrichment")

st.divider()

# ================= KPI CARDS =====================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total Drugs",
        len(df)
    )

with c2:
    st.metric(
        "New Update",
        len(df[df["is_new"] == True])
    )

with c3:
    st.metric(
        "Manufacturers",
        df["manufacturer"].nunique()
    )

with c4:
    st.metric(
        "Categories",
        df["category"].nunique()
    )

st.divider()

st.sidebar.title("🔄 Live Sync")
st.sidebar.caption("Scrape CDSCO & WHO ICD, enrich missing data & update dashboard.")

def trigger_full_scrape():
    with st.spinner("Scraping CDSCO, querying WHO ICD, and enriching data with AI... Please wait."):
        st.cache_data.clear()
        update_pipeline()
        st.success("✅ CDSCO & WHO data fetched and synced successfully!")
        st.rerun()

if st.sidebar.button("⚡ Fetch & Scrape CDSCO + WHO", type="primary", use_container_width=True):
    trigger_full_scrape()

st.sidebar.divider()
st.sidebar.title("Filters")

search = st.sidebar.text_input(
    "🔍 Search Drug"
)

manufacturer = st.sidebar.multiselect(
    "Manufacturer",
    options=sorted(
        df["manufacturer"]
        .dropna()
        .unique()
        .tolist()
    ),
    placeholder="All"
)

category = st.sidebar.multiselect(
    "Category",
    options=sorted(
        df["category"]
        .dropna()
        .unique()
        .tolist()
    ),
    placeholder="All"
)

type_filter = st.sidebar.multiselect(
    "Type",
    options=sorted(
        df["type"]
        .dropna()
        .unique()
        .tolist()
    ),
    placeholder="All"
)

status = st.sidebar.selectbox(
    "Needs Enrichment",
    ["All", "Yes", "No"]
)
show_new = st.sidebar.checkbox(
    "Show only newly added approvals"
)
# ================= FILTERS =======================

filtered = df.copy()
filtered["approval_date"] = pd.to_datetime(
    filtered["approval_date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

filtered = filtered.sort_values(
    by="approval_date",
    ascending=False
)

if search:

    filtered = filtered[
        filtered["drug_name"]
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]

if manufacturer:
    
    filtered = filtered[
        filtered["manufacturer"].isin(manufacturer)
    ]

if category:
    
    filtered = filtered[
        filtered["category"].isin(category)
    ]

if type_filter:
    
    filtered = filtered[
        filtered["type"].isin(type_filter)
    ]
    
if status != "All":

    filtered = filtered[
        filtered["needs_enrichment"] == status
    ]

if show_new:
    
    filtered = filtered[
        filtered["is_new"] == True
    ]

st.success(
    f"Showing {len(filtered)} records"
)

st.divider()
# ===================== CHARTS =======================


st.subheader("Drug Approvals")

display_columns = [
    "drug_name",
    "manufacturer",
    "category",
    "approval_date",
    "type",

    "composition",
    "composition_source",

    "dosage",
    "dosage_source",

    "indication",
    "indication_source",

    "needs_enrichment"
]
available_columns = [
    c for c in display_columns
    if c in filtered.columns
]

st.dataframe(
    filtered[available_columns],
    use_container_width=True,
    height=650,
    column_config={
        "composition_source": st.column_config.LinkColumn(
            "Composition Source"
        ),
        "dosage_source": st.column_config.LinkColumn(
            "Dosage Source"
        ),
        "indication_source": st.column_config.LinkColumn(
            "Indication Source"
        )
    }
)

st.divider()
st.subheader("WHO ICD Mappings")

icd_df = pd.DataFrame(
    fetch_icd_mappings_for_excel()
)
if not icd_df.empty:
    
    filtered_drugs = (
        filtered["drug_name"]
        .dropna()
        .unique()
    )

    icd_df = icd_df[
        icd_df["drug_name"].isin(
            filtered_drugs
        )
    ]
if not icd_df.empty:
    
    st.success(
        f"Showing {len(icd_df)} ICD mappings"
    )

    st.dataframe(
        icd_df,
        use_container_width=True,
        height=350
    )

else:

    st.info(
        "No ICD mappings available for the selected filters."
    )

excel_path = "data/exports/cdsco_approvals.xlsx"

if os.path.exists(excel_path):

    with open(excel_path, "rb") as f:

        st.download_button(
            "⬇ Download Latest Excel Report",
            data=f,
            file_name="cdsco_approvals.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Scrape & Refresh Data (CDSCO + WHO)", use_container_width=True):
        trigger_full_scrape()

with col2:
    st.info("Dashboard connected directly to PostgreSQL.")

st.divider()

st.caption(
    "Developed for Kraftland Intelligence • CDSCO Weekly Tracker"
)