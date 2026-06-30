import logging

import pandas as pd

from app.enrichment.search import tavily_search
from app.enrichment.llm import enrich_record

from app.database.operations import (
    fetch_pending_enrichment,
    fetch_all_records,
    update_enrichment
)

from app.reports.excel import save_dataframe


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

OUTPUT_FILE = "data/exports/cdsco_approvals.xlsx"


def run_pipeline():

    logging.info("Fetching pending records from PostgreSQL...")

    pending_records = fetch_pending_enrichment()

    logging.info(f"{len(pending_records)} records need enrichment.")

    for row in pending_records:

        logging.info(f"Processing: {row['drug_name']}")

        search_results = tavily_search(
            row["drug_name"],
            row["manufacturer"]
        )

        enriched = enrich_record(
            row,
            search_results
        )

        # Composition
        if row["composition"] == "Not Available":

            row["composition"] = enriched["composition"]["value"]
            row["composition_source"] = enriched["composition"]["source"]

        # Dosage
        if row["dosage"] == "Not Available":

            row["dosage"] = enriched["dosage"]["value"]
            row["dosage_source"] = enriched["dosage"]["source"]

        # Indication
        if row["indication"] == "Not Available":

            row["indication"] = enriched["indication"]["value"]
            row["indication_source"] = enriched["indication"]["source"]

        missing = []

        for field in [
            "composition",
            "dosage",
            "indication"
        ]:

            if row[field] == "Not Available":
                missing.append(field)

        if missing:

            row["needs_enrichment"] = "Yes"
            row["missing_fields"] = ", ".join(missing)

        else:

            row["needs_enrichment"] = "No"
            row["missing_fields"] = ""

        update_enrichment(row)

    logging.info("Fetching all records...")

    records = fetch_all_records()

    df = pd.DataFrame(records)

    save_dataframe(
        df,
        OUTPUT_FILE
    )

    logging.info("Pipeline completed successfully.")