from datetime import datetime

CDSCO_URL = "https://www.cdscoonline.gov.in/CDSCO/cdscoDrugs"


def clean_record(record):

    important_fields = [
        "composition",
        "dosage",
        "indication"
    ]

    missing = []

    for field in important_fields:

        value = record.get(field, "NA")

        if not value or value.strip().upper() == "NA":
            record[field] = "Not Available"
            missing.append(field)

    record["needs_enrichment"] = "Yes" if missing else "No"

    record["missing_fields"] = ", ".join(missing) if missing else "-"

    record["source"] = "CDSCO"

    record["source_url"] = CDSCO_URL

    record["last_updated"] = datetime.now().strftime("%d-%b-%Y %H:%M")

    return record