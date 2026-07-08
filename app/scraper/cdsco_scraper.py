from app.scraper.browser import BrowserManager
from app.parser.extractor import CDSCOExtractor
from app.parser.cleaner import clean_record

from app.database.models import create_tables
from app.database.operations import (
    insert_record,
    fetch_all_records
)

from app.reports.excel import generate_excel


CDSCO_URL = "https://www.cdscoonline.gov.in/CDSCO/cdscoDrugs"


def main(headless=True):

    create_tables()

    browser = BrowserManager(headless=headless)

    page = browser.start()

    print("Opening CDSCO website...")

    page.goto(CDSCO_URL)

    page.wait_for_load_state("networkidle")

    html = page.content()

    extractor = CDSCOExtractor(html)

    raw_records = extractor.extract_all_records()

    records = []

    for record in raw_records:
        records.append(clean_record(record))

    print(f"Extracted {len(records)} records")

    inserted = 0

    for record in records:

        if insert_record(record):
            inserted += 1

    print(
        f"Inserted {inserted} new approvals into PostgreSQL."
    )

    all_records = fetch_all_records()

    generate_excel(
        all_records,
        "data/exports/cdsco_approvals.xlsx"
    )

    print("Excel generated successfully!")

    browser.close()


if __name__ == "__main__":
    main()