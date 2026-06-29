from app.scraper.browser import BrowserManager
from app.parser.extractor import CDSCOExtractor
from app.parser.cleaner import clean_record
from app.reports.excel import generate_excel

CDSCO_URL = "https://www.cdscoonline.gov.in/CDSCO/cdscoDrugs"


def main():

    browser = BrowserManager(headless=False)

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

    generate_excel(
        records,
        "data/exports/cdsco_approvals.xlsx"
    )

    print("Excel generated successfully!")

    browser.close()


if __name__ == "__main__":
    main()