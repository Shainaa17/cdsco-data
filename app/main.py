from app.scraper.cdsco_scraper import main as scrape
from app.enrichment.pipeline import run_pipeline


def main():

    print("\n==============================")
    print(" CDSCO WEEKLY TRACKER ")
    print("==============================\n")

    print("Step 1: Scraping CDSCO...\n")
    scrape()

    print("\nStep 2: Running enrichment pipeline...\n")
    run_pipeline()

    print("\nDone! Excel generated successfully.\n")


if __name__ == "__main__":
    main()