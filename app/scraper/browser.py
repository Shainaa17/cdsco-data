from playwright.sync_api import sync_playwright


class BrowserManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        import subprocess
        self.playwright = sync_playwright().start()

        try:
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
            )
        except Exception as e:
            # If Chromium binary is missing in cloud environments (like Streamlit Cloud)
            if "Executable doesn't exist" in str(e) or "playwright install" in str(e).lower():
                print("Playwright chromium not found. Installing now...")
                subprocess.run(["playwright", "install", "chromium"], check=True)
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
                )
            else:
                raise e

        self.page = self.browser.new_page(
            viewport={"width": 1600, "height": 900}
        )

        return self.page

    def close(self):
        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()