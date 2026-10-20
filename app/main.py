from app.scraper.cdsco_scraper import main as scrape
from app.enrichment.pipeline import run_pipeline
from app.icd.pipeline import run_icd_pipeline
from app.database.operations import clear_new_flags


def main():

    print("\n==============================")
    print(" CDSCO WEEKLY TRACKER ")
    print("==============================\n")

    print("Step 1: Clearing previous update flags...\n")
    clear_new_flags()

    print("Step 2: Scraping CDSCO...\n")
    scrape()

    print("\nStep 3: Running enrichment pipeline...\n")
    run_pipeline()

    print("\nStep 4: Running WHO ICD mapping pipeline...\n")
    try:
        run_icd_pipeline(limit=None)
    except Exception as e:
        print(f"WHO ICD pipeline notice: {e}")

    print("\nDone! Scraping and enrichment completed successfully.\n")


if __name__ == "__main__":
    main()