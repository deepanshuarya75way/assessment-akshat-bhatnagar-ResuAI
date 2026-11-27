from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH_DIR = Path("app/auth")
AUTH_DIR.mkdir(exist_ok=True)

STORAGE_STATE = AUTH_DIR / "storage_state.json"


class BrowserAuth:

    def login(self):

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            context = browser.new_context()

            page = context.new_page()

            page.goto("https://recruit.thapar.edu")

            print("=" * 60)
            print("Please login manually.")
            print("After reaching the RecruitSage dashboard,")
            print("return to this terminal and press ENTER.")
            print("=" * 60)

            input()

            context.storage_state(
                path=str(STORAGE_STATE)
            )

            browser.close()
            
            print("Storage state saved successfully.")


browser_auth = BrowserAuth()