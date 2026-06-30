from app.database.operations import insert_record

record = {

    "category": "SND",
    "drug_name": "Test Drug",
    "approval_date": "01-Jul-2026",
    "type": "Bulk Drug",

    "composition": "Not Available",
    "dosage": "Not Available",
    "indication": "Not Available",

    "manufacturer": "OpenAI Pharma",

    "needs_enrichment": "Yes",
    "missing_fields": "composition,dosage,indication",

    "source": "CDSCO",
    "source_url": "https://www.cdsco.gov.in",

    "last_updated": "2026-07-01"

}

print(insert_record(record))