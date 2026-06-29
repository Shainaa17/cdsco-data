from app.scraper.selectors import CDSCO_URL


class Navigator:

    def __init__(self, page):
        self.page = page

    def open_cdsco(self):
        print("Opening CDSCO website...")

        self.page.goto(CDSCO_URL)

        self.page.wait_for_load_state("networkidle")

        print("Website Loaded Successfully!")