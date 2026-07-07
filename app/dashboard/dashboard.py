import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px

from app.database.operations import fetch_all_records
from app.main import main as update_pipeline

st.set_page_config(
    page_title="CDSCO Weekly Drug Tracker",
    page_icon="💊",
    layout="wide"
)


def load_data():
    return pd.DataFrame(fetch_all_records())


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

# ================= SIDEBAR =======================

st.sidebar.title("Filters")

search = st.sidebar.text_input(
    "🔍 Search Drug"
)

manufacturer = st.sidebar.selectbox(
    "Manufacturer",
    ["All"] + sorted(
        df["manufacturer"]
        .dropna()
        .unique()
        .tolist()
    )
)

category = st.sidebar.selectbox(
    "Category",
    ["All"] + sorted(
        df["category"]
        .dropna()
        .unique()
        .tolist()
    )
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

if search:

    filtered = filtered[
        filtered["drug_name"]
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]

if manufacturer != "All":

    filtered = filtered[
        filtered["manufacturer"] == manufacturer
    ]

if category != "All":

    filtered = filtered[
        filtered["category"] == category
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

    if st.button("🔄 Refresh Dashboard"):

        st.rerun()

with col2:

    st.info(
        "Dashboard connected directly to PostgreSQL."
    )

st.divider()

st.caption(
    "Developed for Kraftland Intelligence • CDSCO Weekly Tracker"
)